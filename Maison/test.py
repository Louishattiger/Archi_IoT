import os

def dynamic_route(mac):
    print("****************DELETE*****************")
    print(mac)
    config_path = 'config.txt'
    print("Répertoire de travail actuel:", os.getcwd())
    config_path = 'config.txt'
    abs_config_path = os.path.abspath(config_path)
    print("Chemin absolu de config.txt:", abs_config_path)

    with open(config_path, 'r') as config_file:
        config_macs = [line.strip() for line in config_file]

    if mac in config_macs:
        config_macs.remove(mac)

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(config_macs))

        print(f"Adresse MAC {mac} supprimée avec succès.")
    else:
        print(f"L'adresse MAC {mac} n'est pas présente dans le fichier de configuration.")

dynamic_route("11:22:33:44:55:66")