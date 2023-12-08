# def quarter_ellipse(self, ratio, quadrant):
#     # We always move anticlockwise

#     init_pos = [self.x_mtr.position, self.y_mtr.position]

#     self.pen_down()
#     time.sleep(0.5)
#     try:
#         assert quadrant >= 1 and quadrant <= 4
#     except AssertionError:
#         print("Make sure you enter a valid quadrant")

#     self.x_mtr.STOP_ACTION_HOLD = 'hold'
#     self.y_mtr.STOP_ACTION_HOLD = 'hold'
    
#     num_steps = 3
#     dx = 2/(num_steps+1) * abs(ratio[0])
#     dy = 0.0
#     if quadrant % 2 == 1:
#         dx = 0.0
#         dy = 2/(num_steps+1) * abs(ratio[1])

#     x_sign, y_sign = -1, 1
#     if quadrant == 2:
#         y_sign = -y_sign
#     elif quadrant == 3:
#         x_sign, y_sign = y_sign, x_sign
#     elif quadrant == 4:
#         x_sign = -x_sign
        
#     step = 2 / ((num_steps)*(num_steps+1)) #(abs(dx - dy)) / num_steps

#     for i in range(0, num_steps+1):
#         # if i == num_steps:
#         #     self.x_mtr.STOP_ACTION_HOLD = 'brake'
#         #     self.y_mtr.STOP_ACTION_HOLD = 'brake'

#         if dy > dx:
#             #x_ratio = ((abs(ratio[0]) * dx)/(abs(ratio[1]) * dy))
#             x_ratio = dx/dy
#             y_ratio = 1
#             print(360*dx, 360*dy, 20 * x_ratio)
#         else:
#             x_ratio = 1
#             y_ratio = dy/dx
#             #y_ratio = (abs(ratio[1]) * dy)/(abs(ratio[0]) * dx)
#             print(360*dx, 360*dy, 20 * y_ratio)
        
#         self.x_mtr.move_angle(x_sign * 360 * (dx), spd = 20 * x_ratio, block=False)
#         self.y_mtr.move_angle(y_sign * 360 * (dy), spd = 20 * y_ratio, block=True)
        
#         if quadrant % 2 == 0:
#             dx -= step * abs(ratio[0])
#             dy += step * abs(ratio[1])
#         else:
#             dx += step * abs(ratio[0])
#             dy -= step * abs(ratio[1])
#         time.sleep(0.25)
    
#     print("quarter_ellipse", quadrant, self.x_mtr.position - init_pos[0], self.y_mtr.position - init_pos[1])
#     self.relative_pos[0] += x_sign * ratio[0]
#     self.relative_pos[1] += y_sign * ratio[1]
#     self.x_mtr.STOP_ACTION_HOLD = 'brake'
#     self.y_mtr.STOP_ACTION_HOLD = 'brake'
#     time.sleep(0.5)