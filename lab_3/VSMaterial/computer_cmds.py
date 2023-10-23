from queue import Queue
from server import Server
import numpy as np
import color_tracking
import time

def init_host():
    host = "192.168.0.2"
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
    J = J + alpha * ((dp - J * dt) / (dt.T * dt) * dt)
    return J

#TODO: implement get angle function on server
#TODO: tighten / test HSV values on actual camera
#TODO: check in what order we are returning points in coltracker if issues arise


def move_to_goal():
    server, queue = init_host()
    tracker = color_tracking.Tracker('b', 'g')
    dp = np.array([[1, 3],
                   [2, 4]])
    theta = np.array([0, 0])
    ptheta = np.array([0, 0])
    err = np.array([10000, 10000])
    J = None

    delta = 0.1
    update_rate = 5
    
    idx = 0
    while err[0] >= 5 and err[1] >= 5:
        if idx < 2:
            goal = tracker.goal
        end = tracker.point
        # wait for image to load
        if not np.all(end == (0, 0, 0)):
            end = end[0]
            err = goal - end
            # init J if first loop
            if np.all(J == None):
                dt = np.array([5, 5])
                # get the change in x and y for movement dt
                server.sendAngles(dt[0], dt[1], queue)
                dp[:, :] = (tracker.point[0] - end)[:-1]
                server.sendAngles(-dt[0], -dt[1], queue)
                # calculate J
                J = get_J(dp, dt)
            
            
            # calculate next moevment, and save change in theta
            ptheta = theta
            theta = theta + delta * (J.T * err)
            dt = theta - ptheta

            # move the arm, get the change in pixels
            server.sendAngles(*theta, queue)
            dp[:, :] = (tracker.point[0] - end)[:-1]

            if idx % update_rate == 0:
                J = update_J(J, dp, dt)
            idx += 1

            time.sleep(2)


dt = np.array([10, 10])
dp = np.array([[20, 50],
               [10, 90]])

print(get_J(dp, dt))

move_to_goal()

