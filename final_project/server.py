#!/usr/bin/python
# RUN ON LAPTOP USING PYTHON 3.6

import socket
from queue import Queue
from CV import LetterDetection
import sys

# This class handles the Server side of the comunication between the laptop and the brick.
class Server:
    def __init__(self, host, port):
       # setup server socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # We need to use the ip address that shows up in ipconfig for the usb ethernet adapter that handles the comunication between the PC and the brick
        print("Setting up Server\nAddress: " + host + "\nPort: " + str(port))
        
        serversocket.bind((host, port))
        # queue up to 5 requests
        serversocket.listen(5) 
        self.cs, addr = serversocket.accept()
        print ("Connected to: " + str(addr))

    def send_msg(self, msg):
        data = str(msg)

        self.cs.send(data.encode("UTF-8"))
        # Waiting for the client (ev3 brick) to let the server know that it is done moving
        reply = self.cs.recv(128).decode("UTF-8")
        queue.put(reply)
        # block is true because we want to wait for the motors to fully move before continuing the program
        assert queue.get(block=True) == "DONE" 

global server, tracker, queue, initial_jacobian

# host = "169.254.225.196"
host = "169.254.79.135"
port = 9999
server = Server(host, port)
queue = Queue()

DETECTOR = False
try:
    input_method = str(sys.argv[1])
    if input_method == "image":
        DETECTOR = True
        detector = LetterDetection()
except IndexError:
    pass

msg = ""
while msg != "exit":
    if DETECTOR:
        input("Write a new word, and save it")
        msg = detector.get_word_from_image('text.jpg')
        msg += " "
        print(msg)

    else:
        msg = sys.stdin.read()

    server.send_msg(msg)
