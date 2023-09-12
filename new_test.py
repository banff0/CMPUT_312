#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, SpeedPercent, MoveTank

mtr_b = LargeMotor(OUTPUT_B)
mtr_d = LargeMotor(OUTPUT_D)
drive = MoveTank(OUTPUT_B, OUTPUT_D)

# mtr_b.on_for_rotations(SpeedPercent(75), 5)
# mtr_d.on_for_rotations(SpeedPercent(75), 5)

drive.on_for_rotations(-50, 50, 20)
drive.on_for_rotations(-100, -100, 5)

