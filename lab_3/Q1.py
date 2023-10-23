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

from ev3dev2.motor import OUTPUT_D, OUTPUT_B

from ev3dev2.sensor import INPUT_1 
from ev3dev2.sensor.lego import TouchSensor
from math import cos, sin, radians, degrees, acos, atan2
from time import sleep

from util import ArmMotor, calculate_coordinates, l1, l2

import traceback  # For printing exceptions using traceback.print_exc(), should any arise

# All length units are in cm, all angles are in degrees

def inverse_kin_analytical(x, y, init_theta2):
    init_theta2 = radians(init_theta2)
    theta2 = acos((x**2 + y**2 - l1**2 - l2**2) / (2*l1*l2))
    theta2_options = [theta2, -theta2]
    theta2 = theta2_options[0] if abs(theta2_options[0] - init_theta2) < abs(theta2_options[1] - init_theta2) else theta2_options[1]

    theta1 = atan2(y, x) - atan2(l2 * sin(theta2), l1 + l2 * cos(theta2))

    return [theta1, theta2]

def move_to_position(x, y, theta1, theta2):

    x_init, y_init = calculate_coordinates(theta1, theta2)

    print(x_init, y_init)

    tot_x_dist = x - x_init
    tot_y_dist = y - y_init

    step_size = 10

    x_step = tot_x_dist / step_size
    y_step = tot_y_dist / step_size

    for step in range(1, step_size + 1):
        print(x_init + x_step * step)
        print(y_init + y_step * step)

        if step == step_size:
            dtheta1, dtheta2 = inverse_kin_analytical(x, y, theta2)
        else:
            dtheta1, dtheta2 = inverse_kin_analytical(x_init + x_step * step, y_init + y_step * step, theta2)
        
        second_motor.move_angle(round(degrees(dtheta2) - theta2))
        first_motor.move_angle(round(degrees(dtheta1) - theta1))
        # second_motor.wait_while('running')
        first_motor.wait_while('running')

        theta1 = degrees(dtheta1)
        theta2 = degrees(dtheta2)
    # inverse_kin_numerical(x, y, theta1, theta2)
    
    print(theta1, theta2)
    #second_motor.move_angle(round(degrees(theta2)))
    #first_motor.move_angle(round(degrees(theta1)))

    print("Moved to position: ", calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position()))

    return [theta1, theta2]

def get_points(num_points):
    # Should be able to get an arbitrary number of points now
    points = []
    for _ in range(num_points):
        btn.wait_for_pressed()
        print("CLICKED")
        calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position())
        points.append(calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position()))
        print(points[-1])
        btn.wait_for_released()
    return points

def go_to_point():
    x, y = get_points(1)[0]
    btn.wait_for_pressed()
    print("CLICKED")
    move_to_position(x, y, first_motor.position, second_motor.position)


print("RUNNING...")

first_motor = ArmMotor(OUTPUT_D, False)
second_motor = ArmMotor(OUTPUT_B, False)
first_motor.position = 0
second_motor.position = 0
btn = TouchSensor(INPUT_1)

try:
    print("First Motor Initial: {}, Second Motor Initial: {}".format(first_motor.calibrated_position(), second_motor.calibrated_position()))

    # Starting Position: (18, 0)
    x = 0
    y = 18
    print(calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position()))
    
    go_to_point()

except Exception:
    traceback.print_exc()
finally:
    input()
    first_motor.reset()
    second_motor.reset()
    print("First Motor Final: {}, Second Motor Final: {}".format(first_motor, second_motor))