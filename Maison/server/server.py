import builtins
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from mqtt_server import MQTTClient
from maison import serveur_publi

app = Flask(__name__)
CORS(app)  # Ajoutez cette ligne pour activer le support CORS

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
    serveur_publi('archi/pair', json.dumps(['True']))
    return jsonify(200)

@app.route('/open')
def open():
    print("****************OPEN*****************")
    serveur_publi('archi/gate', json.dumps(['True']))
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

        print(f"Adresse MAC {mac} supprimée avec succès.")
        return jsonify({"mac_supprimee": mac})
    else:
        print(f"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration.")
        return jsonify({"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration."})

if __name__ == '__main__':
    port = 9001
    app.run(host='0.0.0.0', port=port, debug=True)
    print("Serveur en cours d execution")