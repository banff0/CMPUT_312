#!/usr/bin/python3       
# RUN ON BRICK
    
import socket
from utils import ArmMotor
from ev3dev2.motor import OUTPUT_B, OUTPUT_C, OUTPUT_D
from utils import ArmMotor
from letters import SWAN
import traceback

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
    
    def get_msg(self):
        msg = self.pollData()
        # angles = [float(angle) for angle in self.pollData().split(",")]
        self.sendDone()
        return msg

global first_motor, second_motor

y_mtr = ArmMotor(OUTPUT_D)
x_mtr = ArmMotor(OUTPUT_B)
z_mtr = ArmMotor(OUTPUT_C, hold_action = "coast")

x_mtr.position = 0; y_mtr.position = 0
swan = SWAN(x_mtr, y_mtr, z_mtr, 2)

# host = "169.254.225.196"
host = "169.254.79.135"
port = 9999
client = Client(host, port)

while True:
    msg = client.get_msg()

    try:
        swan.write_str(msg)
    except AssertionError:
        traceback.print_exc()
    except Exception:
        traceback.print_exc()
    finally:
        print(x_mtr.position, y_mtr.position)
        # input("Click Enter to reset")

x_mtr.reset()
y_mtr.reset()
    
