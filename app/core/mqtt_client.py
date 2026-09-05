import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import settings
from app.services.gps_service import process_gps_data

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id="gps_tracking_server")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(
                settings.MQTT_USERNAME,
                settings.MQTT_PASSWORD
            )

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ Connected to MQTT Broker")
            client.subscribe(settings.MQTT_GPS_TOPIC)
            logger.info(f"📡 Subscribed to topic: {settings.MQTT_GPS_TOPIC}")
        else:
            logger.error(f"❌ Failed to connect to MQTT, return code: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 3:
                logger.warning(f"Invalid topic format: {msg.topic}")
                return

            vehicle_code = topic_parts[1]
            payload = json.loads(msg.payload.decode("utf-8"))

            logger.info(f"📍 GPS data received for vehicle: {vehicle_code}")

            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                process_gps_data(vehicle_code=vehicle_code, payload=payload)
            )
            loop.close()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"⚠️ Disconnected from MQTT broker with code: {rc}")
        if rc != 0:
            logger.info("🔄 Attempting to reconnect...")

    def connect(self):
        try:
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=60
            )
            self.client.loop_start()
            logger.info("🚀 MQTT client started")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client disconnected")


mqtt_client = MQTTClient()