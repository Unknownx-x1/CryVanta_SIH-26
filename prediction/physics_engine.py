"""
PredictFuse - Physics Prediction & Potency Engine
Applies Newton's Law of Cooling, calculates projected temperatures, solves time-to-threshold,
and estimates pharmaceutical potency degradation.
Adheres to coldguard/forecast and coldguard/potency schemas in SYSTEM_CONTRACT.md.
"""

from datetime import datetime, timezone
from collections import deque
from typing import Dict, List, Any, Tuple

try:
    from prediction.config import (
        TEMP_TARGET_MAX,
        TEMP_CRITICAL_THRESHOLD,
        FORECAST_LOOKAHEAD_SEC,
        NEWTON_COOLING_DEFAULT_K,
        POTENCY_DECAY_BASE_RATE,
    )
except ImportError:
    from config import (
        TEMP_TARGET_MAX,
        TEMP_CRITICAL_THRESHOLD,
        FORECAST_LOOKAHEAD_SEC,
        NEWTON_COOLING_DEFAULT_K,
        POTENCY_DECAY_BASE_RATE,
    )


class PhysicsPredictionEngine:
    """
    Physics & AI prediction engine for cold-chain thermal excursion analysis.
    """

    def __init__(self, history_window_size: int = 10):
        self.window_size = history_window_size
        # Per-zone history: deque of (timestamp_epoch, temp_c)
        self.zone_history: Dict[int, deque] = {}
        # Per-zone cumulative potency loss (%)
        self.zone_potency_loss: Dict[int, float] = {}

    def process_telemetry(self, telemetry: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Consumes a telemetry payload, updates thermal models, and returns
        (forecast_payload, potency_payload).
        """
        timestamp_str = telemetry.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        ambient_temp_c = telemetry.get("ambient", {}).get("temp_c", 6.2)
        zones = telemetry.get("zones", [])

        forecast_zones = []
        potency_zones = []
        overall_potency_list = []

        # Parse timestamp epoch for rate calculation
        try:
            ts_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            ts_epoch = ts_dt.timestamp()
        except Exception:
            ts_epoch = datetime.now(timezone.utc).timestamp()

        for z in zones:
            z_id = z["zone_id"]
            current_temp = z["temp_c"]

            if z_id not in self.zone_history:
                self.zone_history[z_id] = deque(maxlen=self.window_size)
                self.zone_potency_loss[z_id] = 0.0

            # Store current point in sliding history
            history = self.zone_history[z_id]
            history.append((ts_epoch, current_temp))

            # 1. Fit per-zone warming rate (°C per minute)
            warming_rate_c_per_min = self._calculate_warming_rate(history)

            # 2. Project temperature using Newton's Law of Cooling model
            projected_temp_c = self._predict_future_temperature(
                current_temp=current_temp,
                ambient_temp=ambient_temp_c,
                warming_rate_c_per_min=warming_rate_c_per_min,
                lookahead_sec=FORECAST_LOOKAHEAD_SEC,
            )

            # 3. Calculate Time to Critical Threshold (12.0°C)
            time_to_threshold_sec = self._calculate_time_to_threshold(
                current_temp=current_temp,
                warming_rate_c_per_min=warming_rate_c_per_min,
                target_threshold=TEMP_CRITICAL_THRESHOLD,
            )

            # 4. Calculate Potency Loss
            self._update_potency_loss(z_id, current_temp)
            current_potency_pct = max(0.0, min(100.0, 100.0 - self.zone_potency_loss[z_id]))
            overall_potency_list.append(current_potency_pct)

            forecast_zones.append({
                "zone_id": z_id,
                "current_temp_c": round(current_temp, 1),
                "projected_temp_c": round(projected_temp_c, 1),
                "time_to_threshold_sec": int(time_to_threshold_sec),
                "warming_rate_c_per_min": round(warming_rate_c_per_min, 2),
            })

            potency_zones.append({
                "zone_id": z_id,
                "potency_pct": round(current_potency_pct, 1),
            })

        forecast_payload = {
            "timestamp": timestamp_str,
            "zones": forecast_zones,
        }

        overall_potency_pct = (
            sum(overall_potency_list) / len(overall_potency_list)
            if overall_potency_list
            else 100.0
        )

        potency_payload = {
            "timestamp": timestamp_str,
            "overall_potency_pct": round(overall_potency_pct, 1),
            "zones": potency_zones,
        }

        return forecast_payload, potency_payload

    def _calculate_warming_rate(self, history: deque) -> float:
        """Calculates smoothed temperature rate of change in °C/min."""
        if len(history) < 2:
            return 0.0

        t0, temp0 = history[0]
        t1, temp1 = history[-1]
        dt_sec = t1 - t0

        if dt_sec <= 0.5:
            return 0.0

        dt_min = dt_sec / 60.0
        d_temp = temp1 - temp0
        raw_rate = d_temp / dt_min

        # Clamp realistic physical warming/cooling rate limits (-3.0 to +3.0 °C/min)
        clamped_rate = max(-3.0, min(3.0, raw_rate))
        return clamped_rate

    def _predict_future_temperature(
        self,
        current_temp: float,
        ambient_temp: float,
        warming_rate_c_per_min: float,
        lookahead_sec: float,
    ) -> float:
        """
        Projects temperature using damped rate trend & Newton's Law relaxation towards ambient.
        """
        # Lookahead in minutes
        lookahead_min = lookahead_sec / 60.0

        if warming_rate_c_per_min > 0.05:
            # Active warming trend: linear growth damped towards ambient / realistic upper limit
            projected = current_temp + (warming_rate_c_per_min * lookahead_min * 0.5)
        else:
            # Newton's Law relaxation towards ambient
            k = NEWTON_COOLING_DEFAULT_K
            projected = ambient_temp + (current_temp - ambient_temp) * (2.71828 ** (-k * lookahead_sec))

        # Clamp max realistic projected temperature for realistic cold-chain bounds
        return max(0.0, min(25.0, projected))

    def _calculate_time_to_threshold(
        self,
        current_temp: float,
        warming_rate_c_per_min: float,
        target_threshold: float,
    ) -> float:
        """
        Solves for seconds remaining until current_temp reaches target_threshold.
        Returns capped 1200 seconds if stable/cooling or already breached.
        """
        if current_temp >= target_threshold:
            return 0.0

        if warming_rate_c_per_min <= 0.01:
            return 1200.0  # Safe / stable ceiling

        temp_needed = target_threshold - current_temp
        minutes_needed = temp_needed / warming_rate_c_per_min
        seconds_needed = minutes_needed * 60.0

        return max(0.0, min(1200.0, seconds_needed))

    def _update_potency_loss(self, zone_id: int, current_temp: float):
        """Accumulates thermal degradation loss if temperature exceeds safe ceiling (8.0°C)."""
        if current_temp > TEMP_TARGET_MAX:
            excursion_delta = current_temp - TEMP_TARGET_MAX
            # Degradation rate grows exponentially with thermal excess
            loss_increment = POTENCY_DECAY_BASE_RATE * (excursion_delta ** 1.2) * 5.0  # per step scaling
            self.zone_potency_loss[zone_id] += loss_increment


if __name__ == "__main__":
    print("--- Running Physics Engine Standalone Test ---")
    engine = PhysicsPredictionEngine()
    dummy_telemetry = {
        "timestamp": "2026-08-17T10:28:44Z",
        "ambient": {"temp_c": 6.2, "humidity_pct": 41.0},
        "gps": {"lat": 12.9716, "lng": 77.5946},
        "zones": [
            {"zone_id": 1, "temp_c": 5.8, "fuse_triggered": False},
            {"zone_id": 2, "temp_c": 9.1, "fuse_triggered": True, "vial_id": "V17", "fuse_level": 2, "trigger_temp_c": 15.0},
        ],
    }

    forecast, potency = engine.process_telemetry(dummy_telemetry)
    import json
    print("Forecast Output:\n", json.dumps(forecast, indent=2))
    print("Potency Output:\n", json.dumps(potency, indent=2))
