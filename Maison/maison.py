import json
from mqtt_manager import MQTTManager


# from mqtt_server import MQTTClient

def devices(msg):
    # Lire les adresses MAC du fichier config
    # received_data = json.loads(msg.payload.decode('utf8'))
    received_data = json.loads(msg)
    #print("received_data: ",received_data)
    received_macs = [device["Address"] for device in received_data]
    #print("Liste des adresses MAC reçue : ", received_macs)

    config_file_path = 'config.txt'
    existing_macs = set()
    try:
        with open(config_file_path, 'r') as existing_file:
            existing_macs = set(line.strip() for line in existing_file)
    except FileNotFoundError:
        pass  # Le fichier n'existe pas encore, c'est normal
    print(received_macs)
    new_macs = [mac for mac in received_macs if mac not in existing_macs]
    if new_macs:
        with open(config_file_path, 'a') as config_file:
            config_file.write('\n'.join(received_macs))
            config_file.write('\n')

# def is_registered(client, userdata, msg):
def is_registered(clientMqtt,msg):
    config_file_path = 'config.txt'
    with open(config_file_path, 'r') as file:
        adresses_mac_config = set(line.strip() for line in file)
        #print("adresse presente dans config: ", adresses_mac_config)
    # received_data = msg.payload.decode('utf8')
    received_data = json.loads(msg)
    #print("adresse recue: ",msg)
    received_macs = [device["Address"] for device in received_data]

    # Filtrer les éléments de la liste en fonction des adresses MAC
    resultats_filtres = [element for element in received_macs if element in adresses_mac_config]
    if (len(resultats_filtres) == 0):
        resultats_filtres = ['False']
    print(resultats_filtres)
    clientMqtt.publish('archi/gate', json.dumps(resultats_filtres))
    # client.publish(client.TOPIC_GATE, json.dumps(resultats_filtres))


# def first_connection(client, userdata, msg):
def first_connection():
    from connexion_bluetooth import pairable, maj_config
    mac_address = pairable()
    maj_config(mac_address)


#def serveur_publi(topic_name, msg):
#    client.publish(topic_name, msg)


# Parse environment variables to get MQTT broker parameters
# DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']

# if set(DOCKER_VARENV).issubset(set(os.environ)):
#   MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
#  MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
# else:
#   MQTT_HOST = 'localhost'
#  MQTT_PORT = 1883

# Start a connexion to the MQTT broker
# QOS = 0
# client = MQTTClient("controler", MQTT_HOST, MQTT_PORT, QOS)

# S'abonne au topic de requêtes du portail
# client.message_callback_add(client.TOPIC_REQUEST, is_registered)

# S'abonne au topic de devices du portail
# client.message_callback_add(client.TOPIC_DEVICES, devices)

# S'abonne au topic pour savoir si l'on doit faire la première connexion d'un device
# client.message_callback_add(client.TOPIC_BLUETOOTH, first_connection)
if __name__ == "__main__":
    global client
    client = MQTTManager("Maison")
    client.loop()