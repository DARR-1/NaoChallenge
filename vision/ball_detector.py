from naoqi import ALProxy
import robot_config
import time

IP = robot_config.IP_ADDRESS
PORT = robot_config.PORT
class BallDetector:
    def __init__(self):
        self.tracker = ALProxy("ALTracker", IP, PORT)

        self.tracker.registerTarget("RedBall", 0.066845)  # El tamano real de la pelota en metros
        self.tracker.track("RedBall")

    def stop_tracking(self):
        self.tracker.stopTracker()
        self.tracker.unregisterAllTargets()

    def get_ball_position(self):
        pos = self.tracker.getTargetPosition(0)
        if pos:
            return (pos[0], pos[1], pos[2])
        else:
            return None

if __name__ == "__main__":
    ball_detector = BallDetector()
    while True:
        pos = ball_detector.tracker.getTargetPosition(0)

        if pos:
            print("x=%.3f y=%.3f z=%.3f" % (pos[0], pos[1], pos[2]))

        time.sleep(0.5)