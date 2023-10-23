#!/usr/bin/python3       
# RUN ON BRICK
    
import socket
import os
import time
import ast

from ev3dev2.motor import OUTPUT_B, OUTPUT_D
from util import ArmMotor

# This class handles the client side of communication. It has a set of predefined messages to send to the server as well as functionality to poll and decode data.
class Client:
    def __init__(self, host, port):
        # We need to use the ipv4 address that shows up in ipconfig in the computer for the USB. Ethernet adapter handling the connection to the EV3
        print("Setting up client\nAddress: " + host + "\nPort: " + str(port))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.connect((host, port))  
        self.done = False      
        self.first_motor = ArmMotor(OUTPUT_D)
        self.second_motor = ArmMotor(OUTPUT_B)
        self.first_motor.position = 0
        self.second_motor.position = 0
            
        
    # Block until a message from the server is received. When the message is received it will be decoded and returned as a string.
    # Output: UTF-8 decoded string containing the instructions from server.
    def pollData(self):
        print("Waiting for Data")
        data = self.s.recv(128).decode("UTF-8")
        print("Data Received")
        print(data)
        if data != "":
            return ast.literal_eval(data)
        else:
            return {"cmd": "404"}
    
    def run_cmd(self, cmd, data):
        if cmd == "EXIT":
            self.get_done(data)
        elif cmd == "MOVE":
            self.move_cmd(data)
        elif cmd == "GET_ANGLES":
            self.get_angles(data)
        else:
            print("404")
    
    # Sends a message to the server letting it know that the movement of the motors was executed without any inconvenience.
    def sendDone(self):
        self.s.send("DONE".encode("UTF-8"))

    # Sends a message to the server letting it know that there was an isse during the execution of the movement (obstacle avoided) and that the initial jacobian should be recomputed (Visual servoing started from scratch)
    def sendReset(self):
        self.s.send("RESET".encode("UTF-8"))

    def move_cmd(self, data):
        angles = [float(angle) for angle in data.split(",")]
        self.second_motor.move_angle(angles[0])
        self.first_motor.move_angle(angles[1])
        self.sendDone()

    def get_angles(self, data):
        res = "[{}, {}]".format(self.second_motor.position, self.second_motor.position)
        self.s.send(res.encode("UTF-8"))
        self.sendDone()


    def get_done(self, data):
        self.done = True
        self.sendDone()


host = "169.254.79.135"
port = 9999
client = Client(host, port)
i = 0
DONE = False

print("Client hosted at {host}, on port {port}")
while not client.done:
    data = client.pollData()
    client.run_cmd(data["cmd"], data["data"])

print("CLIENT HAS STOPPED")
