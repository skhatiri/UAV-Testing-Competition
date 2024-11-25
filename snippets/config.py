# Global Variables

# Fibonacci Spiral
NUM_SPIRAL_POINTS = 3500
SPIRAL_GOLDEN_ANGLE = 0.1 
SPIRAL_RADIUS_INCREMENT = 0.01

# Generation Area
GENERATION_AREA_MIN_POS = (-40,10)
GENERATION_AREA_MAX_POS = (30,40)

# Filtered Spiral
THRESHOLD_DISTANCE = 3 #meters
ROUND_PARAMETER = 1

# Discrete steps on x and y when mutating
DRONE_SIZE = 0.55
X_RANGE = [-15, -10, -5, 5, 10, 15]
Y_RANGE = [-15, -10, -5, 5, 10, 15]
X_RANGE = [x * DRONE_SIZE for x in X_RANGE]
Y_RANGE = [x * DRONE_SIZE for x in Y_RANGE]

#Obstacles
OBST_LENGTH = 20 #meters
OBST_WIDTH = 2 #meters 
OBSTACLE_HEIGHT = 25 #meters
OBST_Z = 0
ANGLE_STEP = 10
MAX_ATTEMPTS_GENERATION = 1000
MAX_ATTEMPTS_PERFORMANCE = 10

# Execution
MINIMUM_DISTANCE_EXECUTION = 50 # meters
LOCAL_MINIMUM = 50
DIR_GENERATED_PLOTS = "./generated_tests_plot/"
DIR_GENERATED_TESTS = "./generated_tests/"
TESTING = False
NUM_OBSTS = 2
