import random
from src.utils.vector import Vector2
from src.entities.agent import Agent
from src.entities.food import Food
from src.entities.water import WaterSource
from src.entities.obstacle import Obstacle
from src.core.spatial_grid import SpatialGrid
from src.systems.food_clusters import FoodClusterManager
import math
import config


class World:
    def __init__(self, settings):
        self.settings = settings
        self.agent_list = []
        self.food_list = []
        self.water_list = []

        self.agent_grid = SpatialGrid(self.settings['WORLD_WIDTH'], self.settings['WORLD_HEIGHT'], self.settings['GRID_CELL_SIZE'])
        self.food_grid = SpatialGrid(self.settings['WORLD_WIDTH'], self.settings['WORLD_HEIGHT'], self.settings['GRID_CELL_SIZE'])

        self.food_clusters = FoodClusterManager(self.settings)

        # Set up trait ranges and defaults from settings or config
        self.trait_ranges = self.settings.get('TRAIT_RANGES', config.TRAIT_RANGES)
        self.trait_defaults = self.settings.get('TRAIT_DEFAULTS', config.TRAIT_DEFAULTS)

        # Initialize temperature zones for geographic visualization only if enabled
        if (self.settings.get('TEMPERATURE_ENABLED', False) and
            self.settings.get('TEMPERATURE_ZONES_X', 2) > 0 and
            self.settings.get('TEMPERATURE_ZONES_Y', 2) > 0):
            self.temperature_zones = self._init_temperature_zones()
        else:
            self.temperature_zones = []

        self._init_population()
        self._init_water()

    def _init_temperature_zones(self):
        """Initialize temperature zones for geographic visualization."""
        # Create temperature zones based on settings
        num_temp_zones_x = self.settings.get('TEMPERATURE_ZONES_X', 4)  # 4 temperature zones horizontally
        num_temp_zones_y = self.settings.get('TEMPERATURE_ZONES_Y', 3)  # 3 temperature zones vertically

        # Handle case where zones are disabled (zero zones)
        if num_temp_zones_x <= 0 or num_temp_zones_y <= 0:
            return []

        world_width = self.settings['WORLD_WIDTH']
        world_height = self.settings['WORLD_HEIGHT']

        zone_width = world_width / num_temp_zones_x
        zone_height = world_height / num_temp_zones_y

        temperature_zones = []

        for y in range(num_temp_zones_y):
            for x in range(num_temp_zones_x):
                # Calculate zone boundaries
                left = x * zone_width
                top = y * zone_height
                right = (x + 1) * zone_width
                bottom = (y + 1) * zone_height

                # Generate a temperature value for this zone (hotter zones will be redder, cooler bluer)
                # Use a pattern that creates variation across the world
                temp_base = 20.0  # Base temperature
                # Use a smoother pattern for more gradual transitions
                temp_variation = 10.0 * math.sin(2 * math.pi * x / num_temp_zones_x) * math.cos(2 * math.pi * y / num_temp_zones_y)
                temperature = temp_base + temp_variation

                zone_info = {
                    'bounds': (left, top, right, bottom),
                    'temperature': temperature,
                    'color_offset': (int(20 * (temperature / 30.0)), int(-20 * (temperature / 30.0)), 0)  # Red offset for hot, blue for cold
                }
                temperature_zones.append(zone_info)

        return temperature_zones

    def get_temperature_at_position(self, pos):
        """Get the temperature at a specific position using smooth interpolation."""
        # If temperature zones are disabled, return a default temperature
        if not self.temperature_zones:
            return 20.0  # Default temperature when zones are disabled

        world_width = self.settings['WORLD_WIDTH']
        world_height = self.settings['WORLD_HEIGHT']

        # Normalize position to 0-1 range
        norm_x = pos.x / world_width
        norm_y = pos.y / world_height

        # Use trigonometric functions for smooth temperature variation across the world
        temp_base = 20.0  # Base temperature
        temp_variation = 10.0 * math.sin(2 * math.pi * norm_x) * math.cos(2 * math.pi * norm_y)
        temperature = temp_base + temp_variation

        return temperature

    def get_zone_at_position(self, pos):
        """Get the temperature zone at a given position."""
        for zone in self.temperature_zones:
            left, top, right, bottom = zone['bounds']
            if left <= pos.x < right and top <= pos.y < bottom:
                return zone
        return None

    def _init_population(self):
        for _ in range(self.settings['INITIAL_AGENTS']):
            pos = Vector2.random_in_rect(self.settings['WORLD_WIDTH'], self.settings['WORLD_HEIGHT'])
            agent = Agent.create_random(pos, self.settings)
            agent.world = self  # Set world reference for geographic temperature effects
            self.agent_list.append(agent)

        for _ in range(self.settings['MAX_FOOD']):
            pos = self.food_clusters.get_spawn_position()
            self.food_list.append(Food(pos, self.settings['FOOD_ENERGY']))

        # Initialize obstacles if enabled
        self.obstacle_list = []
        if self.settings.get('OBSTACLES_ENABLED', False):
            self._init_obstacles()


    def _init_obstacles(self):
        """Initialize obstacles in the world."""
        world_width = self.settings['WORLD_WIDTH']
        world_height = self.settings['WORLD_HEIGHT']

        # Add border obstacles if enabled
        if self.settings.get('BORDER_ENABLED', True):
            border_width = self.settings.get('BORDER_WIDTH', 10)

            # Top border
            self.obstacle_list.append(Obstacle(Vector2(0, 0), world_width, border_width, 'wall'))
            # Bottom border
            self.obstacle_list.append(Obstacle(Vector2(0, world_height - border_width), world_width, border_width, 'wall'))
            # Left border
            self.obstacle_list.append(Obstacle(Vector2(0, border_width), border_width, world_height - 2 * border_width, 'wall'))
            # Right border
            self.obstacle_list.append(Obstacle(Vector2(world_width - border_width, border_width),
                                             border_width, world_height - 2 * border_width, 'wall'))

        # Add internal obstacles
        num_internal_obstacles = self.settings.get('NUM_INTERNAL_OBSTACLES', 5)
        for _ in range(num_internal_obstacles):
            # Random position with some padding from borders
            padding = 50
            pos = Vector2(
                random.uniform(padding, world_width - padding - 50),
                random.uniform(padding, world_height - padding - 50)
            )
            # Random size for the obstacle
            width = random.uniform(20, 100)
            height = random.uniform(20, 100)
            # Random obstacle type
            obstacle_types = ['wall', 'mountain', 'cliff']
            obstacle_type = random.choice(obstacle_types)
            self.obstacle_list.append(Obstacle(pos, width, height, obstacle_type))


    def _init_water(self):
        for _ in range(self.settings['NUM_WATER_SOURCES']):
            pos = Vector2(
                random.uniform(50, self.settings['WORLD_WIDTH'] - 50),
                random.uniform(50, self.settings['WORLD_HEIGHT'] - 50)
            )
            self.water_list.append(WaterSource(pos, self.settings['WATER_SOURCE_RADIUS']))

    def rebuild_grids(self):
        self.agent_grid.clear()
        self.food_grid.clear()

        for a in self.agent_list:
            if a.alive:
                self.agent_grid.insert(a)
        for f in self.food_list:
            if f.alive:
                self.food_grid.insert(f)

    def cleanup(self):
        """Remove dead entities."""
        # Remove world reference from dying agents to prevent memory leaks
        for agent in self.agent_list:
            if not agent.alive:
                agent.world = None
        self.agent_list = [a for a in self.agent_list if a.alive]
        self.food_list = [f for f in self.food_list if f.alive]
        # Note: Obstacles are persistent and don't die, so no need to filter them

    def spawn_food(self, dt):
        """Spawn food up to MAX_FOOD using cluster positions."""
        alive_food = len(self.food_list)
        if alive_food < self.settings['MAX_FOOD']:
            to_spawn = min(int(self.settings['FOOD_SPAWN_RATE'] * dt) + 1, self.settings['MAX_FOOD'] - alive_food)
            for _ in range(to_spawn):
                pos = self.food_clusters.get_spawn_position()
                self.food_list.append(Food(pos, self.settings['FOOD_ENERGY']))

    def add_agent(self, agent):
        self.agent_list.append(agent)
        # Set the world reference for the agent to enable geographic temperature effects
        agent.world = self
