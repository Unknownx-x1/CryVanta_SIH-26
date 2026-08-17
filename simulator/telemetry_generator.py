"""
PredictFuse - Telemetry Simulator
Generates continuous environmental telemetry, GPS route updates, and vial fuse events.
Adheres strictly to coldguard/telemetry schema in SYSTEM_CONTRACT.md.
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

try:
    from prediction.config import (
        TOPIC_TELEMETRY,
        TOPIC_ACTUATE,
        DEFAULT_AMBIENT_TEMP_C,
        DEFAULT_AMBIENT_HUMIDITY_PCT,
        TEMP_FUSE_TRIGGER_THRESHOLD,
    )
except ImportError:
    from config import (
        TOPIC_TELEMETRY,
        TOPIC_ACTUATE,
        DEFAULT_AMBIENT_TEMP_C,
        DEFAULT_AMBIENT_HUMIDITY_PCT,
        TEMP_FUSE_TRIGGER_THRESHOLD,
    )


class TelemetrySimulator:
    """
    Simulates multi-zone cold-chain box telemetry with 4 operational scenarios.
    """

    SCENARIOS = ["NORMAL", "LOCALIZED_WARMING", "COOLING_SUCCESS", "COOLING_FAILURE"]

    def __init__(self, scenario: str = "NORMAL", publish_interval_sec: float = 2.0):
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Allowed: {self.SCENARIOS}")

        self.scenario = scenario
        self.interval = publish_interval_sec
        self.step_count = 0

        # Base environment state
        self.ambient_temp_c = DEFAULT_AMBIENT_TEMP_C
        self.ambient_humidity_pct = DEFAULT_AMBIENT_HUMIDITY_PCT
        self.gps_lat = 12.9716
        self.gps_lng = 77.5946

        # Zone states
        self.zone_temps = {1: 5.5, 2: 5.8, 3: 5.2}
        self.fuse_triggered = {1: False, 2: False, 3: False}
        self.fuse_details = {}

        # Actuation state received from backend
        self.cooling_active = False

    def set_scenario(self, scenario: str):
        """Dynamically change the scenario."""
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Allowed: {self.SCENARIOS}")
        self.scenario = scenario
        self.step_count = 0

    def receive_actuation(self, payload: Dict[str, Any]):
        """Callback to handle actuation commands received from backend."""
        peltier_state = payload.get("peltier_state", "OFF")
        if peltier_state == "ON":
            self.cooling_active = True
        elif peltier_state == "OFF":
            self.cooling_active = False

    def tick(self) -> Dict[str, Any]:
        """
        Advances the simulation by one step and returns a JSON-compliant dict.
        """
        self.step_count += 1
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Simulate ambient slight fluctuations
        self.ambient_temp_c += 0.02 * (self.step_count % 3 - 1)
        self.ambient_humidity_pct = max(30.0, min(80.0, self.ambient_humidity_pct + (self.step_count % 2 - 0.5)))
        self.gps_lat += 0.0001
        self.gps_lng += 0.0001

        # Zone 1 and 3 stay stable in all scenarios
        self.zone_temps[1] = max(4.8, min(6.2, 5.5 + 0.1 * (self.step_count % 5 - 2)))
        self.zone_temps[3] = max(4.5, min(6.0, 5.2 + 0.1 * (self.step_count % 4 - 2)))

        # Handle Zone 2 according to active scenario
        if self.scenario == "NORMAL":
            self.zone_temps[2] = max(5.0, min(6.5, 5.8 + 0.1 * (self.step_count % 3 - 1)))

        elif self.scenario in ["LOCALIZED_WARMING", "COOLING_FAILURE"]:
            # Rapid localized warming in Zone 2
            self.zone_temps[2] += 0.35
            if self.zone_temps[2] >= TEMP_FUSE_TRIGGER_THRESHOLD and not self.fuse_triggered[2]:
                self.fuse_triggered[2] = True
                self.fuse_details[2] = {
                    "vial_id": "V17",
                    "fuse_level": 2,
                    "trigger_temp_c": round(self.zone_temps[2], 1),
                }

        elif self.scenario == "COOLING_SUCCESS":
            if not self.cooling_active and self.step_count <= 5:
                # Zone 2 starts warming before intervention
                self.zone_temps[2] += 0.4
            else:
                # Cooling intervention active or takes effect -> bring temp down
                self.zone_temps[2] = max(5.5, self.zone_temps[2] - 0.3)

        # Build zones payload
        zones_payload = []
        for z_id in sorted(self.zone_temps.keys()):
            z_data = {
                "zone_id": z_id,
                "temp_c": round(self.zone_temps[z_id], 1),
                "fuse_triggered": self.fuse_triggered[z_id],
            }
            if self.fuse_triggered[z_id] and z_id in self.fuse_details:
                z_data.update(self.fuse_details[z_id])
            zones_payload.append(z_data)

        telemetry = {
            "timestamp": now_iso,
            "ambient": {
                "temp_c": round(self.ambient_temp_c, 1),
                "humidity_pct": round(self.ambient_humidity_pct, 1),
            },
            "gps": {
                "lat": round(self.gps_lat, 4),
                "lng": round(self.gps_lng, 4),
            },
            "zones": zones_payload,
        }

        return telemetry

    def run_generator(self, max_steps: Optional[int] = None):
        """Generator yielding telemetry payloads sequentially."""
        steps = 0
        while True:
            if max_steps is not None and steps >= max_steps:
                break
            yield self.tick()
            steps += 1
            time.sleep(self.interval)


if __name__ == "__main__":
    print("--- Running Telemetry Simulator (Standalone Mode: LOCALIZED_WARMING) ---")
    sim = TelemetrySimulator(scenario="LOCALIZED_WARMING", publish_interval_sec=0.5)
    for i, payload in enumerate(sim.run_generator(max_steps=10)):
        print(f"Step {i+1}: {json.dumps(payload, indent=2)}")
