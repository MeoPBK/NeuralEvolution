# === Population ===
FOOD_SPAWN_RATE = 30  # food items per second

# === Genetics ===
MUTATION_RATE = 0.2           # per gene per reproduction event
CROSSOVER_RATE = 0.3           # per chromosome per meiosis
LARGE_MUTATION_CHANCE = 0.05   # within mutations, chance of large effect
DOMINANCE_MUTATION_RATE = 0.15 # chance a mutation affects dominance instead of value
POINT_MUTATION_STDDEV = 0.3    # standard deviation for point mutations
LARGE_MUTATION_STDDEV = 1.5    # standard deviation for large-effect mutations

# === Neural Network ===
NN_TYPE = 'FNN'                # 'FNN' for feed-forward or 'RNN' for recurrent
NN_WEIGHT_INIT_STD = 0.5       # std for initial brain weight alleles

# === Energy ===
BASE_ENERGY = 150.0
MAX_ENERGY = 300.0
REPRODUCTION_THRESHOLD = 80.0
REPRODUCTION_COST = 40.0
FOOD_ENERGY = 60.0
ENERGY_DRAIN_BASE = 0.3        # base energy loss per second
MOVEMENT_ENERGY_FACTOR = 0.01  # energy cost = speed * size / efficiency * factor

# === Hydration ===
BASE_HYDRATION = 100.0
MAX_HYDRATION = 150.0
HYDRATION_DRAIN_RATE = 0.4     # hydration loss per second
DRINK_RATE = 30.0              # hydration gain per second when in water

# === Water ===
NUM_WATER_SOURCES = 4
WATER_SOURCE_RADIUS = 40.0

# === Combat ===
ATTACK_DISTANCE = 10.0
ATTACK_DAMAGE_BASE = 20.0     # damage/sec base
ATTACK_ENERGY_COST = 2.0      # energy cost/sec to attack
KILL_ENERGY_GAIN = 30.0       # energy gained on kill

# === Food Clusters ===
NUM_FOOD_CLUSTERS = 5
FOOD_CLUSTER_SPREAD = 40.0    # Gaussian sigma for food scatter
SEASON_SHIFT_INTERVAL = 30.0  # seconds between cluster drift

# === World ===
WORLD_WIDTH = 3000
WORLD_HEIGHT = 1400
GRID_CELL_SIZE = 50
HUD_WIDTH = 280
WINDOW_WIDTH = WORLD_WIDTH + HUD_WIDTH
WINDOW_HEIGHT = WORLD_HEIGHT

# === Agents ===
MAX_SPEED_BASE = 6.0
EATING_DISTANCE = 10.0
MATING_DISTANCE = 50.0
WANDER_STRENGTH = 0.5
STEER_STRENGTH = 0.1

# === Aging ===
MATURITY_AGE = 5.0            # must be this old to reproduce

# === Reproduction ===
REPRODUCTION_COOLDOWN = 3.0   # seconds between reproductions
MATE_SEARCH_RADIUS = 100.0

# === Geographic Zones ===
TEMPERATURE_ZONES_X = 4  # Number of temperature zones horizontally
TEMPERATURE_ZONES_Y = 3  # Number of temperature zones vertically

# === Trait Ranges (for clamping phenotype) ===
TRAIT_RANGES = {
    'speed': (1.0, 6.0),
    'size': (3.0, 12.0),
    'vision_range': (40.0, 200.0),
    'energy_efficiency': (0.5, 2.0),
    'reproduction_urge': (0.3, 1.5),
    'camouflage': (0.0, 1.0),
    'aggression': (0.3, 2.0),
    'max_age': (10.0, 150.0),  # Range for genetic max age (from 10 to 150)
}

# === Trait Defaults (initial population mean) ===
TRAIT_DEFAULTS = {
    'speed': 3.0,
    'size': 6.0,
    'vision_range': 100.0,
    'energy_efficiency': 1.0,
    'reproduction_urge': 0.8,
    'camouflage': 0.5,
    'aggression': 1.0,
    'max_age': 70.0,  # Default max age for agents
}

# === Rendering ===
FPS = 60
BG_COLOR = (20, 35, 20)
FOOD_COLOR = (100, 220, 50)
WATER_COLOR = (60, 130, 220)
AGENT_COLOR_PASSIVE = (50, 200, 50)
AGENT_COLOR_AGGRESSIVE = (220, 50, 50)
HUD_BG_COLOR = (30, 30, 40)
TEXT_COLOR = (220, 220, 220)
GRAPH_AGENT_COLOR = (100, 180, 220)
