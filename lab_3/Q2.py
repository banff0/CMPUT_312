#!/usr/bin/env python3

"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 16-Oct-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 

	...

Brief Solution Summary:

	Algorithmic idea, underlying theory, etc...

Used Resources/Collaborators:
	- python-ev3dev2 API reference: https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html
    - Lecture Slides

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B

from math import cos, sin, radians, degrees, acos, atan2
import traceback
from time import sleep

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT, block):
        super(ArmMotor, self).__init__(OUTPUT)
        self.initial_pos = self.position
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand
        self.block = block
        
    def move_angle(self, theta, spd=10):
        self.on_for_degrees(spd, theta, block=self.block)

    def reset(self):
        self.move_angle(-self.position) 
        # self.move_angle(self.initial_pos-self.position) 

    def calibrated_position(self):
        #return self.position
        return super().position-self.initial_pos
    
    def __str__(self) -> str:
        return str(self.calibrated_position())
    
def calculate_coordinates(theta1, theta2):
    theta1, theta2 = radians(theta1), radians(theta2)
    x = l1*cos(theta1) + l2*cos(theta1+theta2)
    y = l1*sin(theta1) + l2*sin(theta1+theta2)
    return [x, y]

first_motor = ArmMotor(OUTPUT_D, False)
second_motor = ArmMotor(OUTPUT_B, False)
first_motor.position = 0
second_motor.position = 0

try:
    global l1, l2
    l1 = 11
    l2 = 7

    print("First Motor Initial: {}, Second Motor Initial: {}".format(first_motor.calibrated_position(), second_motor.calibrated_position()))

    # Starting Position: (18, 0)
    x = 0
    y = 18
    print(calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position()))   

    first_motor.move_angle(20)
    second_motor.move_angle(20)

except Exception:
    traceback.print_exc()
finally:
    input()
    first_motor.reset()
    second_motor.reset()
    second_motor.wait_while('running')
    print("First Motor Final: {}, Second Motor Final: {}".format(first_motor, second_motor))