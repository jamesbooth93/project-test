from action_registry import action_category, action_cost, action_label
from scenario_scripts import STORY_BUILDERS, WEEK_BIAS_APPLIERS
from scenario_rules import scenario_route_active, select_outcome_key_and_tier


def _clean_analysis_lede(text: str) -> str:
    prefixes = (
        "A more effective response here was to ",
        "That was an effective response because it ",
    )
    for prefix in prefixes:
        if text.startswith(prefix):
            parts = text.split(". ", 1)
            if len(parts) == 2:
                return parts[1]
    return text


def _week_tactics_sentence(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    for prefix in ("use ", "using "):
        lowered = cleaned.lower()
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    cleaned = cleaned.replace(", alongside ", " together with ")
    cleaned = cleaned.replace(", while also using ", " together with ")
    cleaned = cleaned.replace(" while also using ", " together with ")
    return f"One strong move here was to use {cleaned}"


def recommended_actions_for_week(game, week=None):
    selected_week = game.week if week is None else week
    runtime_preset = getattr(game.scenario_definition, "runtime_preset", {}) or {}
    return runtime_preset.get("recommended_actions_by_week", {}).get(selected_week, [])


def apply_recommended_actions_for_week(game, week=None):
    for action_spec in recommended_actions_for_week(game, week):
        action_type = action_spec[0]
        if action_type == "do_nothing":
            if game.manager_state["energy_current"] >= action_cost(action_type):
                game.apply_player_action({"type": action_type, "target": None})
            continue
        if action_type == "reallocate_workload" and len(action_spec) >= 3:
            from_target = game.get_scenario_role_node_id(action_spec[1])
            to_target = game.get_scenario_role_node_id(action_spec[2])
            if from_target is None or to_target is None:
                continue
            if game.manager_state["energy_current"] >= action_cost(action_type):
                game.apply_player_action({"type": action_type, "target": {"from": from_target, "to": to_target}})
            continue

        role_name = action_spec[1]
        target = game.get_scenario_role_node_id(role_name)
        if target is None:
            continue
        if game.manager_state["energy_current"] >= action_cost(action_type):
            game.apply_player_action({"type": action_type, "target": target})


def _matches_action_quality_rule(game, rule, action_type, node, secondary_node=None):
    if rule.get("action_types") and action_type not in set(rule.get("action_types", [])):
        return False
    roles = game.scenario_state.get("scenario_roles", {})
    target_role = rule.get("target_role")
    if target_role is not None and roles.get(target_role) != node:
        return False
    secondary_target_role = rule.get("secondary_target_role")
    if secondary_target_role is not None and roles.get(secondary_target_role) != secondary_node:
        return False
    return True


def authored_action_quality(game, action_type, node=None, secondary_node=None, week=None):
    selected_week = game.week if week is None else week
    runtime_preset = getattr(game.scenario_definition, "runtime_preset", {}) or {}
    quality_rules = runtime_preset.get("action_quality_by_week", {}).get(selected_week, [])
    for rule in quality_rules:
        if _matches_action_quality_rule(game, rule, action_type, node, secondary_node=secondary_node):
            return rule.get("quality")
    return None


def apply_benchmark_actions_for_week(game, benchmark_name):
    if benchmark_name == "no_intervention":
        game.end_week()
        return

    focal = game.get_scenario_role_node_id("focal_employee")
    hidden = game.get_scenario_role_node_id("hidden_strain_employee")
    anchor = game.get_scenario_role_node_id("cluster_anchor")

    if benchmark_name == "misread_response":
        if focal is not None and game.manager_state["energy_current"] >= action_cost("reduce_workload"):
            game.apply_player_action({"type": "reduce_workload", "target": focal})
        if focal is not None and game.manager_state["energy_current"] >= action_cost("quick_check_in"):
            game.apply_player_action({"type": "quick_check_in", "target": focal})
        game.end_week()
        return

    if benchmark_name == "mixed_response":
        if game.week % 2 == 1:
            if focal is not None and game.manager_state["energy_current"] >= action_cost("quick_check_in"):
                game.apply_player_action({"type": "quick_check_in", "target": focal})
            if hidden is not None and game.manager_state["energy_current"] >= action_cost("group_mediation"):
                game.apply_player_action({"type": "group_mediation", "target": hidden})
        else:
            if focal is not None and game.manager_state["energy_current"] >= action_cost("reduce_workload"):
                game.apply_player_action({"type": "reduce_workload", "target": focal})
            if (
                hidden is not None
                and anchor is not None
                and hidden != anchor
                and game.manager_state["energy_current"] >= action_cost("reallocate_workload")
            ):
                game.apply_player_action({
                    "type": "reallocate_workload",
                    "target": {"from": hidden, "to": anchor},
                })
        game.end_week()
        return

    if benchmark_name == "stabilising_response":
        apply_recommended_actions_for_week(game)
        game.end_week()
        return

    raise ValueError(f"Unknown benchmark_name: {benchmark_name}")


def strategy_aligned_with_recommendation(snapshot, week=None):
    if not snapshot:
        return False

    selected_week = snapshot.get("week") if week is None else week
    recommended_actions = snapshot.get("recommended_actions", [])
    if not recommended_actions:
        return False

    actions = snapshot.get("actions_taken", [])
    if not actions and all(
        recommended_action.get("type") == "do_nothing"
        for recommended_action in recommended_actions
    ):
        return True

    def matches_recommended(action, recommended_action):
        if action.get("type") != recommended_action.get("type"):
            return False
        if action.get("type") == "reallocate_workload":
            return (
                (action.get("target") or {}).get("from_id") == recommended_action.get("target_id")
                and (action.get("target") or {}).get("to_id") == recommended_action.get("to_target_id")
            )
        if action.get("type") == "do_nothing":
            return True
        return ((action.get("target") or {}).get("id") == recommended_action.get("target_id"))

    matched_count = sum(
        1
        for recommended_action in recommended_actions
        if any(matches_recommended(action, recommended_action) for action in actions)
    )
    required_matches = len(recommended_actions)
    if required_matches > 1:
        required_matches -= 1
    return matched_count >= required_matches


def strategy_aligned_through_week(history, week):
    if not history or week is None or week <= 0:
        return False

    snapshots_by_week = {
        snapshot.get("week"): snapshot
        for snapshot in history
        if snapshot.get("week") is not None and snapshot.get("week") <= week
    }
    for prior_week in range(1, week + 1):
        snapshot = snapshots_by_week.get(prior_week)
        if snapshot is None or not strategy_aligned_with_recommendation(snapshot, prior_week):
            return False
    return True


def player_ahead_of_benchmark(game, snapshot, benchmark_snapshot):
    if not snapshot or not benchmark_snapshot:
        return False

    if game.scenario == "scenario_02":
        hidden_id = snapshot.get("scenario_roles", {}).get("hidden_strain_employee")
        hidden_row = next((row for row in snapshot.get("employees", []) if row.get("id") == hidden_id), None)
        benchmark_hidden_row = next((row for row in benchmark_snapshot.get("employees", []) if row.get("id") == hidden_id), None)
        if hidden_row is None or benchmark_hidden_row is None:
            return False
        player_load = float(hidden_row.get("absorbed_workload", 0.0))
        benchmark_load = float(benchmark_hidden_row.get("absorbed_workload", 0.0))
        return player_load <= benchmark_load + 0.02

    cluster_ids = set(snapshot.get("scenario_roles", {}).values())
    cluster_ids.discard(None)
    if not cluster_ids:
        return False

    def cluster_avg(current_snapshot):
        values = [
            float(row.get("true_strain", 0.0))
            for row in current_snapshot.get("employees", [])
            if row.get("id") in cluster_ids
        ]
        return (sum(values) / len(values)) if values else None

    player_avg = cluster_avg(snapshot)
    benchmark_avg = cluster_avg(benchmark_snapshot)
    if player_avg is None or benchmark_avg is None:
        return False
    return player_avg <= benchmark_avg + 0.01


def recommended_analysis_copy(game, snapshot=None, week=None, history=None, benchmark_snapshot=None, force_reinforcing=False):
    selected_week = game.week if week is None else week
    runtime_preset = getattr(game.scenario_definition, "runtime_preset", {}) or {}
    templates = runtime_preset.get("recommended_analysis_copy", {})
    if not templates:
        return ""

    def join_with_and(items):
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return f"{', '.join(items[:-1])}, and {items[-1]}"

    def role_name(role_key, fallback):
        node_id = game.get_scenario_role_node_id(role_key)
        if node_id is None:
            return fallback
        return game.G.nodes[node_id].get("name", fallback)

    if selected_week == 0:
        opening_template = templates.get("opening", "")
        if not opening_template:
            return ""
        return opening_template.format(
            focal=role_name("focal_employee", "the focal employee"),
            hidden=role_name("hidden_strain_employee", "the quieter employee"),
            spillover=role_name("spillover_employee", "the nearby teammate"),
            anchor=role_name("cluster_anchor", "the cluster anchor"),
        )

    recommended_action_labels = []
    for action_spec in recommended_actions_for_week(game, selected_week):
        action_type = action_spec[0]
        if action_type == "do_nothing":
            recommended_action_labels.append(action_label(action_type))
            continue
        if action_type == "reallocate_workload" and len(action_spec) >= 3:
            from_name = role_name(action_spec[1], "Team")
            to_name = role_name(action_spec[2], "Team")
            recommended_action_labels.append(f"{action_label(action_type)} ({from_name} -> {to_name})")
        else:
            recommended_action_labels.append(
                f"{action_label(action_type)} ({role_name(action_spec[1], 'Team')})"
            )
    recommended_actions_text = join_with_and(recommended_action_labels)
    openers = runtime_preset.get("recommended_analysis_openers", {})
    aligned = strategy_aligned_through_week(history, selected_week) if history else False
    outperforming = player_ahead_of_benchmark(game, snapshot, benchmark_snapshot) if snapshot and benchmark_snapshot else False
    reinforcing = force_reinforcing or aligned or outperforming
    template_group = templates.get("reinforcing" if reinforcing else "corrective", {})
    template = template_group.get(selected_week, "")
    if not template:
        return ""

    week_tactics_templates = runtime_preset.get("recommended_week_tactics", {})
    week_tactics = week_tactics_templates.get(selected_week, recommended_actions_text)
    if "{" in week_tactics:
        week_tactics = week_tactics.format(
            focal=role_name("focal_employee", "the focal employee"),
            hidden=role_name("hidden_strain_employee", "the quieter employee"),
            spillover=role_name("spillover_employee", "the nearby teammate"),
            anchor=role_name("cluster_anchor", "the cluster anchor"),
        )

    tactics_sentence = _week_tactics_sentence(week_tactics)

    rendered = template.format(
        focal=role_name("focal_employee", "the focal employee"),
        hidden=role_name("hidden_strain_employee", "the quieter employee"),
        spillover=role_name("spillover_employee", "the nearby teammate"),
        anchor=role_name("cluster_anchor", "the cluster anchor"),
        recommended_actions=recommended_actions_text,
        week_tactics=week_tactics,
        week_tactics_sentence=tactics_sentence,
    )
    cleaned = _clean_analysis_lede(rendered)
    opener = openers.get(selected_week, "")
    if opener:
        opener = opener.format(
            focal=role_name("focal_employee", "the focal employee"),
            hidden=role_name("hidden_strain_employee", "the quieter employee"),
            spillover=role_name("spillover_employee", "the nearby teammate"),
            anchor=role_name("cluster_anchor", "the cluster anchor"),
        )
        return f"{opener} {cleaned}"
    return cleaned


def update_scenario_progress(game, action_type, node=None, action_categories=None):
    action_categories = action_categories or {}
    category = action_categories.get(action_type)
    runtime_preset = getattr(game.scenario_definition, "runtime_preset", {}) or {}
    progress_rules = runtime_preset.get("action_progress_rules", [])
    roles = game.scenario_state.get("scenario_roles", {})

    for rule in progress_rules:
        if _progress_rule_matches(game, rule, action_type, node, category, roles):
            for counter_name, amount in (rule.get("increments") or {}).items():
                game.scenario_state[counter_name] = game.scenario_state.get(counter_name, 0) + amount
            if rule.get("append_week_to"):
                counter_name = rule["append_week_to"]
                game.scenario_state.setdefault(counter_name, []).append(game.week)

    game.scenario_state["acceptable_route_active"] = scenario_route_active(game, "acceptable")
    game.scenario_state["great_manager_path_active"] = scenario_route_active(game, "mastery")


def apply_authored_trajectory_shaping(game):
    if game.scenario != "scenario_01":
        return
    from scenario_copy import scenario_weekly_narrative_path

    snapshot = {
        "week": game.week,
        "actions_taken": game.current_week_actions[:],
        "scenario_roles": dict(game.scenario_state.get("scenario_roles", {})),
    }
    history = game.get_analysis_history()
    weekly_path = scenario_weekly_narrative_path(game, history, snapshot)
    if not weekly_path:
        return

    per_path_adjustments = {
        "well_done": {
            "focal_employee": -0.018,
            "hidden_strain_employee": -0.026,
            "spillover_employee": -0.022,
            "cluster_anchor": -0.018,
        },
        "more_strain_than_needed": {
            "focal_employee": -0.010,
            "hidden_strain_employee": -0.014,
            "spillover_employee": -0.010,
            "cluster_anchor": -0.008,
        },
        "high_strain_count": {
            "focal_employee": -0.012,
            "hidden_strain_employee": 0.010,
            "spillover_employee": 0.012,
            "cluster_anchor": 0.008,
        },
        "spiralled": {
            "focal_employee": 0.012,
            "hidden_strain_employee": 0.020,
            "spillover_employee": 0.022,
            "cluster_anchor": 0.016,
        },
    }

    adjustments = per_path_adjustments.get(weekly_path, {})
    if not adjustments:
        return

    week_scalars = {
        1: 0.85,
        2: 0.95,
        3: 1.10,
        4: 1.10,
        5: 1.00,
        6: 0.95,
    }
    scalar = week_scalars.get(game.week, 1.0)
    roles = game.scenario_state.get("scenario_roles", {})

    for role_name, base_delta in adjustments.items():
        node_id = roles.get(role_name)
        if node_id is None or node_id not in game.G.nodes:
            continue
        node = game.G.nodes[node_id]
        node["strain"] = min(1.0, max(0.0, float(node.get("strain", 0.0)) + (base_delta * scalar)))


def _progress_rule_matches(game, rule, action_type, node, category, roles):
    if rule.get("category") and rule.get("category") != category:
        return False
    if rule.get("action_types") and action_type not in set(rule.get("action_types", [])):
        return False
    if rule.get("week_lte") is not None and game.week > rule["week_lte"]:
        return False
    if rule.get("week_gte") is not None and game.week < rule["week_gte"]:
        return False

    target_role = rule.get("target_role")
    if target_role is not None and roles.get(target_role) != node:
        return False

    node_in_roles = rule.get("node_in_roles")
    if node_in_roles:
        allowed_nodes = {roles.get(role_name) for role_name in node_in_roles}
        if node not in allowed_nodes:
            return False

    return True


def qualifies_for_conflict_cluster_survive(game):
    return scenario_route_active(game, "acceptable")


def qualifies_for_conflict_cluster_mastery(game):
    return scenario_route_active(game, "mastery")


def evaluate_scenario_outcome(game):
    if game.scenario == "Baseline":
        return
    if not game.game_over and game.week < game.max_weeks:
        game.scenario_outcome_tier = None
        game.scenario_outcome_title = None
        game.scenario_outcome_explanation = ""
        game.scenario_outcome_strength = ""
        game.scenario_outcome_improvement = ""
        return

    game.scenario_mastery_reveal = game.scenario_definition.mastery_rule.get("description", "")
    selected_key, selected_tier = select_outcome_key_and_tier(game)

    if selected_tier is None or selected_key is None:
        game.scenario_outcome_tier = None
        game.scenario_outcome_title = None
        game.scenario_outcome_explanation = ""
        game.scenario_outcome_strength = ""
        game.scenario_outcome_improvement = ""
        return

    outcome_copy = game.scenario_definition.runtime_preset.get("outcome_copy", {}).get(selected_key, {})
    game.scenario_outcome_tier = selected_tier.label
    game.scenario_outcome_title = outcome_copy.get(
        "title",
        "The situation spiralled." if selected_tier.label == "Fail" else "You managed the situation.",
    )
    game.scenario_outcome_explanation = selected_tier.explanation
    game.scenario_outcome_strength = outcome_copy.get("strength", "")
    game.scenario_outcome_improvement = outcome_copy.get("improvement", selected_tier.upgrade_message)


def build_scenario_story_data(game):
    builder = STORY_BUILDERS.get(game.scenario)
    if builder:
        return builder(game)

    return {
        "what_you_chose": "You managed the week based on the signals available to you.",
        "how_it_landed": "The week moved according to the pressure already in the system.",
        "what_shifted": "The team remains in motion.",
        "what_to_watch": "Keep watching for where visible signals and hidden strain begin to diverge.",
        "response_style": game._classify_weekly_response_style(),
    }


def apply_scenario_week_bias(game):
    applier = WEEK_BIAS_APPLIERS.get(game.scenario)
    if applier:
        applier(game)
