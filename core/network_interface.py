import json
import time
import logging

try:
    import paho.mqtt.client as mqtt
except ImportError:
    # Fallback mock for offline validation or non-network test environments
    mqtt = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosNetwork")

class HomeosMqttInterface:
    def __init__(self, broker_address="127.0.0.1", port=1883, client_id="homeos_core"):
        """
        Initializes the MQTT telemetry broadcasting engine.
        Configured by default for local-first, low-latency loopbacks.
        """
        self.broker = broker_address
        self.port = port
        self.client_id = client_id
        self.is_mock = mqtt is None
        self.connected = False

        if not self.is_mock:
            self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
        else:
            logger.warning("paho-mqtt missing or unreachable. Operating in Simulation-Only mode.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Successfully bound to local MQTT broker network topology.")
        else:
            logger.error(f"MQTT binding failure. Connection rejected with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning("Disconnected from MQTT network broker channel.")

    def connect_loop(self):
        """Establishes non-blocking network connection loops."""
        if self.is_mock:
            self.connected = True
            return True
        try:
            self.client.connect_async(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize network sockets: {str(e)}")
            return False

    def broadcast_telemetry_packet(self, status_flag, equilibrium_index, strain, temperature, flux_leakage):
        """
        Serializes and broadcasts live metrics to the local automation network.
        Topic maps to standard Home Assistant MQTT Discovery topologies.
        """
        payload = {
            "timestamp": int(time.time()),
            "status_flag": status_flag,
            "global_equilibrium": round(equilibrium_index, 4),
            "hull_strain_index": round(strain, 6),
            "core_temperature_c": round(temperature, 2),
            "magnetic_flux_leakage_t": round(flux_leakage, 4)
        }

        json_payload = json.dumps(payload)
        topic = f"homeos/{self.client_id}/telemetry"

        if self.is_mock:
            logger.info(f"[MOCK BROADCAST] Topic: '{topic}' | Payload: {json_payload}")
            return True

        if not self.connected:
            logger.warning("Telemetry dropped: Broker socket offline.")
            return False

        try:
            result = self.client.publish(topic, json_payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed transmission execution across network space: {str(e)}")
            return False

    def terminate_session(self):
        """Gracefully tears down active threads and sockets."""
        if not self.is_mock:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT network engine session finalized.")
