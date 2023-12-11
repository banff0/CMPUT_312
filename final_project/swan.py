import time
from string import ascii_uppercase
from math import sin, cos, pi, floor

class SWAN:
    ALLOWED_LETTERS = ascii_uppercase

    ## Positive x is right
    ## Positive y: (tray moves down, pen draws up)
    ## 360 degrees is ~1.9 cm
    default_speed = 10
    default_ratio = (1, 1)  # Ratio of x-distance to y-distance
    default_x_unit = 1  # How wide a letter is in terms of (default_angle)*font_size
    default_y_unit = 2

    # This was an appropriate maximum font size, where font size 1 was legible
    # while the maximum font size allowed a fair amount of letters per line to
    # be written
    max_font_size = 5

    relative_pos = [0, 0]

    def __init__(self, x_mtr, y_mtr, z_mtr, font):
        try:
            assert font > 0 and font <= self.max_font_size
        except:
            print("Please enter a valid font in the range [1, 5]")
        self.x_mtr = x_mtr
        self.y_mtr = y_mtr
        self.z_mtr = z_mtr
        self.pen_pos_up = False
        self.down_dist = 20  # The angle by which to move the z-motor by for pen-up and pen-down 
        self.max_letters_per_line = floor(14 / (1.9*1.25*font/5))
        self.max_lines_per_page = floor(25 / (1.7*2.25*font/5))
        self.line_letters = 0
        # max_font_size corresponds to 1 full rotation of either motors
        self.default_angle = (font+1) * 360 / (self.max_font_size + 1)

        self.str_to_letter = {' ': self.space, '\n': self.next_line}
        for letter in self.ALLOWED_LETTERS:
            # If function to draw this character has been implemented, add it to self.str_to_letter
            if hasattr(self, letter):
                self.str_to_letter[letter] = eval("self.{}".format(letter))
        self.pen_up()

    def horizontal(self, x_units = default_ratio[0]):
        self.x_mtr.move_angle(x_units * self.default_angle, self.default_speed, block = True)
        self.relative_pos[0] += x_units
        time.sleep(0.5)

    def vertical(self, y_units = default_ratio[1]):
        # Move y motor by y_ratio units
        self.y_mtr.move_angle(y_units * self.default_angle, self.default_speed, block = True)
        self.relative_pos[1] += y_units
        time.sleep(0.5)

    def diagonal(self, units = default_ratio):
        # Move x and y motors at the same time, adjusting speed so that they stop at the same time
        # units here is a 2-item list containing the units to move in the x and y directions
        self.x_mtr.move_angle(units[0] * self.default_angle, abs(units[0]) * self.default_speed, block=False)
        self.y_mtr.move_angle(units[1] * self.default_angle, abs(units[1]) * self.default_speed, block=True)
        self.relative_pos[0] += units[0]
        self.relative_pos[1] += units[1]
        time.sleep(0.5)

    def quarter_ellipse(self, units, rotation = 'ccw'):
        # units here is a 2-item list containing the units to move in the x and y directions
        try:
            # Make sure a valid rotational direction was entered
            rotation = rotation.lower()
            assert len(rotation) > 0 and rotation in ['cw', 'ccw']
        except:
            print("Make sure you enter a correct rotational direction (cw, ccw)")
        self.x_mtr.stop_action_hold = 'coast'
        self.y_mtr.stop_action_hold = 'coast'
        self.pen_down()

        # Minimum of 2 steps to avoid division by zero
        # Here, num_steps signifies the number of angles between 0 and pi/2 inclusive. If we use
        # 1 step, then our only angle is 0 and we can never get to pi/2, hence the minimum is 2 steps.
        num_steps = 20
        theta_step = pi / (2*(num_steps-1))

        # This block decides which of the x and y motors will interpolate sin and cos. This
        # is what decides the direction of movement and which quadrant the curve will be in
        x_func, y_func = cos, sin
        if rotation == 'cw':
            x_func, y_func = sin, cos
        if (abs(units[0]) / units[0]) != (abs(units[1]) / units[1]):
            x_func, y_func = y_func, x_func

        x_steps = [x_func(step*theta_step) for step in range(num_steps)]
        y_steps = [y_func(step*theta_step) for step in range(num_steps)]
        
        for i in range(num_steps):
            self.x_mtr.move_angle(units[0] * theta_step * x_steps[i] * self.default_angle, abs(units[0]) * x_steps[i] * self.default_speed * 3, block=False)
            self.y_mtr.move_angle(units[1] * theta_step * y_steps[i] * self.default_angle, abs(units[1]) * y_steps[i] * self.default_speed * 3, block=True)
        
        self.x_mtr.stop_action_hold = 'brake'
        self.y_mtr.stop_action_hold = 'brake'
        self.relative_pos[0] += units[0]
        self.relative_pos[1] += units[1]
        time.sleep(0.5)
    
    # NOTE: abs_units in this functions are only for distance, they do not include rotational direction,
    # as for a semi ellipse, we move in opposite directions on an axis during different halves of the semi
    # ellipse
    def semi_ellipse(self, direction, ratio, rotation='ccw'):
        try:
            # Make sure a valid direction was entered
            direction = direction.lower()
            assert len(direction) > 0 and direction[0] in 'uldr'
        except:
            print("Make sure you enter a correct direction (uldr)")
        try:
            # Make sure a valid rotational direction was entered
            rotation = rotation.lower()
            assert len(rotation) > 0 and rotation in ['cw', 'ccw']
        except:
            print("Make sure you enter a correct rotational direction (cw, ccw)")
    
        ratio = [abs(ratio[0]), abs(ratio[1])]

        if direction[0] == 'u':
            ratio[0] /= 2
            if rotation == 'ccw':
                self.quarter_ellipse([ratio[0], -ratio[1]])
                self.quarter_ellipse([ratio[0], ratio[1]])
            else:
                self.quarter_ellipse([-ratio[0], -ratio[1]], rotation)
                self.quarter_ellipse([-ratio[0], ratio[1]], rotation)
        elif direction[0] == 'l':
            ratio[1] /= 2
            if rotation == 'ccw':
                self.quarter_ellipse([ratio[0], ratio[1]])
                self.quarter_ellipse([-ratio[0], ratio[1]])
            else:
                self.quarter_ellipse([ratio[0], -ratio[1]], rotation)
                self.quarter_ellipse([-ratio[0], -ratio[1]], rotation)
        elif direction[0] == 'd':
            ratio[0] /= 2
            if rotation == 'ccw':
                self.quarter_ellipse([-ratio[0], ratio[1]])
                self.draw_horizontal(0.2)
                self.quarter_ellipse([-ratio[0], -ratio[1]])
            else:
                self.quarter_ellipse([ratio[0], ratio[1]], rotation)
                self.quarter_ellipse([ratio[0], -ratio[1]], rotation)
        else:
            # Right
            ratio[1] /= 2 
            if rotation == 'ccw':
                self.quarter_ellipse([-ratio[0], -ratio[1]])
                self.quarter_ellipse([ratio[0], -ratio[1]])
            else:
                self.quarter_ellipse([-ratio[0], ratio[1]], rotation)
                self.quarter_ellipse([ratio[0], ratio[1]], rotation)

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
            self.z_mtr.move_angle(-(self.down_dist - 0.5), spd=5)
            self.pen_pos_up = True
    
    def pen_down(self):
        if self.pen_pos_up:
            self.z_mtr.move_angle(self.down_dist, spd=10)
            self.z_mtr.move_angle(-0.5, spd=5)
            self.pen_pos_up = False

    def next_letter(self):
        self.pen_up()
        self.horizontal(1.25)
        self.relative_pos = [0, 0]
        self.line_letters += 1.25
    
    def next_line(self):
        self.pen_up()
        self.diagonal([-self.line_letters, -2.25])
        self.relative_pos = [0, 0]
        self.line_letters = 0
    
    def space(self):
        self.pen_up()

    def write_str(self, str):
        print("Writing \"{}\"...".format(str.upper()))
        letters_per_line = 0
        lines_written = 0
        for char in str.upper():
            if lines_written == self.max_lines_per_page:
                print("Reached end of page! Exiting...")
                break
            
            init_pos = [self.x_mtr.position, self.y_mtr.position]
            self.str_to_letter[char]()
            
            if char != "\n":
                # Make sure we are back at the starting position for this letter.
                # This is to minimize accumulation of error
                self.correct_position(init_pos)
                self.next_letter()
                letters_per_line += 1
            else:
                letters_per_line = 0
                lines_written += 1
            
            if letters_per_line == self.max_letters_per_line:
                self.next_line()
                letters_per_line = 0
                lines_written += 1

    def assert_reset(self):
        try:
            assert self.relative_pos == [0, 0]
        except AssertionError:
            print("Make sure you get back to starting position!")
    
    def get_pos(self):
        return [self.x_mtr.position, self.y_mtr.position]
    
    def correct_position(self, init_pos):
        pos_diff = [init_pos[0] - self.x_mtr.position, init_pos[1] - self.y_mtr.position]
        assert pos_diff[0] < 50 and pos_diff[1] < 50
        
        rx, ry = 1, 1
        if pos_diff[0] != 0 and pos_diff[1] != 0:
            if pos_diff[0] > pos_diff[1]:
                ry = pos_diff[1]/pos_diff[0]
            else:
                rx = pos_diff[0]/pos_diff[1]
        self.x_mtr.move_angle(pos_diff[0], spd = min(abs(rx * self.default_speed), 100), block=False)
        self.y_mtr.move_angle(pos_diff[1], spd = min(abs(ry * self.default_speed), 100), block=True)


    # Start drawing from bottom left corner

    def A(self):
        # Draw the 2 main diagonals
        # self.pen_down()
        self.draw_diagonal((self.default_x_unit / 2, self.default_y_unit))
        self.draw_diagonal((self.default_x_unit / 2, -self.default_y_unit))
        # Go back up half the most recent diagonal
        # self.pen_up()
        self.move_diagonal((-self.default_x_unit / 4, self.default_y_unit / 2))
        # Draw the line in between the diagonals, parallel to x-axis
        # self.pen_down()
        self.draw_horizontal(-self.default_x_unit / 2)

        # Get back to starting pos
        # self.pen_up()
        self.move_diagonal((-self.default_x_unit / 4, -self.default_y_unit / 2))
        self.assert_reset()
    
    def B(self):
        init_pos = self.get_pos()
        for _ in range(2):
            self.semi_ellipse('l', [1, 1])
        self.draw_vertical(-2)
        self.correct_position(init_pos)
        
        self.assert_reset()

    def C(self):
        self.move_diagonal([0.8, 2])
        self.semi_ellipse('r', [1, 2])

        self.move_horizontal(-0.8)
        self.assert_reset()

    def D(self):
        self.semi_ellipse('l', [1, 2])
        self.draw_vertical(-2)

        self.assert_reset()

    def E(self):
        self.F()
        self.draw_horizontal(1)
        self.move_horizontal(-1)
        self.assert_reset()

    def F(self):
        self.move_diagonal([1, 2])
        self.draw_horizontal(-1)
        self.draw_vertical(-1)
        self.draw_horizontal(0.5)
        self.move_horizontal(-0.5)
        self.draw_vertical(-1)
        self.assert_reset()
    
    def G(self):
        self.C()
        self.move_horizontal(0.8)
        self.draw_vertical(1)
        self.draw_horizontal(-0.4)
        self.move_diagonal((-0.4, -1))
        self.assert_reset()

    def H(self):
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
        self.draw_horizontal(1)
        self.move_horizontal(-0.5)
        self.draw_vertical(2)
        self.move_horizontal(0.5)
        self.draw_horizontal(-1)

        # Get back to starting pos
        self.move_vertical(-2)
        self.assert_reset()
    
    def J(self):
        self.move_vertical(1)
        self.semi_ellipse('u', [0.5, 1])
        self.draw_vertical(1)
        self.move_horizontal(0.5)
        self.draw_horizontal(-1)

        self.move_vertical(-2)
        self.assert_reset()

    def K(self):
        self.draw_vertical(2)
        self.move_vertical(-1)

        self.draw_diagonal((1, 1))
        self.move_diagonal((-1, -1))
        self.draw_diagonal((1, -1))

        self.move_horizontal(-1)
        self.assert_reset()

    def L(self):
        self.draw_vertical(2)
        self.move_vertical(-2)
        self.draw_horizontal(1)

        self.move_horizontal(-1)
        self.assert_reset()
    
    def M(self):
        self.draw_vertical(2)
        self.draw_diagonal((0.5, -1))
        self.draw_diagonal((0.5, 1))
        self.draw_vertical(-2)

        self.move_horizontal(-1)
        self.assert_reset()

    def N(self):
        self.draw_vertical(2)
        self.draw_diagonal([1, -2])
        self.draw_vertical(2)

        self.move_diagonal([-1, -2])
        self.assert_reset()
    
    def O(self):
        self.move_horizontal(0.4)
        init_pos = self.get_pos()
        self.semi_ellipse('l', [0.5, 2])
        self.semi_ellipse('r', [0.5, 2])
        self.correct_position(init_pos)
        self.move_horizontal(-0.4)
        self.assert_reset()

    def P(self):
        init_pos = self.get_pos()
        self.draw_vertical(2)
        self.semi_ellipse('l', [1, 1.25], 'cw')
        self.move_vertical(-0.75)
        self.correct_position(init_pos)
        
        self.assert_reset()

    def Q(self):
        self.O()
        self.move_diagonal((0.4, 1))
        self.draw_diagonal((0.6, -1))

        self.move_horizontal(-1)
        self.assert_reset()

    def R(self):
        init_pos = self.get_pos()
        self.draw_vertical(2)
        self.semi_ellipse('l', [1, 1.25], 'cw')
        self.draw_diagonal((1, -0.75))
        
        self.move_horizontal(-1)
        self.correct_position(init_pos)
        self.assert_reset()
    
    def S(self):
        self.draw_horizontal(0.5)
        self.semi_ellipse('l', [0.5, 1])
        self.semi_ellipse('r', [0.5, 1], 'cw')
        self.draw_horizontal(0.5)

        self.move_diagonal((-1, -2))
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
    
    def U(self):
        self.move_vertical(2)
        self.draw_vertical(-1)
        self.semi_ellipse('u', [1, 1])
        self.draw_vertical(1)

        self.move_diagonal((-1, -2))
        self.assert_reset()

    def V(self):
        self.move_vertical(2)
        self.draw_diagonal((0.5, -2))
        self.draw_diagonal((0.5, 2))

        self.move_diagonal((-1, -2))
        self.assert_reset()

    def W(self):
        self.move_vertical(2)
        self.draw_vertical(-2)
        self.draw_diagonal((0.5, 1))
        self.draw_diagonal((0.5, -1))
        self.draw_vertical(2)

        self.move_diagonal((-1, -2))
        self.assert_reset()
    
    def X(self):
        self.draw_diagonal((1, 2))
        self.move_horizontal(-1)
        self.draw_diagonal((1, -2))

        self.move_horizontal(-1)
        self.assert_reset()
    
    def Y(self):
        self.move_horizontal(0.5)
        self.draw_vertical(1)
        self.draw_diagonal((0.5, 1))
        self.move_horizontal(-1)
        self.draw_diagonal((0.5, -1))

        self.move_diagonal((-0.5, -1))
        self.assert_reset()
    
    def Z(self):
        self.move_vertical(2)
        self.draw_horizontal(1)
        self.draw_diagonal((-1, -2))
        self.draw_horizontal(1)
        
        self.move_horizontal(-1)
        self.assert_reset()

        