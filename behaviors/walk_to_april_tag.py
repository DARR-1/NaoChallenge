from controllers.pid import PID
from robot.robot_interface import RobotInterface


class WalkToAprilTag:

    def __init__(
        self,
        robot: RobotInterface,
        distance_x=0.5,
        distance_y=0.0,
        dt=0.05,
        april_tag_id=0
    ):  

        self.robot = robot

        self.april_tag_id = april_tag_id

        self.distance_x = distance_x
        self.distance_y = distance_y

        self.dt = dt

        self.pid_x = PID(
            0.5,
            0.1,
            0.01,
            out_min=-1,
            out_max=1
        )

        self.pid_y = PID(
            0.5,
            0.1,
            0.01,
            out_min=-1,
            out_max=1
        )

        self.pid_theta = PID(
            0.8,
            0.0,
            0.02,
            out_min=-1,
            out_max=1
        )

    def update(self, dt):
        self.dt = dt

        tag = self.robot.get_april_tag_distances(
            self.april_tag_id
        )

        if tag is None:

            self.robot.walk(
                0,
                0,
                0
            )

            return

        x = tag["x"]
        y = tag["y"]
        z = tag["z"]

        theta = tag["yaw"]

        self.robot.aim(
            x,
            y,
            z
        )

        # distance control
        x_error = self.distance_x - x
        y_error = self.distance_y - y

        x_vel = self.pid_x.update(
            x_error,
            self.dt,
        )

        y_vel = self.pid_y.update(
            y_error,
            self.dt,
        )
        
        theta_vel = self.pid_theta.update(
            0,
            self.dt,
        )

        self.robot.walk(
            x_vel,
            y_vel,
            theta_vel
        )