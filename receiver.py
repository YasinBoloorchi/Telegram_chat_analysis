#!/usr/bin/python3.6

from datetime import datetime
import socket
import pickle
import pandas as pd
import numpy

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_config(address):
    config_file = open("./.config")
    config = config_file.readlines()
    config_file.close()

    for line in config:
        addr = line.split('=')[0]
        if addr == address:
            return line.split('=')[1].strip()
        
    return False

# Log
print(f"{bcolors.OKBLUE}[I Receiver] Starting receiver{bcolors.ENDC}")

# read ip and port from config file
HEADER_LENGTH = int(get_config('HEADER_LENGTH'))
IP = get_config('receiver_IP')
PORT = int(get_config('receiver_PORT'))

# Log
print(f"{bcolors.OKBLUE}[I Receiver] Receiver starting at IP Address ({IP}) and Port Number ({PORT}) {bcolors.ENDC}")

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

# secont port connection for receiving from analyzer
PORT2 = int(get_config('receiver_PORT2'))

# Log
print(f"{bcolors.OKBLUE}[I Receiver] Receiver second Port Number: ({PORT2}) {bcolors.ENDC}")


for_analyze_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for_analyze_socket.bind((IP, PORT2))
for_analyze_socket.listen()

BUFFER_SIZE = 1000000

def send_to_parser(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    # Log
    print(f"{bcolors.OKBLUE}[I Receiver] Message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]{bcolors.ENDC}")

    # Read from config file
    # Parser IP and PORT
    IP = get_config('parser_IP')
    PORT = int(get_config('parser_PORT'))

    parser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parser_socket.connect((IP, PORT))

    # Log
    print(f'{bcolors.OKBLUE}[I Receiver] Sending file to the Parser...{bcolors.ENDC}')
    
    parser_socket.send(sending_message)
    
    ack = parser_socket.recv(50)
    
    # Log
    print(f'{bcolors.OKBLUE}[I Receiver] ACK: ',ack.decode('utf-8'), bcolors.ENDC)


def send_to_client(file_bytes, client_socket):

    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    # Log
    print(f"{bcolors.OKBLUE}[I Receiver] Message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]{bcolors.ENDC}")
    print(f'{bcolors.OKBLUE}[I Receiver] Sending results to the Client...{bcolors.ENDC}')
    
    client_socket.send(sending_message)
    


while True:
    
    # LOG
    print(f'{bcolors.HEADER}[I Receiver] Listening..{bcolors.ENDC}')
    
    client_socket, client_address = server_socket.accept()
    
    print(f"{bcolors.OKGREEN}[I Receiver] Connection from >>{client_address}<< has been stablished!{bcolors.ENDC}")

    data = b''
    new_msg = True

    while True:
        msg = client_socket.recv(BUFFER_SIZE)

        if new_msg:

            # LOG
            print(f'{bcolors.OKBLUE}[I Receiver] New message receiving! | TIME: {datetime.now()}{bcolors.ENDC}')
            print(f'{bcolors.OKBLUE}[I Receiver] Message length: {msg[:HEADER_LENGTH].decode("utf-8")}{bcolors.ENDC}')

            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:

            # Log
            print(f"{bcolors.OKBLUE}[I Receiver] Message received completely{bcolors.ENDC}")
            
            data = data[HEADER_LENGTH:]

            #for ack we can use line below
            # client_socket.send(b'Files received!')
            break
    
    # Log
    print(f"{bcolors.OKBLUE}[I Receiver] Sending data to the parser{bcolors.ENDC}")
    
    # send data to the parser
    send_to_parser(data)
    
    

    # Log
    print(f"{bcolors.OKBLUE}[I Receiver] Listening for result from analyzer...{bcolors.ENDC}")

    # get the result from analyzer
    analyzer_socket, analyzer_address = for_analyze_socket.accept()

    # Log
    print(f"{bcolors.OKGREEN}[I Receiver] Connection from >>{analyzer_address}<< (Analyzer) has been stablished!{bcolors.ENDC}")
    

    data = b''
    new_msg = True

    while True:
        msg = analyzer_socket.recv(BUFFER_SIZE)
        if new_msg:
            
            # Log
            print(f'{bcolors.OKBLUE}[I Receiver] New message receiving! | TIME: {datetime.now()}{bcolors.ENDC}')
            print(f'{bcolors.OKBLUE}[I Receiver] Message length: {msg[:HEADER_LENGTH].decode("utf-8")}{bcolors.ENDC}')
            
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            
            # Log
            print(f"{bcolors.OKBLUE}[I Receiver] Message received completely{bcolors.ENDC}")
            
            data = data[HEADER_LENGTH:]
            ack_message = bytes('Files received!', 'utf-8')
            
            break
    
    send_to_client(data, client_socket)
    
