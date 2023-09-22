"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 18-Sep-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 
	(From Part 4 Description) 
    Write a program that receives as input a 3x3 array. The first two 
    columns are the left and right motor power respectively, the last 
    column is the time during which the power is apply to the motors.
    After it is done executing all three rows the robot has to transmit 
    its location and orientation to the PC and/or show it in the display. 

Brief Solution Summary:

	Algorithmic idea, underlying theory, etc...

Used Resources/Collaborators:
	python-ev3dev API reference: https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""
#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, MoveTank

from math import pi, degrees, sin, cos

# outputs 
mtr_b = LargeMotor(OUTPUT_B)  # Left Motor
mtr_d = LargeMotor(OUTPUT_D)  # Right Motor
drive = MoveTank(OUTPUT_B, OUTPUT_D)

def kinematics(cmds):
    # features of the robot
    d = 5.5  # diameter 
    l = 18   # l is equivalent to 2d in lab notes
    # start the robot at the origin, facing up

    sub_steps = 4

    last_position = [0, 0]
    final_position = last_position
    omega_agg = 0  # Aggregate Omega (in radians)
    for cmd in cmds:
        p1, p2, t = cmd
        for _ in range(t*sub_steps):
            tr_rot = -mtr_d.position
            tl_rot = -mtr_b.position
            time_per_step = t/sub_steps
            drive.on_for_seconds(-p1, -p2, time_per_step, brake=False)
            
            # Number of rotations for left and right wheel respectively, calculated using the number
			# of ticks the motor rotated. There are 360 ticks/rotation
            l_rot = (-mtr_b.position - tl_rot) / mtr_b.count_per_rot 
            r_rot = (-mtr_d.position - tr_rot) / mtr_d.count_per_rot  

            # phi1 and phi2 below are the linear velocities of the wheels, in cm/s
            phi1 = (pi * d * l_rot)
            phi2 = (pi * d * r_rot)

            if phi2 == phi1:
                # To avoid DivisionByZeroError
                final_position = [phi1*time_per_step + last_position[0], last_position[1]]
            else:
                # from lab notes
                omega = (phi2 - phi1) / l
                radius_of_curvature = (l/2) * ((phi2 + phi1) / (phi2 - phi1))
                v = radius_of_curvature*omega
                omega_agg += omega
                
                final_position = [v*cos(omega_agg) + last_position[0], v*sin(omega_agg) + last_position[1]]
            last_position = final_position
            
    orientation = [final_position[0], final_position[1], degrees(omega_agg)]
    return orientation



commands = [
    [ 80, 60, 2],
    [ 60, 60, 1],
    [-50, 80, 2]
]

# Uncomment the following lines to run the program and print the orientation

#orientation = kinematics(commands)
#print(orientation)

    


