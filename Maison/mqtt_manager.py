import paho.mqtt.client as mqtt

MQTT_HOST = "192.168.80.5"
MQTT_PORT = 1883


class MQTTManager:
    client = None

    def __init__(self, name):
        self.client = mqtt.Client(name)  # Create instance of client with client ID “digi_mqtt_test”
        self.client.on_connect = self.on_connect  # Define callback function for successful connection
        self.client.on_message = self.on_message  # Define callback function for receipt of a message
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        # client.loop_forever()  # Start networking daemon
        # Créez une instance de la classe CameraManager
        # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

    def on_connect(self, client, userdata, flags, rc):  # The callback for when the client connects to the broker
        # Print result of connection attempt
        print("Connected with resultcode {0}".format(str(rc)))
        # Subscribe to the topic “digitest/test1”, receive any messages published on it
        client.subscribe("archi/devices", qos=2)
        client.subscribe("archi/bluetooth", qos=2)
        client.subscribe("archi/request", qos=2)

    def publish(self, topic, msg):
        print("Publishing on topic '{}': '{}'".format(topic, msg))
        return self.client.publish(topic, msg)

    def on_message(self, client, userdata, msg):
        from maison import is_registered, devices, first_connection
        print("Message received-> " + msg.topic)  # Print a received msg
        if msg.topic == "archi/devices":
            devices(msg.payload.decode())
        elif msg.topic == "archi/bluetooth":
            first_connection()
        else:
            is_registered(self.client,msg.payload.decode())

    def loop(self):
        self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()

    def loop_stop(self):
        self.client.loop_stop()