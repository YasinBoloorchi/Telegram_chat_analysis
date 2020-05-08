#!/usr/bin/python3.6

import socket
import pickle


def send_file(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    # Parser IP and PORT
    IP = "127.0.0.1"
    PORT = 4123

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect((IP, PORT))

    print('sending file to the Parser...')
    receiver_socket.send(sending_message)
    print('file sent to the Parser!')

    result = receiver_socket.recv(100)
    print(result.decode('utf-8'))


HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 4123

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000

while True:
    print('Parser is listening..')
    receiver_socket, receiver_address = server_socket.accept()
    print(f"Connection from {receiver_socket} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = receiver_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'new message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("full msg receivd")
            data = data[HEADER_LENGTH:]
            receiver_socket.send(b'Prser received the file!')
            break
    

    # print(type(data))
    data = pickle.loads(data)
    print(type(data), len(data))

    # TODO 
    # Pars File

    # TODO 
    # send file to the tokenizer
