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
        # Prioritize settings over config
        self.trait_ranges = self.settings.get('TRAIT_RANGES', config.TRAIT_RANGES)
        self.trait_defaults = self.settings.get('TRAIT_DEFAULTS', config.TRAIT_DEFAULTS)

        # Initialize temperature zones for geographic visualization only if enabled
        if (self.settings.get('TEMPERATURE_ENABLED', False) and
            self.settings.get('TEMPERATURE_ZONES_X', 2) > 0 and
            self.settings.get('TEMPERATURE_ZONES_Y', 2) > 0):
            self.temperature_zones = self._init_temperature_zones()
        else:
            self.temperature_zones = []

        # Initialize obstacles first (before population so food can check for trees)
        self.obstacle_list = []
        # Initialize border obstacles if enabled
        if self.settings.get('BORDER_ENABLED', True):
            world_width = self.settings['WORLD_WIDTH']
            world_height = self.settings['WORLD_HEIGHT']
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

        # Add trees if enabled
        if self.settings.get('TREES_ENABLED', True):
            # Determine number of trees based on either fixed count or density
            world_width = self.settings['WORLD_WIDTH']
            world_height = self.settings['WORLD_HEIGHT']
            if self.settings.get('TREE_DENSITY', 0) > 0:
                # Calculate number of trees based on density and world area
                world_area = world_width * world_height
                num_trees = int(self.settings.get('TREE_DENSITY', 0.0001) * world_area)
                # Limit to reasonable bounds
                num_trees = max(0, min(num_trees, 50))  # Cap at 50 trees to prevent excessive numbers
            else:
                num_trees = self.settings.get('NUM_TREES', 15)

            for _ in range(num_trees):
                # Random position with some padding from borders
                padding = 50
                pos = Vector2(
                    random.uniform(padding, world_width - padding - 40),
                    random.uniform(padding, world_height - padding - 40)
                )
                # Random size for the tree
                width = random.uniform(25, 50)
                height = random.uniform(40, 80)
                # Random tree type
                tree_types = ['deciduous', 'coniferous', 'palm']
                tree_type = random.choice(tree_types)
                # Random foliage color variation
                foliage_colors = [
                    (30, 100, 30),   # Green
                    (25, 85, 25),   # Darker green
                    (35, 110, 35),  # Lighter green
                    (40, 120, 40),  # Bright green
                ]
                foliage_color = random.choice(foliage_colors)
                self.obstacle_list.append(Obstacle(pos, width, height, 'tree', tree_type=tree_type, tree_foliage_color=foliage_color))

        # Add internal obstacles if enabled
        if self.settings.get('OBSTACLES_ENABLED', False):
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
        # Check if we're in multiagent mode (multiple agent configs specified)
        if 'MULTIAGENT_CONFIGS' in self.settings and self.settings['MULTIAGENT_CONFIGS']:
            # Multiagent mode: create agents based on multiple configurations
            configs = self.settings['MULTIAGENT_CONFIGS']
            num_configs = len(configs)

            # Calculate how many agents to create for each configuration
            agents_per_config = self.settings['INITIAL_AGENTS'] // num_configs
            remainder = self.settings['INITIAL_AGENTS'] % num_configs

            config_names = list(configs.keys())
            for i, config_name in enumerate(config_names):
                # Determine how many agents for this configuration (distribute remainder)
                num_agents_for_config = agents_per_config
                if i < remainder:
                    num_agents_for_config += 1

                # Get the specific configuration for this agent type
                agent_config = configs[config_name]

                # Create the specified number of agents with this configuration
                for _ in range(num_agents_for_config):
                    pos = Vector2.random_in_rect(self.settings['WORLD_WIDTH'], self.settings['WORLD_HEIGHT'])

                    # Create agent with specific configuration
                    agent = Agent.create_with_config(pos, self.settings, agent_config)
                    agent.world = self  # Set world reference for geographic temperature effects
                    self.agent_list.append(agent)
        else:
            # Single agent type mode (original behavior)
            for _ in range(self.settings['INITIAL_AGENTS']):
                pos = Vector2.random_in_rect(self.settings['WORLD_WIDTH'], self.settings['WORLD_HEIGHT'])
                agent = Agent.create_random(pos, self.settings)
                agent.world = self  # Set world reference for geographic temperature effects
                self.agent_list.append(agent)

        max_food = self.settings.get('MAX_FOOD', 400)  # Default from settings.py
        food_energy = self.settings.get('FOOD_ENERGY', config.FOOD_ENERGY)
        for _ in range(max_food):
            pos = self.food_clusters.get_spawn_position()
            # Only check if food is near tree if trees are enabled
            if self.settings.get('TREES_ENABLED', True):
                is_tree_food = self._is_position_near_tree(pos)
            else:
                is_tree_food = False
            self.food_list.append(Food(pos, food_energy, is_tree_food=is_tree_food))





    def _is_position_near_tree(self, pos):
        """Check if a position is near a tree to determine if food is tree food."""
        # Only check for trees if they are enabled
        if not self.settings.get('TREES_ENABLED', True):
            return False

        tree_proximity = self.settings.get('TREE_FOOD_PROXIMITY', 30.0)
        for obstacle in self.obstacle_list:
            if obstacle.obstacle_type == 'tree':
                # Calculate distance from position to tree center
                tree_center_x = obstacle.pos.x + obstacle.width / 2
                tree_center_y = obstacle.pos.y + obstacle.height / 2
                distance = math.sqrt((pos.x - tree_center_x)**2 + (pos.y - tree_center_y)**2)
                if distance <= tree_proximity:
                    return True
        return False


    def _init_water(self):
        for _ in range(self.settings['NUM_WATER_SOURCES']):
            pos = Vector2(
                random.uniform(50, self.settings['WORLD_WIDTH'] - 50),
                random.uniform(50, self.settings['WORLD_HEIGHT'] - 50)
            )
            # Create irregular lake instead of simple circular water source
            # Use the lake generation method to create an irregular water body
            from src.systems.terrain_generator import TerrainGenerator
            world_width = self.settings['WORLD_WIDTH']
            world_height = self.settings['WORLD_HEIGHT']

            # Calculate position ratios based on the position
            center_x_ratio = pos.x / world_width
            center_y_ratio = pos.y / world_height

            # Use a smaller size for water sources compared to lakes
            size_ratio = self.settings.get('WATER_SOURCE_RADIUS', 40.0) / min(world_width, world_height) * 2.5

            # Create irregular lake at this position
            lake_obstacles = TerrainGenerator.generate_lake(
                world_width, world_height,
                center_x_ratio=center_x_ratio,
                center_y_ratio=center_y_ratio,
                size_ratio=size_ratio,
                irregularity=self.settings.get('LAKE_IRREGULARITY', 0.4),
                settings=self.settings
            )

            # Add the lake obstacles to the obstacle list
            self.obstacle_list.extend(lake_obstacles)

            # Still add the original water source for drinking mechanics
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
        # Use settings values with fallback to config
        max_food = self.settings.get('MAX_FOOD', 400)  # Default value from settings.py
        food_spawn_rate = self.settings.get('FOOD_SPAWN_RATE', config.FOOD_SPAWN_RATE)
        tree_food_spawn_rate = self.settings.get('TREE_FOOD_SPAWN_RATE', 15)  # Default tree food spawn rate
        food_energy = self.settings.get('FOOD_ENERGY', config.FOOD_ENERGY)

        alive_food = len(self.food_list)
        if alive_food < max_food:
            # Calculate how many foods to spawn normally
            normal_food_to_spawn = max(0, int(food_spawn_rate * dt))

            # Calculate how many foods to spawn near trees (if enabled)
            tree_food_to_spawn = 0
            if self.settings.get('ENABLE_TREE_FOOD_SOURCES', True):
                tree_food_to_spawn = max(0, int(tree_food_spawn_rate * dt * 0.3))  # 30% of tree food rate for balance

            # Total food to spawn
            total_to_spawn = normal_food_to_spawn + tree_food_to_spawn
            remaining_space = max_food - alive_food
            to_spawn = min(total_to_spawn, remaining_space)

            # Separate counters for regular and tree food
            regular_food_count = 0
            tree_food_count = 0

            # Calculate approximate split based on intended rates
            if total_to_spawn > 0 and (normal_food_to_spawn + tree_food_to_spawn) > 0:
                tree_food_ratio = tree_food_to_spawn / (normal_food_to_spawn + tree_food_to_spawn)
                tree_food_count = int(to_spawn * tree_food_ratio)
                regular_food_count = to_spawn - tree_food_count
            else:
                regular_food_count = to_spawn  # Default to regular food if tree food is disabled

            # Spawn regular food
            for _ in range(regular_food_count):
                pos = self.food_clusters.get_spawn_position()
                is_tree_food = self._is_position_near_tree(pos)
                self.food_list.append(Food(pos, food_energy, is_tree_food=is_tree_food))

            # Spawn tree food
            for _ in range(tree_food_count):
                # Only spawn tree food if trees are enabled
                if self.settings.get('TREES_ENABLED', True):
                    # Find a random tree
                    trees = [obs for obs in self.obstacle_list if obs.obstacle_type == 'tree']
                    if trees:
                        tree = random.choice(trees)
                        # Spawn food near the tree
                        proximity = self.settings.get('TREE_FOOD_PROXIMITY', 30.0)
                        angle = random.uniform(0, 2 * math.pi)
                        distance = random.uniform(5, proximity)
                        pos = Vector2(
                            tree.pos.x + tree.width/2 + math.cos(angle) * distance,
                            tree.pos.y + tree.height/2 + math.sin(angle) * distance
                        )
                        # Make sure the position is within bounds
                        pos.x = max(10, min(self.settings['WORLD_WIDTH'] - 10, pos.x))
                        pos.y = max(10, min(self.settings['WORLD_HEIGHT'] - 10, pos.y))
                        is_tree_food = True
                    else:
                        pos = self.food_clusters.get_spawn_position()
                        is_tree_food = False
                else:
                    pos = self.food_clusters.get_spawn_position()
                    is_tree_food = False

                self.food_list.append(Food(pos, food_energy, is_tree_food=is_tree_food))

    def add_agent(self, agent):
        self.agent_list.append(agent)
        # Set the world reference for the agent to enable geographic temperature effects
        agent.world = self
