from risk_engine import calculate_risk
from decision_engine import create_decision


zone = {
    "zone_id": 2,
    "current_temp_c": 9.1,
    "projected_temp_c": 12.4,
    "time_to_threshold_sec": 210,
    "warming_rate_c_per_min": 0.45
}

risk = calculate_risk(zone["time_to_threshold_sec"])

decision = create_decision(zone, risk)

print(decision)