from envparse import env
import os
import time
import bluetooth
import json
#import keyboard
#from pynput import keyboard

from mqtt_server import MQTTClient

#def on_press(key):
#       try:
#               # Vérifiez si la touche "B" est pressée
#               if key.char == 'b':
#                       print("Touche B enfoncée. Envoi de True dans le topic GATE.")
#                       client.publish(client.TOPIC_GATE, 'True')
#       except AttributeError:
#               pass

def is_registered(client, userdata, msg):
    # Lire les adresses MAC du fichier config
    config_file_path = 'config.txt'
    with open(config_file_path, 'r') as config_file:
        config_macs = [line.strip() for line in config_file]

    received_data = json.loads(msg.payload.decode('utf8'))
    received_macs = [device["Address"] for device in received_data]
    print("Liste des adresses MAC reçue : ", received_macs)

    # Filtrer les adresses MAC qui sont à la fois dans le message MQTT et le fichier de configuration
    matching_macs = list(set(received_macs) & set(config_macs))
    print("Adresses MAC correspondantes : ", matching_macs)
    client.publish(client.TOPIC_GATE, json.dumps(matching_macs))

#def mock_first_connection(client, userdata, msg):
#       liste_mac = ["00:11:22:33:44:55", "66:77:88:99:AA:BB"]
#       bluetooth_scan.enregistrer_device(liste_mac)

def first_connection(client, userdata, msg):
    from connexion_bluetooth import pairable, maj_config
    mac_address = pairable()
    maj_config(mac_address)

#i = 0

# Parse environment variables to get MQTT broker parameters
DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']

if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

# Start a connexion to the MQTT broker
QOS = 0
client = MQTTClient("controler", MQTT_HOST, MQTT_PORT, QOS)
client.loop_start() # start client in a dedicated thread to

# S'abonne au topic de requêtes du portail
client.message_callback_add(client.TOPIC_REQUEST, is_registered)

# S'abonne au topic pour savoir si l'on doit faire la première connexion d'un device
client.message_callback_add(client.TOPIC_BLUETOOTH, first_connection)

#with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    # Le programme reste en cours d'exécution
#    listener.join()

while True:
        time.sleep(1)
        #i += 1
        #if i == 20:
        #       i = 0
        #       client.publish(client.TOPIC_GATE, 'True')

        # Mock du bouton pour demander d'ouvrir le portail depuis le boitier
        #if keyboard.is_pressed('B'):
        #       print("J'appuie sur le bouton pour ouvrir le portail à distance")
        #       client.publish(client.TOPIC_GATE, 'True')

# End connexion to MQTT broker before exiting
client.loop_stop()