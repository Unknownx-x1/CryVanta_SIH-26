import unittest

from decision_engine import create_decision_from_forecast


class DecisionEngineTest(unittest.TestCase):
    def test_decision_uses_most_urgent_zone(self):
        forecast = {
            "timestamp": "2026-08-17T10:28:44Z",
            "zones": [
                {
                    "zone_id": 1,
                    "current_temp_c": 5.8,
                    "projected_temp_c": 6.5,
                    "time_to_threshold_sec": 1200,
                    "warming_rate_c_per_min": 0.05,
                },
                {
                    "zone_id": 2,
                    "current_temp_c": 9.1,
                    "projected_temp_c": 12.4,
                    "time_to_threshold_sec": 210,
                    "warming_rate_c_per_min": 0.45,
                },
            ],
        }
        telemetry = {
            "zones": [
                {"zone_id": 2, "temp_c": 9.1, "fuse_triggered": True, "vial_id": "V17"},
                {"zone_id": 1, "temp_c": 5.8, "fuse_triggered": False},
            ]
        }

        decision = create_decision_from_forecast(forecast, telemetry)

        self.assertEqual(decision["risk_level"], "HIGH")
        self.assertEqual(decision["primary_zone_affected"], 2)
        self.assertEqual(decision["action_selected"], "COOLING_ON_SERVO_OPEN")
        self.assertEqual(decision["recommended_route"], "ALTERNATE_ROUTE_A")
        self.assertEqual(decision["vials_at_risk_count"], 1)
        self.assertTrue(decision["timestamp"].endswith("Z"))


if __name__ == "__main__":
    unittest.main()
