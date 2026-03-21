import numpy as np
import networkx as nx
import intervention_engine
import scenario_runtime
from action_registry import ACTION_REGISTRY, action_category, action_cost, is_team_wide
from role_config import ROLE_MODIFIERS
from scenario_definitions import SCENARIOS
from simulation_engine import (
    initialize_intervention_state,
    apply_shock,
    update_node_states,
    generate_behavior_signals,
    update_observed_risk,
    update_edge_weights,
    update_network_structure,
    apply_passive_recovery,
    propagate_support,
)

# ============================================================
# BASIC STARTUP DATA
# ============================================================

FOUNDER_EMPLOYEE = {"name": "Alex", "role": "Founder"}

TEAM_EMPLOYEES = [
    {"name": "Maya", "role": "Lead Engineer"},
    {"name": "Jordan", "role": "Product Manager"},
    {"name": "Sam", "role": "Backend Engineer"},
    {"name": "Taylor", "role": "Frontend Engineer"},
    {"name": "Riley", "role": "Designer"},
    {"name": "Avery", "role": "Data Scientist"},
    {"name": "Morgan", "role": "Operations"},
    {"name": "Casey", "role": "Sales Lead"},
    {"name": "Drew", "role": "Account Executive"},
    {"name": "Quinn", "role": "Customer Success"},
    {"name": "Harper", "role": "Marketing Lead"},
    {"name": "Jamie", "role": "Finance Manager"},
    {"name": "Blake", "role": "People Ops"},
    {"name": "Rowan", "role": "QA Engineer"},
    {"name": "Parker", "role": "Systems Analyst"},
]

ACTION_CATEGORIES = {action_id: action_category(action_id) for action_id in ACTION_REGISTRY}
TEAM_WIDE_ACTIONS = {
    action_id for action_id in ACTION_REGISTRY if is_team_wide(action_id)
}

ROLE_CLASS_MAP = {
    "Founder": "founder",
    "Lead Engineer": "lead",
    "Product Manager": "lead",
    "Backend Engineer": "ic",
    "Frontend Engineer": "ic",
    "Designer": "ic",
    "Data Scientist": "ic",
    "Operations": "support",
    "Sales Lead": "lead",
    "Account Executive": "support",
    "Customer Success": "support",
    "Marketing Lead": "lead",
    "Finance Manager": "support",
    "People Ops": "support",
    "QA Engineer": "ic",
    "Systems Analyst": "support",
}

DIFFICULTY_PRESETS = {
    "Easy": {
        "shock_freq_mult": 1.02,
        "shock_budget_mult": 1.02,
        "shock_strain_mult": 1.02,
        "shock_aftereffect_mult": 1.02,
        "positive_relief_mult": 0.98,
        "passive_recovery_mult": 0.98,
        "support_propagation_mult": 1.00,
        "collapse_threshold_mult": 1.00,
        "contagion_mult": 1.00,
        "workload_strain_mult": 1.00,
        "noise_mult": 0.98,
        "instability_bias": 0.001,
        "behavior_escalation_mult": 1.00,
        "crisis_avg_threshold": 0.60,
        "danger_avg_threshold": 0.65,
        "danger_high_fraction_threshold": 0.43,
        "danger_cluster_fraction": 0.39,
        "danger_limit": 5,
        "crisis_persistence_weeks": 2,
    },
    "Normal": {
        "shock_freq_mult": 1.28,
        "shock_budget_mult": 1.12,
        "shock_strain_mult": 1.16,
        "shock_aftereffect_mult": 1.32,
        "positive_relief_mult": 0.84,
        "passive_recovery_mult": 0.72,
        "support_propagation_mult": 0.93,
        "collapse_threshold_mult": 0.92,
        "contagion_mult": 1.35,
        "workload_strain_mult": 1.40,
        "noise_mult": 1.22,
        "instability_bias": 0.015,
        "behavior_escalation_mult": 1.22,
        "crisis_avg_threshold": 0.58,
        "danger_avg_threshold": 0.63,
        "danger_high_fraction_threshold": 0.40,
        "danger_cluster_fraction": 0.36,
        "danger_limit": 4,
        "crisis_persistence_weeks": 2,
    },
    "Hard": {
        "shock_freq_mult": 1.42,
        "shock_budget_mult": 1.20,
        "shock_strain_mult": 1.26,
        "shock_aftereffect_mult": 1.38,
        "positive_relief_mult": 0.72,
        "passive_recovery_mult": 0.62,
        "support_propagation_mult": 0.90,
        "collapse_threshold_mult": 0.88,
        "contagion_mult": 1.52,
        "workload_strain_mult": 1.56,
        "noise_mult": 1.38,
        "instability_bias": 0.022,
        "behavior_escalation_mult": 1.30,
        "crisis_avg_threshold": 0.57,
        "danger_avg_threshold": 0.62,
        "danger_high_fraction_threshold": 0.38,
        "danger_cluster_fraction": 0.35,
        "danger_limit": 4,
        "crisis_persistence_weeks": 2,
    },
}

# ============================================================
# GAME STATE
# ============================================================

class GameState:
    def __init__(
        self,
        team_size=15,
        max_weeks=52,
        initial_strain=0.15,
        starting_budget=100.0,
        connectivity=0.30,
        founder_quality=0.5,
        difficulty="Normal",
        scenario="Baseline",
        evaluation_mode=None,
        seed=None,
        debug=False,
    ):
        scenario = scenario if scenario in SCENARIOS else "Baseline"
        self.scenario = scenario
        self.scenario_definition = SCENARIOS[self.scenario]
        resolved_evaluation_mode = evaluation_mode or self.scenario_definition.default_evaluation_mode
        if resolved_evaluation_mode not in self.scenario_definition.evaluation_modes:
            resolved_evaluation_mode = self.scenario_definition.default_evaluation_mode
        self.evaluation_mode = resolved_evaluation_mode
        self.scenario_config = {
            "name": self.scenario_definition.name,
            "label": self.scenario_definition.label,
            "teaching_pattern": self.scenario_definition.teaching_pattern,
            "description": self.scenario_definition.description,
            "team_size": self.scenario_definition.team_size,
            "default_length": self.scenario_definition.length,
            "primary_lesson": self.scenario_definition.primary_lesson,
            "intro_text": (
                self.scenario_definition.ui_config.briefing_narrative_template
                if self.scenario_definition.ui_config is not None
                else self.scenario_definition.description
            ),
            "default_evaluation_mode": self.scenario_definition.default_evaluation_mode,
            "evaluation_modes": self.scenario_definition.evaluation_modes,
            "evaluation_mode": self.evaluation_mode,
            "surface_story": self.scenario_definition.surface_story.get("summary", ""),
            "underlying_story": self.scenario_definition.hidden_pattern.get("summary", ""),
            "benchmark_text": {
                key: value.get("summary", "")
                for key, value in self.scenario_definition.benchmark_paths.items()
            },
            "role_assignments": self.scenario_definition.runtime_preset.get("role_assignments", {}),
            "ui_schema": self.scenario_definition.ui_schema,
            "ui_config": self.scenario_definition.ui_config,
        }

        self.team_size = int(self.scenario_config.get("team_size", team_size))
        self.max_weeks = int(self.scenario_config.get("default_length", max_weeks))
        self.initial_strain = initial_strain
        # Internal org-health budget remains available for background shocks only.
        self.org_resource = float(starting_budget)
        self.connectivity = connectivity
        self.founder_quality = float(np.clip(founder_quality, 0.0, 1.0))
        difficulty_aliases = {
            "Tutorial": "Easy",
            "Medium": "Normal",
        }
        difficulty = difficulty_aliases.get(difficulty, difficulty)
        self.difficulty = difficulty if difficulty in DIFFICULTY_PRESETS else "Normal"
        self.diff = DIFFICULTY_PRESETS[self.difficulty]
        self.debug = debug

        self.week = 1
        self.phase = "management"
        self.game_over = False
        self.result = None
        self.weeks_in_crisis = 0

        self.rng_seed = seed
        self.rng = np.random.RandomState(seed)

        self.event_log = []
        self.weekly_event_text = []
        self.last_action_summary = ""
        self.last_metrics = {}
        self.analysis_history = []
        self.current_week_actions = []
        self.current_week_diagnosis = ""
        self.weekly_energy_regen = 0.0
        self.pending_team_effects = []
        self.run_strategy_counters = {
            "total_actions": 0,
            "targeted_actions": 0,
            "clustered_actions": 0,
            "team_actions": 0,
            "focal_targeted_actions": 0,
        }
        self.run_strategy_profile = "no_intervention"
        self.scenario_outcome_tier = None
        self.scenario_outcome_title = None
        self.scenario_outcome_explanation = ""
        self.scenario_outcome_strength = ""
        self.scenario_outcome_improvement = ""
        self.scenario_mastery_reveal = ""

        # Pressure / collapse tracking
        self.avg_strain_danger_weeks = 0
        self.cluster_danger_weeks = 0
        self.high_risk_danger_weeks = 0
        self.crisis_warning_weeks = 0
        self.cluster_tipping_active = False
        self.manager_tipping_active = False
        self.founder_tipping_active = False

        self.manager_state = self.initialize_manager_state()
        self.founder_state = self.initialize_founder_state()
        self.scenario_state = self.initialize_scenario_state()

        self.G = self.initialize_team(self.team_size)
        self.G.graph["difficulty_profile"] = dict(self.diff)
        self.apply_scenario_preset()
        update_observed_risk(
            self.G,
            decay=0.9,
            noise_sd=0.02,
            manager_state=self.manager_state,
            founder_state=self.founder_state,
        )
        self.refresh_metrics()
        self.update_phase(force=True)

    def scale_threshold(self, value):
        return float(np.clip(value * self.diff["collapse_threshold_mult"], 0.0, 1.0))

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def initialize_manager_state(self):
        return {
            "name": "You",
            "strain": 0.18,
            "energy_max": 10.0,
            "energy_current": 10.0,
            "visibility_skill": 0.62,
            "intervention_skill": 0.60,
            "relationship_with_founder": float(np.clip(0.48 + 0.20 * self.founder_quality, 0, 1)),
            "recent_actions": [],
            "overload_weeks": 0,
        }

    def initialize_founder_state(self):
        supportiveness = float(np.clip(0.38 + 0.42 * self.founder_quality, 0, 1))
        clarity = float(np.clip(0.34 + 0.50 * self.founder_quality, 0, 1))
        relationship = float(np.clip(0.42 + 0.26 * self.founder_quality, 0, 1))
        pressure = float(np.clip(0.54 - 0.24 * self.founder_quality, 0.1, 0.9))
        return {
            "founder_pressure": pressure,
            "founder_supportiveness": supportiveness,
            "founder_clarity": clarity,
            "founder_relationship_to_manager": relationship,
        }

    def initialize_scenario_state(self):
        scenario_state = {
            "name": self.scenario,
            "intro_shown": False,
            "scenario_roles": {},
            "surface_story": self.scenario_config.get("surface_story", ""),
            "underlying_story": self.scenario_config.get("underlying_story", ""),
            "benchmark_path_guess": "no_intervention",
            "clustered_action_weeks": [],
            "clustered_actions_by_week_3": 0,
            "clustered_actions_on_core_targets_by_week_3": 0,
            "targeted_on_focal_by_week_2": 0,
            "early_targeted_on_focal_count": 0,
            "sensible_targeted_on_focal_by_week_5": 0,
            "containment_core_actions_by_week_3": 0,
            "acceptable_route_active": False,
            "great_manager_path_active": False,
        }
        scenario_state.update(self.scenario_definition.runtime_preset.get("scenario_state_defaults", {}))
        return scenario_state

    def initialize_team(self, team_size):
        total_nodes = team_size + 1
        G = nx.erdos_renyi_graph(total_nodes, self.connectivity, seed=self.rng)
        G.graph["rng"] = self.rng

        if total_nodes > 1:
            for node in G.nodes():
                if G.degree(node) == 0:
                    other = self.rng.choice([n for n in G.nodes() if n != node])
                    G.add_edge(node, other)

        for i, node in enumerate(G.nodes()):
            G.nodes[node]["strain"] = float(np.clip(self.rng.normal(self.initial_strain, 0.05), 0, 1))
            G.nodes[node]["trust"] = float(self.rng.uniform(0.45, 0.85))
            G.nodes[node]["alignment"] = float(self.rng.uniform(0.45, 0.85))
            G.nodes[node]["engagement"] = float(self.rng.uniform(0.45, 0.85))
            G.nodes[node]["resources"] = float(self.rng.uniform(5.0, 10.0))
            G.nodes[node]["vulnerability"] = float(self.rng.uniform(0.2, 0.8))

            if i == 0:
                person = FOUNDER_EMPLOYEE
            else:
                person = TEAM_EMPLOYEES[(i - 1) % len(TEAM_EMPLOYEES)]
            G.nodes[node]["name"] = person["name"]
            G.nodes[node]["role"] = person["role"]
            role_class = ROLE_CLASS_MAP.get(person["role"], "ic")
            role_modifiers = ROLE_MODIFIERS[role_class]
            G.nodes[node]["role_class"] = role_class
            G.nodes[node]["role_observability"] = role_modifiers["observability"]
            G.nodes[node]["visibility_modifier"] = role_modifiers["observability"]
            G.nodes[node]["manager_relationship"] = float(np.clip(
                self.rng.uniform(0.35, 0.75)
                + 0.08 * (G.nodes[node]["trust"] - 0.60)
                + (0.05 if role_class in {"ic", "support"} else -0.04),
                0.20,
                0.90,
            ))
            G.nodes[node]["manager_contact_frequency"] = float(np.clip(
                self.rng.uniform(0.40, 0.85)
                + (0.08 if role_class in {"lead", "ic"} else -0.03),
                0.20,
                0.95,
            ))
            G.nodes[node]["last_intervention_success"] = None
            G.nodes[node]["intervention_history"] = []

            G.nodes[node]["recent_support"] = False
            G.nodes[node]["last_action_note"] = ""
            G.nodes[node]["last_absorbed_workload"] = 0.0
            G.nodes[node]["scenario_display_load"] = 0.0
            G.nodes[node]["scenario_role"] = None
            G.nodes[node]["scenario_cluster_id"] = None
            G.nodes[node]["scenario_visibility_bias"] = 0.0
            G.nodes[node]["scenario_spillover_bias"] = 0.0

            if role_class == "founder":
                G.nodes[node]["founder_pressure"] = self.founder_state["founder_pressure"]
                G.nodes[node]["founder_supportiveness"] = self.founder_state["founder_supportiveness"]
                G.nodes[node]["founder_clarity"] = self.founder_state["founder_clarity"]
                G.nodes[node]["founder_relationship_to_manager"] = self.founder_state["founder_relationship_to_manager"]

        initialize_intervention_state(G)

        for u, v in G.edges():
            G.edges[u, v]["weight"] = float(self.rng.uniform(0.08, 0.25))

        return G

    def founder_node_id(self):
        for n in self.G.nodes():
            if self.G.nodes[n].get("role_class") == "founder":
                return n
        return None

    def managed_node_ids(self):
        founder_id = self.founder_node_id()
        return [n for n in self.G.nodes() if n != founder_id]

    def apply_scenario_preset(self):
        if self.scenario == "Baseline":
            return
        self._assign_scenario_roles()
        self._apply_scenario_initial_state()
        self._apply_scenario_network_overrides()
        self._apply_scenario_tuning_overrides()

    def _assign_scenario_roles(self):
        role_assignments = self.scenario_config.get("role_assignments", {})
        scenario_roles = {}
        for scenario_role, employee_name in role_assignments.items():
            node_id = self.get_node_by_name(employee_name)
            if node_id is None:
                continue
            scenario_roles[scenario_role] = node_id
            self.G.nodes[node_id]["scenario_role"] = scenario_role
            self.G.nodes[node_id]["scenario_cluster_id"] = self.scenario
        self.scenario_state["scenario_roles"] = scenario_roles

    def _apply_scenario_initial_state(self):
        roles = self.scenario_state.get("scenario_roles", {})
        overrides = self.scenario_definition.runtime_preset.get("node_overrides", {})

        for scenario_role, node_id in roles.items():
            node = self.G.nodes[node_id]
            role_override = overrides.get(scenario_role, {})
            for key, value in role_override.items():
                if key in {"strain", "trust", "alignment", "engagement", "manager_relationship", "manager_contact_frequency"}:
                    min_value = 0.10 if key == "manager_relationship" else 0.0
                    max_value = 0.95 if key in {"manager_relationship", "manager_contact_frequency"} else 1.0
                    node[key] = float(np.clip(value, min_value, max_value))
                elif key == "recent_behaviors":
                    node[key] = value[:]
                else:
                    node[key] = value

        named_overrides = self.scenario_definition.runtime_preset.get("named_node_overrides", {})
        for employee_name, node_override in named_overrides.items():
            node_id = self.get_node_by_name(employee_name)
            if node_id is None:
                continue
            node = self.G.nodes[node_id]
            for key, value in node_override.items():
                if key in {"strain", "trust", "alignment", "engagement", "manager_relationship", "manager_contact_frequency"}:
                    min_value = 0.10 if key == "manager_relationship" else 0.0
                    max_value = 0.95 if key in {"manager_relationship", "manager_contact_frequency"} else 1.0
                    node[key] = float(np.clip(value, min_value, max_value))
                elif key == "recent_behaviors":
                    node[key] = value[:]
                else:
                    node[key] = value

    def _apply_scenario_network_overrides(self):
        roles = self.scenario_state.get("scenario_roles", {})
        cluster_nodes = [node_id for node_id in roles.values() if node_id in self.G.nodes()]
        cluster_edges = self.scenario_definition.runtime_preset.get("forced_edges", [])

        for edge_rule in cluster_edges:
            left = roles.get(edge_rule["left_role"])
            right = roles.get(edge_rule["right_role"])
            if left is None or right is None:
                continue
            if not self.G.has_edge(left, right):
                self.G.add_edge(left, right)
            weight_min, weight_max = edge_rule.get("weight_range", [0.32, 0.48])
            self.G.edges[left, right]["weight"] = float(self.rng.uniform(weight_min, weight_max))

        cluster_adjustments = self.scenario_definition.runtime_preset.get("cluster_node_adjustments", {})
        for node_id in cluster_nodes:
            for key, delta in cluster_adjustments.items():
                self.G.nodes[node_id][key] = float(np.clip(self.G.nodes[node_id].get(key, 0.0) + delta, 0, 1))

    def _apply_scenario_tuning_overrides(self):
        manager_adjustments = self.scenario_definition.runtime_preset.get("manager_state_adjustments", {})
        founder_adjustments = self.scenario_definition.runtime_preset.get("founder_state_adjustments", {})
        bounded_manager_fields = {
            "strain",
            "visibility_skill",
            "intervention_skill",
            "relationship_with_founder",
        }
        for key, delta in manager_adjustments.items():
            current = self.manager_state.get(key, 0.0)
            updated = current + delta
            if key in bounded_manager_fields:
                updated = float(np.clip(updated, 0, 1))
            elif key in {"energy_current", "energy_max"}:
                updated = max(0.0, float(updated))
            self.manager_state[key] = float(updated)
        for key, delta in founder_adjustments.items():
            self.founder_state[key] = float(np.clip(self.founder_state.get(key, 0.0) + delta, 0, 1))

    def get_scenario_overview(self):
        return {
            "key": self.scenario,
            "name": self.scenario_config.get("name", self.scenario),
            "label": self.scenario_config.get("label", self.scenario_config.get("name", self.scenario)),
            "teaching_pattern": self.scenario_config.get("teaching_pattern", ""),
            "description": self.scenario_config.get("description", ""),
            "team_size": self.team_size,
            "default_length": self.max_weeks,
            "primary_lesson": self.scenario_config.get("primary_lesson", ""),
            "intro_text": self.scenario_config.get("intro_text", ""),
            "benchmark_text": self.scenario_config.get("benchmark_text", {}),
            "default_evaluation_mode": self.scenario_config.get("default_evaluation_mode", "teaching"),
            "evaluation_modes": self.scenario_config.get("evaluation_modes", {}),
            "evaluation_mode": self.evaluation_mode,
            "ui_schema": self.scenario_config.get("ui_schema", {}),
            "ui_config": self.scenario_config.get("ui_config"),
        }

    def set_weekly_diagnosis(self, text):
        self.current_week_diagnosis = (text or "").strip()

    def _player_facing_workload_value(self, node):
        if self.scenario == "scenario_02":
            return float(node.get("scenario_display_load", 0.0))
        return max(
            float(node.get("absorbed_workload", 0.0)),
            float(node.get("last_absorbed_workload", 0.0)),
        )

    # ========================================================
    # PLAYER-FACING STATE
    # ========================================================

    def get_visible_state(self):
        visible = []

        for n in self.managed_node_ids():
            node = self.G.nodes[n]
            workload_value = self._player_facing_workload_value(node)
            strong_dependency_count = sum(
                1
                for neighbor in self.G.neighbors(n)
                if self.G.edges[n, neighbor].get("weight", 0.0) >= 0.28
            )

            if workload_value >= 0.42:
                workload_clue = "Often ends up carrying extra cleanup"
            elif workload_value >= 0.18:
                workload_clue = "Seems to pick up background work when things get messy"
            else:
                workload_clue = "No clear sign of extra hidden load"

            if strong_dependency_count >= 4:
                dependency_clue = "Several people seem to rely on them to keep work moving"
            elif strong_dependency_count >= 2:
                dependency_clue = "They look tied into multiple handoffs"
            else:
                dependency_clue = "No strong dependency pattern stands out yet"

            if node["strain"] >= 0.72:
                pressure_clue = "Pressure looks close to becoming unsustainable"
            elif node["strain"] >= 0.55 or node.get("observed_risk", 0.0) >= 0.55:
                pressure_clue = "Pressure is building"
            else:
                pressure_clue = "No obvious sign of acute pressure beyond the usual week-to-week load"

            entry = {
                "rank": 0,
                "id": n,
                "name": node["name"],
                "role": node["role"],
                "scenario_role": node.get("scenario_role"),
                "role_class": node.get("role_class", "ic"),
                "observed_risk": round(node.get("observed_risk", 0.0), 2),
                "risk_label": self.risk_label(node.get("observed_risk", 0.0)),
                "warning_signs": ", ".join(node.get("recent_behaviors", [])[-3:]) or "-",
                "engagement_hint": self.engagement_hint(node["engagement"]),
                "absorbed_workload_value": round(workload_value, 2),
                "absorbed_workload": "Yes" if workload_value > 0.10 else "-",
                "recent_support": "Yes" if node.get("recent_support", False) else "-",
                "recent_support_history": node.get("intervention_history", [])[-3:],
                "manager_relationship": round(node.get("manager_relationship", 0.0), 2),
                "last_intervention_success": node.get("last_intervention_success", None),
                "workload_clue": workload_clue,
                "dependency_clue": dependency_clue,
                "pressure_clue": pressure_clue,
                "strong_dependency_count": strong_dependency_count,
            }

            if self.debug:
                entry["true_strain_debug"] = round(node["strain"], 2)

            visible.append(entry)

        visible.sort(key=lambda x: x["observed_risk"], reverse=True)
        for rank, entry in enumerate(visible, start=1):
            entry["rank"] = rank
        return visible

    def get_summary(self):
        self.refresh_metrics()
        metrics = self.last_metrics

        summary = {
            "scenario": self.scenario,
            "scenario_name": self.scenario_config.get("name", self.scenario),
            "scenario_lesson": self.scenario_config.get("primary_lesson", ""),
            "evaluation_mode": self.evaluation_mode,
            "week": self.week,
            "max_weeks": self.max_weeks,
            "phase": self.phase,
            "weeks_in_crisis": self.weeks_in_crisis,
            "manager_energy_current": round(self.manager_state["energy_current"], 1),
            "manager_energy_max": round(self.manager_state["energy_max"], 1),
            "manager_energy_state": self.manager_energy_label(),
            "manager_strain": round(self.manager_state["strain"], 2),
            "manager_visibility_state": self.manager_visibility_label(),
            "weekly_energy_regen": round(self.weekly_energy_regen, 1),
            "founder_pressure": round(self.founder_state["founder_pressure"], 2),
            "founder_clarity": round(self.founder_state["founder_clarity"], 2),
            "founder_relationship": round(self.manager_state["relationship_with_founder"], 2),
            "company_health": self.company_health_label(metrics["avg_strain"]),
            "pressure_state": metrics["pressure_state"],
            "avg_observed_risk": round(metrics["avg_observed_risk"], 2),
            "high_risk_count": metrics["high_risk_count"],
            "critical_warning_signs": metrics["critical_warning_signs"],
            "largest_high_strain_cluster": metrics["largest_high_strain_cluster"],
            "cluster_warning_threshold": metrics["cluster_warning_threshold"],
            "avg_strain_danger_weeks": metrics["avg_strain_danger_weeks"],
            "cluster_danger_weeks": metrics["cluster_danger_weeks"],
            "high_risk_danger_weeks": metrics["high_risk_danger_weeks"],
            "crisis_warning_weeks": metrics["crisis_warning_weeks"],
            "danger_limit": metrics["danger_limit"],
            "cluster_tipping_active": metrics["cluster_tipping_active"],
            "manager_tipping_active": metrics["manager_tipping_active"],
            "founder_tipping_active": metrics["founder_tipping_active"],
            "scenario_outcome_tier": self.scenario_outcome_tier,
            "scenario_outcome_title": self.scenario_outcome_title,
            "great_manager_path_active": bool(self.scenario_state.get("great_manager_path_active", False)),
            "clustered_actions_by_week_3": self.scenario_state.get("clustered_actions_by_week_3", 0),
        }

        if self.debug:
            summary["avg_strain_debug"] = round(metrics["avg_strain"], 2)
            summary["high_fraction_debug"] = round(metrics["high_fraction"], 2)

        return summary

    def get_energy_status(self):
        summary = self.get_summary()
        return {
            "current": summary["manager_energy_current"],
            "max": summary["manager_energy_max"],
        }

    def get_scenario_role_node_id(self, role_name):
        return self.scenario_state.get("scenario_roles", {}).get(role_name)

    def get_scenario_role_name(self, role_name):
        node_id = self.get_scenario_role_node_id(role_name)
        if node_id is None or node_id not in self.G.nodes():
            return None
        return self.G.nodes[node_id]["name"]

    def get_scenario_cluster_node_ids(self):
        role_order = [
            "focal_employee",
            "hidden_strain_employee",
            "spillover_employee",
            "cluster_anchor",
        ]
        return [
            node_id
            for role_name in role_order
            for node_id in [self.get_scenario_role_node_id(role_name)]
            if node_id is not None and node_id in self.G.nodes()
        ]

    def get_scenario_cluster_names(self):
        return [
            self.G.nodes[node_id]["name"]
            for node_id in self.get_scenario_cluster_node_ids()
        ]

    def get_cluster_neighbor_names(self, target_id):
        if target_id is None or target_id not in self.G.nodes():
            return []
        names = [self.G.nodes[n]["name"] for n in self.G.neighbors(target_id)]
        return sorted(names)

    def get_current_week_action_summaries(self):
        rows = []
        for action in self.current_week_actions:
            target = action.get("target")
            rows.append({
                "action_type": action.get("type"),
                "target_name": action.get("target_name") or (target["name"] if target else "Team"),
                "summary": action.get("summary", ""),
                "explanation": action.get("explanation", {}),
            })
        return rows

    def get_event_log(self):
        return self.event_log[:]

    def get_analysis_history(self):
        return self.analysis_history[:]
    
    def tick_active_effects(self):
        """
        Reduce temporary intervention effects each week.
        """
        for n in self.G.nodes():
            for key in [
                "recovery_boost_weeks",
                "spillover_block_weeks",
                "relapse_protection_weeks",
                "visibility_boost_weeks",
                "workload_buffer_weeks",
            ]:
                self.G.nodes[n][key] = max(0, self.G.nodes[n].get(key, 0) - 1)

    def process_delayed_team_effects(self):
        remaining = []
        for effect in self.pending_team_effects:
            if effect.get("apply_week") == self.week:
                if effect.get("type") == "stress_management_workshop":
                    for n in self.managed_node_ids():
                        self.G.nodes[n]["strain"] = max(0.0, self.G.nodes[n]["strain"] - 0.06)
                        self.G.nodes[n]["engagement"] = float(np.clip(self.G.nodes[n]["engagement"] + 0.05, 0, 1))
                        self.G.nodes[n]["trust"] = float(np.clip(self.G.nodes[n]["trust"] + 0.03, 0, 1))
                        self.G.nodes[n]["recovery_boost_weeks"] = max(self.G.nodes[n].get("recovery_boost_weeks", 0), 2)
                    self.event_log.append("The stress management workshop landed this week and eased some pressure across the team.")
            else:
                remaining.append(effect)
        self.pending_team_effects = remaining

    # ========================================================
    # TURN LOOP
    # ========================================================

    def advance_week(self, action=None):
        if action is not None and action.get("type") != "do_nothing":
            self.apply_player_action(action)
        elif not self.current_week_actions:
            self.last_action_summary = "You closed the week without taking a targeted intervention."
        self.end_week()

    def end_week(self):
        if self.game_over:
            return

        self.event_log = self.event_log[:] if self.current_week_actions else []
        self.weekly_event_text = []

        event_text = self.apply_weekly_event()
        self.event_log.append(event_text)

        self.tick_active_effects()
        self.process_delayed_team_effects()
        apply_passive_recovery(self.G, recovery_mult=self.diff["passive_recovery_mult"])

        week_diff = self._current_week_difficulty_profile()
        update_node_states(self.G, difficulty_profile=week_diff)
        generate_behavior_signals(self.G, difficulty_profile=week_diff)
        self._apply_scenario_week_bias()
        update_observed_risk(
            self.G,
            manager_state=self.manager_state,
            founder_state=self.founder_state,
        )

        supported_nodes = [
            n for n in self.G.nodes()
            if self.G.nodes[n].get("recent_support", False)
        ]
        propagate_support(
            self.G,
            supported_nodes,
            strength=0.035 * self.diff["support_propagation_mult"],
        )

        update_edge_weights(self.G)
        update_network_structure(self.G, len(self.G.nodes()))

        self._update_founder_state()
        self._update_relationship_decay()
        self.refresh_metrics()
        self._update_manager_strain()
        self._update_tipping_flags()
        self.refresh_metrics(advance_counters=True)
        phase_changed = self.update_phase()
        self.capture_weekly_consequences()

        if phase_changed:
            self.event_log.append(
                "The organization has entered CRISIS mode. Local strain has become persistently hard to contain."
            )

        self._append_danger_warnings()

        result = self.check_game_over()
        if result is not None:
            self.game_over = True
            self.result = result
            self._evaluate_scenario_outcome()
            self.event_log.append(self.result_text(result))
            self._record_week_snapshot({"type": "end_week", "target": None})
            return

        self._evaluate_scenario_outcome()
        self._record_week_snapshot({"type": "end_week", "target": None})
        self.week += 1
        self._reset_week_flags()
        self._regenerate_manager_energy()

    # ========================================================
    # WEEKLY EVENT LAYER
    # ========================================================

    def apply_weekly_event(self):
        """
        Weekly event layer scaled by difficulty.
        Harder modes:
        - make negative weeks more common
        - make positive weeks rarer and weaker
        - amplify shock impact
        """
        before_budget = self.org_resource
        before_strains = self._strain_array().copy()

        fq = self.founder_quality
        founder_pressure = self.founder_state["founder_pressure"]
        founder_clarity = self.founder_state["founder_clarity"]
        founder_support = self.founder_state["founder_supportiveness"]
        roll = self.rng.rand()

        shock_freq_mult = self.diff["shock_freq_mult"]
        shock_budget_mult = self.diff["shock_budget_mult"]
        shock_strain_mult = self.diff["shock_strain_mult"]
        positive_relief_mult = self.diff["positive_relief_mult"]
        shock_aftereffect_mult = self.diff.get("shock_aftereffect_mult", 1.0)

        negative_cutoff = np.clip(
            (0.28 + 0.12 * founder_pressure - 0.10 * founder_clarity) * shock_freq_mult,
            0.18,
            0.82,
        )
        calm_cutoff = np.clip(
            0.90 - 0.06 * shock_freq_mult + 0.03 * fq + 0.04 * founder_clarity - 0.05 * founder_pressure,
            0.58,
            0.95,
        )

        if roll < negative_cutoff:
            labels = [
                "Founder pressure and delivery risk tightened expectations across the team.",
                "Unexpected customer issues created extra workload.",
                "Cross-team confusion slowed coordination this week.",
                "A key dependency slipped and created knock-on pressure.",
                "Leadership urgency increased uncertainty across the company.",
            ]
            label = self.rng.choice(labels)

            old_budget = self.org_resource
            self.org_resource = apply_shock(
                self.G,
                self.org_resource,
                founder_quality=fq,
            )

            extra_budget_hit = max(0.0, old_budget - self.org_resource) * (shock_budget_mult - 1.0)
            self.org_resource = max(0.0, self.org_resource - extra_budget_hit)

            for n in self.G.nodes():
                extra_strain = (
                    self.rng.uniform(0.006, 0.018)
                    * shock_strain_mult
                    * shock_aftereffect_mult
                )
                if self.cluster_tipping_active:
                    extra_strain *= 1.10
                if self.founder_tipping_active:
                    extra_strain *= 1.12
                vulnerability_factor = 0.75 + 0.50 * self.G.nodes[n]["vulnerability"]
                self.G.nodes[n]["strain"] = float(np.clip(
                    self.G.nodes[n]["strain"] + extra_strain * vulnerability_factor,
                    0,
                    1
                ))
                self.G.nodes[n]["alignment"] = float(np.clip(
                    self.G.nodes[n]["alignment"] - (0.01 + 0.02 * founder_pressure) * (1 - founder_clarity),
                    0,
                    1,
                ))

            self.manager_state["strain"] = float(np.clip(
                self.manager_state["strain"] + 0.02 + 0.03 * founder_pressure,
                0,
                1,
            ))

        elif roll < calm_cutoff:
            label = "Routine week. No major external disruption."

        else:
            positive_events = [
                "Leadership clarified priorities and reduced confusion.",
                "A blocked issue was resolved faster than expected.",
                "The team got brief breathing room this week.",
            ]
            label = self.rng.choice(positive_events)

            for n in self.G.nodes():
                self.G.nodes[n]["strain"] = max(
                    0,
                    self.G.nodes[n]["strain"] - ((0.008 + 0.020 * founder_support) * positive_relief_mult)
                )
                self.G.nodes[n]["engagement"] = float(np.clip(
                    self.G.nodes[n]["engagement"] + (0.01 + 0.02 * founder_support) * positive_relief_mult,
                    0,
                    1,
                ))
                self.G.nodes[n]["trust"] = float(np.clip(
                    self.G.nodes[n]["trust"] + (0.01 + 0.01 * founder_clarity) * positive_relief_mult,
                    0,
                    1,
                ))

            self.org_resource += (0.5 + 0.8 * fq) * positive_relief_mult
            self.manager_state["strain"] = float(np.clip(
                self.manager_state["strain"] - (0.015 + 0.02 * founder_support),
                0,
                1,
            ))

        after_strains = self._strain_array()
        avg_delta = float(np.mean(after_strains - before_strains))
        budget_delta = float(before_budget - self.org_resource)

        detail_parts = []
        if budget_delta > 0.5:
            detail_parts.append(f"Org pressure increased (-{budget_delta:.1f} background resources)")
        elif budget_delta < -0.5:
            detail_parts.append(f"Background conditions improved (+{-budget_delta:.1f})")

        if avg_delta > 0.015:
            detail_parts.append("Team strain rose")
        elif avg_delta < -0.01:
            detail_parts.append("Some pressure eased")

        if detail_parts:
            return f"{label} {'; '.join(detail_parts)}."
        return label

    # ========================================================
    # PLAYER ACTIONS
    # ========================================================

    def apply_player_action(self, action):
        return intervention_engine.apply_player_action(self, action)

    def _record_action_outcome(self, action_type, node, outcome, fit, energy_cost, summary, target_override=None, explanation=None):
        target = target_override
        if target is None and node is not None:
            target = {
                "id": node,
                "name": self.G.nodes[node]["name"],
                "role": self.G.nodes[node]["role"],
            }
        if node is not None:
            history = self.G.nodes[node].get("intervention_history", [])
            history.append({"action": action_type, "outcome": outcome})
            self.G.nodes[node]["intervention_history"] = history[-5:]
            self.G.nodes[node]["last_intervention_success"] = outcome in {"success", "partial"}

        category = action_category(action_type)
        self.run_strategy_counters["total_actions"] += 1
        if category == "targeted":
            self.run_strategy_counters["targeted_actions"] += 1
        elif category == "clustered":
            self.run_strategy_counters["clustered_actions"] += 1
        elif category == "team":
            self.run_strategy_counters["team_actions"] += 1

        focal_id = self.scenario_state.get("scenario_roles", {}).get("focal_employee")
        if category == "targeted" and node is not None and node == focal_id:
            self.run_strategy_counters["focal_targeted_actions"] += 1
        self._update_scenario_progress(action_type, node=node)
        self.run_strategy_profile = self._classify_run_response_style()

        action_record = {
            "type": action_type,
            "target": target,
            "target_name": target.get("name") if target else None,
            "outcome": outcome,
            "fit": round(fit, 2),
            "energy_cost": energy_cost,
            "summary": summary,
            "explanation": explanation or {},
        }
        self.current_week_actions.append(action_record)
        self.manager_state["recent_actions"] = self.current_week_actions[-5:]

    def _classify_weekly_response_style(self):
        if not self.current_week_actions:
            return "no_intervention"

        focal_id = self.scenario_state.get("scenario_roles", {}).get("focal_employee")
        clustered_actions = 0
        targeted_on_focal = 0

        for action in self.current_week_actions:
            category = action_category(action["type"])
            if category == "clustered":
                clustered_actions += 1
            if (
                category == "targeted"
                and focal_id is not None
                and action.get("target", {}).get("id") == focal_id
            ):
                targeted_on_focal += 1

        if clustered_actions > 0:
            return "cluster_stabilising"
        if targeted_on_focal > 0:
            return "targeted_on_focal"
        return "mixed_response"

    def _classify_run_response_style(self):
        counters = self.run_strategy_counters
        if counters["total_actions"] == 0:
            return "no_intervention"
        if counters["clustered_actions"] >= 2 and counters["clustered_actions"] >= counters["focal_targeted_actions"]:
            return "stabilising_response"
        if counters["focal_targeted_actions"] >= 2 and counters["clustered_actions"] == 0:
            return "misread_response"
        return "mixed_response"

    def _update_scenario_progress(self, action_type, node=None):
        scenario_runtime.update_scenario_progress(self, action_type, node=node, action_categories=ACTION_CATEGORIES)

    def _qualifies_for_conflict_cluster_mastery(self):
        return scenario_runtime.qualifies_for_conflict_cluster_mastery(self)

    def _evaluate_scenario_outcome(self):
        scenario_runtime.evaluate_scenario_outcome(self)

    def _build_scenario_story_data(self):
        return scenario_runtime.build_scenario_story_data(self)

    def _shift_relationship(self, node, delta):
        role_gain = self._role_mod(node, "relationship_gain")
        self.G.nodes[node]["manager_relationship"] = float(np.clip(
            self.G.nodes[node]["manager_relationship"] + delta * role_gain,
            0.10,
            0.95,
        ))

    def _role_mod(self, node, key):
        return ROLE_MODIFIERS[self.G.nodes[node].get("role_class", "ic")][key]

    def _current_week_difficulty_profile(self):
        profile = dict(self.diff)
        if self.cluster_tipping_active:
            profile["contagion_mult"] *= 1.18
            profile["workload_strain_mult"] *= 1.15
        if self.manager_tipping_active:
            profile["noise_mult"] *= 1.16
            profile["instability_bias"] += 0.010
        if self.founder_tipping_active:
            profile["behavior_escalation_mult"] *= 1.10
            profile["contagion_mult"] *= 1.08
        return profile

    def _update_founder_state(self):
        metrics = self.last_metrics
        avg_strain = metrics["avg_strain"]
        pressure = self.founder_state["founder_pressure"]
        supportiveness = self.founder_state["founder_supportiveness"]
        clarity = self.founder_state["founder_clarity"]
        founder_rel = self.manager_state["relationship_with_founder"]

        pressure += 0.055 * avg_strain + 0.035 * (metrics["largest_high_strain_cluster"] / max(1, self.team_size))
        pressure += 0.025 * self.manager_state["strain"] - 0.020 * founder_rel
        pressure += self.rng.normal(0, 0.015)
        supportiveness += 0.02 * self.founder_quality - 0.02 * pressure + self.rng.normal(0, 0.01)
        clarity += 0.02 * founder_rel - 0.03 * pressure + self.rng.normal(0, 0.01)
        founder_rel += 0.008 * supportiveness - 0.018 * pressure + self.rng.normal(0, 0.008)

        self.founder_state["founder_pressure"] = float(np.clip(pressure, 0, 1))
        self.founder_state["founder_supportiveness"] = float(np.clip(supportiveness, 0, 1))
        self.founder_state["founder_clarity"] = float(np.clip(clarity, 0, 1))
        self.founder_state["founder_relationship_to_manager"] = float(np.clip(founder_rel, 0, 1))
        self.manager_state["relationship_with_founder"] = self.founder_state["founder_relationship_to_manager"]

        for n in self.G.nodes():
            if self.G.nodes[n].get("role_class") == "founder":
                self.G.nodes[n]["founder_pressure"] = self.founder_state["founder_pressure"]
                self.G.nodes[n]["founder_supportiveness"] = self.founder_state["founder_supportiveness"]
                self.G.nodes[n]["founder_clarity"] = self.founder_state["founder_clarity"]
                self.G.nodes[n]["founder_relationship_to_manager"] = self.founder_state["founder_relationship_to_manager"]

    def _update_relationship_decay(self):
        for n in self.G.nodes():
            if self.G.nodes[n]["strain"] > 0.70 and not self.G.nodes[n].get("recent_support", False):
                self.G.nodes[n]["manager_relationship"] = float(np.clip(
                    self.G.nodes[n]["manager_relationship"] - 0.01,
                    0.10,
                    0.95,
                ))

    def _apply_scenario_week_bias(self):
        scenario_runtime.apply_scenario_week_bias(self)

    def _update_tipping_flags(self):
        metrics = self.last_metrics
        cluster_threshold = max(4, int(np.ceil(0.32 * self.team_size)))
        self.cluster_tipping_active = metrics["largest_high_strain_cluster"] >= cluster_threshold
        self.manager_tipping_active = self.manager_state["overload_weeks"] >= 2
        self.founder_tipping_active = (
            self.founder_state["founder_pressure"] >= 0.72
            and self.manager_state["relationship_with_founder"] <= 0.42
        )

    def _update_manager_strain(self):
        metrics = self.last_metrics
        used_energy_frac = 1.0 - (
            self.manager_state["energy_current"] / max(0.1, self.manager_state["energy_max"])
        )
        successful_actions = sum(
            1 for action in self.current_week_actions
            if action["outcome"] in {"success", "partial"}
        )
        delta = (
            0.11 * metrics["avg_strain"]
            + 0.06 * (metrics["high_risk_count"] / max(1, self.team_size))
            + 0.06 * (metrics["largest_high_strain_cluster"] / max(1, self.team_size))
            + 0.08 * self.founder_state["founder_pressure"]
            + 0.08 * used_energy_frac
            - 0.04 * self.founder_state["founder_supportiveness"]
            - 0.03 * self.manager_state["relationship_with_founder"]
            - 0.015 * min(successful_actions, 2)
        )
        if self.cluster_tipping_active:
            delta += 0.05
        if self.founder_tipping_active:
            delta += 0.05

        self.manager_state["strain"] = float(np.clip(
            self.manager_state["strain"] + delta - 0.025,
            0,
            1,
        ))
        if self.manager_state["strain"] >= 0.68:
            self.manager_state["overload_weeks"] += 1
        else:
            self.manager_state["overload_weeks"] = 0

    def _regenerate_manager_energy(self):
        pressure_state = self.last_metrics.get("pressure_state", "Stable")
        base_regen_map = {
            "Stable": 3.0,
            "Under Pressure": 2.0,
            "Destabilising": 1.0,
            "Critical": 1.0,
        }
        base_regen = base_regen_map.get(pressure_state, 2.0)
        strain = self.manager_state["strain"]
        if strain >= 0.70:
            base_regen -= 2.0
        elif strain >= 0.40:
            base_regen -= 1.0
        if self.manager_tipping_active:
            base_regen -= 0.5
        if self.founder_tipping_active:
            base_regen -= 0.5
        regen = float(np.clip(base_regen, 1.0, 3.0))
        self.weekly_energy_regen = regen
        self.manager_state["energy_current"] = min(
            self.manager_state["energy_max"],
            self.manager_state["energy_current"] + regen,
        )
        self.current_week_actions = []
        self.manager_state["recent_actions"] = []

    def _append_danger_warnings(self):
        metrics = self.last_metrics
        danger_limit = metrics["danger_limit"]

        if self.manager_tipping_active:
            self.event_log.append(
                "Manager overload warning: your own strain is degrading visibility and intervention quality."
            )

        if self.founder_tipping_active:
            self.event_log.append(
                "Founder pressure warning: weak alignment with the founder is amplifying uncertainty."
            )

        if metrics["crisis_warning_weeks"] > 0 and self.phase != "crisis":
            self.event_log.append(
                f"Escalation warning: company-wide strain has been at crisis levels for {metrics['crisis_warning_weeks']} week(s)."
            )

        if metrics["avg_strain_danger_weeks"] > 0:
            self.event_log.append(
                f"Burnout pressure warning: {metrics['avg_strain_danger_weeks']} / {danger_limit} danger weeks."
            )

        if metrics["cluster_danger_weeks"] > 0:
            self.event_log.append(
                f"Cluster instability warning: {metrics['cluster_danger_weeks']} / {danger_limit} danger weeks."
            )

        if metrics["high_risk_danger_weeks"] > 0:
            self.event_log.append(
                f"High-risk saturation warning: {metrics['high_risk_danger_weeks']} / {danger_limit} danger weeks."
            )

    # ========================================================
    # GAME RULES
    # ========================================================

    def update_phase(self, force=False):
        self.refresh_metrics()
        metrics = self.last_metrics

        old_phase = self.phase
        persistence_needed = max(1, self.diff.get("crisis_persistence_weeks", 1))

        if metrics["crisis_warning_weeks"] >= persistence_needed:
            self.phase = "crisis"
        else:
            self.phase = "management"

        if self.phase == "crisis":
            if old_phase == "crisis":
                self.weeks_in_crisis += 1
            else:
                self.weeks_in_crisis = 1
        else:
            self.weeks_in_crisis = 0

        if force:
            return False
        return old_phase != self.phase

    def check_game_over(self):
        self.refresh_metrics()
        metrics = self.last_metrics
        mastery_guarantee_active = self._qualifies_for_conflict_cluster_mastery()
        survive_route_active = scenario_runtime.qualifies_for_conflict_cluster_survive(self)

        avg_strain = metrics["avg_strain"]
        largest_cluster = metrics["largest_high_strain_cluster"]
        high_fraction = metrics["high_fraction"]

        strains = self._strain_array()
        severe_fraction = float(np.mean(strains >= 0.75))

        severe_threshold = self.scale_threshold(0.40)
        avg_threshold = self.scale_threshold(0.72)
        high_fraction_threshold = self.scale_threshold(0.40)

        cluster_size_threshold = max(4, int(np.ceil(self.team_size * self.scale_threshold(0.38))))
        danger_limit = self.diff["danger_limit"]
        crisis_grace_weeks = 1
        in_crisis_grace = self.phase == "crisis" and self.weeks_in_crisis <= crisis_grace_weeks
        catastrophic_severe_threshold = self.scale_threshold(0.55)
        survive_route_catastrophic_threshold = 1.01

        if mastery_guarantee_active:
            if self.week >= self.max_weeks:
                return "kept_job"
            return None

        if self.evaluation_mode == "teaching" and survive_route_active and self.week >= self.max_weeks:
            return "resigned_survived"

        if self.evaluation_mode == "teaching" and survive_route_active and self.week < self.max_weeks:
            if severe_fraction >= survive_route_catastrophic_threshold:
                return "fired_team_breakdown"
            return None

        if severe_fraction >= catastrophic_severe_threshold:
            return "fired_team_breakdown"

        if avg_strain >= avg_threshold and not in_crisis_grace:
            return "fired_burnout_collapse"

        if self.manager_state["strain"] >= 0.97 and self.manager_state["overload_weeks"] >= 4 and not in_crisis_grace:
            return "fired_manager_breakdown"

        if largest_cluster >= cluster_size_threshold and high_fraction >= high_fraction_threshold and not in_crisis_grace:
            return "fired_operational_collapse"

        if severe_fraction >= severe_threshold and not in_crisis_grace:
            return "fired_team_breakdown"

        if (
            self.avg_strain_danger_weeks >= danger_limit
            or self.cluster_danger_weeks >= danger_limit
            or self.high_risk_danger_weeks >= danger_limit
        ) and not in_crisis_grace:
            return "fired_operational_decline"

        if self.week >= self.max_weeks:
            if self.phase == "management":
                return "kept_job"
            return "resigned_survived"

        return None

    def result_text(self, result):
        text = {
            "kept_job": "You kept the company stable enough to finish your contract. You kept your job.",
            "resigned_survived": "The company entered crisis, but you survived until the end of your contract. You resign with your reputation intact.",
            "fired_manager_breakdown": "Your own managerial overload became unsustainable and your judgment collapsed. You were removed from the role.",
            "fired_team_breakdown": "Too much of the team hit severe strain. The company broke down and you were fired.",
            "fired_burnout_collapse": "Average burnout reached catastrophic levels. The company collapsed and you were fired.",
            "fired_operational_collapse": "A persistent stressed cluster triggered operational collapse. You were fired.",
            "fired_operational_decline": "Sustained organizational pressure went unmanaged for too long. The company deteriorated and you were fired.",
        }
        return text.get(result, f"Game ended: {result}")

    # ========================================================
    # METRICS / SUMMARIES
    # ========================================================

    def refresh_metrics(self, advance_counters=False):
        managed_nodes = self.managed_node_ids()
        strains = self._strain_array()
        observed = np.array([self.G.nodes[n].get("observed_risk", 0.0) for n in managed_nodes])
        critical_behaviors = {
            "sick_day",
            "missed_deadline_critical",
            "overload_signal",
            "high_error_rate",
        }

        critical_count = 0
        high_risk_count = 0

        for n in managed_nodes:
            if self.G.nodes[n].get("observed_risk", 0.0) >= 0.65:
                high_risk_count += 1

            recent = self.G.nodes[n].get("recent_behaviors", [])[-3:]
            critical_count += sum(1 for b in recent if b in critical_behaviors)

        avg_strain = float(np.mean(strains))
        largest_cluster = self.compute_largest_high_strain_cluster_size(threshold=0.6)
        high_fraction = float(np.mean(strains > 0.6))

        crisis_avg_threshold = self.diff["crisis_avg_threshold"]
        crisis_cluster_threshold = max(4, int(np.ceil(0.35 * self.team_size)))
        danger_avg_threshold = self.diff["danger_avg_threshold"]
        danger_cluster_threshold = max(4, int(np.ceil(self.diff["danger_cluster_fraction"] * self.team_size)))
        danger_high_fraction_threshold = self.diff["danger_high_fraction_threshold"]

        if advance_counters:
            if avg_strain >= danger_avg_threshold:
                self.avg_strain_danger_weeks += 1
            else:
                self.avg_strain_danger_weeks = 0

            if largest_cluster >= danger_cluster_threshold:
                self.cluster_danger_weeks += 1
            else:
                self.cluster_danger_weeks = 0

            if high_fraction >= danger_high_fraction_threshold:
                self.high_risk_danger_weeks += 1
            else:
                self.high_risk_danger_weeks = 0

            if avg_strain >= crisis_avg_threshold or largest_cluster >= crisis_cluster_threshold:
                self.crisis_warning_weeks += 1
            else:
                self.crisis_warning_weeks = 0

        danger_limit = self.diff["danger_limit"]

        if (
            avg_strain >= self.scale_threshold(0.72)
            or self.avg_strain_danger_weeks >= max(2, danger_limit - 1)
        ):
            pressure_state = "Collapse Imminent"
        elif (
            largest_cluster >= max(5, int(np.ceil(0.40 * self.team_size)))
            or self.cluster_danger_weeks >= max(2, danger_limit - 1)
            or self.high_risk_danger_weeks >= max(2, danger_limit - 1)
        ):
            pressure_state = "Critical"
        elif (
            self.crisis_warning_weeks > 0
            or avg_strain >= (danger_avg_threshold - 0.03)
            or high_fraction >= (danger_high_fraction_threshold - 0.03)
        ):
            pressure_state = "Destabilising"
        elif avg_strain >= 0.48 or critical_count >= 3:
            pressure_state = "Under Pressure"
        else:
            pressure_state = "Stable"

        self.last_metrics = {
            "avg_strain": avg_strain,
            "avg_observed_risk": float(np.mean(observed)),
            "high_risk_count": int(high_risk_count),
            "critical_warning_signs": int(critical_count),
            "largest_high_strain_cluster": largest_cluster,
            "cluster_warning_threshold": danger_cluster_threshold,
            "high_fraction": high_fraction,
            "pressure_state": pressure_state,
            "avg_strain_danger_weeks": self.avg_strain_danger_weeks,
            "cluster_danger_weeks": self.cluster_danger_weeks,
            "high_risk_danger_weeks": self.high_risk_danger_weeks,
            "crisis_warning_weeks": self.crisis_warning_weeks,
            "danger_limit": danger_limit,
            "cluster_tipping_active": bool(self.cluster_tipping_active),
            "manager_tipping_active": bool(self.manager_tipping_active),
            "founder_tipping_active": bool(self.founder_tipping_active),
        }

    def capture_weekly_consequences(self):
        consequence_lines = []

        visible_signals = []
        for n in self.managed_node_ids():
            recent = self.G.nodes[n].get("recent_behaviors", [])[-2:]
            if recent:
                visible_signals.append((self.G.nodes[n]["name"], recent))

        visible_signals = sorted(
            visible_signals,
            key=lambda x: self.G.nodes[self.get_node_by_name(x[0])].get("observed_risk", 0.0),
            reverse=True,
        )

        for name, signals in visible_signals[:4]:
            consequence_lines.append(f"{name} showed warning signs: {', '.join(signals)}.")

        absorbed = []
        for n in self.managed_node_ids():
            amt = self.G.nodes[n].get("absorbed_workload", 0.0)
            if amt > 0.25:
                absorbed.append((self.G.nodes[n]["name"], amt))
                self.G.nodes[n]["last_absorbed_workload"] = amt

        absorbed.sort(key=lambda x: x[1], reverse=True)
        for name, amt in absorbed[:3]:
            consequence_lines.append(f"{name} absorbed extra workload.")

        pressure = self.last_metrics.get("pressure_state", "Stable")
        consequence_lines.append(f"Pressure state: {pressure}.")
        consequence_lines.append(
            f"Manager strain: {self.manager_state['strain']:.2f}. Founder pressure: {self.founder_state['founder_pressure']:.2f}."
        )

        if self.avg_strain_danger_weeks > 0:
            consequence_lines.append(
                f"Average strain has been in the danger zone for {self.avg_strain_danger_weeks} week(s)."
            )

        if self.cluster_danger_weeks > 0:
            consequence_lines.append(
                f"A stressed cluster has remained dangerous for {self.cluster_danger_weeks} week(s)."
            )

        if not consequence_lines:
            consequence_lines.append("No major warning signs were visible this week.")

        self.event_log.extend(consequence_lines)

    def compute_largest_high_strain_cluster_size(self, threshold=0.6):
        high_nodes = [n for n in self.managed_node_ids() if self.G.nodes[n]["strain"] > threshold]
        subgraph = self.G.subgraph(high_nodes)
        if len(subgraph) == 0:
            return 0
        return len(max(nx.connected_components(subgraph), key=len))

    # ========================================================
    # HELPERS
    # ========================================================

    def risk_label(self, value):
        if value < 0.25:
            return "Low"
        if value < 0.50:
            return "Guarded"
        if value < 0.70:
            return "Elevated"
        return "High"

    def engagement_hint(self, value):
        if value >= 0.75:
            return "Strong"
        if value >= 0.55:
            return "Okay"
        if value >= 0.35:
            return "Wobbling"
        return "Low"

    def company_health_label(self, avg_strain):
        if avg_strain < 0.35:
            return "Stable"
        if avg_strain < 0.50:
            return "Under Pressure"
        if avg_strain < 0.65:
            return "Stressed"
        if avg_strain < 0.80:
            return "Critical"
        return "Collapse Risk"

    def manager_visibility_label(self):
        strain = self.manager_state["strain"]
        if strain < 0.30:
            return "Clear"
        if strain < 0.55:
            return "Slightly Degraded"
        if strain < 0.75:
            return "Degraded"
        return "Severely Degraded"

    def manager_energy_label(self):
        energy = self.manager_state["energy_current"]
        if energy >= 8:
            return "Fresh"
        if energy >= 6:
            return "Focused"
        if energy >= 4:
            return "Stretched"
        if energy >= 2:
            return "Drained"
        return "Exhausted"

    def get_node_by_name(self, name):
        for n in self.managed_node_ids():
            if self.G.nodes[n]["name"] == name:
                return n
        return None

    def _strain_array(self):
        return np.array([self.G.nodes[n]["strain"] for n in self.managed_node_ids()], dtype=float)

    def _record_week_snapshot(self, action):
        self.refresh_metrics()
        recommended_actions = scenario_runtime.recommended_actions_for_week(self, self.week)

        employees = []
        managed_nodes = self.managed_node_ids()
        for n in self.managed_node_ids():
            node = self.G.nodes[n]
            true_strain = float(node["strain"])
            observed_risk = float(node.get("observed_risk", 0.0))
            employees.append({
                "id": n,
                "name": node["name"],
                "role": node["role"],
                "true_strain": round(true_strain, 4),
                "observed_risk": round(observed_risk, 4),
                "strain_gap": round(true_strain - observed_risk, 4),
                "risk_label": self.risk_label(observed_risk),
                "recent_behaviors": node.get("recent_behaviors", [])[-5:],
                "recent_support": bool(node.get("recent_support", False)),
                "absorbed_workload": round(self._player_facing_workload_value(node), 4),
                "engagement_hint": self.engagement_hint(node["engagement"]),
                "scenario_role": node.get("scenario_role"),
            })

        employees.sort(key=lambda item: item["observed_risk"], reverse=True)
        network_edges = []
        managed_node_set = set(managed_nodes)
        for left, right in self.G.edges():
            if left in managed_node_set and right in managed_node_set:
                network_edges.append({
                    "source": left,
                    "target": right,
                    "weight": round(float(self.G.edges[left, right].get("weight", 0.0)), 4),
                })
        summary = self.get_summary()
        top_true = max(employees, key=lambda item: item["true_strain"]) if employees else None
        top_observed = max(employees, key=lambda item: item["observed_risk"]) if employees else None

        snapshot_action = self.current_week_actions[-1] if self.current_week_actions else None
        action_type = snapshot_action.get("type", "do_nothing") if snapshot_action else "do_nothing"
        target = None
        if snapshot_action is not None:
            target = snapshot_action.get("target")
        elif action is not None and action.get("target") in self.G.nodes():
            target_node = self.G.nodes[action["target"]]
            target = {
                "id": action["target"],
                "name": target_node["name"],
                "role": target_node["role"],
            }

        snapshot = {
            "scenario": self.scenario,
            "scenario_name": self.scenario_config.get("name", self.scenario),
            "scenario_roles": dict(self.scenario_state.get("scenario_roles", {})),
            "week": self.week,
            "phase": self.phase,
            "result": self.result,
            "game_over": self.game_over,
            "manager_energy_current": round(self.manager_state["energy_current"], 2),
            "manager_energy_max": round(self.manager_state["energy_max"], 2),
            "manager_strain": round(self.manager_state["strain"], 2),
            "founder_pressure": round(self.founder_state["founder_pressure"], 2),
            "summary": dict(summary),
            "event_log": self.get_event_log(),
            "action": {
                "type": action_type,
                "target": target,
                "summary": snapshot_action.get("summary", self.last_action_summary) if snapshot_action else self.last_action_summary,
            },
            "actions_taken": self.current_week_actions[:],
            "recommended_actions": [
                (
                    {
                        "type": action_spec[0],
                        "target_role": action_spec[1],
                        "target_id": self.get_scenario_role_node_id(action_spec[1]),
                        "to_target_role": action_spec[2],
                        "to_target_id": self.get_scenario_role_node_id(action_spec[2]),
                    }
                    if action_spec[0] == "reallocate_workload" and len(action_spec) >= 3
                    else {
                        "type": action_spec[0],
                        "target_role": action_spec[1],
                        "target_id": self.get_scenario_role_node_id(action_spec[1]),
                    }
                )
                for action_spec in recommended_actions
            ],
            "top_true_strain_employee": top_true,
            "top_observed_risk_employee": top_observed,
            "scenario_story_data": self._build_scenario_story_data(),
            "player_diagnosis": self.current_week_diagnosis,
            "run_strategy_profile": self._classify_run_response_style(),
            "scenario_outcome_tier": self.scenario_outcome_tier,
            "scenario_outcome_title": self.scenario_outcome_title,
            "scenario_outcome_explanation": self.scenario_outcome_explanation,
            "scenario_outcome_strength": self.scenario_outcome_strength,
            "scenario_outcome_improvement": self.scenario_outcome_improvement,
            "scenario_mastery_reveal": self.scenario_mastery_reveal,
            "great_manager_path_active": bool(self.scenario_state.get("great_manager_path_active", False)),
            "employees": employees,
            "network_edges": network_edges,
        }
        self.analysis_history.append(snapshot)

    def _mark_supported(self, node, note, success=None):
        self.G.nodes[node]["recent_support"] = True
        self.G.nodes[node]["last_action_note"] = note
        self.G.nodes[node]["support_count"] = self.G.nodes[node].get("support_count", 0) + 1
        self.G.nodes[node]["last_supported_step"] = self.week
        if success is not None:
            self.G.nodes[node]["last_intervention_success"] = success

    def _reset_week_flags(self):
        self.current_week_diagnosis = ""
        for n in self.G.nodes():
            self.G.nodes[n]["recent_support"] = False
            self.G.nodes[n]["last_action_note"] = ""
            self.G.nodes[n]["last_absorbed_workload"] = self.G.nodes[n].get("absorbed_workload", 0.0)
            self.G.nodes[n]["absorbed_workload"] = 0.0


if __name__ == "__main__":
    game = GameState(debug=True)

    print("Game created.")
    print(game.get_summary())
    print()

    print("Visible state:")
    for row in game.get_visible_state()[:5]:
        print(row)

    print("\nAdvancing one week with no action...\n")
    game.advance_week()

    print(game.get_summary())
    for line in game.get_event_log():
        print("-", line)
