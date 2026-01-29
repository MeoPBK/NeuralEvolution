"""
Energy system using V2 neural network architecture.

Energy costs scale with effort output from the neural network.
High-effort actions are more costly, enforcing realistic trade-offs.
Supports advanced modulation features (size scaling, morphology, age effects).
"""
import math
import config


def update_energy(world, dt):
    """Apply metabolic energy costs to all agents.

    Energy cost formula (V2):
    cost = (base_drain + movement_cost * effort_scale) * metabolism_modifier * dt

    Where effort_scale = 0.5 + effort * EFFORT_ENERGY_SCALE
    And metabolism_modifier comes from advanced features.
    """
    settings = world.settings

    for agent in world.agent_list:
        if not agent.alive:
            continue

        cost = _compute_cost(agent, dt, settings)
        agent.energy -= cost

        if agent.energy <= 0:
            agent.die()


def _compute_cost(agent, dt, settings):
    """Compute energy cost with effort scaling and advanced modulation.

    High effort = higher energy cost
    Low effort = lower energy cost (energy conservation)
    Large size = superlinear metabolic cost (if enabled)
    """
    speed = agent.speed
    size = agent.size
    efficiency = agent.efficiency

    # Get effort from neural network output (default to 0.5 for backward compatibility)
    effort = getattr(agent, 'effort', 0.5)

    # Get modifiers from agent (set by movement system)
    modifiers = getattr(agent, 'current_modifiers', {})
    effective_metabolism = modifiers.get('effective_metabolism', 1.0)

    # Effort scaling factor
    effort_energy_scale = settings.get('EFFORT_ENERGY_SCALE', 1.5)
    effort_multiplier = 0.5 + effort * effort_energy_scale

    # Base metabolic cost
    base_cost = settings['ENERGY_DRAIN_BASE']

    # Apply superlinear size scaling if enabled
    if settings.get('SUPERLINEAR_ENERGY_SCALING', True):
        exponent = settings.get('ENERGY_SIZE_EXPONENT', 1.4)
        # Normalize by average size (6.0) so average agents aren't penalized
        size_factor = math.pow(size / 6.0, exponent)
        base_cost *= size_factor

        # Effort amplifies size cost
        effort_size_interaction = settings.get('EFFORT_SIZE_INTERACTION', 0.5)
        base_cost *= (1.0 + effort * effort_size_interaction * (size / 6.0 - 1.0))

    # Movement cost based on actual movement speed
    actual_speed = agent.velocity.length() if hasattr(agent, 'velocity') else speed
    movement_cost = (actual_speed * size / max(0.1, efficiency)) * settings['MOVEMENT_ENERGY_FACTOR']

    # Apply action costs if enabled
    if settings.get('ACTION_COSTS_ENABLED', False):
        # High-speed movement costs more
        speed_ratio = actual_speed / max(0.1, agent.speed * settings.get('MAX_SPEED_BASE', 6.0))
        if speed_ratio > 0.8:
            movement_cost *= settings.get('COST_HIGH_SPEED_MULTIPLIER', 1.5)

        # Sharp turns cost more (detected by velocity change)
        if hasattr(agent, '_last_velocity') and agent._last_velocity is not None:
            turn_magnitude = (agent.velocity - agent._last_velocity).length()
            if turn_magnitude > 0.3:
                movement_cost *= settings.get('COST_SHARP_TURN_MULTIPLIER', 1.3)

        agent._last_velocity = agent.velocity

    # Total cost with effort scaling and metabolism modifier
    total = (base_cost + movement_cost * effort_multiplier) * effective_metabolism * dt

    return total
