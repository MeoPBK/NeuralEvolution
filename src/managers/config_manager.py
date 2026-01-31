"""
Configuration manager for handling multiple agent configurations in multiagent mode.
"""
import json
import os
from typing import Dict, List, Any, Optional


class ConfigManager:
    """Manages multiple agent configurations for multiagent simulations."""

    def __init__(self, saves_dir: str = "saves"):
        self.saves_dir = saves_dir
        self.selected_configs = []
        self.environmental_settings = {}
        self.agent_configs = {}

    def get_available_configs(self) -> List[str]:
        """Get list of available configuration files from the saves/configs directory."""
        # Look in saves/configs directory first, then falls back to saves directory
        configs_dir = os.path.join(self.saves_dir, 'configs')

        if os.path.exists(configs_dir):
            search_dir = configs_dir
        else:
            search_dir = self.saves_dir

        if not os.path.exists(search_dir):
            return []

        config_files = []
        for file_name in os.listdir(search_dir):
            if file_name.endswith('.json'):
                config_files.append(file_name)

        return sorted(config_files)

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load a single configuration file."""
        # Try to load from configs directory first, then from main saves directory
        configs_dir = os.path.join(self.saves_dir, 'configs')
        config_path = os.path.join(configs_dir, config_name)

        # If file doesn't exist in configs dir, try main saves dir
        if not os.path.exists(config_path):
            config_path = os.path.join(self.saves_dir, config_name)

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading config {config_name}: {e}")
            return {}

    def split_config(self, config: Dict[str, Any]) -> tuple:
        """
        Split a configuration into environmental settings and agent-specific settings.

        Returns:
            tuple: (environmental_settings, agent_settings)
        """
        # Define which settings are environmental (shared) vs agent-specific
        environmental_keys = {
            'WORLD_WIDTH', 'WORLD_HEIGHT', 'FOOD_SPAWN_RATE', 'INITIAL_FOOD',
            'WORLD_BOUNDARY_TYPE', 'GRAVITY_ENABLED', 'WIND_EFFECTS',
            'SEASONAL_CHANGES', 'WEATHER_SYSTEM', 'TERRAIN_FEATURES',
            'SIMULATION_SPEED', 'PARTICLE_EFFECTS', 'BACKGROUND_ELEMENTS',
            'MAX_FOOD', 'NUM_WATER_SOURCES', 'WATER_SOURCE_RADIUS',
            'NUM_FOOD_CLUSTERS', 'FOOD_CLUSTER_SPREAD', 'SEASON_SHIFT_INTERVAL',
            'GRID_CELL_SIZE', 'HUD_WIDTH', 'WINDOW_WIDTH', 'WINDOW_HEIGHT',
            'OBSTACLES_ENABLED', 'BORDER_ENABLED', 'BORDER_WIDTH', 'NUM_INTERNAL_OBSTACLES',
            'TEMPERATURE_ENABLED', 'TEMPERATURE_ZONES_X', 'TEMPERATURE_ZONES_Y',
            'REGIONAL_VARIATIONS_ENABLED', 'NUM_REGIONS_X', 'NUM_REGIONS_Y',
            'EPIDEMIC_ENABLED', 'EPIDEMIC_INTERVAL', 'EPIDEMIC_MIN_POPULATION_RATIO',
            'EPIDEMIC_AFFECTED_RATIO', 'EPIDEMIC_BASE_PROBABILITY',
            'DISEASE_TRANSMISSION_ENABLED', 'DISEASE_TRANSMISSION_DISTANCE', 'DISEASE_NAMES', 'NUM_DISEASE_TYPES',
            'INITIAL_AGENTS', 'FPS', 'NUMBER_OF_INITIAL_SPECIES', 'INITIAL_SAME_SPECIES_PERCENTAGE',
            'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE', 'HYBRID_FERTILITY_RATE',
            'MAX_SIMULTANEOUS_OFFSPRING', 'MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE',
            'DOMINANCE_MUTATION_RATE', 'SOMATIC_MUTATION_RATE', 'POINT_MUTATION_STDDEV',
            'LARGE_MUTATION_STDDEV', 'NN_TYPE', 'NN_HIDDEN_SIZE', 'NN_WEIGHT_INIT_STD',
            'NN_RECURRENT_IDENTITY_BIAS', 'NN_HIDDEN_NOISE_ENABLED', 'NN_HIDDEN_NOISE_STD',
            'N_STEP_MEMORY_ENABLED', 'N_STEP_MEMORY_DEPTH', 'SECTOR_COUNT', 'VISION_NOISE_STD',
            'STRESS_GAIN_RATE', 'STRESS_DECAY_RATE', 'STRESS_THREAT_WEIGHT', 'STRESS_RESOURCE_WEIGHT',
            'EFFORT_SPEED_SCALE', 'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE',
            'BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_THRESHOLD', 'REPRODUCTION_COST',
            'FOOD_ENERGY', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR',
            'BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_DRAIN_RATE', 'DRINK_RATE',
            'ATTACK_DISTANCE', 'ATTACK_DAMAGE_BASE', 'ATTACK_ENERGY_COST', 'KILL_ENERGY_GAIN',
            'CANNIBALISM_ENERGY_BONUS', 'MAX_SPEED_BASE', 'EATING_DISTANCE', 'MATING_DISTANCE',
            'WANDER_STRENGTH', 'STEER_STRENGTH', 'REPRODUCTION_COOLDOWN', 'MATE_SEARCH_RADIUS',
            'TRAIT_RANGES', 'TRAIT_DEFAULTS', 'ADVANCED_SIZE_EFFECTS_ENABLED',
            'SIZE_ATTACK_SCALING', 'SIZE_SPEED_PENALTY', 'SIZE_TURN_PENALTY', 'SIZE_METABOLIC_SCALING',
            'SIZE_PERCEPTION_BONUS', 'SUPERLINEAR_ENERGY_SCALING', 'ENERGY_SIZE_EXPONENT',
            'EFFORT_SIZE_INTERACTION', 'AGE_EFFECTS_ENABLED', 'AGE_PRIME_START', 'AGE_PRIME_END',
            'AGE_SPEED_DECLINE', 'AGE_STAMINA_DECLINE', 'AGE_EXPERIENCE_BONUS', 'AGE_REPRODUCTION_CURVE',
            'INTERNAL_STATE_MODULATION_ENABLED', 'LOW_ENERGY_ATTACK_PENALTY', 'LOW_HYDRATION_SPEED_PENALTY',
            'HIGH_STRESS_EFFORT_BOOST', 'EXHAUSTION_THRESHOLD', 'ACTION_COSTS_ENABLED',
            'COST_HIGH_SPEED_MULTIPLIER', 'COST_SHARP_TURN_MULTIPLIER', 'COST_PURSUIT_MULTIPLIER',
            'COST_ATTACK_BASE', 'COST_MATING_BASE', 'MORPHOLOGY_TRAITS_ENABLED', 'AGILITY_SPEED_BONUS',
            'AGILITY_STAMINA_COST', 'ARMOR_DAMAGE_REDUCTION', 'ARMOR_SPEED_PENALTY', 'ARMOR_ENERGY_COST',
            'SENSORY_NOISE_ENABLED', 'SENSOR_DROPOUT_RATE', 'INTERNAL_STATE_NOISE', 'PERCEPTION_LAG',
            'CONTEXT_SIGNALS_ENABLED', 'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY', 'TIME_SINCE_MATING_DECAY',
            'SOCIAL_PRESSURE_ENABLED', 'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD', 'CROWD_STRESS_RATE',
            'DOMINANCE_STRESS_FACTOR', 'RIVER_WIDTH', 'LAKE_SIZE_UNIFORM', 'LAKE_SIZE', 'LAKE_IRREGULARITY',
            'TREES_ENABLED', 'NUM_TREES', 'TREE_DENSITY', 'ENABLE_TREE_FOOD_SOURCES', 'TREE_FOOD_PROXIMITY',
            'TREE_FOOD_SPAWN_RATE', 'NUM_DISEASE_TYPES', 'NUM_WATER_SOURCES', 'WATER_SOURCE_RADIUS',
            # Environmental settings that affect the world but not individual agents
            'MAX_AGE', 'MATURITY_AGE', 'RANDOM_AGE_INITIALIZATION'
        }

        env_settings = {}
        agent_settings = {}

        for key, value in config.items():
            if key in environmental_keys:
                env_settings[key] = value
            else:
                agent_settings[key] = value

        return env_settings, agent_settings

    def select_configs(self, config_names: List[str]):
        """Select multiple configurations for the multiagent simulation."""
        self.selected_configs = config_names
        self.agent_configs = {}

        # Load all selected configs and separate environmental from agent settings
        all_env_settings = {}

        for config_name in config_names:
            full_config = self.load_config(config_name)
            env_settings, agent_settings = self.split_config(full_config)

            # Store agent-specific settings under the config name
            self.agent_configs[config_name] = agent_settings

            # Merge environmental settings (later configs override earlier ones for conflicts)
            all_env_settings.update(env_settings)

        # Override with any custom environmental settings if they exist
        if hasattr(self, 'custom_environmental_settings') and self.custom_environmental_settings:
            all_env_settings.update(self.custom_environmental_settings)

        self.environmental_settings = all_env_settings

        # Store custom names if they exist
        if hasattr(self, 'custom_names'):
            self.custom_names = getattr(self, 'custom_names', {})

    def get_merged_environmental_settings(self) -> Dict[str, Any]:
        """Get the merged environmental settings from all selected configs."""
        return self.environmental_settings.copy()

    def get_agent_config(self, config_name: str) -> Dict[str, Any]:
        """Get the agent-specific settings for a particular configuration."""
        return self.agent_configs.get(config_name, {}).copy()

    def get_all_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent configurations mapped by config name."""
        return self.agent_configs.copy()

    def get_selected_config_names(self) -> List[str]:
        """Get the names of all selected configurations."""
        return self.selected_configs[:]