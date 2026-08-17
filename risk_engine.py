RISK_THRESHOLDS = {
    "low": 1200,
    "medium": 600,
    "high": 180
}


def calculate_risk(time_to_threshold_sec: float) -> str:
    """Map forecast urgency to the frozen SystemContract risk enum."""

    if time_to_threshold_sec > RISK_THRESHOLDS["low"]:
        return "LOW"

    elif time_to_threshold_sec > RISK_THRESHOLDS["medium"]:
        return "MEDIUM"

    elif time_to_threshold_sec > RISK_THRESHOLDS["high"]:
        return "HIGH"

    else:
        return "CRITICAL"


def highest_risk(risk_levels: list[str]) -> str:
    order = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    if not risk_levels:
        return "LOW"

    unknown = [risk for risk in risk_levels if risk not in order]
    if unknown:
        raise ValueError(f"Invalid risk level: {unknown[0]}")

    return max(risk_levels, key=lambda risk: order[risk])
