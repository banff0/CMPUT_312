#!/usr/bin/env python3


from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_C

from ev3dev2.sensor import INPUT_1 
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.button import Button
from math import cos, sin, radians, degrees, sqrt, acos
from time import sleep

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT):
        super(ArmMotor, self).__init__(OUTPUT)
        self.position = 0
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand
        

    def move_angle(self, theta, spd=20, block=True):
        self.on_for_degrees(spd, theta, block = block)

    def reset(self):
        self.move_angle(-self.position) 
    
    def __str__(self) -> str:
        return str(self.calibrated_position())
    

y_mtr = ArmMotor(OUTPUT_D)
x_mtr = ArmMotor(OUTPUT_C)

# x_mtr.move_angle(360 * 1, spd=20, block=True)
# sleep(1)
# x_mtr.reset()

# y_mtr.move_angle(-360 * 3)
# y_mtr.reset()


# y_mtr.STOP_ACTION_HOLD = "coast"
# x_mtr.STOP_ACTION_HOLD = "coast"

dx = 0.1
dy = 0.095

for i in range(0, 10):
    # y_mtr.move_angle(-360 * 0.03, spd=5 + (i/5) * 2, block=False)
    # x_mtr.move_angle(-360 * 0.03, spd=25 - (i/5) * 2, block=True)
    # print(5 + (i/5) * 2, 25 - (i/5) * 2)

    # y_mtr.move_angle(-360 * (0.5 - i/10), spd=25, block=False)
    # x_mtr.move_angle(-360 * (0.1 + i/10), spd=25, block=True)

    ratio = ((100*dx)/(100*dy))
    x_mtr.move_angle(360 * (dx), spd = 10 * ratio, block=False)
    y_mtr.move_angle(-360 * (dy), spd = 10, block=True)

    dx -= 0.01
    dy += 0.01

    print(dx, dy, 10 * ratio)
    
# y_mtr.STOP_ACTION_HOLD = "brake"
# x_mtr.STOP_ACTION_HOLD = "brake"

# for i in range(1, 6):
#     y_mtr.move_angle(-360 * 0.1, spd=15 + i, block=False)
#     x_mtr.move_angle(-360 * 0.1, spd=3*i, block=True)

# y_mtr.move_angle(360 * 1, spd=15, block=True)

# x_mtr.move_angle(-360 * 1, spd=15, block=True)

# y_mtr.move_angle(360 * 1, spd=20, block=True)

# x_mtr.move_angle(-360 * 1, spd=10, block=True)

# y_mtr.move_angle(-360 * 1.5, block=True)

# x_mtr.move_angle(-360 * 1.5, block=True)

# y_mtr.reset()

# x_mtr.reset()


# x_mtr.move_angle(360 * 1)
# y_mtr.move_angle(360 * 1)
# x_mtr.move_angle(-360 * 1)
# y_mtr.move_angle(-360 * 1)