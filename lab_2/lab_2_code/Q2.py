#!/usr/bin/env python3

"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 18-Sep-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 

	...

Brief Solution Summary:
5
	Algorithmic idea, underlying theory, etc...

Used Resources/Collaborators:
	...

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B
from ev3dev2.button import Button
from math import cos, sin, radians
from time import sleep

# All length units are in cm, all angles are in degrees

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT):
        super(ArmMotor, self).__init__(OUTPUT)
        self.agg_theta = 0  # Aggregate Theta. This is the current angle the motor is at
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand

    def move_angle(self, theta, spd=25):
        self.on_for_degrees(spd, theta)
        self.agg_theta += theta

    def reset(self):
        self.move_angle(-self.agg_theta)
    
    def __str__(self) -> str:
        return str(self.position)

def calculate_coordinates(l1, l2, theta1, theta2):
    theta1, theta2 = radians(theta1), radians(theta2)
    x = l1*cos(theta1) + l2*cos(theta1+theta2)
    y = l1*sin(theta1) + l2*sin(theta1+theta2)
    return [x, y]

Button.on_up = lambda x: points.append(calculate_coordinates)

first_motor = ArmMotor(OUTPUT_D)
second_motor = ArmMotor(OUTPUT_B)

l1 = 11
l2 = 7

# def get_angle(motor):
#     return motor.position

# def move_mtr(mtr, theta):
#     mtr.on_for_degrees(80, theta)

# first_motor.move_angle(90)
# second_motor.move_angle(90)
# first_motor.move_angle(-90)


sleep(5)
print(first_motor, second_motor)
print(calculate_coordinates(l1, l2, first_motor.agg_theta, second_motor.agg_theta))


input()
first_motor.reset()
second_motor.reset()

points = []
