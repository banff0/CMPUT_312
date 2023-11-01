#!/usr/bin/env python3

from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor, GyroSensor

from math import pi, cos, sin, degrees
# import numpy as np


# outputs 
mtr_b = LargeMotor(OUTPUT_B)
mtr_d = LargeMotor(OUTPUT_D)
# mtr_b.polarity = mtr_b.POLARITY_INVERSED
# mtr_d.polarity = mtr_d.POLARITY_INVERSED
drive = MoveTank(OUTPUT_B, OUTPUT_D)
# drive.polarity = mtr_b.POLARITY_INVERSED

print(mtr_b.count_per_rot, mtr_d.count_per_rot)
# drive.on_for_rotations(-80, -80, 1)
print(mtr_b.position, mtr_d.position)

# inputs
ultra_sens = UltrasonicSensor(INPUT_2)
ultra_sens.MODE_US_DIST_CM = 'US-DIST-CM'

gryro_sens = GyroSensor(INPUT_3)
gryro_sens.MODE_GYRO_ANG = 'GYRO-ANG'
gryro_sens.reset()

l_light = ColorSensor(INPUT_4)
r_light = ColorSensor(INPUT_1)
# r_light.MODE_COL_AMBIENT = "COL-AMBIENT"
# l_light.MODE_COL_AMBIENT = "COL-AMBIENT"

'''
s_dist = ultra_sens.distance_centimeters_continuous
s_deg = gryro_sens.angle
for i in range(3):
    drive.on_for_rotations(-22, -20, 1)
    print(s_dist - ultra_sens.distance_centimeters_continuous, gryro_sens.angle)
    sleep(10)
'''


def move_shape(shape):

    fwrd_speeds = [-87, -80]
    right_speed = [-90, 100]

    # rectangle 
    if shape == "rect":
        for i in range(4):
            drive.on_for_rotations(*fwrd_speeds, 3)
            drive.on_for_rotations(*right_speed, .9)
            #drive.on_for_rotations(*fwrd_speeds, 4)
            #drive.on_for_rotations(*right_speed, .9)
            #drive.on_for_rotations(*fwrd_speeds, 4)
            #drive.on_for_rotations(*right_speed, .9)
            #drive.on_for_rotations(*fwrd_speeds, 4)
            #drive.on_for_rotations(*right_speed, .9)
    # lemniscade
    else:
        for i in range(1):
            drive.on_for_rotations(*fwrd_speeds, 1)
            drive.on_for_rotations(-55, -10, 4.5)
            drive.on_for_rotations(*fwrd_speeds, 2)
            drive.on_for_rotations(-10, -55, 4.5)
            drive.on_for_rotations(*fwrd_speeds, 1)

def kin(cmds):
    # features of the robot
    r = 5.5
    l = 9
    # start the robot at the origin, facing up
    x = 0
    y = 0
    theta = pi / 2
    
    tr_rot = 0
    tl_rot = 0
    r_rot = 0
    l_rot = 0

    sub_steps = 4

    for cmd in cmds:
        p1, p2, t = cmd

        for i in range(t*sub_steps):
            tr_rot = -mtr_b.position
            tl_rot = -mtr_d.position

            drive.on_for_seconds(-p1, -p2, t/sub_steps)
            # print(-mtr_b.position, -mtr_d.position)

            r_rot = (-mtr_b.position - tr_rot) / mtr_b.count_per_rot
            l_rot = (-mtr_d.position - tl_rot) / mtr_d.count_per_rot

            phi1 = pi * r * r_rot 
            phi2 = pi * r * l_rot

            print(phi1, phi2)


            # calc the instantaniuos vel in the robo frame
            xr = (phi1) / 2 + (phi2) / 2 
            yr = 0
            thetar = (phi2 - phi1) / (2*l)
            # calc the instantanious vel in the world frame
            dx = xr * cos(theta)
            dy = xr * sin(theta)
            dtheta = thetar
            # move according to the insructions
            
            # update the global pose
            print(dx, dy, dtheta)
            print("GT: theta:" + str(gryro_sens.angle))
            # x += dx * t
            # y += dy * t
            # theta += dtheta * t
            x += dx
            y += dy
            theta += dtheta
            # sleep(5)
            print(x, y, theta)

def kin_firas(cmds):
    # features of the robot
    r = 5.5  # diameter NOT radius
    l = 18    # l is equivalent to 2d in lab notes
    # start the robot at the origin, facing up
    x = 0
    y = 0
    
    tr_rot = 0
    tl_rot = 0
    r_rot = 0
    l_rot = 0

    sub_steps = 4

    last_position = [0, 0]
    final_position = last_position
    omega_agg = 0
    for cmd in cmds:
        p1, p2, t = cmd
        for i in range(t*sub_steps):
            tr_rot = -mtr_d.position
            tl_rot = -mtr_b.position
            time_per_step = t/sub_steps
            drive.on_for_seconds(-p1, -p2, time_per_step, brake=False)
            # print(-mtr_b.position, -mtr_d.position)
            #print(-mtr_d.position, tr_rot, mtr_d.count_per_rot)
            # Number of rotations for left and right wheel respectively
            l_rot = (-mtr_b.position - tl_rot) / mtr_b.count_per_rot 
            r_rot = (-mtr_d.position - tr_rot) / mtr_d.count_per_rot  

            # phi1 and phi2 below are the distances covered by the left and right wheels
            # respectively. We can consider this distance to be the velocity of the
            # wheels, in cm/s, if and only if our time steps are 1 second long
            phi1 = (pi * r * l_rot)
            phi2 = (pi * r * r_rot)

            # linear velocity of the wheel (cm/s), since linear_v = angular_v * radius = omega * 5.5/2
            # when dt == 1, phi1 == phi1_mod and phi2 == phi2_mod
            #phi1_mod = radians(-mtr_b.position - tl_rot) * r/2
            #phi2_mod = radians(-mtr_d.position - tr_rot) * r/2

            print(phi1, phi2)
            #print(phi1_mod, phi2_mod)
            # from lab notes
            if phi2 == phi1:
                final_position = [phi1*time_per_step + last_position[0], last_position[1]]
                print(final_position)
                last_position = final_position
            else:
                omega = (phi2 - phi1) / l
                radius_of_curvature = (l/2) * ((phi2 + phi1) / (phi2 - phi1))
                v = radius_of_curvature*omega
                omega_agg += omega
                print(degrees(omega), degrees(omega_agg))

                
                final_position = [v*cos(omega_agg) + last_position[0], v*sin(omega_agg) + last_position[1]]
                # Velocity is always in the x-direction
                #translation = [final_position[i]-initial_position[i] for i in range(2)]
                #translation[0] += (radius_of_curvature - radius_of_curvature*cos(omega)) + v*cos(omega)
                #translation[1] += -(radius_of_curvature*sin(omega)) + v*sin(omega)
                print(last_position)
                print(final_position)
                last_position = final_position
                #print(translation)
            #initial_position = final_position
    print(final_position + [degrees(omega_agg)])

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
            if behave == "cower":
                drive.on(-r_speed, -l_speed)
            else:
                drive.on(l_speed * -1, r_speed * -1)
            


#move_shape("lem")

""" kin_firas(
    [
      [80, 60, 2],
      [60, 60, 1],
      [-50, 80, 2]
    ]
)
"""

#brait("cower")
#brait("agress")
