"""
PredictFuse - Task P1 Configuration & Constants
Central configuration for MQTT topics, thresholds, physics parameters, and data schemas.
"""

import os

# MQTT Broker Configuration
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_KEEPALIVE = 60

# MQTT Topics (from SYSTEM_CONTRACT.md)
TOPIC_TELEMETRY = "coldguard/telemetry"
TOPIC_FORECAST = "coldguard/forecast"
TOPIC_POTENCY = "coldguard/potency"
TOPIC_DECISION = "coldguard/decision"
TOPIC_ACTUATE = "coldguard/actuate"
TOPIC_NARRATION = "coldguard/narration"

# Thermal & Safety Thresholds (°C)
TEMP_TARGET_MIN = 2.0
TEMP_TARGET_MAX = 8.0
TEMP_CRITICAL_THRESHOLD = 12.0
TEMP_FUSE_TRIGGER_THRESHOLD = 15.0

# Zone Configuration
TOTAL_ZONES = 3
DEFAULT_AMBIENT_TEMP_C = 6.2
DEFAULT_AMBIENT_HUMIDITY_PCT = 41.0

# Physics Engine Parameters
FORECAST_LOOKAHEAD_SEC = 600  # 10 minutes lookahead window
NEWTON_COOLING_DEFAULT_K = 0.005  # Per-second cooling/warming rate constant
POTENCY_DECAY_BASE_RATE = 0.00005  # Degradation coefficient per °C above target per sec
