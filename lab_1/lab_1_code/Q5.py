"""
Group Members: 
    - Name: Firas Al Chalabi, CCID: falchala
    - Name: Jasper Leng, CCID:jleng1

Date: 18-Sep-2023
 
Brick Number: G8

Lab Number: D01
 
Brief Program/Problem Description: 
	(From Part 5 Description) 
    Using light detecting sensors, implement the following behaviours in reaction to a light source on your robot:
		- Cowardice
		- Aggression

Brief Solution Summary:
	For aggression, increase power to motor opposite to the sensor with higher light intensity reading.
    For cowardice, increase power to motor adjacent to the sensor with higher light intensity reading.

Used Resources/Collaborators:
	python-ev3dev API reference: https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html

I/we hereby certify that we have produced the following solution 
using only the resources listed above in accordance with the 
CMPUT 312 collaboration policy.
"""
#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import ColorSensor

mtr_b = LargeMotor(OUTPUT_B)
mtr_d = LargeMotor(OUTPUT_D)

drive = MoveTank(OUTPUT_B, OUTPUT_D)

print(mtr_b.count_per_rot, mtr_d.count_per_rot)
print(mtr_b.position, mtr_d.position)

l_light = ColorSensor(INPUT_4)
r_light = ColorSensor(INPUT_1)

def brait(behave):
    while True:
            r_bright = r_light.ambient_light_intensity
            l_bright = l_light.ambient_light_intensity
            print(r_bright, l_bright)
            if r_bright - l_bright >= 5:
                r_speed = 20 * r_bright
                l_speed = 10 * l_bright
            elif r_bright - l_bright <= -5:
                r_speed = 10 * r_bright
                l_speed = 20 * l_bright
            else:
                r_speed, l_speed = 10*r_bright, 10*l_bright
            r_speed = max(-100, min(100, r_speed))
            l_speed = max(-100, min(100, l_speed))
            if behave == "cowardice":
                drive.on(-r_speed, -l_speed)
            elif behave == "aggression":
                drive.on(l_speed * -1, r_speed * -1)
                
# Uncomment one of the following lines to make the robot behave aggresively or cowardly

#brait("aggression")
#brait("cowardice")
