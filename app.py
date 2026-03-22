import math
import os
import matplotlib.pyplot as plt
import streamlit as st

from action_registry import action_cost, action_description, action_label, action_past_tense
from benchmarks import (
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

TEST_MODE = os.environ.get("MANAGEMENT_SIM_TEST_MODE") == "1"

if not TEST_MODE:
    st.set_page_config(page_title="Suppress the Stress", layout="wide")

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
        color: #ffffff;
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


def reset_game(scenario_key=None):
    selected_scenario = scenario_key or st.session_state.get("selected_scenario", DEFAULT_SCENARIO_KEY)
    st.session_state.selected_scenario = selected_scenario
    st.session_state.game = GameState(scenario=selected_scenario)
    st.session_state.pending_week_review = False
    st.session_state.results_view = "summary"
    st.session_state.analysis_week = 0
    st.session_state.evidence_employee_id = None
    for key in ["selected_employee", "selected_employee_from", "selected_employee_to"]:
        if key in st.session_state:
            del st.session_state[key]


def ensure_state():
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = DEFAULT_SCENARIO_KEY
    if "game" not in st.session_state:
        reset_game(st.session_state.selected_scenario)
    else:
        st.session_state.setdefault("pending_week_review", False)
        st.session_state.setdefault("results_view", "summary")
        st.session_state.setdefault("analysis_week", 0)
        st.session_state.setdefault("evidence_employee_id", None)


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
    if outcome_tier == 'Fail':
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


def _draw_snapshot_map(snapshot, title, metric_key, positions=None):
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
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


def draw_analysis_heatmap(snapshot, title, positions=None):
    return _draw_snapshot_map(snapshot, title, "true_strain", positions=positions)


def draw_observed_risk_snapshot_map(snapshot, title, positions=None):
    return _draw_snapshot_map(snapshot, title, "observed_risk", positions=positions)


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

    if st.button("Continue", type="primary", width="stretch"):
        st.session_state.pending_week_review = False
        clear_diagnosis_box()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_final_score(game):
    history = game.get_analysis_history()
    benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
    latest_snapshot = history[-1] if history else None
    player_avg = cluster_strain_avg(latest_snapshot) if latest_snapshot else None

    st.markdown('<div class="shell-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="centered-outcome">Final Score</h2>', unsafe_allow_html=True)
    if player_avg is not None:
        st.markdown(
            f'<div class="summary-impact">Core-group strain at the end of the scenario: {round(player_avg * 100)}%</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    scenario_targets = {
        "scenario_01": 0.29,
        "scenario_02": 0.52,
    }
    target_avg = scenario_targets.get(game.scenario)
    if player_avg is not None and target_avg is not None:
        if player_avg <= target_avg + 0.005:
            copy = (
                f'You finished with core-group strain at {round(player_avg * 100)}%. '
                f'This is better than the target score of {round(target_avg * 100)}% or lower. '
                'Well done.'
            )
        else:
            copy = (
                f'You finished with core-group strain at {round(player_avg * 100)}%. '
                f'A good target for this scenario is {round(target_avg * 100)}% or lower. '
                'That gives you a clear number to aim for next run.'
            )
    elif player_avg is not None:
        copy = (
            f'You finished with core-group strain at {round(player_avg * 100)}%. '
            'Lower is better, so this gives you a clear number to improve on next run.'
        )
    else:
        copy = 'There was not enough history to calculate a final score for this run.'
    st.markdown(f'<div class="centered-results-text">{copy}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    back_col, new_run_col = st.columns(2)
    if back_col.button("Back To Analysis", width="stretch"):
        st.session_state.results_view = "analysis"
        st.rerun()
    if new_run_col.button("Start New Run", type="primary", width="stretch"):
        reset_game()
        st.rerun()


def render_end_screen(game):
    history = game.get_analysis_history()
    latest = history[-1] if history else {}
    benchmark_history = build_benchmark_history(game, benchmark_name="stabilising_response")
    benchmark_latest = _analysis_snapshot_for_week(benchmark_history, game.max_weeks)
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
            st.markdown('<div class="centered-results-text"><strong>End-of-Run Debrief</strong></div>', unsafe_allow_html=True)
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
                    impact_text = (
                        "The demo pressure kept spilling through the surrounding pocket of the team."
                        f'<br><br>With a stronger response, {benchmark_high_strain} {people_label(benchmark_high_strain)} in the core group could have ended under high strain instead of {player_high_strain}.'
                    )
                else:
                    impact_text = (
                        "The launch pressure kept spreading through the surrounding pocket of the team."
                        f'<br><br>With a stronger response, {benchmark_high_strain} {people_label(benchmark_high_strain)} in the core group could have ended under high strain instead of {player_high_strain}.'
                    )
            else:
                if game.scenario == "scenario_02":
                    impact_text = (
                        f"The demo got through, but {player_high_strain} {people_label(player_high_strain)} in the core group were still carrying too much pressure."
                        f'<br><br>With a stronger response, that could have been {benchmark_high_strain}.'
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
                    impact_text = (
                        "The demo got through, but the core group was still carrying more strain than it needed to."
                        "<br><br>A stronger response would have left the group in a better place."
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

        if st.button("Analyse", type="primary", width="stretch"):
            st.session_state.results_view = "analysis"
            st.session_state.analysis_week = 0
            st.rerun()
        if st.button("Start New Run", width="stretch"):
            reset_game()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
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
    benchmark_snapshot = opening_snapshot if selected_week == 0 else _analysis_snapshot_for_week(benchmark_history, selected_week)
    shared_positions = _shared_analysis_positions(selected_snapshot, benchmark_snapshot)

    st.markdown('<div class="results-column">', unsafe_allow_html=True)
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    left_panel, right_panel = st.columns(2)
    with left_panel:
        if selected_snapshot:
            st.pyplot(draw_analysis_heatmap(selected_snapshot, "Your Run", positions=shared_positions), width="stretch")
    with right_panel:
        if benchmark_snapshot:
            st.pyplot(draw_analysis_heatmap(benchmark_snapshot, "Recommended Run", positions=shared_positions), width="stretch")
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
            st.markdown(
                (
                    f'<div class="centered-results-text"><strong>{summary["focal_name"]} and the connected core group</strong> '
                    f'({summary["names_text"]}) are highlighted on the chart. '
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
            for key in (
                "what_the_situation_called_for",
                "how_your_choice_landed",
                "assessment_from_your_starting_point",
                "what_it_meant_for_your_trajectory",
            ):
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

    back_col, new_run_col = st.columns(2)
    if back_col.button("Back", width="stretch"):
        st.session_state.results_view = "summary"
        st.rerun()
    if new_run_col.button("Start New Run", type="primary", width="stretch"):
        reset_game()
        st.rerun()


if not TEST_MODE:
    ensure_state()
    game = st.session_state.game
    vm = build_weekly_view_model(game)

    if st.session_state.pending_week_review and not game.game_over:
        history = game.get_analysis_history()
        if history:
            previous_snapshot = build_opening_snapshot(game) if len(history) == 1 else history[-2]
            render_week_resolution(history[-1], previous_snapshot)
            st.stop()
        st.session_state.pending_week_review = False

    if game.game_over:
        if st.session_state.get("results_view") == "score":
            render_final_score(game)
        else:
            render_end_screen(game)
    else:
        render_header(vm, game)
        render_evidence(vm, game)
        render_decision_space(vm, game)
