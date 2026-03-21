import os
import tempfile
import unittest

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="management_sim_mpl_"))
os.environ.setdefault("MANAGEMENT_SIM_TEST_MODE", "1")

from reporting import (
    BENCHMARK_CACHE,
    _analysis_snapshot_for_week,
    build_benchmark_history,
    determine_summary_branch,
)
from game_logic import GameState
from scenario_definitions import SCENARIOS
from scenario_runtime import apply_recommended_actions_for_week, strategy_aligned_with_recommendation


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


if __name__ == "__main__":
    unittest.main()
