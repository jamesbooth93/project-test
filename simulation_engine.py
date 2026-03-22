import os
import shutil
import hashlib
import numpy as np
import pandas as pd
import networkx as nx
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join("/tmp", "management_sim_matplotlib")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from action_registry import sim_action_map
from role_config import ROLE_MODIFIERS
from scenario_runtime import apply_benchmark_actions_for_week, apply_recommended_actions_for_week


def graph_rng(G):
    return G.graph.get("rng", np.random)

# ----------------------
# Behavioral Strain Weights
# ----------------------
behavior_weights = {
    "sick_day": 0.9,
    "missed_deadline_minor": 0.4,
    "missed_deadline_critical": 0.7,
    "lateness": 0.15,
    "ignored_email": 0.3,
    "complaint": 0.6,
    "engagement_drop": 0.5,
    "overload_signal": 0.6,
    "high_error_rate": 0.7
}

# Behaviors that directly worsen the focal employee's own strain
self_strain_behaviors = {
    "sick_day",
    "overload_signal",
    "high_error_rate",
    "missed_deadline_critical"
}

# Behaviors that spill strain onto teammates
spillover_behaviors = {
    "lateness": 0.015,
    "ignored_email": 0.020,
    "engagement_drop": 0.020,
    "complaint": 0.010,
    "missed_deadline_minor": 0.015,
    "sick_day": 0.025,
    "overload_signal": 0.020,
    "high_error_rate": 0.025,
    "missed_deadline_critical": 0.040
    
}

# Workload burden created by behaviors that leave work uncovered
behavior_workload_load = {
    "sick_day": 1.00,
    "missed_deadline_minor": 0.35,
    "missed_deadline_critical": 0.80,
    "lateness": 0.20,
    "ignored_email": 0.20,
    "complaint": 0.10,
    "engagement_drop": 0.25,
    "overload_signal": 0.50,
    "high_error_rate": 0.60
}


def node_role_mod(node_data, key, default=1.0):
    role_class = node_data.get("role_class", "ic")
    return ROLE_MODIFIERS.get(role_class, {}).get(key, default)

def apply_behavior_decay(G, node, decay=0.02):
    """
    Small passive recovery before any new behavioral strain is added.
    """
    G.nodes[node]["strain"] *= (1 - decay)
    G.nodes[node]["strain"] = float(np.clip(G.nodes[node]["strain"], 0, 1))

def apply_self_behavior_effects(G, node, behaviors):
    """
    Apply behavior-related strain to the focal employee only.
    """
    current_strain = G.nodes[node]["strain"]

    for b in behaviors:
        if b in behavior_weights:
            base = behavior_weights[b]

            # Impact shrinks as strain approaches 1
            scaled = base * (0.35 + 0.65 * (1 - current_strain)) * 0.35
            G.nodes[node]["strain"] += scaled
            G.nodes[node]["strain"] = float(np.clip(G.nodes[node]["strain"], 0, 1))
            current_strain = G.nodes[node]["strain"]

def apply_neighbor_spillover(G, node, behaviors):
    """
    Work left uncovered by one employee spills onto nearby coworkers.
    Strong teams buffer some of it, but repeated overload should bite harder.

    Difficulty-sensitive pacing:
    - higher workload strain multipliers make uncovered work travel farther
    - harder modes convert more of that burden into direct strain
    """
    diff = get_difficulty_profile(G.graph.get("difficulty_profile"))
    spillover_mult = float(np.clip(
        0.92 + 0.30 * (diff["workload_strain_mult"] - 1.0) + 0.18 * (diff["contagion_mult"] - 1.0),
        0.78,
        1.40,
    ))

    rng = graph_rng(G)
    neighbors = list(G.neighbors(node))
    if len(neighbors) == 0:
        return

    total_workload = 0.0
    for b in behaviors:
        total_workload += behavior_workload_load.get(b, 0.0)
    total_workload *= node_role_mod(G.nodes[node], "spillover_out", 1.0)

    if total_workload <= 0:
        return

    scored_neighbors = []
    for nbr in neighbors:
        edge_weight = G.edges[node, nbr].get("weight", 0.0)
        nbr_strain = G.nodes[nbr]["strain"]
        nbr_resources = G.nodes[nbr]["resources"]

        absorb_score = (
            (0.30 + edge_weight)
            * (1.05 - nbr_strain)
            * (0.45 + 0.06 * nbr_resources)
        )
        absorb_score *= node_role_mod(G.nodes[nbr], "workload_absorb", 1.0)
        scored_neighbors.append((nbr, max(absorb_score, 0.01)))

    scored_neighbors.sort(key=lambda x: x[1], reverse=True)

    n_receivers = min(len(scored_neighbors), rng.randint(1, min(4, len(scored_neighbors)) + 1))
    selected = scored_neighbors[:n_receivers]

    weights = np.array([x[1] for x in selected], dtype=float)
    weights = weights / weights.sum()

    for (nbr, _), share in zip(selected, weights):
        absorbed = total_workload * share * spillover_mult

        # Team buffering intervention can reduce spillover temporarily
        if G.nodes[nbr].get("spillover_block_weeks", 0) > 0:
            absorbed *= 0.65

        # Workload relief should also reduce incoming burden for a few weeks
        if G.nodes[nbr].get("workload_buffer_weeks", 0) > 0:
            absorbed *= 0.75

        capacity_limit = 0.75 + 0.10 * G.nodes[nbr]["resources"]
        absorbed = min(absorbed, capacity_limit)

        resource_hit = 0.38 * absorbed

        edge_weight = G.edges[node, nbr].get("weight", 0.0)
        buffer_factor = (
            0.90
            - 0.15 * edge_weight
            - 0.06 * G.nodes[nbr]["trust"]
            - 0.06 * G.nodes[nbr]["engagement"]
        )
        buffer_factor = float(np.clip(buffer_factor, 0.55, 1.15))

        strain_bump = 0.060 * absorbed * (1 + 0.55 * G.nodes[nbr]["vulnerability"])
        strain_bump *= (1 + 0.60 * G.nodes[nbr]["strain"])
        strain_bump *= buffer_factor

        if G.nodes[nbr].get("workload_buffer_weeks", 0) > 0:
            strain_bump *= 0.82
            resource_hit *= 0.88

        if G.nodes[nbr]["strain"] > 0.45:
            strain_bump *= 1.0 + 0.35 * (G.nodes[nbr]["strain"] - 0.45)

        G.nodes[nbr]["resources"] = max(0, G.nodes[nbr]["resources"] - resource_hit)
        G.nodes[nbr]["strain"] = float(np.clip(G.nodes[nbr]["strain"] + strain_bump, 0, 1))
        G.nodes[nbr]["absorbed_workload"] += absorbed

def process_node_behaviors(G, node, behaviors, decay=0.02):
    """
    Clean behavior pipeline:
    1. small passive recovery,
    2. record visible warning signs,
    3. apply self-effects for severe behaviors,
    4. apply spillover to teammates.
    """
    apply_behavior_decay(G, node, decay=decay)
    record_behaviors(G, node, behaviors)

    self_effect_behaviors = [b for b in behaviors if b in self_strain_behaviors]

    if len(self_effect_behaviors) > 0:
        apply_self_behavior_effects(G, node, self_effect_behaviors)

    apply_neighbor_spillover(G, node, behaviors)

def apply_passive_recovery(G, recovery_mult=1.0):
    """
    Weekly recovery pass.

    Design goals:
    - low-strain people recover reasonably well
    - medium-strain people recover slowly
    - high-strain people recover very little unless supported
    - repeated overload should suppress natural recovery
    """
    for n in G.nodes():
        strain = G.nodes[n]["strain"]
        resources = G.nodes[n]["resources"]
        trust = G.nodes[n]["trust"]
        engagement = G.nodes[n]["engagement"]
        absorbed_workload = G.nodes[n].get("absorbed_workload", 0.0)

        base_recovery = (
            0.004
            + 0.002 * min(resources, 10)
            + 0.004 * trust
            + 0.004 * engagement
        )

        if strain < 0.35:
            strain_band_mult = 1.35
        elif strain < 0.55:
            strain_band_mult = 0.90
        elif strain < 0.75:
            strain_band_mult = 0.45
        else:
            strain_band_mult = 0.18

        recovery = base_recovery * strain_band_mult * recovery_mult
        recovery *= node_role_mod(G.nodes[n], "recovery", 1.0)

        # People carrying extra load do not recover normally
        workload_penalty = 0.016 * min(absorbed_workload, 2.0)

        # Temporary support can improve recovery
        recovery_boost_weeks = G.nodes[n].get("recovery_boost_weeks", 0)
        if recovery_boost_weeks > 0:
            recovery += 0.018

        # Workload relief should help sustain recovery a bit longer
        if G.nodes[n].get("workload_buffer_weeks", 0) > 0:
            recovery += 0.006
            workload_penalty *= 0.70

        G.nodes[n]["strain"] = float(np.clip(strain - recovery + workload_penalty, 0, 1))


def propagate_support(G, supported_nodes, strength=0.08):
    """
    Relief spreads weakly across strong ties.
    This is intentionally weaker than stress contagion, but it helps stabilization.
    """
    if not supported_nodes:
        return

    for node in supported_nodes:
        for nbr in G.neighbors(node):
            edge_weight = G.edges[node, nbr].get("weight", 0.0)

            reduction = strength * (0.4 + edge_weight)
            reduction *= (0.6 + 0.4 * G.nodes[node]["trust"])

            G.nodes[nbr]["strain"] = float(np.clip(
                G.nodes[nbr]["strain"] - reduction,
                0,
                1
            ))

            G.nodes[nbr]["engagement"] = float(np.clip(
                G.nodes[nbr]["engagement"] + 0.02 * strength,
                0,
                1
            ))

# ----------------------
# Observed Risk / Intervention State
# ----------------------

behavior_observability = {
    "sick_day": 0.9,
    "missed_deadline_minor": 0.6,
    "missed_deadline_critical": 0.85,
    "lateness": 0.5,
    "ignored_email": 0.55,
    "complaint": 0.8,
    "engagement_drop": 0.7,
    "overload_signal": 0.9,
    "high_error_rate": 0.75
}

def initialize_intervention_state(G):
    """
    Add bookkeeping fields used by the intervention system.
    """
    for n in G.nodes():
        G.nodes[n]["observed_risk"] = 0.0
        G.nodes[n]["recent_behaviors"] = []
        G.nodes[n]["support_count"] = 0
        G.nodes[n]["last_supported_step"] = -999

        # Harm bookkeeping
        G.nodes[n]["behavior_counts"] = {b: 0 for b in behavior_weights.keys()}
        G.nodes[n]["absorbed_workload"] = 0.0

        # Temporary intervention effect state
        G.nodes[n]["recovery_boost_weeks"] = 0
        G.nodes[n]["spillover_block_weeks"] = 0
        G.nodes[n]["relapse_protection_weeks"] = 0
        G.nodes[n]["visibility_boost_weeks"] = 0
        G.nodes[n]["workload_buffer_weeks"] = 0

def record_behaviors(G, node, behaviors):
    """
    Store visible warning-sign history for a node and count behavior totals.
    """
    if "recent_behaviors" not in G.nodes[node]:
        G.nodes[node]["recent_behaviors"] = []

    if "behavior_counts" not in G.nodes[node]:
        G.nodes[node]["behavior_counts"] = {b: 0 for b in behavior_weights.keys()}

    G.nodes[node]["recent_behaviors"].extend(list(behaviors))

    for b in behaviors:
        if b in G.nodes[node]["behavior_counts"]:
            G.nodes[node]["behavior_counts"][b] += 1

    # Keep only the most recent few behaviors
    G.nodes[node]["recent_behaviors"] = G.nodes[node]["recent_behaviors"][-10:]


def update_observed_risk(G, decay=0.24, noise_sd=0.02, manager_state=None, founder_state=None):
    """
    Managers do not observe true strain directly.
    They observe a noisy, smoothed signal based on visible behaviors
    and partial cues.

    Support can temporarily improve visibility of problems.
    """
    rng = graph_rng(G)
    manager_state = manager_state or {
        "strain": 0.20,
        "visibility_skill": 0.60,
    }
    founder_state = founder_state or {
        "founder_clarity": 0.55,
    }
    for n in G.nodes():
        current = G.nodes[n].get("observed_risk", 0.0)
        relationship = G.nodes[n].get("manager_relationship", 0.55)
        contact = G.nodes[n].get("manager_contact_frequency", 0.60)
        role_observability = G.nodes[n].get("role_observability", node_role_mod(G.nodes[n], "observability", 1.0))
        scenario_visibility_bias = G.nodes[n].get("scenario_visibility_bias", 0.0)
        manager_strain = manager_state.get("strain", 0.2)
        visibility_skill = manager_state.get("visibility_skill", 0.6)
        founder_clarity = founder_state.get("founder_clarity", 0.55)

        behavior_signal = 0.0
        recent_behaviors = G.nodes[n].get("recent_behaviors", [])[-4:]
        for b in recent_behaviors:
            behavior_signal += behavior_observability.get(b, 0.0) * 0.12

        latent_signal = (
            0.52 * G.nodes[n]["strain"] +
            0.12 * (1 - G.nodes[n]["engagement"]) +
            0.08 * (1 - G.nodes[n]["alignment"])
        )

        if G.nodes[n].get("visibility_boost_weeks", 0) > 0:
            latent_signal += 0.05

        accuracy_multiplier = np.clip(
            0.28
            + 0.24 * relationship
            + 0.18 * contact
            + 0.26 * visibility_skill
            + 0.18 * role_observability
            + 0.10 * founder_clarity
            + scenario_visibility_bias
            - 0.28 * manager_strain,
            0.18,
            1.10,
        )
        noise_scale = noise_sd * np.clip(
            1.15
            + 0.70 * manager_strain
            + 0.35 * (1 - relationship)
            - 0.25 * role_observability,
            0.6,
            2.0,
        )
        noise = rng.normal(0, noise_scale)
        raw_signal = np.clip(
            behavior_signal * (0.70 + 0.30 * accuracy_multiplier)
            + latent_signal * accuracy_multiplier
            + noise,
            0,
            1,
        )

        observed = (1 - decay) * current + decay * raw_signal
        G.nodes[n]["observed_risk"] = float(np.clip(observed, 0, 1))

        if len(G.nodes[n].get("recent_behaviors", [])) > 6 and rng.rand() < 0.35:
            G.nodes[n]["recent_behaviors"] = G.nodes[n]["recent_behaviors"][-6:]


def diminishing_returns_factor(G, node, step, cooldown=4):
    """
    Repeated support becomes less effective.
    """
    support_count = G.nodes[node].get("support_count", 0)
    last_step = G.nodes[node].get("last_supported_step", -999)

    repeat_penalty = 1 / (1 + 0.35 * support_count)

    if (step - last_step) <= cooldown:
        repeat_penalty *= 0.7

    return repeat_penalty


def get_high_strain_clusters(G, threshold=0.6):
    """
    Return connected components among high-strain nodes.
    """
    high_nodes = [n for n in G.nodes() if G.nodes[n]["strain"] > threshold]
    subgraph = G.subgraph(high_nodes)
    if len(subgraph) == 0:
        return []
    return sorted(nx.connected_components(subgraph), key=len, reverse=True)


def rank_nodes_for_intervention(G, target="high_observed_risk"):
    rng = graph_rng(G)
    nodes = list(G.nodes())

    if target == "high_observed_risk":
        return sorted(nodes, key=lambda n: G.nodes[n]["observed_risk"], reverse=True)

    elif target == "high_strain":
        return sorted(nodes, key=lambda n: G.nodes[n]["strain"], reverse=True)

    elif target == "high_degree":
        return sorted(nodes, key=lambda n: G.degree(n), reverse=True)

    elif target == "bridge_nodes":
        bc = nx.betweenness_centrality(G)
        return sorted(nodes, key=lambda n: bc[n], reverse=True)

    elif target == "strain_growth_proxy":
        # Approximate using high observed risk + strain together
        return sorted(
            nodes,
            key=lambda n: 0.6 * G.nodes[n]["observed_risk"] + 0.4 * G.nodes[n]["strain"],
            reverse=True
        )

    elif target == "random":
        ranked = nodes[:]
        rng.shuffle(ranked)
        return ranked

    return []


def schedule_intervention(intervention_queue, execute_step, plan):
    """
    Add an intervention plan to a delayed queue.
    """
    intervention_queue.append({
        "execute_step": execute_step,
        "plan": plan
    })


def select_nodes_with_capacity(G, ranked_nodes, n_capacity, min_risk=0.0):
    selected = []
    for n in ranked_nodes:
        if G.nodes[n]["observed_risk"] >= min_risk:
            selected.append(n)
        if len(selected) >= n_capacity:
            break
    return selected

def choose_intervention_strategy_from_behaviors(G, node):
    """
    Choose an intervention type based on the node's recent warning signs.
    This makes intervention respond to visible patterns rather than using
    one fixed strategy every time.
    """
    recent = G.nodes[node].get("recent_behaviors", [])[-5:]
    recent_set = set(recent)

    # Workload / overload type problems
    if ("overload_signal" in recent_set) or ("sick_day" in recent_set):
        return "workload_relief"

    # Relationship / communication problems
    if ("complaint" in recent_set) or ("ignored_email" in recent_set):
        return "team_mediation"

    # Motivation / management problems
    if ("engagement_drop" in recent_set) or ("lateness" in recent_set):
        return "manager_support"

    # Performance / capability problems
    if ("high_error_rate" in recent_set) or ("missed_deadline_critical" in recent_set):
        return "capacity_building"

    # Fallback if nothing strong is visible
    return "manager_support"

def apply_universal_support(G, strength=0.08, collective_resource=100.0):
    """
    Low-dose support applied broadly across the organization.
    Useful for testing team-wide relief / proactive support.
    """
    if len(G.nodes()) == 0 or collective_resource <= 0:
        return [], collective_resource

    helped = []
    unit_cost = 0.6

    for n in G.nodes():
        if collective_resource < unit_cost * strength:
            break

        G.nodes[n]["strain"] = max(0, G.nodes[n]["strain"] - 0.08 * strength)
        G.nodes[n]["engagement"] = float(np.clip(G.nodes[n]["engagement"] + 0.04 * strength, 0, 1))
        G.nodes[n]["resources"] += 0.20 * strength

        collective_resource -= unit_cost * strength
        helped.append(n)

    return helped, collective_resource


def apply_team_buffer_support(G, focal_node, strength=0.25, collective_resource=100.0):
    """
    Support a focal person plus their nearest team neighborhood.
    Best used when a local cluster is forming.
    """
    helped = []
    unit_cost = 1.3

    targets = [focal_node] + list(G.neighbors(focal_node))
    if len(targets) > 1:
        nbrs = list(G.neighbors(focal_node))
        nbrs_sorted = sorted(
            nbrs,
            key=lambda n: G.edges[focal_node, n].get("weight", 0.0),
            reverse=True
        )
        targets = [focal_node] + nbrs_sorted[:3]

    for n in targets:
        if collective_resource < unit_cost * strength:
            break

        G.nodes[n]["strain"] = max(0, G.nodes[n]["strain"] - 0.16 * strength)
        G.nodes[n]["resources"] += 0.40 * strength
        G.nodes[n]["engagement"] = float(np.clip(G.nodes[n]["engagement"] + 0.05 * strength, 0, 1))
        G.nodes[n]["spillover_block_weeks"] = max(G.nodes[n].get("spillover_block_weeks", 0), 2)

        collective_resource -= unit_cost * strength
        helped.append(n)

    return helped, collective_resource

# ----------------------
# Collapse Detection Functions
# ----------------------
def detect_collapse(series, threshold=0.90, duration=3):
    """
    Collapse occurs if the metric exceeds threshold for 'duration'
    consecutive steps.
    """
    count = 0
    for x in series:
        if x >= threshold:
            count += 1
            if count >= duration:
                return True
        else:
            count = 0
    return False

def time_to_collapse(series, threshold=0.90, duration=3):
    """
    Returns the first step where collapse begins (1-indexed),
    requiring 'duration' consecutive steps above threshold.
    Returns None if no collapse occurs.
    """
    count = 0
    for i, x in enumerate(series, start=1):
        if x >= threshold:
            count += 1
            if count >= duration:
                return i - duration + 1
        else:
            count = 0
    return None

# ----------------------
# Intervention Function (Realistic Version)
# ----------------------
def apply_intervention(
    G,
    step,
    strategy="workload_relief",
    target="high_observed_risk",
    n_capacity=3,
    strength=0.4,
    strain_threshold=0.6,
    observed_risk_threshold=0.55,
    collective_resource=100.0
):
    """
    More realistic workplace intervention with resource constraints.

    strategy options:
        - workload_relief
        - manager_support
        - team_mediation
        - capacity_building
        - team_buffer_support
        - universal_support
        - auto (node-specific adaptive choice based on warning signs)

    target options:
        - high_observed_risk
        - high_strain
        - high_degree
        - bridge_nodes
        - strain_growth_proxy
        - random
        - high_strain_cluster
        - hybrid_targeted_random
    """
    rng = graph_rng(G)

    if len(G.nodes()) == 0 or n_capacity <= 0 or collective_resource <= 0:
        return [], collective_resource, {
            "workload_relief": 0,
            "manager_support": 0,
            "team_mediation": 0,
            "capacity_building": 0
        }

    # Universal support bypasses node targeting
    if strategy == "universal_support":
        helped, collective_resource = apply_universal_support(
            G,
            strength=strength,
            collective_resource=collective_resource
        )
        for n in helped:
            G.nodes[n]["support_count"] += 1
            G.nodes[n]["last_supported_step"] = step
        return helped, collective_resource, {
            "workload_relief": 0,
            "manager_support": 0,
            "team_mediation": 0,
            "capacity_building": 0
        }

    target_nodes = []

    if target == "high_strain_cluster":
        clusters = get_high_strain_clusters(G, threshold=strain_threshold)
        if len(clusters) > 0:
            largest_cluster_nodes = list(clusters[0])
            ranked_cluster = sorted(
                largest_cluster_nodes,
                key=lambda n: G.nodes[n]["observed_risk"],
                reverse=True
            )
            target_nodes = ranked_cluster[:n_capacity]
    elif target == "hybrid_targeted_random":
        n_targeted = max(1, int(np.ceil(0.5 * n_capacity)))
        n_random = max(0, n_capacity - n_targeted)

        ranked = rank_nodes_for_intervention(G, target="high_observed_risk")
        targeted_nodes = select_nodes_with_capacity(
            G,
            ranked,
            n_capacity=n_targeted,
            min_risk=observed_risk_threshold
        )

        remaining = [n for n in G.nodes() if n not in targeted_nodes]
        rng.shuffle(remaining)
        random_nodes = remaining[:n_random]

        target_nodes = targeted_nodes + random_nodes
    else:
        ranked = rank_nodes_for_intervention(G, target=target)
        target_nodes = select_nodes_with_capacity(
            G,
            ranked,
            n_capacity=n_capacity,
            min_risk=observed_risk_threshold if target == "high_observed_risk" else 0.0
        )

    helped_nodes = []
    strategy_counts = {
        "workload_relief": 0,
        "manager_support": 0,
        "team_mediation": 0,
        "capacity_building": 0
    }

    for n in target_nodes:
        if collective_resource <= 0:
            break

        if strategy == "auto":
            node_strategy = choose_intervention_strategy_from_behaviors(G, n)
        else:
            node_strategy = strategy

        support_dose = strength
        effective_dose = support_dose * diminishing_returns_factor(G, n, step)

        if effective_dose <= 0:
            continue

        if node_strategy == "workload_relief":
            unit_cost = 1.5
        elif node_strategy == "manager_support":
            unit_cost = 1.0
        elif node_strategy == "team_mediation":
            unit_cost = 1.2
        elif node_strategy == "capacity_building":
            unit_cost = 2.0
        elif node_strategy == "team_buffer_support":
            unit_cost = 1.4
        else:
            unit_cost = 1.2

        max_affordable_dose = collective_resource / unit_cost
        eff = min(effective_dose, max_affordable_dose)

        if eff <= 0:
            continue

        if node_strategy == "team_buffer_support":
            helped_local, collective_resource = apply_team_buffer_support(
                G,
                focal_node=n,
                strength=eff,
                collective_resource=collective_resource
            )

            for hn in helped_local:
                if hn not in helped_nodes:
                    helped_nodes.append(hn)

            strategy_counts["manager_support"] += 1
            continue

        if node_strategy == "workload_relief":
            old_strain = G.nodes[n]["strain"]
            reduction = eff * 0.30 * old_strain
            G.nodes[n]["strain"] = max(0, old_strain - reduction)
            G.nodes[n]["resources"] += 1.2 * eff

            nbrs = list(G.neighbors(n))
            if len(nbrs) > 0:
                spill = 0.015 * eff
                for nbr in nbrs:
                    G.nodes[nbr]["strain"] = float(np.clip(G.nodes[nbr]["strain"] + spill, 0, 1))

            collective_resource = max(0, collective_resource - unit_cost * eff)
            helped_nodes.append(n)
            strategy_counts["workload_relief"] += 1

        elif node_strategy == "manager_support":
            G.nodes[n]["engagement"] = float(np.clip(G.nodes[n]["engagement"] + 0.18 * eff, 0, 1))
            G.nodes[n]["alignment"] = float(np.clip(G.nodes[n]["alignment"] + 0.15 * eff, 0, 1))
            G.nodes[n]["trust"] = float(np.clip(G.nodes[n]["trust"] + 0.10 * eff, 0, 1))
            G.nodes[n]["strain"] = max(0, G.nodes[n]["strain"] - 0.10 * eff)

            collective_resource = max(0, collective_resource - unit_cost * eff)
            helped_nodes.append(n)
            strategy_counts["manager_support"] += 1

        elif node_strategy == "team_mediation":
            nbrs = list(G.neighbors(n))
            for nbr in nbrs:
                if G.has_edge(n, nbr):
                    G.edges[n, nbr]["weight"] = float(np.clip(
                        G.edges[n, nbr]["weight"] + 0.08 * eff,
                        0, 1
                    ))

            G.nodes[n]["strain"] = max(0, G.nodes[n]["strain"] - 0.06 * eff)

            for nbr in nbrs:
                G.nodes[nbr]["strain"] = max(0, G.nodes[nbr]["strain"] - 0.02 * eff)

            collective_resource = max(0, collective_resource - unit_cost * eff)
            helped_nodes.append(n)
            strategy_counts["team_mediation"] += 1

        elif node_strategy == "capacity_building":
            G.nodes[n]["resources"] += 1.5 * eff
            G.nodes[n]["engagement"] = float(np.clip(G.nodes[n]["engagement"] + 0.10 * eff, 0, 1))
            G.nodes[n]["trust"] = float(np.clip(G.nodes[n]["trust"] + 0.08 * eff, 0, 1))
            G.nodes[n]["strain"] = max(0, G.nodes[n]["strain"] - 0.05 * eff)

            G.nodes[n]["vulnerability"] = float(
                np.clip(G.nodes[n]["vulnerability"] * (1 - 0.03 * eff), 0, 1)
            )

            collective_resource = max(0, collective_resource - unit_cost * eff)
            helped_nodes.append(n)
            strategy_counts["capacity_building"] += 1

    for n in helped_nodes:
        G.nodes[n]["support_count"] += 1
        G.nodes[n]["last_supported_step"] = step

    return helped_nodes, collective_resource, strategy_counts

# ----------------------
# Utility Functions
# ----------------------
def compute_largest_high_strain_cluster_size(G, threshold=0.6):
    """
    Return the size of the largest connected component of high-strain nodes.
    """
    high_nodes = [n for n in G.nodes() if G.nodes[n]["strain"] > threshold]
    subgraph = G.subgraph(high_nodes)
    if len(subgraph) == 0:
        return 0
    return len(max(nx.connected_components(subgraph), key=len))

# ----------------------
# Shock Function
# ----------------------
def apply_shock(G, collective_resource, founder_quality=0.5):
    """
    Founder quality affects how much external pressure reaches the team.

    New design:
    - minor disruptions happen sometimes
    - major shocks are rarer but stronger
    - shocks accelerate existing problems rather than fully determining outcomes
    """
    rng = graph_rng(G)
    founder_quality = float(np.clip(founder_quality, 0.0, 1.0))

    minor_shock_prob = 0.26 - 0.08 * founder_quality
    major_shock_prob = 0.09 - 0.04 * founder_quality

    minor_severity_mult = 1.10 - 0.30 * founder_quality
    major_severity_mult = 1.20 - 0.35 * founder_quality

    # Minor organization-wide disruption
    if rng.rand() < minor_shock_prob:
        loss = rng.uniform(2.5, 5.5) * minor_severity_mult
        collective_resource = max(0, collective_resource - loss)

        for n in G.nodes():
            bump = rng.uniform(0.015, 0.040) * minor_severity_mult
            G.nodes[n]["strain"] += bump

    # Major localized or cross-team disruption
    if rng.rand() < major_shock_prob:
        affected = rng.choice(
            list(G.nodes()),
            size=rng.randint(3, 7),
            replace=False
        )

        for n in affected:
            G.nodes[n]["strain"] += rng.uniform(0.06, 0.14) * major_severity_mult
            G.nodes[n]["resources"] = max(
                0,
                G.nodes[n]["resources"] - rng.uniform(0.8, 2.2) * major_severity_mult
            )

            if rng.rand() < 0.45:
                behaviors = rng.choice(
                    list(behavior_weights.keys()),
                    size=rng.randint(1, 3),
                    replace=False
                )
                process_node_behaviors(G, n, list(behaviors), decay=0.0)

    for n in G.nodes():
        G.nodes[n]["strain"] = float(np.clip(G.nodes[n]["strain"], 0, 1))

    return collective_resource

def get_difficulty_profile(difficulty_profile=None):
    """
    Lightweight engine-level difficulty controls.

    These tune how quickly strain spreads and compounds without changing the
    shape of the rest of the simulation.
    """
    base = {
        "contagion_mult": 1.0,
        "workload_strain_mult": 1.0,
        "noise_mult": 1.0,
        "instability_bias": 0.0,
        "behavior_escalation_mult": 1.0,
    }
    if difficulty_profile is None:
        return base
    merged = base.copy()
    merged.update({k: v for k, v in difficulty_profile.items() if k in base})
    return merged

def generate_behavior_signals(G, difficulty_profile=None):
    """
    Generate visible warning signs from each node's current state.

    Design goals:
    - warning signs appear earlier on harder modes
    - repeated overload becomes more likely to cascade
    - severe strain creates more visible operational problems
    """
    rng = graph_rng(G)
    diff = get_difficulty_profile(difficulty_profile)
    escalation_mult = diff["behavior_escalation_mult"]
    threshold_shift = 0.04 * (escalation_mult - 1.0)

    for n in G.nodes():
        behaviors = []

        strain = G.nodes[n]["strain"]
        engagement = G.nodes[n]["engagement"]
        resources = G.nodes[n]["resources"]
        recent = G.nodes[n].get("recent_behaviors", [])[-4:]

        repeat_overload = recent.count("overload_signal")
        repeat_errors = recent.count("high_error_rate")
        repeat_sick = recent.count("sick_day")

        if strain > (0.72 - threshold_shift) and rng.rand() < min(0.97, (0.22 + 0.08 * repeat_sick) * escalation_mult):
            behaviors.append("sick_day")

        if strain > (0.55 - threshold_shift) and rng.rand() < min(0.97, (0.34 + 0.12 * repeat_overload) * escalation_mult):
            behaviors.append("overload_signal")

        if strain > (0.52 - threshold_shift) and rng.rand() < min(0.97, (0.23 + 0.10 * repeat_errors) * escalation_mult):
            behaviors.append("high_error_rate")

        if strain > (0.46 - threshold_shift) and rng.rand() < min(0.97, 0.22 * escalation_mult):
            behaviors.append("ignored_email")

        if strain > (0.45 - threshold_shift) and engagement < 0.52 and rng.rand() < min(0.97, 0.26 * escalation_mult):
            behaviors.append("engagement_drop")

        if strain > (0.44 - threshold_shift) and resources < 4.8 and rng.rand() < min(0.97, 0.22 * escalation_mult):
            behaviors.append("missed_deadline_minor")

        if strain > (0.66 - threshold_shift) and resources < 3.8 and rng.rand() < min(0.97, 0.20 * escalation_mult):
            behaviors.append("missed_deadline_critical")

        if strain > (0.39 - threshold_shift) and rng.rand() < min(0.97, 0.18 * escalation_mult):
            behaviors.append("lateness")

        if strain > (0.54 - threshold_shift) and rng.rand() < min(0.97, 0.18 * escalation_mult):
            behaviors.append("complaint")

        if len(behaviors) > 0:
            process_node_behaviors(G, n, behaviors, decay=0.0)

# ----------------------
# State Updates
# ----------------------
def update_node_states(G, difficulty_profile=None):
    rng = graph_rng(G)
    diff = get_difficulty_profile(difficulty_profile)

    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        if not neighbors:
            continue

        avg_neighbor_strain = np.mean([G.nodes[n]["strain"] for n in neighbors])
        influence = np.mean([G.edges[node, n]["weight"] for n in neighbors])

        own_strain = G.nodes[node]["strain"]
        absorbed_workload = G.nodes[node].get("absorbed_workload", 0.0)

        peer_heat = max(0.0, avg_neighbor_strain - max(0.18, own_strain - 0.02))
        cluster_pressure = max(0.0, avg_neighbor_strain - 0.34)

        contagion_delta = (
            0.74
            * diff["contagion_mult"]
            * peer_heat
            * (0.45 + influence)
        )
        contagion_delta += (
            0.024
            * diff["contagion_mult"]
            * cluster_pressure
            * (0.60 + 0.70 * influence)
        )

        workload_delta = (
            0.044
            * diff["workload_strain_mult"]
            * min(absorbed_workload, 3.0)
            * (1.0 + 0.85 * own_strain)
        )

        noise_delta = rng.normal(0, 0.02 * diff["noise_mult"])

        protection = (
            0.56
            + 0.16 * G.nodes[node]["alignment"]
            + 0.13 * G.nodes[node]["engagement"]
        )

        vulnerability_mult = 1 + 0.70 * G.nodes[node]["vulnerability"]

        instability_bias = diff["instability_bias"]
        if own_strain > 0.30:
            instability_bias *= 1.0 + 1.55 * (own_strain - 0.30)
        if own_strain > 0.50:
            instability_bias += 0.014 * diff["contagion_mult"] * (own_strain - 0.50)

        delta = contagion_delta + workload_delta + noise_delta + instability_bias
        delta *= node_role_mod(G.nodes[node], "contagion_in", 1.0)
        delta *= vulnerability_mult
        delta *= (1.22 - protection)

        if own_strain > 0.42:
            delta += 0.016 * diff["workload_strain_mult"] * (own_strain - 0.42)

        if G.nodes[node].get("relapse_protection_weeks", 0) > 0:
            delta *= 0.75

        G.nodes[node]["strain"] = float(np.clip(own_strain + delta, 0, 1))

def update_edge_weights(G):
    for u, v in list(G.edges()):
        strain_diff = abs(G.nodes[u]["strain"] - G.nodes[v]["strain"])
        degree_factor = 1 / max(1, G.degree(u) + G.degree(v))

        G.edges[u, v]["weight"] += 0.05 * (1 - strain_diff) * degree_factor
        G.edges[u, v]["weight"] -= 0.08 * strain_diff
        G.edges[u, v]["weight"] *= 0.97
        G.edges[u, v]["weight"] = np.clip(G.edges[u, v]["weight"], 0, 1)

def update_network_structure(G, N):
    """
    Update network structure slowly.

    Rationale:
    - workplace relationships usually change more slowly than daily stress,
    - we want stress propagation and intervention timing to drive results,
    - not fast network rewiring overwhelming the dynamics.
    """
    rng = graph_rng(G)
    # Remove only clearly weak ties, and do it infrequently
    for u, v in list(G.edges()):
        if G.edges[u, v]["weight"] < 0.08 and rng.rand() < 0.15:
            G.remove_edge(u, v)
        elif rng.rand() < 0.002:
            G.remove_edge(u, v)

    nodes = list(G.nodes())

    # Add a small number of possible new edges
    n_attempts = max(1, N // 8)

    for _ in range(n_attempts):
        i, j = rng.choice(nodes, 2, replace=False)
        if not G.has_edge(i, j):
            strain_diff = abs(G.nodes[i]["strain"] - G.nodes[j]["strain"])
            avg_trust = (G.nodes[i]["trust"] + G.nodes[j]["trust"]) / 2
            avg_engagement = (G.nodes[i]["engagement"] + G.nodes[j]["engagement"]) / 2

            prob = (
                avg_trust
                * avg_engagement
                * (1 - strain_diff)
                * max(0, 1 - nx.density(G))
            )

            if rng.rand() < prob * 0.02:
                G.add_edge(i, j, weight=rng.rand() * 0.15)

    # Rare triadic closure
    for u in G.nodes():
        neighbors = list(G.neighbors(u))
        if len(neighbors) >= 2 and rng.rand() < 0.02:
            a, b = rng.choice(neighbors, 2, replace=False)
            if not G.has_edge(a, b):
                G.add_edge(a, b, weight=rng.rand() * 0.12)

# ----------------------
# Simulation
# ----------------------
def run_simulation(
    sim_id,
    N=75,
    steps=52,
    collective_resource=100.0,
    save_dir="outputs",
    initial_strain_level=0.1,
    intervention_mode=None,
    intervention_start_step=None,
    intervention_strategy="workload_relief",
    intervention_target="high_observed_risk",
    intervention_strength=0.4,
    intervention_budget_frac=0.05,
    intervention_strain_threshold=0.6,
    intervention_trigger_avg=0.5,
    intervention_trigger_observed=0.55,
    intervention_delay=2,
    intervention_max_capacity=None,
    condition_label="default",
    run_id=0,
    connectivity=0.3,
    difficulty_profile=None,
):
    # Deterministic seed
    seed = int(hashlib.md5(sim_id.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.RandomState(seed)

    sim_folder = os.path.join(save_dir, f"sim_{sim_id}")
    os.makedirs(sim_folder, exist_ok=True)

    # Initialize network
    G = nx.erdos_renyi_graph(N, connectivity, seed=rng)
    G.graph["rng"] = rng

    for node in G.nodes():
        G.nodes[node]["strain"] = np.clip(rng.normal(initial_strain_level, 0.05), 0, 1)
        G.nodes[node]["trust"] = rng.rand()
        G.nodes[node]["alignment"] = rng.rand()
        G.nodes[node]["engagement"] = rng.rand()
        G.nodes[node]["resources"] = rng.rand() * 5 + 5
        G.nodes[node]["vulnerability"] = rng.rand()

    initialize_intervention_state(G)
    intervention_queue = []
    last_schedule_step = -999

    for u, v in G.edges():
        G.edges[u, v]["weight"] = rng.rand() * 0.2

    # Metrics containers
    avg_strain_over_time = []
    high_strain_fraction = []
    severe_strain_fraction = []
    severe_observed_risk_nodes = []
    largest_cluster = []
    strain_growth = []
    intervention_counts = []
    observed_risk_mean_pre = []
    observed_risk_mean_post = []
    queued_interventions = []
    collective_resource_history = []
    workload_relief_used = []
    manager_support_used = []
    team_mediation_used = []
    capacity_building_used = []

    # Harm metrics over time
    moderate_strain_person_steps_ts = []
    severe_strain_person_steps_ts = []
    avg_absorbed_workload_ts = []
    steps_operational_danger_ts = []

    sick_day_count_ts = []
    missed_deadline_minor_count_ts = []
    missed_deadline_critical_count_ts = []
    lateness_count_ts = []
    ignored_email_count_ts = []
    complaint_count_ts = []
    engagement_drop_count_ts = []
    overload_signal_count_ts = []
    high_error_rate_count_ts = []

    prev_avg_strain = 0.0

    # Simulation loop
    for step in range(steps):
        # Core dynamics
        collective_resource = apply_shock(G, collective_resource)

        # Underlying internal state changes first
        update_node_states(G, difficulty_profile=difficulty_profile)

        # Visible warning signs emerge from current conditions
        generate_behavior_signals(G, difficulty_profile=difficulty_profile)

        # Managers observe a noisy, incomplete signal after behaviors occur
        update_observed_risk(G)
        

        # Metrics BEFORE intervention execution
        strains = np.array([G.nodes[n]["strain"] for n in G.nodes()])
        avg_strain_pre = strains.mean()
        avg_observed_risk_pre = np.mean([G.nodes[n]["observed_risk"] for n in G.nodes()])

        # Capacity rule
        if intervention_max_capacity is None:
            n_capacity = int(np.ceil(intervention_budget_frac * len(G.nodes())))
        else:
            n_capacity = min(intervention_max_capacity, len(G.nodes()))

        # Schedule intervention (not immediate)
        should_schedule = False

        if intervention_mode == "always":
            should_schedule = True

        elif intervention_mode == "delayed" and intervention_start_step is not None:
            if step >= intervention_start_step:
                should_schedule = True

        elif intervention_mode == "threshold":
             if (avg_strain_pre > intervention_trigger_avg) or (avg_observed_risk_pre > intervention_trigger_observed):
                should_schedule = True

        pending_exists = len(intervention_queue) > 0
        cooldown_ok = (step - last_schedule_step) > intervention_delay

        if should_schedule and (not pending_exists) and cooldown_ok:
            plan = {
                "strategy": intervention_strategy,
                "target": intervention_target,
                "n_capacity": n_capacity,
                "strength": intervention_strength,
                "strain_threshold": intervention_strain_threshold,
                "observed_risk_threshold": intervention_trigger_observed,
            }

            schedule_intervention(
                intervention_queue,
                execute_step=step + intervention_delay,
                plan=plan
            )

            last_schedule_step = step

        # Execute due interventions
        intervened_nodes = []
        remaining_queue = []

        strategy_counts_step = {
            "workload_relief": 0,
            "manager_support": 0,
            "team_mediation": 0,
            "capacity_building": 0
        }

        for item in intervention_queue:
            if item["execute_step"] <= step:
                helped, collective_resource, strategy_counts = apply_intervention(
                    G,
                    step=step,
                    strategy=item["plan"]["strategy"],
                    target=item["plan"]["target"],
                    n_capacity=item["plan"]["n_capacity"],
                    strength=item["plan"]["strength"],
                    strain_threshold=item["plan"]["strain_threshold"],
                    observed_risk_threshold=item["plan"]["observed_risk_threshold"],
                    collective_resource=collective_resource
                )
                intervened_nodes.extend(helped)

                for k in strategy_counts_step:
                    strategy_counts_step[k] += strategy_counts[k]
            else:
                remaining_queue.append(item)

        intervention_queue = remaining_queue

        # Relationship changes happen more slowly, after behaviors and responses
        update_edge_weights(G)
        update_network_structure(G, N)

        # Metrics AFTER intervention
        strains = np.array([G.nodes[n]["strain"] for n in G.nodes()])
        current_avg = strains.mean()
        avg_observed_risk_post = np.mean([G.nodes[n]["observed_risk"] for n in G.nodes()])

        moderate_person_steps = int(np.sum(strains > 0.6))
        severe_person_steps = int(np.sum(strains > 0.8))
        severe_fraction = float(np.mean(strains > 0.8))

        avg_absorbed_workload = float(np.mean([G.nodes[n]["absorbed_workload"] for n in G.nodes()]))

        operational_danger = int((current_avg >= 0.60) or (np.mean(strains > 0.6) >= 0.40))

        behavior_totals = {b: 0 for b in behavior_weights.keys()}
        for node_id in G.nodes():
            for b in behavior_weights.keys():
                behavior_totals[b] += G.nodes[node_id]["behavior_counts"].get(b, 0)

        avg_strain_over_time.append(current_avg)
        high_strain_fraction.append(np.mean(strains > 0.6))
        severe_strain_fraction.append(severe_fraction)
        severe_observed_risk_nodes.append(np.sum([
            G.nodes[n]["observed_risk"] > 0.8 for n in G.nodes()
        ]))
        largest_cluster.append(compute_largest_high_strain_cluster_size(G))
        strain_growth.append(current_avg - prev_avg_strain)
        intervention_counts.append(len(intervened_nodes))
        observed_risk_mean_pre.append(avg_observed_risk_pre)
        observed_risk_mean_post.append(avg_observed_risk_post)
        queued_interventions.append(len(intervention_queue))
        collective_resource_history.append(collective_resource)
        workload_relief_used.append(strategy_counts_step["workload_relief"])
        manager_support_used.append(strategy_counts_step["manager_support"])
        team_mediation_used.append(strategy_counts_step["team_mediation"])
        capacity_building_used.append(strategy_counts_step["capacity_building"])

        moderate_strain_person_steps_ts.append(moderate_person_steps)
        severe_strain_person_steps_ts.append(severe_person_steps)
        avg_absorbed_workload_ts.append(avg_absorbed_workload)
        steps_operational_danger_ts.append(operational_danger)

        sick_day_count_ts.append(behavior_totals["sick_day"])
        missed_deadline_minor_count_ts.append(behavior_totals["missed_deadline_minor"])
        missed_deadline_critical_count_ts.append(behavior_totals["missed_deadline_critical"])
        lateness_count_ts.append(behavior_totals["lateness"])
        ignored_email_count_ts.append(behavior_totals["ignored_email"])
        complaint_count_ts.append(behavior_totals["complaint"])
        engagement_drop_count_ts.append(behavior_totals["engagement_drop"])
        overload_signal_count_ts.append(behavior_totals["overload_signal"])
        high_error_rate_count_ts.append(behavior_totals["high_error_rate"])

        prev_avg_strain = current_avg

    # Save metrics
    metrics = pd.DataFrame({
        "step": np.arange(1, steps + 1),
        "avg_strain": avg_strain_over_time,
        "high_strain_fraction": high_strain_fraction,
        "severe_strain_fraction": severe_strain_fraction,
        "severe_observed_risk_nodes": severe_observed_risk_nodes,
        "largest_high_strain_cluster": largest_cluster,
        "strain_growth": strain_growth,
        "n_intervened": intervention_counts,
        "avg_observed_risk_pre": observed_risk_mean_pre,
        "avg_observed_risk_post": observed_risk_mean_post,
        "queued_interventions": queued_interventions,
        "collective_resource": collective_resource_history,
        "moderate_strain_person_steps": moderate_strain_person_steps_ts,
        "severe_strain_person_steps": severe_strain_person_steps_ts,
        "avg_absorbed_workload": avg_absorbed_workload_ts,
        "operational_danger_step": steps_operational_danger_ts,
        "sick_day_count": sick_day_count_ts,
        "missed_deadline_minor_count": missed_deadline_minor_count_ts,
        "missed_deadline_critical_count": missed_deadline_critical_count_ts,
        "lateness_count": lateness_count_ts,
        "ignored_email_count": ignored_email_count_ts,
        "complaint_count": complaint_count_ts,
        "engagement_drop_count": engagement_drop_count_ts,
        "overload_signal_count": overload_signal_count_ts,
        "high_error_rate_count": high_error_rate_count_ts,
        "workload_relief_used": workload_relief_used,
        "manager_support_used": manager_support_used,
        "team_mediation_used": team_mediation_used,
        "capacity_building_used": capacity_building_used,
        "condition": condition_label,
        "run": run_id,
        "initial_strain": initial_strain_level,
        "intervention_mode": intervention_mode,
        "intervention_strategy": intervention_strategy,
        "intervention_target": intervention_target,
        "intervention_strength": intervention_strength,
        "intervention_budget_frac": intervention_budget_frac,
        "intervention_strain_threshold": intervention_strain_threshold,
        "intervention_trigger_avg": intervention_trigger_avg,
        "intervention_trigger_observed": intervention_trigger_observed,
        "intervention_delay": intervention_delay,
        "connectivity": connectivity,
    })

    metrics.to_csv(os.path.join(sim_folder, "metrics.csv"), index=False)

    # Save collapse info
    # Hard collapse
    avg_threshold = 0.95
    frac_threshold = 0.90

    # Softer and more realistic failure modes
    operational_frac_threshold = 0.50
    severe_mean_threshold = 0.75
    cluster_threshold = max(2, int(np.ceil(0.5 * N)))
    local_failure_cluster_threshold = max(2, int(np.ceil(0.30 * N)))

    duration = 3

    avg_ttc = time_to_collapse(metrics["avg_strain"], threshold=avg_threshold, duration=duration)
    avg_collapsed = detect_collapse(metrics["avg_strain"], threshold=avg_threshold, duration=duration)

    frac_ttc = time_to_collapse(metrics["high_strain_fraction"], threshold=frac_threshold, duration=duration)
    frac_collapsed = detect_collapse(metrics["high_strain_fraction"], threshold=frac_threshold, duration=duration)

    cluster_ttc = time_to_collapse(
        metrics["largest_high_strain_cluster"],
        threshold=cluster_threshold,
        duration=duration
    )
    cluster_collapsed = detect_collapse(
        metrics["largest_high_strain_cluster"],
        threshold=cluster_threshold,
        duration=duration
    )
    
    operational_ttc = time_to_collapse(
        metrics["high_strain_fraction"],
        threshold=operational_frac_threshold,
        duration=duration
    )
    operational_collapsed = detect_collapse(
        metrics["high_strain_fraction"],
        threshold=operational_frac_threshold,
        duration=duration
    )

    severe_mean_ttc = time_to_collapse(
        metrics["avg_strain"],
        threshold=severe_mean_threshold,
        duration=duration
    )
    severe_mean_collapsed = detect_collapse(
        metrics["avg_strain"],
        threshold=severe_mean_threshold,
        duration=duration
    )

    local_failure_ttc = time_to_collapse(
        metrics["largest_high_strain_cluster"],
        threshold=local_failure_cluster_threshold,
        duration=duration
    )
    local_failure_collapsed = detect_collapse(
        metrics["largest_high_strain_cluster"],
        threshold=local_failure_cluster_threshold,
        duration=duration
    )
    collapse_info = pd.DataFrame([{
        "sim_id": sim_id,
        "condition": condition_label,
        "run": run_id,
        "initial_strain": initial_strain_level,
        "connectivity": connectivity,
        "intervention_mode": intervention_mode,
        "intervention_strategy": intervention_strategy,
        "intervention_target": intervention_target,
        "intervention_strength": intervention_strength,
        "intervention_budget_frac": intervention_budget_frac,
        "intervention_strain_threshold": intervention_strain_threshold,
        "intervention_trigger_avg": intervention_trigger_avg,
        "intervention_trigger_observed": intervention_trigger_observed,
        "intervention_delay": intervention_delay,
        "collapse_duration": duration,
        "avg_collapsed": avg_collapsed,
        "avg_time_to_collapse": avg_ttc,
        "avg_threshold": avg_threshold,
        "frac_collapsed": frac_collapsed,
        "frac_time_to_collapse": frac_ttc,
        "frac_threshold": frac_threshold,
        "cluster_collapsed": cluster_collapsed,
        "cluster_time_to_collapse": cluster_ttc,
        "cluster_threshold": cluster_threshold,
        "operational_collapsed": operational_collapsed,
        "operational_time_to_collapse": operational_ttc,
        "operational_frac_threshold": operational_frac_threshold,
        "severe_mean_collapsed": severe_mean_collapsed,
        "severe_mean_time_to_collapse": severe_mean_ttc,
        "severe_mean_threshold": severe_mean_threshold,
        "local_failure_collapsed": local_failure_collapsed,
        "local_failure_time_to_collapse": local_failure_ttc,
        "local_failure_cluster_threshold": local_failure_cluster_threshold,
    }])

    collapse_info.to_csv(os.path.join(sim_folder, "collapse_info.csv"), index=False)

# ============================================================
# INTERVENTION EXPERIMENT
# ============================================================

if __name__ == "__main__":
    EXPERIMENT_DIR = "outputs_intervention_comparison"

    if os.path.exists(EXPERIMENT_DIR):
        shutil.rmtree(EXPERIMENT_DIR)
    os.makedirs(EXPERIMENT_DIR, exist_ok=True)

    # Focus near the transition region
    strain_levels = [0.30, 0.35, 0.40, 0.45]
    runs_per_level = 50

    N = 75
    steps = 52
    connectivity = 0.30

    intervention_configs = [
        {
            "label": "no_intervention",
            "intervention_mode": None,
            "intervention_strategy": "workload_relief",
            "intervention_target": "high_observed_risk",
            "intervention_strength": 0.0,
            "intervention_budget_frac": 0.0,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "targeted_workload_relief",
            "intervention_mode": "threshold",
            "intervention_strategy": "workload_relief",
            "intervention_target": "high_observed_risk",
            "intervention_strength": 0.35,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "auto_warning_sign_response",
            "intervention_mode": "threshold",
            "intervention_strategy": "auto",
            "intervention_target": "high_observed_risk",
            "intervention_strength": 0.35,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "random_workload_relief",
            "intervention_mode": "threshold",
            "intervention_strategy": "workload_relief",
            "intervention_target": "random",
            "intervention_strength": 0.35,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "hub_manager_support",
            "intervention_mode": "threshold",
            "intervention_strategy": "manager_support",
            "intervention_target": "high_degree",
            "intervention_strength": 0.30,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "hybrid_targeted_random_relief",
            "intervention_mode": "threshold",
            "intervention_strategy": "workload_relief",
            "intervention_target": "hybrid_targeted_random",
            "intervention_strength": 0.35,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "team_buffer_support",
            "intervention_mode": "threshold",
            "intervention_strategy": "team_buffer_support",
            "intervention_target": "high_observed_risk",
            "intervention_strength": 0.25,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
        {
            "label": "universal_support",
            "intervention_mode": "threshold",
            "intervention_strategy": "universal_support",
            "intervention_target": "high_observed_risk",
            "intervention_strength": 0.08,
            "intervention_budget_frac": 0.05,
            "intervention_strain_threshold": 0.6,
            "intervention_trigger_avg": 0.5,
            "intervention_trigger_observed": 0.55,
            "intervention_delay": 2,
            "intervention_start_step": None,
        },
    ]

    summary_rows = []

    print("\nRunning intervention experiment...\n")

    for cfg in intervention_configs:
        print(f"Condition: {cfg['label']}")

        for s in strain_levels:
            print(f"  initial_strain = {s:.3f}")

            for run in range(runs_per_level):
                sim_id = f"{cfg['label']}_s{s:.3f}_r{run}"

                run_simulation(
                    sim_id=sim_id,
                    N=N,
                    steps=steps,
                    save_dir=EXPERIMENT_DIR,
                    initial_strain_level=float(s),
                    intervention_mode=cfg["intervention_mode"],
                    intervention_start_step=cfg["intervention_start_step"],
                    intervention_strategy=cfg["intervention_strategy"],
                    intervention_target=cfg["intervention_target"],
                    intervention_strength=cfg["intervention_strength"],
                    intervention_budget_frac=cfg["intervention_budget_frac"],
                    intervention_strain_threshold=cfg["intervention_strain_threshold"],
                    intervention_trigger_avg=cfg["intervention_trigger_avg"],
                    intervention_trigger_observed=cfg["intervention_trigger_observed"],
                    intervention_delay=cfg["intervention_delay"],
                    condition_label=cfg["label"],
                    run_id=run,
                    connectivity=connectivity,
                )

                sim_folder = os.path.join(EXPERIMENT_DIR, f"sim_{sim_id}")
                metrics = pd.read_csv(os.path.join(sim_folder, "metrics.csv"))
                collapse = pd.read_csv(os.path.join(sim_folder, "collapse_info.csv")).iloc[0]

                collapsed = bool(collapse["frac_collapsed"])
                max_cluster = metrics["largest_high_strain_cluster"].max()

                local_cascade_cluster_threshold = max(2, int(np.ceil(0.30 * N)))
                local_cascade = (max_cluster >= local_cascade_cluster_threshold) and (not collapsed)

                summary_rows.append({
                    "condition": cfg["label"],
                    "initial_strain": float(s),
                    "run": run,
                    "collapsed": bool(collapse["frac_collapsed"]),
                    "time_to_collapse": collapse["frac_time_to_collapse"],
                    "operational_collapsed": bool(collapse["operational_collapsed"]),
                    "operational_time_to_collapse": collapse["operational_time_to_collapse"],
                    "severe_mean_collapsed": bool(collapse["severe_mean_collapsed"]),
                    "severe_mean_time_to_collapse": collapse["severe_mean_time_to_collapse"],
                    "local_failure_collapsed": bool(collapse["local_failure_collapsed"]),
                    "local_failure_time_to_collapse": collapse["local_failure_time_to_collapse"],
                    "final_avg_strain": metrics["avg_strain"].iloc[-1],
                    "final_high_strain_fraction": metrics["high_strain_fraction"].iloc[-1],
                    "final_largest_cluster": metrics["largest_high_strain_cluster"].iloc[-1],
                    "max_high_strain_fraction": metrics["high_strain_fraction"].max(),
                    "max_largest_cluster": max_cluster,
                    "cumulative_avg_strain": metrics["avg_strain"].sum(),
                    "moderate_strain_person_steps_total": metrics["moderate_strain_person_steps"].sum(),
                    "severe_strain_person_steps_total": metrics["severe_strain_person_steps"].sum(),
                    "operational_danger_steps_total": metrics["operational_danger_step"].sum(),
                    "final_avg_absorbed_workload": metrics["avg_absorbed_workload"].iloc[-1],
                    "total_sick_days": metrics["sick_day_count"].iloc[-1],
                    "total_missed_deadline_minor": metrics["missed_deadline_minor_count"].iloc[-1],
                    "total_missed_deadline_critical": metrics["missed_deadline_critical_count"].iloc[-1],
                    "total_lateness": metrics["lateness_count"].iloc[-1],
                    "total_ignored_email": metrics["ignored_email_count"].iloc[-1],
                    "total_complaints": metrics["complaint_count"].iloc[-1],
                    "total_engagement_drop": metrics["engagement_drop_count"].iloc[-1],
                    "total_overload_signal": metrics["overload_signal_count"].iloc[-1],
                    "total_high_error_rate": metrics["high_error_rate_count"].iloc[-1],
                    "avg_intervened_per_step": metrics["n_intervened"].mean(),
                    "avg_workload_relief_per_step": metrics["workload_relief_used"].mean(),
                    "avg_manager_support_per_step": metrics["manager_support_used"].mean(),
                    "avg_team_mediation_per_step": metrics["team_mediation_used"].mean(),
                    "avg_capacity_building_per_step": metrics["capacity_building_used"].mean(),
                    "local_cascade": local_cascade,
                })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(EXPERIMENT_DIR, "intervention_summary.csv")
    summary_df.to_csv(summary_path, index=False)

    agg_df = (
        summary_df
        .groupby(["condition", "initial_strain"], as_index=False)
        .agg(
            n_runs=("run", "count"),
            collapse_probability=("collapsed", "mean"),
            local_cascade_probability=("local_cascade", "mean"),
            median_time_to_collapse=(
                "time_to_collapse",
                lambda x: x.dropna().median() if len(x.dropna()) > 0 else np.nan
            ),
            operational_collapse_probability=("operational_collapsed", "mean"),
            severe_mean_collapse_probability=("severe_mean_collapsed", "mean"),
            local_failure_probability=("local_failure_collapsed", "mean"),
            median_operational_time_to_collapse=(
                "operational_time_to_collapse",
                lambda x: x.dropna().median() if len(x.dropna()) > 0 else np.nan
            ),
            median_severe_mean_time_to_collapse=(
                "severe_mean_time_to_collapse",
                lambda x: x.dropna().median() if len(x.dropna()) > 0 else np.nan
            ),
            mean_cumulative_avg_strain=("cumulative_avg_strain", "mean"),
            mean_moderate_strain_person_steps=("moderate_strain_person_steps_total", "mean"),
            mean_severe_strain_person_steps=("severe_strain_person_steps_total", "mean"),
            mean_operational_danger_steps=("operational_danger_steps_total", "mean"),
            mean_final_absorbed_workload=("final_avg_absorbed_workload", "mean"),
            mean_total_sick_days=("total_sick_days", "mean"),
            mean_total_missed_deadline_minor=("total_missed_deadline_minor", "mean"),
            mean_total_missed_deadline_critical=("total_missed_deadline_critical", "mean"),
            mean_total_lateness=("total_lateness", "mean"),
            mean_total_ignored_email=("total_ignored_email", "mean"),
            mean_total_complaints=("total_complaints", "mean"),
            mean_total_engagement_drop=("total_engagement_drop", "mean"),
            mean_total_overload_signal=("total_overload_signal", "mean"),
            mean_total_high_error_rate=("total_high_error_rate", "mean"),
            mean_final_high_strain_fraction=("final_high_strain_fraction", "mean"),
            mean_final_largest_cluster=("final_largest_cluster", "mean"),
            mean_max_high_strain_fraction=("max_high_strain_fraction", "mean"),
            mean_max_largest_cluster=("max_largest_cluster", "mean"),
            avg_intervened_per_step=("avg_intervened_per_step", "mean"),
            avg_workload_relief_per_step=("avg_workload_relief_per_step", "mean"),
            avg_manager_support_per_step=("avg_manager_support_per_step", "mean"),
            avg_team_mediation_per_step=("avg_team_mediation_per_step", "mean"),
            avg_capacity_building_per_step=("avg_capacity_building_per_step", "mean"),
        )
        .sort_values(["condition", "initial_strain"])
    )

    agg_path = os.path.join(EXPERIMENT_DIR, "intervention_aggregated.csv")
    agg_df.to_csv(agg_path, index=False)

    print("\nAggregated results:\n")
    print(agg_df.to_string(index=False))

    # ----------------------
    # Plot 1: Collapse probability
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["collapse_probability"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Collapse Probability")
    plt.title("Collapse Probability vs Initial Strain")
    plt.ylim(-0.02, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "collapse_probability_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 2: Local cascade probability
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["local_cascade_probability"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Local Cascade Probability")
    plt.title("Local Cascade Probability vs Initial Strain")
    plt.ylim(-0.02, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "local_cascade_probability_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 3: Median time to collapse
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["median_time_to_collapse"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Median Time to Collapse")
    plt.title("Median Time to Collapse vs Initial Strain")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "median_time_to_collapse_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 4: Mean max largest cluster
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["mean_max_largest_cluster"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Mean Max Largest Cluster")
    plt.title("Mean Max Largest Cluster vs Initial Strain")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "max_cluster_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 5: Cumulative Strain Burden
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["mean_cumulative_avg_strain"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Mean Cumulative Avg Strain")
    plt.title("Cumulative Harm Burden vs Initial Strain")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "cumulative_harm_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 6: Severe Strain Person-Steps
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["mean_severe_strain_person_steps"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Mean Severe Strain Person-Steps")
    plt.title("Severe Strain Exposure vs Initial Strain")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "severe_strain_exposure_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 7: Operational Collapse Probability
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["operational_collapse_probability"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Operational Collapse Probability")
    plt.title("Operational Collapse vs Initial Strain")
    plt.ylim(-0.02, 1.02)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "operational_collapse_vs_initial_strain.png"), dpi=300)
    plt.show()

    # ----------------------
    # Plot 8: Missed Critical Deadlines
    # ----------------------
    plt.figure(figsize=(8, 5))
    for cond, g in agg_df.groupby("condition"):
        plt.plot(g["initial_strain"], g["mean_total_missed_deadline_critical"], marker="o", label=cond)
    plt.xlabel("Initial Strain")
    plt.ylabel("Mean Total Critical Deadline Misses")
    plt.title("Critical Deadline Failures vs Initial Strain")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_DIR, "critical_deadlines_vs_initial_strain.png"), dpi=300)
    plt.show()

    print("\nDone.")
    print(f"Saved summary: {summary_path}")
    print(f"Saved aggregated results: {agg_path}")
    print(f"Saved figures in: {EXPERIMENT_DIR}")

# --- Auto Simulation Testing ---

def run_autosim(GameStateClass, runs=100):
    results = []
    collapsed_runs = 0
    for i in range(runs):
        game = GameStateClass(seed=i)
        while not game.game_over and game.week <= game.max_weeks:
            game.advance_week(action={"type": "do_nothing", "target": None})
        results.append(game.week)
        if game.result not in {"kept_job", "resigned_survived"}:
            collapsed_runs += 1

    import numpy as np
    avg_collapse = np.mean(results)
    collapse_rate = collapsed_runs / len(results)

    return {
        "runs": runs,
        "average_collapse_week": float(avg_collapse),
        "collapse_rate": float(collapse_rate)
    }


DEFAULT_POLICY_NAMES = [
    "do_nothing",
    "top_risk_manager_support",
    "symptom_targeted",
    "pressure_balanced",
]

DEFAULT_SCENARIO_BENCHMARKS = [
    "no_intervention",
    "misread_response",
    "mixed_response",
    "stabilising_response",
]

SIM_TO_GAME_ACTION = sim_action_map()


def to_game_action(action_type: str) -> str:
    return SIM_TO_GAME_ACTION.get(action_type, action_type)


def choose_policy_action(game, policy_name):
    visible = game.get_visible_state()

    if policy_name == "do_nothing" or not visible:
        return {"type": "do_nothing", "target": None}

    top = visible[0]
    target = top["id"]
    signs = str(top.get("warning_signs", ""))
    summary = game.get_summary()
    pressure_state = summary.get("pressure_state", "Stable")

    if policy_name == "top_risk_manager_support":
        return {"type": to_game_action("manager_support"), "target": target}

    if policy_name == "symptom_targeted":
        if "overload_signal" in signs or "sick_day" in signs:
            action_type = "workload_relief"
        elif "complaint" in signs or "ignored_email" in signs:
            action_type = "team_mediation"
        elif "high_error_rate" in signs or "missed_deadline_critical" in signs:
            action_type = "capacity_building"
        else:
            action_type = "manager_support"
        return {"type": to_game_action(action_type), "target": target}

    if policy_name == "pressure_balanced":
        if (
            pressure_state in {"Critical", "Collapse Imminent"}
            and summary.get("largest_high_strain_cluster", 0) >= max(4, int(np.ceil(0.25 * game.team_size)))
        ):
            return {"type": to_game_action("team_buffer_support"), "target": None}
        if summary.get("high_risk_count", 0) >= max(3, int(np.ceil(0.20 * game.team_size))):
            return {"type": to_game_action("universal_support"), "target": None}
        if "overload_signal" in signs or "sick_day" in signs:
            return {"type": to_game_action("workload_relief"), "target": target}
        if "complaint" in signs or "ignored_email" in signs:
            return {"type": to_game_action("team_mediation"), "target": target}
        if top.get("observed_risk", 0.0) >= 0.65:
            return {"type": to_game_action("capacity_building"), "target": target}
        return {"type": to_game_action("manager_support"), "target": target}

    raise ValueError(f"Unknown policy_name: {policy_name}")


def _apply_scenario_benchmark_week(game, benchmark_name):
    apply_benchmark_actions_for_week(game, benchmark_name)


def run_scenario_benchmarks(
    GameStateClass,
    scenario,
    difficulty="Normal",
    runs_per_benchmark=8,
    benchmark_names=None,
    **game_kwargs,
):
    benchmark_names = benchmark_names or list(DEFAULT_SCENARIO_BENCHMARKS)
    benchmark_rows = []

    for benchmark_name in benchmark_names:
        run_rows = []
        for seed in range(runs_per_benchmark):
            game = GameStateClass(
                difficulty=difficulty,
                scenario=scenario,
                seed=seed,
                **game_kwargs,
            )

            while not game.game_over and game.week <= game.max_weeks:
                _apply_scenario_benchmark_week(game, benchmark_name)

            summary = game.get_summary()
            run_rows.append({
                "result": game.result,
                "end_week": int(game.week),
                "collapsed": bool(game.result not in {"kept_job", "resigned_survived"}),
                "peak_cluster": summary.get("largest_high_strain_cluster", 0),
                "manager_strain": float(game.manager_state.get("strain", 0.0)),
                "high_risk_count": int(summary.get("high_risk_count", 0)),
                "run_strategy_profile": getattr(game, "run_strategy_profile", benchmark_name),
            })

        end_weeks = [row["end_week"] for row in run_rows]
        collapse_rate = float(np.mean([row["collapsed"] for row in run_rows])) if run_rows else 0.0
        common_results = pd.Series([row["result"] for row in run_rows]).value_counts()
        common_result = common_results.index[0] if not common_results.empty else "unknown"

        benchmark_rows.append({
            "benchmark": benchmark_name,
            "runs": len(run_rows),
            "collapse_rate": collapse_rate,
            "average_end_week": float(np.mean(end_weeks)) if end_weeks else 0.0,
            "common_result": common_result,
            "average_peak_cluster": float(np.mean([row["peak_cluster"] for row in run_rows])) if run_rows else 0.0,
            "average_final_manager_strain": float(np.mean([row["manager_strain"] for row in run_rows])) if run_rows else 0.0,
            "average_high_risk_count": float(np.mean([row["high_risk_count"] for row in run_rows])) if run_rows else 0.0,
        })

    return {
        "scenario": scenario,
        "difficulty": difficulty,
        "benchmarks": benchmark_rows,
    }


def _collect_weekly_metrics(game, run_id, policy_name, difficulty, seed, settings, action, week_number):
    summary = game.get_summary()
    strains = np.array([game.G.nodes[n]["strain"] for n in game.G.nodes()], dtype=float)
    observed = np.array([game.G.nodes[n].get("observed_risk", 0.0) for n in game.G.nodes()], dtype=float)
    absorbed = np.array([game.G.nodes[n].get("last_absorbed_workload", 0.0) for n in game.G.nodes()], dtype=float)
    supports = np.array([1 if game.G.nodes[n].get("recent_support", False) else 0 for n in game.G.nodes()], dtype=int)
    resources = np.array([game.G.nodes[n].get("resources", 0.0) for n in game.G.nodes()], dtype=float)
    engagements = np.array([game.G.nodes[n].get("engagement", 0.0) for n in game.G.nodes()], dtype=float)
    trusts = np.array([game.G.nodes[n].get("trust", 0.0) for n in game.G.nodes()], dtype=float)

    return {
        "run_id": run_id,
        "policy": policy_name,
        "difficulty": difficulty,
        "seed": seed,
        "team_size": settings["team_size"],
        "max_weeks": settings["max_weeks"],
        "initial_strain": settings["initial_strain"],
        "starting_org_resource": settings["starting_budget"],
        "connectivity": settings["connectivity"],
        "founder_quality": settings["founder_quality"],
        "week": week_number,
        "phase": summary["phase"],
        "pressure_state": summary["pressure_state"],
        "action_type": action["type"],
        "action_target": action.get("target"),
        "manager_energy_remaining": summary.get("manager_energy_current", 0.0),
        "avg_strain": float(np.mean(strains)),
        "avg_observed_risk": summary["avg_observed_risk"],
        "high_risk_count": summary["high_risk_count"],
        "critical_warning_signs": summary["critical_warning_signs"],
        "largest_high_strain_cluster": summary["largest_high_strain_cluster"],
        "high_strain_count": int(np.sum(strains > 0.60)),
        "severe_strain_count": int(np.sum(strains >= 0.75)),
        "supported_employee_count": int(np.sum(supports)),
        "absorbed_workload_count": int(np.sum(absorbed > 0.25)),
        "avg_absorbed_workload": float(np.mean(absorbed)),
        "avg_resources": float(np.mean(resources)),
        "avg_engagement": float(np.mean(engagements)),
        "avg_trust": float(np.mean(trusts)),
        "avg_strain_danger_weeks": summary["avg_strain_danger_weeks"],
        "cluster_danger_weeks": summary["cluster_danger_weeks"],
        "high_risk_danger_weeks": summary["high_risk_danger_weeks"],
        "crisis_warning_weeks": summary["crisis_warning_weeks"],
        "game_over": bool(game.game_over),
        "result": game.result,
    }


def _save_policy_experiment_plots(aggregated_df, output_dir):
    if aggregated_df.empty:
        return

    plot_specs = [
        ("collapse_rate", "Collapse Rate", "collapse_rate_by_policy_difficulty.png", (0, 1)),
        ("average_end_week", "Average End Week", "average_end_week_by_policy_difficulty.png", None),
        ("average_peak_avg_strain", "Average Peak Avg Strain", "peak_avg_strain_by_policy_difficulty.png", (0, 1)),
        ("average_final_manager_capacity", "Average Final Manager Capacity", "final_manager_capacity_by_policy_difficulty.png", None),
    ]

    for column, title, filename, ylim in plot_specs:
        pivot = (
            aggregated_df
            .pivot(index="policy", columns="difficulty", values=column)
            .reindex(DEFAULT_POLICY_NAMES)
        )
        ax = pivot.plot(kind="bar", figsize=(9, 5))
        ax.set_title(title)
        ax.set_xlabel("Policy")
        ax.set_ylabel(title)
        if ylim is not None:
            ax.set_ylim(*ylim)
        ax.grid(True, axis="y", alpha=0.25)
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename), dpi=300)
        plt.close()


def run_policy_experiment_suite(
    GameStateClass,
    runs_per_condition=25,
    difficulties=None,
    policy_names=None,
    output_dir="outputs_gameplay_reports",
    **game_kwargs,
):
    difficulties = difficulties or ["Easy", "Normal", "Hard"]
    policy_names = policy_names or list(DEFAULT_POLICY_NAMES)

    os.makedirs(output_dir, exist_ok=True)

    run_rows = []
    weekly_rows = []

    for difficulty in difficulties:
        for policy_name in policy_names:
            for seed in range(runs_per_condition):
                settings = {
                    "team_size": game_kwargs.get("team_size", 15),
                    "max_weeks": game_kwargs.get("max_weeks", 52),
                    "initial_strain": game_kwargs.get("initial_strain", 0.15),
                    "starting_budget": game_kwargs.get("starting_budget", 100.0),
                    "connectivity": game_kwargs.get("connectivity", 0.30),
                    "founder_quality": game_kwargs.get("founder_quality", 0.5),
                }
                game = GameStateClass(difficulty=difficulty, seed=seed, **settings)
                run_id = f"{difficulty.lower()}__{policy_name}__seed_{seed}"
                run_weekly = []

                while not game.game_over and game.week <= game.max_weeks:
                    week_number = game.week
                    action = choose_policy_action(game, policy_name)
                    game.advance_week(action)
                    row = _collect_weekly_metrics(
                        game,
                        run_id=run_id,
                        policy_name=policy_name,
                        difficulty=difficulty,
                        seed=seed,
                        settings=settings,
                        action=action,
                        week_number=week_number,
                    )
                    weekly_rows.append(row)
                    run_weekly.append(row)

                peak_avg_strain = max((row["avg_strain"] for row in run_weekly), default=float("nan"))
                peak_high_risk_count = max((row["high_risk_count"] for row in run_weekly), default=0)
                peak_cluster = max((row["largest_high_strain_cluster"] for row in run_weekly), default=0)
                crisis_weeks = sum(1 for row in run_weekly if row["phase"] == "crisis")
                universal_support_uses = sum(1 for row in run_weekly if row["action_type"] == "universal_support")
                team_buffer_uses = sum(1 for row in run_weekly if row["action_type"] == "team_buffer_support")

                run_rows.append({
                    "run_id": run_id,
                    "policy": policy_name,
                    "difficulty": difficulty,
                    "seed": seed,
                    "team_size": settings["team_size"],
                    "max_weeks": settings["max_weeks"],
                    "initial_strain": settings["initial_strain"],
                    "starting_org_resource": settings["starting_budget"],
                    "connectivity": settings["connectivity"],
                    "founder_quality": settings["founder_quality"],
                    "result": game.result,
                    "survived": bool(game.result in {"kept_job", "resigned_survived"}),
                    "collapsed": bool(game.result not in {"kept_job", "resigned_survived"}),
                    "end_week": int(game.week),
                    "final_manager_capacity": float(game.manager_state["capacity_current"]),
                    "final_org_resource": float(game.org_resource),
                    "peak_avg_strain": float(peak_avg_strain),
                    "peak_high_risk_count": int(peak_high_risk_count),
                    "peak_largest_cluster": int(peak_cluster),
                    "mean_avg_strain": float(np.mean([row["avg_strain"] for row in run_weekly])) if run_weekly else np.nan,
                    "mean_avg_observed_risk": float(np.mean([row["avg_observed_risk"] for row in run_weekly])) if run_weekly else np.nan,
                    "mean_manager_energy_remaining": float(np.mean([row["manager_energy_remaining"] for row in run_weekly])) if run_weekly else np.nan,
                    "crisis_weeks": int(crisis_weeks),
                    "universal_support_uses": int(universal_support_uses),
                    "team_buffer_support_uses": int(team_buffer_uses),
                })

    weekly_df = pd.DataFrame(weekly_rows)
    run_df = pd.DataFrame(run_rows)
    aggregated_df = (
        run_df
        .groupby(["difficulty", "policy"], as_index=False)
        .agg(
            runs=("run_id", "count"),
            collapse_rate=("collapsed", "mean"),
            survival_rate=("survived", "mean"),
            average_end_week=("end_week", "mean"),
            average_final_manager_capacity=("final_manager_capacity", "mean"),
            average_mean_manager_energy_remaining=("mean_manager_energy_remaining", "mean"),
            average_peak_avg_strain=("peak_avg_strain", "mean"),
            average_peak_high_risk_count=("peak_high_risk_count", "mean"),
            average_peak_largest_cluster=("peak_largest_cluster", "mean"),
            average_crisis_weeks=("crisis_weeks", "mean"),
        )
        .sort_values(["difficulty", "policy"])
    )

    weekly_path = os.path.join(output_dir, "weekly_metrics.csv")
    run_path = os.path.join(output_dir, "run_summary.csv")
    aggregated_path = os.path.join(output_dir, "aggregated_summary.csv")

    weekly_df.to_csv(weekly_path, index=False)
    run_df.to_csv(run_path, index=False)
    aggregated_df.to_csv(aggregated_path, index=False)
    _save_policy_experiment_plots(aggregated_df, output_dir)

    return {
        "weekly_metrics_path": weekly_path,
        "run_summary_path": run_path,
        "aggregated_summary_path": aggregated_path,
        "runs": int(len(run_df)),
        "weeks_logged": int(len(weekly_df)),
        "summary": aggregated_df,
    }
