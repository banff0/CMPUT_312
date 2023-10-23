from queue import Queue
from server import Server
import numpy as np
import color_tracking
import time

def init_host():
    host = "169.254.79.135"
    port = 9999
    server = Server(host, port)
    queue = Queue()
    return server, queue

def get_J(dp, dt):
    # dp : change in x, y 
    J = np.array([dp[0, :] / dt[0], 
                  dp[1, :] / dt[1]])
    return J

def update_J(J, dp, dt):
    alpha = 0.1
    print(J.shape, dt.shape, dp.shape)
    print((dp - np.matmul(J, dt)))
    print(np.outer(((dp - np.matmul(J, dt)) / np.matmul(dt.T, dt)), dt))
    J = J + alpha * np.outer(((dp - np.matmul(J, dt)) / np.matmul(dt.T, dt)), dt)
    print(J.shape)
    return J


def estimate_jacobian(server, queue, tracker):
    # We move the base motor by 10 degrees, record the initial and final points,
    # and do the same for the second motor. The reset part is done in initial_jacobian() in client.py
    ### Reset done in initial_jacobian() in client.py. The reason is that since we assume we do not
    ### know the motor angles, I can't just send 
    theta = 10

    print(tracker.point)
    u0, v0, _ = tracker.point[0]
    # Theta 1
    server.sendAngles(theta, 0, queue)
    time.sleep(1)
    u1, v1, _ = tracker.point[0]
    server.sendAngles(-theta, 0, queue)

    # Theta 2
    server.sendAngles(0, theta, queue)
    time.sleep(1)
    u2, v2, _ = tracker.point[0]
    server.sendAngles(0, -theta, queue)

    jacobian = np.array([[(u1-u0)/theta, (u2-u0)/theta], 
                         [(v1-v0)/theta, (v2-v0)/theta]])
    
    

    return jacobian

def broyden():
    server, queue = init_host()
    tracker = color_tracking.Tracker('b', 'r')
    # Assuming we already have the initial jacobian

    lambda_ = 0.01
    alpha = 0.5

    # The goal and end effector positions, respectively, in pixel coordinates
    point = (0, 0, 0)
    goal = (0, 0, 0)
    delta_angles = np.array([0,0])
    theta = np.array([0,0])
    while np.all(point == (0, 0, 0)) or np.all(goal == (0, 0, 0)):
        goal = np.array(tracker.goal[0])
        point = np.array(tracker.point[0])
    
    goal = goal[:-1]
    point = point[:-1]
    
    print(point.shape)

    # The error vector. It is the vector from the point to the goal
    error = goal - point
    threshold = 20   # in pixels
    
    jacobian = estimate_jacobian(server, queue, tracker)
    print("INIT JACOBIAN", jacobian)
    idx = 0
    while np.linalg.norm(error) > threshold:
        point = np.array(tracker.point[0])[:-1]
        print(point)
        error = goal - point
        ptheta = theta
        theta = ptheta - lambda_ * np.matmul(np.linalg.pinv(jacobian), error)

        server.sendAngles(theta[0], theta[1], queue)
        if idx % 5 == 0:
            dtheta = ptheta - theta
            jacobian = jacobian + alpha * np.outer(((error - np.matmul(jacobian, dtheta)) / np.dot(dtheta, dtheta)), dtheta)
            print("NEW JACOBIAN", jacobian)
        idx += 1
        time.sleep(1)

    print(np.linalg.norm(error))

dt = np.array([10, 10])
dp = np.array([[20, 50],
               [10, 90]])

print(get_J(dp, dt))

# move_to_goal()
broyden()

print("DONE")
