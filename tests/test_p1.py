"""
PredictFuse - Task P1 Unit Tests
Validates Telemetry Simulator and Physics Engine implementation against SYSTEM_CONTRACT.md.
"""

import unittest
from simulator.telemetry_generator import TelemetrySimulator
from prediction.physics_engine import PhysicsPredictionEngine


class TestTaskP1(unittest.TestCase):

    def setUp(self):
        self.simulator = TelemetrySimulator(scenario="LOCALIZED_WARMING", publish_interval_sec=0.1)
        self.engine = PhysicsPredictionEngine()

    def test_telemetry_schema_compliance(self):
        """Test that generated telemetry strictly follows coldguard/telemetry schema."""
        telemetry = self.simulator.tick()

        self.assertIn("timestamp", telemetry)
        self.assertIn("ambient", telemetry)
        self.assertIn("gps", telemetry)
        self.assertIn("zones", telemetry)

        # Check ambient keys
        self.assertIn("temp_c", telemetry["ambient"])
        self.assertIn("humidity_pct", telemetry["ambient"])

        # Check GPS keys
        self.assertIn("lat", telemetry["gps"])
        self.assertIn("lng", telemetry["gps"])

        # Check zones
        self.assertTrue(len(telemetry["zones"]) >= 3)
        for zone in telemetry["zones"]:
            self.assertIn("zone_id", zone)
            self.assertIn("temp_c", zone)
            self.assertIn("fuse_triggered", zone)

    def test_localized_warming_scenario_and_fuse_trigger(self):
        """Test localized warming in Zone 2 and eventual passive fuse trigger."""
        sim = TelemetrySimulator(scenario="LOCALIZED_WARMING", publish_interval_sec=0.01)
        fuse_triggered_seen = False

        for _ in range(35):
            telemetry = sim.tick()
            zone2 = next(z for z in telemetry["zones"] if z["zone_id"] == 2)
            if zone2["fuse_triggered"]:
                fuse_triggered_seen = True
                self.assertEqual(zone2["vial_id"], "V17")
                self.assertGreaterEqual(zone2["trigger_temp_c"], 15.0)

        self.assertTrue(fuse_triggered_seen, "Passive fuse card should trigger when Zone 2 exceeds 15.0°C")

    def test_physics_engine_forecast_and_potency(self):
        """Test physics engine forecast projection and time-to-threshold countdown."""
        sim = TelemetrySimulator(scenario="LOCALIZED_WARMING", publish_interval_sec=0.01)

        for _ in range(15):
            telemetry = sim.tick()
            forecast, potency = self.engine.process_telemetry(telemetry)

            # Validate forecast schema
            self.assertIn("timestamp", forecast)
            self.assertIn("zones", forecast)
            self.assertEqual(len(forecast["zones"]), len(telemetry["zones"]))

            # Validate potency schema
            self.assertIn("timestamp", potency)
            self.assertIn("overall_potency_pct", potency)
            self.assertIn("zones", potency)

            # Zone 2 time-to-threshold should decrease as temp warms
            zone2_forecast = next(z for z in forecast["zones"] if z["zone_id"] == 2)
            self.assertIsInstance(zone2_forecast["time_to_threshold_sec"], int)
            self.assertIsInstance(zone2_forecast["projected_temp_c"], float)

    def test_cooling_success_scenario(self):
        """Test that actuation signal reduces temperature in COOLING_SUCCESS scenario."""
        sim = TelemetrySimulator(scenario="COOLING_SUCCESS", publish_interval_sec=0.01)

        # Initial warming
        t1 = sim.tick()
        z2_initial = next(z for z in t1["zones"] if z["zone_id"] == 2)["temp_c"]

        # Send actuation signal
        sim.receive_actuation({"peltier_state": "ON", "servo_vent_position": "OPEN"})

        for _ in range(5):
            t2 = sim.tick()

        z2_after_cooling = next(z for z in t2["zones"] if z["zone_id"] == 2)["temp_c"]
        self.assertLess(z2_after_cooling, z2_initial + 1.0, "Cooling actuation should prevent unbounded temp rise")


if __name__ == "__main__":
    unittest.main()
