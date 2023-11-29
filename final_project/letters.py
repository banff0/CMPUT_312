import time
from string import ascii_uppercase

class SWAN:
    ALLOWED_LETTERS = ascii_uppercase

    ## Positive x is right
    ## Positive y: (tray moves down, pen draws up)
    ## 360 degrees is ~1.9 cm
    default_angle = 360
    default_speed = 10
    default_ratio = (1, -1)  # Ratio of x-distance to y-distance

    relative_pos = [0, 0]

    def __init__(self, x_mtr, y_mtr, z_mtr, max_letters_per_line = 5):
        self.x_mtr = x_mtr
        self.y_mtr = y_mtr
        self.z_mtr = z_mtr
        self.pen_pos_up = True
        self.max_letters_per_line = max_letters_per_line
        self.line_letters = 0

        #self.str_to_letter = {'a': self.A, 'e': self.E, "i": self.I, "t": self.T, "f": self.F, " ": self.space, "\n": self.next_line, "n": self.N}
        self.str_to_letter = {' ': self.space, '\n': self.next_line}
        for letter in self.ALLOWED_LETTERS:
            # If function to draw this character has been implemented, add it to self.str_to_letter
            if hasattr(self, letter):
                self.str_to_letter[letter] = eval(f'self.{letter}')

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

    # move and draw with pen down
    def draw_horizontal(self, x_ratio = default_ratio[0]):
        self.pen_down()
        self.horizontal(x_ratio)
    #move without drawing, with pen up
    def move_horizontal(self, x_ratio = default_ratio[0]):
        self.pen_up()
        self.horizontal(x_ratio)
    
    # move and draw with pen down
    def draw_vertical(self, y_ratio = default_ratio[1]):
        self.pen_down()
        self.vertical(y_ratio)
    #move without drawing, with pen up
    def move_vertical(self, y_ratio = default_ratio[1]):
        self.pen_up()
        self.vertical(y_ratio)
    
    # move and draw with pen down
    def draw_diagonal(self, ratio = default_ratio):
        self.pen_down()
        self.diagonal(ratio)
    #move without drawing, with pen up
    def move_diagonal(self, ratio = default_ratio):
        self.pen_up()
        self.diagonal(ratio)

    def pen_up(self):
        if not self.pen_pos_up:
            self.z_mtr.move_angle(-20, spd=5)
            self.pen_pos_up = True
    
    def pen_down(self):
        if self.pen_pos_up:
            self.z_mtr.move_angle(20, spd=5)
            self.pen_pos_up = False

    def next_letter(self):
        self.pen_up()
        self.horizontal(1.25)
        self.relative_pos == [0, 0]
        self.line_letters += 1.25
    
    def next_line(self):
        self.pen_up()
        self.diagonal([-self.line_letters , -2.25])
        self.relative_pos == [0, 0]
        self.line_letters = 0
    
    def space(self):
        self.pen_up()


    def write_str(self, str):
        print(str)
        for i in str.upper():
            ## I changed this to upper. See creation of self.str_to_letter above.
            print(i)
            self.str_to_letter[i]()
            #### Need to make sure we have not reached the end of the page
            if i != "\n":
                self.next_letter()


    def assert_reset(self):
        try:
            assert self.relative_pos == [0, 0]
        except AssertionError:
            print("Make sure you get back to starting position!")

    # Start drawing from bottom left corner

    def A(self):
        # Draw the 2 main diagonals
        # self.pen_down()
        self.draw_diagonal((0.5, 2))
        self.draw_diagonal((0.5, -2))
        # Go back up half the most recent diagonal
        # self.pen_up()
        self.move_diagonal((-0.25, 1))
        # Draw the line in between the diagonals, parallel to x-axis
        # self.pen_down()
        self.draw_horizontal(-0.5)

        # Get back to starting pos
        # self.pen_up()
        self.move_diagonal((-0.25, -1))
        self.assert_reset()

    def E(self):
        # self.pen_down()
        self.draw_horizontal(1)
        # self.pen_up()
        self.move_horizontal(-1)
        self.F()  # F takes care of asserting that we're back at starting position

    def F(self):
        for i in range(2):
            # self.pen_down()
            self.draw_vertical(1)
            self.draw_horizontal(0.5 + 0.5 * i)
            # self.pen_up()
            self.move_horizontal(-(0.5 + 0.5 * i))
        # Get back to starting pos
        # self.pen_up()
        self.move_vertical(-2)
        self.assert_reset()

    def H(self):
        ## UNTESTED
        # Draw 2 sides of H
        self.draw_vertical(2)
        self.move_horizontal(1)
        self.draw_vertical(-2)
        # Draw the line in between
        self.move_vertical(1)
        self.draw_horizontal(-1)

        self.move_vertical(-1)
        self.assert_reset()

    def I(self):
        # self.pen_down()
        self.draw_horizontal(1)
        # self.pen_up()
        self.move_horizontal(-0.5)
        # self.pen_down()
        self.draw_vertical(2)
        # self.pen_up()
        self.move_horizontal(0.5)
        # self.pen_down()
        self.draw_horizontal(-1)

        # Get back to starting pos
        # self.pen_down()
        self.move_vertical(-2)
        self.assert_reset()

    def K(self):
        ## UNTESTED
        self.draw_vertical(2)
        self.move_vertical(-1)

        self.draw_diagonal((1, 1))
        self.move_diagonal((-1, -1))
        self.draw_diagonal((1, -1))

        self.move_horizontal(-1)
        self.assert_reset()

    def L(self):
        ## UNTESTED
        self.draw_vertical(2)
        self.move_vertical(-2)
        self.draw_horizontal(1)

        self.move_horizontal(-1)
        self.assert_reset()
    
    def M(self):
        ## UNTESTED
        self.draw_vertical(2)
        self.draw_diagonal((0.5, -1))
        self.draw_diagonal((0.5, 1))
        self.draw_vertical(-2)

        self.move_horizontal(-1)
        self.assert_reset()

    def N(self):
        ## UNTESTED
        self.draw_vertical(2)
        self.draw_diagonal([1, -2])
        self.draw_vertical(2)

        self.move_diagonal([-1, -2])
        self.assert_reset()
    
    def T(self):
        # go to middle of T
        self.move_horizontal(0.5)
        # draw vertical line up
        self.draw_vertical(2)
        # go to start of horizontal line
        self.move_horizontal(0.5)
        # draw top line
        self.draw_horizontal(-1)
        # go back to start
        self.move_vertical(-2)

        self.assert_reset()

    def V(self):
        ## UNTESTED
        self.move_vertical(2)
        self.draw_diagonal((0.5, -2))
        self.draw_diagonal((0.5, 2))

        self.move_diagonal((-1, -2))
        self.assert_reset()

    def W(self):
        ## UNTESTED
        self.move_vertical(2)
        self.draw_vertical(-2)
        self.draw_diagonal((0.5, 1))
        self.draw_diagonal((0.5, -1))
        self.draw_vertical(2)

        self.move_diagonal((-1, -2))
        self.assert_reset()
    
    def X(self):
        ## UNTESTED
        self.draw_diagonal((1, 2))
        self.move_horizontal(-1)
        self.draw_diagonal((1, -2))

        self.move_horizontal(-1)
        self.assert_reset()
    
    def Y(self):
        ## UNTESTED
        self.move_horizontal(0.5)
        self.draw_vertical(1)
        self.draw_diagonal((0.5, 1))
        self.move_horizontal(-1)
        self.draw_diagonal((0.5, -1))

        self.move_diagonal((-0.5, -1))
        self.assert_reset()
    
    def Z(self):
        ## UNTESTED
        self.move_vertical(2)
        self.draw_horizontal(2)
        self.draw_diagonal((-1, -2))
        self.draw_horizontal(2)
        
        self.move_horizontal(-2)
        self.assert_reset()
