import math
import time

class SearchForBall:
    def __init__(self, robot, alpha=0.0000):
        self.robot = robot
        self.alpha = alpha  # Velocidad del movimiento senoidal
        self.max_yaw = 1  # Rango maximo de yaw (izquierda a derecha)

    def run(self):
        start_time = time.time()
        
        self.robot.motion.wakeUp()
        self.robot.posture.goToPosture("StandInit", 0.5)

        while True:
            # Calcular tiempo transcurrido y generar movimiento senoidal
            elapsed_time = time.time() - start_time
            yaw = self.max_yaw * math.sin(self.alpha * elapsed_time)
            
            # Mover la cabeza de izquierda a derecha
            self.robot.motion.setAngles(["HeadYaw"], [yaw], 0.02)

            # Bajar el pitch lo maximo posible
            min_pitch = 0  # Minimo pitch en radianes (NAO)
            self.robot.motion.setAngles(["HeadPitch"], [min_pitch], 0.1)
            
            # Verificar si detecta la pelota
            if not self.robot.has_red_ball():
                continue
            else:
                ball_pos = self.robot.get_ball_distances()
                
                self.robot.aim(
                    ball_pos[0],
                    ball_pos[1],
                    ball_pos[2]
                )

                print("Ball position: x=%.3f y=%.3f z=%.3f" % (ball_pos[0], ball_pos[1], ball_pos[2]))
                return