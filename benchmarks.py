import random

from action_registry import action_cost
from game_logic import GameState
from reporting import build_benchmark_history, _analysis_snapshot_for_week, determine_summary_branch
from scenario_copy import scenario_01_explicit_route_path
from scenario_definitions import SCENARIOS
from scenario_runtime import apply_recommended_actions_for_week


def _try_apply(game, action):
    action_type = action["type"]
    if game.manager_state["energy_current"] >= action_cost(action_type):
        game.apply_player_action(action)


def _scenario_one_route_actions(route_name, week, focal, hidden):
    if route_name == "blind":
        return []
    if route_name == "high_strain_count":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "offer_coaching_support", "target": focal}],
            3: [{"type": "group_mediation", "target": focal}],
            4: [{"type": "clarify_roles_and_handoffs", "target": focal}],
            5: [{"type": "quick_check_in", "target": focal}],
            6: [{"type": "group_mediation", "target": focal}],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "more_strain_than_needed":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "group_mediation", "target": focal}],
            3: [
                {"type": "quick_check_in", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            4: [
                {"type": "clarify_roles_and_handoffs", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            5: [{"type": "quick_check_in", "target": focal}],
            6: [{"type": "quick_check_in", "target": hidden}],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "well_done":
        route = {
            1: [
                {"type": "quick_check_in", "target": focal},
                {"type": "clarify_roles_and_handoffs", "target": focal},
            ],
            2: [
                {"type": "offer_coaching_support", "target": focal},
                {"type": "group_mediation", "target": focal},
            ],
            3: [
                {"type": "group_mediation", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            4: [
                {"type": "clarify_roles_and_handoffs", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            5: [{"type": "quick_check_in", "target": focal}],
            6: [
                {"type": "group_mediation", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "visible_only":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "offer_coaching_support", "target": focal}],
            3: [{"type": "reduce_workload", "target": focal}],
            4: [{"type": "quick_check_in", "target": focal}],
            5: [{"type": "offer_coaching_support", "target": focal}],
            6: [{"type": "quick_check_in", "target": focal}],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "late_shift":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "offer_coaching_support", "target": focal}],
            3: [
                {"type": "group_mediation", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            4: [
                {"type": "clarify_roles_and_handoffs", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
            5: [{"type": "quick_check_in", "target": hidden}],
            6: [
                {"type": "clarify_roles_and_handoffs", "target": focal},
                {"type": "quick_check_in", "target": hidden},
            ],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "early_read":
        return None
    raise ValueError(f"Unknown scenario_01 route: {route_name}")


def _scenario_two_route_actions(route_name, week, focal, hidden, anchor):
    if route_name == "blind":
        return []
    if route_name == "visible_only":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "offer_coaching_support", "target": focal}],
            3: [{"type": "reduce_workload", "target": focal}],
            4: [{"type": "quick_check_in", "target": focal}],
            5: [{"type": "offer_coaching_support", "target": focal}],
            6: [{"type": "quick_check_in", "target": focal}],
        }
        return [action for action in route.get(week, []) if action.get("target") is not None]
    if route_name == "late_shift":
        route = {
            1: [{"type": "quick_check_in", "target": focal}],
            2: [{"type": "offer_coaching_support", "target": focal}],
            3: [{"type": "check_in_on_load_bearing_risk", "target": hidden}],
            4: [
                {"type": "reallocate_workload", "target": {"from": hidden, "to": anchor}},
                {"type": "clarify_roles_and_handoffs", "target": hidden},
            ],
            5: [{"type": "quick_check_in", "target": hidden}],
            6: [{"type": "do_nothing", "target": None}],
        }
        return [
            action for action in route.get(week, [])
            if action.get("type") == "do_nothing"
            or action.get("target") is not None
            or (action.get("type") == "reallocate_workload" and anchor is not None)
        ]
    if route_name == "early_read":
        return None
    raise ValueError(f"Unknown scenario_02 route: {route_name}")


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
        focal = game.get_scenario_role_node_id("focal_employee")
        hidden = game.get_scenario_role_node_id("hidden_strain_employee")
        anchor = game.get_scenario_role_node_id("cluster_anchor")

        if game.scenario == "scenario_01":
            scenario_one_route = {
                "none": "blind",
                "relieve": "visible_only",
                "mixed": "late_shift",
                "recommended": "early_read",
            }.get(route_name, route_name)
            scenario_one_actions = _scenario_one_route_actions(scenario_one_route, week, focal, hidden)
            if scenario_one_actions is None:
                apply_recommended_actions_for_week(game)
            else:
                for action in scenario_one_actions:
                    _try_apply(game, action)
            game.end_week()
            continue

        if game.scenario == "scenario_02":
            scenario_two_route = {
                "none": "blind",
                "relieve": "visible_only",
                "mixed": "late_shift",
                "recommended": "early_read",
            }.get(route_name, route_name)
            scenario_two_actions = _scenario_two_route_actions(scenario_two_route, week, focal, hidden, anchor)
            if scenario_two_actions is None:
                apply_recommended_actions_for_week(game)
            else:
                for action in scenario_two_actions:
                    _try_apply(game, action)
            game.end_week()
            continue

        if route_name == "none":
            pass
        elif route_name == "recommended":
            apply_recommended_actions_for_week(game)
        elif route_name == "relieve":
            if week in {1, 3}:
                _try_apply(game, {"type": "reduce_workload", "target": focal})
                _try_apply(game, {"type": "quick_check_in", "target": focal})
            elif week in {2, 4, 5, 6}:
                _try_apply(game, {"type": "offer_coaching_support", "target": focal})
                _try_apply(game, {"type": "quick_check_in", "target": focal})
        elif route_name == "mixed":
            if week == 1:
                _try_apply(game, {"type": "group_mediation", "target": focal})
                _try_apply(game, {"type": "quick_check_in", "target": focal})
            elif week == 2:
                _try_apply(game, {"type": "clarify_roles_and_handoffs", "target": focal})
                _try_apply(game, {"type": "offer_coaching_support", "target": focal})
            elif week in {3, 4, 5, 6}:
                _try_apply(game, {"type": "quick_check_in", "target": focal})
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


def autoplay_demo_route_for_outcome_randomized(route_name, desired_tier, scenario_key, attempts=40):
    fallback_game = None
    rng = random.SystemRandom()
    for _ in range(attempts):
        seed = rng.randrange(0, 1_000_000_000)
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        fallback_game = game
        history = game.get_analysis_history()
        latest = history[-1] if history else {}
        if latest.get("scenario_outcome_tier") == desired_tier:
            return game
    deterministic_game = autoplay_demo_route_for_outcome(
        route_name,
        desired_tier,
        scenario_key,
        seeds=range(1000),
    )
    deterministic_history = deterministic_game.get_analysis_history() if deterministic_game else []
    deterministic_latest = deterministic_history[-1] if deterministic_history else {}
    if deterministic_latest.get("scenario_outcome_tier") == desired_tier:
        return deterministic_game
    raise RuntimeError(
        f"Unable to find demo route for outcome '{desired_tier}' in scenario '{scenario_key}'."
    )


def autoplay_demo_route_for_summary_branch_randomized(route_name, desired_branch, scenario_key, attempts=40):
    fallback_game = None
    rng = random.SystemRandom()
    for _ in range(attempts):
        seed = rng.randrange(0, 1_000_000_000)
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        fallback_game = game
        history = game.get_analysis_history()
        latest = history[-1] if history else {}
        benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
        benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)
        if determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest) == desired_branch:
            return game
    deterministic_game = autoplay_demo_route_for_summary_branch(
        route_name,
        desired_branch,
        scenario_key,
        seeds=range(1000),
    )
    deterministic_history = deterministic_game.get_analysis_history() if deterministic_game else []
    deterministic_latest = deterministic_history[-1] if deterministic_history else {}
    deterministic_benchmark_history = build_benchmark_history(
        deterministic_game,
        benchmark_name="stabilising_response",
    ) if deterministic_game else []
    deterministic_benchmark_latest = _analysis_snapshot_for_week(
        deterministic_benchmark_history,
        deterministic_game.max_weeks,
    ) if deterministic_game else None
    if deterministic_game and determine_summary_branch(
        deterministic_game,
        deterministic_history,
        deterministic_latest,
        deterministic_benchmark_history,
        deterministic_benchmark_latest,
    ) == desired_branch:
        return deterministic_game
    raise RuntimeError(
        f"Unable to find demo route for summary branch '{desired_branch}' in scenario '{scenario_key}'."
    )


def autoplay_demo_route_for_explicit_path_randomized(route_name, desired_path, scenario_key, attempts=40):
    fallback_game = None
    rng = random.SystemRandom()
    for _ in range(attempts):
        seed = rng.randrange(0, 1_000_000_000)
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        fallback_game = game
        history = game.get_analysis_history()
        if scenario_key == "scenario_01" and scenario_01_explicit_route_path(history) == desired_path:
            return game
    for seed in range(1000):
        game = autoplay_demo_route(route_name, seed=seed, scenario_key=scenario_key)
        history = game.get_analysis_history()
        if scenario_key == "scenario_01" and scenario_01_explicit_route_path(history) == desired_path:
            return game
    raise RuntimeError(
        f"Unable to find demo route for explicit path '{desired_path}' in scenario '{scenario_key}'."
    )
