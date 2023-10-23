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

#TODO: implement get angle function on server
#TODO: tighten / test HSV values on actual camera
#TODO: check in what order we are returning points in coltracker if issues arise


def move_to_goal():
    server, queue = init_host()
    tracker = color_tracking.Tracker('b', 'r')
    dp = np.array([[1, 3],
                   [2, 4]])
    theta = np.array([0, 0])
    ptheta = np.array([0, 0])
    err = np.array([10000, 10000])
    J = None

    lambda_ = 0.01
    update_rate = 5
    
    idx = 0
    while abs(err[0]) >= 5 and abs(err[1]) >= 5:
        if idx < 2:
            goal = tracker.goal
        end = tracker.point
        # wait for image to load
        if not np.all(end == (0, 0, 0)):
            end = end[0]
            err = goal - end
            err = err[0][:-1]
            print("err", err)
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
            print(theta)
            print(np.linalg.pinv(J).shape, err.shape)
            theta = theta - lambda_ * np.matmul(np.linalg.pinv(J), err)
            print(theta)
            dt = theta - ptheta

            # move the arm, get the change in pixels
            server.sendAngles(*theta, queue)
            print("err", (tracker.point[0] - end)[:-1])
            dp = np.array((tracker.point[0] - end)[:-1])

            if idx % update_rate == 0:
                J = update_J(J, dp, dt)
            idx += 1

            time.sleep(2)


dt = np.array([10, 10])
dp = np.array([[20, 50],
               [10, 90]])

print(get_J(dp, dt))

move_to_goal()

print("DONE")
