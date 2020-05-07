from os import walk
import socket
import pickle
import re
import sys


def get_files_address(path):
    files_addresses = []
    for root, dirs, files in walk(path):
        for f in files:
            try:
                html_filename = re.findall('.*\.html$', f)[0]
                files_addresses.append(root +'/'+ html_filename)
            except:
                pass

    return files_addresses


addresses = get_files_address('/home/hakim/server_chat')
print('addresses: \n', addresses)


def files_to_bytes(address_list):
    file_list = []
    for addr in address_list:
        file = open(addr, 'r')
        file_list += file.readlines()
        print(type(file_list), len(file_list))
        file.close()

    return pickle.dumps(file_list)


file_bytes = files_to_bytes(addresses)
print("list files len: ",len(pickle.loads(file_bytes)))

def send_file(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes

    print(f"message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]")

    IP = "127.0.0.1"
    PORT = 1235

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))

    client_socket.send(sending_message)

send_file(file_bytes)