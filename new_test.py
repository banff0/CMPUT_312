#!/usr/bin/env python3

from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor


# outputs 
mtr_b = LargeMotor(OUTPUT_B)
mtr_d = LargeMotor(OUTPUT_D)
drive = MoveTank(OUTPUT_B, OUTPUT_D)

# inputs
ultra_sens = UltrasonicSensor(INPUT_2)
ultra_sens.MODE_US_DIST_CM = 'US-DIST-CM'

r_light = ColorSensor(INPUT_4)
l_light = ColorSensor(INPUT_1)
# r_light.MODE_COL_AMBIENT = "COL-AMBIENT"
# l_light.MODE_COL_AMBIENT = "COL-AMBIENT"




# for i in range(5):
#     print(ultra_sens.distance_centimeters_continuous)
#     drive.on_for_rotations(-100, -100, 1)
#     sleep(1)

def move_shape(shape):

    fwrd_speeds = [-87, -80]
    right_speed = [-90, 100]

    # rectangle 
    if shape == "rect":
        drive.on_for_rotations(*fwrd_speeds, 4)
        drive.on_for_rotations(*right_speed, .9)
        drive.on_for_rotations(*fwrd_speeds, 4)
        drive.on_for_rotations(*right_speed, .9)
        drive.on_for_rotations(*fwrd_speeds, 4)
        drive.on_for_rotations(*right_speed, .9)
        drive.on_for_rotations(*fwrd_speeds, 4)
        drive.on_for_rotations(*right_speed, .9)
    # lemniscade
    else:
        drive.on_for_rotations(*fwrd_speeds, 1)
        drive.on_for_rotations(-55, -10, 4.5)
        drive.on_for_rotations(*fwrd_speeds, 2)
        drive.on_for_rotations(-10, -55, 4.5)
        drive.on_for_rotations(*fwrd_speeds, 1)

def brait(behave):
    if behave == "cower":
        while True:
            print(r_light.ambient_light_intensity, l_light.ambient_light_intensity)
    else:
        pass


# move_shape("rect")


brait("cower")