from dataclasses import dataclass
from typing import Any

from action_registry import action_decision_type, action_target_level


@dataclass
class AnalysisBlock:
    rating: str | None = None
    score: float | None = None
    label: str | None = None
    summary: str = ""


@dataclass
class DecisionAnalysis:
    decision_type: str
    target_level: str
    fit_to_visible_problem: AnalysisBlock
    fit_to_hidden_problem: AnalysisBlock
    misdirection_risk: AnalysisBlock
    hidden_risk_callout: AnalysisBlock
    time_to_impact: AnalysisBlock
    counterfactual_better_option: AnalysisBlock
    confidence_gap: AnalysisBlock | None
    outcome_classification: str
    teaching_summary: str


def classify_decision_type(action_type: str) -> str:
    return action_decision_type(action_type)


def classify_target_level(action_type: str) -> str:
    return action_target_level(action_type)


def analyse_conflict_cluster(snapshot: dict[str, Any]) -> DecisionAnalysis:
    action = snapshot.get("action", {})
    action_type = action.get("type", "do_nothing")
    run_profile = snapshot.get("run_strategy_profile", "mixed_response")
    outcome_tier = snapshot.get("scenario_outcome_tier", "Fail")

    visible_fit = AnalysisBlock(
        rating="high" if action_type in {"quick_check_in", "reduce_workload", "offer_coaching_support", "group_mediation"} else "low",
        summary="This was a reasonable response to the visible focal problem.",
    )

    if run_profile == "stabilising_response" and outcome_tier == "Succeed":
        hidden_fit = AnalysisBlock(
            rating="high",
            summary="This response acted on the unstable cluster, not only the visible symptom.",
        )
        risk = AnalysisBlock(
            score=0.18,
            label="Low",
            summary="Low chance that your decision stabilised the wrong part of the system.",
        )
        hidden_callout = AnalysisBlock(
            summary="The main hidden risk sat in the surrounding cluster, and your response matched that level."
        )
        time_to_impact = AnalysisBlock(
            label="Contained",
            summary="The pattern was interrupted before it could harden.",
        )
        better_option = AnalysisBlock(
            summary="You were already close to the strongest available response."
        )
        outcome_classification = "root_cause_aligned"
        teaching_summary = "You diagnosed the problem at the right level and acted early enough."
    elif outcome_tier == "Survive":
        hidden_fit = AnalysisBlock(
            rating="medium",
            summary="Your response reduced harm, but did not fully address the unstable cluster.",
        )
        risk = AnalysisBlock(
            score=0.48,
            label="Moderate",
            summary="Moderate chance that the action stabilised the visible symptom more than the real driver.",
        )
        hidden_callout = AnalysisBlock(
            summary="The highest ongoing risk remained in the cluster around the focal employee."
        )
        time_to_impact = AnalysisBlock(
            label="3-4 weeks",
            summary="Without stronger clustered action, local pressure tends to return within a few weeks.",
        )
        better_option = AnalysisBlock(
            summary="A clustered intervention earlier would likely have reduced spread more effectively."
        )
        outcome_classification = "misdirected_but_reasonable"
        teaching_summary = "You made a reasonable call, but a stronger read would have acted on the cluster sooner."
    else:
        hidden_fit = AnalysisBlock(
            rating="low",
            summary="The response did not address the unstable local system underneath the visible problem.",
        )
        risk = AnalysisBlock(
            score=0.72,
            label="High",
            summary="High chance that the action stabilised the wrong part of the system.",
        )
        hidden_callout = AnalysisBlock(
            summary="You targeted the visible symptom while the cluster continued to harden."
        )
        time_to_impact = AnalysisBlock(
            label="1-3 weeks",
            summary="This pattern usually escalates quickly once strain starts spreading locally.",
        )
        better_option = AnalysisBlock(
            summary="Cluster-focused support would likely have reduced the spread more effectively."
        )
        outcome_classification = "under_response" if action_type == "do_nothing" else "misdirected_but_reasonable"
        teaching_summary = "The visible issue was real, but it was not the whole problem."

    confidence_gap = AnalysisBlock(
        label="Confidence Gap",
        summary="The visible signals made one response look obvious, but the hidden pattern rewarded a different level of action.",
    )

    return DecisionAnalysis(
        decision_type=classify_decision_type(action_type),
        target_level=classify_target_level(action_type),
        fit_to_visible_problem=visible_fit,
        fit_to_hidden_problem=hidden_fit,
        misdirection_risk=risk,
        hidden_risk_callout=hidden_callout,
        time_to_impact=time_to_impact,
        counterfactual_better_option=better_option,
        confidence_gap=confidence_gap,
        outcome_classification=outcome_classification,
        teaching_summary=teaching_summary,
    )


def analyse_snapshot(snapshot: dict[str, Any]) -> DecisionAnalysis | None:
    scenario_name = snapshot.get("scenario")
    if scenario_name == "scenario_01":
        return analyse_conflict_cluster(snapshot)
    return None
