#!/usr/bin/python3.8

import socket
import pickle

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1235

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000

def send_to_parser(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    # Parser IP and PORT
    IP = "127.0.0.1"
    PORT = 4123

    parser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parser_socket.connect((IP, PORT))

    print('sending file to the Parser...')
    parser_socket.send(sending_message)
    
    # client_socket.send(client_socket_bytes)

    print('file sent to the Parser!')


while True:
    print('listening..')
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = client_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'new message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("full msg recvd")
            data = data[HEADER_LENGTH:]
            client_socket.send(b'Files received!')
            break
    

    # send data to the parser
    send_to_parser(data)

    # TODO
    # wait for the analysis result
