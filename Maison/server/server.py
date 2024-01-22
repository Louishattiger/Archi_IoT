import builtins
import os
import json
import threading
from flask import Flask, jsonify
from werkzeug.serving import run_simple
from flask_cors import CORS
#from mqtt_server import MQTTClient
#from maison import serveur_publi

from mqtt_manager import MQTTManager

app = Flask(__name__)
CORS(app)  # Ajoutez cette ligne pour activer le support CORS
#client = None
#config_path = "config.txt"

def read_config_file():
    config_path = 'config.txt'
    with builtins.open(config_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

@app.route('/mac')
def get_mac():
    config_elements = read_config_file()
    print("****************PULL_LIST*****************")
    return jsonify(config_elements)

@app.route('/add')
def add():
    print("****************APAIRING*****************")
    print("Publication done ? ",client.publish('archi/pair', json.dumps(['True'])).is_published())
    return jsonify(200)

@app.route('/open')
def open():
    print("****************OPEN*****************")
    print("Publication done ? ",client.publish('archi/gate', json.dumps(['True'])).is_published())
    return jsonify(200)

@app.route('/delete/<mac>')
def dynamic_route(mac):
    print("****************DELETE*****************")
    print(mac)
    config_path = 'config.txt'
    with builtins.open(config_path, 'r') as config_file:
        config_macs = [line.strip() for line in config_file]

    if mac in config_macs:
        config_macs.remove(mac)

        with builtins.open(config_path, 'w') as config_file:
            config_file.write('\n'.join(config_macs))

        # Suppression de l'apparail dans les appairages du portail
        print("Publication done ? ",client.publish('archi/unpair', mac).is_published())

        print(f"Adresse MAC {mac} supprimée avec succès.")
        return jsonify({"mac_supprimee": mac})
    else:
        print(f"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration.")
        return jsonify({"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration."})

def run_flask_app():
    #port_number = 9001
    #app.run(host='0.0.0.0', port=port_number, debug=True)
    global client
    client = MQTTManager("Server")
    client.loop()
    print("Client lancé")

def run_app():
    print("Serveur en cours d execution")
    port = 9001
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    global client
    client = MQTTManager("Serveur")
#    client.loop_start()
#flask_thread = threading.Thread(target=run_flask_app)
#    flask_thread.start()
    run_app()
 #   run_simple('0.0.0.0', 9001, app, use_reloader=True)
    #flask_thread.join()
#    client.loop_stop()
    #print("Client lancé")