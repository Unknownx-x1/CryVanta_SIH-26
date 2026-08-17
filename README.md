# PredictFuse Backend / Decision Service

PredictFuse is a pharmaceutical cold-chain safety prototype. The full system follows:

```text
Sense -> Predict -> Decide -> Act -> Verify -> Explain + Display
```

This repository currently contains the **Person 2** work from the roadmap: the backend and decision layer. It consumes telemetry/forecast data, calculates risk, chooses a route/action, and produces actuator commands that match `SYSTEM_CONTRACT.md`.

## What This Service Does

- Accepts telemetry, forecast, and potency payloads using the frozen system contract.
- Calculates `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` risk from time-to-threshold.
- Selects the most urgent affected zone.
- Generates a decision object for the dashboard/narration layer.
- Generates an actuation command for the ESP32/simulator.
- Can run through REST endpoints, and can optionally connect to MQTT.

## Project Files

```text
main.py             FastAPI backend and request handlers
schemas.py          Pydantic models for SYSTEM_CONTRACT payloads
risk_engine.py      Risk-level calculation
decision_engine.py  Route/action decision logic
actuation.py        ESP32 actuator command generation
mqtt_client.py      MQTT topic constants and MQTT JSON client
test.py             Risk-engine tests
test_decision.py    Decision-engine tests
test_actuation.py   Actuation tests
SYSTEM_CONTRACT.md  Frozen topic and payload contract
```

## Setup

Create/activate a virtual environment if you want one, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Backend

```bash
python -m uvicorn main:app --reload
```

If port `8000` is busy:

```bash
python -m uvicorn main:app --reload --port 8001
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## REST Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check if the service is alive |
| `GET` | `/state` | View latest telemetry, forecast, potency, decision, and actuation |
| `POST` | `/telemetry` | Store latest ESP32/simulator telemetry |
| `POST` | `/potency` | Store latest potency estimate |
| `POST` | `/forecast` | Run decision logic and return decision + actuation |

## Quick Forecast Test

```bash
curl -X POST http://127.0.0.1:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Expected behavior:

- Zone `2` is selected as the primary affected zone.
- Risk becomes `HIGH`.
- Decision action becomes `COOLING_ON_SERVO_OPEN`.
- Actuation turns Peltier `ON`, servo vent `OPEN`, and buzzer `ON`.

## MQTT Mode

By default, MQTT is disabled so the REST backend can run without a broker.

To enable MQTT, start a broker such as Mosquitto, then run:

```bash
MQTT_ENABLED=true python -m uvicorn main:app --reload
```

Optional environment variables:

```bash
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_CLIENT_ID=predictfuse-backend
```

Subscribed topics:

```text
coldguard/telemetry
coldguard/forecast
coldguard/potency
```

Published topics:

```text
coldguard/decision
coldguard/actuate
```

## Run Tests

```bash
python -m unittest test.py test_decision.py test_actuation.py
python -m py_compile risk_engine.py decision_engine.py actuation.py schemas.py mqtt_client.py main.py
```

## Contract Notes

Keep payloads aligned with `SYSTEM_CONTRACT.md`:

- Timestamps should use UTC `Z` format, for example `2026-08-17T10:28:44Z`.
- Topic names and field names are frozen.
- Enum values must match exactly, including uppercase spelling.
- Optional fields should be `null`, not omitted, when sending full contract payloads.
