from controllers.pid import PID
from robot.robot_interface import RobotInterface
import time
import robot_config
from naoqi import ALProxy

class Race:

    def __init__(
        self,
        robot,
        distance_x=3,
        distance_y=0.0,
    ):  
        self.robot = robot
        self.distance_x = distance_x
        self.distance_y = distance_y

        self.robot.start_moving()

    def run(self):
        self.robot.motion.wakeUp()
        self.robot.posture.goToPosture("StandInit", 0.5)
        
        mem = ALProxy("ALMemory", robot_config.IP_ADDRESS, robot_config.PORT)

        intial_yaw = mem.getData("Device/SubDeviceList/InertialSensor/AngleZ/Sensor/Value")
        start_time =  time.time()
        while time.time() - start_time < 5 and not self.robot.mem.getData("Device/SubDeviceList/ChestBoard/Button/Sensor/Value"):
            print(time.time() - start_time)
            yaw = mem.getData("Device/SubDeviceList/InertialSensor/AngleZ/Sensor/Value") - intial_yaw
            print("El yaw es: " + str(yaw))
            theta_error = 0 - yaw

            print("iniciando carrera")
            self.robot.move_toward(1, -0.8, theta_error * -0.5)


        
            