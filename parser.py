#!/usr/bin/python3.8

import socket
import pickle
from bs4 import BeautifulSoup


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


def parsing(data):
    msg_id = 1
    main_dict = {}
    for file in data:
        # for each file/list that we received we make 
        # an html file
        html_file = open('./chatfile.html', 'w')
        html_file.writelines(file)
        html_file.close()

        # then we open that file and soup it
        html_file = open('./chatfile.html', 'r')
        bmf = BeautifulSoup(html_file, 'html.parser')
        print(type(bmf))
        html_file.close()

        html_file = open('./chatfile.html', 'w')
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

                print('-'*30)
                print(plain_from, '-->', plain_text, 'T: ', plain_time )

                main_dict[msg_id] = {'text':plain_text , 'from':plain_from, 'time':plain_time}
                msg_id += 1
            except:
                pass
    
    return main_dict


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
    parsed_data = parsing(data)

    # TODO 
    # send file to the tokenizer
