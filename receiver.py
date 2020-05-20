#!/usr/bin/python3.6

import socket
import pickle
from datetime import datetime
import pandas as pd
import numpy

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1235

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()


PORT2 = 1239

for_analyze_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for_analyze_socket.bind((IP, PORT2))
for_analyze_socket.listen()

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
    
    ack = parser_socket.recv(50)
    print('ACK: ',ack.decode('utf-8'))


def send_to_client(file_bytes, client_socket):
    print(client_socket, type(client_socket))
    print(type(file_bytes), len(file_bytes))

    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    print('sending file to the Parser...')
    client_socket.send(sending_message)
    
    # ack = parser_socket.recv(50)
    # print('ACK: ',ack.decode('utf-8'))


while True:
    print('listening..')
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = client_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'New message receiving! | TIME: {datetime.now()}')
            print(f'new message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("Message received completely")
            data = data[HEADER_LENGTH:]
            # client_socket.send(b'Files received!')
            break
    
    # send data to the parser
    send_to_parser(data)

    # get the result from analyzer
    print("Listening for result from analyzer...")
    analyzer_socket, analyzer_address = for_analyze_socket.accept()
    print(f"Connection from {analyzer_address} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = analyzer_socket.recv(BUFFER_SIZE)
        if new_msg:
            print(f'New message receiving! | TIME: {datetime.now()}')
            print(f'new message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("Message received completely")
            data = data[HEADER_LENGTH:]
            ack_message = bytes('Files received!', 'utf-8')
            # print('ack message length: ', len(ack_message))
            # analyzer_socket.send(ack_message)
            break
    
    # analyzer_socket.close()
    print(type(data))
    
    # 
    send_to_client(data, client_socket)
    
