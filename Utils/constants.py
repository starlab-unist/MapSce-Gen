# Vehicle Model
STANDARD = 1
COMPACT = 2
SUV = 3
VAN = 4
TRUCK = 5

# Agent Types
BASIC = 0
BEHAVIOR = 1
LBC = 3
OTHER = 9

# BasicAgent config
TARGET_SPEED = 60
MAX_THROTTLE = 1  # 0.75
MAX_BRAKE = 1  # 0.3
MAX_STEERING = 0.8

# Static configurations
MAX_DIST_FROM_PLAYER = 40
MIN_DIST_FROM_PLAYER = 5
FRAME_RATE = 20
INIT_SKIP_SECONDS = 2

# Actors
NULL = -1  # special type for traction testing
VEHICLE = 0
WALKER = 1
ACTOR_LIST = [VEHICLE, WALKER]
ACTOR_NAMES = ["vehicle", "walker"]

# Actor Navigation Type
LINEAR = 0
AUTOPILOT = 1
IMMOBILE = 2
MANEUVER = 3
NAVTYPE_LIST = [LINEAR, AUTOPILOT, IMMOBILE]
NAVTYPE_NAMES = ["linear", "autopilot", "immobile", "maneuver"]

# Actor Attributes
VEHICLE_MAX_SPEED = 30  # multiplied with forward vector
WALKER_MAX_SPEED = 5  # m/s

# Puddle Attributes
PROB_PUDDLE = 25  # probability of adding a new puddle
PUDDLE_MAX_SIZE = 500  # centimeters

# Maneuver Attributes
FRAMES_PER_TIMESTEP = 100  # 5 seconds (tentative)

# Camera View Setting
ONROOF = 0
BIRDSEYE = 1

# Driving Quality
HARD_ACC_THRES = 21.2  # km/h per second
HARD_BRAKE_THRES = -21.2  # km/h per second

# Filter config
CUTOFF_FREQ_LIGHT = 3.5
CUTOFF_FREQ_HEAVY = 0.5

# Mutation targets
WEATHER = 0
ACTOR = 1
PUDDLE = 2
MUTATION_TARGET = [WEATHER, ACTOR, PUDDLE]

# Input mutation strategies
ALL = 0
CONGESTION = 1
ENTROPY = 2
INSTABILITY = 3
TRAJECTORY = 4

# Misc
DEVNULL = "2> /dev/null"
