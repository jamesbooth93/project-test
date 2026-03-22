import math

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import networkx as nx


def draw_observed_risk_chart(rows, selected_id):
    ordered_rows = sorted(rows, key=lambda row: row["observed_risk"], reverse=True)
    names = [row["name"] for row in ordered_rows]
    values = [row["observed_risk"] for row in ordered_rows]

    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    cmap = plt.cm.YlOrRd
    colors = [cmap(value) for value in values]
    edgecolors = ["#eadfcb" if row["id"] != selected_id else "#12324a" for row in ordered_rows]
    linewidths = [0.8 if row["id"] != selected_id else 1.8 for row in ordered_rows]
    bars = ax.bar(names, values, color=colors, edgecolor=edgecolors, linewidth=linewidths)
    for bar, row in zip(bars, ordered_rows):
        if row["id"] == selected_id:
            bar.set_alpha(1.0)
        else:
            bar.set_alpha(0.92)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylabel("Visible Friction")
    ax.set_title("Visible Friction", fontsize=12)
    ax.tick_params(axis="x", rotation=35, labelsize=8.5, pad=2)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", alpha=0.14)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    return fig


def visible_friction_score(row):
    score = 0.45 * float(row.get("observed_risk", 0.0))
    warning_signs = [
        item.strip()
        for item in str(row.get("warning_signs", "") or "").split(",")
        if item.strip()
    ]
    visible_behavior_weights = {
        "complaint": 0.20,
        "missed_deadline_minor": 0.18,
        "missed_deadline_critical": 0.28,
        "overload_signal": 0.20,
        "high_error_rate": 0.22,
        "lateness": 0.10,
    }
    score += sum(visible_behavior_weights.get(sign, 0.0) for sign in warning_signs[-3:])
    if row.get("engagement_hint") == "Low":
        score += 0.06
    elif row.get("engagement_hint") == "Wobbling":
        score += 0.03
    scenario_role = row.get("scenario_role")
    if scenario_role == "hidden_strain_employee":
        score *= 0.6
    return float(min(1.0, score))


def absorbed_workload_label(value):
    if value >= 0.55:
        return "High"
    if value >= 0.25:
        return "Moderate"
    if value >= 0.10:
        return "Light"
    return "Low"


def visible_load_label(value):
    if value >= 0.42:
        return "High"
    if value >= 0.18:
        return "Moderate"
    return "Light"


def player_facing_load_value(game, node_id):
    node = game.G.nodes[node_id]
    if game.scenario == "scenario_02":
        return float(node.get("scenario_display_load", 0.0))
    return max(
        float(node.get("absorbed_workload", 0.0)),
        float(node.get("last_absorbed_workload", 0.0)),
    )


def draw_visible_friction_chart(rows, selected_id):
    ordered_rows = sorted(
        rows,
        key=lambda row: visible_friction_score(row),
        reverse=True,
    )
    names = [row["name"] for row in ordered_rows]
    friction_values = [visible_friction_score(row) for row in ordered_rows]

    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    friction_colors = [plt.cm.YlOrRd(0.25 + 0.65 * value) for value in friction_values]
    edgecolors = ["#eadfcb" if row["id"] != selected_id else "#12324a" for row in ordered_rows]
    linewidths = [0.8 if row["id"] != selected_id else 1.8 for row in ordered_rows]

    bars = ax.bar(
        names,
        friction_values,
        color=friction_colors,
        edgecolor=edgecolors,
        linewidth=linewidths,
        alpha=0.94,
        label="Visible Friction",
    )
    for bar, row in zip(bars, ordered_rows):
        if row["id"] == selected_id:
            bar.set_alpha(1.0)

    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_ylabel("Visible Friction")
    ax.set_title("Visible Friction", fontsize=12)
    ax.tick_params(axis="x", rotation=35, labelsize=8.5, pad=2)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", alpha=0.14)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    return fig


def draw_workload_distribution_chart(rows, selected_id):
    ordered_rows = sorted(
        rows,
        key=lambda row: float(row.get("absorbed_workload_value", 0.0)),
        reverse=True,
    )
    names = [row["name"] for row in ordered_rows]
    values = [min(1.0, float(row.get("absorbed_workload_value", 0.0))) for row in ordered_rows]

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    colors = [plt.cm.GnBu(0.25 + 0.65 * value) for value in values]
    edgecolors = ["#eadfcb" if row["id"] != selected_id else "#12324a" for row in ordered_rows]
    linewidths = [0.8 if row["id"] != selected_id else 1.8 for row in ordered_rows]
    bars = ax.barh(names, values, color=colors, edgecolor=edgecolors, linewidth=linewidths, alpha=0.92)
    for bar, row in zip(bars, ordered_rows):
        if row["id"] == selected_id:
            bar.set_alpha(1.0)

    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_title("Absorbed Workload", fontsize=12)
    ax.grid(axis="x", alpha=0.12)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.tick_params(axis="x", labelsize=8.5)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    return fig


def _fixed_team_positions(employee_ids, cluster_ids):
    positions = {}
    cluster_positions = [
        (-0.72, 0.34),
        (0.18, 0.68),
        (0.76, -0.02),
        (-0.12, -0.58),
    ]
    for index, node_id in enumerate(cluster_ids):
        positions[node_id] = cluster_positions[index % len(cluster_positions)]

    non_cluster_ids = [node_id for node_id in sorted(employee_ids) if node_id not in cluster_ids]
    count = len(non_cluster_ids)
    if count:
        radius_x = 1.95
        radius_y = 1.35
        for index, node_id in enumerate(non_cluster_ids):
            angle = (2 * math.pi * index / count) - (math.pi / 2)
            positions[node_id] = (radius_x * math.cos(angle), radius_y * math.sin(angle))

    return positions


def draw_network_chart(game):
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    managed_nodes = game.managed_node_ids()
    graph = game.G.subgraph(managed_nodes).copy()
    cluster_ids = set(game.get_scenario_cluster_node_ids())
    pos = _fixed_team_positions(list(graph.nodes()), cluster_ids)

    node_colors = []
    node_sizes = []
    for node_id in graph.nodes():
        risk = graph.nodes[node_id].get("observed_risk", 0.0)
        absorbed = player_facing_load_value(game, node_id)
        if game.scenario == "scenario_02":
            row = {
                "observed_risk": risk,
                "scenario_role": graph.nodes[node_id].get("scenario_role"),
                "warning_signs": ", ".join(graph.nodes[node_id].get("recent_behaviors", [])[-3:]) or "-",
                "engagement_hint": "Wobbling" if graph.nodes[node_id].get("engagement", 0.0) < 0.55 else "Okay",
            }
            node_colors.append(visible_friction_score(row))
            node_sizes.append(340 + 90 * graph.degree(node_id) + 680 * min(absorbed, 1.0))
        else:
            node_colors.append(risk)
            node_sizes.append(320 + 120 * graph.degree(node_id))

    widths = []
    for u, v in graph.edges():
        width = 0.6 + 2.2 * graph.edges[u, v].get("weight", 0.0)
        if game.scenario == "scenario_02":
            absorbed_u = player_facing_load_value(game, u)
            absorbed_v = player_facing_load_value(game, v)
            width += 1.6 * max(absorbed_u, absorbed_v)
        widths.append(width)
    nx.draw_networkx_edges(graph, pos, width=widths, alpha=0.22, ax=ax)
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        cmap=plt.cm.YlOrRd,
        vmin=0,
        vmax=1,
        node_size=node_sizes,
        alpha=0.92,
        ax=ax,
    )
    labels = {n: graph.nodes[n]["name"] for n in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=7.2, ax=ax)
    ax.set_title("Dependency Flow" if game.scenario == "scenario_02" else "Team Connections", fontsize=12)
    ax.axis("off")
    plt.tight_layout()
    return fig


