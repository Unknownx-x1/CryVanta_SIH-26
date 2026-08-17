from datetime import datetime, timezone

from risk_engine import calculate_risk, highest_risk


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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

def select_primary_zone(zones: list[dict]) -> dict | None:
    if not zones:
        return None

    return min(
        zones,
        key=lambda zone: (
            zone.get("time_to_threshold_sec", float("inf")),
            -zone.get("projected_temp_c", float("-inf")),
        ),
    )


def count_vials_at_risk(telemetry: dict | None, primary_zone_id: int | None) -> int:
    if telemetry is None or primary_zone_id is None:
        return 0

    count = 0
    for zone in telemetry.get("zones", []):
        if zone.get("zone_id") != primary_zone_id:
            continue
        if zone.get("fuse_triggered") or zone.get("temp_c", 0) >= 8.0:
            count += 1
    return count


def create_decision(zone, risk_level: str, telemetry: dict | None = None):

    action = select_action(risk_level)
    route = select_route(risk_level)
    zone_id = zone["zone_id"] if zone else None
    threshold_time = zone.get("time_to_threshold_sec") if zone else None

    decision = {
        "timestamp": utc_timestamp(),
        "risk_level": risk_level,
        "primary_zone_affected": zone_id,
        "action_selected": action,
        "recommended_route": route,
        "vials_at_risk_count": count_vials_at_risk(telemetry, zone_id),
        "reasoning": build_reasoning(zone, threshold_time, risk_level, action, route)
    }

    return decision


def build_reasoning(zone, threshold_time, risk_level: str, action: str, route: str) -> str:
    if zone is None:
        return "No forecast zones available. Risk held at LOW and no actuation requested."

    return (
        f"Zone {zone['zone_id']} projected to breach threshold in "
        f"{threshold_time} seconds. Risk is {risk_level}; selected "
        f"{action} with {route}."
    )


def create_decision_from_forecast(forecast: dict, telemetry: dict | None = None) -> dict:
    zones = forecast.get("zones", [])
    primary_zone = select_primary_zone(zones)

    if primary_zone is None:
        return create_decision(None, "LOW", telemetry)

    risks = [calculate_risk(zone["time_to_threshold_sec"]) for zone in zones]
    risk_level = highest_risk(risks)
    primary_risk = calculate_risk(primary_zone["time_to_threshold_sec"])

    return create_decision(primary_zone, highest_risk([risk_level, primary_risk]), telemetry)
