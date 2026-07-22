import socket

# Configurare conexiune
server_address = ('127.0.0.1', 5000)

# Creare socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Asociere socket cu IP-ul și Portul
server_socket.bind(server_address)

# Ascultare pentru conexiuni de la sender
server_socket.listen(1)
print("[RECEIVER] Astept conexiuni...")

connection, client_address = server_socket.accept()

try:
    # Primire mesaj de la sender
    data = connection.recv(1024).decode('utf-8')
    print(f"[RECEIVER] Mesaj primit: {data}")

    if data:
        # Trimitere răspuns înapoi către sender (Task 2c)
        reply = f"Hello! Your message was {data}."
        connection.sendall(reply.encode('utf-8'))
finally:
    connection.close()
    server_socket.close()
