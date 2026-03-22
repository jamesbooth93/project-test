def _compare(actual, op, expected):
    if op == ">=":
        return actual >= expected
    if op == ">":
        return actual > expected
    if op == "<=":
        return actual <= expected
    if op == "<":
        return actual < expected
    if op == "==":
        return actual == expected
    if op == "!=":
        return actual != expected
    raise ValueError(f"Unsupported operator: {op}")


def evaluate_rule_set(game, rule_set):
    if not rule_set:
        return False

    all_rules = rule_set.get("all", [])
    any_rules = rule_set.get("any", [])
    none_rules = rule_set.get("none", [])

    all_ok = all(evaluate_rule(game, rule) for rule in all_rules) if all_rules else True
    any_ok = any(evaluate_rule(game, rule) for rule in any_rules) if any_rules else True
    none_ok = not any(evaluate_rule(game, rule) for rule in none_rules) if none_rules else True
    return all_ok and any_ok and none_ok


def evaluate_rule(game, rule):
    rule_type = rule.get("type", "counter")

    if rule_type == "counter":
        actual = game.scenario_state.get(rule["counter"], 0)
        return _compare(actual, rule.get("op", ">="), rule["value"])

    if rule_type == "survived_to_end":
        return game.week >= game.max_weeks and game.result in {"kept_job", "resigned_survived"}

    if rule_type == "route_active":
        route_name = rule.get("route")
        scenario = getattr(game, "scenario_definition", None)
        if scenario is None:
            return False
        route_rules = scenario.runtime_preset.get("route_rules", {})
        return evaluate_rule_set(game, route_rules.get(route_name, {}))

    if rule_type == "not":
        nested = rule.get("rule") or {}
        return not evaluate_rule(game, nested)

    raise ValueError(f"Unsupported rule type: {rule_type}")


def scenario_route_active(game, route_name):
    scenario = getattr(game, "scenario_definition", None)
    if scenario is None:
        return False
    route_rules = scenario.runtime_preset.get("route_rules", {})
    return evaluate_rule_set(game, route_rules.get(route_name, {}))


def select_outcome_tier(game):
    scenario = getattr(game, "scenario_definition", None)
    if scenario is None:
        return None

    evaluation_order = scenario.runtime_preset.get("outcome_evaluation_order", [])
    for tier_key in evaluation_order:
        tier = scenario.outcome_tiers.get(tier_key)
        if tier and evaluate_rule_set(game, scenario.runtime_preset.get("outcome_rules", {}).get(tier_key, {})):
            return tier
    return None


def select_outcome_key_and_tier(game):
    scenario = getattr(game, "scenario_definition", None)
    if scenario is None:
        return None, None

    evaluation_order = scenario.runtime_preset.get("outcome_evaluation_order", [])
    for tier_key in evaluation_order:
        tier = scenario.outcome_tiers.get(tier_key)
        if tier and evaluate_rule_set(game, scenario.runtime_preset.get("outcome_rules", {}).get(tier_key, {})):
            return tier_key, tier
    return None, None
