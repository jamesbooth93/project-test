import math
import os
import matplotlib.pyplot as plt
import streamlit as st

from action_registry import action_cost, action_description, action_label, action_past_tense
from benchmarks import (
    autoplay_demo_route,
    autoplay_demo_route_until_week,
    autoplay_demo_route_for_explicit_path_randomized,
    autoplay_demo_route_for_outcome,
    autoplay_demo_route_for_outcome_randomized,
    autoplay_demo_route_for_summary_branch,
    autoplay_demo_route_for_summary_branch_randomized,
)
from game_logic import TEAM_WIDE_ACTIONS, GameState
from scenario_definitions import SCENARIOS, STARTER_PACK_NAME, STARTER_PACK_SCENARIOS
from charts import (
    draw_network_chart,
    draw_observed_risk_chart,
    draw_riley_maya_bar_chart,
    draw_riley_maya_observed_vs_actual_chart,
    draw_visible_friction_chart,
    draw_workload_distribution_chart,
    visible_load_label,
)
from reporting import (
    _analysis_snapshot_for_week,
    build_benchmark_history,
    build_end_of_week_report,
    cluster_strain_avg,
    cluster_strain_improvement,
    core_group_high_strain_count,
    determine_summary_branch,
    SCENARIO_02_HIDDEN_STRAIN_TARGET,
    scenario_two_hidden_employee_strain,
    scenario_two_hidden_strain_comparison,
    scenario_two_peak_dependency_comparison,
)
from scenario_runtime import (
    apply_recommended_actions_for_week,
    recommended_analysis_copy,
)
from scenario_copy import (
    scenario_analysis_copy,
    scenario_end_screen_copy,
    scenario_week_end_report,
)
from character_profiles import character_profile
from view_models import (
    build_weekly_view_model,
)
from workshop_mock import SCENARIO_02_WORKSHOP_MOCK

TEST_MODE = os.environ.get("MANAGEMENT_SIM_TEST_MODE") == "1"
SCENARIO_02_WORKSHOP_TITLE = "Fragile Under Pressure"
SHOW_SIDEBAR = False

if not TEST_MODE:
    st.set_page_config(
        page_title="Suppress the Stress",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

DEFAULT_SCENARIO_KEY = STARTER_PACK_SCENARIOS[0]
PRODUCT_TITLE = "Suppress the Stress"
PRODUCT_SUBTITLE = "Notice the signals. Read the pattern. Strengthen the team."
PACK_STATUS_TEXT = (
    f"This build is currently focused on the {STARTER_PACK_NAME.lower()}. "
    "The scenario shell is staying deliberately narrow while the first pack takes shape."
)
if not TEST_MODE:
    st.markdown(
        """
    <style>
    .block-container {
        max-width: 1260px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    .shell-card {
        background: linear-gradient(180deg, #fffdf8 0%, #f5efe2 100%);
        border: 1px solid #e4d9be;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .soft-card {
        background: transparent;
        border: none;
        box-shadow: none;
        border-radius: 16px;
        padding: 0.4rem 0;
        margin-bottom: 1rem;
    }
    .section-label {
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.74rem;
        color: #8b6f3d;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }
    .centered-subheader {
        text-align: center;
    }
    .centered-miniheader {
        text-align: center;
        font-size: 0.95rem;
        font-weight: 600;
        color: #4b5563;
        margin: 0.7rem 0 0.45rem 0;
    }
    .visible-dev-heading {
        text-align: center;
        font-size: 0.95rem;
        font-weight: 700;
        color: #4f3b17;
        text-decoration: underline;
        margin: 0.7rem 0 0.45rem 0;
    }
    .subtle-section-break {
        display: block;
        border: none;
        border-top: 1px solid #e5dccb;
        margin: 1.4rem auto 1rem auto;
        width: 180px;
    }
    .centered-outcome {
        text-align: center;
    }
    .summary-impact {
        text-align: center;
        font-size: 1.55rem;
        line-height: 1.15;
        color: #ffffff;
        font-weight: 700;
        margin: 0;
    }
    .results-column {
        max-width: 760px;
        margin: 0 auto 1rem auto;
    }
    .centered-results-text {
        text-align: center;
    }
    .hero-title {
        font-size: 2.25rem;
        line-height: 1.05;
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 0.25rem;
        text-align: center;
    }
    .hero-subtitle {
        color: #ffffff;
        font-size: 1rem;
        margin-bottom: 0.85rem;
        text-align: center;
    }
    .title-band {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 1.5rem;
        width: 100%;
        margin-bottom: 0.95rem;
    }
    .title-band-main {
        color: #ffffff;
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 700;
    }
    .title-band-week {
        color: #ffffff;
        font-size: 1.2rem;
        line-height: 1.1;
        font-weight: 600;
        text-align: right;
        white-space: nowrap;
    }
    .signal-list {
        margin: 0.55rem 0 0 0;
        padding-left: 1.2rem;
    }
    .signal-list li {
        margin-bottom: 0.35rem;
    }
    .intent-chip {
        display: inline-block;
        padding: 0.28rem 0.62rem;
        border-radius: 999px;
        margin: 0 0.35rem 0.35rem 0;
        background: #ece4d2;
        color: #5b4321;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .resolution-note {
        background: #f4efe5;
        border-left: 4px solid #b8892d;
        padding: 0.85rem 0.95rem;
        border-radius: 10px;
        margin-top: 0.55rem;
        color: #111111;
    }
    .employee-panel {
        background: #ffffff;
        border: 1px solid #e3d8c3;
        border-radius: 14px;
        padding: 1rem 1.05rem;
    }
    .employee-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.15rem;
    }
    .employee-role {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }
    .employee-note {
        color: #374151;
        font-size: 0.96rem;
        margin-bottom: 0.55rem;
    }
    .employee-summary {
        background: #fffdf8;
        border: 1px solid #eadfcb;
        border-radius: 12px;
        padding: 0.8rem 0.9rem;
        margin-top: 0.6rem;
        color: #111111;
    }
    div[data-testid="stButton"] button[kind="secondary"] {
        background: #2f7d32;
        color: #ffffff;
        border: 1px solid #2f7d32;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: #27692a;
        color: #ffffff;
        border: 1px solid #27692a;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

def clear_diagnosis_box():
    st.session_state.evidence_employee_id = None


SIMULATION_SCENARIOS = ["scenario_01", "scenario_02"]
WORKSHOP_SCENARIOS = ["scenario_02"]


def reset_game(scenario_key=None, experience_mode=None):
    selected_scenario = scenario_key or st.session_state.get("selected_scenario", DEFAULT_SCENARIO_KEY)
    st.session_state.selected_scenario = selected_scenario
    st.session_state.experience_mode = experience_mode or st.session_state.get("experience_mode", "simulation")
    st.session_state.game = GameState(scenario=selected_scenario)
    st.session_state.pending_week_review = False
    st.session_state.review_snapshot_week = None
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None
    for key in ["selected_employee", "selected_employee_from", "selected_employee_to"]:
        if key in st.session_state:
            del st.session_state[key]


def load_demo_run(scenario_key, route_name, desired_tier=None):
    if desired_tier:
        game = autoplay_demo_route_for_outcome(route_name, desired_tier, scenario_key)
    else:
        game = autoplay_demo_route(route_name, seed=0, scenario_key=scenario_key)
    st.session_state.selected_scenario = scenario_key
    st.session_state.experience_mode = "simulation"
    st.session_state.game = game
    st.session_state.pending_week_review = False
    st.session_state.review_snapshot_week = None
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None
    for key in ["selected_employee", "selected_employee_from", "selected_employee_to"]:
        if key in st.session_state:
            del st.session_state[key]


def load_demo_run_for_explicit_path(scenario_key, route_name, desired_path):
    game = autoplay_demo_route_for_explicit_path_randomized(route_name, desired_path, scenario_key)
    st.session_state.selected_scenario = scenario_key
    st.session_state.experience_mode = "simulation"
    st.session_state.game = game
    st.session_state.pending_week_review = False
    st.session_state.review_snapshot_week = None
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None
    for key in ["selected_employee", "selected_employee_from", "selected_employee_to"]:
        if key in st.session_state:
            del st.session_state[key]


def load_demo_week_review(scenario_key, route_name, review_week, desired_tier=None):
    game = autoplay_demo_route_until_week(route_name, seed=0, scenario_key=scenario_key, stop_week=review_week)
    st.session_state.selected_scenario = scenario_key
    st.session_state.experience_mode = "simulation"
    st.session_state.game = game
    st.session_state.pending_week_review = True
    st.session_state.review_snapshot_week = review_week
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None


def load_demo_week_start(scenario_key, route_name, week):
    if week <= 1:
        reset_game(scenario_key, "simulation")
        return
    game = autoplay_demo_route_until_week(route_name, seed=0, scenario_key=scenario_key, stop_week=week - 1)
    st.session_state.selected_scenario = scenario_key
    st.session_state.experience_mode = "simulation"
    st.session_state.game = game
    st.session_state.pending_week_review = False
    st.session_state.review_snapshot_week = None
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None
    for key in ["scenario_02_workshop_step", "scenario_02_workshop_choices"]:
        if key in st.session_state:
            del st.session_state[key]


def ensure_state():
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = DEFAULT_SCENARIO_KEY
    st.session_state.setdefault("experience_mode", "simulation")
    if "game" not in st.session_state:
        reset_game(st.session_state.selected_scenario, st.session_state.get("experience_mode", "simulation"))
    else:
        st.session_state.setdefault("pending_week_review", False)
        st.session_state.setdefault("results_view", "summary")
        st.session_state.setdefault("analysis_week", 0)
        st.session_state.setdefault("evidence_employee_id", None)
        st.session_state.setdefault("scenario_02_workshop_step", 0)
        st.session_state.setdefault("scenario_02_workshop_choices", {})


def people_label(count):
    return "person" if int(count) == 1 else "people"


def format_warning_signs(value):
    raw = str(value or '').strip()
    if not raw or raw == '-':
        return 'Nothing specific is standing out yet'
    parts = [part.strip().replace('_', ' ') for part in raw.split(',') if part.strip()]
    return ', '.join(parts) if parts else 'Nothing specific is standing out yet'


def risk_read(value):
    mapping = {
        "Low": "fairly settled",
        "Guarded": "a little guarded",
        "Elevated": "like a visible pressure point",
        "High": "under real pressure",
    }
    return mapping.get(str(value or "").strip(), "hard to read cleanly")


def determine_summary_title(summary_branch, latest):
    outcome_tier = (latest or {}).get('scenario_outcome_tier')
    if outcome_tier == 'Fail' or summary_branch == 'spiralled':
        return 'The situation spiralled.'
    if summary_branch == 'high_strain_count':
        return 'You managed the situation.'
    if summary_branch == 'more_strain_than_needed':
        return 'You handled the situation reasonably well.'
    return 'You handled the situation exceptionally well.'


def format_event_text(item):
    return str(item).replace("_", " ").strip()


def analysis_step_label(week):
    return "Opening Brief" if week == 0 else f"Week {week}"


def build_opening_snapshot(game):
    opening_game = GameState(
        scenario=game.scenario,
        difficulty=game.difficulty,
        team_size=game.team_size,
        max_weeks=game.max_weeks,
        evaluation_mode=game.evaluation_mode,
        seed=game.rng_seed,
        debug=False,
    )
    visible_rows = opening_game.get_visible_state()
    employees = []
    managed_nodes = set(opening_game.managed_node_ids())
    for row in visible_rows:
        node = opening_game.G.nodes[row["id"]]
        employees.append({
            "id": row["id"],
            "name": row["name"],
            "role": row["role"],
            "true_strain": round(float(node.get("strain", 0.0)), 4),
            "observed_risk": round(float(node.get("observed_risk", 0.0)), 4),
            "strain_gap": round(float(node.get("strain", 0.0)) - float(node.get("observed_risk", 0.0)), 4),
            "risk_label": row.get("risk_label"),
            "recent_behaviors": node.get("recent_behaviors", [])[-5:],
            "recent_support": bool(node.get("recent_support", False)),
            "absorbed_workload": round(float(row.get("absorbed_workload_value", 0.0)), 4),
            "engagement_hint": row.get("engagement_hint"),
            "scenario_role": node.get("scenario_role"),
        })
    network_edges = []
    for left, right in opening_game.G.edges():
        if left in managed_nodes and right in managed_nodes:
            network_edges.append({
                "source": left,
                "target": right,
                "weight": round(float(opening_game.G.edges[left, right].get("weight", 0.0)), 4),
            })
    summary = opening_game.get_summary()
    return {
        "scenario": opening_game.scenario,
        "scenario_name": opening_game.scenario_config.get("name", opening_game.scenario),
        "scenario_roles": dict(opening_game.scenario_state.get("scenario_roles", {})),
        "week": 0,
        "phase": opening_game.phase,
        "result": opening_game.result,
        "game_over": False,
        "manager_energy_current": round(opening_game.manager_state["energy_current"], 2),
        "manager_energy_max": round(opening_game.manager_state["energy_max"], 2),
        "manager_strain": round(opening_game.manager_state["strain"], 2),
        "founder_pressure": round(opening_game.founder_state["founder_pressure"], 2),
        "summary": dict(summary),
        "event_log": [],
        "action": {"type": "opening_brief", "target": None, "summary": ""},
        "actions_taken": [],
        "recommended_actions": [],
        "top_true_strain_employee": max(employees, key=lambda item: item["true_strain"]) if employees else None,
        "top_observed_risk_employee": max(employees, key=lambda item: item["observed_risk"]) if employees else None,
        "scenario_story_data": {},
        "player_diagnosis": "",
        "run_strategy_profile": "opening_state",
        "scenario_outcome_tier": opening_game.scenario_outcome_tier,
        "scenario_outcome_title": opening_game.scenario_outcome_title,
        "scenario_outcome_explanation": opening_game.scenario_outcome_explanation,
        "scenario_outcome_strength": opening_game.scenario_outcome_strength,
        "scenario_outcome_improvement": opening_game.scenario_outcome_improvement,
        "scenario_mastery_reveal": opening_game.scenario_mastery_reveal,
        "great_manager_path_active": bool(opening_game.scenario_state.get("great_manager_path_active", False)),
        "employees": employees,
        "network_edges": network_edges,
    }


def _snapshot_positions(snapshot):
    employees = snapshot.get("employees", []) if snapshot else []
    role_lookup = {employee["id"]: employee.get("scenario_role") for employee in employees}
    ids = [employee["id"] for employee in employees]
    cluster_order = [
        snapshot.get("scenario_roles", {}).get("focal_employee") if snapshot else None,
        snapshot.get("scenario_roles", {}).get("hidden_strain_employee") if snapshot else None,
        snapshot.get("scenario_roles", {}).get("spillover_employee") if snapshot else None,
        snapshot.get("scenario_roles", {}).get("cluster_anchor") if snapshot else None,
    ]
    cluster_ids = [node_id for node_id in cluster_order if node_id in ids]
    positions = {}
    cluster_positions = [(-0.72, 0.34), (0.18, 0.68), (0.76, -0.02), (-0.12, -0.58)]
    for index, node_id in enumerate(cluster_ids):
        positions[node_id] = cluster_positions[index % len(cluster_positions)]
    remaining = [node_id for node_id in ids if node_id not in positions]
    count = len(remaining)
    if count:
        for index, node_id in enumerate(sorted(remaining)):
            angle = (2 * math.pi * index / count) - (math.pi / 2)
            positions[node_id] = (1.95 * math.cos(angle), 1.35 * math.sin(angle))
    return positions


def _shared_analysis_positions(player_snapshot, benchmark_snapshot):
    base = player_snapshot or benchmark_snapshot
    return _snapshot_positions(base)


def _draw_snapshot_map(snapshot, title, metric_key, positions=None, figsize=(6.8, 4.8)):
    fig, ax = plt.subplots(figsize=figsize)
    positions = positions or _snapshot_positions(snapshot)
    employees = snapshot.get("employees", []) if snapshot else []
    employee_lookup = {employee["id"]: employee for employee in employees}
    cluster_ids = {
        snapshot.get("scenario_roles", {}).get("focal_employee"),
        snapshot.get("scenario_roles", {}).get("hidden_strain_employee"),
        snapshot.get("scenario_roles", {}).get("spillover_employee"),
        snapshot.get("scenario_roles", {}).get("cluster_anchor"),
    } if snapshot else set()
    cluster_ids.discard(None)
    for edge in snapshot.get("network_edges", []) if snapshot else []:
        left = positions.get(edge["source"])
        right = positions.get(edge["target"])
        if left and right:
            ax.plot([left[0], right[0]], [left[1], right[1]], color="#d8cdb7", linewidth=0.7 + 2.0 * edge.get("weight", 0.0), alpha=0.22)
    xs, ys, colors, sizes, edgecolors, linewidths = [], [], [], [], [], []
    for node_id, (x, y) in positions.items():
        employee = employee_lookup.get(node_id, {})
        value = float(employee.get(metric_key, 0.0))
        xs.append(x)
        ys.append(y)
        colors.append(value)
        sizes.append(380 + 620 * value)
        if node_id in cluster_ids:
            edgecolors.append("#12324a")
            linewidths.append(2.2)
        else:
            edgecolors.append("#f5efe2")
            linewidths.append(1.0)
        ax.text(x, y, employee.get("name", str(node_id)), ha="center", va="center", fontsize=7.2, color="#1f2937")
    ax.scatter(
        xs,
        ys,
        c=colors,
        s=sizes,
        cmap=plt.cm.YlOrRd,
        vmin=0,
        vmax=1,
        alpha=0.92,
        edgecolors=edgecolors,
        linewidths=linewidths,
    )
    ax.set_title(title, fontsize=12)
    ax.axis("off")
    plt.tight_layout()
    return fig


def draw_analysis_heatmap(snapshot, title, positions=None, figsize=(6.8, 4.8)):
    return _draw_snapshot_map(snapshot, title, "true_strain", positions=positions, figsize=figsize)


def draw_observed_risk_snapshot_map(snapshot, title, positions=None, figsize=(6.8, 4.8)):
    return _draw_snapshot_map(snapshot, title, "observed_risk", positions=positions, figsize=figsize)


def core_group_summary(snapshot):
    if not snapshot:
        return None
    role_keys = (
        "focal_employee",
        "hidden_strain_employee",
        "spillover_employee",
        "cluster_anchor",
    )
    roles = snapshot.get("scenario_roles", {})
    employees = {employee["id"]: employee for employee in snapshot.get("employees", [])}
    group_rows = [employees.get(roles.get(role_key)) for role_key in role_keys if roles.get(role_key) in employees]
    if not group_rows:
        return None
    names = [row.get("name", "Unknown") for row in group_rows]
    avg_true = sum(float(row.get("true_strain", 0.0)) for row in group_rows) / len(group_rows)
    focal_name = names[0]
    if len(names) == 1:
        names_text = focal_name
    elif len(names) == 2:
        names_text = f"{names[0]} and {names[1]}"
    else:
        names_text = f"{', '.join(names[:-1])}, and {names[-1]}"
    return {
        "focal_name": focal_name,
        "names_text": names_text,
        "avg_true": avg_true,
    }


def _observed_strain_label(value):
    if value >= 0.75:
        return "High"
    if value >= 0.45:
        return "Moderate"
    return "Low"


def _scenario_two_management_priority(row, roles):
    node_id = row.get("id")
    if node_id == roles.get("hidden_strain_employee"):
        if float(row.get("absorbed_workload", 0.0)) >= 0.45:
            return "Hidden risk"
        return "Monitor"
    if node_id == roles.get("focal_employee"):
        if float(row.get("observed_risk", 0.0)) >= 0.55:
            return "Visible issue"
        return "Monitor"
    if float(row.get("absorbed_workload", 0.0)) >= 0.30:
        return "Support"
    return "Watch"


def render_scenario_two_management_report(snapshot, title):
    if not snapshot:
        return
    roles = snapshot.get("scenario_roles", {})
    employees = snapshot.get("employees", [])
    order = [
        roles.get("focal_employee"),
        roles.get("hidden_strain_employee"),
        roles.get("spillover_employee"),
        roles.get("cluster_anchor"),
    ]
    employee_lookup = {row.get("id"): row for row in employees}
    ordered_rows = [employee_lookup[node_id] for node_id in order if node_id in employee_lookup]
    ordered_rows.extend(
        row for row in employees
        if row.get("id") not in {item.get("id") for item in ordered_rows}
    )

    table_rows = []
    for row in ordered_rows:
        observed = float(row.get("observed_risk", 0.0))
        workload = float(row.get("absorbed_workload", 0.0))
        role_name = str(row.get("scenario_role") or "").replace("_", " ").title()
        table_rows.append(
            {
                "name": row.get("name", "Unknown"),
                "role": role_name,
                "observed": f"{round(observed * 100)}% ({_observed_strain_label(observed)})",
                "workload": f"{round(workload * 100)}% ({visible_load_label(workload)})",
                "priority": _scenario_two_management_priority(row, roles),
            }
        )

    st.markdown(f'<div class="centered-results-text"><strong>{title}</strong></div>', unsafe_allow_html=True)
    table_html = [
        "<table style='width:100%; border-collapse:collapse; margin-top:0.5rem;'>",
        "<thead>",
        "<tr style='border-bottom:1px solid #e5dccb;'>",
        "<th style='text-align:left; padding:0.4rem 0.35rem; font-size:0.8rem; color:#6b7280;'>Person</th>",
        "<th style='text-align:left; padding:0.4rem 0.35rem; font-size:0.8rem; color:#6b7280;'>Role</th>",
        "<th style='text-align:left; padding:0.4rem 0.35rem; font-size:0.8rem; color:#6b7280;'>Observed Strain</th>",
        "<th style='text-align:left; padding:0.4rem 0.35rem; font-size:0.8rem; color:#6b7280;'>Absorbed Workload</th>",
        "<th style='text-align:left; padding:0.4rem 0.35rem; font-size:0.8rem; color:#6b7280;'>Management Read</th>",
        "</tr>",
        "</thead>",
        "<tbody>",
    ]
    for row in table_rows:
        table_html.extend(
            [
                "<tr style='border-bottom:1px solid #f1ead9;'>",
                f"<td style='padding:0.45rem 0.35rem; color:#1f2937; font-weight:600;'>{row['name']}</td>",
                f"<td style='padding:0.45rem 0.35rem; color:#4b5563;'>{row['role']}</td>",
                f"<td style='padding:0.45rem 0.35rem; color:#1f2937;'>{row['observed']}</td>",
                f"<td style='padding:0.45rem 0.35rem; color:#1f2937;'>{row['workload']}</td>",
                f"<td style='padding:0.45rem 0.35rem; color:#7c5a17; font-weight:600;'>{row['priority']}</td>",
                "</tr>",
            ]
        )
    table_html.extend(["</tbody>", "</table>"])
    st.markdown("".join(table_html), unsafe_allow_html=True)


def format_actions_for_analysis(snapshot):
    actions = snapshot.get("actions_taken", []) if snapshot else []
    if not actions:
        return "closed the week without taking a targeted intervention"
    parts = []
    for action in actions:
        label = action_label(action.get("type", ""))
        target = action.get("target")
        if isinstance(target, dict) and target.get("from") and target.get("to"):
            from_name = target["from"].get("name", "someone")
            to_name = target["to"].get("name", "someone else")
            parts.append(f"used {label} from {from_name} to {to_name}")
        elif isinstance(target, dict) and target.get("name"):
            parts.append(f"used {label} with {target['name']}")
        else:
            parts.append(f"used {label}")
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " together with " + parts[-1]


def format_current_week_action_log(action):
    action_type = action.get("action_type", "")
    target_name = action.get("target_name")
    if action_type == "reallocate_workload":
        explanation = action.get("explanation", {}) or {}
        from_name = explanation.get("from_name", "someone")
        to_name = explanation.get("to_name", "someone else")
        return f"You {action_past_tense(action_type).lower()} from {from_name} to {to_name}."
    if target_name and target_name != "Team":
        return f"You {action_past_tense(action_type).lower()} with {target_name}."
    if target_name == "Team":
        return f"You {action_past_tense(action_type).lower()}."
    return f"You {action_past_tense(action_type).lower()}."


def build_week_explanation_summary(snapshot, previous_snapshot):
    if not snapshot or not previous_snapshot:
        return []
    role_map = snapshot.get("scenario_roles", {})
    def row_for(node_id, source):
        for employee in source.get("employees", []):
            if employee.get("id") == node_id:
                return employee
        return None
    lines = []
    focal = role_map.get("focal_employee")
    hidden = role_map.get("hidden_strain_employee")
    focal_now = row_for(focal, snapshot)
    focal_prev = row_for(focal, previous_snapshot)
    hidden_now = row_for(hidden, snapshot)
    hidden_prev = row_for(hidden, previous_snapshot)
    if focal_now and focal_prev:
        focal_delta = float(focal_now.get("observed_risk", 0.0)) - float(focal_prev.get("observed_risk", 0.0))
        if focal_delta > 0.03:
            lines.append(f"Pressure around {focal_now['name']} grew more visible this week.")
        elif focal_delta < -0.03:
            lines.append(f"The visible pressure around {focal_now['name']} eased a little this week.")
        else:
            lines.append(f"The visible pressure around {focal_now['name']} stayed about the same.")
    if hidden_now and hidden_prev:
        hidden_delta = float(hidden_now.get("absorbed_workload", 0.0)) - float(hidden_prev.get("absorbed_workload", 0.0))
        if hidden_delta > 0.03:
            if snapshot.get("scenario") == "scenario_02":
                lines.append(f"More of the cleanup and spillover appeared to land with {hidden_now['name']}.")
            else:
                lines.append(f"More of the strain started to sit quietly with {hidden_now['name']}.")
        elif hidden_delta < -0.03:
            lines.append(f"Less of the background pressure appeared to rest with {hidden_now['name']}.")
    current_cluster = cluster_strain_avg(snapshot)
    previous_cluster = cluster_strain_avg(previous_snapshot)
    if current_cluster is not None and previous_cluster is not None:
        cluster_delta = current_cluster - previous_cluster
        if cluster_delta > 0.02:
            lines.append("The surrounding group ended the week carrying more pressure overall.")
        elif cluster_delta < -0.02:
            lines.append("The surrounding group ended the week on a steadier footing.")
    return lines[:3]


def _scenario_two_choice_key(checkpoint_id, role_id):
    return f"{checkpoint_id}_{role_id}"


def _scenario_two_selected_option(checkpoint_id, role_id):
    choices = st.session_state.get("scenario_02_workshop_choices", {})
    option_id = choices.get(_scenario_two_choice_key(checkpoint_id, role_id))
    checkpoint = next(
        (item for item in SCENARIO_02_WORKSHOP_MOCK["checkpoints"] if item["id"] == checkpoint_id),
        None,
    )
    if checkpoint is None:
        return None
    role_block = next((role for role in checkpoint.get("roles", []) if role["role_id"] == role_id), None)
    if role_block is None:
        return None
    return next((option for option in role_block["options"] if option["id"] == option_id), None)


def _scenario_two_checkpoint_scores():
    results = []
    for checkpoint in SCENARIO_02_WORKSHOP_MOCK["checkpoints"]:
        role_scores = {}
        for role_block in checkpoint.get("roles", []):
            selected = _scenario_two_selected_option(checkpoint["id"], role_block["role_id"])
            role_scores[role_block["role_id"]] = selected.get("score", 0) if selected else None
        results.append({
            "id": checkpoint["id"],
            "scores": role_scores,
        })
    return results


def _scenario_two_percent(score, max_score):
    if max_score <= 0:
        return 0
    return round((score / max_score) * 100)


def _scenario_two_review_metrics():
    checkpoint_scores = _scenario_two_checkpoint_scores()
    manager_values = []
    maya_values = []
    riley_values = []
    for item in checkpoint_scores:
        scores = item["scores"]
        if scores.get("manager") is not None:
            manager_values.append(scores["manager"])
        if scores.get("maya") is not None:
            maya_values.append(scores["maya"])
        if scores.get("riley") is not None:
            riley_values.append(scores["riley"])

    manager_total = sum(manager_values)
    maya_total = sum(maya_values)
    riley_total = sum(riley_values)
    manager_pct = _scenario_two_percent(manager_total, len(manager_values) * 3) if manager_values else 0
    maya_pct = _scenario_two_percent(maya_total, len(maya_values) * 3) if maya_values else 0
    riley_pct = _scenario_two_percent(riley_total, len(riley_values) * 3) if riley_values else 0
    team_pct = round((manager_pct * 0.4) + (maya_pct * 0.4) + (riley_pct * 0.2))

    aligned_checkpoint_indices = []
    for index, item in enumerate(checkpoint_scores):
        manager_score = item["scores"].get("manager")
        maya_score = item["scores"].get("maya")
        if manager_score is not None and maya_score is not None and manager_score >= 2 and maya_score >= 2:
            aligned_checkpoint_indices.append(index)
    if aligned_checkpoint_indices:
        timing = "Early alignment" if aligned_checkpoint_indices[0] == 0 else "Late alignment"
    else:
        timing = "No real alignment"

    first_pair = None
    last_pair = None
    for item in checkpoint_scores:
        if item["scores"].get("manager") is not None and item["scores"].get("maya") is not None:
            total = item["scores"]["manager"] + item["scores"]["maya"]
            if first_pair is None:
                first_pair = total
            last_pair = total
    if first_pair is None or last_pair is None:
        trajectory = "Drifted"
    elif last_pair >= 5 and first_pair >= 5:
        trajectory = "Strengthened"
    elif last_pair >= 5 and first_pair < 5:
        trajectory = "Recovered"
    elif last_pair < 5 and first_pair >= 5:
        trajectory = "Drifted"
    else:
        trajectory = "Hardened"

    if team_pct >= 75 and max(manager_pct, maya_pct) >= 75:
        ending = "aligned"
    elif manager_pct < 60 and maya_pct >= 60:
        ending = "misaligned_manager"
    elif manager_pct >= 60 and maya_pct < 60:
        ending = "misaligned_employee"
    else:
        ending = "total_misalignment"

    if team_pct >= 70 and riley_pct >= 50:
        human_cost = "Low"
    elif team_pct >= 45:
        human_cost = "Moderate"
    else:
        human_cost = "High"

    return {
        "manager_pct": manager_pct,
        "maya_pct": maya_pct,
        "riley_pct": riley_pct,
        "team_pct": team_pct,
        "timing": timing,
        "trajectory": trajectory,
        "ending": ending,
        "human_cost": human_cost,
    }


def _scenario_two_checkpoint_readout(checkpoint_id):
    scores = {
        role_id: (_scenario_two_selected_option(checkpoint_id, role_id) or {}).get("score")
        for role_id in ("manager", "riley", "maya")
    }
    known_scores = [score for score in scores.values() if score is not None]
    if not known_scores:
        return None
    avg_score = sum(known_scores) / len(known_scores)
    if avg_score >= 2.25:
        visible_friction = "Medium"
        hidden_carrying = "Low"
        team_alignment = "Strong"
        note = (
            "The team did not eliminate pressure, but it began to treat the right problem. Riley stayed "
            "in view without becoming the whole story, and there was less reliance on invisible rescue work."
        )
    elif avg_score >= 1.25:
        visible_friction = "Medium"
        hidden_carrying = "Medium"
        team_alignment = "Partial"
        note = (
            "Some of the deeper pattern became easier to see, even if the team did not fully act on it yet. "
            "Riley remained the loudest signal, while more of the real cost was being absorbed elsewhere."
        )
    else:
        visible_friction = "High"
        hidden_carrying = "High"
        team_alignment = "Weak"
        note = (
            "The team kept getting through the fortnight more by adaptation than alignment. Riley remained "
            "the easiest place to focus concern, while more of the cost quietly routed through Maya."
        )
    return {
        "visible_friction": visible_friction,
        "hidden_carrying": hidden_carrying,
        "team_alignment": team_alignment,
        "note": note,
    }


def _scenario_two_workshop_sequence():
    sequence = [{"type": "opening"}]
    for checkpoint in SCENARIO_02_WORKSHOP_MOCK["checkpoints"]:
        role_ids = [role["role_id"] for role in checkpoint.get("roles", [])]
        if "manager" in role_ids and len(role_ids) > 1:
            sequence.append({"type": "checkpoint_manager", "checkpoint_id": checkpoint["id"]})
            sequence.append({"type": "checkpoint_employee", "checkpoint_id": checkpoint["id"]})
            sequence.append({"type": "minutes", "checkpoint_id": checkpoint["id"]})
        else:
            sequence.append({"type": "checkpoint", "checkpoint_id": checkpoint["id"]})
        if len(checkpoint.get("roles", [])) > 1 and "manager" not in role_ids:
            sequence.append({"type": "minutes", "checkpoint_id": checkpoint["id"]})
    sequence.append({"type": "review"})
    return sequence


def _scenario_two_alignment_band(checkpoint_id):
    readout = _scenario_two_checkpoint_readout(checkpoint_id)
    if not readout:
        return "partial"
    label = readout["team_alignment"]
    if label == "Strong":
        return "strong"
    if label == "Weak":
        return "weak"
    return "partial"


def draw_scenario_two_alignment_triangle(band):
    band = band or "partial"
    positions = {
        "strong": {
            "Manager": (0.50, 0.18),
            "Riley": (0.34, 0.58),
            "Maya": (0.66, 0.56),
        },
        "partial": {
            "Manager": (0.48, 0.14),
            "Riley": (0.26, 0.66),
            "Maya": (0.72, 0.58),
        },
        "weak": {
            "Manager": (0.48, 0.10),
            "Riley": (0.18, 0.76),
            "Maya": (0.80, 0.62),
        },
    }
    palette = {
        "strong": {"line": "#4f7a52", "fill": "#dfe9dd", "node": "#2f5b33"},
        "partial": {"line": "#9a6b2f", "fill": "#efe5d3", "node": "#7a541e"},
        "weak": {"line": "#8e4b3d", "fill": "#f1ddd7", "node": "#733528"},
    }
    current_positions = positions.get(band, positions["partial"])
    colors = palette.get(band, palette["partial"])

    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    ordered = ["Manager", "Riley", "Maya", "Manager"]
    xs = [current_positions[label][0] for label in ordered]
    ys = [current_positions[label][1] for label in ordered]
    ax.fill(xs, ys, color=colors["fill"], alpha=0.95)
    ax.plot(xs, ys, color=colors["line"], linewidth=2.4)

    for label, (x, y) in current_positions.items():
        ax.scatter([x], [y], s=900, color=colors["node"], edgecolors="#fffdf8", linewidths=2.0, zorder=3)
        ax.text(x, y, label, color="#fffdf8", ha="center", va="center", fontsize=10, fontweight="bold", zorder=4)

    ax.set_xlim(0.05, 0.95)
    ax.set_ylim(0.85, 0.0)
    ax.axis("off")
    ax.set_title("Alignment At The End Of The Fortnight", fontsize=12, color="#2f2410")
    plt.tight_layout()
    return fig


def _render_scenario_two_option_block(checkpoint_id, role_block):
    role_key = _scenario_two_choice_key(checkpoint_id, role_block["role_id"])
    options = role_block["options"]
    option_labels = {
        f"{option['label']}": option["id"]
        for option in options
    }
    current_choice = st.session_state.get("scenario_02_workshop_choices", {}).get(role_key, options[0]["id"])
    if current_choice not in [option["id"] for option in options]:
        current_choice = options[0]["id"]
    selected_label = next(
        label for label, option_id in option_labels.items()
        if option_id == current_choice
    )
    chosen_label = st.radio(
        role_block["title"],
        list(option_labels.keys()),
        index=list(option_labels.keys()).index(selected_label),
        key=f"radio_{role_key}",
    )
    selected_option = next(option for option in options if option["id"] == option_labels[chosen_label])
    st.session_state.scenario_02_workshop_choices[role_key] = selected_option["id"]
    st.caption(role_block["prompt"])
    st.markdown(
        f"<div class='resolution-note'>{selected_option['body']}</div>",
        unsafe_allow_html=True,
    )
    if selected_option.get("intent"):
        st.caption(f"Intent: {selected_option['intent']}")


def render_scenario_two_workshop_mock():
    st.session_state.setdefault("scenario_02_workshop_step", 0)
    st.session_state.setdefault("scenario_02_workshop_choices", {})
    step = st.session_state["scenario_02_workshop_step"]
    checkpoints = {
        checkpoint["id"]: checkpoint
        for checkpoint in SCENARIO_02_WORKSHOP_MOCK["checkpoints"]
    }
    sequence = _scenario_two_workshop_sequence()
    total_steps = len(sequence)
    current_step = sequence[step]

    if current_step["type"] == "opening":
        st.markdown('<div class="shell-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-title">{SCENARIO_02_WORKSHOP_MOCK["title"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="hero-subtitle">{SCENARIO_02_WORKSHOP_MOCK["premise"]}</div>',
            unsafe_allow_html=True,
        )
        st.write(SCENARIO_02_WORKSHOP_MOCK["instruction"])
        st.markdown('<hr class="subtle-section-break" />', unsafe_allow_html=True)
        for role in SCENARIO_02_WORKSHOP_MOCK["roles"]:
            st.markdown(
                f"<div class='employee-summary'><strong>{role['name']}</strong><br>{role['summary']}</div>",
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Begin Workshop", type="primary", width="stretch"):
            st.session_state["scenario_02_workshop_step"] = 1
            st.rerun()
        return

    if current_step["type"] in {"checkpoint", "checkpoint_manager", "checkpoint_employee"}:
        checkpoint = checkpoints[current_step["checkpoint_id"]]
        step_type = current_step["type"]
        if step_type == "checkpoint_manager":
            role_blocks = [role for role in checkpoint["roles"] if role["role_id"] == "manager"]
            kicker = checkpoint["kicker"]
            heading = checkpoint["heading"]
            narrative = checkpoint["narrative"]
            signals = checkpoint["signals"]
        elif step_type == "checkpoint_employee":
            role_blocks = [role for role in checkpoint["roles"] if role["role_id"] != "manager"]
            kicker = "Employee Response"
            heading = f"{checkpoint['heading']}: How The Team Responds"
            narrative = (
                "The manager has set the direction for the next fortnight. Riley and Maya now respond "
                "from inside the pressure they are actually carrying."
            )
            signals = [
                "Riley is looking for relief in whatever form still feels available.",
                "Maya has to decide whether to keep carrying the hidden work or make it discussable.",
                "What the team does next will shape how the fortnight actually lands.",
            ]
        else:
            role_blocks = checkpoint["roles"]
            kicker = checkpoint["kicker"]
            heading = checkpoint["heading"]
            narrative = checkpoint["narrative"]
            signals = checkpoint["signals"]

        st.markdown('<div class="shell-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='section-label'>{kicker}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='title-band-main'>{heading}</div>", unsafe_allow_html=True)
        st.write(narrative)
        st.markdown("<ul class='signal-list'>" + "".join(f"<li>{signal}</li>" for signal in signals) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if len(role_blocks) == 1:
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            _render_scenario_two_option_block(checkpoint["id"], role_blocks[0])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            columns = st.columns(len(role_blocks))
            for column, role_block in zip(columns, role_blocks):
                with column:
                    _render_scenario_two_option_block(checkpoint["id"], role_block)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="centered-results-text"><strong>Reflection</strong></div>', unsafe_allow_html=True)
        for prompt in checkpoint["facilitator"]:
            st.markdown(f"<div class='centered-results-text'>{prompt}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        back_col, next_col = st.columns(2)
        if back_col.button("Back", width="stretch", disabled=step == 1):
            st.session_state["scenario_02_workshop_step"] = max(0, step - 1)
            st.rerun()
        next_label = "Continue" if step_type == "checkpoint_manager" else "Lock Choices"
        if step_type == "checkpoint":
            next_label = "Lock Choices"
        if next_col.button(next_label, type="primary", width="stretch"):
            st.session_state["scenario_02_workshop_step"] = min(total_steps - 1, step + 1)
            st.rerun()
        return

    if current_step["type"] == "minutes":
        checkpoint = checkpoints[current_step["checkpoint_id"]]
        readout = _scenario_two_checkpoint_readout(checkpoint["id"])
        st.markdown('<div class="shell-card">', unsafe_allow_html=True)
        st.markdown('<div class="centered-results-text"><strong>Fortnight Minutes</strong></div>', unsafe_allow_html=True)
        st.markdown("<div class='centered-miniheader'>What happened after the meeting</div>", unsafe_allow_html=True)
        minutes_band = _scenario_two_alignment_band(checkpoint["id"])
        minutes_copy = checkpoint.get("minutes", {}).get(minutes_band, {})
        minutes_col, visual_col = st.columns([1.25, 1])
        with minutes_col:
            sections = [
                ("Agreed in the meeting", minutes_copy.get("agreed", "")),
                ("What became visible", minutes_copy.get("visible", "")),
                ("What was carried quietly", minutes_copy.get("quiet", "")),
                ("What this meant for the demo", minutes_copy.get("meaning", "")),
            ]
            for label, body in sections:
                if body:
                    st.markdown(
                        f"<div class='employee-summary'><strong>{label}</strong><br>{body}</div>",
                        unsafe_allow_html=True,
                    )
        with visual_col:
            st.pyplot(draw_scenario_two_alignment_triangle(minutes_band), width="stretch")
        if readout:
            readout_cols = st.columns(3)
            labels = [
                ("Visible friction", readout["visible_friction"]),
                ("Hidden carrying", readout["hidden_carrying"]),
                ("Team alignment", readout["team_alignment"]),
            ]
            for column, (label, value) in zip(readout_cols, labels):
                with column:
                    st.markdown(
                        f"<div class='employee-summary'><strong>{label}</strong><br>{value}</div>",
                        unsafe_allow_html=True,
                    )
        st.markdown('</div>', unsafe_allow_html=True)

        back_col, next_col = st.columns(2)
        if back_col.button("Back", width="stretch"):
            st.session_state["scenario_02_workshop_step"] = max(0, step - 1)
            st.rerun()
        next_label = "Review The Demo" if sequence[step + 1]["type"] == "review" else "Continue"
        if next_col.button(next_label, type="primary", width="stretch"):
            st.session_state["scenario_02_workshop_step"] = step + 1
            st.rerun()
        return

    metrics = _scenario_two_review_metrics()
    review = SCENARIO_02_WORKSHOP_MOCK["review_copy"][metrics["ending"]]
    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown('<div class="centered-results-text"><strong>Client Demo Review</strong></div>', unsafe_allow_html=True)
    st.markdown(f"<h2 class='centered-outcome'>{review['title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='centered-results-text'>{review['outcome']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    score_cols = st.columns(4)
    score_items = [
        ("Riley Alignment", f"{metrics['riley_pct']}%"),
        ("Maya Alignment", f"{metrics['maya_pct']}%"),
        ("Manager Alignment", f"{metrics['manager_pct']}%"),
        ("Team Alignment", f"{metrics['team_pct']}%"),
    ]
    for column, (label, value) in zip(score_cols, score_items):
        with column:
            st.markdown(
                f"<div class='employee-summary'><strong>{label}</strong><br>{value}</div>",
                unsafe_allow_html=True,
            )

    supporting_cols = st.columns(3)
    supporting_items = [
        ("Timing", metrics["timing"]),
        ("Human Cost", metrics["human_cost"]),
        ("Trajectory", metrics["trajectory"]),
    ]
    for column, (label, value) in zip(supporting_cols, supporting_items):
        with column:
            st.markdown(
                f"<div class='employee-summary'><strong>{label}</strong><br>{value}</div>",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    for line in [review["manager"], review["maya"], review["riley"], review["shared"], SCENARIO_02_WORKSHOP_MOCK["review_copy"]["riley_note"]]:
        st.markdown(f"<div class='centered-results-text'>{line}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Back", width="stretch"):
        st.session_state["scenario_02_workshop_step"] = max(0, step - 1)
        st.rerun()


def render_header(vm, game):
    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{PRODUCT_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-subtitle">{PRODUCT_SUBTITLE}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="title-band">
            <div class="title-band-main">{game.get_scenario_overview()['label']}</div>
            <div class="title-band-week">{vm.week_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    combined_briefing = vm.briefing_text
    if vm.briefing_aside:
        combined_briefing = f"{combined_briefing} {vm.briefing_aside}".strip()
    st.write(combined_briefing)
    st.markdown('</div>', unsafe_allow_html=True)


def render_evidence(vm, game):
    employee_rows = vm.employee_rows
    if not employee_rows:
        return

    available_ids = {row["id"] for row in employee_rows}
    default_employee_id = None
    if game.scenario == "scenario_02":
        default_employee_id = game.get_scenario_role_node_id("focal_employee")
    if st.session_state.evidence_employee_id not in available_ids:
        st.session_state.evidence_employee_id = (
            default_employee_id if default_employee_id in available_ids else employee_rows[0]["id"]
        )

    selected_row = next(
        row for row in employee_rows if row["id"] == st.session_state.evidence_employee_id
    )
    employee_options = {
        f"{row['name']} ({row['role']})": row["id"]
        for row in employee_rows
    }
    selected_label = next(
        label for label, row_id in employee_options.items()
        if row_id == st.session_state.evidence_employee_id
    )

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="centered-subheader">What You Can See</h3>', unsafe_allow_html=True)
    if game.scenario == "scenario_02":
        st.pyplot(draw_visible_friction_chart(employee_rows, st.session_state.evidence_employee_id), width="stretch")
    else:
        st.pyplot(draw_observed_risk_chart(employee_rows, st.session_state.evidence_employee_id), width="stretch")
    chosen_label = st.selectbox(
        "Choose a team member to inspect",
        list(employee_options.keys()),
        index=list(employee_options.keys()).index(selected_label),
        key="evidence_employee_select",
    )
    st.session_state.evidence_employee_id = employee_options[chosen_label]
    selected_row = next(
        row for row in employee_rows if row["id"] == st.session_state.evidence_employee_id
    )
    st.markdown('</div>', unsafe_allow_html=True)

    lower_left, lower_right = st.columns([1.2, 1])
    with lower_left:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        profile = character_profile(selected_row["name"])
        live_status = (
            f"If I were calling it quickly, I’d say {selected_row['name']} looks {risk_read(selected_row['risk_label'])} right now. "
            f"I’m noticing {format_warning_signs(selected_row['warning_signs']).lower()}, "
            f"and their engagement feels {selected_row['engagement_hint'].lower()}."
        )
        pressure_status = (
            f"The pressure clue I’d give you is that {selected_row.get('pressure_clue', 'there is no clear pressure clue yet').lower()}. "
            f"Background load looks {visible_load_label(float(selected_row.get('absorbed_workload_value', 0.0))).lower()}, "
            f"and {selected_row.get('workload_clue', 'there is no clear workload clue yet').lower()}."
        )
        coordination_status = (
            f"On coordination, what stands out is that {selected_row.get('dependency_clue', 'no clear coordination clue yet').lower()}."
        )
        st.markdown(
            f"""
            <div class="employee-panel">
                <div class="employee-name">{selected_row['name']}</div>
                <div class="employee-role">{selected_row['role']}</div>
                <div class="employee-summary">{profile.get('team_lead_profile', 'This person is part of the launch group and their pattern may become clearer as the weeks unfold.')}</div>
                <div class="employee-note">{live_status}</div>
                <div class="employee-note">{pressure_status}</div>
                <div class="employee-note">{coordination_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with lower_right:
        if game.scenario == "scenario_02":
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.pyplot(draw_workload_distribution_chart(employee_rows, st.session_state.evidence_employee_id), width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)
        elif "network_graph" in vm.evidence_modules:
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.pyplot(draw_network_chart(game), width="stretch")
            snapshot = build_opening_snapshot(game)
            summary = core_group_summary(snapshot)
            if summary:
                st.markdown(
                    (
                        f'<div class="centered-results-text"><strong>{summary["focal_name"]} and the working group</strong> '
                        f'are highlighted on the chart.</div>'
                    ),
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)


def render_decision_space(vm, game):
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="centered-subheader">Choose What To Do</h3>', unsafe_allow_html=True)

    intent_options = [group["intent"] for group in vm.action_groups]
    selected_intent = st.selectbox("What do you intend to do?", intent_options, key="selected_intent")
    intent_group = next(group for group in vm.action_groups if group["intent"] == selected_intent)

    action_options = {
        f"{action_label(item['key'])} · {int(item['cost'])} energy": item["key"]
        for item in intent_group["actions"]
    }
    selected_action_label = st.selectbox("How do you want to do it?", list(action_options.keys()), key="selected_action")
    selected_action = action_options[selected_action_label]

    employee_rows = vm.employee_rows
    employee_labels = {f"{row['name']} ({row['role']})": row["id"] for row in employee_rows}
    label_for_id = {row["id"]: f"{row['name']} ({row['role']})" for row in employee_rows}
    focal_id = game.get_scenario_role_node_id("focal_employee")
    hidden_id = game.get_scenario_role_node_id("hidden_strain_employee")
    default_target_label = label_for_id.get(focal_id)
    default_from_label = label_for_id.get(hidden_id) or default_target_label
    selected_employee_label = None
    selected_from_label = None
    selected_to_label = None
    needs_target = selected_action not in TEAM_WIDE_ACTIONS and selected_action != "do_nothing"
    if selected_action == "reallocate_workload":
        target_labels = list(employee_labels.keys())
        from_index = target_labels.index(default_from_label) if default_from_label in target_labels else 0
        selected_from_label = st.selectbox(
            "Take work from whom?",
            target_labels,
            index=from_index,
            key="selected_employee_from",
        )
        to_options = [label for label in target_labels if label != selected_from_label]
        to_default = default_target_label if default_target_label in to_options else (to_options[0] if to_options else None)
        to_index = to_options.index(to_default) if to_default in to_options else 0
        selected_to_label = st.selectbox(
            "Give work to whom?",
            to_options,
            index=to_index,
            key="selected_employee_to",
        )
    elif needs_target:
        target_options = list(employee_labels.keys())
        target_index = target_options.index(default_target_label) if default_target_label in target_options else 0
        selected_employee_label = st.selectbox(
            "Who will be the target?",
            target_options,
            index=target_index,
            key="selected_employee",
        )
        if selected_action in {"group_mediation", "clarify_roles_and_handoffs"}:
            target_id = employee_labels[selected_employee_label]
            affected = game.get_cluster_neighbor_names(target_id)
            if affected:
                st.caption(f"This will also affect: {', '.join(affected)}")
            else:
                st.caption("This currently has no nearby colleagues linked in this view.")

    energy = game.get_energy_status()
    st.markdown(
        f"**Energy cost:** {int(action_cost(selected_action))}  \n"
        f"**Current energy:** {int(energy['current'])} / {int(energy['max'])}"
    )

    for action in game.get_current_week_action_summaries():
        st.write(format_current_week_action_log(action))

    action_col, week_col = st.columns(2)
    if action_col.button("Apply Action", width="stretch", key="apply_action_button"):
        target = None
        if selected_action == "reallocate_workload":
            target = {
                "from": employee_labels[selected_from_label],
                "to": employee_labels[selected_to_label],
            }
        elif needs_target:
            target = employee_labels[selected_employee_label]
        if selected_action != "do_nothing":
            game.apply_player_action({"type": selected_action, "target": target})
        st.session_state.game = game
        st.rerun()

    if week_col.button("End Week", type="primary", width="stretch"):
        game.end_week()
        st.session_state.game = game
        st.session_state.pending_week_review = not game.game_over
        clear_diagnosis_box()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_week_resolution(snapshot, previous_snapshot):
    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="centered-outcome">End of Week {snapshot["week"]}</h2>', unsafe_allow_html=True)

    game = st.session_state.game
    benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
    benchmark_latest = _analysis_snapshot_for_week(benchmark_history, snapshot["week"])
    week_report = scenario_week_end_report(game, snapshot, previous_snapshot, benchmark_history, benchmark_latest)
    if week_report is None:
        week_report = build_end_of_week_report(snapshot, previous_snapshot)
    if week_report:
        for line in week_report:
            st.markdown(f'<div class="centered-results-text">{line}</div>', unsafe_allow_html=True)

    if previous_snapshot:
        shared_positions = _shared_analysis_positions(previous_snapshot, snapshot)
        before_col, after_col = st.columns(2)
        with before_col:
            st.pyplot(draw_observed_risk_snapshot_map(previous_snapshot, "Before", positions=shared_positions), width="stretch")
        with after_col:
            st.pyplot(draw_observed_risk_snapshot_map(snapshot, "After", positions=shared_positions), width="stretch")
        if game.scenario == "scenario_01":
            summary = core_group_summary(snapshot)
            if summary:
                st.markdown(
                    (
                        f'<div class="centered-results-text"><strong>{summary["focal_name"]} and the working group</strong> '
                        f'are highlighted on the charts.</div>'
                    ),
                    unsafe_allow_html=True,
                )

    if st.button("Continue", type="primary", width="stretch"):
        st.session_state.pending_week_review = False
        st.session_state.review_snapshot_week = None
        clear_diagnosis_box()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_final_score(game):
    history = game.get_analysis_history()
    benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
    latest_snapshot = history[-1] if history else None
    player_avg = cluster_strain_avg(latest_snapshot) if latest_snapshot else None
    benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)
    hidden_comparison = (
        scenario_two_hidden_strain_comparison(latest_snapshot, benchmark_latest)
        if game.scenario == "scenario_02"
        else None
    )

    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="centered-outcome">Final Score</h2>', unsafe_allow_html=True)
    if game.scenario == "scenario_02" and hidden_comparison is not None:
        st.markdown(
            f'<div class="summary-impact">{hidden_comparison["hidden_name"]} actual end strain: {round(hidden_comparison["player_hidden_strain"] * 100)}%</div>',
            unsafe_allow_html=True,
        )
    elif player_avg is not None:
        st.markdown(
            f'<div class="summary-impact">Core-group strain by launch: {round(player_avg * 100)}%</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    scenario_targets = {
        "scenario_01": 0.30,
    }
    target_avg = scenario_targets.get(game.scenario)
    if game.scenario == "scenario_02" and hidden_comparison is not None:
        target_line = (
            f'A good target for this scenario is {round(SCENARIO_02_HIDDEN_STRAIN_TARGET * 100)}% or lower. '
            'That gives you a clear number to aim for next run.'
        )
        lesson_line = None
    elif player_avg is not None and target_avg is not None:
        if player_avg <= target_avg + 0.005:
            target_line = (
                f'This is better than the target score of {round(target_avg * 100)}% or lower. '
                'Well done.'
            )
            lesson_line = None
        else:
            target_line = (
                f'A good target for this scenario is {round(target_avg * 100)}% or lower. '
                'That gives you a clear number to aim for next run.'
            )
            lesson_line = None
    elif player_avg is not None:
        target_line = (
            'Lower is better, so this gives you a clear number to improve on next run.'
        )
        lesson_line = None
    else:
        target_line = 'There was not enough history to calculate a final score for this run.'
        lesson_line = None
    st.markdown(f'<div class="centered-results-text">{target_line}</div>', unsafe_allow_html=True)
    if lesson_line:
        st.markdown(f'<div class="centered-results-text">{lesson_line}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Back To Analysis", width="stretch"):
        st.session_state.results_view = "analysis"
        st.rerun()


def render_end_screen(game):
    history = game.get_analysis_history()
    latest = history[-1] if history else {}
    benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
    benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)
    hidden_strain_comparison = (
        scenario_two_hidden_strain_comparison(latest, benchmark_latest)
        if game.scenario == "scenario_02"
        else None
    )
    summary_branch = determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest)
    summary_title = determine_summary_title(summary_branch, latest)
    summary_reinforcing = False
    player_high_strain = core_group_high_strain_count(latest) if latest else 0
    benchmark_high_strain = core_group_high_strain_count(benchmark_latest) if benchmark_latest else 0
    results_view = st.session_state.get("results_view", "summary")

    if latest and benchmark_latest and player_high_strain <= benchmark_high_strain:
        if game.scenario == "scenario_02":
            dependency_comparison = scenario_two_peak_dependency_comparison(history, benchmark_history)
            if (
                latest.get("scenario_outcome_tier") == "Succeed"
                and dependency_comparison
                and dependency_comparison["player_peak_hidden_load"] <= dependency_comparison["benchmark_peak_hidden_load"] + 0.05
            ):
                summary_reinforcing = True
        else:
            end_comparison = cluster_strain_improvement(latest, benchmark_latest)
            if (
                latest.get("scenario_outcome_tier") == "Succeed"
                and end_comparison
                and end_comparison["player_cluster_avg"] <= end_comparison["benchmark_cluster_avg"] * 1.15
            ):
                summary_reinforcing = True

    if results_view == "summary":
        authored_end_copy = scenario_end_screen_copy(game, history, latest, benchmark_history, benchmark_latest)
        if authored_end_copy:
            st.markdown('<div class="shell-card">', unsafe_allow_html=True)
            debrief_label = "End of Demo Debrief" if game.scenario == "scenario_02" else "End of Launch Debrief"
            st.markdown(f'<div class="centered-results-text"><strong>{debrief_label}</strong></div>', unsafe_allow_html=True)
            st.markdown(f'<h2 class="centered-outcome">{authored_end_copy["outcome"]}</h2>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="shell-card">', unsafe_allow_html=True)
            for line in (
                authored_end_copy.get("management_pattern"),
                authored_end_copy.get("what_you_did_well"),
                authored_end_copy.get("what_limited_the_result"),
                authored_end_copy.get("kpi_review"),
                authored_end_copy.get("development_point"),
            ):
                if line:
                    st.markdown(f'<div class="centered-results-text">{line}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="shell-card">', unsafe_allow_html=True)
            st.markdown(f'<h2 class="centered-outcome">{summary_title}</h2>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if not authored_end_copy and player_high_strain > benchmark_high_strain:
            if summary_title == "The situation spiralled.":
                if game.scenario == "scenario_02":
                    hidden_name = (hidden_strain_comparison or {}).get("hidden_name", "Maya")
                    player_hidden = round(((hidden_strain_comparison or {}).get("player_hidden_strain", 0.0)) * 100)
                    benchmark_hidden = round(((hidden_strain_comparison or {}).get("benchmark_hidden_strain", 0.0)) * 100)
                    impact_text = (
                        f"The demo pressure kept spilling outward because {hidden_name} was left carrying too much of it."
                        f"<br><br>{hidden_name} finished at {player_hidden}% actual strain. With a stronger response, that could have been closer to {benchmark_hidden}%."
                    )
                else:
                    impact_text = (
                        "The launch pressure kept spreading through the surrounding pocket of the team."
                        f'<br><br>With a stronger response, {benchmark_high_strain} {people_label(benchmark_high_strain)} in the core group could have ended under high strain instead of {player_high_strain}.'
                    )
            else:
                if game.scenario == "scenario_02":
                    hidden_name = (hidden_strain_comparison or {}).get("hidden_name", "Maya")
                    player_hidden = round(((hidden_strain_comparison or {}).get("player_hidden_strain", 0.0)) * 100)
                    benchmark_hidden = round(((hidden_strain_comparison or {}).get("benchmark_hidden_strain", 0.0)) * 100)
                    impact_text = (
                        f"The demo got through, but {hidden_name} still ended the run carrying too much pressure."
                        f"<br><br>{hidden_name}'s actual end strain was {player_hidden}%. With a stronger response, that could have been closer to {benchmark_hidden}%."
                    )
                else:
                    impact_text = (
                        f"The launch got through, but {player_high_strain} {people_label(player_high_strain)} in the core group were still carrying too much pressure."
                        f'<br><br>With a stronger response, that could have been {benchmark_high_strain}.'
                    )
            st.markdown('<div class="shell-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="summary-impact">{impact_text}</div>',
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        elif not authored_end_copy and latest and benchmark_latest:
            end_comparison = cluster_strain_improvement(latest, benchmark_latest)
            if summary_reinforcing:
                if game.scenario == "scenario_02":
                    impact_text = (
                        "The demo held together because you identified the core problem early and intervened effectively."
                        "<br><br>Well done."
                    )
                else:
                    impact_text = (
                        "The launch held together because you identified the core problem early and intervened effectively."
                        "<br><br>Well done."
                    )
                st.markdown('<div class="shell-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="summary-impact">{impact_text}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)
            elif end_comparison and end_comparison["benchmark_cluster_avg"] + 0.02 < end_comparison["player_cluster_avg"]:
                if game.scenario == "scenario_02":
                    hidden_name = (hidden_strain_comparison or {}).get("hidden_name", "Maya")
                    player_hidden = round(((hidden_strain_comparison or {}).get("player_hidden_strain", 0.0)) * 100)
                    benchmark_hidden = round(((hidden_strain_comparison or {}).get("benchmark_hidden_strain", 0.0)) * 100)
                    impact_text = (
                        f"The demo got through, but {hidden_name} still ended the run carrying more strain than she needed to."
                        f"<br><br>{hidden_name}'s actual end strain was {player_hidden}%. A stronger response would have brought that closer to {benchmark_hidden}%."
                    )
                else:
                    impact_text = (
                        "The launch got through, but the core group was still carrying more strain than it needed to."
                        "<br><br>A stronger response would have left the group in a better place."
                    )
                st.markdown('<div class="shell-card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="summary-impact">{impact_text}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Analyse Run", type="primary", width="stretch"):
            st.session_state.results_view = "analysis"
            st.session_state.analysis_week = 0
            st.rerun()
        return

    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="centered-outcome">Management Review</h2>', unsafe_allow_html=True)
    authored_overall = scenario_analysis_copy(game, latest, "overall", history, benchmark_history, benchmark_latest)
    st.markdown(
        f'<div class="centered-outcome">{(authored_overall or {}).get("overall_assessment", summary_title)}</div>',
        unsafe_allow_html=True,
    )
    if authored_overall:
        for key in ("management_pattern", "kpi_review"):
            line = authored_overall.get(key)
            if line:
                st.markdown(f'<div class="centered-results-text">{line}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    opening_snapshot = build_opening_snapshot(game)
    review_weeks = [0] + [snapshot["week"] for snapshot in history]
    if not review_weeks:
        return
    if st.session_state.analysis_week not in review_weeks:
        st.session_state.analysis_week = 0

    selected_week = st.session_state.analysis_week
    selected_snapshot = opening_snapshot if selected_week == 0 else next(
        snapshot for snapshot in history if snapshot["week"] == selected_week
    )
    previous_analysis_snapshot = None
    if selected_week > 0:
        previous_analysis_snapshot = opening_snapshot if selected_week == 1 else next(
            snapshot for snapshot in history if snapshot["week"] == selected_week - 1
        )
    benchmark_snapshot = opening_snapshot if selected_week == 0 else _analysis_snapshot_for_week(benchmark_history, selected_week)
    previous_benchmark_snapshot = None
    if selected_week > 0:
        previous_benchmark_snapshot = opening_snapshot if selected_week == 1 else _analysis_snapshot_for_week(benchmark_history, selected_week - 1)
    shared_positions = _shared_analysis_positions(selected_snapshot, benchmark_snapshot)

    st.markdown('<div class="results-column">', unsafe_allow_html=True)
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    left_panel, right_panel = st.columns(2)
    with left_panel:
        if selected_snapshot:
            if game.scenario == "scenario_02":
                st.pyplot(draw_riley_maya_observed_vs_actual_chart(selected_snapshot, "Your Run"), width="stretch")
            else:
                st.pyplot(draw_observed_risk_snapshot_map(selected_snapshot, "Your Run", positions=shared_positions), width="stretch")
    with right_panel:
        if benchmark_snapshot:
            if game.scenario == "scenario_02":
                st.pyplot(draw_riley_maya_observed_vs_actual_chart(benchmark_snapshot, "Recommended Run"), width="stretch")
            else:
                st.pyplot(draw_observed_risk_snapshot_map(benchmark_snapshot, "Recommended Run", positions=shared_positions), width="stretch")
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
    current_index = review_weeks.index(selected_week)
    if nav_left.button("Previous Week", width="stretch", disabled=current_index == 0):
        if current_index > 0:
            st.session_state.analysis_week = review_weeks[current_index - 1]
            st.rerun()
    nav_mid.markdown(
        f'<div class="centered-results-text"><strong>Reviewing {analysis_step_label(selected_week)}</strong></div>',
        unsafe_allow_html=True,
    )
    next_label = "Final Score" if current_index == len(review_weeks) - 1 else "Next Week"
    if nav_right.button(next_label, width="stretch"):
        if current_index < len(review_weeks) - 1:
            st.session_state.analysis_week = review_weeks[current_index + 1]
            st.rerun()
        else:
            st.session_state.results_view = "score"
            st.rerun()
    if selected_snapshot:
        summary = core_group_summary(selected_snapshot)
        if summary:
            if game.scenario == "scenario_02":
                roles = selected_snapshot.get("scenario_roles", {})
                employees = {employee["id"]: employee for employee in selected_snapshot.get("employees", [])}
                hidden_row = employees.get(roles.get("hidden_strain_employee"))
                hidden_name = (hidden_row or {}).get("name", "Maya")
                hidden_true = float((hidden_row or {}).get("true_strain", 0.0))
                st.markdown(
                    (
                        f'<div class="centered-results-text">{hidden_name}\'s true strain at this point '
                        f'was {round(hidden_true * 100)}%.</div>'
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    (
                        f'<div class="centered-results-text"><strong>{summary["focal_name"]} and the working group</strong> '
                        f'are highlighted on the chart. '
                        f'Their average true strain at this point was {round(summary["avg_true"] * 100)}%.</div>'
                    ),
                    unsafe_allow_html=True,
                )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    if selected_week == 0:
        opening_copy = recommended_analysis_copy(game, week=0)
        if opening_copy:
            st.markdown(
                f'<div class="centered-results-text">{opening_copy}</div>',
                unsafe_allow_html=True,
            )
    elif selected_snapshot and benchmark_snapshot:
        authored_week_copy = scenario_analysis_copy(
            game,
            selected_snapshot,
            selected_week,
            history,
            benchmark_history,
            benchmark_latest,
        )
        if authored_week_copy:
            analysis_keys = [
                "what_the_situation_called_for",
                "how_your_choice_landed",
                "assessment_from_your_starting_point",
                "what_it_meant_for_your_trajectory",
            ]
            if selected_week == 1:
                analysis_keys = [
                    key for key in analysis_keys
                    if key != "assessment_from_your_starting_point"
                ]
            for key in analysis_keys:
                line = authored_week_copy.get(key)
                if line:
                    st.markdown(
                        f'<div class="centered-results-text">{line}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            teaching_copy = recommended_analysis_copy(
                game,
                snapshot=selected_snapshot,
                week=selected_week,
                history=history,
                benchmark_snapshot=benchmark_snapshot,
                force_reinforcing=summary_reinforcing,
            )

            if teaching_copy:
                st.markdown(
                    f'<div class="centered-results-text">{teaching_copy}</div>',
                    unsafe_allow_html=True,
                )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Back", width="stretch"):
        st.session_state.results_view = "summary"
        st.rerun()


if not TEST_MODE:
    ensure_state()
    game = st.session_state.game
    vm = build_weekly_view_model(game)
    scenario_key = st.session_state.get("selected_scenario", DEFAULT_SCENARIO_KEY)
    experience_mode = st.session_state.get("experience_mode", "simulation")

    if SHOW_SIDEBAR:
        st.sidebar.title("Run Controls")
        st.sidebar.write(PACK_STATUS_TEXT)
        selected_scenario_key = st.session_state.get("selected_scenario", DEFAULT_SCENARIO_KEY)
        experience_mode = st.session_state.get("experience_mode", "simulation")

        st.sidebar.markdown("**Simulations**")
        for scenario_key in SIMULATION_SCENARIOS:
            label = SCENARIOS[scenario_key].label
            is_selected = selected_scenario_key == scenario_key and experience_mode == "simulation"
            button_label = f"{'• ' if is_selected else ''}{label}"
            if st.sidebar.button(button_label, width="stretch", key=f"nav_sim_{scenario_key}"):
                if selected_scenario_key != scenario_key or experience_mode != "simulation":
                    reset_game(scenario_key, "simulation")
                    st.rerun()
        st.sidebar.markdown("<div style='height: 0.9rem;'></div>", unsafe_allow_html=True)

        st.sidebar.markdown("**Workshop**")
        for scenario_key in WORKSHOP_SCENARIOS:
            label = SCENARIO_02_WORKSHOP_TITLE if scenario_key == "scenario_02" else SCENARIOS[scenario_key].label
            is_selected = selected_scenario_key == scenario_key and experience_mode == "workshop"
            button_label = f"{'• ' if is_selected else ''}{label}"
            if st.sidebar.button(button_label, width="stretch", key=f"nav_workshop_{scenario_key}"):
                if selected_scenario_key != scenario_key or experience_mode != "workshop":
                    reset_game(scenario_key, "workshop")
                    st.rerun()
        st.sidebar.markdown("---")
        if selected_scenario_key == "scenario_01" and experience_mode == "simulation":
            st.sidebar.markdown("**Relevant Runs**")
            if st.sidebar.button("Spiralled", width="stretch", key="scenario_01_path_spiralled"):
                load_demo_run("scenario_01", "none", desired_tier="Fail")
                st.rerun()
            if st.sidebar.button("Supported Jordan Only", width="stretch", key="scenario_01_path_high_strain"):
                load_demo_run_for_explicit_path("scenario_01", "relieve", "high_strain_count")
                st.rerun()
            if st.sidebar.button("Late Shift", width="stretch", key="scenario_01_path_more_strain"):
                load_demo_run_for_explicit_path("scenario_01", "mixed", "more_strain_than_needed")
                st.rerun()
            if st.sidebar.button("Gold Run", width="stretch", key="scenario_01_path_well_done"):
                load_demo_run_for_explicit_path("scenario_01", "recommended", "well_done")
                st.rerun()
            st.sidebar.markdown("---")
        if selected_scenario_key == "scenario_02" and experience_mode == "simulation":
            st.sidebar.markdown("**Relevant Runs**")
            scenario_02_run_map = {
                "Missed Hidden Strain": ("reactive_escalation", "Fail"),
                "Supported Riley Only": ("surface_containment", "Survive"),
                "Late Recovery": ("late_widening", "Survive"),
                "Gold Run": ("early_realignment", "Succeed"),
            }
            if st.sidebar.button("Missed Hidden Strain", width="stretch", key="scenario_02_path_reactive"):
                route_name, tier = scenario_02_run_map["Missed Hidden Strain"]
                load_demo_run("scenario_02", route_name, desired_tier=tier)
                st.rerun()
            if st.sidebar.button("Supported Riley Only", width="stretch", key="scenario_02_path_surface"):
                route_name, tier = scenario_02_run_map["Supported Riley Only"]
                load_demo_run("scenario_02", route_name, desired_tier=tier)
                st.rerun()
            if st.sidebar.button("Late Recovery", width="stretch", key="scenario_02_path_late"):
                route_name, tier = scenario_02_run_map["Late Recovery"]
                load_demo_run("scenario_02", route_name, desired_tier=tier)
                st.rerun()
            if st.sidebar.button("Gold Run", width="stretch", key="scenario_02_path_early"):
                route_name, tier = scenario_02_run_map["Gold Run"]
                load_demo_run("scenario_02", route_name, desired_tier=tier)
                st.rerun()
            st.sidebar.markdown("**Screen Tester**")
            tester_path_label = st.sidebar.selectbox(
                "Run",
                [
                    "Missed Hidden Strain",
                    "Supported Riley Only",
                    "Late Recovery",
                    "Gold Run",
                ],
                key="scenario_02_week_tester_path",
            )
            tester_week = st.sidebar.selectbox(
                "Week",
                [1, 2, 3, 4, 5, 6],
                format_func=lambda week: f"Week {week}",
                key="scenario_02_week_tester_week",
            )
            tester_screen = st.sidebar.radio(
                "Screen",
                ["Week Screen", "Week-End Screen"],
                key="scenario_02_week_tester_screen",
            )
            if st.sidebar.button("Load Screen", width="stretch", key="scenario_02_week_tester_go"):
                route_name = scenario_02_run_map[tester_path_label][0]
                if tester_screen == "Week Screen":
                    load_demo_week_start("scenario_02", route_name, tester_week)
                else:
                    load_demo_week_review("scenario_02", route_name, tester_week)
                st.rerun()
            st.sidebar.markdown("---")
        if st.sidebar.button("Restart Scenario", width="stretch"):
            reset_game()
            st.rerun()

    if scenario_key == "scenario_02" and experience_mode == "workshop":
        render_scenario_two_workshop_mock()
    elif st.session_state.pending_week_review:
        history = game.get_analysis_history()
        if history:
            review_week = st.session_state.get("review_snapshot_week")
            snapshot = None
            if review_week is not None:
                snapshot = next((entry for entry in history if entry["week"] == review_week), None)
            if snapshot is None:
                snapshot = history[-1]
            snapshot_index = history.index(snapshot)
            previous_snapshot = build_opening_snapshot(game) if snapshot_index == 0 else history[snapshot_index - 1]
            render_week_resolution(snapshot, previous_snapshot)
            st.stop()
        st.session_state.pending_week_review = False
        st.session_state.review_snapshot_week = None

    elif game.game_over:
        if st.session_state.get("results_view") == "score":
            render_final_score(game)
        else:
            render_end_screen(game)
    else:
        render_header(vm, game)
        render_evidence(vm, game)
        render_decision_space(vm, game)
