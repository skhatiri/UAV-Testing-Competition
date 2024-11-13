# Global Variables

class Position:
    """
    Represents a 3D position in Cartesian coordinates with an optional angle attribute.
    
    Attributes:
    x (float): X-coordinate in meters.
    y (float): Y-coordinate in meters.
    z (float): Z-coordinate in meters (default is 0).
    angle (int): Angle in degrees (default is 0).
    """
    def __init__(self, x: float, y: float, z: float = 0, angle: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

OBSTACLE_HEIGHT = 25
NUM_SPIRAL_POINTS = 600

GENERATION_AREA_MIN_POS = Position(-40,10)
GENERATION_AREA_MAX_POS = Position(30,40)

OBST_MIN_LENGTH = 2
OBST_MIN_WIDTH = 2
OBST_MAX_WIDTH = 20
OBST_MAX_LENGTH = 20
OBST_MIN_HEIGHT = 10
OBST_MAX_HEIGHT = 25

THRESHOLD_DISTANCE = 3

DIR_GENERATED_PLOTS = "generated_tests_plot/"

SPIRAL_GOLDEN_ANGLE = 0.1 
SPIRAL_RADIUS_INCREMENT = 0.02
SPIRAL_NUM_POINTS = 30

MIN_DISTANCE = 10
MAX_DISTANCE = 14

DRONE_DIMENSIONS = 0.55

NUM_OBSTACLES = 2