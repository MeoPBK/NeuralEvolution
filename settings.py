#-*- coding: utf-8 -*-

"""
This file contains the settings that can be configured through the UI.
"""

SETTINGS = {
    # === ENVIRONMENT SETTINGS ===
    
    # === World ===
    'WORLD_WIDTH': 1200,
    'WORLD_HEIGHT': 600,
    'GRID_CELL_SIZE': 50,
    'HUD_WIDTH': 280,
    'WINDOW_WIDTH': 3280,  # WORLD_WIDTH + HUD_WIDTH
    'WINDOW_HEIGHT': 1400,

    # === Population ===
    'INITIAL_AGENTS': 150,
    'MAX_FOOD': 400,
    'FOOD_SPAWN_RATE': 30,

    # === Food Clusters ===
    'NUM_FOOD_CLUSTERS': 5,
    'FOOD_CLUSTER_SPREAD': 40.0,
    'SEASON_SHIFT_INTERVAL': 30.0,

    # === Water ===
    'NUM_WATER_SOURCES': 4,  # Number of water sources (now unified with lakes)
    'WATER_SOURCE_RADIUS': 40.0,  # Radius for water sources (now unified with lakes)
    'RIVER_WIDTH': 25.0,
    'LAKE_SIZE_UNIFORM': True,  # Whether to make all lakes the same size (unified with water sources)
    'LAKE_SIZE': 80.0,  # Fixed size for lakes when LAKE_SIZE_UNIFORM is True (unified with water sources)
    'LAKE_IRREGULARITY': 0.4,  # How irregular the lake shape is (unified with water sources)

    # === Obstacles & Walls ===
    'OBSTACLES_ENABLED': False,  # Enable/disable obstacles (now rocks when enabled)
    'BORDER_ENABLED': True,  # Enable/disable border walls
    'BORDER_WIDTH': 10,  # Width of border obstacles around the world
    'NUM_INTERNAL_OBSTACLES': 5,  # Number of internal obstacles to create (now used for rocks)
    'ROCK_TYPES_ENABLED': True,  # Enable different rock types (granite, limestone, etc.)
    'TREES_ENABLED': True,  # Enable/disable trees (separate from other obstacles)
    'NUM_TREES': 15,  # Number of trees to generate in the world
    'TREE_DENSITY': 0.0001,  # Density of trees per unit area (alternative to NUM_TREES)
    'ENABLE_TREE_FOOD_SOURCES': True,  # Enable food generation around trees for herbivores/omnivores
    'TREE_FOOD_PROXIMITY': 30.0,  # Distance from trees where food appears
    'TREE_FOOD_SPAWN_RATE': 15,  # Rate at which food spawns near trees

    # === Temperature Zones ===
    'TEMPERATURE_ENABLED': False,  # Enable/disable temperature zones
    'TEMPERATURE_ZONES_X': 2,  # Number of temperature zones horizontally
    'TEMPERATURE_ZONES_Y': 2,  # Number of temperature zones vertically

    # === Geographic Variations ===
    'REGIONAL_VARIATIONS_ENABLED': False,
    'NUM_REGIONS_X': 2,  # Number of regions horizontally
    'NUM_REGIONS_Y': 2,  # Number of regions vertically
    'REGION_SPEED_MODIFIER': [1.1, 0.9, 1.0, 1.2],  # Speed modifiers for each region (TL, TR, BL, BR)
    'REGION_SIZE_MODIFIER': [0.9, 1.1, 1.0, 0.8],   # Size modifiers for each region
    'REGION_AGGRESSION_MODIFIER': [1.2, 0.8, 1.0, 1.3],  # Aggression modifiers for each region
    'REGION_EFFICIENCY_MODIFIER': [0.95, 1.05, 1.0, 0.85],  # Energy efficiency modifiers for each region

    # === Virus/Epidemic Settings ===
    'EPIDEMIC_ENABLED': False,
    'EPIDEMIC_INTERVAL': 100.0,  # seconds between checks
    'EPIDEMIC_MIN_POPULATION_RATIO': 0.8,  # minimum population ratio to trigger
    'EPIDEMIC_AFFECTED_RATIO': 0.3,  # fraction of population affected
    'EPIDEMIC_BASE_PROBABILITY': 0.001,  # base probability when conditions met

    # === Disease & Epidemic Settings ===
    'DISEASE_TRANSMISSION_ENABLED': True,  # Enable/disable disease transmission between agents
    'DISEASE_TRANSMISSION_DISTANCE': 15.0,  # Distance threshold for disease transmission
    'DISEASE_NAMES': ['Flu', 'Plague', 'Malaria', 'Pox', 'Fever', 'Rot', 'Blight', 'Wilt'],  # Names for different diseases
    'NUM_DISEASE_TYPES': 4,  # Number of different disease types in the simulation

    # === AGENT SETTINGS ===
    
    # === Genetics ===
    'MUTATION_RATE': 0.2,
    'CROSSOVER_RATE': 0.3,
    'LARGE_MUTATION_CHANCE': 0.05,
    'DOMINANCE_MUTATION_RATE': 0.15,
    'POINT_MUTATION_STDDEV': 0.3,
    'LARGE_MUTATION_STDDEV': 1.5,
    'SOMATIC_MUTATION_RATE': 0.2,

    # === Neural Network (V2 Architecture) ===
    'NN_TYPE': 'FNN',  # 'FNN' (254 weights) or 'RNN' (318 weights)
    'NN_HIDDEN_SIZE': 8,  # Hidden layer neurons
    'NN_WEIGHT_INIT_STD': 0.3,  # Weight initialization std
    'NN_RECURRENT_IDENTITY_BIAS': 0.1,  # Identity bias for RNN stability
    'NN_HIDDEN_NOISE_ENABLED': False,  # Add stochastic noise to RNN hidden state
    'NN_HIDDEN_NOISE_STD': 0.02,  # Noise standard deviation

    # === N-Step Memory (Optional) ===
    'N_STEP_MEMORY_ENABLED': False,  # Store past hidden states as inputs
    'N_STEP_MEMORY_DEPTH': 2,  # Number of past states to store

    # === Sensing ===
    'SECTOR_COUNT': 5,  # Number of angular vision sectors
    'VISION_NOISE_STD': 0.05,  # Noise added to sensor inputs

    # === Internal State ===
    'STRESS_GAIN_RATE': 0.5,  # Stress accumulation rate
    'STRESS_DECAY_RATE': 0.2,  # Stress natural decay rate
    'STRESS_THREAT_WEIGHT': 1.0,  # Weight for nearby threat stress
    'STRESS_RESOURCE_WEIGHT': 0.5,  # Weight for low resource stress

    # === Effort System ===
    'EFFORT_SPEED_SCALE': 1.0,  # How much effort affects speed
    'EFFORT_DAMAGE_SCALE': 0.5,  # How much effort affects attack damage
    'EFFORT_ENERGY_SCALE': 1.5,  # How much effort affects energy cost

    # === Energy ===
    'BASE_ENERGY': 150.0,
    'MAX_ENERGY': 300.0,
    'REPRODUCTION_THRESHOLD': 80.0,
    'REPRODUCTION_COST': 40.0,
    'FOOD_ENERGY': 60.0,
    'ENERGY_DRAIN_BASE': 0.3,
    'MOVEMENT_ENERGY_FACTOR': 0.01,

    # === Hydration ===
    'BASE_HYDRATION': 100.0,
    'MAX_HYDRATION': 150.0,
    'HYDRATION_DRAIN_RATE': 0.4,
    'DRINK_RATE': 30.0,

    # === Combat ===
    'ATTACK_DISTANCE': 10.0,
    'ATTACK_DAMAGE_BASE': 20.0,
    'ATTACK_ENERGY_COST': 2.0,
    'KILL_ENERGY_GAIN': 30.0,

    # === Agents ===
    'MAX_SPEED_BASE': 6.0,
    'EATING_DISTANCE': 10.0,
    'MATING_DISTANCE': 50.0,
    'WANDER_STRENGTH': 0.5,
    'STEER_STRENGTH': 0.3,

    # === Aging ===
    'MATURITY_AGE': 5.0,
    'RANDOM_AGE_INITIALIZATION': True,  # Initialize agents with random ages between 0 and max age

    # === Reproduction ===
    'REPRODUCTION_COOLDOWN': 3.0,
    'MATE_SEARCH_RADIUS': 100.0,

    # === Other ===
    'MAX_AGE': 70.0,
    'CANNIBALISM_ENERGY_BONUS': 20.0,  # Additional energy gained from eating another agent

    # === Diet & Habitat ===
    'diet_type': 1.0,  # 0=carnivore, 1=omnivore, 2=herbivore
    'habitat_preference': 1.0,  # 0=aquatic, 1=amphibious, 2=terrestrial
    'diet_speed_efficiency': 1.0,  # Speed efficiency based on diet appropriateness
    'habitat_energy_cost': 1.0,  # Energy cost factor based on habitat match
    'diet_energy_conversion': 1.0,  # Energy conversion efficiency based on diet
    'habitat_movement_efficiency': 1.0,  # Movement efficiency based on habitat match
    'speed_in_water_aquatic': 5.0,      # Speed in water for aquatic agents
    'speed_in_water_amphibious': 3.0,   # Speed in water for amphibious agents
    'speed_in_water_terrestrial': 1.0,  # Speed in water for terrestrial agents
    'land_speed_aquatic': 2.0,          # Speed on land for aquatic agents (usually slower)
    'land_speed_amphibious': 4.0,       # Speed on land for amphibious agents (moderate)
    'land_speed_terrestrial': 5.5,      # Speed on land for terrestrial agents (usually fastest)
    'energy_consumption_aquatic': 0.8,  # Energy consumption rate for aquatic agents
    'energy_consumption_amphibious': 1.0, # Energy consumption rate for amphibious agents
    'energy_consumption_terrestrial': 0.9, # Energy consumption rate for terrestrial agents
    'vision_range_aquatic': 80.0,       # Vision range for aquatic agents in water
    'vision_range_amphibious': 100.0,   # Vision range for amphibious agents
    'vision_range_terrestrial': 120.0,  # Vision range for terrestrial agents on land
    'RANDOMIZE_DIET_TYPE': True,  # Randomly assign initial diet type
    'RANDOMIZE_HABITAT_PREF': True,  # Randomly assign initial habitat preference

    # === Species Settings ===
    'INITIAL_SAME_SPECIES_PERCENTAGE': 1.0,  # 100% of initial population from same species
    'SPECIES_GENETIC_SIMILARITY_THRESHOLD': 0.8,  # Genetic similarity threshold for same species
    'SPECIES_DRIFT_RATE': 0.4,  # Rate at which genetic differences accumulate
    'HYBRID_FERTILITY_RATE': 0.1,  # Fertility rate for cross-species offspring (10% of normal)

    # === Reproduction Settings ===
    'MAX_SIMULTANEOUS_OFFSPRING': 1,  # Maximum number of offsprings per mating session

    # === Species Settings ===
    'NUMBER_OF_INITIAL_SPECIES': 4,  # Number of different species in the initial population (for visual diversity)

    # === Rendering ===
    'FPS': 60,

    # === Physics & Environment ===
    'WORLD_BOUNDARY_TYPE': 'wrap',  # 'wrap', 'bounce', or 'solid' - how agents behave at world edges
    'GRAVITY_ENABLED': False,  # Enable/disable gravity physics
    'WIND_EFFECTS': False,  # Enable/disable wind forces affecting agents
    'SEASONAL_CHANGES': False,  # Enable/disable seasonal environmental changes
    'WEATHER_SYSTEM': False,  # Enable/disable dynamic weather patterns
    'TERRAIN_FEATURES': False,  # Enable/disable varied terrain features
    'SIMULATION_SPEED': 1.0,  # Multiplier for simulation speed (1.0 = normal speed)
    'PARTICLE_EFFECTS': True,  # Enable/disable visual particle effects
    'BACKGROUND_ELEMENTS': True,  # Enable/disable decorative background elements

    # === Trait Ranges (for clamping phenotype) ===
    'TRAIT_RANGES': {
        'speed': (1.0, 6.0),
        'size': (3.0, 12.0),
        'vision_range': (40.0, 200.0),
        'energy_efficiency': (0.5, 2.0),
        'reproduction_urge': (0.3, 1.5),
        'camouflage': (0.0, 1.0),
        'aggression': (0.3, 2.0),
        'max_age': (10.0, 150.0),  # Reasonable range for max age
        'virus_resistance': (0.0, 1.0),  # Range from 0 (no resistance) to 1 (full resistance)
        'agility': (0.0, 1.0),  # Morphological trait: turning/acceleration
        'armor': (0.0, 1.0),  # Morphological trait: damage reduction
        # New diet and habitat traits
        'diet_type': (0.0, 2.0),  # 0=carnivore, 1=omnivore, 2=herbivore
        'habitat_preference': (0.0, 2.0),  # 0=aquatic, 1=amphibious, 2=terrestrial
        # Speed in water for each habitat type
        'speed_in_water_aquatic': (2.0, 8.0),      # Speed in water for aquatic agents (fastest)
        'speed_in_water_amphibious': (1.0, 5.0),   # Speed in water for amphibious agents (moderate)
        'speed_in_water_terrestrial': (0.5, 2.0),  # Speed in water for terrestrial agents (slowest)
        # Speed on land for each habitat type
        'land_speed_aquatic': (1.0, 4.0),          # Speed on land for aquatic agents (slower)
        'land_speed_amphibious': (2.0, 6.0),       # Speed on land for amphibious agents (moderate)
        'land_speed_terrestrial': (3.0, 7.0),      # Speed on land for terrestrial agents (faster)
        # Energy consumption for each habitat type
        'energy_consumption_aquatic': (0.5, 1.5),  # Energy consumption rate for aquatic agents
        'energy_consumption_amphibious': (0.7, 1.3), # Energy consumption rate for amphibious agents
        'energy_consumption_terrestrial': (0.6, 1.4), # Energy consumption rate for terrestrial agents
        # Vision range for each habitat type
        'vision_range_aquatic': (60.0, 120.0),     # Vision range for aquatic agents in water
        'vision_range_amphibious': (80.0, 140.0),  # Vision range for amphibious agents
        'vision_range_terrestrial': (100.0, 160.0), # Vision range for terrestrial agents on land
        # Diet and habitat specific parameters
        'AQUATIC_TERRAIN_PENALTY': (0.0, 1.0),  # Penalty for aquatic agents on land
        'TERRESTRIAL_WATER_PENALTY': (0.0, 1.0),  # Penalty for terrestrial agents in water
        'HABITAT_TRANSITION_COST': (0.0, 10.0),  # Energy cost for habitat transitions
        'AQUATIC_SWIMMING_EFFICIENCY': (0.1, 10.0),  # Swimming efficiency for aquatic agents
        'TERRESTRIAL_LAND_EFFICIENCY': (0.1, 10.0),  # Land movement efficiency for terrestrial agents
        'DIET_FOOD_PREFERENCE_CARNIVORE': (0.0, 5.0),  # Food preference strength for carnivores
        'DIET_FOOD_PREFERENCE_HERBIVORE': (0.0, 5.0),  # Food preference strength for herbivores
        'DIET_FOOD_PREFERENCE_OMNIVORE': (0.0, 3.0),  # Food preference strength for omnivores
    },

    # === Trait Defaults (initial population mean) ===
    'TRAIT_DEFAULTS': {
        'speed': 3.0,
        'size': 6.0,
        'vision_range': 100.0,
        'energy_efficiency': 1.0,
        'reproduction_urge': 0.8,
        'camouflage': 0.5,
        'aggression': 1.0,
        'max_age': 70.0,
        'virus_resistance': 0.5,  # Default to medium resistance
        'agility': 0.5,  # Default to medium agility
        'armor': 0.5,  # Default to medium armor
        # New diet and habitat defaults
        'diet_type': 1.0,  # Default to omnivore
        'habitat_preference': 1.0,  # Default to amphibious
        # Speed in water defaults for each habitat type
        'speed_in_water_aquatic': 5.0,      # Default speed in water for aquatic agents
        'speed_in_water_amphibious': 3.0,   # Default speed in water for amphibious agents
        'speed_in_water_terrestrial': 1.0,  # Default speed in water for terrestrial agents
        # Speed on land defaults for each habitat type
        'land_speed_aquatic': 2.0,          # Default speed on land for aquatic agents
        'land_speed_amphibious': 4.0,       # Default speed on land for amphibious agents
        'land_speed_terrestrial': 5.5,      # Default speed on land for terrestrial agents
        # Energy consumption defaults for each habitat type
        'energy_consumption_aquatic': 0.8,  # Default energy consumption rate for aquatic agents
        'energy_consumption_amphibious': 1.0, # Default energy consumption rate for amphibious agents
        'energy_consumption_terrestrial': 0.9, # Default energy consumption rate for terrestrial agents
        # Vision range defaults for each habitat type
        'vision_range_aquatic': 80.0,       # Default vision range for aquatic agents in water
        'vision_range_amphibious': 100.0,   # Default vision range for amphibious agents
        'vision_range_terrestrial': 120.0,  # Default vision range for terrestrial agents on land
        # Diet and habitat specific defaults
        'AQUATIC_TERRAIN_PENALTY': 0.7,
        'TERRESTRIAL_WATER_PENALTY': 0.6,
        'HABITAT_TRANSITION_COST': 2.0,
        'AQUATIC_SWIMMING_EFFICIENCY': 2.0,
        'TERRESTRIAL_LAND_EFFICIENCY': 2.0,
        'DIET_FOOD_PREFERENCE_CARNIVORE': 1.5,
        'DIET_FOOD_PREFERENCE_HERBIVORE': 1.5,
        'DIET_FOOD_PREFERENCE_OMNIVORE': 1.0,
    },


    # ============================================
    # === ADVANCED FEATURES (Optional) =========
    # ============================================

    # === 1. Body Size Effects ===
    'ADVANCED_SIZE_EFFECTS_ENABLED': False,  # Enable size-based trade-offs
    'SIZE_ATTACK_SCALING': 1.5,  # Larger = stronger attacks (exponent)
    'SIZE_SPEED_PENALTY': 0.3,  # Larger = slower (linear penalty per size unit)
    'SIZE_TURN_PENALTY': 0.4,  # Larger = slower turning
    'SIZE_METABOLIC_SCALING': 1.3,  # Superlinear metabolic cost exponent
    'SIZE_PERCEPTION_BONUS': 0.1,  # Larger = slightly better perception range

    # === 2. Size-Scaled Energy Costs ===
    'SUPERLINEAR_ENERGY_SCALING': True,  # Use superlinear scaling for large agents
    'ENERGY_SIZE_EXPONENT': 1.4,  # Metabolic cost scales as size^exponent
    'EFFORT_SIZE_INTERACTION': 0.5,  # How much effort amplifies size cost

    # === 3. Age-Dependent Modulation ===
    'AGE_EFFECTS_ENABLED': False,  # Enable age-based modulation
    'AGE_PRIME_START': 0.2,  # Age ratio when prime begins
    'AGE_PRIME_END': 0.6,  # Age ratio when prime ends
    'AGE_SPEED_DECLINE': 0.3,  # Max speed reduction in old age
    'AGE_STAMINA_DECLINE': 0.4,  # Max stamina reduction in old age
    'AGE_EXPERIENCE_BONUS': 0.2,  # Combat bonus from experience (peaks at prime)
    'AGE_REPRODUCTION_CURVE': True,  # Reproduction effectiveness varies with age

    # === 4. Internal State Behavior Bias ===
    'INTERNAL_STATE_MODULATION_ENABLED': False,  # Enable soft internal state effects
    'LOW_ENERGY_ATTACK_PENALTY': 0.5,  # Attack effectiveness when energy < 30%
    'LOW_HYDRATION_SPEED_PENALTY': 0.3,  # Speed penalty when dehydrated
    'HIGH_STRESS_EFFORT_BOOST': 0.2,  # Stress can boost short-term effort
    'EXHAUSTION_THRESHOLD': 0.2,  # Energy level below which penalties apply

    # === 5. Action-Specific Cost Asymmetry ===
    'ACTION_COSTS_ENABLED': False,  # Enable differentiated action costs
    'COST_HIGH_SPEED_MULTIPLIER': 1.5,  # Extra cost for max speed movement
    'COST_SHARP_TURN_MULTIPLIER': 1.3,  # Extra cost for sharp direction changes
    'COST_PURSUIT_MULTIPLIER': 1.2,  # Extra cost for sustained pursuit
    'COST_ATTACK_BASE': 3.0,  # Base energy cost per attack tick
    'COST_MATING_BASE': 5.0,  # Energy cost for mating attempt

    # === 6. Morphological Trade-offs ===
    'MORPHOLOGY_TRAITS_ENABLED': False,  # Enable agility and armor traits
    'AGILITY_SPEED_BONUS': 0.4,  # High agility = faster turning/acceleration
    'AGILITY_STAMINA_COST': 0.2,  # High agility = higher base metabolism
    'ARMOR_DAMAGE_REDUCTION': 0.4,  # High armor = reduced incoming damage
    'ARMOR_SPEED_PENALTY': 0.3,  # High armor = slower movement
    'ARMOR_ENERGY_COST': 0.15,  # High armor = higher maintenance cost

    # === 7. Sensory Imperfection ===
    'SENSORY_NOISE_ENABLED': True,  # Enable sensory noise (uses VISION_NOISE_STD)
    'SENSOR_DROPOUT_RATE': 0.05,  # Probability of missing a sector signal
    'INTERNAL_STATE_NOISE': 0.03,  # Noise on internal state perception
    'PERCEPTION_LAG': 0.0,  # Optional: slight delay in perception (0 -> disabled)

    # === 8. Short-Term Context Signals ===
    'CONTEXT_SIGNALS_ENABLED': False,  # Enable time-since signals as inputs
    'TIME_SINCE_FOOD_DECAY': 10.0,  # Seconds for signal to decay to 0
    'TIME_SINCE_DAMAGE_DECAY': 15.0,  # Seconds for damage signal to decay
    'TIME_SINCE_MATING_DECAY': 20.0,  # Seconds for mating signal to decay

    # === 9. Social Pressure Effects ===
    'SOCIAL_PRESSURE_ENABLED': True,  # Enable crowding/social stress
    'CROWD_STRESS_RADIUS': 50.0,  # Radius for counting nearby agents
    'CROWD_STRESS_THRESHOLD': 3,  # Number of agents before stress increases
    'CROWD_STRESS_RATE': 0.1,  # Stress increase per extra agent
    'DOMINANCE_STRESS_FACTOR': 0.5,  # Stress from larger/aggressive neighbors
}