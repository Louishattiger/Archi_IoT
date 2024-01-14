def pairable():
    from pairable_mode import Agent, Adapter, bus, AGENT_PATH, BUS_NAME, AGNT_MNGR_PATH, AGNT_MNGR_IFACE, CAPABILITY, disconnect_new_device
    import dbus
    import dbus.service
    import dbus.mainloop.glib
    from gi.repository import GLib

    PAIRING_TIME = 30   # Temps durant lequel le device est en mode Pairing
    agent = Agent(bus, AGENT_PATH)
    agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
                               AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
    agnt_mngr.RequestDefaultAgent(AGENT_PATH)

    adapter = Adapter()
    mainloop = GLib.MainLoop()

    # Planifiez l'arrêt du mainloop après 10 secondes (ajustez selon vos besoins)
    GLib.timeout_add_seconds(30, lambda: mainloop.quit())
    print(f"Going pairing mode for {PAIRING_TIME} seconds")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(AGENT_PATH)
        mainloop.quit()
    #adapter.adapter_reset()
    mac_address = disconnect_new_device()
    adapter.adapter_reset()
    return mac_address

def maj_config(address):
    try:
        with open('config.txt', 'r') as file:
            adresses_mac_existantes = file.read().splitlines()
    except FileNotFoundError:
        # si le fichier existe pas, on le crée
        with open('config.txt', 'w') as file:
            pass
        adresses_mac_existantes = []

    # Vérifier si l'adresse MAC sélectionnée est déjà dans le fichier
    if address in adresses_mac_existantes:
        print(f"L'appareil avec l'adresse MAC {address} a déjà été appareillé une fois.")
    else:
        # Ajouter l'adresse MAC au fichier
        with open('config.txt', 'a') as file:
            file.write(address + '\n')
        print(f"L'appareil avec l'adresse MAC {address} a été ajouté au fichier.")