import socket
import pickle

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1235

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

while True:
    print('listening..')
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} has been stablished!")

    message_header = client_socket.recv(HEADER_LENGTH)
    message_header = int(message_header)

    data = []
    while True:
        message = client_socket.recv(4096)
        if not message: break

        data.append(message)

    data_arr = pickle.loads(b"".join(data))
    print(type(data_arr))
    print(len(data_arr))
    print(data_arr)

    client_socket.close()