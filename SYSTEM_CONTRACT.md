# PredictFuse — System Data Contract (`SYSTEM_CONTRACT.md`)

> **Version**: 1.0.0  
> **Status**: Frozen  
> **Purpose**: Master communication interface & payload schemas across Hardware (ESP32/Simulator), Backend (FastAPI), AI/Prediction, Narration (LLM), and Dashboard (React UI).

---

## 1. Global Standards & Conventions

1. **Protocol**: MQTT over TCP / WebSockets.
2. **Data Format**: Standard JSON.
3. **Timestamps**: ISO-8601 UTC strings formatted as `YYYY-MM-DDTHH:MM:SSZ` (e.g., `"2026-08-17T10:28:44Z"`).
4. **Units of Measurement**:
   * **Temperature**: Degrees Celsius (`°C`)
   * **Humidity**: Percentage (`%`)
   * **Time**: Seconds (`sec`)
   * **Coordinates**: Decimal degrees (`lat`/`lng`)
   * **Potency**: Percentage (`%`, range `0.0` – `100.0`)
5. **Identifiers**:
   * `zone_id`: Integer (`1`, `2`, `3`, ...)
   * `vial_id`: String (e.g., `"V17"`)
   * `fuse_level`: Integer (`1`, `2`, `3`)

---

## 2. MQTT Topic Registry

| Topic Name | Publisher | Subscriber(s) | Description |
| :--- | :--- | :--- | :--- |
| `coldguard/telemetry` | ESP32 / Simulator (P1) | Backend (P2), Dashboard (P3) | Real-time sensor readings, GPS, & vial fuse state |
| `coldguard/forecast` | Prediction Engine (P1) | Backend (P2), Dashboard (P3) | Thermal forecasts, time-to-threshold per zone |
| `coldguard/potency` | Prediction Engine (P1) | Backend (P2), Dashboard (P3) | Estimated drug potency levels |
| `coldguard/decision` | Backend Engine (P2) | Narration (P4), Dashboard (P3) | Evaluated risk status & recommended actions |
| `coldguard/actuate` | Backend Engine (P2) | ESP32 / Simulator (P1) | Physical actuator execution commands |
| `coldguard/narration` | Narration Service (P4) | Dashboard (P3) | Human-readable system briefings |

---

## 3. Detailed JSON Schemas

### 3.1 Telemetry — `coldguard/telemetry`
**Published by**: `P1 Telemetry Simulator / ESP32`  
**Frequency**: Every 1–5 seconds

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "ambient": {
    "temp_c": 6.2,
    "humidity_pct": 41.0
  },
  "gps": {
    "lat": 12.9716,
    "lng": 77.5946
  },
  "zones": [
    {
      "zone_id": 1,
      "temp_c": 5.8,
      "fuse_triggered": false
    },
    {
      "zone_id": 2,
      "temp_c": 9.1,
      "fuse_triggered": true,
      "vial_id": "V17",
      "fuse_level": 2,
      "trigger_temp_c": 15.0
    }
  ]
}
```

---

### 3.2 Forecast — `coldguard/forecast`
**Published by**: `P1 Prediction / AI`  
**Frequency**: Every 3–5 seconds

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "zones": [
    {
      "zone_id": 1,
      "current_temp_c": 5.8,
      "projected_temp_c": 6.5,
      "time_to_threshold_sec": 1200,
      "warming_rate_c_per_min": 0.05
    },
    {
      "zone_id": 2,
      "current_temp_c": 9.1,
      "projected_temp_c": 12.4,
      "time_to_threshold_sec": 210,
      "warming_rate_c_per_min": 0.45
    }
  ]
}
```

---

### 3.3 Potency — `coldguard/potency`
**Published by**: `P1 Prediction / AI`  
**Frequency**: Every 5–10 seconds

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "overall_potency_pct": 98.4,
  "zones": [
    {
      "zone_id": 1,
      "potency_pct": 99.1
    },
    {
      "zone_id": 2,
      "potency_pct": 97.2
    }
  ]
}
```

---

### 3.4 Decision — `coldguard/decision`
**Published by**: `P2 Backend / Decision Engine`  
**Frequency**: Triggered on state change or risk update

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "risk_level": "HIGH",
  "primary_zone_affected": 2,
  "action_selected": "COOLING_ON_SERVO_OPEN",
  "recommended_route": "ALTERNATE_ROUTE_B",
  "vials_at_risk_count": 5,
  "reasoning": "Zone 2 projected to breach 12.0°C threshold in 210 seconds."
}
```

#### Allowed Enums for Decision:
* **`risk_level`**: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`
* **`action_selected`**: `"NONE"`, `"COOLING_ON"`, `"SERVO_OPEN"`, `"COOLING_ON_SERVO_OPEN"`, `"ALERT_ONLY"`
* **`recommended_route`**: `"CURRENT_ROUTE"`, `"ALTERNATE_ROUTE_A"`, `"ALTERNATE_ROUTE_B"`, `"IMMEDIATE_STOP"`

---

### 3.5 Actuation — `coldguard/actuate`
**Published by**: `P2 Backend / Decision Engine`  
**Target**: `ESP32 Smart Spine / Simulator`

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "target_zone_id": 2,
  "peltier_state": "ON",
  "servo_vent_position": "OPEN",
  "alert_buzzer": "ON"
}
```

#### Allowed Enums for Actuation:
* **`peltier_state`**: `"ON"`, `"OFF"`
* **`servo_vent_position`**: `"OPEN"`, `"CLOSED"`
* **`alert_buzzer`**: `"ON"`, `"OFF"`

---

### 3.6 Narration — `coldguard/narration`
**Published by**: `P4 LLM / Narration Service`  
**Frequency**: Triggered on risk change or fuse breach

```json
{
  "timestamp": "2026-08-17T10:28:44Z",
  "briefing": "Zone 2 localized warming detected (9.1°C). Time to threshold is 210 seconds. Peltier cooling and venting activated. Passive fuse card triggered for Vial V17 at 15.0°C.",
  "is_fallback": false
}
```

---

## 4. Responsibility & Ownership Matrix

| Feature / Artifact | Owner | Input Topic(s) | Output Topic(s) |
| :--- | :--- | :--- | :--- |
| **Telemetry Simulator** | **Person 1** | None / Config | `coldguard/telemetry` |
| **Thermal Forecast & Potency** | **Person 1** | `coldguard/telemetry` | `coldguard/forecast`, `coldguard/potency` |
| **Backend & Risk Logic** | **Person 2** | `coldguard/telemetry`, `coldguard/forecast` | `coldguard/decision`, `coldguard/actuate` |
| **React Dashboard UI** | **Person 3** | All Topics | UI Presentation |
| **LLM Narration & Testing** | **Person 4** | `coldguard/decision`, `coldguard/telemetry` | `coldguard/narration` |

---

## 5. Change Management Rules

1. No individual team member may modify field names or topic strings unilaterally.
2. Any breaking schema change must be proposed, approved by all 4 members, and versioned in `SYSTEM_CONTRACT.md`.
3. If an optional field is absent, it must be set to `null` rather than omitted from the JSON object.
