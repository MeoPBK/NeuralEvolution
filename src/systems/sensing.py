"""
Sector-based sensing system for computing neural network inputs.

The agent's field of view is divided into 5 angular sectors of 72 degrees each,
providing spatial awareness without perfect point-location knowledge.
"""
import math
import random


# Sector configuration
N_SECTORS = 5
SECTOR_ANGLE = 2 * math.pi / N_SECTORS  # 72 degrees per sector


def compute_sector_inputs(agent, world, settings):
    """Compute all neural network inputs for an agent.

    Base inputs (24 values):
    - [0-4]: Food signals per sector
    - [5-9]: Water signals per sector
    - [10-14]: Agent signals per sector (positive=smaller, negative=larger)
    - [15]: Energy (normalized)
    - [16]: Hydration (normalized)
    - [17]: Age ratio
    - [18]: Stress level
    - [19]: Health (combined vitality)
    - [20]: Forward velocity
    - [21]: Lateral velocity
    - [22]: Own size (normalized)
    - [23]: Own speed capability (normalized)

    Optional context signals (+3 if enabled):
    - [24]: Hunger signal (time since food)
    - [25]: Safety signal (time since damage)
    - [26]: Mating receptivity signal
    """
    inputs = []

    # Get vision range with possible perception modifier
    base_vision = agent.phenotype.get('vision_range', 100.0)

    # Apply perception modifier if advanced features enabled
    if settings.get('ADVANCED_SIZE_EFFECTS_ENABLED', False):
        from src.systems.modulation import compute_size_modifiers
        size_mods = compute_size_modifiers(agent, settings)
        vision_range = base_vision * size_mods.get('perception_modifier', 1.0)
    else:
        vision_range = base_vision

    noise_std = settings.get('VISION_NOISE_STD', 0.05)

    # === Sector-based sensing ===
    # Food signals (5 sectors)
    food_signals = compute_food_sectors(agent, world, vision_range)
    inputs.extend(add_noise(food_signals, noise_std))

    # Water signals (5 sectors)
    water_signals = compute_water_sectors(agent, world, vision_range, settings)
    inputs.extend(add_noise(water_signals, noise_std))

    # Agent signals (5 sectors)
    agent_signals = compute_agent_sectors(agent, world, vision_range)
    inputs.extend(add_noise(agent_signals, noise_std))

    # === Internal state ===
    max_energy = settings.get('MAX_ENERGY', 300.0)
    max_hydration = settings.get('MAX_HYDRATION', 150.0)

    # Energy (normalized 0-1)
    energy_norm = clamp(agent.energy / max_energy, 0, 1)
    inputs.append(energy_norm)

    # Hydration (normalized 0-1)
    hydration_norm = clamp(agent.hydration / max_hydration, 0, 1)
    inputs.append(hydration_norm)

    # Age ratio (0-1)
    max_age = agent.phenotype.get('max_age', settings.get('MAX_AGE', 70.0))
    age_ratio = clamp(agent.age / max_age, 0, 1) if max_age > 0 else 0
    inputs.append(age_ratio)

    # Stress level (0-1) - computed from agent's stress state
    stress = getattr(agent, 'stress', 0.0)
    inputs.append(clamp(stress, 0, 1))

    # Health (combined vitality metric)
    health = compute_health(agent, settings)
    inputs.append(health)

    # === Egocentric velocity ===
    vel_forward, vel_lateral = compute_egocentric_velocity(agent, settings)
    inputs.append(vel_forward)
    inputs.append(vel_lateral)

    # === Self traits (normalized) ===
    trait_ranges = settings.get('TRAIT_RANGES', {})

    # Own size normalized
    size_range = trait_ranges.get('size', (3.0, 12.0))
    own_size = agent.phenotype.get('size', 6.0)
    own_size_norm = (own_size - size_range[0]) / (size_range[1] - size_range[0])
    inputs.append(clamp(own_size_norm, 0, 1))

    # Own speed normalized
    speed_range = trait_ranges.get('speed', (1.0, 6.0))
    own_speed = agent.phenotype.get('speed', 3.0)
    own_speed_norm = (own_speed - speed_range[0]) / (speed_range[1] - speed_range[0])
    inputs.append(clamp(own_speed_norm, 0, 1))

    # === Optional Context Signals ===
    if settings.get('CONTEXT_SIGNALS_ENABLED', False):
        from src.systems.modulation import get_context_signal_inputs
        context_inputs = get_context_signal_inputs(agent, settings)
        inputs.extend(context_inputs)

    # === Apply Sensory Noise ===
    if settings.get('SENSORY_NOISE_ENABLED', True):
        from src.systems.modulation import apply_sensory_noise
        inputs = apply_sensory_noise(inputs, settings)

    return inputs


def compute_food_sectors(agent, world, vision_range):
    """Compute food presence signal for each sector.

    Returns list of 5 values (one per sector), each in range [0, 1].
    Higher values indicate more/closer food in that sector.
    """
    sectors = [0.0] * N_SECTORS

    # Query nearby food using spatial grid
    nearby_food = world.food_grid.query_radius(agent.pos, vision_range)

    for food in nearby_food:
        # Calculate direction and distance to food
        dx = food.pos.x - agent.pos.x
        dy = food.pos.y - agent.pos.y

        # Handle toroidal wrapping
        world_w = world.settings.get('WORLD_WIDTH', 1200)
        world_h = world.settings.get('WORLD_HEIGHT', 600)
        if abs(dx) > world_w / 2:
            dx = dx - math.copysign(world_w, dx)
        if abs(dy) > world_h / 2:
            dy = dy - math.copysign(world_h, dy)

        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            dist = 1  # Avoid division by zero

        if dist <= vision_range:
            # Determine which sector this food is in
            angle = math.atan2(dy, dx)  # -pi to pi
            sector = angle_to_sector(angle, agent)

            # Distance-weighted signal (inverse square falloff)
            signal = 1.0 / (1.0 + (dist / vision_range) ** 2)
            sectors[sector] += signal

    # Normalize to [0, 1] range
    max_signal = max(sectors) if max(sectors) > 0 else 1
    return [clamp(s / max(max_signal, 1), 0, 1) for s in sectors]


def compute_water_sectors(agent, world, vision_range, settings):
    """Compute water proximity signal for each sector.

    Returns list of 5 values (one per sector), each in range [0, 1].
    """
    sectors = [0.0] * N_SECTORS

    water_radius = settings.get('WATER_SOURCE_RADIUS', 40.0)

    for water in world.water_list:
        # Calculate direction and distance to water center
        dx = water.pos.x - agent.pos.x
        dy = water.pos.y - agent.pos.y

        # Handle toroidal wrapping
        world_w = world.settings.get('WORLD_WIDTH', 1200)
        world_h = world.settings.get('WORLD_HEIGHT', 600)
        if abs(dx) > world_w / 2:
            dx = dx - math.copysign(world_w, dx)
        if abs(dy) > world_h / 2:
            dy = dy - math.copysign(world_h, dy)

        dist_to_center = math.sqrt(dx * dx + dy * dy)
        dist_to_edge = max(0, dist_to_center - water_radius)

        if dist_to_edge <= vision_range:
            # Determine sector
            angle = math.atan2(dy, dx)
            sector = angle_to_sector(angle, agent)

            # Signal based on distance to water edge
            if dist_to_edge < 1:
                signal = 1.0  # Inside or at edge of water
            else:
                signal = 1.0 / (1.0 + (dist_to_edge / vision_range) ** 2)

            sectors[sector] = max(sectors[sector], signal)

    return sectors


def compute_agent_sectors(agent, world, vision_range):
    """Compute agent presence signal for each sector.

    Returns list of 5 values (one per sector), each in range [-1, 1].
    Positive values indicate smaller/weaker agents (potential prey).
    Negative values indicate larger/stronger agents (potential threats).
    """
    sectors = [0.0] * N_SECTORS
    sector_counts = [0] * N_SECTORS

    # Query nearby agents
    nearby_agents = world.agent_grid.query_radius(agent.pos, vision_range, exclude=agent)

    own_size = agent.phenotype.get('size', 6.0)
    own_aggr = agent.phenotype.get('aggression', 1.0)

    for other in nearby_agents:
        if not other.alive:
            continue

        # Calculate direction and distance
        dx = other.pos.x - agent.pos.x
        dy = other.pos.y - agent.pos.y

        # Handle toroidal wrapping
        world_w = world.settings.get('WORLD_WIDTH', 1200)
        world_h = world.settings.get('WORLD_HEIGHT', 600)
        if abs(dx) > world_w / 2:
            dx = dx - math.copysign(world_w, dx)
        if abs(dy) > world_h / 2:
            dy = dy - math.copysign(world_h, dy)

        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            dist = 1

        if dist <= vision_range:
            # Determine sector
            angle = math.atan2(dy, dx)
            sector = angle_to_sector(angle, agent)

            # Compare size/threat level
            other_size = other.phenotype.get('size', 6.0)
            other_aggr = other.phenotype.get('aggression', 1.0)

            # Threat metric: larger and more aggressive = more threatening
            threat_diff = (other_size * other_aggr) - (own_size * own_aggr)

            # Distance-weighted signal
            weight = 1.0 / (1.0 + (dist / vision_range) ** 2)

            # Positive = smaller/weaker (prey), Negative = larger/stronger (threat)
            signal = -math.tanh(threat_diff * 0.2) * weight

            sectors[sector] += signal
            sector_counts[sector] += 1

    # Average and clamp
    for i in range(N_SECTORS):
        if sector_counts[i] > 0:
            sectors[i] = clamp(sectors[i] / sector_counts[i], -1, 1)

    return sectors


def angle_to_sector(angle, agent):
    """Convert an angle to a sector index.

    Args:
        angle: Angle in radians (-pi to pi)
        agent: The agent (for facing direction, if implemented)

    Returns:
        Sector index (0 to N_SECTORS-1)
    """
    # Get agent's facing direction (if available, otherwise use velocity or default to right)
    facing_angle = getattr(agent, 'facing_angle', 0.0)
    if hasattr(agent, 'velocity') and agent.velocity:
        vx = agent.velocity.x if hasattr(agent.velocity, 'x') else 0
        vy = agent.velocity.y if hasattr(agent.velocity, 'y') else 0
        if abs(vx) > 0.01 or abs(vy) > 0.01:
            facing_angle = math.atan2(vy, vx)

    # Relative angle from agent's facing direction
    rel_angle = angle - facing_angle

    # Normalize to [0, 2*pi)
    while rel_angle < 0:
        rel_angle += 2 * math.pi
    while rel_angle >= 2 * math.pi:
        rel_angle -= 2 * math.pi

    # Map to sector (0 = front, then clockwise)
    # Offset so that front sector is centered on 0
    offset_angle = rel_angle + SECTOR_ANGLE / 2
    if offset_angle >= 2 * math.pi:
        offset_angle -= 2 * math.pi

    sector = int(offset_angle / SECTOR_ANGLE)
    return min(sector, N_SECTORS - 1)


def compute_health(agent, settings):
    """Compute combined health/vitality metric.

    Returns value in [0, 1] where 1 is perfect health.
    """
    max_energy = settings.get('MAX_ENERGY', 300.0)
    max_hydration = settings.get('MAX_HYDRATION', 150.0)

    energy_factor = clamp(agent.energy / max_energy, 0, 1)
    hydration_factor = clamp(agent.hydration / max_hydration, 0, 1)

    # Health is geometric mean of energy and hydration
    health = math.sqrt(energy_factor * hydration_factor)

    # Penalize for high age
    max_age = agent.phenotype.get('max_age', settings.get('MAX_AGE', 70.0))
    if max_age > 0:
        age_penalty = max(0, (agent.age / max_age) - 0.7) * 0.5
        health = max(0, health - age_penalty)

    return clamp(health, 0, 1)


def compute_egocentric_velocity(agent, settings):
    """Compute velocity in agent's reference frame.

    Returns (forward_velocity, lateral_velocity), each normalized to [-1, 1].
    """
    # Get agent's velocity
    if not hasattr(agent, 'velocity') or agent.velocity is None:
        return 0.0, 0.0

    vx = agent.velocity.x if hasattr(agent.velocity, 'x') else 0
    vy = agent.velocity.y if hasattr(agent.velocity, 'y') else 0

    # Get max speed for normalization
    max_speed = agent.phenotype.get('speed', 3.0) * settings.get('MAX_SPEED_BASE', 6.0)
    if max_speed < 0.1:
        max_speed = 1.0

    # Get facing direction
    facing_angle = getattr(agent, 'facing_angle', 0.0)
    if abs(vx) > 0.01 or abs(vy) > 0.01:
        facing_angle = math.atan2(vy, vx)

    # Project velocity onto forward and lateral axes
    cos_f = math.cos(facing_angle)
    sin_f = math.sin(facing_angle)

    vel_forward = (vx * cos_f + vy * sin_f) / max_speed
    vel_lateral = (-vx * sin_f + vy * cos_f) / max_speed

    return clamp(vel_forward, -1, 1), clamp(vel_lateral, -1, 1)


def update_agent_stress(agent, world, settings, dt):
    """Update agent's internal stress/arousal level.

    Stress increases from:
    - Nearby threatening agents
    - Low energy or hydration
    - Recent damage

    Stress decays naturally over time.
    """
    if not hasattr(agent, 'stress'):
        agent.stress = 0.0

    gain_rate = settings.get('STRESS_GAIN_RATE', 0.5)
    decay_rate = settings.get('STRESS_DECAY_RATE', 0.2)
    threat_weight = settings.get('STRESS_THREAT_WEIGHT', 1.0)
    resource_weight = settings.get('STRESS_RESOURCE_WEIGHT', 0.5)

    # Threat from nearby larger agents
    threat_level = 0.0
    vision_range = agent.phenotype.get('vision_range', 100.0)
    own_size = agent.phenotype.get('size', 6.0)

    nearby = world.agent_grid.query_radius(agent.pos, vision_range * 0.5, exclude=agent)
    for other in nearby:
        if other.alive:
            other_size = other.phenotype.get('size', 6.0)
            other_aggr = other.phenotype.get('aggression', 1.0)
            if other_size * other_aggr > own_size * 1.2:
                threat_level += 0.3

    # Resource stress
    max_energy = settings.get('MAX_ENERGY', 300.0)
    max_hydration = settings.get('MAX_HYDRATION', 150.0)
    energy_stress = max(0, 0.5 - agent.energy / max_energy)
    hydration_stress = max(0, 0.5 - agent.hydration / max_hydration)

    # Recent damage stress
    recent_damage = getattr(agent, 'recent_damage', 0.0)

    # Accumulate stress
    stress_gain = gain_rate * dt * (
        threat_level * threat_weight +
        (energy_stress + hydration_stress) * resource_weight +
        recent_damage * 2.0
    )

    # Apply gain and decay
    agent.stress += stress_gain
    agent.stress -= decay_rate * dt
    agent.stress = clamp(agent.stress, 0, 1)

    # Decay recent damage tracker
    if hasattr(agent, 'recent_damage'):
        agent.recent_damage = max(0, agent.recent_damage - 0.1 * dt)


def add_noise(values, noise_std):
    """Add small Gaussian noise to sensor values for partial observability."""
    if noise_std <= 0:
        return values
    return [clamp(v + random.gauss(0, noise_std), -1, 1) for v in values]


def clamp(value, min_val, max_val):
    """Clamp value to range."""
    return max(min_val, min(max_val, value))
