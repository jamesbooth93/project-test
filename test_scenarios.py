import os
import tempfile
import unittest

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="management_sim_mpl_"))
os.environ.setdefault("MANAGEMENT_SIM_TEST_MODE", "1")

from streamlit.testing.v1 import AppTest

from reporting import (
    BENCHMARK_CACHE,
    _analysis_snapshot_for_week,
    build_benchmark_history,
    determine_summary_branch,
)
from benchmarks import autoplay_demo_route, autoplay_demo_route_for_outcome, autoplay_demo_route_for_summary_branch
from game_logic import GameState
from scenario_copy import scenario_end_screen_copy, scenario_week_end_report
from scenario_definitions import SCENARIOS
from scenario_runtime import apply_recommended_actions_for_week, authored_action_quality, strategy_aligned_with_recommendation
from view_models import build_weekly_view_model


class ScenarioRegressionTests(unittest.TestCase):
    def _run_recommended(self, scenario_key: str, seed: int = 0) -> GameState:
        game = GameState(
            scenario=scenario_key,
            difficulty="Normal",
            team_size=SCENARIOS[scenario_key].team_size,
            max_weeks=SCENARIOS[scenario_key].length,
            seed=seed,
        )
        while not game.game_over and game.week <= game.max_weeks:
            apply_recommended_actions_for_week(game)
            game.end_week()
        return game

    def _run_actions(self, scenario_key: str, actions_by_week: dict[int, list[tuple[str, str]]], seed: int = 0) -> GameState:
        game = GameState(
            scenario=scenario_key,
            difficulty="Normal",
            team_size=SCENARIOS[scenario_key].team_size,
            max_weeks=SCENARIOS[scenario_key].length,
            seed=seed,
        )
        role_targets = {
            "focal": game.get_scenario_role_node_id("focal_employee"),
            "hidden": game.get_scenario_role_node_id("hidden_strain_employee"),
        }
        while not game.game_over and game.week <= game.max_weeks:
            for action_type, target_role in actions_by_week.get(game.week, []):
                game.apply_player_action({"type": action_type, "target": role_targets[target_role]})
            game.end_week()
        return game

    def _run_actions_until_week(self, scenario_key: str, actions_by_week: dict[int, list[tuple[str, str]]], stop_week: int, seed: int = 0) -> GameState:
        game = GameState(
            scenario=scenario_key,
            difficulty="Normal",
            team_size=SCENARIOS[scenario_key].team_size,
            max_weeks=SCENARIOS[scenario_key].length,
            seed=seed,
        )
        role_targets = {
            "focal": game.get_scenario_role_node_id("focal_employee"),
            "hidden": game.get_scenario_role_node_id("hidden_strain_employee"),
        }
        while not game.game_over and game.week <= min(stop_week, game.max_weeks):
            for action_type, target_role in actions_by_week.get(game.week, []):
                game.apply_player_action({"type": action_type, "target": role_targets[target_role]})
            game.end_week()
            if game.get_analysis_history() and game.get_analysis_history()[-1]["week"] >= stop_week:
                break
        return game

    def test_scenario_01_recommended_route_succeeds(self):
        game = self._run_recommended("scenario_01", seed=0)
        latest = game.get_analysis_history()[-1]
        self.assertEqual(latest.get("scenario_outcome_tier"), "Succeed")

    def test_scenario_02_recommended_route_succeeds(self):
        game = self._run_recommended("scenario_02", seed=0)
        latest = game.get_analysis_history()[-1]
        self.assertEqual(latest.get("scenario_outcome_tier"), "Succeed")

    def test_scenario_02_diagnostic_actions_are_distinct(self):
        capacity_game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            seed=0,
        )
        workflow_game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            seed=0,
        )

        hidden_capacity = capacity_game.get_scenario_role_node_id("hidden_strain_employee")
        hidden_workflow = workflow_game.get_scenario_role_node_id("hidden_strain_employee")
        neighbor_capacity = sorted(capacity_game.G.neighbors(hidden_capacity))[0]
        neighbor_workflow = sorted(workflow_game.G.neighbors(hidden_workflow))[0]

        capacity_game.apply_player_action({"type": "check_in_on_load_bearing_risk", "target": hidden_capacity})
        workflow_game.apply_player_action({"type": "surface_hidden_support_work", "target": hidden_workflow})

        self.assertGreater(
            capacity_game.G.nodes[hidden_capacity]["manager_relationship"],
            workflow_game.G.nodes[hidden_workflow]["manager_relationship"],
        )
        self.assertGreater(
            workflow_game.G.nodes[neighbor_workflow].get("visibility_boost_weeks", 0),
            capacity_game.G.nodes[neighbor_capacity].get("visibility_boost_weeks", 0),
        )
        self.assertNotEqual(
            capacity_game.current_week_actions[-1]["explanation"].get("diagnostic_read"),
            workflow_game.current_week_actions[-1]["explanation"].get("diagnostic_read"),
        )

    def test_scenario_02_recommended_route_is_well_done_branch(self):
        game = self._run_recommended("scenario_02", seed=0)
        history = game.get_analysis_history()
        latest = history[-1]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)

        branch = determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)
        self.assertEqual(branch, "well_done")

    def test_snapshot_action_records_player_decision_not_end_week(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        focal = game.get_scenario_role_node_id("focal_employee")
        game.apply_player_action({"type": "quick_check_in", "target": focal})
        game.end_week()

        latest = game.get_analysis_history()[-1]
        self.assertEqual(latest["action"]["type"], "quick_check_in")
        self.assertEqual(latest["actions_taken"][-1]["type"], "quick_check_in")

    def test_crisis_requires_full_persistence_window(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        game.phase = "management"
        game.crisis_warning_weeks = 1
        game.last_metrics["crisis_warning_weeks"] = 1
        game.update_phase()
        self.assertNotEqual(game.phase, "crisis")

        game.crisis_warning_weeks = game.diff["crisis_persistence_weeks"]
        game.last_metrics["crisis_warning_weeks"] = game.diff["crisis_persistence_weeks"]
        game.update_phase()
        self.assertEqual(game.phase, "crisis")

    def test_manager_tipping_flag_updates_after_manager_strain_change(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        game.manager_state["strain"] = 0.69
        game.manager_state["overload_weeks"] = 1
        game.refresh_metrics()
        game._update_manager_strain()
        game._update_tipping_flags()
        self.assertGreaterEqual(game.manager_state["overload_weeks"], 2)
        self.assertTrue(game.manager_tipping_active)

    def test_scenario_02_workload_action_updates_visible_load_signal(self):
        game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            seed=0,
        )
        hidden = game.get_scenario_role_node_id("hidden_strain_employee")
        before = float(game.G.nodes[hidden].get("scenario_display_load", 0.0))
        game.apply_player_action({"type": "reduce_workload", "target": hidden})
        after = float(game.G.nodes[hidden].get("scenario_display_load", 0.0))
        self.assertLess(after, before)

    def test_benchmark_cache_key_includes_evaluation_mode(self):
        BENCHMARK_CACHE.clear()
        teaching_game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            evaluation_mode="teaching",
            seed=0,
        )
        simulation_game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            evaluation_mode="simulation",
            seed=0,
        )

        build_benchmark_history(teaching_game, benchmark_name="stabilising_response")
        build_benchmark_history(simulation_game, benchmark_name="stabilising_response")
        self.assertEqual(len(BENCHMARK_CACHE), 2)

    def test_passive_week_matches_do_nothing_recommendation(self):
        game = GameState(
            scenario="scenario_02",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_02"].team_size,
            max_weeks=SCENARIOS["scenario_02"].length,
            seed=0,
        )
        for _ in range(5):
            game.end_week()

        game.end_week()
        latest = game.get_analysis_history()[-1]
        self.assertEqual(latest["week"], 6)
        self.assertEqual(latest["actions_taken"], [])
        self.assertTrue(strategy_aligned_with_recommendation(latest, 6))

    def test_benchmark_histories_respect_requested_strategy(self):
        BENCHMARK_CACHE.clear()
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )

        no_intervention = build_benchmark_history(game, benchmark_name="no_intervention")
        misread = build_benchmark_history(game, benchmark_name="misread_response")
        mixed = build_benchmark_history(game, benchmark_name="mixed_response")
        stabilising = build_benchmark_history(game, benchmark_name="stabilising_response")

        self.assertEqual(no_intervention[-1]["run_strategy_profile"], "no_intervention")
        self.assertEqual(misread[-1]["run_strategy_profile"], "misread_response")
        self.assertEqual(mixed[-1]["run_strategy_profile"], "mixed_response")
        self.assertEqual(stabilising[-1]["run_strategy_profile"], "stabilising_response")

    def test_scenario_01_authored_copy_routes_cover_all_four_paths(self):
        cases = [
            ("spiralled", autoplay_demo_route_for_outcome("none", "Fail", "scenario_01")),
            ("high_strain_count", self._run_actions("scenario_01", {
                1: [("quick_check_in", "focal")],
                2: [("offer_coaching_support", "focal")],
                3: [("group_mediation", "focal")],
                4: [("clarify_roles_and_handoffs", "focal")],
                5: [("quick_check_in", "focal")],
                6: [("group_mediation", "focal")],
            })),
            ("more_strain_than_needed", self._run_actions("scenario_01", {
                1: [("quick_check_in", "focal")],
                2: [("group_mediation", "focal")],
                3: [("quick_check_in", "focal"), ("quick_check_in", "hidden")],
                4: [("clarify_roles_and_handoffs", "focal"), ("quick_check_in", "hidden")],
                5: [("quick_check_in", "focal")],
                6: [("quick_check_in", "hidden")],
            })),
            ("well_done", self._run_actions("scenario_01", {
                1: [("quick_check_in", "focal"), ("clarify_roles_and_handoffs", "focal")],
                2: [("offer_coaching_support", "focal"), ("group_mediation", "focal")],
                3: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
                4: [("clarify_roles_and_handoffs", "focal"), ("quick_check_in", "hidden")],
                5: [("quick_check_in", "focal")],
                6: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
            })),
        ]

        expected_outcomes = {
            "spiralled": "Management Review: The launch was not controlled well enough.",
            "high_strain_count": "Management Review: You got the launch through, but not strongly enough.",
            "more_strain_than_needed": "Management Review: You recovered the situation, but later than we would want.",
            "well_done": "Management Review: This was a strong piece of management under pressure.",
        }

        for expected_path, game in cases:
            history = game.get_analysis_history()
            latest = history[-1]
            benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
            benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)

            authored_copy = scenario_end_screen_copy(game, history, latest, benchmark_history, benchmark_latest)
            self.assertIsNotNone(authored_copy)
            self.assertEqual(authored_copy["outcome"], expected_outcomes[expected_path])

    def test_scenario_01_week_one_individual_plus_coordination_on_jordan_gets_positive_weekend_note(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        focal = game.get_scenario_role_node_id("focal_employee")
        game.apply_player_action({"type": "quick_check_in", "target": focal})
        game.apply_player_action({"type": "clarify_roles_and_handoffs", "target": focal})
        game.end_week()

        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = {
            "week": 0,
            "scenario": game.scenario,
            "scenario_roles": dict(game.scenario_state.get("scenario_roles", {})),
            "employees": latest["employees"],
        }
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("group around him looked steadier", week_note[0])

        second_game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        second_focal = second_game.get_scenario_role_node_id("focal_employee")
        second_game.apply_player_action({"type": "offer_coaching_support", "target": second_focal})
        second_game.apply_player_action({"type": "group_mediation", "target": second_focal})
        second_game.end_week()

        second_history = second_game.get_analysis_history()
        second_latest = second_history[-1]
        second_previous_snapshot = {
            "week": 0,
            "scenario": second_game.scenario,
            "scenario_roles": dict(second_game.scenario_state.get("scenario_roles", {})),
            "employees": second_latest["employees"],
        }
        second_benchmark_history = build_benchmark_history(second_game, benchmark_name="stabilising_response")
        second_benchmark_latest = _analysis_snapshot_for_week(second_benchmark_history, second_latest["week"])
        second_week_note = scenario_week_end_report(
            second_game,
            second_latest,
            second_previous_snapshot,
            second_benchmark_history,
            second_benchmark_latest,
        )

        self.assertIsNotNone(second_week_note)
        self.assertIn("group around him looked steadier", second_week_note[0])

    def test_scenario_01_weeks_three_to_six_strong_action_rules_match_authored_path(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        focal = game.get_scenario_role_node_id("focal_employee")
        hidden = game.get_scenario_role_node_id("hidden_strain_employee")

        strong_cases = [
            (3, "group_mediation", focal),
            (3, "quick_check_in", hidden),
            (4, "clarify_roles_and_handoffs", focal),
            (4, "offer_coaching_support", hidden),
            (5, "quick_check_in", focal),
            (5, "group_mediation", focal),
            (6, "offer_coaching_support", focal),
            (6, "surface_hidden_support_work", hidden),
        ]

        for week, action_type, node in strong_cases:
            self.assertEqual(
                authored_action_quality(game, action_type, node=node, week=week),
                "strong",
                msg=f"Expected week {week} action {action_type} to be strong",
            )

    def test_scenario_01_week_two_individual_plus_coordination_on_jordan_stays_positive(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        focal = game.get_scenario_role_node_id("focal_employee")
        game.apply_player_action({"type": "quick_check_in", "target": focal})
        game.apply_player_action({"type": "clarify_roles_and_handoffs", "target": focal})
        game.end_week()

        previous_snapshot = game.get_analysis_history()[-1]
        game.apply_player_action({"type": "offer_coaching_support", "target": focal})
        game.apply_player_action({"type": "group_mediation", "target": focal})
        game.end_week()

        latest = game.get_analysis_history()[-1]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("launch pressure looked more manageable", week_note[0].lower())

    def test_scenario_01_week_two_main_screen_aside_reflects_strong_opening(self):
        game = self._run_actions_until_week("scenario_01", {
            1: [("quick_check_in", "focal"), ("clarify_roles_and_handoffs", "focal")],
        }, stop_week=1)
        vm = build_weekly_view_model(game)

        self.assertIn("steadied the group around jordan", vm.briefing_aside.lower())

    def test_sidebar_demo_buttons_are_not_rendered(self):
        original_test_mode = os.environ.pop("MANAGEMENT_SIM_TEST_MODE", None)
        try:
            app = AppTest.from_file("/Users/james/Supress The Stress/app.py")
            app.run(timeout=20)
            labels = [button.label for button in app.sidebar.button]
            self.assertNotIn("Restart Scenario", labels)
            self.assertNotIn("Demo: Spiralled", labels)
            self.assertNotIn("Demo: High Strain Count", labels)
            self.assertNotIn("Demo: More Strain Than Needed", labels)
            self.assertNotIn("Demo: Well Done", labels)
        finally:
            if original_test_mode is not None:
                os.environ["MANAGEMENT_SIM_TEST_MODE"] = original_test_mode

    def test_scenario_01_week_three_coordination_on_jordan_plus_individual_on_sam_stays_positive(self):
        game = self._run_actions_until_week("scenario_01", {
            1: [("quick_check_in", "focal"), ("clarify_roles_and_handoffs", "focal")],
            2: [("offer_coaching_support", "focal"), ("group_mediation", "focal")],
            3: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
        }, stop_week=3)
        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = history[-2]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("launch could have hardened", week_note[0].lower())

    def test_scenario_01_week_five_action_on_jordan_stays_positive(self):
        game = self._run_actions_until_week("scenario_01", {
            1: [("quick_check_in", "focal"), ("clarify_roles_and_handoffs", "focal")],
            2: [("offer_coaching_support", "focal"), ("group_mediation", "focal")],
            3: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
            4: [("clarify_roles_and_handoffs", "focal"), ("quick_check_in", "hidden")],
            5: [("quick_check_in", "focal")],
        }, stop_week=5)
        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = history[-2]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("about as steady as it realistically could", week_note[0].lower())

    def test_scenario_01_week_six_action_on_jordan_plus_individual_on_sam_stays_positive(self):
        game = self._run_actions_until_week("scenario_01", {
            1: [("quick_check_in", "focal"), ("clarify_roles_and_handoffs", "focal")],
            2: [("offer_coaching_support", "focal"), ("group_mediation", "focal")],
            3: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
            4: [("clarify_roles_and_handoffs", "focal"), ("quick_check_in", "hidden")],
            5: [("quick_check_in", "focal")],
            6: [("group_mediation", "focal"), ("quick_check_in", "hidden")],
        }, stop_week=6)
        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = history[-2]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("launch reached the final week under pressure", week_note[0].lower())

    def test_scenario_01_high_strain_count_does_not_get_strong_overlay_language(self):
        game = self._run_actions_until_week("scenario_01", {
            1: [("quick_check_in", "focal")],
            2: [("offer_coaching_support", "focal")],
            3: [("group_mediation", "focal")],
        }, stop_week=3)
        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = history[-2]
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        self.assertIn("team is paying more for it than it should", week_note[0].lower())
        self.assertNotIn("right level of intervention", " ".join(week_note).lower())

    def test_scenario_01_no_action_uses_no_action_overlay_language(self):
        game = GameState(
            scenario="scenario_01",
            difficulty="Normal",
            team_size=SCENARIOS["scenario_01"].team_size,
            max_weeks=SCENARIOS["scenario_01"].length,
            seed=0,
        )
        game.end_week()

        history = game.get_analysis_history()
        latest = history[-1]
        previous_snapshot = {
            "week": 0,
            "scenario": game.scenario,
            "scenario_roles": dict(game.scenario_state.get("scenario_roles", {})),
            "employees": latest["employees"],
        }
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, latest["week"])
        week_note = scenario_week_end_report(game, latest, previous_snapshot, benchmark_history, benchmark_latest)

        self.assertIsNotNone(week_note)
        combined = " ".join(week_note).lower()
        self.assertIn("needed a clearer intervention", combined)
        self.assertNotIn("too narrow", combined)


if __name__ == "__main__":
    unittest.main()
