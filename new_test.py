#!/usr/bin/env python3

from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import UltrasonicSensor


# outputs 
mtr_b = LargeMotor(OUTPUT_B)
mtr_d = LargeMotor(OUTPUT_D)
drive = MoveTank(OUTPUT_B, OUTPUT_D)

# inputs
ultra_sens = UltrasonicSensor(INPUT_2)
ultra_sens.MODE_US_DIST_CM = 'US-DIST-CM'


# for i in range(5):
#     print(ultra_sens.distance_centimeters_continuous)
#     drive.on_for_rotations(-100, -100, 1)
#     sleep(1)

shape = "lem"

fwrd_speeds = [-90, -45]
right_speed = [-90, 100]

# rectangle 
if shape == "rect":
    drive.on_for_rotations(*fwrd_speeds, 5)
    drive.on_for_rotations(*right_speed, 9)
    drive.on_for_rotations(*fwrd_speeds, 5)
    drive.on_for_rotations(*right_speed, 9)
    drive.on_for_rotations(*fwrd_speeds, 5)
    drive.on_for_rotations(*right_speed, 9)
    drive.on_for_rotations(*fwrd_speeds, 5)
    drive.on_for_rotations(*right_speed, 9)
else:
    drive.on_for_rotations(-50, -25, 10)


# mtr_b.on_for_rotations(SpeedPercent(75), 5)
# mtr_d.on_for_rotations(SpeedPercent(75), 5)

# drive.on_for_rotations(-50, 50, 20)
# drive.on_for_rotations(-100, -100, 5)

