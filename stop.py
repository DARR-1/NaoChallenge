import time

import robot_config
from robot.naoqi_robot import NaoqiRobot
from behaviors.walk_to_ball import WalkToBall
from behaviors.search_ball import SearchForBall
from behaviors.kick import Kick
from behaviors.goalie import Goalie
from behaviors.race import Race


robot = NaoqiRobot(robot_config.IP_ADDRESS)


prev_time = time.time()

try:
    robot.stop()
except Exception as e:
    print(e)
    print("Exiting...")
    robot.stop()
