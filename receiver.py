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

    # message_header = client_socket.recv(HEADER_LENGTH)
    # message_header = int(message_header)
    
    full_msg = b''
    new_msg = True

    while True:
        msg = client_socket.recv(4096)

        if new_msg:
            print(f'new message length: {msg[:HEADER_LENGTH]}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        full_msg += msg

        if len(full_msg) - HEADER_LENGTH == msglen:
            print("full msg recvd")
            full_msg = full_msg[HEADER_LENGTH:]
            break
    
    # print(type(full_msg))
    data = pickle.loads(full_msg)
    print(type(data), len(data))
    
    client_socket.send(b'Files received!')


