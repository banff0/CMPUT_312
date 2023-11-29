#!/usr/bin/env python3


from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_C, OUTPUT_B

from ev3dev2.sensor import INPUT_1 
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.button import Button
from math import cos, sin, radians, degrees, sqrt, acos
from time import sleep

from letters import SWAN
import traceback

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT, invert=False):
        super(ArmMotor, self).__init__(OUTPUT)
        self.position = 0
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand
        if invert:
            self.POLARITY_INVERSED = "inversed"

    def move_angle(self, theta, spd=10, block=True):
        self.on_for_degrees(spd, theta, block = block)

    def reset(self):
        self.move_angle(-self.position) 
    
    def __str__(self) -> str:
        return str(self.calibrated_position())
    

y_mtr = ArmMotor(OUTPUT_D)
x_mtr = ArmMotor(OUTPUT_C)
z_mtr = ArmMotor(OUTPUT_B)

# z_mtr.move_angle(-20, spd=5)
# time.sleep(1)
# x_mtr.move_angle(-360 * 0.5, spd=20)
# z_mtr.move_angle(20, spd=5)
# y_mtr.move_angle(-360 * 0.5, spd=20)

# x_mtr.move_angle(360 * 1, spd=20, block=True)
# sleep(1)
# x_mtr.reset()

# y_mtr.move_angle(-360 * 3)
# y_mtr.reset()


# y_mtr.STOP_ACTION_HOLD = "coast"
# x_mtr.STOP_ACTION_HOLD = "coast"

# y_mtr.move_angle(360 * .5, block=False)
# x_mtr.move_angle(360 * .25)

# y_mtr.move_angle(-360 * .5, block=False)
# x_mtr.move_angle(-360)


### ARC
# z_mtr.move_angle(-20, spd=5)
# dx = 0.05
# dy = 0.0
# num_steps = 20

# step = (abs(dx - dy)) / num_steps

# for i in range(0, num_steps):
#     if dy > dx:
#         x_ratio = ((100*dx)/(100*dy))
#         y_ratio = 1
#         print(dx, dy, 10 * x_ratio)
#     else:
#         x_ratio = 1
#         y_ratio = ((100*dy)/(100*dx))
#         print(dx, dy, 10 * y_ratio)
#     x_mtr.move_angle(360 * (dx), spd = 10 * x_ratio, block=False)
#     y_mtr.move_angle(360 * (dy), spd = 10 * y_ratio, block=True)

#     dx -= step
#     dy += step

# dx = 0.0
# dy = 0.05
# num_steps = 20

# step = abs(dx - dy) / num_steps

# for i in range(0, 20):
#     if dy > dx:
#         x_ratio = ((100*dx)/(100*dy))
#         y_ratio = 1
#         print(dx, dy, 10 * x_ratio)
#     else:
#         x_ratio = 1
#         y_ratio = ((100*dy)/(100*dx))
#         print(dx, dy, 10 * y_ratio)
#     x_mtr.move_angle(-360 * (dx), spd = 10 * x_ratio, block=False)
#     y_mtr.move_angle(360 * (dy), spd = 10 * y_ratio, block=True)

#     dx += step
#     dy -= step

# y_mtr.move_angle(-360*0.5)
# x_mtr.position = 0; y_mtr.position = 0
# swan = SWAN(x_mtr, y_mtr, z_mtr)
# try:
#     swan.write_str("EAT\nIT")
#     # swan.F()
#     # swan.next_letter()
#     # swan.A()
#     # swan.next_line()
#     # swan.E()
#     # swan.F()
#     # swan.I()
# except AssertionError:
#     pass
# except Exception as e:
#     traceback.print_exc()
# finally:
#     print(x_mtr.position, y_mtr.position)
#     input("Click Enter to reset")
#     x_mtr.reset()
#     y_mtr.reset()
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

# SQUARE
# x_mtr.move_angle(-360 * 1)
# y_mtr.move_angle(360 * 1)
# x_mtr.move_angle(360 * 1)
# y_mtr.move_angle(-360 * 1)

def main():
    x_mtr.position = 0; y_mtr.position = 0
    swan = SWAN(x_mtr, y_mtr, z_mtr)
    try:
        swan.write_str("N")
        # swan.F()
        # swan.next_letter()
        # swan.A()
        # swan.next_line()
        # swan.E()
        # swan.F()
        # swan.I()
    except AssertionError:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        print(x_mtr.position, y_mtr.position)
        input("Click Enter to reset")
        x_mtr.reset()
        y_mtr.reset()
    y_mtr.STOP_ACTION_HOLD = "brake"
    x_mtr.STOP_ACTION_HOLD = "brake"

main()

