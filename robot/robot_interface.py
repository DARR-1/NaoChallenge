from abc import ABCMeta, abstractmethod

class RobotInterface(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def move(self, x, y, theta):
        pass
    
    @abstractmethod
    def walk(self, x_vel, y_vel, theta_vel):
        pass

    @abstractmethod
    def aim(self, x, y, z):
        pass

    @abstractmethod
    def stop(self):
        self.walk(0, 0, 0)

    @abstractmethod
    def get_camera_image(self):
        pass

    @abstractmethod
    def get_ball_distances(self):
        pass

    @abstractmethod
    def start_moving(self):
        pass

    @abstractmethod
    def move_toward(self):
        pass