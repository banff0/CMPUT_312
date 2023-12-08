from ev3dev2.motor import LargeMotor

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT, invert=False, hold_action="brake"):
        super(ArmMotor, self).__init__(OUTPUT)
        self.position = 0
        self.STOP_ACTION_HOLD = hold_action
        if invert:
            self.POLARITY_INVERSED = "inversed"

    def move_angle(self, theta, spd=10, block=True):
        self.on_for_degrees(spd, theta, block = block)

    def reset(self):
        self.move_angle(-self.position) 
    
    def __str__(self) -> str:
        return str(self.position)