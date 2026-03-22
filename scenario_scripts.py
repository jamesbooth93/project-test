import numpy as np


def build_baseline_story_data(game):
    return {
        "what_you_chose": "You managed the week based on the signals available to you.",
        "how_it_landed": "The week moved according to the pressure already in the system.",
        "what_shifted": "No single authored scenario was driving events this week.",
        "what_to_watch": "Keep watching for where visible signals and hidden strain begin to diverge.",
        "response_style": game._classify_weekly_response_style(),
    }


def build_conflict_cluster_story_data(game):
    style = game._classify_weekly_response_style()
    if style == "no_intervention":
        return {
            "what_you_chose": "You held back this week and let the situation play forward without a targeted response.",
            "how_it_landed": "The visible tension remained unresolved, and the cluster had room to harden.",
            "what_shifted": "More of the burden appears to be moving indirectly through the nearby delivery group.",
            "what_to_watch": "If that pattern continues, the next warning signs may come from someone quieter than the focal employee.",
            "response_style": style,
        }
    if style == "targeted_on_focal":
        return {
            "what_you_chose": "You responded directly to the clearest signs of overload from the focal employee.",
            "how_it_landed": "The immediate support helped on the surface, but it did not fully settle the surrounding pattern.",
            "what_shifted": "Pressure appears to be shifting outward through nearby working relationships rather than disappearing.",
            "what_to_watch": "Watch for quieter strain signals from colleagues connected to the focal issue.",
            "response_style": style,
        }
    if any(action["type"] == "offer_coaching_support" for action in game.current_week_actions):
        return {
            "what_you_chose": "You invested in a relationship-level read rather than only immediate firefighting.",
            "how_it_landed": "That did not solve the cluster directly, but it improved your read on where strain may surface next.",
            "what_shifted": "The visible focal point still matters, but the surrounding pattern may now be easier to read.",
            "what_to_watch": "Use that clearer signal to decide whether the local cluster itself needs stabilising.",
            "response_style": style,
        }
    if style == "cluster_stabilising":
        return {
            "what_you_chose": "You treated the issue as a local pattern rather than a single point of distress.",
            "how_it_landed": "The cluster began to stabilise, even if the visible focal employee still carried some pressure.",
            "what_shifted": "Local friction eased and the surrounding group looked less likely to absorb further strain.",
            "what_to_watch": "See whether the quieter members of the cluster recover, or whether tension starts to rebuild.",
            "response_style": style,
        }
    return {
        "what_you_chose": "You used a mixed response rather than committing to one level of intervention.",
        "how_it_landed": "Parts of the situation improved, but the cluster still looks unsettled.",
        "what_shifted": "The visible pressure changed shape without fully resolving the local instability.",
        "what_to_watch": "Pay attention to whether the next warning signs stay local or begin to spread.",
        "response_style": style,
    }


def build_quiet_high_performer_story_data(game):
    actions = game.current_week_actions
    roles = game.scenario_state.get("scenario_roles", {})
    focal_id = roles.get("focal_employee")
    hidden_id = roles.get("hidden_strain_employee")
    targeted_action_types = {
        "quick_check_in",
        "offer_coaching_support",
        "reduce_workload",
        "reallocate_workload",
        "check_in_on_load_bearing_risk",
        "surface_hidden_support_work",
    }
    clustered_action_types = {
        "group_mediation",
        "clarify_roles_and_handoffs",
    }

    targeted_on_focal = any(
        action["target"]["id"] == focal_id
        for action in actions
        if action.get("target") and action["type"] in targeted_action_types
    )
    targeted_on_hidden = any(
        action["target"]["id"] == hidden_id
        for action in actions
        if action.get("target") and action["type"] in targeted_action_types
    )
    clustered = any(action["type"] in clustered_action_types for action in actions)

    if not actions:
        return {
            "what_you_chose": "You waited another week and let the visible delivery wobble speak for itself.",
            "how_it_landed": "The obvious surface problem remained visible, while a few steadier people kept quietly helping the week land.",
            "what_shifted": "A steadier part of the team appears to keep picking up the settling and clarifying work in the background.",
            "what_to_watch": "If that continues, pay attention to who keeps making the team look more stable than it really is.",
            "response_style": "no_intervention",
        }
    if targeted_on_focal and not targeted_on_hidden and not clustered:
        return {
            "what_you_chose": "You responded to the teammate who looked like the clearest visible source of slippage.",
            "how_it_landed": "That helped at the surface, but much of the week still appears to have landed because a few steadier teammates helped absorb the messier edges.",
            "what_shifted": "The visible bottleneck softened slightly while the same steadier part of the team remained involved in several of the fixes.",
            "what_to_watch": "Watch not just who is noisy, but who keeps making the noise manageable for everyone else.",
            "response_style": "targeted_on_focal",
        }
    if targeted_on_hidden and not clustered:
        return {
            "what_you_chose": "You checked in with the person who appeared to be helping the whole week hold together.",
            "how_it_landed": "That gave the hidden carrier some support, but the wider pattern around them is still fragile.",
            "what_shifted": "It is a little clearer how often work keeps passing through the same dependable person before it lands cleanly.",
            "what_to_watch": "The next question is whether that person stays the helpful exception, or keeps becoming the default answer to everyone else's instability.",
            "response_style": "targeted_on_hidden",
        }
    if clustered:
        return {
            "what_you_chose": "You treated the issue as a pattern in how the team was leaning on one dependable person, not only a visible wobble from one teammate.",
            "how_it_landed": "That began to redistribute pressure and made the surrounding system a little less reliant on quiet rescue work.",
            "what_shifted": "The work now looks a little less concentrated in one dependable set of hands.",
            "what_to_watch": "See whether that relief holds, or whether the same exceptions drift back to the same person next week.",
            "response_style": "cluster_stabilising",
        }
    return {
        "what_you_chose": "You used a mixed response while still working out what level of problem you were dealing with.",
        "how_it_landed": "Some pressure moved, but the underlying pattern of who keeps carrying the work remains only partly addressed.",
        "what_shifted": "The visible symptoms changed shape without fully answering why the same dependable person keeps appearing at the point where work gets settled.",
        "what_to_watch": "Keep testing whether the system is becoming less dependent on that hidden carrier, or simply quieter about it.",
        "response_style": "mixed_response",
    }


def apply_conflict_cluster_week_bias(game):
    roles = game.scenario_state.get("scenario_roles", {})
    focal = roles.get("focal_employee")
    hidden = roles.get("hidden_strain_employee")
    spillover = roles.get("spillover_employee")
    anchor = roles.get("cluster_anchor")
    weekly_style = game._classify_weekly_response_style()

    if focal is None or hidden is None or spillover is None:
        return

    def add_behaviors(node_id, behaviors):
        current = game.G.nodes[node_id].get("recent_behaviors", [])
        for behavior in behaviors:
            if behavior not in current:
                current.append(behavior)
        game.G.nodes[node_id]["recent_behaviors"] = current[-5:]

    if game.week <= 3:
        add_behaviors(focal, ["complaint", "overload_signal"])
        add_behaviors(hidden, ["ignored_email"])
        game.G.nodes[spillover]["absorbed_workload"] += 0.14

    if weekly_style == "no_intervention":
        for node_id, bump in [(focal, 0.022), (hidden, 0.030), (spillover, 0.024)]:
            game.G.nodes[node_id]["strain"] = float(np.clip(game.G.nodes[node_id]["strain"] + bump, 0, 1))
        add_behaviors(focal, ["complaint"])
        add_behaviors(hidden, ["engagement_drop"])
        if anchor is not None:
            game.G.nodes[anchor]["alignment"] = float(np.clip(game.G.nodes[anchor]["alignment"] - 0.02, 0, 1))
    elif weekly_style == "targeted_on_focal":
        game.G.nodes[focal]["strain"] = float(np.clip(game.G.nodes[focal]["strain"] - 0.032, 0, 1))
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] + 0.014, 0, 1))
        game.G.nodes[spillover]["strain"] = float(np.clip(game.G.nodes[spillover]["strain"] + 0.012, 0, 1))
        game.G.nodes[spillover]["absorbed_workload"] += 0.12
        game.G.nodes[focal]["trust"] = float(np.clip(game.G.nodes[focal]["trust"] + 0.02, 0, 1))
        add_behaviors(spillover, ["overload_signal"])
        add_behaviors(hidden, ["ignored_email", "engagement_drop"])
    elif weekly_style == "cluster_stabilising":
        for node_id, drop in [(focal, 0.040), (hidden, 0.035), (spillover, 0.032)]:
            game.G.nodes[node_id]["strain"] = float(np.clip(game.G.nodes[node_id]["strain"] - drop, 0, 1))
        game.G.nodes[spillover]["absorbed_workload"] = max(0.0, game.G.nodes[spillover]["absorbed_workload"] - 0.22)
        if anchor is not None:
            game.G.nodes[anchor]["alignment"] = float(np.clip(game.G.nodes[anchor]["alignment"] + 0.04, 0, 1))
            game.G.nodes[anchor]["trust"] = float(np.clip(game.G.nodes[anchor]["trust"] + 0.02, 0, 1))
    else:
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] + 0.012, 0, 1))
        game.G.nodes[spillover]["absorbed_workload"] += 0.10

    if game.scenario_state.get("acceptable_route_active", False):
        game.G.nodes[focal]["strain"] = float(np.clip(game.G.nodes[focal]["strain"] - 0.028, 0, 1))
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] - 0.020, 0, 1))
        game.G.nodes[spillover]["strain"] = float(np.clip(game.G.nodes[spillover]["strain"] - 0.018, 0, 1))
        game.G.nodes[spillover]["absorbed_workload"] = max(0.0, game.G.nodes[spillover]["absorbed_workload"] - 0.12)
        if anchor is not None:
            game.G.nodes[anchor]["alignment"] = float(np.clip(game.G.nodes[anchor]["alignment"] + 0.02, 0, 1))

    game.scenario_state["benchmark_path_guess"] = game._classify_run_response_style()


def apply_quiet_high_performer_week_bias(game):
    roles = game.scenario_state.get("scenario_roles", {})
    focal = roles.get("focal_employee")
    hidden = roles.get("hidden_strain_employee")
    spillover = roles.get("spillover_employee")
    story_style = build_quiet_high_performer_story_data(game).get("response_style")

    if focal is None or hidden is None or spillover is None:
        return

    def add_behaviors(node_id, behaviors):
        current = game.G.nodes[node_id].get("recent_behaviors", [])
        for behavior in behaviors:
            if behavior not in current:
                current.append(behavior)
        game.G.nodes[node_id]["recent_behaviors"] = current[-5:]

    def redistribution_rotation(node_id, week):
        return ((sum(ord(char) for char in str(node_id)) + (week * 7)) % 9) / 100.0

    def redistribute_hidden_work(hidden_share):
        pool = float(game.scenario_state.get("hidden_support_work_pool", 1.0))
        for node_id in game.managed_node_ids():
            game.G.nodes[node_id]["scenario_display_load"] = 0.0
        game.G.nodes[hidden]["scenario_display_load"] = pool * hidden_share

        candidate_nodes = [
            node_id
            for node_id in game.managed_node_ids()
            if node_id not in {hidden, focal}
        ]
        if not candidate_nodes:
            return

        average_candidate_strain = sum(
            game.G.nodes[node_id]["strain"] for node_id in candidate_nodes
        ) / len(candidate_nodes)

        strain_sorted = sorted(
            candidate_nodes,
            key=lambda node_id: (
                game.G.nodes[node_id]["strain"],
                -game.G.nodes[node_id]["engagement"],
            ),
        )
        low_strain_cluster = [
            node_id
            for node_id in strain_sorted
            if game.G.nodes[node_id]["strain"] <= average_candidate_strain + 0.015
        ]
        if len(low_strain_cluster) < min(3, len(candidate_nodes)):
            low_strain_cluster = strain_sorted[: min(4, len(candidate_nodes))]

        selected = low_strain_cluster[: min(5, len(low_strain_cluster))]
        if not selected:
            return

        remaining_pool = max(0.0, pool * (1.0 - hidden_share))
        weights = []
        for node_id in selected:
            node = game.G.nodes[node_id]
            weight = (
                (1.05 - node["strain"])
                * (0.75 + 0.25 * node["engagement"])
                * (0.70 + 0.30 * node["trust"])
                * (1.0 + redistribution_rotation(node_id, game.week))
            )
            if node_id == spillover and node["strain"] > average_candidate_strain:
                weight *= 0.45
            weights.append(max(0.05, weight))

        total_weight = sum(weights)
        for node_id, weight in zip(selected, weights):
            share = remaining_pool * (weight / total_weight)
            game.G.nodes[node_id]["scenario_display_load"] = share

    if game.week <= 3:
        add_behaviors(focal, ["missed_deadline_minor", "complaint"])
    if game.week >= 4:
        add_behaviors(hidden, ["ignored_email"])

    if story_style == "no_intervention":
        for node_id, bump in [(focal, 0.016), (hidden, 0.034), (spillover, 0.020)]:
            game.G.nodes[node_id]["strain"] = float(np.clip(game.G.nodes[node_id]["strain"] + bump, 0, 1))
        redistribute_hidden_work(0.58)
        add_behaviors(hidden, ["lateness"])
        cluster_anchor = roles.get("cluster_anchor")
        if cluster_anchor is not None:
            game.G.nodes[cluster_anchor]["alignment"] = float(np.clip(game.G.nodes[cluster_anchor]["alignment"] - 0.02, 0, 1))
    elif story_style == "targeted_on_focal":
        game.G.nodes[focal]["strain"] = float(np.clip(game.G.nodes[focal]["strain"] - 0.030, 0, 1))
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] + 0.026, 0, 1))
        game.G.nodes[spillover]["strain"] = float(np.clip(game.G.nodes[spillover]["strain"] + 0.012, 0, 1))
        redistribute_hidden_work(0.62)
        add_behaviors(hidden, ["lateness", "high_error_rate"])
    elif story_style == "targeted_on_hidden":
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] - 0.040, 0, 1))
        redistribute_hidden_work(0.44)
        game.G.nodes[focal]["strain"] = float(np.clip(game.G.nodes[focal]["strain"] + 0.005, 0, 1))
        cluster_anchor = roles.get("cluster_anchor")
        if cluster_anchor is not None:
            game.G.nodes[cluster_anchor]["alignment"] = float(np.clip(game.G.nodes[cluster_anchor]["alignment"] + 0.01, 0, 1))
    elif story_style == "cluster_stabilising":
        for node_id, drop in [(hidden, 0.050), (focal, 0.028), (spillover, 0.024)]:
            game.G.nodes[node_id]["strain"] = float(np.clip(game.G.nodes[node_id]["strain"] - drop, 0, 1))
        redistribute_hidden_work(0.34)
        game.G.nodes[spillover]["alignment"] = float(np.clip(game.G.nodes[spillover]["alignment"] + 0.04, 0, 1))
        cluster_anchor = roles.get("cluster_anchor")
        if cluster_anchor is not None:
            game.G.nodes[cluster_anchor]["alignment"] = float(np.clip(game.G.nodes[cluster_anchor]["alignment"] + 0.05, 0, 1))
    else:
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] + 0.014, 0, 1))
        redistribute_hidden_work(0.50)

    if game.scenario_state.get("acceptable_route_active", False):
        game.G.nodes[hidden]["strain"] = float(np.clip(game.G.nodes[hidden]["strain"] - 0.022, 0, 1))
        game.G.nodes[focal]["strain"] = float(np.clip(game.G.nodes[focal]["strain"] - 0.010, 0, 1))
        redistribute_hidden_work(0.40)

    game.scenario_state["benchmark_path_guess"] = game._classify_run_response_style()


STORY_BUILDERS = {
    "Baseline": build_baseline_story_data,
    "scenario_01": build_conflict_cluster_story_data,
    "scenario_02": build_quiet_high_performer_story_data,
}


WEEK_BIAS_APPLIERS = {
    "scenario_01": apply_conflict_cluster_week_bias,
    "scenario_02": apply_quiet_high_performer_week_bias,
}
