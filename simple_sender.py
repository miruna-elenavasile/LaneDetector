import socket

# Configurare conexiune TCP/IP
server_address = ('127.0.0.1', 5000)

# Creare socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectare la receiver/server
client_socket.connect(server_address)

# Trimitere mesaj (trebuie codificat în bytes)
message = "Hello from sender!"
client_socket.sendall(message.encode('utf-8'))

# Citire răspuns trimis de receiver (Task 2c)
response = client_socket.recv(1024).decode('utf-8')
print(f"[SENDER] Raspuns primit de la receiver: {response}")

# Închidere conexiune
client_socket.close()
