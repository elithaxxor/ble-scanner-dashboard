import json
import logging
import os

try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover - optional dependency
    mqtt = None

logger = logging.getLogger(__name__)
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ble/events")
MQTT_TLS = os.getenv("MQTT_TLS", "0") == "1"
MQTT_TLS_CA = os.getenv("MQTT_TLS_CA")
MQTT_TLS_CERT = os.getenv("MQTT_TLS_CERT")
MQTT_TLS_KEY = os.getenv("MQTT_TLS_KEY")
_client = mqtt.Client() if mqtt else None


def setup() -> None:
    if _client is None:
        logger.warning("paho-mqtt not installed; MQTT disabled")
        return
    try:
        if MQTT_TLS:
            _client.tls_set(ca_certs=MQTT_TLS_CA, certfile=MQTT_TLS_CERT, keyfile=MQTT_TLS_KEY)
        _client.connect(MQTT_BROKER)
        _client.loop_start()
        logger.info("Connected to MQTT broker %s", MQTT_BROKER)
    except Exception as exc:
        logger.error("MQTT connect failed: %s", exc)


def publish_event(event: dict) -> None:
    if _client is None:
        return
    try:
        payload = json.dumps(event)
        _client.publish(MQTT_TOPIC, payload)
    except Exception as exc:
        logger.error("MQTT publish failed: %s", exc)
