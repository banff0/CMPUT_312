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
from math import cos, sin, radians, degrees, sqrt, acos, asin, atan2, pi
from time import sleep

# from Q2 import calculate_coordinates

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
    x = l1*cos(theta1) + l2*cos(theta1+theta2)
    y = l1*sin(theta1) + l2*sin(theta1+theta2)
    return [x, y]

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

def inverse_kin_analytical(x, y):
    theta2 = acos((x**2 + y**2 - l1**2 - l2**2) / (2*l1*l2))
    theta2_options = [theta2, -theta2]

    ftheta1_options = [asin((l2*sin(t2))/sqrt(x**2 + y**2)) + (atan2(y, x)) for t2 in theta2_options]

    theta1_options = [atan2(y, x) - atan2(l2 * sin(theta2_i), l1 + l2 * cos(theta2_i)) for theta2_i in theta2_options]

    # print("Firas sol: {}, Jasper sol: {}".format(ftheta1_options, theta1_options))

    min_euclidean = 100  # Euclidian distance between calculated_point and true_point
    best_thetas = []
    true_point = (x, y)
    for theta1 in theta1_options:
        for theta2 in theta2_options:
            calculated_point = calculate_coordinates(theta1, theta2)
            current_euclidean = get_euclidean(calculated_point, true_point)
            if current_euclidean < min_euclidean:
                best_thetas = [theta1, theta2]
                min_euclidean = current_euclidean

    return best_thetas  #[theta1, -theta2]

def newtons(x, y):
    theta1, theta2 = first_motor.calibrated_position(), second_motor.calibrated_position()
    init_theta1, init_theta2 = theta1, theta2

    # Using Newton's method
    # Initializing vectors
    J = [[0,0],[0,0]]    
    
    
    for angle in range(1, 3):
        for j in range(2):
            if j == 0:
                theta1 = radians(init_theta1 + angle)
                theta2 = radians(init_theta2 + angle)
            else:
                theta1 = radians(init_theta1 - angle)
                theta2 = radians(init_theta2 - angle)
            x_dist = 100
            y_dist = 100
            prev_theta1 = 100
            prev_theta2 = 100
            idx = 0
            sig_dig = 6

            # while abs(x_dist) > 0.5 or abs(y_dist) > 0.5 and i < 10:
            while round(prev_theta1, sig_dig) != round(theta1, sig_dig) and round(prev_theta2, sig_dig) != round(theta2, sig_dig) and idx < 100:
                # Partial derivative of f1 with respect to theta1
                J[0][0] = -l1*sin(theta1)-l2*sin(theta1+theta2)
                # Partial derivative of f1 with respect to theta2
                J[0][1] = -l2*sin(theta1+theta2)
                # Partial derivative of f2 with respect to theta1
                J[1][0] = l1*cos(theta1)+l2*cos(theta1+theta2)
                # Partial derivative of f2 with respect to theta2
                J[1][1] = l2*cos(theta1+theta2)
                det = (J[0][0] * J[1][1]) - (J[0][1] * J[1][0])

                inv_J = [[J[1][1], -J[0][1]],
                        [-J[1][0], J[0][0]]]
                for i in range(2):
                    inv_J[i][0] /= det
                    inv_J[i][1] /= det

                # f(r)
                pos = calculate_coordinates(theta1, theta2)
                # W - f(r)
                x_dist = x - pos[0]
                y_dist = y - pos[1]

                x_dot = (-l1 * sin(prev_theta1) - l2 * sin(prev_theta1 + prev_theta2) * theta1) - (l2 * sin(prev_theta1 + prev_theta2) * theta2)
                y_dot = (l1 * cos(prev_theta1) + l2 * cos(prev_theta1 + prev_theta2) * theta1) + (l2 * cos(prev_theta1 + prev_theta2) * theta2)

                # x_dot = -(l1 * sin(prev_theta1) * theta1) - (l2 * sin(prev_theta1 + prev_theta2) * (theta1 + theta2))
                # y_dot = (l1 * cos(prev_theta1) * theta1) + (l2 * cos(prev_theta1 + prev_theta2) * (theta1 + theta2))

                # print("distances", x_dist, y_dist)

                # dr = [(J[1][1] / det) * x_dot - (J[0][1] / det) * y_dot, 
                #       (J[1][0] / det) * x_dot + (J[0][0] / det) * y_dot]
                
                # dr = [(cos(theta1 + theta2) / l1 * sin(theta2)) * x_dist + (sin(theta1 + theta2) / l1 * sin(theta2)) * y_dist, 
                #       -(l1 * cos(theta1) + l2 * cos(theta1 + theta2) / l1 * l2 * sin(theta2)) * x_dist + 
                #       (-l1 * sin(theta1) - l2 * sin(theta1 + theta2) / l1 * l2 * sin(theta2)) * y_dist]
                
                dr = [inv_J[0][0] * x_dist + inv_J[0][1] * y_dist, 
                    inv_J[1][0] * x_dist + inv_J[1][1] * y_dist]

                prev_theta1 = theta1
                prev_theta2 = theta2
                theta1 += dr[0]
                theta2 += dr[1]
                # print("thetas", degrees(theta1), degrees(theta2))
                idx += 1
        if idx < 100:
            print("starting theta: ", angle, idx)
            # print("distances", x_dist, y_dist)
            while degrees(abs(theta1)) > 180:
                theta1 -= 2*pi * (theta1 / abs(theta1))
                # print(degrees(theta1), 2*pi * (theta1 / abs(theta1)))
            while degrees(abs(theta2)) > 180:
                theta2 -= 2*pi * (theta2 / abs(theta2))
                # print(degrees(theta2),  2*pi * (theta2 / abs(theta2)))
            return [theta1, theta2]
    return [init_theta1, init_theta2]

def inverse_kin_numerical(x, y):
    theta1, theta2 = 0, 0
    x_init, y_init = calculate_coordinates(radians(theta1), radians(theta2))

    tot_x_dist = x - x_init
    tot_y_dist = y - y_init

    x_step = tot_x_dist / 10
    y_step = tot_y_dist / 10


    for step in range(1, 11):
        print(x_init + x_step * step)
        print(y_init + y_step * step)

        theta1, theta2 = newtons(x_init + x_step * step, y_init + y_step * step)

    # theta1, theta2 = newtons(x, y, 0, 0)
    
    return [theta1, theta2]




    # return newtons(x, y, 0, 0)

def move_to_position(x, y, solution_type):
    if solution_type.lower() == "a":
        theta1, theta2 = inverse_kin_analytical(x, y)
    elif solution_type.lower() == "n":
        theta1, theta2 = inverse_kin_numerical(x, y)
    else:
        raise Exception("Invalid solution type. Please enter 'a' for the analytical solution or 'n' for the numerical solution.")
    
    print(theta1, theta2)
    second_motor.move_angle(round(degrees(theta2)))
    first_motor.move_angle(round(degrees(theta1)))

    print("Moved to position: ", calculate_coordinates(radians(first_motor.calibrated_position()), radians(second_motor.calibrated_position())))

    return [theta1, theta2]

def get_vector(p1, p2):
    # Returns the vector equivalent to p2 - p1
    x1, y1, x2, y2 = *p1, *p2
    return [x2-x1, y2-y1]

def get_points(num_points):
    # Should be able to get an arbitrary number of points now
    points = []
    for _ in range(num_points):
        btn.wait_for_pressed()
        print("CLICKED")
        calculate_coordinates(first_motor.calibrated_position(), second_motor.calibrated_position())
        points.append(calculate_coordinates(radians(first_motor.calibrated_position()), radians(second_motor.calibrated_position())))
        print(points[-1])
        btn.wait_for_released()
    return points

def add_vector(v1, v2):
    return [v1[0]+v2[0], v1[1]+v2[1]]

def midpoint(method):
    points = get_points(2)
    # points = [[1, 1], [2, 2]]
    print(points, "MID_PNT")
    vec = get_vector(points[1], points[0])
    mp = add_vector(points[1], [vec[0]/2, vec[1]/2])

    first_motor.reset()
    second_motor.reset()
    sleep(0.5)


    print("MIDPOINT: ", mp)

    move_to_position(*mp, method)

    # return mp
    #print(get_euclidean(points[0], points[1]))


print("RUNNING...")

first_motor = ArmMotor(OUTPUT_D)
second_motor = ArmMotor(OUTPUT_B)
btn = TouchSensor(INPUT_1)

try:
    global l1, l2
    l1 = 11
    l2 = 7

    print("First Motor Initial: {}, Second Motor Initial: {}".format(first_motor.calibrated_position(), second_motor.calibrated_position()))

    # Starting Position: (18, 0)
    x = 15
    y = 4

    # theta1, theta2 = move_to_position(x, y, "a")
    # theta1, theta2 = move_to_position(x, y, "n")
    # print("theta1 = {}, theta2 = {}".format(degrees(theta1), degrees(theta2)))  # Move to (x,y) position using analytical solution
    # print("First Motor Pos: {}, Second Motor Pos: {}".format(first_motor, second_motor))
    # print((l1*cos(theta1)+l2*cos(theta1+theta2), l1*sin(theta1)+l2*sin(theta1+theta2)))
    # print('robot thinks it is at: ', calculate_coordinates(theta1, theta2))
    # move_to_position(x, y, "n")  # Move to (x,y) position using numerical solution

    midpoint("n")

    #first_motor.move_angle(20)
    #second_motor.move_angle(40)
except Exception:
    traceback.print_exc()
finally:
    input()
    first_motor.reset()
    second_motor.reset()
    print("First Motor Final: {}, Second Motor Final: {}".format(first_motor, second_motor))