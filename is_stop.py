#!/usr/bin/python3.6

import socket
import pickle
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 9876

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 100000

# Read stop words from .stop_words.txt

# Log
print(f"{bcolors.OKBLUE}[I StopWord] Opening .stop_words.txt file {bcolors.ENDC}")

stop_words_file = open('./.stop_words.txt', 'r')

stop_words_lines = stop_words_file.readlines()
stop_words = list(map( (lambda word: word.split('\n')[0] ) , stop_words_lines))

stop_words_file.close()



def is_stop_word(word):
    if word in stop_words:
        
        # Verbose
        # print(f'{word} IS STOP WORD')
        
        return True
    
    else:
        return False


while True:
    
    # Log
    print(f'{bcolors.HEADER}[I StopWord] Stop word checker is listening...{bcolors.ENDC}')

    tokenizer_socket, tokenizer_address = server_socket.accept()
    
    # Log
    print(f"{bcolors.OKGREEN}[I StopWord] Connection from {tokenizer_address} has been stablished!{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}[I StopWord] Start checking stop words {bcolors.ENDC}")
    
    while True:
        msg = tokenizer_socket.recv(100000)
        
        data = pickle.loads(msg)
        
        if data == 'END':
            break

        res = is_stop_word(data)

        tokenizer_socket.send(pickle.dumps(res))

