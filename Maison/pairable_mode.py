import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess

BUS_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
ADAPTER_ROOT = '/org/bluez/hci'
AGENT_IFACE = 'org.bluez.Agent1'
AGNT_MNGR_IFACE = 'org.bluez.AgentManager1'
AGENT_PATH = '/my/app/agent'
AGNT_MNGR_PATH = '/org/bluez'
CAPABILITY = 'KeyboardDisplay'
DEVICE_IFACE = 'org.bluez.Device1'
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
new_address_mac = None

def set_trusted(path):
    global new_address_mac

    print("DEVICE: ",path)
    props = dbus.Interface(bus.get_object(BUS_NAME, path), dbus.PROPERTIES_IFACE)
    props.Set(DEVICE_IFACE, "Trusted", True)# La chaîne que vous avez

    # Utilisez le découpage pour extraire la partie qui représente l'adresse MAC
    adresse_mac_part = path.split('/')[-1]

    new_address_mac = adresse_mac_part.replace('_', ':').replace('dev:', '')
    print('new_address_mac = ',new_address_mac)

def get_new_address_mac():
    return new_address_mac

def disconnect_new_device():
    print('Disconnecting device: ',new_address_mac)
    try:
        # Exécute la commande bluetoothctl avec sudo
        result = subprocess.run(['sudo', 'bluetoothctl', 'disconnect', new_address_mac], capture_output=True)

        # Affiche la sortie de la commande
        print(result.stdout)
        return new_address_mac

    except subprocess.CalledProcessError as e:
        # Gère les erreurs lors de l'exécution de la commande
        print(f"Erreur lors de l'exécution de la commande bluetoothctl : {e}")


class Agent(dbus.service.Object):

    @dbus.service.method(AGENT_IFACE,
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_IFACE,
                         in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        print(f'RequestPinCode {device}')
        return '0000'

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        set_trusted(device)
        return

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        auth = input("Authorize? (yes/no): ")
        if (auth == "yes"):
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = input("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" %
              (device, passkey, entered))

    @dbus.service.method(AGENT_IFACE,
                         in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))


class Adapter:
    def __init__(self, idx=0):
        bus = dbus.SystemBus()
        self.path = f'{ADAPTER_ROOT}{idx}'
        self.adapter_object = bus.get_object(BUS_NAME, self.path)
        self.adapter_props = dbus.Interface(self.adapter_object,
                                            dbus.PROPERTIES_IFACE)
        self.adapter_props.Set(ADAPTER_IFACE,
                               'DiscoverableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Discoverable', True)
        self.adapter_props.Set(ADAPTER_IFACE,
                               'PairableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Pairable', True)

    def adapter_reset(self):
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Discoverable', False)
        self.adapter_props.Set(ADAPTER_IFACE,
                               'Pairable', False)


if __name__ == '__main__':
    agent = Agent(bus, AGENT_PATH)
    agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
                               AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
    agnt_mngr.RequestDefaultAgent(AGENT_PATH)

    adapter = Adapter()
    mainloop = GLib.MainLoop()

    # Planifiez l'arrêt du mainloop après 10 secondes (ajustez selon vos besoins)
    GLib.timeout_add_seconds(30, lambda: mainloop.quit())

    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(AGENT_PATH)
        mainloop.quit()
    disconnect_new_device()