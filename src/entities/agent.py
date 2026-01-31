import random
import math
import pygame
import weakref
from src.utils.vector import Vector2
from src.genetics.genome import Genome
from src.genetics.phenotype import compute_phenotype
from src.nn.brain_phenotype import build_brain, get_brain_weight_count
from src.nn.rnn_brain import RecurrentBrain
import config


class Agent:
    _next_id = 0

    def __init__(self, pos, genome, generation=0, trait_ranges=None, settings=None):
        Agent._next_id += 1
        self.id = Agent._next_id
        self.pos = pos
        self.velocity = Vector2.random_unit() * 0.5
        self.genome = genome
        self.phenotype = compute_phenotype(genome, trait_ranges or config.TRAIT_RANGES)

        # Get neural network type from settings
        nn_type = settings.get('NN_TYPE', 'FNN') if settings else config.NN_TYPE
        self.nn_type = nn_type
        self.brain = build_brain(genome, nn_type, settings)

        self.energy = config.BASE_ENERGY
        self.hydration = config.BASE_HYDRATION
        self.age = 0.0
        self.generation = generation
        self.alive = True
        self.reproduction_cooldown = 0.0
        self.somatic_mutation_timer = 0.0
        self.total_mutations = 0  # Track total mutations for visualization

        # NN outputs (updated each tick by movement system) - V2 Architecture
        self.attack_intent = 0.0  # Legacy compatibility
        self.mate_desire = 0.0
        self.avoid_drive = 0.0    # V2: Flee/avoidance tendency
        self.attack_drive = 0.0   # V2: Attack tendency
        self.effort = 0.5         # V2: Energy expenditure level

        # Internal state (V2 Architecture)
        self.stress = 0.0         # Arousal/stress level (0-1)
        self.recent_damage = 0.0  # Recent damage received (for stress calculation)
        self.memory_buffer = None # N-step memory buffer (created by movement system if enabled)

        # Advanced modulation state
        self.current_modifiers = {}  # Modifiers from advanced features (set by movement system)
        self._last_velocity = None   # For sharp turn detection in energy costs

        # Store last neural network inputs and outputs for visualization
        self.last_nn_inputs = [0.0] * 24  # V2: 24 sector-based inputs
        self.last_nn_outputs = [0.0] * 6  # V2: 6 outputs
        self.last_hidden_activations = [0.0] * 8  # V2: 8 hidden neurons

        # Species information
        self.species_id = 0  # Will be set during initialization based on genetic similarity
        self.genetic_similarity_score = 1.0  # Measure of genetic similarity to original species
        self.shape_type = self._determine_shape_type()  # Determine shape based on species

        # Mutation tracking
        self.dominant_mutations = []  # Track significant mutations that define the agent
        self.mutation_history = []  # Track all mutations over the agent's lifetime

        # Dietary behavior tracking
        self.dietary_classification = 'omnivore'  # Default classification
        self.hunting_success_rate = 0.0  # Track success in hunting other agents
        self.herding_behavior = 0.0  # Track tendency to stay near food sources
        self.carnivorous_tendency = 0.0  # Track tendency towards aggressive/attacking behavior
        self.herbivorous_tendency = 0.0  # Track tendency towards peaceful/foraging behavior

        # Geographic region tracking - calculate after position is set
        self.region = 0  # Initialize to 0, will be updated after position is properly set
        # Initialize with default trait modifiers to avoid issues during construction
        self.region_trait_modifiers = {
            'speed': 1.0,
            'size': 1.0,
            'aggression': 1.0,
            'energy_efficiency': 1.0,
            'vision_range': 1.0,
            'reproduction_urge': 1.0,
            'camouflage': 1.0,
            'max_age': 1.0,
            'virus_resistance': 1.0,
        }

        # Initialize water speed based on habitat preference
        self._update_water_speed()

        # Store world reference as a weak reference to prevent circular references
        self._world_ref = None

        # Disease/infection tracking
        self.infected = False  # Whether the agent is currently infected
        self.infection_timer = 0.0  # Timer for infection effects/duration
        self.current_disease = None  # Name of the current disease affecting the agent
        self.disease_resistances = {  # Genetic resistances to different diseases
            'Flu': self.phenotype.get('disease_resistance_1', 0.5),
            'Plague': self.phenotype.get('disease_resistance_2', 0.5),
            'Malaria': self.phenotype.get('disease_resistance_3', 0.5),
            'Pox': self.phenotype.get('disease_resistance_4', 0.5)
        }
        self.disease_recovery_rates = {  # How quickly agents recover from different diseases
            'Flu': 0.05,      # Faster recovery
            'Plague': 0.02,   # Slower recovery, more severe
            'Malaria': 0.03,  # Moderate recovery time
            'Pox': 0.04       # Moderate recovery time
        }

        # Fixed color based on genetic makeup - calculated once at initialization
        self.base_color = self._calculate_base_color()

        # Offspring tracking
        self.offspring_count = 0  # Count of successful reproductions

        # Water exposure tracking
        self.time_in_water = 0.0  # Time spent continuously in water
        self.is_in_water = False  # Whether currently in water

        # Random diet and habitat assignment if enabled in settings
        if settings:
            if settings.get('RANDOMIZE_DIET_TYPE', False):
                import random
                # Randomly assign diet type (0.0 to 2.0)
                self.phenotype['diet_type'] = random.uniform(0.0, 2.0)
            if settings.get('RANDOMIZE_HABITAT_PREF', False):
                import random
                # Randomly assign habitat preference (0.0 to 2.0)
                self.phenotype['habitat_preference'] = random.uniform(0.0, 2.0)

    def _determine_region(self, settings=None):
        """Determine which geographic region the agent is in based on position."""
        # Use settings to determine number of regions, default to 2x2 if not specified
        if settings:
            num_regions_x = settings.get('NUM_REGIONS_X', 2)
            num_regions_y = settings.get('NUM_REGIONS_Y', 2)
            world_width = settings.get('WORLD_WIDTH', config.WORLD_WIDTH)
            world_height = settings.get('WORLD_HEIGHT', config.WORLD_HEIGHT)
        else:
            num_regions_x = 2
            num_regions_y = 2
            world_width = config.WORLD_WIDTH
            world_height = config.WORLD_HEIGHT

        # Calculate region based on position and number of regions
        region_width = world_width / num_regions_x if num_regions_x > 0 else world_width
        region_height = world_height / num_regions_y if num_regions_y > 0 else world_height

        # Ensure position values are valid numbers
        x_pos = getattr(self.pos, 'x', 0)
        y_pos = getattr(self.pos, 'y', 0)

        x_region = min(num_regions_x - 1, max(0, int(x_pos // region_width))) if region_width > 0 else 0
        y_region = min(num_regions_y - 1, max(0, int(y_pos // region_height))) if region_height > 0 else 0

        # Convert 2D region index to 1D
        return x_region + y_region * num_regions_x

    def _get_region_trait_modifiers(self, settings=None):
        """Get trait modifiers based on the current region."""
        # Use settings to determine region modifiers if available
        if settings and settings.get('REGIONAL_VARIATIONS_ENABLED', True):
            # Get the region-specific modifiers from settings, ensuring we don't exceed array bounds
            speed_modifiers = self._parse_or_get_default(settings.get('REGION_SPEED_MODIFIER', [1.1, 0.9, 1.0, 1.2]))
            region_index = min(self.region, len(speed_modifiers) - 1) if len(speed_modifiers) > 0 else 0
            speed_modifier = speed_modifiers[region_index] if 0 <= region_index < len(speed_modifiers) else 1.0

            size_modifiers = self._parse_or_get_default(settings.get('REGION_SIZE_MODIFIER', [0.9, 1.1, 1.0, 0.8]))
            region_index = min(self.region, len(size_modifiers) - 1) if len(size_modifiers) > 0 else 0
            size_modifier = size_modifiers[region_index] if 0 <= region_index < len(size_modifiers) else 1.0

            aggression_modifiers = self._parse_or_get_default(settings.get('REGION_AGGRESSION_MODIFIER', [1.2, 0.8, 1.0, 1.3]))
            region_index = min(self.region, len(aggression_modifiers) - 1) if len(aggression_modifiers) > 0 else 0
            aggression_modifier = aggression_modifiers[region_index] if 0 <= region_index < len(aggression_modifiers) else 1.0

            efficiency_modifiers = self._parse_or_get_default(settings.get('REGION_EFFICIENCY_MODIFIER', [0.95, 1.05, 1.0, 0.85]))
            region_index = min(self.region, len(efficiency_modifiers) - 1) if len(efficiency_modifiers) > 0 else 0
            efficiency_modifier = efficiency_modifiers[region_index] if 0 <= region_index < len(efficiency_modifiers) else 1.0

            # Create a modifier for the current region
            return {
                'speed': float(speed_modifier) if isinstance(speed_modifier, (int, float)) else 1.0,
                'size': float(size_modifier) if isinstance(size_modifier, (int, float)) else 1.0,
                'aggression': float(aggression_modifier) if isinstance(aggression_modifier, (int, float)) else 1.0,
                'energy_efficiency': float(efficiency_modifier) if isinstance(efficiency_modifier, (int, float)) else 1.0,
                # Add default 1.0 for other traits that don't have regional modifiers
                'vision_range': 1.0,
                'reproduction_urge': 1.0,
                'camouflage': 1.0,
                'max_age': 1.0,
                'virus_resistance': 1.0,
            }
        else:
            # Default to no regional modifications if disabled
            return {
                'speed': 1.0,
                'size': 1.0,
                'aggression': 1.0,
                'energy_efficiency': 1.0,
                'vision_range': 1.0,
                'reproduction_urge': 1.0,
                'camouflage': 1.0,
                'max_age': 1.0,
                'virus_resistance': 1.0,
            }

    def _parse_or_get_default(self, value):
        """Parse a value that might be a string representation of a list, or return as-is."""
        if isinstance(value, str):
            try:
                import ast
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                # If parsing fails, return default
                return [1.0, 1.0, 1.0, 1.0]  # Default to neutral modifiers
        return value

    def update_region(self, settings=None):
        """Update the agent's region and trait modifiers if it has moved to a new region."""
        old_region = self.region
        self.region = self._determine_region(settings)

        if self.region != old_region or settings is not None:
            self.region_trait_modifiers = self._get_region_trait_modifiers(settings)

    def get_modified_trait(self, trait_name):
        """Get a trait value modified by regional effects."""
        base_value = self.phenotype.get(trait_name, 1.0)
        modifier = self.region_trait_modifiers.get(trait_name, 1.0)
        return base_value * modifier

    @staticmethod
    def create_random(pos, settings=None):
        genome = Genome.create_random()
        trait_ranges = settings.get('TRAIT_RANGES', config.TRAIT_RANGES) if settings else config.TRAIT_RANGES
        agent = Agent(pos, genome, generation=0, trait_ranges=trait_ranges, settings=settings)
        # Use settings to initialize energy and hydration if provided
        if settings:
            agent.energy = settings.get('BASE_ENERGY', config.BASE_ENERGY)
            agent.hydration = settings.get('BASE_HYDRATION', config.BASE_HYDRATION)
            # Initialize with random age if option is enabled
            if settings.get('RANDOM_AGE_INITIALIZATION', False):
                # Set age to a random value between 0 and MAX_AGE
                agent.age = random.uniform(0, settings.get('MAX_AGE', 70.0))

            # Initialize species information based on settings
            # For initial population, distribute among specified number of species
            num_initial_species = settings.get('NUMBER_OF_INITIAL_SPECIES', 1)

            if num_initial_species <= 1:
                # If only one species, assign to main species (species_id = 0)
                agent.species_id = 0
                agent.genetic_similarity_score = 1.0
            else:
                # Distribute agents among multiple species
                # Assign to a random species ID from 0 to num_initial_species-1
                agent.species_id = random.randint(0, num_initial_species - 1)
                # Set genetic similarity based on how different this species is from the base
                agent.genetic_similarity_score = 1.0 - (agent.species_id / num_initial_species) * 0.3  # Slight genetic differences between species
        else:
            # Default to main species if no settings provided
            agent.species_id = 0
            agent.genetic_similarity_score = 1.0

        # Update the shape type based on the assigned species ID
        agent.shape_type = agent._determine_shape_type()

        # Now that the agent is fully initialized, calculate its region
        agent.region = agent._determine_region(settings)
        # Update the region trait modifiers based on the calculated region
        agent.region_trait_modifiers = agent._get_region_trait_modifiers(settings)

        return agent

    def calculate_genetic_similarity(self, other_agent):
        """Calculate genetic similarity between this agent and another agent."""
        # Compare genes in the genome to determine similarity
        # This is a simplified approach - in a real implementation, we'd compare actual gene values
        similarity = 0.0
        count = 0

        # Compare genes in both genomes
        for gene_a in self.genome.all_genes():
            for gene_b in other_agent.genome.all_genes():
                if gene_a.name == gene_b.name:
                    # Compare the two alleles of each gene
                    # For simplicity, we'll compare the expressed values
                    similarity += abs(gene_a.express() - gene_b.express())
                    count += 1
                    break

        if count > 0:
            # Normalize and invert so that lower differences mean higher similarity
            avg_diff = similarity / count
            # Convert to similarity score (higher values mean more similar)
            # Using exponential decay to map differences to similarity scores
            genetic_similarity = math.exp(-avg_diff * 2.0)  # Adjust multiplier as needed
        else:
            # If no comparable genes, return 0 similarity
            genetic_similarity = 0.0

        return genetic_similarity

    def is_same_species_as(self, other_agent, settings=None):
        """Check if this agent is the same species as another agent."""
        if settings is None:
            from src import config
            settings = config.SETTINGS  # Use default settings if none provided

        threshold = settings.get('SPECIES_GENETIC_SIMILARITY_THRESHOLD', 0.8)
        genetic_similarity = self.calculate_genetic_similarity(other_agent)

        return genetic_similarity >= threshold

    def update_dietary_behavior(self, attack_successful=False, ate_food=False):
        """Update dietary behavior based on recent actions."""
        # Update carnivorous tendency based on attack intent and success
        if self.attack_intent > 0.5:  # Agent is trying to attack
            self.carnivorous_tendency += 0.01
            if attack_successful:
                self.hunting_success_rate += 0.05
        elif self.attack_intent < -0.5:  # Agent is trying to flee
            self.herbivorous_tendency += 0.005

        # Update herbivorous tendency based on food consumption
        if ate_food:
            self.herbivorous_tendency += 0.02

        # Update classification based on tendencies
        if self.carnivorous_tendency > self.herbivorous_tendency * 2:
            self.dietary_classification = 'carnivore'
        elif self.herbivorous_tendency > self.carnivorous_tendency * 2:
            self.dietary_classification = 'herbivore'
        else:
            self.dietary_classification = 'omnivore'

    def _update_water_speed(self):
        """Update the water speed based on habitat preference and genetic traits."""
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)

        if habitat_pref < 0.7:  # Aquatic
            self.water_speed = self.phenotype.get('speed_in_water_aquatic', 5.0)
        elif habitat_pref > 1.3:  # Terrestrial
            self.water_speed = self.phenotype.get('speed_in_water_terrestrial', 1.0)
        else:  # Amphibious
            self.water_speed = self.phenotype.get('speed_in_water_amphibious', 3.0)

    @property
    def speed(self):
        return self.get_modified_trait('speed')

    @property
    def speed_in_water(self):
        """Get the agent's speed when in water based on habitat type."""
        # Update water speed if habitat preference has changed significantly
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)

        # Determine expected water speed based on current habitat preference
        if habitat_pref < 0.7:  # Aquatic
            expected_speed = self.phenotype.get('speed_in_water_aquatic', 5.0)
        elif habitat_pref > 1.3:  # Terrestrial
            expected_speed = self.phenotype.get('speed_in_water_terrestrial', 1.0)
        else:  # Amphibious
            expected_speed = self.phenotype.get('speed_in_water_amphibious', 3.0)

        # Update if needed
        if not hasattr(self, 'water_speed') or abs(self.water_speed - expected_speed) > 0.01:
            self._update_water_speed()

        return self.water_speed

    @property
    def speed_on_land(self):
        """Get the agent's speed when on land based on habitat type."""
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)

        # Determine land speed based on current habitat preference
        if habitat_pref < 0.7:  # Aquatic
            return self.phenotype.get('land_speed_aquatic', 2.0)
        elif habitat_pref > 1.3:  # Terrestrial
            return self.phenotype.get('land_speed_terrestrial', 5.5)
        else:  # Amphibious
            return self.phenotype.get('land_speed_amphibious', 4.0)

    @property
    def energy_consumption_rate(self):
        """Get the agent's energy consumption rate based on habitat type."""
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)

        # Determine energy consumption based on current habitat preference
        if habitat_pref < 0.7:  # Aquatic
            return self.phenotype.get('energy_consumption_aquatic', 0.8)
        elif habitat_pref > 1.3:  # Terrestrial
            return self.phenotype.get('energy_consumption_terrestrial', 0.9)
        else:  # Amphibious
            return self.phenotype.get('energy_consumption_amphibious', 1.0)

    @property
    def vision_range_by_habitat(self):
        """Get the agent's vision range based on habitat type."""
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)

        # Determine vision range based on current habitat preference
        if habitat_pref < 0.7:  # Aquatic
            return self.phenotype.get('vision_range_aquatic', 80.0)
        elif habitat_pref > 1.3:  # Terrestrial
            return self.phenotype.get('vision_range_terrestrial', 120.0)
        else:  # Amphibious
            return self.phenotype.get('vision_range_amphibious', 100.0)

    @property
    def diet_energy_conversion_rate(self):
        """Get the agent's diet-specific energy conversion rate."""
        diet_type = self.diet_type_numeric

        # Determine energy conversion based on current diet type
        if diet_type <= 0.5:  # Carnivore
            return self.phenotype.get('diet_energy_conversion', 1.0)
        elif diet_type >= 1.5:  # Herbivore
            return self.phenotype.get('diet_energy_conversion', 1.0)
        else:  # Omnivore
            return self.phenotype.get('diet_energy_conversion', 1.0)

    @property
    def size(self):
        return self.get_modified_trait('size')

    @property
    def vision_range(self):
        return self.phenotype.get('vision_range', 100.0)  # Vision is not region-dependent

    @property
    def efficiency(self):
        return self.get_modified_trait('energy_efficiency')

    @property
    def aggression(self):
        return self.get_modified_trait('aggression')

    @property
    def max_age(self):
        return self.phenotype.get('max_age', 70.0)

    @property
    def virus_resistance(self):
        return self.phenotype.get('virus_resistance', 0.5)  # Default to 0.5 if not in phenotype

    @property
    def agility(self):
        """Morphological trait: turning/acceleration capability."""
        return self.phenotype.get('agility', 0.5)

    @property
    def armor(self):
        """Morphological trait: damage reduction."""
        return self.phenotype.get('armor', 0.5)

    @property
    def sex(self):
        """Get the agent's sex from its genome."""
        if hasattr(self, 'genome') and self.genome:
            return self.genome.sex
        return 'unknown'  # Default if genome not available

    def _determine_shape_type(self):
        """Determine the shape type based on species ID."""
        # Different species get different shapes
        # This creates visual distinction between species
        shape_types = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']
        # Use species_id to determine shape, cycling through available shapes
        return shape_types[self.species_id % len(shape_types)]

    def radius(self):
        # Base radius on genetic size trait
        base_radius = max(2, int(self.size))

        # Add species-based size variation
        # Different species can have different size characteristics
        species_size_factor = 1.0 + (self.species_id % 3) * 0.2  # Factor of 1.0, 1.2, or 1.4 based on species ID

        return max(2, int(base_radius * species_size_factor))

    def draw_with_shape(self, screen, pos):
        """Draw the agent with its specific shape based on species."""
        color = self.get_color()
        radius = self.radius()

        if self.shape_type == 'circle':
            pygame.draw.circle(screen, color, pos, radius)
        elif self.shape_type == 'square':
            pygame.draw.rect(screen, color, (pos[0] - radius, pos[1] - radius, radius * 2, radius * 2))
        elif self.shape_type == 'triangle':
            # Draw an upward-pointing triangle
            points = [
                (pos[0], pos[1] - radius),  # Top point
                (pos[0] - radius, pos[1] + radius),  # Bottom left
                (pos[0] + radius, pos[1] + radius)   # Bottom right
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'diamond':
            # Draw a diamond/rhombus shape
            points = [
                (pos[0], pos[1] - radius),  # Top
                (pos[0] + radius, pos[1]),  # Right
                (pos[0], pos[1] + radius),  # Bottom
                (pos[0] - radius, pos[1])   # Left
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'hexagon':
            # Draw a hexagon shape
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30  # Offset by -30 to make flat side on top
                angle_rad = math.radians(angle_deg)
                x = pos[0] + radius * math.cos(angle_rad)
                y = pos[1] + radius * math.sin(angle_rad)
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'parallelogram':
            # Draw a parallelogram shape (slanted rectangle)
            offset = radius * 0.5  # Horizontal slant
            points = [
                (pos[0] - radius + offset, pos[1] - radius),  # Top-left shifted right
                (pos[0] + radius + offset, pos[1] - radius),  # Top-right shifted right
                (pos[0] + radius - offset, pos[1] + radius),  # Bottom-right shifted left
                (pos[0] - radius - offset, pos[1] + radius)   # Bottom-left shifted left
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'pentagon':
            # Draw a pentagon shape
            points = []
            for i in range(5):
                angle_deg = 72 * i - 90  # 72 degrees per vertex, start at top (-90 degrees)
                angle_rad = math.radians(angle_deg)
                x = pos[0] + radius * math.cos(angle_rad)
                y = pos[1] + radius * math.sin(angle_rad)
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'star':
            # Draw a 5-pointed star shape
            outer_points = []
            inner_points = []

            for i in range(5):
                # Outer points (tips of star)
                outer_angle = math.radians(72 * i - 90)  # Start at top
                outer_x = pos[0] + radius * math.cos(outer_angle)
                outer_y = pos[1] + radius * math.sin(outer_angle)
                outer_points.append((outer_x, outer_y))

                # Inner points (valleys of star)
                inner_angle = math.radians(72 * i + 36 - 90)  # Between outer points
                inner_x = pos[0] + (radius * 0.4) * math.cos(inner_angle)  # Inner radius is smaller
                inner_y = pos[1] + (radius * 0.4) * math.sin(inner_angle)
                inner_points.append((inner_x, inner_y))

            # Combine outer and inner points in order
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])

            pygame.draw.polygon(screen, color, star_points)
        else:
            # Default to circle if unknown shape
            pygame.draw.circle(screen, color, pos, radius)

    def draw_with_shape_scaled(self, screen, pos, scale=1.0):
        """Draw the agent with its specific shape based on species, with scaling."""
        color = self.get_color()
        radius = max(1, int(self.radius() * scale))

        if self.shape_type == 'circle':
            pygame.draw.circle(screen, color, pos, radius)
        elif self.shape_type == 'square':
            pygame.draw.rect(screen, color, (pos[0] - radius, pos[1] - radius, radius * 2, radius * 2))
        elif self.shape_type == 'triangle':
            # Draw an upward-pointing triangle
            points = [
                (pos[0], pos[1] - radius),  # Top point
                (pos[0] - radius, pos[1] + radius),  # Bottom left
                (pos[0] + radius, pos[1] + radius)   # Bottom right
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'diamond':
            # Draw a diamond/rhombus shape
            points = [
                (pos[0], pos[1] - radius),  # Top
                (pos[0] + radius, pos[1]),  # Right
                (pos[0], pos[1] + radius),  # Bottom
                (pos[0] - radius, pos[1])   # Left
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'hexagon':
            # Draw a hexagon shape
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30  # Offset by -30 to make flat side on top
                angle_rad = math.radians(angle_deg)
                x = pos[0] + radius * math.cos(angle_rad)
                y = pos[1] + radius * math.sin(angle_rad)
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'parallelogram':
            # Draw a parallelogram shape (slanted rectangle)
            offset = radius * 0.5  # Horizontal slant
            points = [
                (pos[0] - radius + offset, pos[1] - radius),  # Top-left shifted right
                (pos[0] + radius + offset, pos[1] - radius),  # Top-right shifted right
                (pos[0] + radius - offset, pos[1] + radius),  # Bottom-right shifted left
                (pos[0] - radius - offset, pos[1] + radius)   # Bottom-left shifted left
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'pentagon':
            # Draw a pentagon shape
            points = []
            for i in range(5):
                angle_deg = 72 * i - 90  # 72 degrees per vertex, start at top (-90 degrees)
                angle_rad = math.radians(angle_deg)
                x = pos[0] + radius * math.cos(angle_rad)
                y = pos[1] + radius * math.sin(angle_rad)
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
        elif self.shape_type == 'star':
            # Draw a 5-pointed star shape
            outer_points = []
            inner_points = []

            for i in range(5):
                # Outer points (tips of star)
                outer_angle = math.radians(72 * i - 90)  # Start at top
                outer_x = pos[0] + radius * math.cos(outer_angle)
                outer_y = pos[1] + radius * math.sin(outer_angle)
                outer_points.append((outer_x, outer_y))

                # Inner points (valleys of star)
                inner_angle = math.radians(72 * i + 36 - 90)  # Between outer points
                inner_x = pos[0] + (radius * 0.4) * math.cos(inner_angle)
                inner_y = pos[1] + (radius * 0.4) * math.sin(inner_angle)
                inner_points.append((inner_x, inner_y))

            # Combine outer and inner points in order
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])

            pygame.draw.polygon(screen, color, star_points)
        else:
            # Default to circle if unknown shape
            pygame.draw.circle(screen, color, pos, radius)

    def die(self):
        self.alive = False
        # Clear infection status when agent dies
        self.infected = False
        self.current_disease = None
        self.infection_timer = 0.0

    def can_reproduce(self, settings=None):
        settings = settings or {}
        return (self.energy >= settings.get('REPRODUCTION_THRESHOLD', config.REPRODUCTION_THRESHOLD) and
                self.hydration > 20.0 and
                self.age >= settings.get('MATURITY_AGE', config.MATURITY_AGE) and
                self.reproduction_cooldown <= 0)

    def _calculate_base_color(self):
        """Calculate the base color based on genetic color traits - this remains fixed for the agent's lifetime."""
        # Get base color values from phenotype (these are inherited traits)
        base_red = self.phenotype.get('color_red', 128.0)  # Base red value from genetics (default to middle value)
        base_green = self.phenotype.get('color_green', 128.0)  # Base green value from genetics
        base_blue = self.phenotype.get('color_blue', 128.0)  # Base blue value from genetics

        # Normalize base color values to 0-255 range
        r = max(0, min(255, int(base_red)))
        g = max(0, min(255, int(base_green)))
        b = max(0, min(255, int(base_blue)))

        return (max(20, r), max(20, g), max(20, b))

    @property
    def world(self):
        """Get the world reference using weak reference."""
        if self._world_ref is not None:
            return self._world_ref()
        return None

    @world.setter
    def world(self, world_obj):
        """Set the world reference as a weak reference."""
        if world_obj is not None:
            self._world_ref = weakref.ref(world_obj)
        else:
            self._world_ref = None

    def get_color(self):
        """Color based on fixed genetic color traits with energy brightness only."""
        # Use the fixed base color calculated at initialization
        r, g, b = self.base_color

        # Apply energy brightness factor only
        energy_factor = min(1.0, max(0.3, self.energy / config.MAX_ENERGY))
        r = int(r * energy_factor)
        g = int(g * energy_factor)
        b = int(b * energy_factor)

        return (max(20, r), max(20, g), max(20, b))

    def update_infection_status(self, dt):
        """Update infection status and handle recovery."""
        if self.infected:
            # Decrease infection timer
            self.infection_timer -= dt

            # Check if agent should recover
            if self.infection_timer <= 0:
                self.recover_from_disease()

    def get_disease_resistance(self, disease_name):
        """Get the genetic resistance to a specific disease."""
        return self.disease_resistances.get(disease_name, 0.5)  # Default to 0.5 if disease not found

    def can_catch_disease(self, disease_name):
        """Check if the agent can catch a specific disease based on genetic resistance."""
        resistance = self.get_disease_resistance(disease_name)
        # Higher resistance means lower chance of catching the disease
        return random.random() > resistance

    def infect_with_disease(self, disease_name, duration=10.0):
        """Infect the agent with a specific disease."""
        if not self.infected:
            self.infected = True
            self.current_disease = disease_name
            self.infection_timer = duration
            # Apply disease effects based on the specific disease
            self._apply_disease_effects(disease_name)

    def _apply_disease_effects(self, disease_name):
        """Apply specific effects of a disease to the agent.

        Note: Speed and vision_range are read-only properties derived from phenotype,
        so disease effects are applied to energy and hydration only.
        """
        # Different diseases have different effects on energy/hydration
        if disease_name == 'Flu':
            # Flu reduces energy
            self.energy *= 0.9
        elif disease_name == 'Plague':
            # Plague heavily reduces energy
            self.energy *= 0.7
        elif disease_name == 'Malaria':
            # Malaria affects hydration and energy
            self.hydration *= 0.8
            self.energy *= 0.85
        elif disease_name == 'Pox':
            # Pox reduces energy
            self.energy *= 0.9
        # Add more diseases as needed

    def recover_from_disease(self):
        """Recover from the current disease."""
        if self.infected:
            self.infected = False
            self.current_disease = None
            self.infection_timer = 0.0
            # Reverse disease effects
            self._reverse_disease_effects()

    def _reverse_disease_effects(self):
        """Reverse the effects of the disease when recovered."""
        # This would reverse the effects applied in _apply_disease_effects
        # For now, we'll just reset to normal values
        # In a more complex implementation, we might need to store original values
        pass

    def _calculate_genetic_distance_from_mean(self):
        """Calculate how genetically different this agent is from the population mean."""
        if not hasattr(self, 'world') or not self.world:
            return 0.0

        # Calculate population averages for comparison
        agents = self.world.agent_list
        if len(agents) == 0:
            return 0.0

        # Calculate population averages
        avg_speed = sum(a.speed for a in agents) / len(agents)
        avg_size = sum(a.size for a in agents) / len(agents)
        avg_aggression = sum(a.aggression for a in agents) / len(agents)
        avg_vision = sum(a.vision_range for a in agents) / len(agents)
        avg_efficiency = sum(a.efficiency for a in agents) / len(agents)
        avg_max_age = sum(a.max_age for a in agents) / len(agents)

        # Calculate how much this agent differs from the population averages
        speed_diff = abs(self.speed - avg_speed) / max(avg_speed, 1.0)
        size_diff = abs(self.size - avg_size) / max(avg_size, 1.0)
        aggro_diff = abs(self.aggression - avg_aggression) / max(avg_aggression, 1.0)
        vision_diff = abs(self.vision_range - avg_vision) / max(avg_vision, 1.0)
        efficiency_diff = abs(self.efficiency - avg_efficiency) / max(avg_efficiency, 1.0)
        max_age_diff = abs(self.max_age - avg_max_age) / max(avg_max_age, 1.0)

        # Average the differences to get a genetic distance factor
        avg_diff = (speed_diff + size_diff + aggro_diff + vision_diff + efficiency_diff + max_age_diff) / 6.0
        return min(1.0, avg_diff)  # Clamp to 0-1 range

    def rebuild_brain(self, settings=None):
        """Rebuild brain from current genome (after somatic mutation)."""
        nn_type = self.nn_type
        if settings:
            nn_type = settings.get('NN_TYPE', nn_type)
        self.brain = build_brain(self.genome, nn_type, settings)

        # If RNN, preserve hidden state if possible
        if isinstance(self.brain, RecurrentBrain) and hasattr(self, '_saved_hidden_state'):
            self.brain.hidden_state = self._saved_hidden_state

    def reset_brain_state(self):
        """Reset the RNN hidden state (useful on significant events)."""
        if isinstance(self.brain, RecurrentBrain):
            self.brain.reset_hidden_state()

    @classmethod
    def create_with_config(cls, pos, settings, agent_config):
        """
        Create an agent with a specific configuration.

        Args:
            pos: Position for the agent
            settings: Global simulation settings
            agent_config: Specific configuration for this agent type

        Returns:
            Agent instance with the specified configuration
        """
        # Create a genome with the specific configuration
        from src.genetics.genome import Genome

        # Create a genome based on the agent configuration
        # This would use the specific traits defined in the agent_config
        genome = Genome.create_with_traits(agent_config)

        # Create the agent with the specific genome
        agent = cls(pos, genome, generation=0,
                   trait_ranges=settings.get('TRAIT_RANGES', config.TRAIT_RANGES),
                   settings=settings)

        # Apply any specific configuration overrides
        for key, value in agent_config.items():
            # Skip environmental settings that should be shared
            environmental_keys = [
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
                'DISEASE_TRANSMISSION_ENABLED', 'DISEASE_TRANSMISSION_DISTANCE', 'DISEASE_NAMES', 'NUM_DISEASE_TYPES'
            ]

            if key not in environmental_keys:
                if hasattr(agent, key.lower()):
                    setattr(agent, key.lower(), value)
                elif hasattr(agent, key):
                    setattr(agent, key, value)

        return agent

    @property
    def diet_type(self):
        """Get the agent's diet type based on genetic traits.
        Returns: 'carnivore', 'herbivore', or 'omnivore'
        """
        # Average the two alleles for diet type
        diet_val = (self.phenotype.get('diet_type_1', 1.0) + self.phenotype.get('diet_type_2', 1.0)) / 2.0

        # Map continuous value to discrete diet types
        if diet_val < 0.7:
            return 'carnivore'
        elif diet_val > 1.3:
            return 'herbivore'
        else:
            return 'omnivore'

    @property
    def habitat_preference(self):
        """Get the agent's habitat preference based on genetic traits.
        Returns: 'aquatic', 'amphibious', or 'terrestrial'
        """
        # Average the two alleles for habitat preference
        habitat_val = (self.phenotype.get('habitat_preference_1', 1.0) + self.phenotype.get('habitat_preference_2', 1.0)) / 2.0

        # Map continuous value to discrete habitat types
        if habitat_val < 0.7:
            return 'aquatic'
        elif habitat_val > 1.3:
            return 'terrestrial'
        else:
            return 'amphibious'

    def update_dietary_behavior(self, attack_successful=False, ate_food=False):
        """Update dietary behavior based on recent actions, strongly influenced by genetic diet type."""
        # Update carnivorous tendency based on attack intent and success
        if self.attack_intent > 0.5:  # Agent is trying to attack
            self.carnivorous_tendency += 0.01
            if attack_successful:
                self.hunting_success_rate += 0.05
        elif self.attack_intent < -0.5:  # Agent is trying to flee
            self.herbivorous_tendency += 0.005

        # Update herbivorous tendency based on food consumption
        if ate_food:
            self.herbivorous_tendency += 0.02

        # Strongly bias the classification toward the genetic diet type
        # The genetic diet type is the primary determinant of behavior
        if self.diet_type == 'carnivore':
            # Carnivores are strongly biased toward carnivorous behavior
            self.carnivorous_tendency += 0.05
            self.dietary_classification = 'carnivore'
        elif self.diet_type == 'herbivore':
            # Herbivores are strongly biased toward herbivorous behavior
            self.herbivorous_tendency += 0.05
            self.dietary_classification = 'herbivore'
        else:  # Omnivore
            # Omnivores can exhibit both behaviors but tend toward balanced tendencies
            self.carnivorous_tendency *= 0.98  # Slow decay toward neutrality
            self.herbivorous_tendency *= 0.98  # Slow decay toward neutrality
            # Classification based on actual tendencies but with omnivore bias
            if self.carnivorous_tendency > self.herbivorous_tendency * 1.5:
                self.dietary_classification = 'carnivore'
            elif self.herbivorous_tendency > self.carnivorous_tendency * 1.5:
                self.dietary_classification = 'herbivore'
            else:
                self.dietary_classification = 'omnivore'

    def can_enter_water(self):
        """Check if the agent can enter water based on habitat preference.
        All agents can enter water, but with different penalties based on habitat preference."""
        # All agents can enter water, but with different penalties
        return True

    def can_enter_land(self):
        """Check if the agent can enter land based on habitat preference."""
        # Get numeric habitat preference (0.0 = aquatic, 1.0 = amphibious, 2.0 = terrestrial)
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)
        # Aquatic agents (closer to 0.0) cannot enter land, others can
        return habitat_pref > 0.5

    @property
    def diet_type_numeric(self):
        """Get the agent's diet type as a numeric value (0.0 = carnivore, 1.0 = omnivore, 2.0 = herbivore)."""
        return self.phenotype.get('diet_type', 1.0)

    def can_eat_meat(self):
        """Check if the agent can eat meat based on diet type."""
        diet_type = self.diet_type_numeric
        return diet_type <= 1.0  # carnivore (0.0) or omnivore (1.0)

    def can_eat_plants(self):
        """Check if the agent can eat plants based on diet type."""
        diet_type = self.diet_type_numeric
        return diet_type >= 1.0  # omnivore (1.0) or herbivore (2.0)

    def __repr__(self):
        # Convert numeric values to string representations for display
        diet_map = {0.0: 'carnivore', 1.0: 'omnivore', 2.0: 'herbivore'}
        habitat_map = {0.0: 'aquatic', 1.0: 'amphibious', 2.0: 'terrestrial'}

        diet_str = diet_map.get(int(self.diet_type_numeric), f'unknown({self.diet_type_numeric})')
        habitat_pref = self.phenotype.get('habitat_preference', 1.0)
        habitat_str = habitat_map.get(int(habitat_pref), f'unknown({habitat_pref})')

        return f"Agent(id={self.id}, gen={self.generation}, diet={diet_str}, habitat={habitat_str})"
