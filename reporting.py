from game_logic import GameState
from simulation_engine import apply_benchmark_actions_for_week


BENCHMARK_CACHE_VERSION = 1
BENCHMARK_CACHE: dict[tuple, list[dict]] = {}


def build_benchmark_history(game, benchmark_name="stabilising_response"):
    cache_key = (
        BENCHMARK_CACHE_VERSION,
        benchmark_name,
        game.scenario,
        game.evaluation_mode,
        game.difficulty,
        game.rng_seed,
        game.max_weeks,
    )
    cached = BENCHMARK_CACHE.get(cache_key)
    if cached is not None and all("network_edges" in snapshot for snapshot in cached):
        return cached

    benchmark_game = GameState(
        scenario=game.scenario,
        difficulty=game.difficulty,
        team_size=game.team_size,
        max_weeks=game.max_weeks,
        evaluation_mode=game.evaluation_mode,
        seed=game.rng_seed,
        debug=False,
    )
    while not benchmark_game.game_over and benchmark_game.week <= benchmark_game.max_weeks:
        apply_benchmark_actions_for_week(benchmark_game, benchmark_name)

    history = benchmark_game.get_analysis_history()
    BENCHMARK_CACHE[cache_key] = history
    return history


def _analysis_snapshot_for_week(history, selected_week):
    if not history:
        return None
    matching = [snapshot for snapshot in history if snapshot["week"] == selected_week]
    if matching:
        return matching[0]
    prior = [snapshot for snapshot in history if snapshot["week"] <= selected_week]
    if prior:
        return prior[-1]
    return history[0]


def _cluster_node_ids(snapshot):
    scenario_roles = snapshot.get("scenario_roles", {})
    ordered = [
        scenario_roles.get("focal_employee"),
        scenario_roles.get("hidden_strain_employee"),
        scenario_roles.get("spillover_employee"),
        scenario_roles.get("cluster_anchor"),
    ]
    return [node_id for node_id in ordered if node_id is not None]


def cluster_strain_avg(snapshot):
    cluster_ids = set(_cluster_node_ids(snapshot))
    if not cluster_ids:
        return None
    cluster_values = [
        float(employee.get("true_strain", 0.0))
        for employee in snapshot.get("employees", [])
        if employee["id"] in cluster_ids
    ]
    if not cluster_values:
        return None
    return sum(cluster_values) / len(cluster_values)


def cluster_strain_improvement(player_snapshot, benchmark_snapshot):
    player_cluster_avg = cluster_strain_avg(player_snapshot)
    benchmark_cluster_avg = cluster_strain_avg(benchmark_snapshot)
    if player_cluster_avg is None or benchmark_cluster_avg is None:
        return None
    if player_cluster_avg <= 0:
        return {
            "player_cluster_avg": player_cluster_avg,
            "benchmark_cluster_avg": benchmark_cluster_avg,
            "improvement_pct": 0.0,
        }
    improvement_pct = max(0.0, (player_cluster_avg - benchmark_cluster_avg) / player_cluster_avg)
    return {
        "player_cluster_avg": player_cluster_avg,
        "benchmark_cluster_avg": benchmark_cluster_avg,
        "improvement_pct": improvement_pct,
    }


def core_group_high_strain_count(snapshot, threshold=0.6):
    cluster_ids = set(_cluster_node_ids(snapshot))
    if not cluster_ids:
        return 0
    return sum(
        1
        for employee in snapshot.get("employees", [])
        if employee["id"] in cluster_ids and float(employee.get("true_strain", 0.0)) > threshold
    )


def _employee_row(snapshot, node_id):
    if snapshot is None or node_id is None:
        return None
    for employee in snapshot.get("employees", []):
        if employee.get("id") == node_id:
            return employee
    return None


def scenario_two_dependency_metrics(snapshot):
    if not snapshot:
        return None
    hidden_id = snapshot.get("scenario_roles", {}).get("hidden_strain_employee")
    hidden_row = _employee_row(snapshot, hidden_id)
    employees = snapshot.get("employees", [])
    if hidden_row is None or not employees:
        return None

    load_values = [float(employee.get("absorbed_workload", 0.0)) for employee in employees]
    total_load = sum(load_values)
    hidden_load = float(hidden_row.get("absorbed_workload", 0.0))
    active_carriers = sum(1 for value in load_values if value >= 0.10)
    dependency_share = (hidden_load / total_load) if total_load > 0 else 0.0
    return {
        "hidden_name": hidden_row.get("name", "the reliable fixer"),
        "hidden_load": hidden_load,
        "total_load": total_load,
        "active_carriers": active_carriers,
        "dependency_share": dependency_share,
    }


def scenario_two_peak_dependency_comparison(player_history, benchmark_history):
    def peak_metrics(history):
        metrics = [scenario_two_dependency_metrics(snapshot) for snapshot in history or []]
        metrics = [metric for metric in metrics if metric is not None]
        if not metrics:
            return None
        return max(metrics, key=lambda metric: metric["hidden_load"])

    player = peak_metrics(player_history)
    benchmark = peak_metrics(benchmark_history)
    if player is None or benchmark is None:
        return None
    return {
        "hidden_name": player["hidden_name"],
        "player_peak_hidden_load": player["hidden_load"],
        "benchmark_peak_hidden_load": benchmark["hidden_load"],
        "player_peak_dependency_share": player["dependency_share"],
        "benchmark_peak_dependency_share": benchmark["dependency_share"],
        "player_active_carriers": player["active_carriers"],
        "benchmark_active_carriers": benchmark["active_carriers"],
    }


def determine_summary_branch(game, history, latest, benchmark_history, benchmark_latest):
    if not latest:
        return "high_strain_count"

    player_high_strain = core_group_high_strain_count(latest)
    benchmark_high_strain = core_group_high_strain_count(benchmark_latest) if benchmark_latest else 0

    if latest.get("scenario_outcome_tier") == "Fail":
        return "high_strain_count"

    if player_high_strain > benchmark_high_strain:
        return "high_strain_count"

    if latest and benchmark_latest and player_high_strain <= benchmark_high_strain:
        if game.scenario == "scenario_02":
            dependency_comparison = scenario_two_peak_dependency_comparison(history, benchmark_history)
            if (
                latest.get("scenario_outcome_tier") == "Succeed"
                and dependency_comparison
                and dependency_comparison["player_peak_hidden_load"] <= dependency_comparison["benchmark_peak_hidden_load"] + 0.05
            ):
                return "well_done"
        else:
            end_comparison = cluster_strain_improvement(latest, benchmark_latest)
            if (
                latest.get("scenario_outcome_tier") == "Succeed"
                and end_comparison
                and end_comparison["player_cluster_avg"] <= end_comparison["benchmark_cluster_avg"] * 1.15
            ):
                return "well_done"

    end_comparison = cluster_strain_improvement(latest, benchmark_latest) if latest and benchmark_latest else None
    if end_comparison and end_comparison["benchmark_cluster_avg"] + 0.02 < end_comparison["player_cluster_avg"]:
        return "more_strain_than_needed"
    return "well_done"


OPENERS = {
    "intervened": {
        "improved": [
            "What we changed this week helped, and the team looked a little steadier by the end of it.",
            "We made some useful progress this week, and things felt more manageable by the end of it.",
        ],
        "mixed": [
            "We stepped in this week, and it helped, even if the pressure did not fully settle.",
            "We tried to steady things this week, and the team looked a little steadier by the end of it.",
        ],
        "worsened": [
            "We tried to intervene this week, but the team looked less steady by the end of it.",
            "We made changes this week, but the pressure still seemed to spread.",
        ],
    },
    "no_action": {
        "improved": [
            "The week felt a little steadier by the end of it, even without a direct intervention.",
        ],
        "mixed": [
            "We got through the week without changing much directly, and the picture stayed a little uneven.",
            "The week kept moving, and there were some signs of stability, even if it did not fully settle.",
        ],
        "worsened": [
            "We got through the week, but the team looked more strained by the end of it.",
            "The week kept moving, but the pressure looked harder to contain by the end of it.",
        ],
    },
}

SCENARIO_01_FALLBACK = "Jordan remained the clearest pressure point, and the surrounding pocket did not look fully settled."
SCENARIO_02_FALLBACK = "Riley remained the most visible source of pressure, while some of the background work still seemed to be landing elsewhere."

SCENARIO_01_PRESSURE_READS = {
    ("more_visible", "worsened"): [
        "Jordan remained the most visible point of strain, and the surrounding pocket looked less steady overall.",
        "The pressure around Jordan became easier to see, and the people around him looked more fragile by the end of the week.",
    ],
    ("more_visible", "mixed"): [
        "Jordan was still where the pressure showed up most clearly, and there were signs the surrounding pocket was beginning to feel it too.",
    ],
    ("steady", "worsened"): [
        "Jordan remained the clearest pressure point, but it no longer looked like the issue sat with him alone.",
    ],
    ("less_visible", "improved"): [
        "The pressure around Jordan looked a little more contained, and the surrounding pocket seemed steadier by the end of the week.",
    ],
    ("steady", "improved"): [
        "Jordan was still the clearest pressure point, but the wider group looked steadier around him.",
    ],
}

SCENARIO_02_PRESSURE_READS = {
    ("more_visible", "more_hidden_load"): [
        "Riley remained the most visible source of pressure, while more of the cleanup and clarification seemed to be landing elsewhere in the team.",
        "The pressure around Riley became easier to see, but the week also looked as though it was creating more spillover in the background.",
    ],
    ("more_visible", "steady_hidden_load"): [
        "Riley remained the clearest source of friction, while some of the background pressure still seemed to be sitting elsewhere.",
    ],
    ("steady", "more_hidden_load"): [
        "Riley was still the most visible issue, but more of the background burden appeared to be landing elsewhere in the team.",
    ],
    ("less_visible", "less_hidden_load"): [
        "Riley was still the clearest visible issue, but less of the background burden seemed to be resting in one place.",
    ],
    ("steady", "less_hidden_load"): [
        "Riley remained the most visible source of pressure, but the week looked less dependent on quiet carrying work by the end of it.",
    ],
}

WATCH_NEXT = {
    "scenario_01": {
        "improved": [
            "The main thing to watch now is whether this improvement holds next week.",
            "The main thing to watch now is whether the group can keep this steadier footing under fresh pressure.",
        ],
        "mixed": [
            "The main thing to watch now is whether the strain stays contained or starts to spread further.",
            "The main thing to watch now is whether the people around Jordan steady next week or come under more pressure themselves.",
        ],
        "worsened": [
            "The main thing to watch now is whether this remains a local issue or becomes a wider team problem.",
            "The main thing to watch now is whether quieter strain keeps building around the visible issue.",
        ],
    },
    "scenario_02": {
        "improved": [
            "The main thing to watch now is whether this improvement holds next week.",
            "The main thing to watch now is whether the team can keep this steadier footing without falling back on quiet rescue work.",
        ],
        "mixed": [
            "The main thing to watch now is whether the pressure is easing or simply moving around the team.",
            "The main thing to watch now is whether the spillover is actually reducing or just landing somewhere less visible.",
        ],
        "worsened": [
            "The main thing to watch now is whether too much of the week is being held together quietly in the background.",
            "The main thing to watch now is whether the pressure keeps spreading beyond the most visible issue.",
        ],
    },
}


def _pick_line(options):
    return options[0] if options else ""


def _classify_stability(snapshot, previous_snapshot):
    current_cluster = cluster_strain_avg(snapshot)
    previous_cluster = cluster_strain_avg(previous_snapshot)
    if current_cluster is None or previous_cluster is None:
        return "mixed"
    cluster_delta = current_cluster - previous_cluster
    if cluster_delta <= -0.02:
        return "improved"
    if cluster_delta >= 0.02:
        return "worsened"
    return "mixed"


def _classify_focal_visibility(snapshot, previous_snapshot):
    focal_id = snapshot.get("scenario_roles", {}).get("focal_employee") if snapshot else None
    focal_now = _employee_row(snapshot, focal_id)
    focal_prev = _employee_row(previous_snapshot, focal_id)
    if not focal_now or not focal_prev:
        return "steady"
    delta = float(focal_now.get("observed_risk", 0.0)) - float(focal_prev.get("observed_risk", 0.0))
    if delta >= 0.03:
        return "more_visible"
    if delta <= -0.03:
        return "less_visible"
    return "steady"


def _classify_hidden_load(snapshot, previous_snapshot):
    hidden_id = snapshot.get("scenario_roles", {}).get("hidden_strain_employee") if snapshot else None
    hidden_now = _employee_row(snapshot, hidden_id)
    hidden_prev = _employee_row(previous_snapshot, hidden_id)
    if not hidden_now or not hidden_prev:
        return "steady_hidden_load"
    delta = float(hidden_now.get("absorbed_workload", 0.0)) - float(hidden_prev.get("absorbed_workload", 0.0))
    if delta >= 0.03:
        return "more_hidden_load"
    if delta <= -0.03:
        return "less_hidden_load"
    return "steady_hidden_load"


def build_end_of_week_report(snapshot, previous_snapshot):
    if not snapshot or not previous_snapshot:
        return []

    scenario = snapshot.get("scenario")
    action_tone = "intervened" if snapshot.get("actions_taken") else "no_action"
    stability = _classify_stability(snapshot, previous_snapshot)
    opener = _pick_line(OPENERS[action_tone][stability])

    focal_state = _classify_focal_visibility(snapshot, previous_snapshot)
    hidden_state = _classify_hidden_load(snapshot, previous_snapshot)

    if scenario == "scenario_01":
        pressure_read = _pick_line(SCENARIO_01_PRESSURE_READS.get((focal_state, stability), [SCENARIO_01_FALLBACK]))
    else:
        pressure_read = _pick_line(SCENARIO_02_PRESSURE_READS.get((focal_state, hidden_state), [SCENARIO_02_FALLBACK]))

    watch_next = _pick_line(WATCH_NEXT.get(scenario, WATCH_NEXT["scenario_01"])[stability])
    return [line for line in [opener, pressure_read, watch_next] if line]


def average_cluster_strain_across_history(history):
    values = [cluster_strain_avg(snapshot) for snapshot in history or []]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / len(values)
