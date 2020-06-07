# Telegram Chat Analysis

this project is a micro service that provide analysis of chats that been exported from telegram with __"Export chat history"__.



## Programs

this project is contain 6  programs, each with different task. 

### Client 

[client](https://github.com/YasinBoloorchi/Telegram_chat_analysis/blob/master/client.py) is the client side program that will take the exported chat directory and get all of the HTML files and finally send them to the program side application  by the name of __receiver__.

### Receiver

[Receiver](https://github.com/YasinBoloorchi/Telegram_chat_analysis/blob/master/receiver.py) is our first server side program that have the responsibility of receiving raw data from client and sending back the result of the analysis. receiver will send the received data to the parser for further processes.

### Parser

[Parser](https://github.com/YasinBoloorchi/Telegram_chat_analysis/blob/master/parser.py) is the first step of analysis in server side. parser will get the received data from receiver and parse it within the parsing function. after that it will send the data to the tokenizer.

### Tokenizer

[Tokenizer](https://github.com/YasinBoloorchi/Telegram_chat_analysis/blob/master/tokenizer.py) is going to get the parsed data from parser and tokenize it with the help of "is_stop" program. it will send each parsed word to the "is_stop" program to check if it's a stop word. after finishing tokenization it will send the result to the analyzer program.

### Analyzer

At the end of the analyzing chain, there is [Analyzer](https://github.com/YasinBoloorchi/Telegram_chat_analysis/blob/master/analyzer.py) program that will get the parsed and tokenized data and analyze it with the help of pandas and matplotlib libraries. after analysis finished, it will convert the analysis result to a picture and the read it with OpenCV library for converting image to pandas object and transport it more easily. at the end it will send the result to receiver so it return the result to the client.



## Installation

For installing this project, first you need to download it and put it on 5 different servers (one server for each program) or even run them all on your local machine. after you download (or clone it from Git-hub), open the configuration file in the directory by the name of '.config' and set the IP address and port number for each program. then run them all (if you move the programs to different places you should copy the config file for all of them).

## Example

![Example](/home/hakim/Documents/python_programing/Server Project/plot_images/2020-06-07 12:39:53.959843.png)

