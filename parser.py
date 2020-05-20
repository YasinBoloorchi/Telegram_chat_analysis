#!/usr/bin/python3.6

import socket
import pickle
from bs4 import BeautifulSoup
from datetime import datetime


def send_to_tokenizer(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    # Parser IP and PORT
    IP = "127.0.0.1"
    PORT = 3421

    tokenizer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tokenizer_socket.connect((IP, PORT))

    print('sending file to the Parser...')
    tokenizer_socket.send(sending_message)
    print('file sent to the Parser!')

    result = tokenizer_socket.recv(100)
    print(result.decode('utf-8'))


HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 4123

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000


def parsing(data):
    msg_id = 1
    main_dict = {}
    
    print(f"Parsing #{len(data)} File")
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
    print('Parser is listening..')
    receiver_socket, receiver_address = server_socket.accept()
    print(f"Connection from {receiver_address} has been stablished!")

    data = b''
    new_msg = True

    while True:
        msg = receiver_socket.recv(BUFFER_SIZE)

        if new_msg:
            print(f'New message receiving! | TIME: {datetime.now()}')
            print(f'Message length: {msg[:HEADER_LENGTH].decode("utf-8")}')
            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:
            print("Message received completely")
            data = data[HEADER_LENGTH:]
            receiver_socket.send(b'Parser received the file!')
            break
    

    # print(type(data))
    data = pickle.loads(data)
    
    print('data class: ',type(data), '-- data length:' ,len(data))

    # TODO 
    # Pars File
    print("Start parsing the Files")
    parsed_data = parsing(data)
    print(f'Parsing Completed\nParsed file length: {len(parsed_data)} | TIME: {datetime.now()}')

    # TODO 
    # send file to the tokenizer
    parsed_data_bytes = pickle.dumps(parsed_data)
    send_to_tokenizer(parsed_data_bytes)