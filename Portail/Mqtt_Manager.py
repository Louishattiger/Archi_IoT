import paho.mqtt.client as mqtt
import ast

MQTT_HOST = "192.168.80.177"
MQTT_PORT = 2883  # 1884


class Mqtt_Manager:
    client = None

    def __init__(self):
        self.client = mqtt.Client("Portail")  # Create instance of client with client ID “digi_mqtt_test”
        self.client.on_connect = self.on_connect  # Define callback function for successful connection
        self.client.on_message = self.on_message  # Define callback function for receipt of a message
        # client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        # client.loop_forever()  # Start networking daemon
        # Créez une instance de la classe CameraManager
        # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

    def start_listening(self):
        print("Début de l'écoute sur le Broker...")
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()
        print("Fin de l'écoute sur le Broker.")

    def on_connect(self, client, userdata, flags, rc):  # The callback for when the client connects to the broker
        # Print result of connection attempt
        print("Connected with resultcode {0}".format(str(rc)))
        # Subscribe to the topic “digitest/test1”, receive any messages published on it
        client.subscribe("archi/gate")

    def on_message(self, client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
        from scan_bluetooth import broker_response
        print("Message received-> " + msg.topic)  # Print a received msg
        broker_response(ast.literal_eval(msg.payload.decode()))

    def publish(self, topic, msg):
        print("Publishing on topic '{}': '{}'".format(topic, msg))
        self.client.publish(topic, msg)
