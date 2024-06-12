TURN_RIGHT = 0
TURN_LEFT = 1
FORWARD = 2
BACKWARD = 3
DONTMOVE = 4

SHOOT = 0
AIM_RIGHT = 1
AIM_LEFT = 2

FIND_OIL = 0
FIND_BULLET = 1
FIND_ENEMY = 2

ANGLE_0 = 0
ANGLE_45 = 1
ANGLE_90 = 2
ANGLE_135 = 3
ANGLE_180 = 4
ANGLE_225 = 5
ANGLE_270 = 6
ANGLE_315 = 7
ANGLE_LIST = ["ANGLE_0", "ANGLE_45", "ANGLE_90", "ANGLE_135", "ANGLE_180", "ANGLE_225", "ANGLE_270", "ANGLE_315"]
RADIUS = 300
WIDTH = 1000
HEIGHT = 600

MAX_DISTANCE = 1166
MAX_OIL = 100
MAX_BULLET = 10
WALL_WIDTH = 50

defaultdict = {
    "STRATEGY_2P": {"feature": [[0, 0]], "target": [0]},
    "TANK_2P": {"feature": [[0, 0, 0, 0, 0, 0, 0, 0]], "target": [0]},
    "GUN_2P": {"feature": [[0, 0, 0]], "target": [0]},
    "STRATEGY_1P": {"feature": [[0, 0]], "target": [0]},
    "TANK_1P": {"feature": [[0, 0, 0, 0, 0, 0, 0, 0]], "target": [0]},
    "GUN_1P": {"feature": [[0, 0, 0]], "target": [0]}    
}