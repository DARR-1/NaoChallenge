import time

from naoqi import ALProxy
import robot_config
from robot.naoqi_robot import NaoqiRobot
from behaviors.walk_to_ball import WalkToBall
from behaviors.search_ball import SearchForBall
from behaviors.kick import Kick
from behaviors.goalie import Goalie
from behaviors.race import Race


robot = NaoqiRobot(robot_config.IP_ADDRESS)

search_ball_behavior = SearchForBall(robot)
walk_to_ball_behavior = WalkToBall(robot)
kick_behavior = Kick(robot)
goalie_behavior = Goalie(robot)
race_behavior = Race(robot, 7, 0)


prev_time = time.time()
selected_action = "ns"

try:
    robot.motion.wakeUp()
    robot.posture.goToPosture("StandInit", 0.5)

    animated_speech = ALProxy(
            "ALAnimatedSpeech", 
            robot_config.IP_ADDRESS, robot_config.PORT
        )

    configuration = {
        "bodyLanguageMode": "disabled"
    }

    while not robot.mem.getData("Device/SubDeviceList/ChestBoard/Button/Sensor/Value"):
        right_hand = robot.mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value")

        head = robot.mem.getData("Device/SubDeviceList/Head/Touch/Middle/Sensor/Value")
        head_back = robot.mem.getData("Device/SubDeviceList/Head/Touch/Rear/Sensor/Value")
            
        if right_hand:
            selected_action = "kick_right"
            animated_speech.say("Estado patear derecho seleccionado", configuration)
            search_ball_behavior.run()
            walk_to_ball_behavior.run(True, "right")
            kick_behavior.run()
            robot.stop()
        elif head:
            selected_action = "portero"
            #animated_speech.say("Estado portero seleccionado", configuration)
            goalie_behavior.run()
            robot.stop()
        elif head_back:
            selected_action = "race"
            #animated_speech.say("Estado carrera seleccionado", configuration)
            race_behavior.run()
            robot.stop()
        else:
            selected_action = "ns"

    robot.stop()
except Exception as e:
    print(e)
    print("Exiting...")
    robot.stop()
