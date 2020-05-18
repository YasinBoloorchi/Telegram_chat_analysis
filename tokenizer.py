#!/usr/bin/python3.8

import socket
import pickle
from datetime import datetime

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 3421


# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000

def send_to_analysis(file_bytes):
    
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    # analysis IP and PORT
    IP = "127.0.0.1"
    PORT = 2341

    analysis_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    analysis_socket.connect((IP, PORT))

    print('sending file to the analysis...')
    analysis_socket.send(sending_message)
    
    # client_socket.send(client_socket_bytes)

    print('file sent to the analysis!')


# TODO 
# create a stop word checker program
def is_stop_word(word):

    stop_words = ['این', 'و', 'در', 'با', 'اون', 'برای', 'از']
    if word in stop_words:
        return True
    
    else:
        return False
    


def tokenize(parsed_dictionary):
    
    Invert_index = {}
    for DID in parsed_dictionary:
        doc = parsed_dictionary[DID]
        
        text = doc['text'].split(' ')

        # TODO 
        # add a stemmer function 
        stemmed_words = []
        for word in text:
            if not is_stop_word(word):
                stemmed_words.append(word)

        for word in stemmed_words:
            if word not in Invert_index:
                Invert_index[word] = {'DocIDs':[DID], 'DocTF': { DID : 1 }, 'DF' : 1 }
            
            else:
                if DID not in Invert_index[word]['DocIDs']:
                    Invert_index[word]['DocIDs'].append(DID)
                    Invert_index[word]['DocTF'][DID] = 1
                    Invert_index[word]['DF'] += 1
                
                elif DID in Invert_index[word]['DocIDs']:
                    Invert_index[word]['DocTF'][DID] += 1
    
    return Invert_index
    


# Listen for get new data
while True:
    print('Tokenizer is listening..')
    parser_socket, parser_address = server_socket.accept()
    print(f"Connection from {parser_address} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = parser_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'New message receiving! | TIME: {datetime.now()}')
            print(f'new message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("Message received completely")
            data = data[HEADER_LENGTH:]
            parser_socket.send(b'Files received!')
            break
    
    data = pickle.loads(data)
    print('data class: ',type(data), '-- data length:' ,len(data))
    

    # TODO
    inv_indx = tokenize(data)
    print('Inver Index Created.\nwidth:', len(inv_indx))

    # for word in inv_indx:
    #     df = inv_indx[word]['DF']
    #     if int(df) > 10:
    #         print(word, '-'*10, '>', inv_indx[word]['DF'])


    # TODO
    # send_to_analysis(pickle.dumps(inv_indx))