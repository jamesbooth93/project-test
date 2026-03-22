from dataclasses import dataclass

from action_registry import INTENTION_WAIT_AND_OBSERVE, action_cost, action_label
from scenario_copy import scenario_main_screen_aside, scenario_weekly_briefing


@dataclass
class WeeklyViewModel:
    week_label: str
    briefing_text: str
    briefing_aside: str
    key_signals: list[str]
    evidence_modules: list[str]
    employee_rows: list[dict]
    focus_options: list[dict]
    reflection_prompt: str
    action_groups: list[dict]
    energy_remaining: float
    energy_max: float
    resolution: dict[str, str]


def _action_label(action_key: str) -> str:
    return action_label(action_key)


def build_weekly_view_model(game) -> WeeklyViewModel:
    overview = game.get_scenario_overview()
    ui_config = overview.get("ui_config")
    visible_state = game.get_visible_state()
    summary = game.get_summary()

    action_groups = []
    if ui_config:
        for intent, actions in ui_config.action_groups.items():
            if intent == INTENTION_WAIT_AND_OBSERVE:
                continue
            action_groups.append({
                "intent": intent,
                "actions": [
                    {
                        "key": action_key,
                        "label": _action_label(action_key),
                        "cost": action_cost(action_key),
                    }
                    for action_key in actions
                ],
            })

    story = game._build_scenario_story_data()
    briefing_override = scenario_weekly_briefing(game.scenario, game.week)
    return WeeklyViewModel(
        week_label=f"Week {game.week} of {game.max_weeks}",
        briefing_text=(
            briefing_override.get("briefing")
            or (ui_config.briefing_narrative_template if ui_config else overview.get("description", ""))
        ),
        briefing_aside=scenario_main_screen_aside(game),
        key_signals=(briefing_override.get("signals") or (ui_config.key_signals if ui_config else [])),
        evidence_modules=(ui_config.evidence_modules if ui_config else ["employee_table"]),
        employee_rows=visible_state,
        focus_options=visible_state[:5],
        reflection_prompt=(
            ui_config.reflection_prompts[(game.week - 1) % len(ui_config.reflection_prompts)]
            if ui_config and ui_config.reflection_prompts else
            "What stands out to you this week?"
        ),
        action_groups=action_groups,
        energy_remaining=summary["manager_energy_current"],
        energy_max=summary["manager_energy_max"],
        resolution={
            "what_you_chose": story.get("what_you_chose", ""),
            "how_it_landed": story.get("how_it_landed", ""),
            "what_shifted": story.get("what_shifted", ""),
            "what_to_watch": story.get("what_to_watch", ""),
        },
    )
