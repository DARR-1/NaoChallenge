from controllers.pid import PID
from robot.robot_interface import RobotInterface
import time
import math


class WalkToBall:

    def __init__(
        self,
        robot
    ):  

        self.robot = robot
        self.distance_x = 0.5
        self.distance_y = 0.5
        self.robot.start_moving()

    def run(self, use_predefined_pos = False, side = "left"):
        self.robot.motion.wakeUp()
        self.robot.posture.goToPosture("StandInit", 0.5)


        x_pos = 0
        y_pos = 0
        theta_pos = 0

        succesful_measures = 0
        while succesful_measures < 20 and not use_predefined_pos and not self.robot.mem.getData("Device/SubDeviceList/ChestBoard/Button/Sensor/Value"):
            

            tag = self.robot.get_ball_distances()


            if tag != None:
                x = tag[0]
                y = tag[1]
                z = tag[2]

                self.robot.aim(
                    x,
                    y,
                    z
                )

                # distance control
                x_pos += x - self.distance_x
                y_pos += y - self.distance_y

                succesful_measures += 1

        if use_predefined_pos:
            if side == "left":
                x_pos = 0.125
                y_pos = 0
                theta_pos = math.radians(0)
            if side == "right":
                x_pos = 0.125
                y_pos = 0
                theta_pos = math.radians(0)

        self.robot.move(x_pos, y_pos, theta_pos)

        
            