def select_action(risk_level: str) -> str:

    if risk_level == "LOW":
        return "NONE"

    elif risk_level == "MEDIUM":
        return "ALERT_ONLY"

    elif risk_level == "HIGH":
        return "COOLING_ON_SERVO_OPEN"

    elif risk_level == "CRITICAL":
        return "COOLING_ON_SERVO_OPEN"

    else:
        raise ValueError(f"Invalid risk level: {risk_level}")

def select_route(risk_level: str) -> str:

    if risk_level == "LOW":
        return "CURRENT_ROUTE"

    elif risk_level == "MEDIUM":
        return "CURRENT_ROUTE"

    elif risk_level == "HIGH":
        return "ALTERNATE_ROUTE_A"

    elif risk_level == "CRITICAL":
        return "IMMEDIATE_STOP"

    else:
        raise ValueError(f"Invalid risk level: {risk_level}")

def create_decision(zone, risk_level: str):

    action = select_action(risk_level)
    route = select_route(risk_level)

    decision = {
        "timestamp": None,
        "risk_level": risk_level,
        "primary_zone_affected": zone["zone_id"],
        "action_selected": action,
        "recommended_route": route,
        "vials_at_risk_count": 0,
        "reasoning": (
            f"Zone {zone['zone_id']} projected to reach "
            f"the thermal threshold in "
            f"{zone['time_to_threshold_sec']} seconds."
        )
    }

    return decision