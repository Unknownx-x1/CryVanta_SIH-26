import json
import os
from typing import Callable

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - exercised only when dependency is absent
    mqtt = None


TOPIC_TELEMETRY = "coldguard/telemetry"
TOPIC_FORECAST = "coldguard/forecast"
TOPIC_POTENCY = "coldguard/potency"
TOPIC_DECISION = "coldguard/decision"
TOPIC_ACTUATE = "coldguard/actuate"
TOPIC_NARRATION = "coldguard/narration"


SUBSCRIBE_TOPICS = (TOPIC_TELEMETRY, TOPIC_FORECAST, TOPIC_POTENCY)


class MqttDecisionClient:
    def __init__(
        self,
        on_message_payload: Callable[[str, dict], None],
        host: str | None = None,
        port: int | None = None,
    ):
        if mqtt is None:
            raise RuntimeError("paho-mqtt is not installed. Install requirements.txt first.")

        self.host = host or os.getenv("MQTT_HOST", "localhost")
        self.port = port or int(os.getenv("MQTT_PORT", "1883"))
        self.on_message_payload = on_message_payload
        self.client = mqtt.Client(client_id=os.getenv("MQTT_CLIENT_ID", "predictfuse-backend"))
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_json(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload), qos=1)

    def _on_connect(self, client, userdata, flags, reason_code):
        for topic in SUBSCRIBE_TOPICS:
            client.subscribe(topic, qos=1)

    def _on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        self.on_message_payload(message.topic, payload)
