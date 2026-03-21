from action_registry import action_cost
from game_logic import GameState
from reporting import build_benchmark_history, _analysis_snapshot_for_week, determine_summary_branch
from scenario_definitions import SCENARIOS
from scenario_runtime import apply_recommended_actions_for_week


def autoplay_demo_route(route_name, seed, scenario_key):
    game = GameState(
        scenario=scenario_key,
        difficulty="Normal",
        team_size=SCENARIOS[scenario_key].team_size,
        max_weeks=SCENARIOS[scenario_key].length,
        seed=seed,
        debug=False,
    )
    while not game.game_over and game.week <= game.max_weeks:
        week = game.week
        if route_name == "none":
            pass
        elif route_name == "recommended":
            apply_recommended_actions_for_week(game)
        elif route_name == "relieve":
            focal = game.get_scenario_role_node_id("focal_employee")
            if week in {1, 3}:
                if game.manager_state["energy_current"] >= action_cost("reduce_workload"):
                    game.apply_player_action({"type": "reduce_workload", "target": focal})
                if game.manager_state["energy_current"] >= action_cost("quick_check_in"):
                    game.apply_player_action({"type": "quick_check_in", "target": focal})
            elif week in {2, 4, 5, 6}:
                if game.manager_state["energy_current"] >= action_cost("offer_coaching_support"):
                    game.apply_player_action({"type": "offer_coaching_support", "target": focal})
                if game.manager_state["energy_current"] >= action_cost("quick_check_in"):
                    game.apply_player_action({"type": "quick_check_in", "target": focal})
        elif route_name == "mixed":
            if game.scenario == "scenario_01":
                apply_recommended_actions_for_week(game)
            else:
                focal = game.get_scenario_role_node_id("focal_employee")
                if week == 1:
                    if game.manager_state["energy_current"] >= action_cost("group_mediation"):
                        game.apply_player_action({"type": "group_mediation", "target": focal})
                    if game.manager_state["energy_current"] >= action_cost("quick_check_in"):
                        game.apply_player_action({"type": "quick_check_in", "target": focal})
                elif week == 2:
                    if game.manager_state["energy_current"] >= action_cost("clarify_roles_and_handoffs"):
                        game.apply_player_action({"type": "clarify_roles_and_handoffs", "target": focal})
                    if game.manager_state["energy_current"] >= action_cost("offer_coaching_support"):
                        game.apply_player_action({"type": "offer_coaching_support", "target": focal})
                elif week in {3, 4, 5, 6}:
                    if game.manager_state["energy_current"] >= action_cost("quick_check_in"):
                        game.apply_player_action({"type": "quick_check_in", "target": focal})
        else:
            raise ValueError(f"Unknown demo route: {route_name}")

        game.end_week()

    return game


def autoplay_demo_route_for_outcome(route_name, desired_tier, scenario_key, seeds=range(10)):
    fallback_game = None
    for seed in seeds:
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        fallback_game = game
        history = game.get_analysis_history()
        latest = history[-1] if history else {}
        if latest.get("scenario_outcome_tier") == desired_tier:
            return game
    return fallback_game


def autoplay_demo_route_for_summary_branch(route_name, desired_branch, scenario_key, seeds=range(10)):
    fallback_game = None
    for seed in seeds:
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        fallback_game = game
        history = game.get_analysis_history()
        latest = history[-1] if history else {}
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)
        if determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest) == desired_branch:
            return game
    return fallback_game
