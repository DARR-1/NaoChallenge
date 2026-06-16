import robot_config
import time
import math
import motion

class Kick:
    def __init__(self, robot):
        self.robot = robot

    def run(self):

        proxy = self.robot.motion

        # Rigidez y postura inicial
        robot_config.StiffnessOn(proxy)
        robot_config.PoseInit(proxy)

        # Activar Whole Body Balancer
        proxy.wbEnable(True)

        # Ambos pies fijos
        proxy.wbFootState("Fixed", "Legs")

        # Restricciones de balance
        proxy.wbEnableBalanceConstraint(True, "Legs")

        # Transferir peso a la pierna izquierda
        proxy.wbGoToBalance("LLeg", 4.0)

        time.sleep(1.0)

        # Liberar pierna derecha
        proxy.wbFootState("Free", "RLeg")

        effectorName = "RLeg"
        space = motion.FRAME_TORSO
        axisMask = 63

        targetList = [
            [-0.03, 0.00, 0.02, 0.00, 0.05, 0.00],
            [ 0.05, 0.00, 0.01, 0.00, 0.00, 0.00],
            [ 0.00, 0.00, 0.01, 0.00, 0.00, 0.00],
            [ 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
        ]

        times = [1.0, 1.2, 1.6, 2.0]

        proxy.positionInterpolation(
            effectorName,
            space,
            targetList,
            axisMask,
            times,
            False
        )

        # Esperar estabilidad
        time.sleep(4)

        # Recuperar equilibrio
        proxy.wbGoToBalance("Legs", 1.5)

        # Fijar nuevamente ambos pies
        proxy.wbFootState("Fixed", "Legs")

        # Desactivar Whole Body
        proxy.wbEnable(False)

        # Volver a postura inicial
        robot_config.PoseInit(proxy)