import time


class SWAN:
    ## Positive x is right
    ## Positive y: (tray moves down, pen draws up)
    ## 360 degrees is ~1.9 cm
    default_angle = 360
    default_speed = 10
    default_ratio = (1, -1)  # Ratio of x-distance to y-distance

    relative_pos = [0, 0]

    def __init__(self, x_mtr, y_mtr):
        self.x_mtr = x_mtr
        self.y_mtr = y_mtr

    def horizontal(self, x_ratio = default_ratio[0]):
        self.x_mtr.move_angle(x_ratio * self.default_angle, self.default_speed, block = True)
        self.relative_pos[0] += x_ratio
        time.sleep(0.5)

    def vertical(self, y_ratio = default_ratio[1]):
        self.y_mtr.move_angle(y_ratio * self.default_angle, self.default_speed, block = True)
        self.relative_pos[1] += y_ratio
        time.sleep(0.5)

    def diagonal(self, ratio = default_ratio):
        self.x_mtr.move_angle(ratio[0] * self.default_angle, abs(ratio[0]) * self.default_speed, block=False)
        self.y_mtr.move_angle(ratio[1] * self.default_angle, abs(ratio[1]) * self.default_speed, block=True)
        self.relative_pos[0] += ratio[0]
        self.relative_pos[1] += ratio[1]
        time.sleep(0.5)


    def assert_reset(self):
        try:
            assert self.relative_pos == [0, 0]
        except AssertionError:
            print("Make sure you get back to starting position!")

    # Start drawing from bottom left corner

    def A(self):
        # self.x_mtr.move_angle(360, block=False)
        # self.y_mtr.move_angle(2*-360, spd=20, block=True)
        # self.x_mtr.move_angle(360, block=False)
        # self.y_mtr.move_angle(2*360, spd=20, block=True)
        ################################
        # Draw the 2 main diagonals
        self.diagonal((0.5, 2))
        self.diagonal((0.5, -2))
        # Go back up half the most recent diagonal
        self.diagonal((-0.25, 1))
        # Draw the line in between the diagonals, parallel to x-axis
        self.horizontal(-0.5)

        # Get back to starting pos
        self.diagonal((-0.25, -1))
        self.assert_reset()
        

    def E(self):
        self.horizontal(1)
        self.horizontal(-1)
        self.F()  # F takes care of asserting that we're back at starting position

    def F(self):
        for _ in range(2):
            self.vertical(1)
            self.horizontal(1)
            self.horizontal(-1)
        # Get back to starting pos
        self.vertical(-2)
        self.assert_reset()

    def I(self):
        self.horizontal(1)
        self.horizontal(-0.5)
        self.vertical(2)
        self.horizontal(0.5)
        self.horizontal(-1)

        # Get back to starting pos
        self.horizontal(0.5)
        self.vertical(-2)
        self.horizontal(-0.5)
        self.assert_reset()