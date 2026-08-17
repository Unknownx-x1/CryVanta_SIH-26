"""
PredictFuse - Task P1 Main Runner Script
Runs the Telemetry Simulator and Physics Prediction Engine together.
Supports CLI JSON streaming and MQTT broker integration.
"""

import sys
import time
import json
import argparse
from typing import Optional, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from simulator.telemetry_generator import TelemetrySimulator
from prediction.physics_engine import PhysicsPredictionEngine
from prediction.config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    TOPIC_TELEMETRY,
    TOPIC_FORECAST,
    TOPIC_POTENCY,
)

# Optional MQTT import
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False


class P1Runner:
    """Unified runner for Telemetry Generator + Physics Prediction Engine."""

    def __init__(self, scenario: str = "LOCALIZED_WARMING", interval_sec: float = 1.0, use_mqtt: bool = True):
        self.simulator = TelemetrySimulator(scenario=scenario, publish_interval_sec=interval_sec)
        self.engine = PhysicsPredictionEngine()
        self.use_mqtt = use_mqtt and HAS_MQTT
        self.mqtt_client: Optional[Any] = None

        if self.use_mqtt:
            try:
                self.mqtt_client = mqtt.Client(client_id="P1_Simulator_Physics_Engine")
                self.mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
                self.mqtt_client.loop_start()
                print(f"[P1 Runner] Connected to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            except Exception as e:
                print(f"[P1 Runner] Warning: Could not connect to MQTT Broker ({e}). Falling back to CLI mode.")
                self.use_mqtt = False

    def run(self, max_steps: Optional[int] = None):
        """Main execution loop."""
        print(f"\n========================================================")
        print(f"       PREDICTFUSE TASK P1 - SIMULATOR & AI ENGINE       ")
        print(f" Scenario: {self.simulator.scenario} | Interval: {self.simulator.interval}s | MQTT: {self.use_mqtt}")
        print(f"========================================================\n")

        steps = 0
        try:
            for telemetry in self.simulator.run_generator(max_steps=max_steps):
                steps += 1
                # Process physics prediction
                forecast, potency = self.engine.process_telemetry(telemetry)

                # Output to MQTT if enabled
                if self.use_mqtt and self.mqtt_client:
                    self.mqtt_client.publish(TOPIC_TELEMETRY, json.dumps(telemetry))
                    self.mqtt_client.publish(TOPIC_FORECAST, json.dumps(forecast))
                    self.mqtt_client.publish(TOPIC_POTENCY, json.dumps(potency))

                # Print CLI output
                print(f"--- [Step {steps}] {telemetry['timestamp']} ---")
                print(f"[Telemetry]  Ambient {telemetry['ambient']['temp_c']}°C | Zones: {[z['temp_c'] for z in telemetry['zones']]}")
                print(f"[Forecast]   Projected Temps {[z['projected_temp_c'] for z in forecast['zones']]}°C | Time to Threshold: {[z['time_to_threshold_sec'] for z in forecast['zones']]}s")
                print(f"[Potency]    Overall {potency['overall_potency_pct']}% | Zone Potencies: {[z['potency_pct'] for z in potency['zones']]}\n")

        except KeyboardInterrupt:
            print("\n[P1 Runner] Simulation stopped by user.")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="PredictFuse Task P1 Runner")
    parser.add_argument(
        "--scenario",
        choices=["NORMAL", "LOCALIZED_WARMING", "COOLING_SUCCESS", "COOLING_FAILURE"],
        default="LOCALIZED_WARMING",
        help="Simulation scenario to execute",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="Publish interval in seconds")
    parser.add_argument("--steps", type=int, default=5, help="Number of steps to run (0 for infinite)")
    parser.add_argument("--no-mqtt", action="store_true", help="Disable MQTT and run CLI-only mode")

    args = parser.parse_args()
    steps = None if args.steps <= 0 else args.steps

    runner = P1Runner(scenario=args.scenario, interval_sec=args.interval, use_mqtt=not args.no_mqtt)
    runner.run(max_steps=steps)


if __name__ == "__main__":
    main()
