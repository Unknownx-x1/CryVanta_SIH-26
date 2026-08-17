from decision_engine import utc_timestamp


def create_actuation_command(zone_id: int, action: str):

    if action == "NONE":
        command = {
            "peltier_state": "OFF",
            "servo_vent_position": "CLOSED",
            "alert_buzzer": "OFF"
        }

    elif action == "ALERT_ONLY":
        command = {
            "peltier_state": "OFF",
            "servo_vent_position": "CLOSED",
            "alert_buzzer": "ON"
        }

    elif action == "COOLING_ON":
        command = {
            "peltier_state": "ON",
            "servo_vent_position": "CLOSED",
            "alert_buzzer": "OFF"
        }

    elif action == "SERVO_OPEN":
        command = {
            "peltier_state": "OFF",
            "servo_vent_position": "OPEN",
            "alert_buzzer": "OFF"
        }

    elif action == "COOLING_ON_SERVO_OPEN":
        command = {
            "peltier_state": "ON",
            "servo_vent_position": "OPEN",
            "alert_buzzer": "ON"
        }

    else:
        raise ValueError(f"Unknown action: {action}")

    return {
        "timestamp": utc_timestamp(),
        "target_zone_id": zone_id,
        **command
    }


def create_actuation_from_decision(decision: dict) -> dict:
    return create_actuation_command(
        zone_id=decision.get("primary_zone_affected"),
        action=decision["action_selected"],
    )
