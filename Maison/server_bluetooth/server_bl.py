#pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print("Attente de la connexion sur le port", port)

client_sock, address = server_sock.accept()
print("Connexion établie avec", address)

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            break
        print("Message reçu:", data.decode())
except OSError:
    pass

print("Fermeture de la connexion")
client_sock.close()
server_sock.close()
