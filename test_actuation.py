import unittest

from actuation import create_actuation_command, create_actuation_from_decision


class ActuationTest(unittest.TestCase):
    def test_cooling_servo_open_command(self):
        command = create_actuation_command(
            zone_id=2,
            action="COOLING_ON_SERVO_OPEN",
        )

        self.assertEqual(command["target_zone_id"], 2)
        self.assertEqual(command["peltier_state"], "ON")
        self.assertEqual(command["servo_vent_position"], "OPEN")
        self.assertEqual(command["alert_buzzer"], "ON")
        self.assertTrue(command["timestamp"].endswith("Z"))

    def test_actuation_from_decision(self):
        command = create_actuation_from_decision(
            {
                "primary_zone_affected": 3,
                "action_selected": "ALERT_ONLY",
            }
        )

        self.assertEqual(command["target_zone_id"], 3)
        self.assertEqual(command["peltier_state"], "OFF")
        self.assertEqual(command["alert_buzzer"], "ON")


if __name__ == "__main__":
    unittest.main()
