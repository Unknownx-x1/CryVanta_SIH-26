RISK_THRESHOLDS = {
    "low": 1200,
    "medium": 600,
    "high": 180
}


def calculate_risk(time_to_threshold_sec: float) -> str:

    if time_to_threshold_sec > RISK_THRESHOLDS["low"]:
        return "LOW"

    elif time_to_threshold_sec > RISK_THRESHOLDS["medium"]:
        return "MEDIUM"

    elif time_to_threshold_sec > RISK_THRESHOLDS["high"]:
        return "HIGH"

    else:
        return "CRITICAL"