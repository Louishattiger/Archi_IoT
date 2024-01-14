import logging
import paho.mqtt.client as mqtt


class MQTTClient(mqtt.Client):

    # topics
    TOPIC_REQUEST = "archi/request"
    TOPIC_GATE = "archi/gate"
    # topic uniquement pour simuler le bouton de première connexion bluetooth
    TOPIC_BLUETOOTH = "archi/bluetooth"

    def __init__(self, client_id, host, port=1883, keepalive=60, qos=0, **kwargs):
        super(MQTTClient, self).__init__(
            client_id=client_id, clean_session=True, **kwargs)
        self.qos = qos
        super().connect(host, port)
        logging.info("Connected to MQTT", flush=True)

    def on_connect(self, client, userdata, flags, rc):
        switcher = {
            1: 'incorrect protocol version',
            2: 'invalid client identifier',
            3: 'server unavailable',
            4: 'bad username or password',
            5: 'not authorised'
        }
        if (rc == 0):
            logging.info("MQTT broker connection OK.")
        else:
            logging.info("MQTT broker bad connection: %s",
                         switcher.get(rc, "Unknown return code"))

    def on_disconnect(self, client, userdata, rc):
        logging.info("MQTT broker disconnecting: " + str(rc))
        logging.info("MQTT broker: will automatically reconnect")

    def message_callback_add(self, topic, callback, qos=None):
        super().message_callback_add(topic, callback)
        if (qos):
            self.subscribe(topic, qos)
        else:
            self.subscribe(topic, self.qos)