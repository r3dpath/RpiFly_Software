# For better model, maybe consider implementing AHRS library
import math

class Attitude:
    def __init__(self, gx_init=0, gy_init=0, gz_init=0):
        #Initialises the attitude to zero, setting initial values for angle
        self.x, self.y, self.z = 0, 0, 0
        self.x_dot, self.y_dot, self.v_dot = 0, 0, 0
        self.ax, self.ay, self.az = 0, 0, 0

        self.theta_x, self.theta_y, self.theta_z = gx_init, gy_init, gz_init
        self.theta_x_dot, self.theta_y_dot, self.theta_z_dot = 0, 0, 0
        self.theta_x_ddot, self.theta_y_ddot, self.theta_z_ddot = 0, 0, 0

    def complimentary(self, ax, ay, az, gx, gy, gz):

    def accel_angle(self, ax, ay, az):
        radToDeg = 180 / math.pi
        ax_angle = math.atan


