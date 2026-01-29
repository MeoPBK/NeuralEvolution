import random
import config
from src.utils.vector import Vector2
from src.entities.agent import Agent
from src.genetics.reproduction import create_offspring


def update_reproduction(world, dt):
    """Check for mating pairs and produce offspring."""
    new_agents = []

    for agent in world.agent_list:
        if not agent.alive or not agent.can_reproduce(world.settings):
            continue
        # Only reproduce if NN mate_desire is high enough
        if agent.mate_desire <= 0.5:
            continue

        mate = _find_nearby_mate(agent, world.agent_grid, world.settings)
        if mate is None:
            continue
        offsprings = _reproduce_multiple(parent_a=agent, parent_b=mate, settings=world.settings, world=world)
        if offsprings:
            new_agents.extend(offsprings)

    for a in new_agents:
        world.add_agent(a)


def _reproduce_multiple(parent_a, parent_b, settings, world):
    """Create multiple offsprings from two parents."""
    # Get reproduction modifiers from both parents (affected by age if AGE_EFFECTS_ENABLED)
    parent_a_mods = getattr(parent_a, 'current_modifiers', {})
    parent_b_mods = getattr(parent_b, 'current_modifiers', {})
    reproduction_modifier_a = parent_a_mods.get('reproduction_modifier', 1.0)
    reproduction_modifier_b = parent_b_mods.get('reproduction_modifier', 1.0)

    # Combined reproduction success is affected by both parents
    combined_modifier = (reproduction_modifier_a + reproduction_modifier_b) / 2.0

    # Reproduction may fail based on age modifiers
    if random.random() > combined_modifier:
        # Reproduction attempt failed due to age-related effects
        return None

    # Randomize the number of offsprings for this mating session (0 to max)
    num_offsprings = random.randint(0, settings.get('MAX_SIMULTANEOUS_OFFSPRING', 1))

    # If no offsprings are produced, return None
    if num_offsprings == 0:
        return None

    # Reset mating context signal for both parents
    if hasattr(parent_a, 'time_since_mating'):
        parent_a.time_since_mating = 0.0
    if hasattr(parent_b, 'time_since_mating'):
        parent_b.time_since_mating = 0.0

    # Deduct reproduction cost once for the mating session
    parent_a.energy -= settings['REPRODUCTION_COST'] * num_offsprings
    parent_b.energy -= settings['REPRODUCTION_COST'] * num_offsprings
    parent_a.reproduction_cooldown = settings['REPRODUCTION_COOLDOWN']
    parent_b.reproduction_cooldown = settings['REPRODUCTION_COOLDOWN']

    # Create a temporary config-like object with the settings values
    class TempConfig:
        def __getattr__(self, name):
            # Return the setting value if it exists, otherwise return a default
            defaults = {
                'MUTATION_RATE': 0.02,
                'CROSSOVER_RATE': 0.3,
                'LARGE_MUTATION_CHANCE': 0.05,
                'DOMINANCE_MUTATION_RATE': 0.15,
                'POINT_MUTATION_STDDEV': 0.3,
                'LARGE_MUTATION_STDDEV': 1.5
            }
            return settings.get(name, defaults.get(name, 0))

    # Create all offsprings for this mating session
    offsprings = []
    for i in range(num_offsprings):
        # Create offspring genome
        offspring_genome, mutations_from_reproduction = create_offspring(parent_a.genome, parent_b.genome, TempConfig())

        # Calculate spawn position with slight variation for each offspring
        offset = Vector2.random_unit() * (20 + i * 5)  # Spread out multiple offsprings
        spawn_pos = parent_a.pos + offset
        spawn_pos.x = spawn_pos.x % settings['WORLD_WIDTH']
        spawn_pos.y = spawn_pos.y % settings['WORLD_HEIGHT']

        generation = max(parent_a.generation, parent_b.generation) + 1
        trait_ranges = settings.get('TRAIT_RANGES', config.TRAIT_RANGES)

        # Create offspring and determine its species
        offspring = Agent(spawn_pos, offspring_genome, generation, trait_ranges=trait_ranges, settings=settings)
        offspring.energy = settings['BASE_ENERGY'] * 0.8
        offspring.hydration = settings['BASE_HYDRATION'] * 0.8
        offspring.total_mutations = mutations_from_reproduction  # Initialize with mutations from reproduction
        offspring.age = 0.0  # Newborn agents always start at age 0

        # Determine offspring's species based on parents
        # If parents are the same species, offspring is of that species
        if parent_a.is_same_species_as(parent_b, settings):
            # Same species parents - offspring gets the same species ID as parents
            offspring.species_id = parent_a.species_id
            offspring.genetic_similarity_score = 1.0  # Start with high similarity to parent species
        else:
            # Cross-species parents - offspring gets a new species ID or inherits from one parent
            # For now, we'll assign it to the species of the first parent
            offspring.species_id = parent_a.species_id
            # Calculate genetic similarity based on both parents
            similarity_a = parent_a.calculate_genetic_similarity(offspring)
            similarity_b = parent_b.calculate_genetic_similarity(offspring)
            offspring.genetic_similarity_score = (similarity_a + similarity_b) / 2.0

        # Assign shape based on species ID to ensure visual distinction
        offspring.shape_type = offspring._determine_shape_type()

        # Inherit disease resistances from parents with potential mutations
        # Offspring inherits disease resistances from both parents with some genetic variation
        for disease_name in offspring.disease_resistances.keys():
            # Get parent resistances
            parent_a_resistance = parent_a.get_disease_resistance(disease_name)
            parent_b_resistance = parent_b.get_disease_resistance(disease_name)

            # Average the resistances from both parents
            avg_resistance = (parent_a_resistance + parent_b_resistance) / 2.0

            # Add some genetic variation through mutation
            mutation_factor = (random.random() - 0.5) * 0.1  # Small variation (-0.05 to +0.05)
            offspring_resistance = max(0.0, min(1.0, avg_resistance + mutation_factor))

            # Set the offspring's resistance to this disease
            if disease_name in offspring.disease_resistances:
                offspring.disease_resistances[disease_name] = offspring_resistance

        offsprings.append(offspring)

    # Increment offspring count for both parents
    parent_a.offspring_count += num_offsprings
    parent_b.offspring_count += num_offsprings

    # Record mating event for animation
    mating_pos = ((parent_a.pos.x + parent_b.pos.x) / 2, (parent_a.pos.y + parent_b.pos.y) / 2)
    if not hasattr(world, 'mating_events'):
        world.mating_events = []
    world.mating_events.append({
        'position': mating_pos,
        'time': 1.0  # Duration of the animation in seconds
    })

    return offsprings


def _find_nearby_mate(agent, grid, settings):
    """Find a compatible mate within mating distance."""
    candidates = grid.query_radius(
        agent.pos, settings['MATING_DISTANCE'], exclude=agent
    )
    for c in candidates:
        if (c.alive and c.can_reproduce() and
                c.genome.sex != agent.genome.sex and
                c.mate_desire > 0.5):
            # Check species compatibility
            if _are_compatible_species(agent, c, settings):
                return c
    return None


def _are_compatible_species(agent_a, agent_b, settings):
    """Check if two agents are compatible for reproduction based on species."""
    # Check if agents are of the same species
    same_species = agent_a.is_same_species_as(agent_b, settings)

    if same_species:
        return True
    else:
        # Check if cross-species mating is allowed based on hybrid fertility settings
        hybrid_fertility_rate = settings.get('HYBRID_FERTILITY_RATE', 0.1)
        return random.random() < hybrid_fertility_rate  # Chance of cross-species reproduction based on setting
