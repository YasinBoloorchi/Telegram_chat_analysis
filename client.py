#!/usr/bin/python3.6

from os import walk
import socket
import pickle
import re
import sys
import numpy
import pandas
import cv2

# Color for LOGs
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# getting all of the .html file in the selected directory
def get_files_address(path):
    
    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] Finding all of the Files...{bcolors.ENDC}')
    files_addresses = []
    for root, dirs, files in walk(path):
        for f in files:
            try:
                # use regex to find html files and merge them with
                # their root directory address to get the full path.
                html_filename = re.findall('.*\.html$', f)[0]
                files_addresses.append(root +'/'+ html_filename)
            except:
                pass
    if len(files_addresses) == 0:
        raise Exception(f"{bcolors.FAIL} No HTML File Found in the given path! please try again.")

    return files_addresses

# turn all of the given files addresses to byte codes
def files_to_bytes(address_list):
    file_list = []
    for addr in address_list:
        file = open(addr, 'r')
        file_list.append(file.readlines())
        file.close()

    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] Number of readed Files:  {len(file_list)}{bcolors.ENDC}',)
    return pickle.dumps(file_list)


def send_files(file_bytes):

    # turn the byte codes to a message with header of file length
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] All file size length: {len(file_bytes)}{bcolors.ENDC}')
    print(f'{bcolors.OKBLUE}[I ClientApp] Connecting to the server{bcolors.ENDC}')
    
    # set ip and port of the server receiver program
    IP = "127.0.0.1"
    PORT = 1235

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))

    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] Sending file to the server...{bcolors.ENDC}')

    client_socket.send(sending_message)

    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] File sent to the server!{bcolors.ENDC}')

    # LOG
    print(f'{bcolors.OKBLUE}[I ClientApp] Waiting for the result{bcolors.ENDC}')

    BUFFER_SIZE = 1000000
    data = b''
    new_msg = True

    # get the receiving message of result in a 
    # sequence of messages 
    while True:

        # get the header of message and a little bit more
        msg = client_socket.recv(BUFFER_SIZE)

        # if it was a new message get the fixed size header
        if new_msg:
            
            # LOG
            print(f'{bcolors.OKBLUE}[I ClientApp] Reveiving message with length: {msg[:HEADER_SIZE].decode("utf-8")}{bcolors.ENDC}')
            msglen = int(msg[:HEADER_SIZE])
            new_msg = False

        # if it wasn't a new massage then add to the rest of the message
        data += msg

        # if message received completely then remove header
        # and return then load original message and return it
        if len(data) - HEADER_SIZE == msglen:

            # LOG
            print(f"{bcolors.OKGREEN}[I ClientApp] Result received completely{bcolors.ENDC}")
            data = data[HEADER_SIZE:]
            break

    # return the result
    return pickle.loads(data)


path = input(f"{bcolors.HEADER}Enter the Telegram chats exported directory: {bcolors.ENDC}")

# get all files addresses in a list
addresses = get_files_address(path)

# read all files and return them in a single byte file
file_bytes = files_to_bytes(addresses)

# sending the byte file to the server receiver and get
# the result
result_file = send_files(file_bytes)

# open the received result with OpenCV
while True:
    cv2.imshow('plot image', result_file)
    key = cv2.waitKey(20)
    
    # exit on ESC
    if key == 27: 
        break
    

