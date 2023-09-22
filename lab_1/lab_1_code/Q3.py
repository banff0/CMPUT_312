"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 18-Sep-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 
	Write a program to make the differential drive robot move in:
      a) a rectangle
      b) a lemniscate

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

# outputs 
mtr_b = LargeMotor(OUTPUT_B)  # Left Motor
mtr_d = LargeMotor(OUTPUT_D)  # Right Motor
drive = MoveTank(OUTPUT_B, OUTPUT_D)

def move_shape(shape):
    fwrd_speeds = [-87, -80]

    # rectangle 
    if shape == "rect":
        right_speed = [-90, 100]
        for i in range(4):
            drive.on_for_rotations(*fwrd_speeds, 3)
            drive.on_for_rotations(*right_speed, .9)
    # lemniscate
    elif shape == "lem":
        drive.on_for_rotations(*fwrd_speeds, 1)
        drive.on_for_rotations(-55, -10, 4.5)
        drive.on_for_rotations(*fwrd_speeds, 2)
        drive.on_for_rotations(-10, -55, 4.5)
        drive.on_for_rotations(*fwrd_speeds, 1)
            

#### Uncomment a line below and run to get a shape

#move_shape("rect")
#move_shape("lem")