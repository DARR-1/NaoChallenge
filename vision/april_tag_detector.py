import numpy as np

from vision.camera import NaoCamera


class AprilTagPose(object):
    """Pose of a detected AprilTag w.r.t. the camera/robot convention used by this repo.

    Units:
      - x, y, z in meters
      - yaw, pitch, roll in radians

        Coordinate convention used in this project:
            - x: forward
            - y: left
            - z: up

        Internally, `pupil-apriltags` returns pose in the usual OpenCV camera frame:
            - x: right
            - y: down
            - z: forward

        We convert translation to the project convention with:
            x_fwd = z_cv
            y_left = -x_cv
            z_up = -y_cv
    """
    def __init__(self, tag_id, x, y, z, yaw, pitch, roll):
        self.tag_id = tag_id
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll


def _rvec_to_ypr(rvec):
    """Convert OpenCV Rodrigues rvec -> yaw/pitch/roll (Z-Y-X) in radians."""
    import cv2

    R, _ = cv2.Rodrigues(rvec.reshape(3, 1))
    # ZYX: R = Rz(yaw) * Ry(pitch) * Rx(roll)
    sy = float(np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0]))
    singular = sy < 1e-6

    if not singular:
        roll = float(np.arctan2(R[2, 1], R[2, 2]))
        pitch = float(np.arctan2(-R[2, 0], sy))
        yaw = float(np.arctan2(R[1, 0], R[0, 0]))
    else:
        # Gimbal lock fallback
        roll = float(np.arctan2(-R[1, 2], R[1, 1]))
        pitch = float(np.arctan2(-R[2, 0], sy))
        yaw = 0.0

    return yaw, pitch, roll


class AprilTagDetector(object):
    """Detect AprilTags from NAO camera frames and estimate pose.

    Requirements:
      - pip install pupil-apriltags opencv-python

    You must provide:
      - camera_matrix (3x3) and dist_coeffs for NAO camera (calibration)
      - tag_size_m: physical tag size in meters (edge length)
    """

    def __init__(self, camera, tag_size_m, camera_matrix, dist_coeffs=None, tag_families="tag36h11"):
        self._camera = camera
        self._tag_size_m = float(tag_size_m)
        self._K = np.asarray(camera_matrix, dtype=np.float64).reshape(3, 3)

        if dist_coeffs is None:
            self._dist = np.zeros((5, 1), dtype=np.float64)
        else:
            self._dist = np.asarray(dist_coeffs, dtype=np.float64).reshape(-1, 1)

        try:
            from pupil_apriltags import Detector
        except Exception as e:
            raise ImportError(
                "Missing dependency. Install with: pip install pupil-apriltags opencv-python"
            )

        self._detector = Detector(families=tag_families)

    def detect(self):
        """Detect all tags and return their poses (camera frame)."""
        import cv2

        img_bgr = self._camera.get_image()
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Intrinsics for pupil-apriltags: (fx, fy, cx, cy)
        fx = float(self._K[0, 0])
        fy = float(self._K[1, 1])
        cx = float(self._K[0, 2])
        cy = float(self._K[1, 2])

        detections = self._detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=(fx, fy, cx, cy),
            tag_size=self._tag_size_m,
        )

        out = []
        for d in detections:
            # pupil-apriltags returns:
            #  - d.pose_t: (3,1) translation in meters
            #  - d.pose_R: (3,3) rotation matrix
            t_cv = np.asarray(d.pose_t, dtype=np.float64).reshape(3)
            R = np.asarray(d.pose_R, dtype=np.float64).reshape(3, 3)

            # Convert translation from OpenCV camera frame to repo convention.
            # OpenCV: (x right, y down, z forward)
            # Repo:   (x forward, y left, z up)
            x = float(t_cv[2])
            y = float(-t_cv[0])
            z = float(-t_cv[1])

            # Convert R -> rvec -> yaw/pitch/roll
            rvec, _ = cv2.Rodrigues(R)
            yaw, pitch, roll = _rvec_to_ypr(rvec)

            out.append(
                AprilTagPose(
                    tag_id=int(d.tag_id),
                    x=x,
                    y=y,
                    z=z,
                    yaw=yaw,
                    pitch=pitch,
                    roll=roll,
                )
            )

        return out

    def get_pose(self, tag_id):
        """Return pose for a specific tag id, or None if not found."""
        for pose in self.detect():
            if pose.tag_id == int(tag_id):
                return pose
        return None