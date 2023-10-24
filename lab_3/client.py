#!/usr/bin/python3       
# RUN ON BRICK
    
import socket
import os
import time

from ev3dev2.motor import OUTPUT_B, OUTPUT_D
from util import ArmMotor, calculate_coordinates

# This class handles the client side of communication. It has a set of predefined messages to send to the server as well as functionality to poll and decode data.
class Client:
    def __init__(self, host, port):
        # We need to use the ipv4 address that shows up in ipconfig in the computer for the USB. Ethernet adapter handling the connection to the EV3
        print("Setting up client\nAddress: " + host + "\nPort: " + str(port))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.connect((host, port))                               
        
    # Block until a message from the server is received. When the message is received it will be decoded and returned as a string.
    # Output: UTF-8 decoded string containing the instructions from server.
    def pollData(self):
        print("Waiting for Data")
        data = self.s.recv(128).decode("UTF-8")
        print("Data Received", data)
        return data
    
    # Sends a message to the server letting it know that the movement of the motors was executed without any inconvenience.
    def sendDone(self):
        self.s.send("DONE".encode("UTF-8"))

    # Sends a message to the server letting it know that there was an isse during the execution of the movement (obstacle avoided) and that the initial jacobian should be recomputed (Visual servoing started from scratch)
    def sendReset(self):
        self.s.send("RESET".encode("UTF-8"))
    
    # def sendData(self, data):
    #     # If data is an iterable, turn it into a nicer format for splitting, otherwise just send it
    #     if hasattr(data, '__iter__'):
    #         formattedData = ",".join([str(i) for i in data])
    #     else:
    #         formattedData = str(data)
    #     self.s.send(formattedData.encode("UTF-8"))
    
    def get_angles(self):
        angles = [float(angle) for angle in self.pollData().split(",")]
        self.sendDone()
        return angles

first_motor = ArmMotor(OUTPUT_D)
second_motor = ArmMotor(OUTPUT_B)
first_motor.position = 0
second_motor.position = 0

host = "169.254.79.135"
port = 9999
client = Client(host, port)
i = 0

def initial_jacobian():
    ### See jacobian_estimate() in server.py
    for i in range(2):
        first_angle, second_angle = client.get_angles()
        first_motor.move_angle(first_angle)
        second_motor.move_angle(second_angle)
        time.sleep(2)
        first_motor.move_angle(-first_angle)
        second_motor.move_angle(-second_angle)
        ################## Ask Christoph about resetting motors
        time.sleep(2)

initial_jacobian()

while True:
    first_angle, second_angle = client.get_angles()
    first_motor.move_angle(first_angle)
    second_motor.move_angle(second_angle)
    
