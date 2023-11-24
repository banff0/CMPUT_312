# This file contains utility functions and classes used in Q1 and Q2 of the lab.
# The reason this file is included is because we want to isolate the Q1 and Q2 code
# from some of the functions we used to make them work.

from ev3dev2.motor import LargeMotor
from math import radians, cos, sin, sqrt, acos, atan2

# All length units are in cm, all angles are in degrees

l1, l2 = 11, 7

class ArmMotor(LargeMotor):
    def __init__(self, OUTPUT):
        super(ArmMotor, self).__init__(OUTPUT)
        self.STOP_ACTION_HOLD = "brake" # make it so that the motors can be moved by hand
        
    def move_angle(self, theta, spd=10, block=True):
        self.on_for_degrees(spd, theta, block=block)

    def reset(self):
        self.move_angle(-self.position) 
    
    def __str__(self) -> str:
        return str(self.position)
    
class Matrix:
    def __init__(self, matrix):
        self.matrix = matrix
        self.rows = len(matrix)
        self.columns = len(matrix[0])

    def __add__(self, other):
        assert self.rows == other.rows and self.columns == other.columns
        result = [[0 for j in range(self.columns)] for i in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.columns):
                result[row][col] = self.matrix[row][col] + other.matrix[row][col]
        return Matrix(result)
    
    def __sub__(self, other):
        assert self.rows == other.rows and self.columns == other.columns
        result = [[0 for j in range(len(self.matrix[0]))] for j in range(len(self.matrix))]
        for row in range(self.rows):
            for col in range(self.columns):
                result[row][col] = self.matrix[row][col] - other.matrix[row][col]
        return Matrix(result)
    
    def __neg__(self):
        return Matrix([[-element for element in row] for row in self.matrix])

    def __getitem__(self, row):
        return Vector(self.matrix[row])

    def __str__(self):
        return "\n".join([str(row) for row in self.matrix])
    
    def multiply_with_scalar(self, scalar):
        assert type(scalar) in [int, float]
        return Matrix([[scalar*element for element in row] for row in self.matrix])

    def multiply_with_vector(self, vector):
        assert self.columns == len(vector)
        assert type(vector) in [Vector, list, tuple]
        result = []
        for row in range(self.rows):
            result.append(0)
            for col in range(self.columns):
                result[-1] += self.matrix[row][col] * vector[col]
        
        # Result is n*1 dimensions
        return Vector(result)

class Vector:
    def __init__(self, vector):
        self.vector = vector
    
    def __len__(self):
        return len(self.vector)
    
    def __add__(self, other):
        assert len(self) == len(other)
        return Vector([self[i] + other[i] for i in range(len(self))])
    
    def __sub__(self, other):
        assert len(self) == len(other)
        return Vector([self[i] - other[i] for i in range(len(self))])
    
    def __neg__(self):
        return Vector([-element for element in self.vector])

    def __getitem__(self, index):
        return self.vector[index]
    
    def __str__(self):
        return str(self.vector)
    
    def norm(self):
        return sqrt(self[0]*self[0] + self[1]*self[1])
    
    def multiply_with_scalar(self, scalar):
        return Vector([scalar*element for element in self.vector])
    
    def dot_product(self, other):
        assert len(self) == len(other)
        return sum([self[i]*other[i] for i in range(len(self))])
    
    def outer_product(self, other):
        assert len(self) == len(other)
        return Matrix([[self[i]*other[j] for j in range(len(self))] for i in range(len(self))])
    

def calculate_coordinates(theta1, theta2):
    theta1, theta2 = radians(theta1), radians(theta2)
    x = l1*cos(theta1) + l2*cos(theta1+theta2)
    y = l1*sin(theta1) + l2*sin(theta1+theta2)
    return Vector([x, y])

def inverse_kin_analytical(x, y, init_theta2):
    init_theta2 = radians(init_theta2)
    theta2 = acos((x**2 + y**2 - l1**2 - l2**2) / (2*l1*l2))
    theta2_options = [theta2, -theta2]
    theta2 = theta2_options[0] if abs(theta2_options[0] - init_theta2) < abs(theta2_options[1] - init_theta2) else theta2_options[1]

    theta1 = atan2(y, x) - atan2(l2 * sin(theta2), l1 + l2 * cos(theta2))

    return Vector([theta1, theta2])
