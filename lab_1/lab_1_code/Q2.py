"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 18-Sep-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 
	Q2 of Lab 1, CMPUT312. Error analysis of a differential drive robot moving
    in a straight line and when rotating. At least 2 methods must be used when 
    measuring errors in each of those movements, at least 1 of which must use a sensor.
    

Brief Solution Summary:
	We pick a movement, and whether we want high or low power. Then we run the same movement
	at the chosen power 3 times, pausing for 30 seconds between eash time so we can make some
	markings for the actual measurement of the movement (distance for straight line, angle for
	rotations), and also printing out the sensor readings after each time.
	

Used Resources/Collaborators:
	python-ev3dev API reference: https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""
#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, MoveTank
from ev3dev2.sensor import INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from time import sleep

# outputs 
mtr_b = LargeMotor(OUTPUT_B)  # Left Motor
mtr_d = LargeMotor(OUTPUT_D)  # Right Motor
drive = MoveTank(OUTPUT_B, OUTPUT_D)

# inputs
ultra_sens = UltrasonicSensor(INPUT_2)
ultra_sens.MODE_US_DIST_CM = 'US-DIST-CM'

gryro_sens = GyroSensor(INPUT_3)
gryro_sens.MODE_GYRO_ANG = 'GYRO-ANG'
gryro_sens.reset()

def measurements(straight_line=True, fast=True):
	# Initial States
	s_dist = ultra_sens.distance_centimeters_continuous
	s_deg = gryro_sens.angle

	fwrd_fast = [-87, -80]
	fwrd_slow = [-22, -20]

	clockwise_fast = [-80, 80] 
	clockwise_slow = [-20, 20]

	straight_line = True
	fast = True
	for i in range(3):
		rotations = 1
		if straight_line:
			if fast:
				drive.on_for_rotations(*fwrd_fast, rotations)
			else:
				drive.on_for_rotations(*fwrd_slow, rotations)
			current_dist = ultra_sens.distance_centimeters_continuous
			print(s_dist - current_dist)
			s_dist = current_dist
		else:
			if fast:
				drive.on_for_rotations(*clockwise_fast, rotations)
			else:
				drive.on_for_rotations(*clockwise_slow)
			current_deg = gryro_sens.angle
			print(current_deg - s_deg)
			s_deg = current_deg
		sleep(30)

#### Uncomment a line below to get a certain movement with a certain power

#measurements(True, True)    # Straight Line, High Power
#measurements(True, False)   # Straight Line, Low Power
#measurements(False, True)   # Rotation     , High Power
#measurements(False, False)  # Rotationm    , Low Power
	
