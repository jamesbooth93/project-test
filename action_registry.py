from dataclasses import dataclass

INTENTION_SUPPORT_INDIVIDUAL = "Support an Individual"
INTENTION_SUPPORT_TEAM = "Support the Team"
INTENTION_INVESTIGATE_FURTHER = "Investigate Further"
INTENTION_REDISTRIBUTE_WORKLOAD = "Redistribute Workload"
INTENTION_IMPROVE_COORDINATION = "Improve Coordination"
INTENTION_WAIT_AND_OBSERVE = "Wait and Observe"

GAME_INTENTIONS = (
    INTENTION_SUPPORT_INDIVIDUAL,
    INTENTION_SUPPORT_TEAM,
    INTENTION_INVESTIGATE_FURTHER,
    INTENTION_REDISTRIBUTE_WORKLOAD,
    INTENTION_IMPROVE_COORDINATION,
    INTENTION_WAIT_AND_OBSERVE,
)


@dataclass(frozen=True)
class ActionPresentation:
    label: str
    description: str
    past_tense_label: str


@dataclass(frozen=True)
class ActionDef:
    id: str
    intention: str
    family: str
    target_scope: str
    target_required: bool
    energy_cost: float
    strategy_group: str = "other"
    tags: tuple[str, ...] = ()
    decision_type: str = "unknown"
    sim_aliases: tuple[str, ...] = ()
    presentation: ActionPresentation | None = None


ACTION_REGISTRY: dict[str, ActionDef] = {
    "do_nothing": ActionDef(
        id="do_nothing",
        intention=INTENTION_WAIT_AND_OBSERVE,
        family="observation",
        target_scope="none",
        target_required=False,
        energy_cost=0.0,
        strategy_group="none",
        tags=("wait", "observation"),
        decision_type="under_response",
        presentation=ActionPresentation(
            label="Hold Back For Now And Watch For A Clearer Signal",
            description="Pause before intervening and wait to see whether the pattern becomes clearer next week.",
            past_tense_label="Held Back And Watched For A Clearer Signal",
        ),
    ),
    "quick_check_in": ActionDef(
        id="quick_check_in",
        intention=INTENTION_SUPPORT_INDIVIDUAL,
        family="individual_support",
        target_scope="individual",
        target_required=True,
        energy_cost=1.0,
        strategy_group="targeted",
        tags=("support", "diagnostic"),
        decision_type="reactive_targeted_support",
        sim_aliases=("manager_support",),
        presentation=ActionPresentation(
            label="Understand What They Need Via A 1:1 Check-In",
            description="Use a short 1:1 conversation to respond quickly to visible pressure around one person.",
            past_tense_label="Used A 1:1 Check-In To Understand What They Needed",
        ),
    ),
    "reduce_workload": ActionDef(
        id="reduce_workload",
        intention=INTENTION_REDISTRIBUTE_WORKLOAD,
        family="workload_rebalancing",
        target_scope="individual",
        target_required=True,
        energy_cost=4.0,
        strategy_group="targeted",
        tags=("support", "workload"),
        decision_type="reactive_targeted_support",
        sim_aliases=("workload_relief",),
        presentation=ActionPresentation(
            label="Take Pressure Off Them Via A Priority Reset",
            description="Reduce immediate pressure on one person by making it clear what can wait.",
            past_tense_label="Used A Priority Reset To Take Pressure Off Them",
        ),
    ),
    "reallocate_workload": ActionDef(
        id="reallocate_workload",
        intention=INTENTION_REDISTRIBUTE_WORKLOAD,
        family="workload_rebalancing",
        target_scope="individual",
        target_required=True,
        energy_cost=2.0,
        strategy_group="targeted",
        tags=("workload", "redistribution"),
        decision_type="workload_reallocation",
        presentation=ActionPresentation(
            label="Spread Pressure More Evenly Via Workload Reallocation",
            description="Move work from one person to another to rebalance pressure across the team.",
            past_tense_label="Used Workload Reallocation To Spread Pressure More Evenly",
        ),
    ),
    "offer_coaching_support": ActionDef(
        id="offer_coaching_support",
        intention=INTENTION_SUPPORT_INDIVIDUAL,
        family="capacity_building",
        target_scope="individual",
        target_required=True,
        energy_cost=3.0,
        strategy_group="targeted",
        tags=("support", "resilience"),
        decision_type="proactive_relationship_building",
        sim_aliases=("capacity_building", "manager_support"),
        presentation=ActionPresentation(
            label="Help Them Cope Better Via Focused Coaching",
            description="Spend focused time helping one person handle the work more effectively.",
            past_tense_label="Used Focused Coaching To Help Them Cope Better",
        ),
    ),
    "check_in_on_load_bearing_risk": ActionDef(
        id="check_in_on_load_bearing_risk",
        intention=INTENTION_INVESTIGATE_FURTHER,
        family="diagnostic_support",
        target_scope="individual",
        target_required=True,
        energy_cost=3.0,
        strategy_group="targeted",
        tags=("support", "diagnostic", "dependency"),
        decision_type="diagnostic_support",
        presentation=ActionPresentation(
            label="Test Whether They Are Carrying Hidden Strain Via A Direct Capacity Check",
            description="Ask one person how manageable the work really feels and what they may be carrying quietly.",
            past_tense_label="Used A Direct Capacity Check To Test For Hidden Strain",
        ),
    ),
    "surface_hidden_support_work": ActionDef(
        id="surface_hidden_support_work",
        intention=INTENTION_INVESTIGATE_FURTHER,
        family="diagnostic_support",
        target_scope="individual",
        target_required=True,
        energy_cost=3.0,
        strategy_group="targeted",
        tags=("diagnostic", "dependency", "visibility"),
        decision_type="diagnostic_support",
        presentation=ActionPresentation(
            label="Reveal Where Rescue Work Is Accumulating Via A Workflow Review",
            description="Look at where work is getting stuck and who keeps quietly picking it up.",
            past_tense_label="Used A Workflow Review To Reveal Where Rescue Work Was Accumulating",
        ),
    ),
    "group_mediation": ActionDef(
        id="group_mediation",
        intention=INTENTION_IMPROVE_COORDINATION,
        family="coordination_repair",
        target_scope="cluster",
        target_required=True,
        energy_cost=3.0,
        strategy_group="clustered",
        tags=("coordination", "cluster"),
        decision_type="cluster_stabilisation",
        sim_aliases=("team_mediation",),
        presentation=ActionPresentation(
            label="Clear The Air Via A Mediated Team Conversation",
            description="Bring the relevant people together to address tension directly before it spreads further.",
            past_tense_label="Used A Mediated Team Conversation To Clear The Air",
        ),
    ),
    "clarify_roles_and_handoffs": ActionDef(
        id="clarify_roles_and_handoffs",
        intention=INTENTION_IMPROVE_COORDINATION,
        family="coordination_repair",
        target_scope="cluster",
        target_required=True,
        energy_cost=3.0,
        strategy_group="clustered",
        tags=("coordination", "structure"),
        decision_type="cluster_stabilisation",
        sim_aliases=("team_mediation",),
        presentation=ActionPresentation(
            label="Set Clear Boundaries Via Roles And Handoffs",
            description="Set clearer ownership boundaries so work stops bouncing back and forth.",
            past_tense_label="Used Roles And Handoffs To Set Clear Boundaries",
        ),
    ),
    "team_meeting": ActionDef(
        id="team_meeting",
        intention=INTENTION_SUPPORT_TEAM,
        family="team_reset",
        target_scope="team",
        target_required=False,
        energy_cost=2.0,
        strategy_group="team",
        tags=("team", "alignment"),
        decision_type="broad_team_support",
        sim_aliases=("team_buffer_support",),
        presentation=ActionPresentation(
            label="Steady The Team This Week Via A Reset Meeting",
            description="Bring the team together to reset priorities and improve alignment this week.",
            past_tense_label="Used A Reset Meeting To Steady The Team This Week",
        ),
    ),
    "stress_management_workshop": ActionDef(
        id="stress_management_workshop",
        intention=INTENTION_SUPPORT_TEAM,
        family="team_resilience",
        target_scope="team",
        target_required=False,
        energy_cost=4.0,
        strategy_group="team",
        tags=("team", "resilience"),
        decision_type="broad_team_support",
        sim_aliases=("universal_support",),
        presentation=ActionPresentation(
            label="Put Longer-Term Support In Place Via A Stress Workshop",
            description="Set up support for the team that helps over time rather than immediately.",
            past_tense_label="Used A Stress Workshop To Put Longer-Term Support In Place",
        ),
    ),
}


def get_action(action_id: str) -> ActionDef | None:
    return ACTION_REGISTRY.get(action_id)


def action_cost(action_id: str) -> float:
    action = get_action(action_id)
    return action.energy_cost if action else 0.0


def action_label(action_id: str) -> str:
    action = get_action(action_id)
    if action and action.presentation:
        return action.presentation.label
    return action_id.replace("_", " ").title()


def action_description(action_id: str) -> str:
    action = get_action(action_id)
    if action and action.presentation:
        return action.presentation.description
    return ""


def action_past_tense(action_id: str) -> str:
    action = get_action(action_id)
    if action and action.presentation:
        return action.presentation.past_tense_label
    return action_label(action_id)


def action_decision_type(action_id: str) -> str:
    action = get_action(action_id)
    return action.decision_type if action else "unknown"


def action_target_level(action_id: str) -> str:
    action = get_action(action_id)
    return action.target_scope if action else "unknown"


def action_category(action_id: str) -> str:
    action = get_action(action_id)
    return action.strategy_group if action else "unknown"


def action_intention(action_id: str) -> str:
    action = get_action(action_id)
    return action.intention if action else "unknown"


def is_team_wide(action_id: str) -> bool:
    return action_target_level(action_id) == "team"


def action_has_tag(action_id: str, tag: str) -> bool:
    action = get_action(action_id)
    return bool(action and tag in action.tags)


def sim_action_map() -> dict[str, str]:
    mapping: dict[str, str] = {"do_nothing": "do_nothing"}
    for action_id, action in ACTION_REGISTRY.items():
        for alias in action.sim_aliases:
            mapping[alias] = action_id
    return mapping
