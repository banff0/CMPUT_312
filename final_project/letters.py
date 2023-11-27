## Positive x is right
## Negative y is up
## 360 degrees is ~1.9 cm
default_angle = 360
default_speed = 10
default_ratio = (1, -1)  # Ratio of x-distance to y-distance

def A(x_mtr, y_mtr):
    # x_mtr.move_angle(360, block=False)
    # y_mtr.move_angle(2*-360, spd=20, block=True)
    # x_mtr.move_angle(360, block=False)
    # y_mtr.move_angle(2*360, spd=20, block=True)
    ################################
    # Draw the 2 main diagonals
    diagonal(x_mtr, y_mtr, (1, 2))
    diagonal(x_mtr, y_mtr, (1, -2))
    # Go back up half the most recent diagonal
    diagonal(x_mtr, y_mtr, (-1, 1))
    # Draw the line in between the diagonals, parallel to x-axis
    horizontal(x_mtr, -1)

def sign(num):
    # Returns the sign of a number
    if num == 0:
        return 0
    elif num > 0:
        return 1
    else:
        return -1    

def horizontal(x_mtr, x_ratio = 1):
    x_mtr.move_angle(x_ratio * default_angle, default_speed, block = True)

def diagonal(x_mtr, y_mtr, ratio = default_ratio):
    x_mtr.move_angle(ratio[0] * default_angle, abs(ratio[0]) * default_speed, block=False)
    y_mtr.move_angle(ratio[1] * default_angle, abs(ratio[1]) * default_speed, block=True)
