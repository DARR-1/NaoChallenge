import time

class Goalie:

    def __init__(self, robot):

        self.robot = robot

        # Ganancias PID
        self.kp = 10
        self.ki = 0.1
        self.kd = 0.0

        self.integral = 1
        self.prev_error = 0.0

        self.robot.start_moving()

    def pid(self, error, dt):

        self.integral += error * dt

        derivative = 0.0
        if dt > 0:
            derivative = (error - self.prev_error) / dt

        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )

        self.prev_error = error

        # Saturacion entre -1 y 1
        output = max(-1.0, min(1.0, output))

        return output

    def run(self):

        self.robot.motion.wakeUp()
        self.robot.posture.goToPosture("StandInit", 0.5)

        last_time = time.time()

        while True and not self.robot.mem.getData("Device/SubDeviceList/ChestBoard/Button/Sensor/Value"):

            tag = self.robot.get_ball_distances()

            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            if tag is not None:

                x, y, z = tag

                self.robot.aim(x, y, z)

                # Error lateral
                error = y

                # PID normalizado [-1, 1]
                lateral_speed = self.pid(error, dt)

                # Camina solo lateralmente
                self.robot.move_toward(
                    0.0,            # avance
                    lateral_speed,  # izquierda/derecha
                    0.0             # giro
                )

                print("x = {:.3f}, y = {:.3f}, z = {:.3f}".format(x, y, z))

            else:
                self.robot.move_toward(0.0, 0.0, 0.0)
                print("No tag found")