import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosNetworkBroker")

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None
    logger.warning("Paho-MQTT client missing. Local broker simulation fallback initialized.")

class HomeosMqttInterface:
    def __init__(self, broker_address="127.0.0.1", port=1883, client_id="homeos_core"):
        """
        Initializes the local network interface broker engine.
        Enforces standard subscription-free local topology configurations.
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

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Successfully connected to local MQTT telemetry broker.")
        else:
            self.connected = False
            logger.error(f"MQTT connection rejected by network broker. Status code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning("Network connection dropped from local MQTT broker.")

    def connect_loop(self):
        """ Initializes asynchronous network background loops. """
        if self.is_mock:
            self.connected = True
            logger.info("Mock network broker loop active. Local data container online.")
            return True
        try:
            self.client.connect_async(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to bind connection loop to local broker interface: {str(e)}")
            return False

    def broadcast_telemetry_packet(self, status_flag, equilibrium_index, strain, temperature, flux_leakage):
        """
        Packages and publishes a local state telemetry frame into JSON topic strings.
        """
        payload = {
            "timestamp": int(time.time()),
            "status_flag": status_flag,
            "global_equilibrium": round(equilibrium_index, 4),
            "hull_strain_index": round(strain, 6),
            "core_temperature_c": round(temperature, 2),
            "magnetic_flux_leakage_t": round(flux_leakage, 4)
        }
        
        if self.is_mock:
            logger.info(f"[LOCAL MONITOR LOOP BROADCAST] {json.dumps(payload)}")
            return True
            
        if not self.connected:
            logger.warning("Telemetry broadcast aborted: Network link state is disconnected.")
            return False
            
        try:
            target_topic = f"homeos/{self.client_id}/telemetry"
            result = self.client.publish(target_topic, json.dumps(payload), qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed to transmit JSON payload over local socket matrix: {str(e)}")
            return False
