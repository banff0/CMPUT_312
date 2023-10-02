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

	Algorithmic idea, underlying theory, etc...

Used Resources/Collaborators:
	- python-ev3dev2 API reference: https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html
    - Lecture Slides

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B

from ev3dev2.sensor import INPUT_1 
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.button import Button
from math import cos, sin, radians, degrees, sqrt, acos
from time import sleep

import traceback  # For printing exceptions using traceback.print_exc(), should any arise

# All length units are in cm, all angles are in degrees

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT):
        super(ArmMotor, self).__init__(OUTPUT)
        self.initial_pos = self.position
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand

    def move_angle(self, theta, spd=10):
        self.on_for_degrees(spd, theta)

    def reset(self):
        self.move_angle(self.initial_pos-self.position) 

    def calibrated_position(self):
        return super().position-self.initial_pos
    
    def __str__(self) -> str:
        return str(self.calibrated_position())

def calculate_coordinates(theta1, theta2):
    l1 = 7
    l2 = 11

    theta1, theta2 = radians(theta1), radians(theta2)
    x = l1*cos(theta1) + l2*cos(theta1+theta2)
    y = l1*sin(theta1) + l2*sin(theta1+theta2)
    return [x, y]

def move(theta1, theta2):
    first_motor.move_angle(theta1)
    second_motor.move_angle(theta2)
    return calculate_coordinates(theta1, theta2)

def norm(v):
    x, y = v
    return sqrt(x**2 + y**2)

def get_vector(p1, p2):
    # Returns the vector equivalent to p2 - p1
    x1, y1, x2, y2 = *p1, *p2
    return [x2-x1, y2-y1]

def get_euclidean(p1, p2):
    # Euclidean == norm(p2-p1) 
    v = get_vector(p1, p2)
    return norm(v)

def dot_product(v1, v2):
    x1, y1, x2, y2 = *v1, *v2
    return x1*x2 + y1*y2

def calculate_angle(p1, p2, p3):
    v1 = get_vector(p1, p2)
    v2 = get_vector(p1, p3)
    print(dot_product(v1, v2)/(norm(v1)*norm(v2)))
    return degrees(acos(dot_product(v1, v2)/(norm(v1)*norm(v2))))

def get_points(num_points):
    # Should be able to get an arbitrary number of points now
    points = []
    for _ in range(num_points):
        btn.wait_for_pressed()
        print("CLICKED")
        points.append(calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position()))
        print(points[-1])
        btn.wait_for_released()
    return points

def get_dist():
    # Q2 c-i)
    points = get_points(2)
    print(points, "GET_DIST")
    print(get_euclidean(points[0], points[1]))

def get_angle():
    # Q2 c-ii)
    # points[0] is the intersection point
    points = get_points(3)
    print(calculate_angle(*points))


print("RUNNING...")

first_motor = ArmMotor(OUTPUT_D)
second_motor = ArmMotor(OUTPUT_B)
btn = TouchSensor(INPUT_1)

try:
    #get_dist()
    #get_angle()

    print(first_motor, second_motor)

    move(32, 60)

    print(first_motor, second_motor)
    # print(c2 - c1)
except Exception:
    traceback.print_exc()
finally:
    input()
    first_motor.reset()
    second_motor.reset()
