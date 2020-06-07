#!/usr/bin/python3.6

import socket
import pickle
from bs4 import BeautifulSoup
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
print(f"{bcolors.OKBLUE}[I Receiver] Starting tokenizer{bcolors.ENDC}")

# read from config file
HEADER_LENGTH = int(get_config('HEADER_LENGTH'))

IP = get_config('parser_IP')
PORT = int(get_config('parser_PORT'))

# Log
print(f"{bcolors.OKBLUE}[I Receiver] Tokenizer starting at IP Address ({IP}) and Port Number ({PORT}) {bcolors.ENDC}")

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000



def send_to_tokenizer(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"{bcolors.OKBLUE}[I Parser] message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]{bcolors.ENDC}")

    # TODO Read from config file
    # Parser IP and PORT
    IP = get_config("tokenizer_IP")
    PORT = int(get_config('tokenizer_PORT'))

    tokenizer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tokenizer_socket.connect((IP, PORT))

    # Log
    print(f'{bcolors.OKBLUE}[I Parser] Sending file to the tokenizer...{bcolors.ENDC}')
    tokenizer_socket.send(sending_message)
    
    # Log
    print(f'{bcolors.OKBLUE}[I Parser] file sent to the tokenizer!{bcolors.ENDC}')

    # Ack
    result = tokenizer_socket.recv(100)
    print(f'{bcolors.OKBLUE}[I Parser]', result.decode('utf-8'), bcolors.ENDC)


def parsing(data):
    msg_id = 1
    main_dict = {}
    
    print(f"{bcolors.OKBLUE}[I Parser] Parsing #{len(data)} File {bcolors.ENDC}")
    for file in data:
        # for each file/list that we received we make 
        # an html file
        html_file = open('./.chatfile.html', 'w')
        html_file.writelines(file)
        html_file.close()

        # then we open that file and soup it
        html_file = open('./.chatfile.html', 'r')
        bmf = BeautifulSoup(html_file, 'html.parser')
        
        html_file.close()

        html_file = open('./.chatfile.html', 'w')
        html_file.write('')
        html_file.close()



        all_messages = bmf.find_all('div', attrs={'class':'message default clearfix'})

        for d in all_messages:
            text_tag = d.find_all('div', attrs={'class':'text'})
            from_tag = d.find_all('div', attrs={'class':'from_name'})
            time_tag = d.find_all('div', attrs={'class':'pull_right date details'})[0]['title']

            try:
                plain_time = str(time_tag).replace('\n','')
                plain_text = str(text_tag[0].string).replace('\n','')
                plain_from = str(from_tag[0].string).replace('\n','')

                # print('-'*30)
                # print(plain_from, '-->', plain_text, 'T: ', plain_time )

                main_dict[msg_id] = {'text':plain_text , 'from':plain_from, 'time':plain_time}
                msg_id += 1
            except:
                pass

    return main_dict


while True:

    # Log
    print(f'{bcolors.HEADER}[I Parser] Parser is listening..{bcolors.ENDC}')
    
    receiver_socket, receiver_address = server_socket.accept()
    
    # Log
    print(f"{bcolors.OKGREEN}[I Parser] Connection from >>{receiver_address}<< (Receiver) has been stablished!{bcolors.ENDC}")
    
    data = b''
    new_msg = True

    while True:
        msg = receiver_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'{bcolors.OKBLUE}[I Parser] New message receiving! | TIME: {datetime.now()}{bcolors.ENDC}')
            print(f'{bcolors.OKBLUE}[I Parser] Message length: {msg[:HEADER_LENGTH].decode("utf-8")}{bcolors.ENDC}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            
            # Log
            print(f"{bcolors.OKGREEN}[I Parser] Message received completely{bcolors.ENDC}")
            
            data = data[HEADER_LENGTH:]

            # Ack
            receiver_socket.send(b'Parser received the file!')
            break
    
    data = pickle.loads(data)
    
    # Log
    print(f'{bcolors.OKBLUE}[I Parser] List length : {len(data)} {bcolors.ENDC}')

    # Pars File
    
    # Log
    print(f"{bcolors.OKBLUE}[I Parser] parsing the Files {bcolors.ENDC}")

    parsed_data = parsing(data)

    # Log
    print(f'{bcolors.OKBLUE}[I Parser] Parsing Completed. Parsed file length: {len(parsed_data)} | TIME: {datetime.now()}{bcolors.ENDC}')


    # send file to the tokenizer
    
    # Log
    print(f"{bcolors.OKBLUE}[I Parser] Sending file to tokenizer {bcolors.ENDC}")
    
    parsed_data_bytes = pickle.dumps(parsed_data)
    send_to_tokenizer(parsed_data_bytes)