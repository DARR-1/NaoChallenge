from naoqi import ALProxy
from robot.robot_interface import RobotInterface
from vision.camera import NaoCamera
from vision.ball_detector import BallDetector
import robot_config
import math


class NaoqiRobot(RobotInterface):

    def __init__(self, ip):
        self.motion = ALProxy(
            "ALMotion",
            ip,
            robot_config.PORT
        )

        self.posture = ALProxy(
            "ALRobotPosture",
            ip,
            robot_config.PORT
        )

        # Tracker es el que sabe "mirar a" un punto/target
        try:
            self.tracker = ALProxy("ALTracker", ip, robot_config.PORT)
        except Exception:
            self.tracker = None

        self.mem = ALProxy("ALMemory", ip, robot_config.PORT)

        self.camera = NaoCamera(ip)

        self.ball_detector = BallDetector()

    def move(self, x, y, theta):
        self.motion.moveTo(
            x,
            y,
            theta,
            [
                ["MaxStepX", 0.03],
                ["MaxStepY", 0.02],
                ["MaxStepTheta", 0.2],
                ["StepHeight", 0.015]
            ]
        )

    def move_toward(self, x, y, theta):
        self.motion.moveToward(
            x,
            y,
            theta,
            [
                ["MaxStepX", 0.08],
                ["MaxStepY", 0.1],
                ["MaxStepTheta", 0.2],
                ["StepHeight", 0.015]
            ]
        )
    
    def walk(self, x_vel, y_vel, theta_vel):

        # NAOqi expects normalized speeds in [-1, 1] and a step frequency in [0, 1].
        # Using velocity control is usually better for PID behaviors.
        self.motion.setWalkTargetVelocity(
            float(x_vel),
            float(y_vel),
            float(theta_vel),
            0.5,
        )

    def start_moving(self):
        self.motion.moveInit()

    
    def aim(self, x, y, z):
        """Apunta la cabeza hacia el punto (x,y,z).

        Intenta usar ALTracker.lookAt si esta disponible. Si no, cae a yaw/pitch.
        Importante: (x,y,z) deben ser coherentes con el frame usado.
        En NAOqi lookAt usa un sistema de referencia (frame) explicito.
        """
        x = float(x)
        y = float(y)
        z = float(z)

        # Asegurar rigidez para que se mueva la cabeza
        self.motion.setStiffnesses("Head", 1.0)

        if self.tracker is not None:
            # We use the repo convention x forward, y left, z up.
            # That matches NAOqi's robot frame convention (X forward, Y left, Z up).
            # Frame 2 suele ser FRAME_ROBOT en NAOqi.
            frame = 2
            speed = 0.2
            useWholeBody = False
            self.tracker.lookAt([x, y, z], frame, speed, useWholeBody)
            return

        # Fallback: calcular yaw/pitch usando la convencion del proyecto:
        #   x: adelante, y: izquierda, z: arriba
        # Geometria:
        #   yaw   = atan2(y, x)
        #   pitch = atan2(z, x)
        # (si el punto esta justo a x=0, evitamos division por cero)
        print("aim fallback: x={:.3f}, y={:.3f}, z={:.3f}".format(x, y, z))

        if abs(x) < 1e-6:
            x = 1e-6

        yaw = math.atan2(y, x)
        pitch = math.atan2(z, x)

        self.motion.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], 0.2)

    def stop(self):
        self.walk(0, 0, 0)
        self.motion.rest()

    def get_camera_image(self):
        return self.camera.get_image()
    
    def get_ball_distances(self):
        return self.ball_detector.get_ball_position()
    
    def has_red_ball(self):
        return self.get_ball_distances() is not None