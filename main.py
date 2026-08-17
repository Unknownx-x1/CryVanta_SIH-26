import os

from fastapi import FastAPI, HTTPException

from actuation import create_actuation_from_decision
from decision_engine import create_decision_from_forecast
from mqtt_client import TOPIC_ACTUATE, TOPIC_DECISION, TOPIC_FORECAST, TOPIC_POTENCY, TOPIC_TELEMETRY, MqttDecisionClient
from schemas import ActuationCommand, Decision, Forecast, Potency, Telemetry


app = FastAPI(title="PredictFuse Backend / Decision Service", version="1.0.0")

state = {
    "telemetry": None,
    "forecast": None,
    "potency": None,
    "decision": None,
    "actuation": None,
}
mqtt_client = None


def process_forecast(forecast: dict) -> tuple[dict, dict]:
    state["forecast"] = forecast
    decision = create_decision_from_forecast(forecast, state["telemetry"])
    actuation = create_actuation_from_decision(decision)
    state["decision"] = decision
    state["actuation"] = actuation

    if mqtt_client is not None:
        mqtt_client.publish_json(TOPIC_DECISION, decision)
        mqtt_client.publish_json(TOPIC_ACTUATE, actuation)

    return decision, actuation


def handle_mqtt_payload(topic: str, payload: dict):
    if topic == TOPIC_TELEMETRY:
        state["telemetry"] = Telemetry(**payload).dict()
    elif topic == TOPIC_FORECAST:
        forecast = Forecast(**payload).dict()
        process_forecast(forecast)
    elif topic == TOPIC_POTENCY:
        state["potency"] = Potency(**payload).dict()


@app.on_event("startup")
def startup():
    global mqtt_client
    if os.getenv("MQTT_ENABLED", "false").lower() != "true":
        return

    try:
        mqtt_client = MqttDecisionClient(handle_mqtt_payload)
        mqtt_client.connect()
    except RuntimeError:
        mqtt_client = None


@app.on_event("shutdown")
def shutdown():
    if mqtt_client is not None:
        mqtt_client.disconnect()


@app.get("/health")
def health():
    return {"status": "ok", "service": "backend-decision"}


@app.get("/state")
def get_state():
    return state


@app.post("/telemetry", response_model=Telemetry)
def ingest_telemetry(payload: Telemetry):
    state["telemetry"] = payload.dict()
    return payload


@app.post("/potency", response_model=Potency)
def ingest_potency(payload: Potency):
    state["potency"] = payload.dict()
    return payload


@app.post("/forecast")
def ingest_forecast(payload: Forecast):
    if not payload.zones:
        raise HTTPException(status_code=400, detail="Forecast must contain at least one zone.")

    decision, actuation = process_forecast(payload.dict())
    return {
        "decision": Decision(**decision),
        "actuation": ActuationCommand(**actuation),
    }
