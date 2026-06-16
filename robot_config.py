CAMERA_MATRIX = [
    [500, 0, 320],
    [0, 500, 240],
    [0, 0, 1]
]
DIST_COEFFS = [0, 0, 0, 0]

IP_ADDRESS = "192.168.0.165"
PORT = 9559

def StiffnessOn(motionProxy):
    motionProxy.stiffnessInterpolation("Body", 1.0, 1.0)


def PoseInit(motionProxy):
    names = [
        "HeadYaw", "HeadPitch",
        "LShoulderPitch", "LShoulderRoll",
        "LElbowYaw", "LElbowRoll",
        "RShoulderPitch", "RShoulderRoll",
        "RElbowYaw", "RElbowRoll",
        "LHipYawPitch", "LHipRoll", "LHipPitch",
        "LKneePitch", "LAnklePitch", "LAnkleRoll",
        "RHipRoll", "RHipPitch",
        "RKneePitch", "RAnklePitch", "RAnkleRoll"
    ]

    angles = [
        0.0, 0.0,
        1.4, 0.3,
        -1.2, -0.5,
        1.4, -0.3,
        1.2, 0.5,
        0.0, 0.0, -0.4,
        0.95, -0.55, 0.0,
        0.0, -0.4,
        0.95, -0.55, 0.0
    ]

    fractionMaxSpeed = 0.2

    motionProxy.setAngles(names, angles, fractionMaxSpeed)