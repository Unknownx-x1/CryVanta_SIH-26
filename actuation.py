from datetime import datetime, timezone


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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_zone_id": zone_id,
        **command
    }