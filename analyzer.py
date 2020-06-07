#!/usr/bin/python3.6

import cv2
import socket
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from datetime import datetime

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

HEADER_LENGTH = 10

# this program IP and PORT numer
IP = "127.0.0.1"
PORT = 7654

# startup settings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()

BUFFER_SIZE = 1000000

def send_to_receiver(file_bytes):
    HEADER_SIZE = 10
    header = f"{len(file_bytes):^ {HEADER_SIZE}}".encode('utf-8')
    sending_message = header + file_bytes
        # Log
    print(f"{bcolors.OKBLUE}[I Analyzer] Analyzing finished{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}[I Analyzer] message: [|{header.decode('utf-8')}|{str(type(file_bytes))}]{bcolors.ENDC}")

    # Parser IP and PORT
    IP = "127.0.0.1"
    PORT = 1239

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.connect((IP, PORT))

    # Log
    print(f"{bcolors.OKBLUE}[I Analyzer] Sending result to receiver{bcolors.ENDC}")    

    receiver_socket.send(sending_message)
    
    print(f"{bcolors.OKBLUE}[I Analyzer] Result sent to receiver{bcolors.ENDC}")    


def analyze(inv_indx, doc_info):
    # analyze the invert index
    
    # Convert invert index and doc_info to DataFrame
    invert_indx_df = pd.DataFrame(inv_indx).transpose()
    doc_info_df = pd.DataFrame(doc_info).transpose()
    
    # sort invert index and get top used word by df
    invert_indx_df = invert_indx_df.sort_values(by='DF', ascending=False)
    top_word_df = invert_indx_df[:10]
    top_word_df = top_word_df.drop(['DocIDs','DocTF'], axis=1)

    # get all of the persons involve with this messages
    persons = doc_info_df['from'].unique()
    person_message_count  = pd.DataFrame(doc_info_df['from'].value_counts())
    
    # seprate day date and exact hour of each message by regex
    day, hour = [], []
    for row in range(len(doc_info_df)):
        date_time = doc_info_df.iloc[row]['time']
        date_time_re = re.findall('(\d{2}\.\d{2}\.\d{4})\s(\d{2}):\d{2}:\d{2}', date_time)
        day.append(date_time_re[0][0])
        hour.append(str(date_time_re[0][1]+':00'))

    # add day and hour column to the doc_info
    doc_info_df['day'] = day
    doc_info_df['hour'] = hour

    # count top days and hour with most traffic
    hour_counts = pd.DataFrame(doc_info_df['hour'].value_counts())
    day_counts = pd.DataFrame(doc_info_df['day'].value_counts())
    day_counts_top = day_counts[:10]
    hour_counts_top = hour_counts.sort_index()
    
    # customize the figure size
    plt.figure(figsize=(25,25))

    # Top 10 Words
    plt.subplot2grid((5,6), (0,0), colspan=6, rowspan=2)
    plt.bar(top_word_df.index , top_word_df.DF, color='#543864')
    plt.title('Top 10 Most Used Words')
    plt.ylabel('Counts')

    # Top 10 days
    plt.subplot2grid((5,6), (2,0), colspan=4, rowspan=2)
    plt.bar(day_counts_top.index, day_counts_top.day, color='#ff6363')
    plt.title('Top 10 Day with most messages')

    # Each person messages percentage
    plt.subplot2grid((5,6), (2,4), colspan=2, rowspan=2)
    plt.pie(person_message_count, labels=persons, autopct='%1.0f%%', explode=[0.02 for i in range(len(persons))])
    plt.title('Each Person messages percentage')

    # Message Traffic per hour
    plt.subplot2grid((5,6), (4,0), colspan=6)
    plt.plot(hour_counts_top.index,hour_counts_top.hour, color='#ffbd69', marker='o', ls='-.')
    plt.title('Message traffic per hour')

    # save all of the plots in a plot_images subdirectory
    plot_name = './plot_images/' + str(datetime.now()) + '.png'
    plt.savefig(plot_name)

    # turn plot image into numpy array and return it as the result
    plot_img = cv2.imread(plot_name)
    plot_img_pick = pickle.dumps(plot_img)
    
    return plot_img_pick


while True:
    
    # Log
    print(f'{bcolors.HEADER}[I Analyzer] Analyizer is listening...{bcolors.ENDC}')

    client_socket, client_address = server_socket.accept()

    # Log
    print(f"{bcolors.OKGREEN}[I Analyzer] Connection from >>{client_address}<< has been stablished!{bcolors.ENDC}")

    data = b''
    new_msg = True

    while True:
        msg = client_socket.recv(BUFFER_SIZE)

        if new_msg:
            
            # Log
            print(f'{bcolors.OKBLUE}[I Analyzer] New message receiving! | TIME: {datetime.now()}{bcolors.ENDC}')
            print(f'{bcolors.OKBLUE}[I Analyzer] Message length: {msg[:HEADER_LENGTH].decode("utf-8")}{bcolors.ENDC}')

            msglen = int(msg[:HEADER_LENGTH])
            new_msg = False
    
        data += msg

        if len(data) - HEADER_LENGTH == msglen:

            # Log
            print(f"{bcolors.OKBLUE}[I Analyzer] Message received completely{bcolors.ENDC}")

            data = data[HEADER_LENGTH:]
            client_socket.send(b'Files received!')
            break
    
    data = pickle.loads(data)

    invert_index = data[0]
    doc_info = data[1]

    # this part of the code is for writing the analyze 
    # function in jupyter. and we can delete it later.
    # invert_index_file = open('./invert_index.json', 'w')
    # json.dump(invert_index, invert_index_file)
    # invert_index_file.close()

    # doc_info_file = open('./doc_info.json', 'w')
    # json.dump(doc_info, doc_info_file)
    # doc_info_file.close()


    # send the data to the analyze function and get the results
    
    # Log
    print(f"{bcolors.OKBLUE}[I Analyzer] Start analyzing {bcolors.ENDC}")
    
    analysis_res = analyze(invert_index, doc_info)

    if analysis_res:
        # Log
        print(f"{bcolors.OKGREEN}[I Analyzer] Analyzing finished{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}[I Analyzer] Result size {len(analysis_res)}{bcolors.ENDC}")
        
        # send the result to the receiver
        send_to_receiver(analysis_res)