import bluetooth
import time
import sys
import math
import json
import os
import subprocess
import re

rfcomm_ports_to_try = [1, 2, 3, 4, 5]

# Fonction pour extraire l'adresse MAC et le nom du périphérique
def extract_device_info(device_str):
    # Utilisation d'une expression régulière pour extraire l'adresse MAC et le nom
    match = re.match(r'Device (\S+) (.+)', device_str.decode('utf-8'))
    if match:
        address = match.group(1)
        alias = match.group(2)
        return {'Address': address, 'Alias': alias}
    else:
        return None

def open_gate():
    print("##### OUVERTURE DU PORTAIL #####")
    iteration = 0
    print("Output liés à l'utilisation de la LED PWR")
    # Set the PWR LED to GPIO mode (set 'off' by default).
    os.system("echo gpio | sudo tee /sys/class/leds/led1/trigger")
    while iteration <= 10:
        # (Optional) Turn on (1) or off (0) the PWR LED.
        os.system("echo 1 | sudo tee /sys/class/leds/led1/brightness")
        time.sleep(0.5)
        iteration += 1
    # Revert the PWR LED back to 'under-voltage detect' mode.
    os.system("echo input | sudo tee /sys/class/leds/led1/trigger")


def broker_response(addr_list):
    print("Call broker_response")
    for address in addr_list:
        print("Current address processing: ",address)
        if address == "True":
            open_gate()
        elif address != "False":
            #rfcomm_ports_to_try = [1, 2, 3, 4, 5]
            if connect_to_device(address,rfcomm_ports_to_try):
                return open_gate()

def pairable():
    from pairable_mode import Agent, Adapter, bus, AGENT_PATH, BUS_NAME, AGNT_MNGR_PATH, AGNT_MNGR_IFACE, CAPABILITY, disconnect_new_device
    import dbus
    import dbus.service
    import dbus.mainloop.glib
    from gi.repository import GLib

    PAIRING_TIME = 30 	# Temps durant lequel le device est en mode Pairing
    agent = Agent(bus, AGENT_PATH)
    agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
                               AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
    agnt_mngr.RequestDefaultAgent(AGENT_PATH)

    adapter = Adapter()
    mainloop = GLib.MainLoop()

    # Planifiez l'arrêt du mainloop après 10 secondes (ajustez selon vos besoins)
    GLib.timeout_add_seconds(60, lambda: mainloop.quit())
    print(f"Going pairing mode for {PAIRING_TIME} seconds")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(AGENT_PATH)
        mainloop.quit()
    #adapter.adapter_reset()
    disconnect_new_device()
    get_paired_devices()
    adapter.adapter_reset()

def get_paired_devices():
    try:
        # Exécute la commande bluetoothctl avec sudo
        result = subprocess.run(['sudo', 'bluetoothctl', 'devices'], capture_output=True)

        # Récupère la sortie de la commande (liste des périphériques Bluetooth)
        output_lines = result.stdout.splitlines()

        # Retourne la liste des périphériques Bluetooth
        #return output_lines

        paired_devices_str = [extract_device_info(device) for device in output_lines]

        # Filtrer les éléments None (qui n'ont pas pu être extraits)
        paired_devices_str = [info for info in paired_devices_str if info is not None]

        return paired_devices_str

    except subprocess.CalledProcessError as e:
        # Gère les erreurs lors de l'exécution de la commande
        print(f"Erreur lors de l'exécution de la commande bluetoothctl : {e}")
        return []

def unpair_device(device):
    try:
        # Exécute la commande bluetoothctl avec sudo
        result = subprocess.run(['sudo', 'bluetoothctl', 'remove', device], capture_output=True)

        # Récupère la sortie de la commande (liste des périphériques Bluetooth)
        output_lines = result.stdout.splitlines()

        print(output_lines)

    except subprocess.CalledProcessError as e:
        # Gère les erreurs lors de l'exécution de la commande
        print(f"Erreur lors de l'exécution de la commande bluetoothctl : {e}")
        return []


def scan_devices():
    print("Scanning for nearby Bluetooth devices...")
    nearby_devices = bluetooth.discover_devices(duration=3, flush_cache=True, lookup_names=True, lookup_class=True, device_id=-1, iac=10390323)
    devices_list = []
    if not nearby_devices:
        print("Aucun périphérique Bluetooth trouvé.")
    else:
        devices_list = [{"Address": addr, "Alias": name} for addr, name, _ in nearby_devices]
        print("Périphériques Bluetooth trouvés :")
        for device in devices_list:
            print(f"Adresse : {device['Address']}, Nom : {device['Alias']}")

    return devices_list

def connect_to_device(mac_address, service_ports):

    # Vérifiez d'abord si le périphérique est appairé (trusted)
    paired_devices = get_paired_devices()

    # Extrayez les adresses MAC de la liste des périphériques appairés
    paired_addresses = [device['Address'] for device in paired_devices]

    if mac_address not in paired_addresses:
        print(f"Le périphérique avec l'adresse MAC {mac_address} n'est pas appairé (trusted).")
        return False

    for port in service_ports:
        try:
            # Crée une socket Bluetooth
            socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            # Adresse du périphérique auquel vous souhaitez vous connecter
            target_address = mac_address

            # Tente de se connecter au périphérique sur le port RFCOMM spécifié
            socket.connect((target_address, port))

            print(f"Connecté au périphérique avec l'adresse MAC : {target_address} sur le port RFCOMM : {port}")

            # Vous pouvez maintenant envoyer et recevoir des données via la socket
            # Par exemple : socket.send("Hello, World!")

            # N'oubliez pas de fermer la connexion lorsque vous avez terminé
            socket.close()

            # Si la connexion réussit, sortir de la boucle
            # break
            return True

        except bluetooth.btcommon.BluetoothError as e:
            print(f"Erreur lors de la connexion au périphérique sur le port RFCOMM {port}: {e}")
            socket.close()
            if hasattr(e, 'errno') and e.errno == 112: # L'hôte est down (et donc pas besoin de tester les 5 ports)
                return False

    return False


def check_bluetooth_services():
    print("looking for nearby devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = 20)
    print("found %d devices" % len(nearby_devices))
    for addr, name in nearby_devices:
        print(" %s - %s" % (addr, name))
        for services in bluetooth.find_service(address = addr):
            print(" Name: %s" % (services["name"]))
            print(" Description: %s" % (services["description"]))
            print(" Protocol: %s" % (services["protocol"]))
            print(" Provider: %s" % (services["provider"]))
            print(" Port: %s" % (services["port"]))
            print(" Service id: %s" % (services["service-id"]))

def sleeping(iteration):
    print("Sleeping for 3s",end="")
    sys.stdout.flush()
    while iteration > 1:
        print(".",end="")
        sys.stdout.flush()
        iteration -= 1
        time.sleep(1)
    print(".")

def downgraded_mode(devices):
    print('##### SWITCHING TO DOWNGRADED MODE #####')
    adresses_mac = [objet[0] for objet in devices]
    for addr in adresses_mac:
        if connect_to_device(addr,rfcomm_ports_to_try): return open_gate()

if __name__ == "__main__":
    from Mqtt_Manager import Mqtt_Manager

    previous_devices = []	# Les appareils détectés dans les dernières DETECTION_LATENCY secondes
    SLEEPING_TIME = 3 	# Le temps entre chaque ecoute, en secondes
    DETECTION_LATENCY = 60 	# Le temps entre chaque différenciation de detection pour un meme device, en secondes
    iteration = 0		# Iteration d'un pas de SLEEPING_TIME dans la DETECTION_LATENCY
    mqttManager = Mqtt_Manager()
    paired_devices = []
    previous_paired_devices = []

    while True:
        paired_devices = get_paired_devices()
        #print("Paired devices: ", paired_devices,previous_paired_devices)
        #if len(paired_devices) == 0:
        #paired_devices = get_paired_devices()
        #previous_paired_devices = paired_devices
        if paired_devices != previous_paired_devices:
            print('Publishing new pairing device: ',paired_devices)
            # Appliquer la fonction à chaque élément de la liste
            #paired_devices_str = [extract_device_info(device) for device in paired_devices]

            # Filtrer les éléments None (qui n'ont pas pu être extraits)
            #paired_devices_str = [info for info in paired_devices_str if info is not None]

            #print('publication archi/devices')
            mqttManager.publish('archi/devices',json.dumps(paired_devices))
            previous_paired_devices = paired_devices
        #iteration = DETECTION_LATENCY
        #else: paired_devices = get_paired_devices()
        actual_devices = scan_devices()
        # On vérifie si on est dans une nouvelle boucle du DETECTION_LATENCY
        if iteration >= DETECTION_LATENCY:
            previous_devices = {}
            new_devices = actual_devices
            iteration = 0
        else:
            # On compare les nouvelles valeurs detectées
            #previous_devices_MAC_addr = {for MAC_addr['Address'] in previous_devices}
            #new_devices = [actual_devices_MAC_addr for actual_devices_MAC_addr in actual_devices if actual_devices_MAC_addr not in previous_devices_MAC_addr]
            actual_addresses = {device['Address'] for device in actual_devices}
            previous_addresses = {device['Address'] for device in previous_devices}
            # Calculate the set difference to find addresses present in actual_devices but not in previous_devices
            new_addresses = actual_addresses - previous_addresses
            # Create a list of dictionaries for the new devices
            new_devices = [{"Address": address, "Alias": next(device['Alias'] for device in actual_devices if device['Address'] == address)} for address in new_addresses]
            print("New devices: ", new_devices)
            if len(previous_devices) == 0:
                previous_devices = new_devices
            else:
                # On ajoute les nouvelles valeurs a previous_devices
                print("Previous_device",previous_devices)
                #previous_devices.extend(actual_devices)
                #previous_devices = list(set(previous_devices))
                previous_devices += new_devices

        if len(new_devices) > 0:
            json_message = json.dumps(new_devices)
            loraWan_access = mqttManager.publish('archi/request',json_message)
            if not loraWan_access: #Passage en mode dégradé
                downgraded_mode(new_devices)
        mqttManager.start_listening()
        sleeping(3)
        mqttManager.stop_listening()

        if len(new_devices) == 0:
            iteration += SLEEPING_TIME
        else:
            iteration = math.floor(iteration/2)
        print("Iteration N°",iteration)

