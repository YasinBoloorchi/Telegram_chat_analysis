#!/usr/bin/python3.8

import socket
import pickle
from datetime import datetime

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 9876

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000

# Read stop words from .stop_words.txt
stop_words_file = open('./.stop_words.txt', 'r')

stop_words_lines = stop_words_file.readlines()
stop_words = list(map( (lambda word: word.split('\n')[0] ) , stop_words_lines))

stop_words_file.close()



def is_stop_word(word):
    if word in stop_words:
        print(f'{word} IS STOP WORD')
        return True
    
    else:
        return False


while True:
    print('stop word checker is listening..')
    tokenizer_socket, tokenizer_address = server_socket.accept()
    print(f"Connection from {tokenizer_address} has been stablished!")

    while True:
        msg = tokenizer_socket.recv(100)
        
        data = pickle.loads(msg)
        
        if data == 'END':
            break

        # print(type(data), data)

        res = is_stop_word(data)

        tokenizer_socket.send(pickle.dumps(res))

