#!/usr/bin/python
# RUN ON LAPTOP USING PYTHON 3.6

import socket
import time
from queue import Queue

from color_tracking import Tracker
from util import Vector, Matrix

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

    # Sends set of angles to the brick via TCP.
    # Input: base_angle [Float]: The angle by which we want the base to move
    #        joint_angle [Float]: The angle by which we want to joint to move
    #        queue [Thread-safe Queue]: Mutable data structure to store (and return) the messages received from the client
    def sendAngles(self, base_angle, joint_angle, queue):
        # Format in which the client expects the data: "angle1,angle2"
        data = str(base_angle) + "," + str(joint_angle)
        print("Sending Data: (" + data + ") to robot.")
        self.cs.send(data.encode("UTF-8"))
        # Waiting for the client (ev3 brick) to let the server know that it is done moving
        reply = self.cs.recv(128).decode("UTF-8")
        queue.put(reply)
        # block is true because we want to wait for the motors to fully move before continuing the program
        assert queue.get(block=True) == "DONE" 


def estimate_jacobian():
    # We move the base motor by 10 degrees, record the initial and final points,
    # and do the same for the second motor. The reset part is done in initial_jacobian() in client.py
    ### Reset done in initial_jacobian() in client.py. The reason is that since we assume we do not
    ### know the motor angles, I can't just send 
    theta = 15

    u0, v0, _ = tracker.point
    # Theta 1
    server.sendAngles(theta, 0, queue)
    time.sleep(2)
    u1, v1, _ = tracker.point

    # Theta 2
    server.sendAngles(0, theta, queue)
    time.sleep(2)
    u2, v2, _ = tracker.point

    jacobian = [[(u1-u0)/theta, (u2-u0)/theta], 
                [(v1-v0)/theta, (v2-v0)/theta]]
    
    time.sleep(1)
    return Matrix(jacobian)

def inverse(j):
    # Computes the inverse of a 2*2 jacobian
    a, b, c, d = *j[0], *j[1]
    det = a*d - b*c  # determinants
    return Matrix([[d, -b], [-c, a]]).multiply_with_scalar(1/det)

def broyden():
    # Assuming we already have the initial jacobian

    # The goal and end effector positions, respectively, in pixel coordinates
    goal = Vector(tracker.goal[:-1])
    point = Vector(tracker.point[:-1])

    # The error vector. It is the vector from the point to the goalv
    error = goal - point
    threshold = 25   # 25 pixels
    
    jacobian = initial_jacobian
    idx = 0
    while error.norm() > threshold:
        print(error.norm(), goal, Vector(tracker.point[:-1]))
        # print(inverse(jacobian), error)
        delta_angles = inverse(jacobian).multiply_with_vector(error).multiply_with_scalar(0.25)
        server.sendAngles(delta_angles[0], delta_angles[1], queue)
        time.sleep(2)
        ## Not tested yet (I have a class, sorry!)
        if idx % 5 == 0:
            print("hii")
            # pass
            jacobian = jacobian + ((error - jacobian.multiply_with_vector(delta_angles)).multiply_with_scalar(1 / delta_angles.dot_product(delta_angles))).outer_product(delta_angles).multiply_with_scalar(.10)
        error = goal - Vector(tracker.point[:-1])
        idx += 1
    
    print("DONE", error.norm())

global server, tracker, queue, initial_jacobian

host = "169.254.225.196"
port = 9999
server = Server(host, port)
queue = Queue()

print("Tracker Setup")
tracker = Tracker('g', 'r')
time.sleep(2)
print("Moving on")

while True:
    initial_jacobian = estimate_jacobian()
    time.sleep(1)
    broyden()
    input()