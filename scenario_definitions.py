from dataclasses import dataclass, field
from typing import Any

from action_registry import (
    INTENTION_IMPROVE_COORDINATION,
    INTENTION_INVESTIGATE_FURTHER,
    INTENTION_REDISTRIBUTE_WORKLOAD,
    INTENTION_SUPPORT_INDIVIDUAL,
    INTENTION_SUPPORT_TEAM,
    INTENTION_WAIT_AND_OBSERVE,
)


@dataclass
class StrategyPath:
    id: str
    manager_intent: str
    action_pattern: list[str]
    target_level: str
    expected_effect: str
    likely_outcome_tier: str


@dataclass
class OutcomeTier:
    label: str
    conditions: list[str]
    explanation: str
    teaching_message: str
    upgrade_message: str


@dataclass
class ScenarioUIConfig:
    briefing_narrative_template: str
    key_signals: list[str]
    evidence_modules: list[str]
    reflection_prompts: list[str]
    action_groups: dict[str, list[str]]
    weekly_feedback_focus: list[str]
    diagnosis_type: str
    strategy_metrics: list[str]
    comparison_logic: str
    tone: str = "coaching"


@dataclass
class ScenarioDefinition:
    id: str
    name: str
    label: str
    teaching_pattern: str
    description: str
    primary_lesson: str
    secondary_lessons: list[str]
    team_size: int
    length: int
    surface_story: dict[str, Any]
    hidden_pattern: dict[str, Any]
    strategy_paths: dict[str, StrategyPath]
    mastery_rule: dict[str, Any]
    outcome_tiers: dict[str, OutcomeTier]
    benchmark_paths: dict[str, dict[str, str]]
    reflection_rules: dict[str, Any]
    modular_hooks: dict[str, Any]
    ui_config: ScenarioUIConfig | None = None
    ui_schema: dict[str, Any] = field(default_factory=dict)
    evaluation_modes: dict[str, Any] = field(default_factory=dict)
    default_evaluation_mode: str = "teaching"
    runtime_preset: dict[str, Any] = field(default_factory=dict)


BASELINE = ScenarioDefinition(
    id="Baseline",
    name="Open Play",
    label="Open Play",
    teaching_pattern="open_play",
    description="Manage the team in an open simulation without a pre-authored pressure pattern.",
    primary_lesson="Read imperfect signals and use your limited management energy carefully.",
    secondary_lessons=[],
    team_size=15,
    length=52,
    surface_story={
        "summary": "The team is carrying mixed low-level pressure."
    },
    hidden_pattern={
        "pattern_type": "open_play",
        "summary": "There is no single authored pattern. You are responding to whatever emerges."
    },
    strategy_paths={},
    mastery_rule={
        "description": ""
    },
    outcome_tiers={},
    benchmark_paths={},
    reflection_rules={
        "weekly_focus": ["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        "end_reveal": {},
    },
    modular_hooks={
        "required_patterns": [],
        "required_action_types": [],
        "optional_layers": [],
    },
    ui_config=ScenarioUIConfig(
        briefing_narrative_template="The team is carrying mixed low-level pressure. Watch for where visible signals and underlying strain start to diverge.",
        key_signals=[
            "No single authored pattern is driving events.",
            "Observed risk is your clearest live signal.",
            "Use limited energy carefully and keep updating your read.",
        ],
        evidence_modules=["employee_table"],
        reflection_prompts=[
            "What stands out to you this week?",
            "Where would you focus your attention right now?",
        ],
        action_groups={
            INTENTION_SUPPORT_INDIVIDUAL: ["quick_check_in", "offer_coaching_support"],
            INTENTION_INVESTIGATE_FURTHER: ["check_in_on_load_bearing_risk", "surface_hidden_support_work"],
            INTENTION_REDISTRIBUTE_WORKLOAD: ["reduce_workload", "reallocate_workload"],
            INTENTION_SUPPORT_TEAM: ["team_meeting", "stress_management_workshop"],
            INTENTION_IMPROVE_COORDINATION: ["group_mediation", "clarify_roles_and_handoffs"],
            INTENTION_WAIT_AND_OBSERVE: ["do_nothing"],
        },
        weekly_feedback_focus=["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        diagnosis_type="open_play",
        strategy_metrics=["targeted_vs_clustered_actions", "timing_of_actions", "distribution_of_effort"],
        comparison_logic="Compare the player's evolving read with the mixed, non-authored pressure pattern.",
    ),
    ui_schema={
        "primary_signal_label": "Observed Risk",
        "secondary_signal_label": "Team Pressure",
        "hidden_signal_label": "Underlying Risk",
        "primary_signal_description": "Visible warning signs are your main live signal.",
        "hidden_signal_description": "No single authored hidden pattern is driving the case.",
        "reveal_mode": "generic_review",
        "teaching_misread": "Open play does not emphasize one specific misread.",
    },
    evaluation_modes={
        "teaching": {
            "allow_acceptable_route_support": True,
            "allow_success_guarantee": True,
            "outcome_labels": ["Fail", "Survive", "Succeed"],
            "feedback_style": "coaching",
        },
        "simulation": {
            "allow_acceptable_route_support": False,
            "allow_success_guarantee": False,
            "outcome_labels": ["Escalating", "Contained", "Stabilised", "Collapsed"],
            "feedback_style": "analytical",
        },
    },
    default_evaluation_mode="simulation",
)


CONFLICT_CLUSTER = ScenarioDefinition(
    id="scenario_01",
    name="Product Launch Crunch",
    label="Product Launch Crunch",
    teaching_pattern="cluster_instability",
    description="One visibly overloaded employee draws attention, but the real risk is a fragile local delivery cluster.",
    primary_lesson="Visible distress may be the symptom, not the root cause.",
    secondary_lessons=[
        "Clustered responses can outperform targeted-only responses.",
        "Reasonable management can still miss the deeper pattern.",
    ],
    team_size=15,
    length=6,
    surface_story={
        "focal_employee": "Jordan",
        "focal_role": "Product Manager",
        "visible_signals": ["complaint", "overload_signal", "sick_day"],
        "likely_manager_interpretation": "Jordan is overloaded and needs direct support.",
        "summary": "A visibly overloaded employee looks like the immediate problem.",
    },
    hidden_pattern={
        "pattern_type": "cluster_instability",
        "hidden_risk_location": ["Jordan", "Sam", "Priya", "Chloe"],
        "system_driver": "Poor handoffs, local coordination friction, and workload redistribution.",
        "observability_distortion": "Jordan is highly visible; Sam carries quieter hidden strain.",
        "summary": "The real risk sits in a strained local cluster with poor handoffs and shifting workload.",
    },
    strategy_paths={
        "wrong_but_plausible": StrategyPath(
            id="targeted_relief_path",
            manager_intent="Help the visibly distressed individual.",
            action_pattern=["quick_check_in", "offer_coaching_support"],
            target_level="individual",
            expected_effect="Reduces visible distress but misses cluster spread.",
            likely_outcome_tier="Survive or Fail",
        ),
        "acceptable": StrategyPath(
            id="individual_support_path",
            manager_intent="Support the obvious person well enough to reduce harm.",
            action_pattern=["quick_check_in", "offer_coaching_support", "occasional_group_mediation"],
            target_level="mostly_individual",
            expected_effect="Contains some damage and often reaches the end, but does not fully solve the pattern.",
            likely_outcome_tier="Survive",
        ),
        "great": StrategyPath(
            id="cluster_stabilisation_path",
            manager_intent="Stabilize the local pattern early.",
            action_pattern=["group_mediation", "clarify_roles_and_handoffs"],
            target_level="cluster",
            expected_effect="Interrupts spread and stabilizes the local system.",
            likely_outcome_tier="Succeed",
        ),
    },
    mastery_rule={
        "description": "Use at least two cluster-level interventions on the focal cluster by the end of week 3.",
        "all": [
            {"type": "counter", "counter": "clustered_actions_by_week_3", "op": ">=", "value": 2},
            {"type": "counter", "counter": "clustered_actions_on_core_targets_by_week_3", "op": ">=", "value": 2},
        ],
    },
    outcome_tiers={
        "fail": OutcomeTier(
            label="Fail",
            conditions=["collapse_before_end"],
            explanation="The visible strain was real, but the underlying cluster hardened faster than your response contained it.",
            teaching_message="You acted too little or at the wrong level.",
            upgrade_message="Intervene at the cluster level earlier.",
        ),
        "acceptable": OutcomeTier(
            label="Survive",
            conditions=["survive_to_end", "not_mastery_path"],
            explanation="You reduced harm and got through the scenario, but did not fully solve the deeper cluster pattern.",
            teaching_message="You made a reasonable management response.",
            upgrade_message="To be great, diagnose the cluster earlier and commit to clustered actions sooner.",
        ),
        "success": OutcomeTier(
            label="Succeed",
            conditions=["survive_to_end", "mastery_rule_met"],
            explanation="You identified the real level of the problem early and stabilized it with the strongest response.",
            teaching_message="You treated the focal employee as the signal, not the whole story.",
            upgrade_message="This is the strongest response this scenario was designed to teach.",
        ),
    },
    benchmark_paths={
        "no_intervention": {
            "summary": "Visible overload remained unresolved while strain spread through the surrounding cluster.",
            "teaching_takeaway": "Ignoring the focal point allows the cluster to harden.",
        },
        "misread_response": {
            "summary": "Direct support eased some surface pressure, but the underlying cluster became more fragile as pressure shifted outward.",
            "teaching_takeaway": "Helping the obvious person is reasonable, but not always sufficient.",
        },
        "stabilising_response": {
            "summary": "The most effective response treated the issue as a local cluster problem, reducing strain spread and stabilizing the surrounding team.",
            "teaching_takeaway": "Early clustered intervention solves the right level of the problem.",
        },
        "mixed_response": {
            "summary": "A mixed response changed parts of the pattern, but left ambiguity about whether the underlying cluster was truly stabilised.",
            "teaching_takeaway": "Partial reads can reduce harm without fully solving the pattern.",
        },
    },
    reflection_rules={
        "weekly_focus": ["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        "end_reveal": {
            "show_outcome_tier": True,
            "show_mastery_rule_after_run": True,
            "compare_to_benchmarks": True,
        },
    },
    modular_hooks={
        "required_patterns": ["cluster_instability", "visible_focal_employee", "hidden_quieter_risk"],
        "required_action_types": ["targeted", "clustered"],
        "optional_layers": ["relationship_visibility", "founder_pressure"],
    },
    ui_config=ScenarioUIConfig(
        briefing_narrative_template="We’ve got a product launch starting to slip, and the pressure around it is getting harder to contain. Timelines are moving, priorities keep changing, and Jordan has become the person trying to hold everything together across the team. He’s been complaining about workload, already took a sick day, and sounds close to burnout in meetings. Jordan is where the pressure is most obvious right now, but I’m not sure the pattern starts and ends with him.",
        key_signals=[
            "Jordan is the clearest visible problem.",
            "Complaints and overload signals are concentrated in one delivery pocket.",
            "Quieter strain may be sitting near the focal employee rather than in Jordan alone.",
        ],
        evidence_modules=["employee_table", "network_graph"],
        reflection_prompts=[
            "What stands out to you this week?",
            "Where would you focus your attention?",
            "What feels most important right now?",
        ],
        action_groups={
            INTENTION_SUPPORT_INDIVIDUAL: ["quick_check_in", "offer_coaching_support"],
            INTENTION_INVESTIGATE_FURTHER: ["check_in_on_load_bearing_risk", "surface_hidden_support_work"],
            INTENTION_REDISTRIBUTE_WORKLOAD: ["reduce_workload", "reallocate_workload"],
            INTENTION_SUPPORT_TEAM: ["team_meeting", "stress_management_workshop"],
            INTENTION_IMPROVE_COORDINATION: ["group_mediation", "clarify_roles_and_handoffs"],
            INTENTION_WAIT_AND_OBSERVE: ["do_nothing"],
        },
        weekly_feedback_focus=["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        diagnosis_type="cluster_instability",
        strategy_metrics=["targeted_vs_clustered_actions", "timing_of_actions", "distribution_of_effort"],
        comparison_logic="Compare an individual-overload diagnosis against the authored cluster-instability pattern.",
    ),
    ui_schema={
        "primary_signal_label": "Observed Risk",
        "secondary_signal_label": "Visible Focal Strain",
        "hidden_signal_label": "Cluster Instability",
        "primary_signal_description": "The focal employee's visible warning signs should feel like the clearest live signal.",
        "hidden_signal_description": "The real teaching risk sits in the surrounding local cluster, not only the focal person.",
        "reveal_mode": "scenario_specific",
        "teaching_misread": "The player is meant to over-trust visible individual overload and under-read the local cluster pattern.",
        "play_ui": {
            "lead_prompt": "Respond to the clearest visible issue, but keep asking whether the problem is larger than one person.",
            "status_labels": {
                "failing": "Escalating",
                "acceptable": "Contained",
                "mastery": "Stabilising",
            },
        },
    },
    evaluation_modes={
        "teaching": {
            "allow_acceptable_route_support": True,
            "allow_success_guarantee": True,
            "outcome_labels": ["Fail", "Survive", "Succeed"],
            "feedback_style": "coaching",
        },
        "simulation": {
            "allow_acceptable_route_support": False,
            "allow_success_guarantee": False,
            "outcome_labels": ["Escalating", "Contained", "Stabilised", "Collapsed"],
            "feedback_style": "analytical",
        },
    },
    default_evaluation_mode="teaching",
    runtime_preset={
        "role_assignments": {
            "focal_employee": "Jordan",
            "hidden_strain_employee": "Sam",
            "spillover_employee": "Priya",
            "cluster_anchor": "Chloe",
        },
        "scenario_state_defaults": {
            "clustered_action_weeks": [],
            "clustered_actions_by_week_3": 0,
            "clustered_actions_on_core_targets_by_week_3": 0,
            "targeted_on_focal_by_week_2": 0,
        },
        "node_overrides": {
            "focal_employee": {
                "strain": 0.54,
                "manager_relationship": 0.68,
                "manager_contact_frequency": 0.78,
                "recent_behaviors": ["complaint", "overload_signal", "sick_day"],
                "scenario_visibility_bias": 0.10,
                "scenario_spillover_bias": 0.04,
            },
            "hidden_strain_employee": {
                "strain": 0.66,
                "manager_relationship": 0.42,
                "manager_contact_frequency": 0.45,
                "recent_behaviors": ["ignored_email", "engagement_drop"],
                "scenario_visibility_bias": -0.08,
                "scenario_spillover_bias": 0.06,
            },
            "spillover_employee": {
                "strain": 0.44,
                "manager_relationship": 0.56,
                "manager_contact_frequency": 0.60,
                "recent_behaviors": [],
                "scenario_visibility_bias": -0.02,
                "scenario_spillover_bias": 0.08,
                "absorbed_workload": 0.45,
                "last_absorbed_workload": 0.45,
            },
            "cluster_anchor": {
                "strain": 0.46,
                "manager_relationship": 0.58,
                "manager_contact_frequency": 0.66,
                "recent_behaviors": ["ignored_email"],
                "scenario_visibility_bias": 0.00,
                "scenario_spillover_bias": 0.05,
            },
        },
        "forced_edges": [
            {"left_role": "focal_employee", "right_role": "hidden_strain_employee", "weight_range": [0.32, 0.48]},
            {"left_role": "focal_employee", "right_role": "spillover_employee", "weight_range": [0.32, 0.48]},
            {"left_role": "focal_employee", "right_role": "cluster_anchor", "weight_range": [0.32, 0.48]},
            {"left_role": "cluster_anchor", "right_role": "hidden_strain_employee", "weight_range": [0.32, 0.48]},
            {"left_role": "cluster_anchor", "right_role": "spillover_employee", "weight_range": [0.32, 0.48]},
        ],
        "cluster_node_adjustments": {
            "trust": -0.08,
            "alignment": -0.10,
        },
        "manager_state_adjustments": {
            "strain": 0.01,
        },
        "founder_state_adjustments": {
            "founder_pressure": 0.02,
            "founder_clarity": -0.01,
        },
        "action_progress_rules": [
            {
                "category": "targeted",
                "target_role": "focal_employee",
                "week_lte": 2,
                "increments": {"targeted_on_focal_by_week_2": 1},
            },
            {
                "category": "clustered",
                "week_lte": 3,
                "append_week_to": "clustered_action_weeks",
                "increments": {"clustered_actions_by_week_3": 1},
            },
            {
                "category": "clustered",
                "week_lte": 3,
                "node_in_roles": ["focal_employee", "hidden_strain_employee", "spillover_employee", "cluster_anchor"],
                "increments": {"clustered_actions_on_core_targets_by_week_3": 1},
            },
        ],
        "action_quality_by_week": {
            1: [
                {"action_types": ["group_mediation"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support"], "target_role": "focal_employee", "quality": "acceptable"},
                {"action_types": ["check_in_on_load_bearing_risk", "surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["reduce_workload", "do_nothing"], "quality": "weak"},
            ],
            2: [
                {"action_types": ["clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["group_mediation"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support"], "target_role": "focal_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "check_in_on_load_bearing_risk", "surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["reduce_workload", "do_nothing"], "quality": "weak"},
            ],
            3: [
                {"action_types": ["group_mediation", "clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "check_in_on_load_bearing_risk", "surface_hidden_support_work", "reduce_workload"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support"], "target_role": "focal_employee", "quality": "acceptable"},
                {"action_types": ["reduce_workload", "do_nothing"], "quality": "weak"},
            ],
            4: [
                {"action_types": ["group_mediation", "clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "check_in_on_load_bearing_risk", "surface_hidden_support_work", "reduce_workload"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            5: [
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload", "group_mediation", "clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["check_in_on_load_bearing_risk", "surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            6: [
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload", "group_mediation", "clarify_roles_and_handoffs"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "check_in_on_load_bearing_risk", "surface_hidden_support_work", "reduce_workload"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
        },
        "route_rules": {
            "mastery": {
                "all": [
                    {"type": "counter", "counter": "clustered_actions_by_week_3", "op": ">=", "value": 2},
                    {"type": "counter", "counter": "clustered_actions_on_core_targets_by_week_3", "op": ">=", "value": 2},
                ],
            },
            "acceptable": {
                "all": [
                    {"type": "counter", "counter": "targeted_on_focal_by_week_2", "op": ">=", "value": 1},
                ],
                "none": [
                    {"type": "route_active", "route": "mastery"},
                ],
            },
        },
        "outcome_evaluation_order": ["fail", "success", "acceptable"],
        "outcome_rules": {
            "fail": {
                "all": [
                    {"type": "not", "rule": {"type": "survived_to_end"}},
                ],
            },
            "success": {
                "all": [
                    {"type": "survived_to_end"},
                    {"type": "route_active", "route": "mastery"},
                ],
            },
            "acceptable": {
                "all": [
                    {"type": "survived_to_end"},
                ],
            },
        },
        "recommended_actions_by_week": {
            1: [("group_mediation", "focal_employee"), ("quick_check_in", "hidden_strain_employee")],
            2: [("clarify_roles_and_handoffs", "focal_employee")],
            3: [("group_mediation", "focal_employee"), ("quick_check_in", "hidden_strain_employee")],
            4: [("clarify_roles_and_handoffs", "focal_employee"), ("quick_check_in", "hidden_strain_employee")],
            5: [("quick_check_in", "hidden_strain_employee")],
            6: [("clarify_roles_and_handoffs", "focal_employee"), ("quick_check_in", "hidden_strain_employee")],
        },
        "recommended_analysis_openers": {
            1: "Early on, it was reasonable to focus on Jordan because that was where the pressure was easiest to see.",
            2: "By this stage, the task was becoming less about Jordan in isolation and more about whether the surrounding group was steady enough to absorb the launch pressure.",
            3: "By week three, the pattern should have been clearer.",
            4: "At this stage, the question was no longer whether there was pressure around Jordan.",
            5: "By this point, a stronger manager would be watching not just Jordan, but the quieter strain building around the visible problem.",
            6: "By the end of the run, the quality of the response came down to whether you had treated this as one struggling person or as a local team pattern that needed stabilising.",
        },
        "recommended_week_tactics": {
            1: "Resolve Working Tensions around {focal}, alongside a Quick Check-In with {hidden}",
            2: "Clarify Roles And Handoffs around {focal}",
            3: "Resolve Working Tensions around {focal}, alongside a Quick Check-In with {hidden}",
            4: "Clarify Roles And Handoffs around {focal}, alongside a Quick Check-In with {hidden}",
            5: "Quick Check-In with {hidden}",
            6: "Clarify Roles And Handoffs around {focal}, alongside a Quick Check-In with {hidden}",
        },
        "recommended_analysis_copy": {
            "opening": (
                "At the outset, {focal} looked like the problem. The more important question was whether the strain was actually sitting with {focal} alone or already starting to spread through the people closest to them. "
                "Stress propagates through the connections around it, so the goal was not just to extinguish the visible flames, but to stop the spread before it gathered momentum. "
                "By looking at the pocket around {focal}, {hidden}, {spillover}, and {anchor}, you could see that the noise around {focal} was part of a deeper local pattern rather than a single-person issue."
            ),
            "corrective": {
                1: (
                    "By staying too tightly with the most visible pressure point, you left the wider stability of the group less tested than it needed to be. "
                    "{week_tactics_sentence}. That would have supported {focal} while also stepping into the strain already forming around them. "
                    "That was the stronger early read of the situation."
                ),
                2: (
                    "The task was becoming less about {focal} in isolation and more about whether the surrounding group was steady enough to absorb the launch pressure. "
                    "{week_tactics_sentence}. That would have kept {focal} in view while starting to stabilise the local pattern around them. "
                    "What mattered here was shifting the level of response, not simply offering more of the same support."
                ),
                3: (
                    "{focal} was still the visible issue, but the larger risk was whether the surrounding pocket was beginning to fray around them. "
                    "{week_tactics_sentence}. That would have helped prevent the pressure from simply moving from the loudest person to the less visible one."
                ),
                4: (
                    "The stronger management read was whether you were acting at the level of the group rather than staying with the most visible individual. "
                    "{week_tactics_sentence}. That would have helped stop the problem from shifting out of sight rather than truly settling."
                ),
                5: (
                    "A stronger manager would be watching not just {focal}, but the quieter strain building around the visible problem. "
                    "{week_tactics_sentence}. That would have helped hold the cluster steady while bringing down the quieter risk that had emerged within it. "
                    "The key question here was whether the surrounding pattern was genuinely cooling."
                ),
                6: (
                    "The quality of the response came down to whether you had treated this as one struggling person or as a local team pattern that needed stabilising. "
                    "{week_tactics_sentence}. That would have helped keep the cluster from reigniting while finishing the recovery work. "
                    "The goal here was not just a calmer {focal}, but a more stable local system overall."
                ),
            },
            "reinforcing": {
                1: (
                    "You were starting to read this at the right level rather than treating {focal} as the whole problem. "
                    "{week_tactics_sentence}. That supported the most visible pressure point while also stepping into the strain already forming around them. "
                    "That was the stronger early read of the situation."
                ),
                2: (
                    "You were beginning to move beyond {focal} in isolation and look at whether the surrounding group was steady enough to absorb the launch pressure. "
                    "{week_tactics_sentence}. That kept {focal} in view while starting to stabilise the local pattern around them. "
                    "What mattered was that you were shifting the level of response at the right time."
                ),
                3: (
                    "{focal} was still the visible issue, but you were also treating the surrounding pocket as the larger management risk. "
                    "{week_tactics_sentence}. That helped prevent the pressure from simply moving from the loudest person to the less visible one."
                ),
                4: (
                    "You were no longer acting as though the issue sat with {focal} alone. "
                    "{week_tactics_sentence}. That kept the local system steadier while checking whether quieter strain was still building nearby. "
                    "That was the right level of response by this point."
                ),
                5: (
                    "You were watching not just {focal}, but the quieter strain building around the visible problem. "
                    "{week_tactics_sentence}. That helped hold the cluster steady while bringing down the quieter risk that had emerged within it. "
                    "The important thing here was that you were reading the surrounding pattern, not just the loudest signal."
                ),
                6: (
                    "You were treating this as a local team pattern rather than one struggling person. "
                    "{week_tactics_sentence}. That helped keep the cluster from reigniting while finishing the recovery work. "
                    "The result was not just a calmer {focal}, but a more stable local system overall."
                ),
            },
        },
        "outcome_copy": {
            "fail": {
                "title": "The situation spiralled.",
                "strength": "You did something a good manager might plausibly do: you responded to visible strain rather than ignoring it.",
                "improvement": "Intervene at the cluster level earlier.",
            },
            "acceptable": {
                "title": "You managed the situation.",
                "strength": "You acted on a real problem and responded in a humane, sensible way.",
                "improvement": "To solve the real problem, you needed to move from supporting the visible individual to stabilising the cluster earlier.",
            },
            "success": {
                "title": "You managed the situation.",
                "strength": "You diagnosed the local pattern early and stayed at the right intervention level.",
                "improvement": "This is the strongest response this scenario was designed to teach.",
            },
        },
    },
)


QUIET_HIGH_PERFORMER = ScenarioDefinition(
    id="scenario_02",
    name="Client Demo Spillover",
    label="Client Demo Spillover",
    teaching_pattern="quiet_load_bearing",
    description="Ahead of a high-stakes client demo, one employee's visible disengagement pulls attention to the surface while the team becomes more fragile by carrying pressure in different, misaligned ways.",
    primary_lesson="High load can look stronger than it is. Visible disengagement is not always apathy, and a team that still looks functional may already be relying on fragile coping patterns.",
    secondary_lessons=[
        "Stress grows when managers and employees adapt privately instead of restoring alignment together.",
        "Good management means reading hidden strain and team fragility early rather than over-trusting what still appears to be holding.",
    ],
    team_size=15,
    length=6,
    surface_story={
        "focal_employee": "Riley",
        "focal_role": "Designer",
        "visible_signals": ["missed_deadline_minor", "complaint"],
        "likely_manager_interpretation": "Riley is the main issue, and the fastest route is to steady the visible problem so the demo stays on track.",
        "summary": "A visible delivery wobble makes Riley look like the problem, while the deeper risk is that the team is keeping the work moving through quiet coping rather than realigning how the pressure is being carried.",
    },
    hidden_pattern={
        "pattern_type": "quiet_load_bearing",
        "hidden_risk_location": ["Maya", "Riley", "Jordan", "Sam"],
        "system_driver": "Visible strain in one person and suppressed carrying in another allow the team to keep functioning without ever truly realigning how the work, stress, and responsibility are being carried.",
        "observability_distortion": "Riley is highly visible and easy to misread as not caring; Maya looks steady because she keeps catching problems before they become visible to everyone else.",
        "summary": "The team is staying afloat by letting one person's strain show up loudly while another person quietly absorbs the fallout, which makes a fragile system look stronger and more settled than it really is.",
    },
    strategy_paths={
        "wrong_but_plausible": StrategyPath(
            id="surface_performance_path",
            manager_intent="Protect the demo by steadying Riley at the surface while the rest of the team quietly compensates around them.",
            action_pattern=["quick_check_in", "offer_coaching_support", "reduce_workload"],
            target_level="visible_problem_only",
            expected_effect="Makes the visible issue feel more managed while leaving the hidden carrying and team fragility pattern largely intact.",
            likely_outcome_tier="Survive or Fail",
        ),
        "acceptable": StrategyPath(
            id="late_hidden_support_path",
            manager_intent="Support Riley early, then begin to notice that the team is carrying the pressure in a more fragile and misaligned way than it first appeared.",
            action_pattern=["quick_check_in", "check_in_on_load_bearing_risk", "reduce_workload", "clarify_roles_and_handoffs"],
            target_level="individual_then_alignment",
            expected_effect="Reduces harm and starts to widen the read, but leaves the team privately adapting for too long before the underlying pattern is properly addressed.",
            likely_outcome_tier="Survive",
        ),
        "great": StrategyPath(
            id="dependency_reduction_path",
            manager_intent="Treat visible disengagement and quiet carrying as connected signals, then act early enough to bring the team back into alignment before coping hardens into fragility.",
            action_pattern=["surface_hidden_support_work", "reduce_workload", "reallocate_workload", "clarify_roles_and_handoffs", "group_mediation"],
            target_level="misalignment_pattern",
            expected_effect="Reduces hidden carrying, stops over-reading the visible symptom, and gives the team room to recover without privately consuming one another's capacity.",
            likely_outcome_tier="Succeed",
        ),
    },
    mastery_rule={
        "description": "By the end of week 4, investigate Maya's hidden carrying early, take meaningful load off her, make the hidden support pattern visible, and continue giving Riley direct individual support as the visible issue.",
        "all": [
            {"type": "counter", "counter": "investigated_hidden_by_week_2", "op": ">=", "value": 1},
            {"type": "counter", "counter": "load_relief_on_hidden_by_week_4", "op": ">=", "value": 1},
            {"type": "counter", "counter": "targeted_on_hidden_by_week_4", "op": ">=", "value": 2},
            {"type": "counter", "counter": "focal_support_by_week_2", "op": ">=", "value": 1},
        ],
    },
    outcome_tiers={
        "fail": OutcomeTier(
            label="Fail",
            conditions=["collapse_before_end"],
            explanation="The visible wobble was manageable, but the team stayed out of alignment for too long. Riley's strain kept showing up loudly while too much of the real cost stayed hidden elsewhere, leaving the team more fragile than it looked.",
            teaching_message="You never got hold of how the pressure was actually being carried across the team.",
            upgrade_message="Notice the hidden carrying earlier and act before fragile coping becomes the system.",
        ),
        "acceptable": OutcomeTier(
            label="Survive",
            conditions=["survive_to_end", "not_mastery_path"],
            explanation="You moved beyond the first surface read and reduced some harm, but the team still spent too long surviving through misalignment rather than restoring alignment cleanly.",
            teaching_message="You found part of the real issue and improved the situation meaningfully.",
            upgrade_message="To be stronger, read the hidden strain sooner and intervene before fragile coping patterns become normal.",
        ),
        "success": OutcomeTier(
            label="Succeed",
            conditions=["survive_to_end", "mastery_rule_met"],
            explanation="You recognized that visible disengagement and hidden carrying were part of the same pattern and intervened early enough to bring the team back toward alignment before the system hardened around coping.",
            teaching_message="You treated surface behavior as a signal, not the whole story, and acted on where the real cost was landing.",
            upgrade_message="This is the strongest response this scenario was designed to teach.",
        ),
    },
    benchmark_paths={
        "no_intervention": {
            "summary": "The visible wobble continued while more of the hidden cost kept moving elsewhere in the team, leaving the group increasingly fragile even where it still looked functional.",
            "teaching_takeaway": "If no one interrupts misalignment, the team starts surviving by privately absorbing strain until fragility looks like normal delivery.",
        },
        "misread_response": {
            "summary": "Supporting Riley helped at the surface, but the team still solved around the pressure by quietly asking too much of the people carrying the fallout.",
            "teaching_takeaway": "Reasonable support can still miss how the team is privately adapting to pressure and becoming more fragile in the process.",
        },
        "stabilising_response": {
            "summary": "The strongest response widened the read early, reduced hidden carrying, and stopped the week being held together by private rescue work.",
            "teaching_takeaway": "The right move is to bring the team back into alignment before fragile coping becomes normal.",
        },
        "mixed_response": {
            "summary": "Parts of the problem improved, but the team still spent too long carrying pressure in different, only partly visible ways.",
            "teaching_takeaway": "Partial insight can reduce harm without fully restoring alignment.",
        },
    },
    reflection_rules={
        "weekly_focus": ["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        "end_reveal": {
            "show_outcome_tier": True,
            "show_mastery_rule_after_run": True,
            "compare_to_benchmarks": True,
        },
    },
    modular_hooks={
        "required_patterns": ["visible_surface_story", "hidden_load_bearing_employee", "dependency_risk"],
        "required_action_types": ["targeted", "clustered"],
        "optional_layers": ["relationship_visibility", "succession_fragility"],
    },
    ui_config=ScenarioUIConfig(
        briefing_narrative_template="We’ve got a client demo coming up, and the team is starting to feel less settled than it should this early. Riley’s work has been arriving unevenly, a few details have had to be reworked, and some frustration is building around avoidable cleanup. We’re still getting the week over the line, which is the reassuring part. The less reassuring part is that some of the clarification and rescue work seems to keep landing elsewhere in the team. Riley is drawing most of the attention right now, but I’m not convinced the pressure starts and ends there.",
        key_signals=[
            "Riley is the clearest visible source of friction.",
            "Visible disengagement does not necessarily tell you what the team is really struggling with.",
            "The work may still be landing because other people are quietly adapting around the strain.",
        ],
        evidence_modules=["employee_table", "network_graph"],
        reflection_prompts=[
            "What is the most plausible first read here?",
            "Who is making this look more stable than it really is?",
            "What would reduce dependency here, not just relieve this week's friction?",
        ],
        action_groups={
            INTENTION_SUPPORT_INDIVIDUAL: ["quick_check_in", "offer_coaching_support"],
            INTENTION_INVESTIGATE_FURTHER: ["check_in_on_load_bearing_risk", "surface_hidden_support_work"],
            INTENTION_REDISTRIBUTE_WORKLOAD: ["reduce_workload", "reallocate_workload"],
            INTENTION_IMPROVE_COORDINATION: ["group_mediation", "clarify_roles_and_handoffs"],
            INTENTION_SUPPORT_TEAM: ["team_meeting", "stress_management_workshop"],
            INTENTION_WAIT_AND_OBSERVE: ["do_nothing"],
        },
        weekly_feedback_focus=["what_you_chose", "how_it_landed", "what_shifted", "what_to_watch"],
        diagnosis_type="quiet_load_bearing",
        strategy_metrics=["who_you_supported", "whether_you_reduced_dependency", "timing_of_coordination_actions"],
        comparison_logic="Compare a surface-performance read against the authored misalignment pattern forming underneath it.",
    ),
    ui_schema={
        "primary_signal_label": "Observed Risk",
        "secondary_signal_label": "Visible Delivery Wobble",
        "hidden_signal_label": "Hidden Misalignment Risk",
        "primary_signal_description": "The visible friction around Riley is meant to feel like the clearest live issue.",
        "hidden_signal_description": "The real teaching risk is that the team is staying functional by carrying pressure in hidden, misaligned ways that make the system more fragile than it looks.",
        "reveal_mode": "scenario_specific",
        "teaching_misread": "The player is meant to over-read Riley's visible disengagement as apathy and under-read the quieter carrying that is making the system look stronger and steadier than it really is.",
        "play_ui": {
            "lead_prompt": "Take the visible issue seriously, but keep asking whether the team is coping by privately adapting around it rather than bringing the strain back into alignment.",
            "status_labels": {
                "failing": "Compounding",
                "acceptable": "Holding",
                "mastery": "Redistributing",
            },
        },
    },
    evaluation_modes={
        "teaching": {
            "allow_acceptable_route_support": True,
            "allow_success_guarantee": True,
            "outcome_labels": ["Fail", "Survive", "Succeed"],
            "feedback_style": "coaching",
        },
        "simulation": {
            "allow_acceptable_route_support": False,
            "allow_success_guarantee": False,
            "outcome_labels": ["Escalating", "Contained", "Stabilised", "Collapsed"],
            "feedback_style": "analytical",
        },
    },
    default_evaluation_mode="teaching",
    runtime_preset={
        "role_assignments": {
            "focal_employee": "Riley",
            "hidden_strain_employee": "Maya",
            "spillover_employee": "Jordan",
            "cluster_anchor": "Sam",
        },
        "scenario_state_defaults": {
            "investigated_hidden_by_week_2": 0,
            "targeted_on_hidden_by_week_4": 0,
            "load_relief_on_hidden_by_week_4": 0,
            "clustered_on_hidden_by_week_4": 0,
            "focal_support_by_week_2": 0,
            "hidden_support_work_pool": 0.98,
        },
        "node_overrides": {
            "focal_employee": {
                "strain": 0.50,
                "manager_relationship": 0.58,
                "manager_contact_frequency": 0.67,
                "recent_behaviors": ["missed_deadline_minor", "complaint"],
                "scenario_visibility_bias": 0.12,
                "scenario_spillover_bias": 0.04,
            },
            "hidden_strain_employee": {
                "strain": 0.48,
                "manager_relationship": 0.54,
                "manager_contact_frequency": 0.63,
                "recent_behaviors": [],
                "scenario_visibility_bias": -0.22,
                "scenario_spillover_bias": 0.10,
                "absorbed_workload": 0.52,
                "last_absorbed_workload": 0.52,
                "scenario_display_load": 0.52,
            },
            "spillover_employee": {
                "strain": 0.42,
                "manager_relationship": 0.60,
                "manager_contact_frequency": 0.72,
                "recent_behaviors": ["complaint"],
                "scenario_visibility_bias": 0.01,
                "scenario_spillover_bias": 0.05,
            },
            "cluster_anchor": {
                "strain": 0.40,
                "manager_relationship": 0.55,
                "manager_contact_frequency": 0.58,
                "recent_behaviors": [],
                "scenario_visibility_bias": 0.00,
                "scenario_spillover_bias": 0.04,
                "absorbed_workload": 0.14,
                "last_absorbed_workload": 0.14,
                "scenario_display_load": 0.14,
            },
        },
        "named_node_overrides": {
            "Avery": {
                "strain": 0.36,
                "recent_behaviors": ["ignored_email"],
                "scenario_visibility_bias": -0.05,
                "absorbed_workload": 0.20,
                "last_absorbed_workload": 0.20,
                "scenario_display_load": 0.20,
            },
            "Morgan": {
                "strain": 0.33,
                "recent_behaviors": [],
                "scenario_visibility_bias": -0.04,
                "absorbed_workload": 0.12,
                "last_absorbed_workload": 0.12,
                "scenario_display_load": 0.12,
            },
        },
        "forced_edges": [
            {"left_role": "hidden_strain_employee", "right_role": "focal_employee", "weight_range": [0.34, 0.50]},
            {"left_role": "hidden_strain_employee", "right_role": "spillover_employee", "weight_range": [0.34, 0.50]},
            {"left_role": "hidden_strain_employee", "right_role": "cluster_anchor", "weight_range": [0.34, 0.50]},
            {"left_role": "spillover_employee", "right_role": "focal_employee", "weight_range": [0.28, 0.42]},
            {"left_role": "cluster_anchor", "right_role": "spillover_employee", "weight_range": [0.28, 0.42]},
        ],
        "cluster_node_adjustments": {
            "trust": -0.05,
            "alignment": -0.08,
        },
        "manager_state_adjustments": {
            "strain": 0.02,
        },
        "founder_state_adjustments": {
            "founder_pressure": 0.03,
            "founder_clarity": -0.02,
        },
        "action_progress_rules": [
            {
                "category": "targeted",
                "target_role": "focal_employee",
                "week_lte": 2,
                "increments": {"focal_support_by_week_2": 1},
            },
            {
                "action_types": ["check_in_on_load_bearing_risk", "surface_hidden_support_work"],
                "target_role": "hidden_strain_employee",
                "week_lte": 2,
                "increments": {"investigated_hidden_by_week_2": 1},
            },
            {
                "category": "targeted",
                "target_role": "hidden_strain_employee",
                "week_lte": 4,
                "increments": {"targeted_on_hidden_by_week_4": 1},
            },
            {
                "action_types": ["reduce_workload", "reallocate_workload"],
                "target_role": "hidden_strain_employee",
                "week_lte": 4,
                "increments": {"load_relief_on_hidden_by_week_4": 1},
            },
            {
                "category": "clustered",
                "target_role": "hidden_strain_employee",
                "week_lte": 4,
                "increments": {"clustered_on_hidden_by_week_4": 1},
            },
        ],
        "action_quality_by_week": {
            1: [
                {"action_types": ["quick_check_in"], "target_role": "focal_employee", "quality": "strong"},
                {"action_types": ["check_in_on_load_bearing_risk"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["offer_coaching_support"], "target_role": "focal_employee", "quality": "acceptable"},
                {"action_types": ["reduce_workload", "group_mediation", "clarify_roles_and_handoffs", "do_nothing"], "quality": "weak"},
            ],
            2: [
                {"action_types": ["reallocate_workload"], "target_role": "hidden_strain_employee", "secondary_target_role": "cluster_anchor", "quality": "strong"},
                {"action_types": ["clarify_roles_and_handoffs"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["reduce_workload"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["group_mediation"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            3: [
                {"action_types": ["surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["check_in_on_load_bearing_risk", "quick_check_in"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["clarify_roles_and_handoffs"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            4: [
                {"action_types": ["group_mediation"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["clarify_roles_and_handoffs"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["reduce_workload", "reallocate_workload"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            5: [
                {"action_types": ["quick_check_in"], "target_role": "hidden_strain_employee", "quality": "strong"},
                {"action_types": ["offer_coaching_support"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["check_in_on_load_bearing_risk", "surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
                {"action_types": ["do_nothing"], "quality": "weak"},
            ],
            6: [
                {"action_types": ["do_nothing"], "quality": "strong"},
                {"action_types": ["quick_check_in"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["surface_hidden_support_work"], "target_role": "hidden_strain_employee", "quality": "acceptable"},
                {"action_types": ["group_mediation", "clarify_roles_and_handoffs", "reduce_workload", "reallocate_workload"], "target_role": "hidden_strain_employee", "quality": "weak"},
                {"action_types": ["quick_check_in", "offer_coaching_support", "reduce_workload"], "target_role": "focal_employee", "quality": "weak"},
            ],
        },
        "route_rules": {
            "mastery": {
                "all": [
                    {"type": "counter", "counter": "investigated_hidden_by_week_2", "op": ">=", "value": 1},
                    {"type": "counter", "counter": "load_relief_on_hidden_by_week_4", "op": ">=", "value": 1},
                    {"type": "counter", "counter": "targeted_on_hidden_by_week_4", "op": ">=", "value": 2},
                ],
            },
            "acceptable": {
                "all": [
                    {"type": "counter", "counter": "focal_support_by_week_2", "op": ">=", "value": 1},
                    {"type": "counter", "counter": "targeted_on_hidden_by_week_4", "op": ">=", "value": 1},
                    {"type": "counter", "counter": "load_relief_on_hidden_by_week_4", "op": ">=", "value": 1},
                ],
                "none": [
                    {"type": "route_active", "route": "mastery"},
                ],
            },
        },
        "outcome_evaluation_order": ["fail", "success", "acceptable"],
        "outcome_rules": {
            "fail": {
                "all": [
                    {"type": "not", "rule": {"type": "survived_to_end"}},
                ],
            },
            "success": {
                "all": [
                    {"type": "survived_to_end"},
                    {"type": "route_active", "route": "mastery"},
                ],
            },
            "acceptable": {
                "all": [
                    {"type": "survived_to_end"},
                ],
            },
        },
        "recommended_actions_by_week": {
            1: [("quick_check_in", "focal_employee"), ("check_in_on_load_bearing_risk", "hidden_strain_employee")],
            2: [("reallocate_workload", "hidden_strain_employee", "cluster_anchor"), ("quick_check_in", "focal_employee")],
            3: [("surface_hidden_support_work", "hidden_strain_employee")],
            4: [("quick_check_in", "hidden_strain_employee"), ("quick_check_in", "focal_employee")],
            5: [("quick_check_in", "focal_employee")],
            6: [("quick_check_in", "focal_employee")],
        },
        "recommended_week_tactics": {
            1: "use Quick Check-In with {focal}, while also using Check Capacity with {hidden}",
            2: "use Reallocate Workload away from {hidden}, while also using Quick Check-In with {focal} so the visible issue is still being managed directly",
            3: "use Review How Work Is Flowing around {hidden}",
            4: "use Quick Check-In with both {hidden} and {focal} so the hidden load stays visible while Riley still gets direct support",
            5: "use Quick Check-In directly with {focal} while the earlier structural changes keep the background carrying from rebuilding",
            6: "use Quick Check-In directly with {focal} so the visible issue still gets direct management attention without collapsing the read back to surface-only support",
        },
        "recommended_analysis_openers": {
            1: "Early on, it was reasonable to focus on Riley because that was where the friction was easiest to see.",
            2: "By this stage, the job was becoming less about the visible symptom and more about whether the week was quietly being held together in the background.",
            3: "By week three, the pattern should have been easier to recognise.",
            4: "At this stage, the question was how to keep Maya visible in the read without abandoning Riley as the visible issue.",
            5: "By this point, a stronger manager would be checking whether the earlier structural correction was holding while still staying close to Riley directly.",
            6: "By the end of the run, the quality of the response came down to whether you had reduced the spillover early enough to return your attention to Riley without losing the broader read.",
        },
        "recommended_analysis_copy": {
            "opening": (
                "At the outset, the main management question was whether the friction around {focal} was the whole problem or the most visible sign of pressure already spilling elsewhere in the team. "
                "The easy move was to manage what you could already see. The stronger read was to ask who was quietly keeping the week on track. "
                "What mattered most at this stage was not just calming the visible issue, but understanding where the spillover was actually landing."
            ),
            "corrective": {
                1: (
                    "By staying too tightly with the visible issue around {focal}, you left the quieter question of who was carrying the week less tested than it needed to be. "
                    "{week_tactics_sentence}. That would have taken the visible friction seriously while also checking whether {hidden} was carrying more than was obvious."
                ),
                2: (
                    "The task was becoming less about the visible symptom and more about whether the week was quietly being rescued in the background. "
                    "{week_tactics_sentence}. That would have started to take pressure out of the work landing with {hidden}, rather than only reacting to how the week looked on the surface."
                ),
                3: (
                    "{focal} was still the visible issue, but the larger risk was whether too much of the cleanup was quietly resting with {hidden}. "
                    "{week_tactics_sentence}. That would have been a stronger read than getting through the week by quietly spending {hidden}'s reliability."
                ),
                4: (
                    "The stronger management read was whether you were reducing the spillover rather than treating {hidden}'s steadiness as proof that they would keep coping. "
                    "{week_tactics_sentence}. That would have helped turn quiet reliability into something the team supported, instead of something it leaned on."
                ),
                5: (
                    "A stronger manager would be staying close to {hidden} while checking that the surrounding group was not drifting back into old rescue habits. "
                    "{week_tactics_sentence}. The key question here was whether the team was actually asking less of one dependable person."
                ),
                6: (
                    "The quality of the response came down to whether you had reduced the spillover or simply made the week look calmer on the surface. "
                    "{week_tactics_sentence}. That would have protected {hidden}'s recovery while confirming that the visible symptom around {focal} no longer depended on invisible rescue work."
                ),
            },
            "reinforcing": {
                1: (
                    "You were beginning to read this at the right level rather than treating the visible friction around {focal} as the whole problem. "
                    "{week_tactics_sentence}. That started to separate the visible wobble from the quieter question of who was keeping the week on track."
                ),
                2: (
                    "You were moving past the visible symptom and paying attention to whether the week was quietly being held together in the background. "
                    "{week_tactics_sentence}. That started to take pressure out of the work landing with {hidden}, rather than only reacting to how the week looked on the surface."
                ),
                3: (
                    "{focal} was still the visible issue, but you were also treating the spillover around {hidden} as the larger management risk. "
                    "{week_tactics_sentence}. That was a stronger read than simply getting through the week by quietly spending {hidden}'s reliability."
                ),
                4: (
                    "You were no longer acting as though the problem started and ended with {focal}. "
                    "{week_tactics_sentence}. That kept strengthening the system around {hidden} rather than treating their steadiness as proof they would just keep coping."
                ),
                5: (
                    "You were staying close to {hidden} while checking that the surrounding group was not drifting back into old rescue habits. "
                    "{week_tactics_sentence}. The important thing here was that you were watching whether the team was actually asking less of one dependable person."
                ),
                6: (
                    "You were reducing the spillover rather than simply making the week look calmer on the surface. "
                    "{week_tactics_sentence}. That protected {hidden}'s recovery while confirming that the visible symptom around {focal} no longer depended on invisible rescue work."
                ),
            },
        },
        "outcome_copy": {
            "fail": {
                "title": "The situation spiralled.",
                "strength": "You did something a good manager might plausibly do: you responded to the visible issue and tried to steady the week.",
                "improvement": "To get ahead of the pattern, you needed to notice sooner where the spillover work was quietly landing.",
            },
            "acceptable": {
                "title": "You managed the situation.",
                "strength": "You moved beyond the first surface read and offered meaningful support where the team was quietly carrying the pressure.",
                "improvement": "To solve the deeper problem, you needed to reduce hidden spillover earlier instead of only calming the visible friction.",
            },
            "success": {
                "title": "You managed the situation.",
                "strength": "You treated quiet reliability as a risk signal and reduced how much of the week depended on one dependable person.",
                "improvement": "This is the strongest response this scenario was designed to teach.",
            },
        },
    },
)


SCENARIOS = {
    BASELINE.id: BASELINE,
    CONFLICT_CLUSTER.id: CONFLICT_CLUSTER,
    QUIET_HIGH_PERFORMER.id: QUIET_HIGH_PERFORMER,
}

STARTER_PACK_SCENARIOS = [
    "scenario_01",
    "scenario_02",
]

STARTER_PACK_NAME = "Suppress the Stress Starter Pack"
