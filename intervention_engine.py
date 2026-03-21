import numpy as np

from action_registry import ACTION_REGISTRY, action_cost, is_team_wide
from simulation_engine import choose_intervention_strategy_from_behaviors


LEGACY_ACTION_EFFECT_ALIASES = {
    "stabilise_visible_contributor": "offer_coaching_support",
    "protect_key_contributor_capacity": "reduce_workload",
    "clarify_ownership_boundaries": "clarify_roles_and_handoffs",
    "reset_escalation_paths": "group_mediation",
    "reassign_hidden_glue_work": "clarify_roles_and_handoffs",
}


def resolve_effect_action(action_type: str) -> str:
    return LEGACY_ACTION_EFFECT_ALIASES.get(action_type, action_type)


SUCCESS_SUMMARIES = {
    "quick_check_in": "Quick check-in landed well with {name} and gave you a little more clarity.",
    "reduce_workload": "Adjusting priorities helped take some pressure off {name} immediately.",
    "reallocate_workload": "Reallocating work from {name} to {to_name} reduced some immediate pressure.",
    "offer_coaching_support": "Coaching support steadied {name} and made them feel more resilient.",
    "group_mediation": "Resolving tensions eased some of the strain around {name} and nearby colleagues.",
    "clarify_roles_and_handoffs": "Clarifying roles and handoffs reduced strain around {name}.",
    "stabilise_visible_contributor": "Supporting {name} reduced some of the visible week-to-week friction around their work.",
    "check_in_on_load_bearing_risk": "Checking capacity with {name} gave you a clearer sense of how manageable their workload really is.",
    "surface_hidden_support_work": "Reviewing how work is flowing around {name} gave you a much better read on where work keeps getting caught and picked back up.",
    "protect_key_contributor_capacity": "Protecting {name}'s capacity gave them immediate breathing room and took some hidden load off them.",
    "clarify_ownership_boundaries": "Clarifying ownership boundaries reduced the amount of work quietly drifting back toward {name}.",
    "reset_escalation_paths": "Resetting escalation paths reduced how often issues automatically flowed through {name}.",
    "reassign_hidden_glue_work": "Reassigning hidden glue work reduced how much invisible coordination had been resting on {name}.",
}

PARTIAL_SUMMARIES = {
    "quick_check_in": "The check-in helped with {name}, but only a little.",
    "reduce_workload": "Adjusting priorities bought {name} some breathing room.",
    "reallocate_workload": "Moving work from {name} to {to_name} helped a little, but created some tradeoffs elsewhere.",
    "offer_coaching_support": "Coaching support helped {name}, but not enough to change wider patterns.",
    "group_mediation": "The conversation softened tension, but did not fully settle it.",
    "clarify_roles_and_handoffs": "Clarifying roles helped somewhat, but the group still feels unsettled.",
    "stabilise_visible_contributor": "Supporting {name} reduced some visible friction, but the wider pattern still feels unstable.",
    "check_in_on_load_bearing_risk": "Checking capacity with {name} gave you some useful context, but not enough to fully clarify what they are carrying.",
    "surface_hidden_support_work": "Reviewing how work is flowing around {name} helped somewhat, but the full pattern is still murky.",
    "protect_key_contributor_capacity": "Protecting {name}'s capacity bought some breathing room, but it did not yet change the wider dependency pattern.",
    "clarify_ownership_boundaries": "Ownership is a little clearer around {name}, but work still seems to drift back their way.",
    "reset_escalation_paths": "Some escalation pressure came off {name}, but the old habits are still partly in place.",
    "reassign_hidden_glue_work": "Some hidden glue work came off {name}, but too much still appears to flow back to them.",
}

BACKFIRE_SUMMARIES = {
    "quick_check_in": "The check-in landed badly with {name} and left you more confused.",
    "reduce_workload": "Trying to adjust priorities created friction around {name} and did not land well.",
    "reallocate_workload": "Moving work from {name} to {to_name} created more friction than relief.",
    "offer_coaching_support": "Coaching support landed badly with {name} and reduced trust.",
    "group_mediation": "The conversation created more tension around {name}.",
    "clarify_roles_and_handoffs": "The roles-and-handoffs intervention added confusion around {name} instead of easing it.",
    "stabilise_visible_contributor": "Trying to steady {name} created more friction than it removed.",
    "check_in_on_load_bearing_risk": "The conversation about capacity made {name} feel scrutinized rather than supported.",
    "surface_hidden_support_work": "Reviewing how work is flowing around {name} created defensiveness instead of clarity.",
    "protect_key_contributor_capacity": "Protecting {name}'s capacity created confusion about who was supposed to pick up the work.",
    "clarify_ownership_boundaries": "Trying to clarify ownership around {name} created more argument than clarity.",
    "reset_escalation_paths": "Resetting escalation routes around {name} created confusion and slowed the team down.",
    "reassign_hidden_glue_work": "Trying to reassign glue work away from {name} created friction without enough clarity.",
}

FAILURE_SUMMARIES = {
    "quick_check_in": "The check-in barely changed the situation for {name}.",
    "reduce_workload": "Adjusting priorities had little lasting effect for {name}.",
    "reallocate_workload": "Moving work from {name} to {to_name} changed very little this week.",
    "offer_coaching_support": "Coaching support helped very little this week.",
    "group_mediation": "The conversation did not meaningfully change anything this week.",
    "clarify_roles_and_handoffs": "Clarifying roles had no meaningful effect.",
    "stabilise_visible_contributor": "Supporting {name} changed very little about the visible friction this week.",
    "check_in_on_load_bearing_risk": "Checking capacity with {name} stayed inconclusive, but it still suggested there may be more going on beneath the surface.",
    "surface_hidden_support_work": "Reviewing how work is flowing around {name} stayed noisy, but it still pointed to work getting caught in the same places.",
    "protect_key_contributor_capacity": "Protecting {name}'s capacity had less effect than you needed.",
    "clarify_ownership_boundaries": "Ownership still feels blurry around {name}.",
    "reset_escalation_paths": "Issues still kept routing through {name} despite the attempted reset.",
    "reassign_hidden_glue_work": "Most of the hidden glue work still appears to be sitting with {name}.",
}

DIAGNOSTIC_ACTIONS = {
    "check_in_on_load_bearing_risk",
    "surface_hidden_support_work",
}


def visible_workload_value(game, node):
    return float(game._player_facing_workload_value(game.G.nodes[node]))


def adjust_visible_workload(game, node, delta):
    if game.scenario != "scenario_02":
        return
    game.G.nodes[node]["scenario_display_load"] = float(np.clip(
        game.G.nodes[node].get("scenario_display_load", 0.0) + delta,
        0.0,
        1.0,
    ))


def diagnostic_signal_quality(game, node, action_type, fit):
    workload = visible_workload_value(game, node)
    dependency = min(1.0, 0.2 * len(list(game.G.neighbors(node))))
    if action_type == "check_in_on_load_bearing_risk":
        score = 0.55 * fit + 0.30 * workload + 0.15 * float(game.G.nodes[node].get("engagement", 0.0) < 0.55)
    else:
        score = 0.50 * fit + 0.30 * workload + 0.20 * dependency
    if score >= 0.72:
        return "clear"
    if score >= 0.45:
        return "weak"
    return "noisy"


def build_capacity_signal(game, node, signal_quality):
    person = game.G.nodes[node]
    workload = visible_workload_value(game, node)
    recent = person.get("recent_behaviors", [])[-3:]
    if signal_quality == "clear":
        if workload >= 0.45:
            return "They say they can keep going, but they are carrying more than is obvious from the outside."
        if recent:
            return f"They sound fairly steady, but their recent pattern still shows strain: {', '.join(recent)}."
        return "They sound composed, but there is still more pressure sitting with them than they are letting on."
    if signal_quality == "weak":
        if recent:
            return f"They describe things as manageable, but there are hints of strain in the week so far: {', '.join(recent)}."
        return "They present it as manageable, but there are signs this may be costing them more than they are saying."
    return "They describe things as manageable, but the picture is still mixed and may be masking hidden load."


def build_workflow_signal(game, node, signal_quality):
    person = game.G.nodes[node]
    neighbors = sorted(
        list(game.G.neighbors(node)),
        key=lambda nbr: game.G.edges[node, nbr].get("weight", 0.0),
        reverse=True,
    )
    connected_names = [game.G.nodes[nbr]["name"] for nbr in neighbors[:3]]
    dependency_count = len([nbr for nbr in neighbors if game.G.edges[node, nbr].get("weight", 0.0) >= 0.28])
    if signal_quality == "clear":
        if connected_names:
            return f"Work appears to keep routing back through them, especially around {', '.join(connected_names)}."
        return "Work appears to keep routing back through them more often than the formal roles suggest."
    if signal_quality == "weak":
        if dependency_count >= 2:
            return f"There are signs that work is sticking to them across multiple handoffs, especially with {dependency_count} nearby dependencies."
        return "There are signs that they are quietly picking up work when things slip, but the pattern is only partly visible."
    return "The flow still looks messy, but it suggests the same person may be catching problems more often than expected."


def explain_outcome(game, node, action_type, fit, success_prob, backfire_prob, outcome, secondary_node=None):
    drivers = []
    secondary = []
    relationship = game.G.nodes[node]["manager_relationship"]
    manager_strain = game.manager_state["strain"]
    employee_strain = game.G.nodes[node]["strain"]
    workload = visible_workload_value(game, node)

    if fit >= 0.7:
        drivers.append("This was a strong match for the underlying issue")
    elif fit >= 0.45:
        pass
    else:
        drivers.append("This did not match the underlying issue closely")

    if relationship >= 0.65:
        drivers.append("Trust helped the conversation land")
    elif relationship < 0.4:
        secondary.append("Low trust reduced the impact")

    if workload >= 0.45 and action_type in DIAGNOSTIC_ACTIONS | {"reduce_workload", "reallocate_workload"}:
        drivers.append("There was enough pressure here for the pattern to show up clearly")

    if manager_strain > 0.6:
        secondary.append("High manager pressure reduced intervention quality")

    if employee_strain > 0.72 and action_type in {"quick_check_in", "check_in_on_load_bearing_risk"}:
        secondary.append("The situation was already quite escalated for a lighter intervention")

    if action_type == "reallocate_workload" and secondary_node is not None:
        to_node = game.G.nodes[secondary_node]
        if to_node["strain"] > 0.6:
            secondary.append(f"Moving work onto {to_node['name']} carried extra risk")
        else:
            drivers.append(f"{to_node['name']} had enough room to absorb some of the work")

    confidence_score = 0.5 * fit + 0.3 * success_prob + 0.2 * (1 - backfire_prob)
    if action_type in DIAGNOSTIC_ACTIONS:
        signal_quality = diagnostic_signal_quality(game, node, action_type, fit)
        if signal_quality == "clear":
            drivers.append("The signal came through clearly")
        elif signal_quality == "weak":
            secondary.append("The signal was there, but only faintly")
        else:
            secondary.append("The signal was noisy, so this only gave you a partial read")
        if action_type == "check_in_on_load_bearing_risk":
            diagnostic_read = build_capacity_signal(game, node, signal_quality)
        else:
            diagnostic_read = build_workflow_signal(game, node, signal_quality)
    else:
        signal_quality = None
        diagnostic_read = None

    if confidence_score >= 0.72:
        confidence = "strong"
    elif confidence_score >= 0.48:
        confidence = "mixed"
    else:
        confidence = "noisy"

    return {
        "primary_drivers": drivers[:3],
        "secondary_factors": secondary[:3],
        "confidence": confidence,
        "signal_quality": signal_quality,
        "diagnostic_read": diagnostic_read,
        "outcome_label": outcome,
    }


def format_outcome_explanation(explanation):
    if not explanation:
        return ""
    parts = []
    primary = explanation.get("primary_drivers") or []
    secondary = explanation.get("secondary_factors") or []
    confidence = explanation.get("confidence")
    signal_quality = explanation.get("signal_quality")

    if primary:
        parts.append(primary[0])
    if secondary:
        parts.append(secondary[0])
    if signal_quality:
        if signal_quality == "clear":
            parts.append("You got a clear read from it")
        elif signal_quality == "weak":
            parts.append("It gave you a weak but usable signal")
        else:
            parts.append("It gave you a noisy signal rather than a clear answer")
    elif confidence == "strong":
        parts.append("The result was fairly dependable")
    elif confidence == "noisy":
        parts.append("The result was more context-sensitive than it first looked")
    return "Why: " + " ".join(parts) if parts else ""


def apply_player_action(game, action):
    action_type = action.get("type", "do_nothing")
    target = action.get("target", None)

    if not game.current_week_actions:
        game.event_log = []

    if action_type == "do_nothing":
        game.last_action_summary = "You saved your energy for another week."
        game.event_log.append(game.last_action_summary)
        game._record_action_outcome(action_type, None, "success", 1.0, 0.0, game.last_action_summary)
        return game.last_action_summary

    if action_type not in ACTION_REGISTRY:
        game.last_action_summary = f"Unknown action: {action_type}. No action taken."
        return game.last_action_summary

    if action_type == "reallocate_workload":
        if not isinstance(target, dict):
            game.last_action_summary = "Choose who to take work from and who should take it on."
            return game.last_action_summary
        from_node = target.get("from")
        to_node = target.get("to")
        if from_node is None or to_node is None or from_node == to_node:
            game.last_action_summary = "Choose two different people to reallocate workload."
            return game.last_action_summary
        if from_node not in game.G.nodes() or to_node not in game.G.nodes():
            game.last_action_summary = "Invalid workload reallocation targets."
            return game.last_action_summary

    if not is_team_wide(action_type) and target is None:
        game.last_action_summary = "No target selected. No action taken."
        return game.last_action_summary

    if action_type != "reallocate_workload" and not is_team_wide(action_type) and target not in game.G.nodes():
        game.last_action_summary = "Invalid employee target. No action taken."
        return game.last_action_summary

    energy_cost = action_cost(action_type)
    if game.manager_state["energy_current"] < energy_cost:
        game.last_action_summary = f"You did not have enough energy left for {action_type.replace('_', ' ')}."
        return game.last_action_summary

    game.manager_state["energy_current"] = max(
        0.0,
        game.manager_state["energy_current"] - energy_cost,
    )

    if is_team_wide(action_type):
        if action_type == "team_meeting":
            helped = manual_team_meeting(game)
            for node in helped:
                game._mark_supported(node, "Joined the team meeting.", success=True)
            summary = "You gathered the whole team to reset alignment and steady engagement."
        else:
            manual_stress_management_workshop(game)
            summary = "You booked a stress management workshop. It will take a few weeks before any benefit shows."
        game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] - 0.01, 0, 1))
        game.last_action_summary = summary
        explanation = {
            "primary_drivers": ["This reset the whole team rather than one person"],
            "secondary_factors": [],
            "confidence": "strong",
            "signal_quality": None,
            "outcome_label": "success",
        }
        game._record_action_outcome(action_type, None, "success", 1.0, energy_cost, game.last_action_summary, explanation=explanation)
        game.event_log.append(game.last_action_summary)
        return game.last_action_summary

    if action_type == "reallocate_workload":
        from_node = target["from"]
        to_node = target["to"]
        from_name = game.G.nodes[from_node]["name"]
        to_name = game.G.nodes[to_node]["name"]
        fit = intervention_fit_score(game, from_node, action_type, secondary_node=to_node)
        outcome_info = resolve_intervention_outcome(game, from_node, action_type, fit, secondary_node=to_node)
        outcome = outcome_info["outcome"]
        if outcome == "success":
            manual_reallocate_workload(game, from_node, to_node, strength=1.0, fit=fit)
            game._shift_relationship(from_node, 0.02 * game._role_mod(from_node, "relationship_gain"))
            game._shift_relationship(to_node, 0.01 * game._role_mod(to_node, "relationship_gain"))
            game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] - 0.01, 0, 1))
            summary = SUCCESS_SUMMARIES[action_type].format(name=from_name, to_name=to_name)
        elif outcome == "partial":
            manual_reallocate_workload(game, from_node, to_node, strength=0.6, fit=fit)
            summary = PARTIAL_SUMMARIES[action_type].format(name=from_name, to_name=to_name)
        elif outcome == "backfire":
            apply_backfire(game, from_node, fit)
            apply_backfire(game, to_node, fit * 0.8)
            game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] + 0.05, 0, 1))
            summary = BACKFIRE_SUMMARIES[action_type].format(name=from_name, to_name=to_name)
        else:
            manual_reallocate_workload(game, from_node, to_node, strength=0.2, fit=fit)
            game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] + 0.02, 0, 1))
            summary = FAILURE_SUMMARIES[action_type].format(name=from_name, to_name=to_name)

        target_override = {
            "id": from_node,
            "name": f"{from_name} -> {to_name}",
            "role": f"{game.G.nodes[from_node]['role']} -> {game.G.nodes[to_node]['role']}",
            "from_id": from_node,
            "to_id": to_node,
            "from_name": from_name,
            "to_name": to_name,
        }
        game.last_action_summary = summary
        game.event_log.append(summary)
        game._record_action_outcome(
            action_type,
            from_node,
            outcome,
            fit,
            energy_cost,
            summary,
            target_override=target_override,
            explanation=outcome_info["explanation"],
        )
        return game.last_action_summary

    node = target
    name = game.G.nodes[node]["name"]
    fit = intervention_fit_score(game, node, action_type)
    outcome_info = resolve_intervention_outcome(game, node, action_type, fit)
    outcome = outcome_info["outcome"]

    if outcome == "success":
        apply_intervention_effect(game, action_type, node, strength=1.0, fit=fit)
        game._shift_relationship(node, 0.03 * game._role_mod(node, "relationship_gain"))
        game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] - 0.02, 0, 1))
        game._mark_supported(node, f"Received {action_type.replace('_', ' ')}.", success=True)
        summary = SUCCESS_SUMMARIES.get(action_type, "The intervention helped {name}.").format(name=name)
    elif outcome == "partial":
        apply_intervention_effect(game, action_type, node, strength=0.55, fit=fit)
        game._shift_relationship(node, 0.01 * game._role_mod(node, "relationship_gain"))
        game._mark_supported(node, f"Received partial {action_type.replace('_', ' ')}.", success=True)
        summary = PARTIAL_SUMMARIES.get(action_type, "The intervention helped a little with {name}.").format(name=name)
    elif outcome == "backfire":
        apply_backfire(game, node, fit)
        game._shift_relationship(node, -0.05)
        game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] + 0.04, 0, 1))
        game._mark_supported(node, f"{action_type.replace('_', ' ').title()} backfired.", success=False)
        summary = BACKFIRE_SUMMARIES.get(action_type, "The intervention created more friction around {name}.").format(name=name)
    else:
        apply_intervention_effect(game, action_type, node, strength=0.15, fit=fit)
        game._shift_relationship(node, -0.02)
        game.manager_state["strain"] = float(np.clip(game.manager_state["strain"] + 0.02, 0, 1))
        game._mark_supported(node, f"{action_type.replace('_', ' ').title()} had little effect.", success=False)
        summary = FAILURE_SUMMARIES.get(action_type, "The intervention had little effect for {name}.").format(name=name)

    game.last_action_summary = summary
    game.event_log.append(summary)
    game._record_action_outcome(action_type, node, outcome, fit, energy_cost, summary, explanation=outcome_info["explanation"])
    return game.last_action_summary


def manual_quick_check_in(game, node, strength=1.0):
    eff = max(strength, 0.0)
    game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.02 * eff)
    game.G.nodes[node]["trust"] = float(np.clip(game.G.nodes[node]["trust"] + 0.05 * eff, 0, 1))
    game.G.nodes[node]["manager_relationship"] = float(np.clip(
        game.G.nodes[node]["manager_relationship"] + 0.04 * eff,
        0.10,
        0.95,
    ))
    game.G.nodes[node]["visibility_boost_weeks"] = max(game.G.nodes[node].get("visibility_boost_weeks", 0), 1)


def manual_check_capacity(game, node, strength=1.0):
    eff = max(strength, 0.0)
    game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.015 * eff)
    game.G.nodes[node]["trust"] = float(np.clip(game.G.nodes[node]["trust"] + 0.06 * eff, 0, 1))
    game.G.nodes[node]["manager_relationship"] = float(np.clip(
        game.G.nodes[node]["manager_relationship"] + 0.05 * eff,
        0.10,
        0.95,
    ))
    game.G.nodes[node]["visibility_boost_weeks"] = max(game.G.nodes[node].get("visibility_boost_weeks", 0), 3)
    game.G.nodes[node]["recovery_boost_weeks"] = max(game.G.nodes[node].get("recovery_boost_weeks", 0), 1)


def manual_review_workflow(game, node, strength=1.0):
    eff = max(strength, 0.0)
    neighbors = list(game.G.neighbors(node))
    ranked_neighbors = sorted(
        neighbors,
        key=lambda nbr: game.G.edges[node, nbr].get("weight", 0.0),
        reverse=True,
    )[:4]

    game.G.nodes[node]["alignment"] = float(np.clip(game.G.nodes[node]["alignment"] + 0.04 * eff, 0, 1))
    game.G.nodes[node]["visibility_boost_weeks"] = max(game.G.nodes[node].get("visibility_boost_weeks", 0), 4)

    for nbr in ranked_neighbors:
        game.G.nodes[nbr]["visibility_boost_weeks"] = max(game.G.nodes[nbr].get("visibility_boost_weeks", 0), 3)
        game.G.nodes[nbr]["alignment"] = float(np.clip(game.G.nodes[nbr]["alignment"] + 0.03 * eff, 0, 1))
        game.G.nodes[nbr]["trust"] = float(np.clip(game.G.nodes[nbr]["trust"] + 0.01 * eff, 0, 1))

    # A better workflow read makes hidden carrying work more legible without directly "solving" it.
    game.G.nodes[node]["last_absorbed_workload"] = max(
        game.G.nodes[node].get("last_absorbed_workload", 0.0),
        game.G.nodes[node].get("absorbed_workload", 0.0),
    )


def manual_reduce_workload(game, node, strength=1.0):
    eff = max(strength, 0.0)
    game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.14 * eff)
    game.G.nodes[node]["resources"] += 1.5 * eff
    game.G.nodes[node]["workload_buffer_weeks"] = max(game.G.nodes[node].get("workload_buffer_weeks", 0), 3)
    game.G.nodes[node]["recovery_boost_weeks"] = max(game.G.nodes[node].get("recovery_boost_weeks", 0), 2)
    game.G.nodes[node]["absorbed_workload"] = max(0.0, game.G.nodes[node].get("absorbed_workload", 0.0) - 0.16 * eff)
    game.G.nodes[node]["last_absorbed_workload"] = max(0.0, game.G.nodes[node].get("last_absorbed_workload", 0.0) - 0.10 * eff)
    adjust_visible_workload(game, node, -(0.16 * eff))

    neighbors = list(game.G.neighbors(node))
    if neighbors:
        selected = sorted(neighbors, key=lambda nbr: game.G.nodes[nbr]["strain"])[: min(3, len(neighbors))]
        share = 0.12 * eff
        for nbr in selected:
            game.G.nodes[nbr]["strain"] = float(np.clip(game.G.nodes[nbr]["strain"] + 0.015 * eff, 0, 1))
            game.G.nodes[nbr]["absorbed_workload"] += share
            adjust_visible_workload(game, nbr, share)


def manual_reallocate_workload(game, from_node, to_node, strength=1.0, fit=1.0):
    eff = max(strength, 0.0) * (0.70 + 0.30 * fit)
    shifted_load = 0.24 * eff
    from_data = game.G.nodes[from_node]
    to_data = game.G.nodes[to_node]

    from_data["strain"] = max(0, from_data["strain"] - 0.08 * eff)
    from_data["absorbed_workload"] = max(0.0, from_data.get("absorbed_workload", 0.0) - shifted_load)
    from_data["last_absorbed_workload"] = max(0.0, from_data.get("last_absorbed_workload", 0.0) - shifted_load * 0.75)
    adjust_visible_workload(game, from_node, -shifted_load)

    to_data["strain"] = float(np.clip(to_data["strain"] + 0.05 * eff, 0, 1))
    to_data["absorbed_workload"] = to_data.get("absorbed_workload", 0.0) + shifted_load
    to_data["last_absorbed_workload"] = to_data.get("last_absorbed_workload", 0.0) + shifted_load * 0.75
    to_data["workload_buffer_weeks"] = max(to_data.get("workload_buffer_weeks", 0), 1)
    adjust_visible_workload(game, to_node, shifted_load)

    hidden = game.scenario_state.get("scenario_roles", {}).get("hidden_strain_employee")
    if hidden is not None and to_node == hidden:
        to_data["strain"] = float(np.clip(to_data["strain"] + 0.04 * eff, 0, 1))
    if hidden is not None and from_node == hidden:
        from_data["recovery_boost_weeks"] = max(from_data.get("recovery_boost_weeks", 0), 2)


def manual_offer_coaching_support(game, node, strength=1.0):
    eff = max(strength, 0.0)
    game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.08 * eff)
    game.G.nodes[node]["engagement"] = float(np.clip(game.G.nodes[node]["engagement"] + 0.12 * eff, 0, 1))
    game.G.nodes[node]["trust"] = float(np.clip(game.G.nodes[node]["trust"] + 0.08 * eff, 0, 1))
    game.G.nodes[node]["manager_relationship"] = float(np.clip(
        game.G.nodes[node]["manager_relationship"] + 0.03 * eff,
        0.10,
        0.95,
    ))
    game.G.nodes[node]["recovery_boost_weeks"] = max(game.G.nodes[node].get("recovery_boost_weeks", 0), 3)
    game.G.nodes[node]["relapse_protection_weeks"] = max(game.G.nodes[node].get("relapse_protection_weeks", 0), 3)


def manual_group_mediation(game, node, strength=1.0):
    eff = max(strength, 0.0)
    neighbors = list(game.G.neighbors(node))
    game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.06 * eff)
    game.G.nodes[node]["alignment"] = float(np.clip(game.G.nodes[node]["alignment"] + 0.06 * eff, 0, 1))
    game.G.nodes[node]["spillover_block_weeks"] = max(game.G.nodes[node].get("spillover_block_weeks", 0), 2)
    for nbr in neighbors:
        game.G.edges[node, nbr]["weight"] = float(np.clip(
            game.G.edges[node, nbr].get("weight", 0.0) + 0.08 * eff,
            0,
            1,
        ))
        game.G.nodes[nbr]["strain"] = max(0, game.G.nodes[nbr]["strain"] - 0.04 * eff)
        game.G.nodes[nbr]["alignment"] = float(np.clip(game.G.nodes[nbr]["alignment"] + 0.05 * eff, 0, 1))
        game.G.nodes[nbr]["trust"] = float(np.clip(game.G.nodes[nbr]["trust"] + 0.03 * eff, 0, 1))
        game.G.nodes[nbr]["spillover_block_weeks"] = max(game.G.nodes[nbr].get("spillover_block_weeks", 0), 2)


def manual_clarify_roles_and_handoffs(game, node, strength=1.0):
    eff = max(strength, 0.0)
    affected = [node] + list(game.G.neighbors(node))
    for current in affected:
        game.G.nodes[current]["alignment"] = float(np.clip(
            game.G.nodes[current]["alignment"] + (0.08 if current == node else 0.06) * eff,
            0,
            1,
        ))
        game.G.nodes[current]["strain"] = max(
            0,
            game.G.nodes[current]["strain"] - (0.01 if current == node else 0.02) * eff,
        )
        game.G.nodes[current]["spillover_block_weeks"] = max(game.G.nodes[current].get("spillover_block_weeks", 0), 3)
        game.G.nodes[current]["recovery_boost_weeks"] = max(game.G.nodes[current].get("recovery_boost_weeks", 0), 2)
    for neighbor in list(game.G.neighbors(node)):
        game.G.edges[node, neighbor]["weight"] = float(np.clip(
            game.G.edges[node, neighbor].get("weight", 0.0) + 0.04 * eff,
            0,
            1,
        ))


def manual_team_meeting(game):
    helped = []
    for node in game.managed_node_ids():
        game.G.nodes[node]["engagement"] = float(np.clip(game.G.nodes[node]["engagement"] + 0.03, 0, 1))
        game.G.nodes[node]["alignment"] = float(np.clip(game.G.nodes[node]["alignment"] + 0.06, 0, 1))
        game.G.nodes[node]["trust"] = float(np.clip(game.G.nodes[node]["trust"] + 0.02, 0, 1))
        game.G.nodes[node]["strain"] = max(0, game.G.nodes[node]["strain"] - 0.015)
        helped.append(node)
    return helped


def manual_stress_management_workshop(game):
    game.pending_team_effects.append({
        "type": "stress_management_workshop",
        "apply_week": game.week + 2,
    })


def apply_intervention_effect(game, action_type, node, strength, fit):
    effective_strength = strength * (0.65 + 0.35 * fit) * game._role_mod(node, "intervention_leverage")
    resolved_action_type = resolve_effect_action(action_type)
    if action_type == "check_in_on_load_bearing_risk":
        manual_check_capacity(game, node, strength=0.95 * effective_strength)
    elif action_type == "surface_hidden_support_work":
        manual_review_workflow(game, node, strength=0.92 * effective_strength)
    elif resolved_action_type == "quick_check_in":
        manual_quick_check_in(game, node, strength=0.95 * effective_strength)
    elif resolved_action_type == "reduce_workload":
        manual_reduce_workload(game, node, strength=0.92 * effective_strength)
        if action_type == "protect_key_contributor_capacity":
            game.G.nodes[node]["absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("absorbed_workload", 0.0) - 0.35 * effective_strength,
            )
            game.G.nodes[node]["last_absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("last_absorbed_workload", 0.0) - 0.25 * effective_strength,
            )
            game.G.nodes[node]["recovery_boost_weeks"] = max(game.G.nodes[node].get("recovery_boost_weeks", 0), 3)
            adjust_visible_workload(game, node, -(0.35 * effective_strength))
    elif resolved_action_type == "offer_coaching_support":
        manual_offer_coaching_support(game, node, strength=0.90 * effective_strength)
    elif resolved_action_type == "group_mediation":
        manual_group_mediation(game, node, strength=0.88 * effective_strength)
        if action_type == "reset_escalation_paths":
            for neighbor in list(game.G.neighbors(node)):
                game.G.edges[node, neighbor]["weight"] = float(np.clip(
                    game.G.edges[node, neighbor].get("weight", 0.0) - 0.04 * effective_strength,
                    0.06,
                    1.0,
                ))
        if game.scenario == "scenario_02" and node == game.scenario_state.get("scenario_roles", {}).get("hidden_strain_employee"):
            game.G.nodes[node]["absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("absorbed_workload", 0.0) - 0.10 * effective_strength,
            )
            adjust_visible_workload(game, node, -(0.10 * effective_strength))
    elif resolved_action_type == "clarify_roles_and_handoffs":
        manual_clarify_roles_and_handoffs(game, node, strength=0.86 * effective_strength)
        if action_type == "clarify_ownership_boundaries":
            game.G.nodes[node]["absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("absorbed_workload", 0.0) - 0.18 * effective_strength,
            )
            adjust_visible_workload(game, node, -(0.18 * effective_strength))
        if action_type == "reassign_hidden_glue_work":
            game.G.nodes[node]["absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("absorbed_workload", 0.0) - 0.40 * effective_strength,
            )
            game.G.nodes[node]["last_absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("last_absorbed_workload", 0.0) - 0.30 * effective_strength,
            )
            for neighbor in list(game.G.neighbors(node))[:3]:
                game.G.nodes[neighbor]["absorbed_workload"] += 0.06 * effective_strength
                adjust_visible_workload(game, neighbor, 0.06 * effective_strength)
            adjust_visible_workload(game, node, -(0.40 * effective_strength))
        if game.scenario == "scenario_02" and node == game.scenario_state.get("scenario_roles", {}).get("hidden_strain_employee"):
            game.G.nodes[node]["absorbed_workload"] = max(
                0.0,
                game.G.nodes[node].get("absorbed_workload", 0.0) - 0.12 * effective_strength,
            )
            adjust_visible_workload(game, node, -(0.12 * effective_strength))


def apply_backfire(game, node, fit):
    game.G.nodes[node]["strain"] = float(np.clip(
        game.G.nodes[node]["strain"] + 0.02 + 0.04 * (1 - fit),
        0,
        1,
    ))
    game.G.nodes[node]["engagement"] = float(np.clip(game.G.nodes[node]["engagement"] - 0.05, 0, 1))
    game.G.nodes[node]["trust"] = float(np.clip(game.G.nodes[node]["trust"] - 0.04, 0, 1))
    game.G.nodes[node]["alignment"] = float(np.clip(game.G.nodes[node]["alignment"] - 0.03, 0, 1))


def _scenario_action_fit_adjustment(game, node, action_type, secondary_node=None):
    adjustment = 0.0
    roles = game.scenario_state.get("scenario_roles", {})
    focal = roles.get("focal_employee")
    hidden = roles.get("hidden_strain_employee")

    if game.scenario == "scenario_01":
        if action_type in {"group_mediation", "clarify_roles_and_handoffs"}:
            if node == focal or node == hidden:
                adjustment += 0.22
        if action_type in {"check_in_on_load_bearing_risk", "surface_hidden_support_work"}:
            if node == focal:
                adjustment -= 0.08
            if node == hidden:
                adjustment += 0.06
        if action_type == "reduce_workload":
            if node == focal:
                adjustment += 0.03
            else:
                adjustment -= 0.08
        if action_type == "reallocate_workload":
            adjustment -= 0.16

    if game.scenario == "scenario_02":
        if action_type in {"check_in_on_load_bearing_risk", "surface_hidden_support_work"}:
            if node == hidden:
                adjustment += 0.24
            if node == focal:
                adjustment -= 0.06
        if action_type == "reduce_workload":
            if node == hidden:
                adjustment += 0.24
            if node == focal:
                adjustment -= 0.05
        if action_type == "reallocate_workload" and secondary_node is not None:
            if node == hidden and secondary_node != hidden:
                adjustment += 0.20
            if secondary_node == hidden:
                adjustment -= 0.28
            if secondary_node == focal:
                adjustment -= 0.08
        if action_type in {"group_mediation", "clarify_roles_and_handoffs"}:
            if node == hidden:
                adjustment += 0.18
            if node == focal:
                adjustment -= 0.04
        if action_type == "offer_coaching_support":
            if node == focal:
                adjustment += 0.05
            if node == hidden:
                adjustment += 0.08
        if action_type == "quick_check_in":
            if node == focal:
                adjustment += 0.04
            if node == hidden:
                adjustment += 0.10

    return adjustment


def intervention_fit_score(game, node, action_type, secondary_node=None):
    recommended = choose_intervention_strategy_from_behaviors(game.G, node)
    recent = game.G.nodes[node].get("recent_behaviors", [])[-5:]
    fit = 0.45
    recommended_map = {
        "workload_relief": "reduce_workload",
        "manager_support": "quick_check_in",
        "team_mediation": "group_mediation",
        "capacity_building": "offer_coaching_support",
    }
    resolved_action_type = resolve_effect_action(action_type)
    if resolved_action_type == recommended_map.get(recommended):
        fit += 0.35
    if resolved_action_type == "reduce_workload" and any(b in recent for b in ["overload_signal", "sick_day"]):
        fit += 0.18
    if resolved_action_type == "group_mediation" and any(b in recent for b in ["complaint", "ignored_email"]):
        fit += 0.18
    if resolved_action_type == "quick_check_in" and any(b in recent for b in ["engagement_drop", "lateness", "complaint"]):
        fit += 0.15
    if resolved_action_type == "offer_coaching_support" and any(b in recent for b in ["engagement_drop", "ignored_email", "lateness", "high_error_rate"]):
        fit += 0.18
    if action_type == "check_in_on_load_bearing_risk":
        fit += 0.08
        if any(b in recent for b in ["engagement_drop", "lateness", "complaint", "overload_signal"]):
            fit += 0.12
        fit += 0.06 * visible_workload_value(game, node)
    if action_type == "surface_hidden_support_work":
        fit += 0.10
        fit += 0.06 * min(4, len(list(game.G.neighbors(node))))
        if any(b in recent for b in ["complaint", "ignored_email", "high_error_rate"]):
            fit += 0.08
        fit += 0.08 * visible_workload_value(game, node)
    if resolved_action_type == "clarify_roles_and_handoffs":
        fit += 0.12 + 0.08 * min(3, len(list(game.G.neighbors(node))))
    if action_type == "reallocate_workload" and secondary_node is not None:
        secondary = game.G.nodes[secondary_node]
        fit += 0.18 * visible_workload_value(game, node)
        fit += 0.10 * max(0.0, 0.70 - secondary["strain"])
        if secondary_node == game.scenario_state.get("scenario_roles", {}).get("hidden_strain_employee"):
            fit -= 0.22
        if game.scenario_state.get("scenario_roles", {}).get("focal_employee") == secondary_node:
            fit -= 0.10
    if action_type in {"protect_key_contributor_capacity", "reassign_hidden_glue_work"}:
        fit += 0.14 * visible_workload_value(game, node)
    fit += _scenario_action_fit_adjustment(game, node, action_type, secondary_node=secondary_node)
    return float(np.clip(fit, 0.10, 1.0))


def resolve_intervention_outcome(game, node, action_type, fit, secondary_node=None):
    relationship = game.G.nodes[node]["manager_relationship"]
    manager_strain = game.manager_state["strain"]
    employee_strain = game.G.nodes[node]["strain"]
    recent_wrong = sum(
        1
        for entry in game.G.nodes[node].get("intervention_history", [])
        if entry["action"] != action_type and entry["outcome"] in {"failure", "backfire"}
    )
    success_prob = np.clip(
        0.15
        + 0.32 * relationship
        + 0.20 * game.manager_state["intervention_skill"]
        + 0.18 * fit
        + 0.08 * game.G.nodes[node]["manager_contact_frequency"]
        - 0.18 * manager_strain
        - 0.14 * max(0.0, employee_strain - 0.68)
        + 0.06 * game._role_mod(node, "intervention_leverage"),
        0.08,
        0.88,
    )
    backfire_prob = np.clip(
        0.03
        + 0.20 * (1 - relationship)
        + 0.18 * manager_strain
        + 0.16 * max(0.0, 0.55 - fit)
        + 0.12 * max(0.0, employee_strain - 0.75)
        + 0.05 * recent_wrong,
        0.02,
        0.55,
    )

    if game.rng.rand() < backfire_prob:
        outcome = "backfire"
        return {
            "outcome": outcome,
            "success_prob": float(success_prob),
            "backfire_prob": float(backfire_prob),
            "explanation": explain_outcome(
                game, node, action_type, fit, float(success_prob), float(backfire_prob), outcome, secondary_node=secondary_node
            ),
        }
    roll = game.rng.rand()
    if roll < success_prob:
        outcome = "success"
    elif roll < min(0.98, success_prob + 0.22):
        outcome = "partial"
    else:
        outcome = "failure"
    return {
        "outcome": outcome,
        "success_prob": float(success_prob),
        "backfire_prob": float(backfire_prob),
        "explanation": explain_outcome(
            game, node, action_type, fit, float(success_prob), float(backfire_prob), outcome, secondary_node=secondary_node
        ),
    }
