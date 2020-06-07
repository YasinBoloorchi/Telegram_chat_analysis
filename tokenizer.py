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

# TODO Read from config file
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
    
    # Log
    print(f"{bcolors.OKBLUE}[I Tokenizer] message: [|{header.decode('utf-8')}|{str(type(file_bytes))}] {bcolors.ENDC}")

    # TODO Read from config file
    # analyzer IP and PORT
    IP = "127.0.0.1"
    PORT = 7654

    analysis_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    analysis_socket.connect((IP, PORT))

    print(f'{bcolors.OKBLUE}[I Tokenizer] Sending file to the analyzer... {bcolors.ENDC}')

    analysis_socket.send(sending_message)

    print(f'{bcolors.OKBLUE}[I Tokenizer] File sent to the analyzer {bcolors.ENDC}')
    


def is_stop_word(word, is_stop_socket):
    word_byte = pickle.dumps(word)
    
    is_stop_socket.send(word_byte)

    # verbose
    # print(f"send word '{word}' to is_stop")

    res = is_stop_socket.recv(100)
    
    return pickle.loads(res)


def tokenize(parsed_dictionary):
    
    # Log
    print(f'{bcolors.OKBLUE}[I Tokenizer] Start tokenizing {bcolors.ENDC}')
    
    # TODO Read from config file
    # Connect to stop word
    IP = "127.0.0.1"
    PORT = 9876

    is_stop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_stop_socket.connect((IP, PORT))


    Invert_index = {}
    for DID in parsed_dictionary:
        doc = parsed_dictionary[DID]
        
        text = doc['text'].split(' ')

        # TODO 
        # add a stemmer function 
        stemmed_words = []
        for word in text:
            if not is_stop_word(word, is_stop_socket) and len(word) > 0:
                stemmed_words.append(word)

        # Verbose
        # print('length of stemmed word: ',len(stemmed_words))

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
    
    is_stop_socket.send(pickle.dumps('END'))

    # Log
    print(f'{bcolors.OKBLUE}[I Tokenizer] Tokenizing finished. invert index len: {len(Invert_index)} {bcolors.ENDC}')

    return Invert_index
    


# Listen for get new data
while True:
    
    # Log
    print(f'{bcolors.HEADER}[I Tokenizer] Tokenizer is listening..{bcolors.ENDC}')
    
    parser_socket, parser_address = server_socket.accept()
    
    # Log
    print(f"{bcolors.OKGREEN}[I Tokenizer] Connection from {parser_address} has been stablished!{bcolors.ENDC}")

    data = b''
    new_msg = True

    while True:
        msg = parser_socket.recv(BUFFER_SIZE)

        if new_msg:

            # Log
            print(f'{bcolors.OKBLUE}[I Tokenizer] New message receiving! | TIME: {datetime.now()}')
            print(f'{bcolors.OKBLUE}[I Tokenizer] new message length: {msg[:HEADER_LENGTH].decode("utf-8")}{bcolors.ENDC}')

            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:

            # Log
            print(f"{bcolors.OKBLUE}[I Tokenizer] Message received completely{bcolors.ENDC}")

            data = data[HEADER_LENGTH:]
            parser_socket.send(b'Files received!')
            break
    
    data = pickle.loads(data)
    print(f'{bcolors.OKBLUE}[I Tokenizer] Dictionary length: {len(data)} {bcolors.ENDC}')

    inv_indx = tokenize(data)
    
    # TO pring dictionary
    # print('Inver Index Created.\nwidth:', len(inv_indx))
    # doc_info = {}
    # for doc_id in data:
    #     doc_info[doc_id] = {'from': data[doc_id]['from'], 'time': data[doc_id]['time']}

    # delete text from dictionary to send to analyzer
    for doc_id in data:
        del data[doc_id]['text']

    # send invert index and data (without texts)
    inv_indx_W_doc_id = [inv_indx, data]

    # TODO
    send_to_analysis(pickle.dumps(inv_indx_W_doc_id))