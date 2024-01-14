import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Ajoutez cette ligne pour activer le support CORS

def read_config_file():
    config_path = os.path.join(os.pardir, 'config.txt')
    with open(config_path, 'r') as file:
        lines = file.readLines()
    return [line.strip() for line in lines]

@app.route('/mac')
def get_mac():
    config_elements = read_config_file()
    #elements = ['element 1', 'element 2', 'element 3']
    print("****************PULL_LIST*****************")
    return jsonify(config_elements)

@app.route('/add')
def add():
    from connexion_bluetooth import pairable, maj_config
    mac_address = pairable()
    maj_config(mac_address)
    print("****************APAIRING*****************")
    return jsonify(mac_address)

@app.route('/open')
def open():
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
    client.publish(client.TOPIC_GATE, json.dumps(['True'])
    client.loop_stop()
    print("****************OPEN*****************")
    return jsonify(200)
    #if result.rc == MQTTClient.MQTT_ERR_SUCCESS:
        # Message was successfully published
     #   client.loop_stop()
     #   print("****************OPEN*****************")
     #   return jsonify(200)
    #else:
        # There was an error publishing the message
     #   client.loop_stop()
     #   return jsonify('error: Failed to publish message')

@app.route('/delete/<mac>')
def dynamic_route(mac):
    print("****************DELETE*****************")
    print(mac)
    config_path = os.path.join(os.pardir, 'config.txt')
    with open(config_path, 'r') as config_file:
        config_macs = [line.strip() for line in config_file]

    if mac in config_macs:
        config_macs.remove(mac)

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(config_macs))

        print(f"Adresse MAC {mac} supprimée avec succès.")
        return jsonify({"mac_supprimee": mac})
    else:
        print(f"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration.")
        return jsonify({"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration."})

if __name__ == '__main__':
    port = 9001
    app.run(host='0.0.0.0', port=port, debug=True)
    print("Serveur en cours d execution")
