import bluetooth
import time
import sys
import math
import json
import os


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
        print("Current address processing: ", address)
        if address == "True":
            open_gate()
        else:
            rfcomm_ports_to_try = [1, 2, 3, 4, 5]
            if connect_to_device(address, rfcomm_ports_to_try):
                return open_gate()


def scan_devices():
    print("Scanning for nearby Bluetooth devices...")
    nearby_devices = bluetooth.discover_devices(duration=3, flush_cache=True, lookup_names=True, lookup_class=True,
                                                device_id=-1, iac=10390323)

    if not nearby_devices:
        print("Aucun périphérique Bluetooth trouvé.")
    else:
        print("Périphériques Bluetooth trouvés :")
        for addr, name, _ in nearby_devices:
            print(f"Adresse : {addr}, Nom : {name}")
    return nearby_devices


def connect_to_device(mac_address, service_ports):
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
            if hasattr(e, 'errno') and e.errno == 112:  # L'hôte est down (et donc pas besoin de tester les 5 ports)
                return False

    return False


def check_bluetooth_services():
    print("looking for nearby devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True, flush_cache=True, duration=20)
    print("found %d devices" % len(nearby_devices))
    for addr, name in nearby_devices:
        print(" %s - %s" % (addr, name))
        for services in bluetooth.find_service(address=addr):
            print(" Name: %s" % (services["name"]))
            print(" Description: %s" % (services["description"]))
            print(" Protocol: %s" % (services["protocol"]))
            print(" Provider: %s" % (services["provider"]))
            print(" Port: %s" % (services["port"]))
            print(" Service id: %s" % (services["service-id"]))


def sleeping(iteration):
    print("Sleeping for 3s", end="")
    sys.stdout.flush()
    while iteration > 1:
        print(".", end="")
        sys.stdout.flush()
        iteration -= 1
        time.sleep(1)
    print(".")


if __name__ == "__main__":
    from Mqtt_Manager import Mqtt_Manager

    previous_devices = []  # Les appareils détectés dans les dernières DETECTION_LATENCY secondes
    SLEEPING_TIME = 3  # Le temps entre chaque ecoute, en secondes
    DETECTION_LATENCY = 60  # Le temps entre chaque différenciation de detection pour un meme device, en secondes
    iteration = 0  # Iteration d'un pas de SLEEPING_TIME dans la DETECTION_LATENCY
    mqttManager = Mqtt_Manager()

    while True:
        actual_devices = scan_devices()
        # On vérifie si on est dans une nouvelle boucle du DETECTION_LATENCY
        if iteration >= DETECTION_LATENCY:
            previous_devices = []
            new_devices = actual_devices
            iteration = 0
        else:
            # On compare les nouvelles valeurs detectées
            previous_devices_MAC_addr = {MAC_addr[0] for MAC_addr in previous_devices}
            new_devices = [actual_devices_MAC_addr for actual_devices_MAC_addr in actual_devices if
                           actual_devices_MAC_addr[0] not in previous_devices_MAC_addr]
            if len(previous_devices) == 0:
                previous_devices = new_devices
            else:
                # On ajoute les nouvelles valeurs a previous_devices
                print("Previous_device", previous_devices)
                previous_devices.extend(actual_devices)
                previous_devices = list(set(previous_devices))

        print("New devices: ", new_devices)  # a push sur le broker
        if len(new_devices) > 0:
            json_message = json.dumps(new_devices)
            mqttManager.publish('archi/request', json_message)
        mqttManager.start_listening()
        sleeping(3)
        mqttManager.stop_listening()

        if len(new_devices) == 0:
            iteration += SLEEPING_TIME
        else:
            iteration = math.floor(iteration / 2)
        print("Iteration N°", iteration)
