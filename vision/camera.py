import numpy as np


class NaoCameraConfig(object):
    # NAOqi ALVideoDevice defaults / common values
    def __init__(self, camera_index=1, resolution=2, color_space=11, fps=15):
        self.camera_index = camera_index  # 0=top, 1=bottom
        self.resolution = resolution  # 0=160x120, 1=320x240, 2=640x480, 3=1280x960
        self.color_space = color_space  # kBGRColorSpace = 11 (OpenCV-friendly)
        self.fps = fps


class NaoCamera(object):
    """Small helper to fetch images from NAO via NAOqi ALVideoDevice.

    Returns:
      - numpy ndarray in BGR order (H, W, 3), dtype=uint8
    """

    def __init__(self, ip, port=9559, config=None):
        from naoqi import ALProxy

        self._config = config or NaoCameraConfig()
        self._video = ALProxy("ALVideoDevice", ip, port)
        self._client_name = None

    def start(self):
        if self._client_name is not None:
            return
        self._client_name = self._video.subscribeCamera(
            "naoqi_competition_cam",
            self._config.camera_index,
            self._config.resolution,
            self._config.color_space,
            self._config.fps,
        )

    def stop(self):
        if self._client_name is None:
            return
        try:
            self._video.unsubscribe(self._client_name)
        finally:
            self._client_name = None

    def get_image(self):
        """Fetch one frame from the robot camera."""
        if self._client_name is None:
            self.start()

        data = self._video.getImageRemote(self._client_name)
        if data is None:
            raise RuntimeError("ALVideoDevice.getImageRemote returned None")

        # NAOqi format: [0]=width, [1]=height, ... [6]=image bytes
        width = int(data[0])
        height = int(data[1])
        buf = data[6]
        if buf is None:
            raise RuntimeError("ALVideoDevice.getImageRemote: empty image buffer")

        img = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 3))  # BGR
        return img

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()