#!/usr/bin/python3.8

import socket
import pickle
from datetime import datetime
import json

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 7654

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000

def send_to_client(file_bytes):
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

def analyze(inv_indx, doc_info):
    # analyze the invert index

    for word in inv_indx:
        df = inv_indx[word]['DF']
        
        if int(df) > 10:
            print(word, '-->',df)

    return True

while True:
    print('Analyizer is listening..')
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
            client_socket.send(b'Files received!')
            break
    
    # send data to the parser
    data = pickle.loads(data)

    invert_index = data[0]
    doc_info = data[1]

    invert_index_file = open('./invert_index.json', 'w')
    json.dump(invert_index, invert_index_file)
    invert_index_file.close()

    doc_info_file = open('./doc_info.json', 'w')
    json.dump(doc_info, doc_info_file)
    doc_info_file.close()
    
    analysis_res = analyze(invert_index, doc_info)
    if analysis_res:
        print('Inver index has been analyzed!')
    # TODO
    # wait for the analysis result
