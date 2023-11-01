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

from math import degrees
from util import ArmMotor, Vector, calculate_coordinates, inverse_kin_analytical

import traceback  # For printing exceptions using traceback.print_exc(), should any arise

# All length units are in cm, all angles are in degrees

def move_to_position(x, y, theta1, theta2):

    x_init, y_init = calculate_coordinates(theta1, theta2)

    print(x_init, y_init)

    # We want to divide our path into 10 segments
    num_steps = 10

    # Total distance from our current position to our goal
    tot_x_dist = x - x_init
    tot_y_dist = y - y_init
    
    # Distance of one path segment
    x_step = tot_x_dist / num_steps
    y_step = tot_y_dist / num_steps

    for step in range(1, num_steps + 1):
        if step == num_steps:
            # In the last step, we can use the actual (x,y) coordinates we would like to end up at. 
            # We do this to avoid rounding errors in the last step
            new_theta1, new_theta2 = inverse_kin_analytical(x, y, old_theta2)
        else:
            # We get the angles required to be at the end of the current segment
            new_theta1, new_theta2 = inverse_kin_analytical(x_init + x_step * step, y_init + y_step * step, theta2)
        
        # Since we want the movement to be as smooth as possible, we make the base motor and joint motor
        # rotate at the same time (so their movement is non-blocking).
        second_motor.move_angle(round(degrees(new_theta2) - old_theta2), block=False)
        first_motor.move_angle(round(degrees(new_theta1) - old_theta1), block=False)
        # Since their movement is non-blocking, we have this command to make sure we don't continue with the loop
        # iterations until both motors have stopped running.
        second_motor.wait_while('running')
        first_motor.wait_while('running')

        # Update the angles we're currently at to be the current position of the motor to overcome errors in
        # motor movement
        old_theta1, old_theta2 = first_motor.position, second_motor.position
    
    # Print the position the robot is at by the end of this function
    print("Moved to position: ", calculate_coordinates(first_motor.position, second_motor.position))

    return [theta1, theta2]

def get_points(num_points):
    # This function allows us to use the touch sensor to record an arbitrary number of points
    # based on the current angular position of the motors
    points = []
    for _ in range(num_points):
        btn.wait_for_pressed()
        print("CLICKED")
        points.append(calculate_coordinates(first_motor.position, second_motor.position))
        print(points[-1])
        btn.wait_for_released()
    return points

def go_to_point():
    # This function is the main program function. It goes from our current position to thr position
    # returned by get_points(1). 
    # We basically move the end effector to the destination point, record it by clicking the 
    # touch sensor, then move it to our starting position. After the touch sensor is clicked again,
    # we start moving towards our destination point.
    x, y = get_points(1)[0]
    btn.wait_for_pressed()
    print("CLICKED")
    move_to_position(x, y, first_motor.position, second_motor.position)

try:
    print("RUNNING...")
    global first_motor, second_motor, btn

    first_motor = ArmMotor(OUTPUT_D)
    second_motor = ArmMotor(OUTPUT_B)
    # Reset the motors to so that they're at 0, 0 at the start of the program. We do this because our calculate_coordinates()
    # function returns the angles needed to reach position (x,y) from the starting position (18, 0)
    first_motor.position, second_motor.position = 0, 0
    btn = TouchSensor(INPUT_1)
    print("First Motor Initial Pos: {}, Second Motor Initial Pos: {}".format(first_motor.position, second_motor.position))

    # Starting Position: (18, 0)
    
    go_to_point()

except Exception:
    traceback.print_exc()
finally:
    input()
    first_motor.reset()
    second_motor.reset()
    print("First Motor Final: {}, Second Motor Final: {}".format(first_motor, second_motor))