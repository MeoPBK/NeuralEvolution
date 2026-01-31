"""
Configuration Manager for the Evolutionary Simulation

This module provides a unified configuration system that resolves inconsistencies
between config.py and settings.py while preserving all UI functionality.
"""

import config as config_module
from settings import SETTINGS as settings_module_settings
import os
import json


class ConfigManager:
    """
    Manages configuration with clear precedence: settings take precedence over config
    but defaults come from config when not specified in settings.
    """

    def __init__(self):
        # Start with config defaults
        self._config_values = self._get_config_defaults()

        # Override with settings values
        self._apply_settings_overrides()

        # Store available configurations
        self._available_configs = self._load_available_configs()

        # Selected configurations for multiagent mode
        self._selected_configs = []

    def _get_config_defaults(self):
        """Extract all config values from the config module."""
        config_values = {}

        # Get all attributes from config module that are not private
        for attr_name in dir(config_module):
            if not attr_name.startswith('_'):
                attr_value = getattr(config_module, attr_name)
                config_values[attr_name] = attr_value

        return config_values

    def _load_available_configs(self):
        """Load available configuration files from the configs directory."""
        configs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'configs')
        available_configs = []

        if os.path.exists(configs_dir):
            for filename in os.listdir(configs_dir):
                if filename.endswith('.json'):
                    config_name = filename[:-5]  # Remove .json extension
                    available_configs.append(config_name)

        # Add default configurations if none exist
        if not available_configs:
            available_configs = ['Default_Config', 'Aggressive_Agents', 'Passive_Agents', 'Balanced_Agents']

        return available_configs

    def get_available_configs(self):
        """Get list of available configuration names."""
        return self._available_configs

    def select_configs(self, config_names):
        """Select configurations for multiagent mode."""
        self._selected_configs = config_names

    def get_selected_configs(self):
        """Get the names of selected configurations."""
        return self._selected_configs

    def load_config(self, config_name):
        """Load a specific configuration from file."""
        configs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'configs')
        config_path = os.path.join(configs_dir, f"{config_name}.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading configuration {config_name}: {e}")
                return {}
        else:
            # Return empty dict if config doesn't exist
            return {}

    def get_all_agent_configs(self):
        """Get all selected agent configurations for multiagent mode."""
        configs = {}
        for config_name in self._selected_configs:
            full_config = self.load_config(config_name)
            configs[config_name] = full_config
        return configs
    
    def _apply_settings_overrides(self):
        """Apply settings values to override config defaults where applicable."""
        # Apply settings values to override config defaults
        for key, value in settings_module_settings.items():
            # Convert key to uppercase to match config format
            upper_key = key.upper()
            
            # Only apply if the key exists in config or it's a known settings-only key
            if upper_key in self._config_values or self._is_settings_only_key(upper_key):
                self._config_values[key] = value
                if upper_key in self._config_values:  # Also update the uppercase version
                    self._config_values[upper_key] = value
    
    def _is_settings_only_key(self, key):
        """Check if a key is specific to settings (not in config)."""
        settings_only_keys = {
            'INITIAL_AGENTS', 'MAX_FOOD', 'SOMATIC_MUTATION_RATE', 
            'NN_HIDDEN_SIZE', 'NN_RECURRENT_IDENTITY_BIAS', 'NN_HIDDEN_NOISE_ENABLED',
            'NN_HIDDEN_NOISE_STD', 'N_STEP_MEMORY_ENABLED', 'N_STEP_MEMORY_DEPTH',
            'SECTOR_COUNT', 'STRESS_GAIN_RATE', 'STRESS_DECAY_RATE',
            'STRESS_THREAT_WEIGHT', 'STRESS_RESOURCE_WEIGHT', 'EFFORT_SPEED_SCALE',
            'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE', 'MAX_AGE',
            'CANNIBALISM_ENERGY_BONUS', 'TEMPERATURE_ENABLED',
            'RANDOM_AGE_INITIALIZATION', 'EPIDEMIC_ENABLED', 'EPIDEMIC_INTERVAL',
            'EPIDEMIC_MIN_POPULATION_RATIO', 'EPIDEMIC_AFFECTED_RATIO',
            'EPIDEMIC_BASE_PROBABILITY', 'INITIAL_SAME_SPECIES_PERCENTAGE',
            'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE',
            'HYBRID_FERTILITY_RATE', 'MAX_SIMULTANEOUS_OFFSPRING',
            'DISEASE_TRANSMISSION_ENABLED', 'DISEASE_TRANSMISSION_DISTANCE',
            'DISEASE_NAMES', 'NUM_DISEASE_TYPES', 'NUMBER_OF_INITIAL_SPECIES',
            'REGIONAL_VARIATIONS_ENABLED', 'NUM_REGIONS_X', 'NUM_REGIONS_Y',
            'REGION_SPEED_MODIFIER', 'REGION_SIZE_MODIFIER', 'REGION_AGGRESSION_MODIFIER',
            'REGION_EFFICIENCY_MODIFIER', 'OBSTACLES_ENABLED', 'BORDER_ENABLED',
            'BORDER_WIDTH', 'NUM_INTERNAL_OBSTACLES', 'ADVANCED_SIZE_EFFECTS_ENABLED',
            'SIZE_ATTACK_SCALING', 'SIZE_SPEED_PENALTY', 'SIZE_TURN_PENALTY',
            'SIZE_METABOLIC_SCALING', 'SIZE_PERCEPTION_BONUS', 'SUPERLINEAR_ENERGY_SCALING',
            'ENERGY_SIZE_EXPONENT', 'EFFORT_SIZE_INTERACTION', 'AGE_EFFECTS_ENABLED',
            'AGE_PRIME_START', 'AGE_PRIME_END', 'AGE_SPEED_DECLINE', 'AGE_STAMINA_DECLINE',
            'AGE_EXPERIENCE_BONUS', 'AGE_REPRODUCTION_CURVE', 'INTERNAL_STATE_MODULATION_ENABLED',
            'LOW_ENERGY_ATTACK_PENALTY', 'LOW_HYDRATION_SPEED_PENALTY', 'HIGH_STRESS_EFFORT_BOOST',
            'EXHAUSTION_THRESHOLD', 'ACTION_COSTS_ENABLED', 'COST_HIGH_SPEED_MULTIPLIER',
            'COST_SHARP_TURN_MULTIPLIER', 'COST_PURSUIT_MULTIPLIER', 'COST_ATTACK_BASE',
            'COST_MATING_BASE', 'MORPHOLOGY_TRAITS_ENABLED', 'AGILITY_SPEED_BONUS',
            'AGILITY_STAMINA_COST', 'ARMOR_DAMAGE_REDUCTION', 'ARMOR_SPEED_PENALTY',
            'ARMOR_ENERGY_COST', 'SENSORY_NOISE_ENABLED', 'SENSOR_DROPOUT_RATE',
            'INTERNAL_STATE_NOISE', 'PERCEPTION_LAG', 'CONTEXT_SIGNALS_ENABLED',
            'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY', 'TIME_SINCE_MATING_DECAY',
            'SOCIAL_PRESSURE_ENABLED', 'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD',
            'CROWD_STRESS_RATE', 'DOMINANCE_STRESS_FACTOR', 'VIRUS_RESISTANCE',
            'AGILITY', 'ARMOR', 'SEX', 'TRAIT_RANGES', 'TRAIT_DEFAULTS'
        }
        return key in settings_only_keys
    
    def get(self, key, default=None):
        """Get a configuration value with optional default."""
        return self._config_values.get(key, default)
    
    def get_all(self):
        """Get all configuration values as a dictionary."""
        return self._config_values.copy()
    
    def update_settings(self, settings_dict):
        """Update configuration with new settings values."""
        for key, value in settings_dict.items():
            # Convert to both formats to maintain consistency
            upper_key = key.upper()
            self._config_values[key] = value
            self._config_values[upper_key] = value


# Global configuration manager instance
_config_manager = ConfigManager()


def get_config(key, default=None):
    """Get a configuration value."""
    return _config_manager.get(key, default)


def get_all_config():
    """Get all configuration values."""
    return _config_manager.get_all()


def update_config_with_settings(settings_dict):
    """Update the configuration with new settings."""
    _config_manager.update_settings(settings_dict)


# Backwards compatibility - expose the same interface as the original config
def __getattr__(name):
    """Provide backwards compatibility with the original config module."""
    return _config_manager.get(name)