import json
import time
import math
import random
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "mqtt_broker")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

VEHICLES = {
    "BUS-001": {
        "start_lat": 12.9716,
        "start_lng": 77.5946,
        "end_lat": 12.9352,
        "end_lng": 77.6245,
        "current_step": 0,
        "total_steps": 100,
    },
    "BUS-002": {
        "start_lat": 13.0827,
        "start_lng": 80.2707,
        "end_lat": 13.0569,
        "end_lng": 80.2425,
        "current_step": 0,
        "total_steps": 100,
    },
}


def interpolate_position(start_lat, start_lng, end_lat, end_lng, step, total_steps):
    t = step / total_steps
    lat = start_lat + (end_lat - start_lat) * t
    lng = start_lng + (end_lng - start_lng) * t
    lat += random.uniform(-0.0002, 0.0002)
    lng += random.uniform(-0.0002, 0.0002)
    return lat, lng


def simulate_speed(step, total_steps):
    base_speed = 40.0
    variation = math.sin(step * 0.1) * 15
    noise = random.uniform(-5, 5)
    return max(0, base_speed + variation + noise)


def run_simulator():
    client = mqtt.Client(client_id="gps_simulator")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    logger.info("🚌 GPS Simulator started...")

    try:
        while True:
            for vehicle_id, config in VEHICLES.items():
                step = config["current_step"]
                total = config["total_steps"]

                lat, lng = interpolate_position(
                    config["start_lat"], config["start_lng"],
                    config["end_lat"], config["end_lng"],
                    step, total
                )

                speed = simulate_speed(step, total)
                heading = random.uniform(0, 360)

                payload = {
                    "latitude": round(lat, 6),
                    "longitude": round(lng, 6),
                    "speed": round(speed, 2),
                    "heading": round(heading, 2),
                    "altitude": round(random.uniform(900, 950), 2),
                    "accuracy": round(random.uniform(5, 15), 2),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }

                topic = f"vehicle/{vehicle_id}/gps"
                client.publish(topic, json.dumps(payload))
                logger.info(f"📍 Published to {topic}: ({lat:.6f}, {lng:.6f}) {speed:.1f}km/h")

                config["current_step"] = (step + 1) % total

            time.sleep(3)

    except KeyboardInterrupt:
        logger.info("🛑 Simulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run_simulator()