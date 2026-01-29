"""
Advanced Modulation System for embodied agent behaviors.

This module provides continuous, soft modulation of agent capabilities based on:
- Body size (strength vs efficiency vs agility trade-offs)
- Age (life-history strategies)
- Internal state (energy, hydration, stress)
- Morphological traits (agility, armor)

All effects are continuous and evolvable - no hard-coded behavior rules.
"""
import math
import random


def compute_size_modifiers(agent, settings):
    """Compute movement, attack, and metabolic modifiers based on body size.

    Larger agents are stronger but slower and more expensive to maintain.
    Smaller agents are efficient but weaker.

    Returns dict with modifier values (all multiplicative, 1.0 = no change).
    """
    if not settings.get('ADVANCED_SIZE_EFFECTS_ENABLED', False):
        return {
            'attack_modifier': 1.0,
            'speed_modifier': 1.0,
            'turn_modifier': 1.0,
            'metabolic_modifier': 1.0,
            'perception_modifier': 1.0,
        }

    # Normalize size relative to trait range
    trait_ranges = settings.get('TRAIT_RANGES', {})
    size_range = trait_ranges.get('size', (3.0, 12.0))
    size_min, size_max = size_range
    size = agent.phenotype.get('size', 6.0)

    # Normalized size (0 = smallest, 1 = largest)
    size_norm = (size - size_min) / (size_max - size_min)
    size_norm = max(0, min(1, size_norm))

    # Attack strength scales superlinearly with size
    attack_exponent = settings.get('SIZE_ATTACK_SCALING', 1.5)
    attack_modifier = 0.5 + 1.5 * (size_norm ** attack_exponent)

    # Speed penalty for larger size (larger = slower)
    speed_penalty = settings.get('SIZE_SPEED_PENALTY', 0.3)
    speed_modifier = 1.0 - (size_norm * speed_penalty)

    # Turn rate penalty (larger = slower turning)
    turn_penalty = settings.get('SIZE_TURN_PENALTY', 0.4)
    turn_modifier = 1.0 - (size_norm * turn_penalty)

    # Metabolic cost scales superlinearly (larger = much more expensive)
    metabolic_exponent = settings.get('SIZE_METABOLIC_SCALING', 1.3)
    metabolic_modifier = 0.7 + 0.6 * (size_norm ** metabolic_exponent)

    # Perception bonus for larger size (slightly better vision)
    perception_bonus = settings.get('SIZE_PERCEPTION_BONUS', 0.1)
    perception_modifier = 1.0 + (size_norm * perception_bonus)

    return {
        'attack_modifier': attack_modifier,
        'speed_modifier': max(0.3, speed_modifier),  # Floor to prevent immobility
        'turn_modifier': max(0.3, turn_modifier),
        'metabolic_modifier': metabolic_modifier,
        'perception_modifier': perception_modifier,
    }


def compute_age_modifiers(agent, settings):
    """Compute capability modifiers based on agent age.

    Implements a life-history curve:
    - Young: Still developing, reduced capabilities
    - Prime: Peak performance
    - Old: Declining capabilities but potentially more experienced

    Returns dict with modifier values.
    """
    if not settings.get('AGE_EFFECTS_ENABLED', False):
        return {
            'speed_modifier': 1.0,
            'stamina_modifier': 1.0,
            'experience_modifier': 1.0,
            'reproduction_modifier': 1.0,
        }

    max_age = agent.phenotype.get('max_age', settings.get('MAX_AGE', 70.0))
    age_ratio = agent.age / max_age if max_age > 0 else 0
    age_ratio = max(0, min(1, age_ratio))

    prime_start = settings.get('AGE_PRIME_START', 0.2)
    prime_end = settings.get('AGE_PRIME_END', 0.6)

    # Compute life stage multiplier (0 = not in prime, 1 = peak prime)
    if age_ratio < prime_start:
        # Young - still developing
        development = age_ratio / prime_start
        prime_factor = 0.7 + 0.3 * development
    elif age_ratio <= prime_end:
        # Prime years
        prime_factor = 1.0
    else:
        # Aging - declining
        decline_progress = (age_ratio - prime_end) / (1.0 - prime_end)
        prime_factor = 1.0 - (decline_progress * 0.5)

    # Speed declines with age after prime
    speed_decline = settings.get('AGE_SPEED_DECLINE', 0.3)
    if age_ratio > prime_end:
        decline = (age_ratio - prime_end) / (1.0 - prime_end)
        speed_modifier = 1.0 - (decline * speed_decline)
    else:
        speed_modifier = prime_factor

    # Stamina (sustained effort capacity) declines with age
    stamina_decline = settings.get('AGE_STAMINA_DECLINE', 0.4)
    if age_ratio > prime_end:
        decline = (age_ratio - prime_end) / (1.0 - prime_end)
        stamina_modifier = 1.0 - (decline * stamina_decline)
    else:
        stamina_modifier = prime_factor

    # Experience bonus peaks at end of prime, then slowly declines
    experience_bonus = settings.get('AGE_EXPERIENCE_BONUS', 0.2)
    if age_ratio < prime_start:
        experience_modifier = 0.8 + 0.2 * (age_ratio / prime_start)
    elif age_ratio <= prime_end:
        experience_modifier = 1.0 + experience_bonus * ((age_ratio - prime_start) / (prime_end - prime_start))
    else:
        # Experience remains high but physical decline offsets it
        experience_modifier = 1.0 + experience_bonus * 0.8

    # Reproduction effectiveness varies with age
    if settings.get('AGE_REPRODUCTION_CURVE', True):
        if age_ratio < prime_start:
            reproduction_modifier = 0.5 + 0.5 * (age_ratio / prime_start)
        elif age_ratio <= prime_end:
            reproduction_modifier = 1.0
        else:
            decline = (age_ratio - prime_end) / (1.0 - prime_end)
            reproduction_modifier = 1.0 - (decline * 0.6)
    else:
        reproduction_modifier = 1.0

    return {
        'speed_modifier': max(0.3, speed_modifier),
        'stamina_modifier': max(0.3, stamina_modifier),
        'experience_modifier': experience_modifier,
        'reproduction_modifier': max(0.1, reproduction_modifier),
    }


def compute_internal_state_modifiers(agent, settings):
    """Compute soft modulation based on internal state (energy, hydration, stress).

    Low resources reduce effectiveness but don't hard-block actions.
    Stress can provide short-term boosts but has costs.

    Returns dict with modifier values.
    """
    if not settings.get('INTERNAL_STATE_MODULATION_ENABLED', False):
        return {
            'attack_modifier': 1.0,
            'speed_modifier': 1.0,
            'effort_capacity': 1.0,
            'stress_boost': 0.0,
        }

    max_energy = settings.get('MAX_ENERGY', 300.0)
    max_hydration = settings.get('MAX_HYDRATION', 150.0)
    exhaustion_threshold = settings.get('EXHAUSTION_THRESHOLD', 0.2)

    energy_ratio = agent.energy / max_energy if max_energy > 0 else 0
    hydration_ratio = agent.hydration / max_hydration if max_hydration > 0 else 0
    stress = getattr(agent, 'stress', 0.0)

    # Attack effectiveness drops when energy is very low
    attack_penalty = settings.get('LOW_ENERGY_ATTACK_PENALTY', 0.5)
    if energy_ratio < exhaustion_threshold:
        exhaustion_factor = energy_ratio / exhaustion_threshold
        attack_modifier = 0.5 + 0.5 * exhaustion_factor
    else:
        attack_modifier = 1.0

    # Speed penalty when dehydrated
    speed_penalty = settings.get('LOW_HYDRATION_SPEED_PENALTY', 0.3)
    if hydration_ratio < 0.3:
        dehydration_factor = hydration_ratio / 0.3
        speed_modifier = 1.0 - speed_penalty * (1.0 - dehydration_factor)
    else:
        speed_modifier = 1.0

    # Effort capacity reduced when exhausted
    if energy_ratio < exhaustion_threshold:
        effort_capacity = 0.5 + 0.5 * (energy_ratio / exhaustion_threshold)
    else:
        effort_capacity = 1.0

    # Stress can provide short-term boost (fight-or-flight)
    stress_boost_max = settings.get('HIGH_STRESS_EFFORT_BOOST', 0.2)
    # Stress boost is bell-curved - moderate stress helps, extreme stress hinders
    stress_boost = stress_boost_max * stress * (1.0 - stress * 0.5)

    return {
        'attack_modifier': max(0.3, attack_modifier),
        'speed_modifier': max(0.4, speed_modifier),
        'effort_capacity': max(0.3, effort_capacity),
        'stress_boost': stress_boost,
    }


def compute_morphology_modifiers(agent, settings):
    """Compute modifiers based on morphological traits (agility, armor).

    Agility: Better turning/acceleration, higher metabolism
    Armor: Damage reduction, slower movement, higher maintenance

    Returns dict with modifier values.
    """
    if not settings.get('MORPHOLOGY_TRAITS_ENABLED', False):
        return {
            'turn_modifier': 1.0,
            'acceleration_modifier': 1.0,
            'damage_reduction': 0.0,
            'speed_modifier': 1.0,
            'metabolic_modifier': 1.0,
        }

    # Get traits from phenotype (normalized 0-1)
    agility = agent.phenotype.get('agility', 0.5)
    armor = agent.phenotype.get('armor', 0.5)

    # Agility effects
    agility_speed_bonus = settings.get('AGILITY_SPEED_BONUS', 0.4)
    agility_stamina_cost = settings.get('AGILITY_STAMINA_COST', 0.2)

    turn_modifier = 1.0 + agility * agility_speed_bonus
    acceleration_modifier = 1.0 + agility * agility_speed_bonus * 0.5
    agility_metabolic = 1.0 + agility * agility_stamina_cost

    # Armor effects
    armor_damage_reduction = settings.get('ARMOR_DAMAGE_REDUCTION', 0.4)
    armor_speed_penalty = settings.get('ARMOR_SPEED_PENALTY', 0.3)
    armor_energy_cost = settings.get('ARMOR_ENERGY_COST', 0.15)

    damage_reduction = armor * armor_damage_reduction
    armor_speed = 1.0 - armor * armor_speed_penalty
    armor_metabolic = 1.0 + armor * armor_energy_cost

    return {
        'turn_modifier': turn_modifier,
        'acceleration_modifier': acceleration_modifier,
        'damage_reduction': damage_reduction,
        'speed_modifier': max(0.4, armor_speed),
        'metabolic_modifier': agility_metabolic * armor_metabolic,
    }


def compute_action_costs(agent, action_type, base_cost, settings):
    """Compute energy cost for a specific action with asymmetric scaling.

    Different actions have different energy costs:
    - high_speed: Moving at maximum speed
    - sharp_turn: Changing direction sharply
    - pursuit: Sustained chasing
    - attack: Combat actions
    - mating: Reproduction attempts

    Returns adjusted energy cost.
    """
    if not settings.get('ACTION_COSTS_ENABLED', False):
        return base_cost

    effort = getattr(agent, 'effort', 0.5)
    size = agent.phenotype.get('size', 6.0)

    # Size scaling (superlinear if enabled)
    if settings.get('SUPERLINEAR_ENERGY_SCALING', True):
        size_exponent = settings.get('ENERGY_SIZE_EXPONENT', 1.4)
        trait_ranges = settings.get('TRAIT_RANGES', {})
        size_range = trait_ranges.get('size', (3.0, 12.0))
        size_norm = (size - size_range[0]) / (size_range[1] - size_range[0])
        size_factor = 0.6 + 0.8 * (size_norm ** size_exponent)
    else:
        size_factor = size / 6.0  # Linear scaling

    # Effort-size interaction
    effort_size_interaction = settings.get('EFFORT_SIZE_INTERACTION', 0.5)
    interaction_factor = 1.0 + effort * size_factor * effort_size_interaction

    # Action-specific multipliers
    multipliers = {
        'high_speed': settings.get('COST_HIGH_SPEED_MULTIPLIER', 1.5),
        'sharp_turn': settings.get('COST_SHARP_TURN_MULTIPLIER', 1.3),
        'pursuit': settings.get('COST_PURSUIT_MULTIPLIER', 1.2),
        'attack': settings.get('COST_ATTACK_BASE', 3.0) / max(0.1, base_cost),
        'mating': settings.get('COST_MATING_BASE', 5.0) / max(0.1, base_cost),
        'idle': 0.7,
        'normal': 1.0,
    }

    action_multiplier = multipliers.get(action_type, 1.0)

    return base_cost * size_factor * interaction_factor * action_multiplier


def compute_combined_modifiers(agent, settings):
    """Compute all modifiers and combine them into final effective values.

    Returns a dict with all combined modifiers for use by other systems.
    """
    size_mods = compute_size_modifiers(agent, settings)
    age_mods = compute_age_modifiers(agent, settings)
    state_mods = compute_internal_state_modifiers(agent, settings)
    morph_mods = compute_morphology_modifiers(agent, settings)

    # Combine modifiers (multiplicative)
    combined = {
        # Speed: affected by size, age, internal state, morphology
        'effective_speed': (
            size_mods['speed_modifier'] *
            age_mods['speed_modifier'] *
            state_mods['speed_modifier'] *
            morph_mods['speed_modifier']
        ),

        # Turn rate: affected by size, morphology
        'effective_turn_rate': (
            size_mods['turn_modifier'] *
            morph_mods['turn_modifier']
        ),

        # Attack power: affected by size, age experience, internal state
        'effective_attack': (
            size_mods['attack_modifier'] *
            age_mods['experience_modifier'] *
            state_mods['attack_modifier']
        ),

        # Damage reduction from armor
        'damage_reduction': morph_mods['damage_reduction'],

        # Metabolic rate: affected by size, morphology
        'effective_metabolism': (
            size_mods['metabolic_modifier'] *
            morph_mods['metabolic_modifier']
        ),

        # Effort capacity: affected by internal state and age
        'effective_effort_capacity': (
            state_mods['effort_capacity'] *
            age_mods['stamina_modifier']
        ),

        # Stress-induced boost
        'stress_boost': state_mods['stress_boost'],

        # Perception range modifier
        'perception_modifier': size_mods['perception_modifier'],

        # Reproduction modifier from age
        'reproduction_modifier': age_mods['reproduction_modifier'],

        # Raw modifiers for detailed access
        'size_mods': size_mods,
        'age_mods': age_mods,
        'state_mods': state_mods,
        'morph_mods': morph_mods,
    }

    return combined


def apply_sensory_noise(inputs, settings):
    """Apply sensory imperfection to neural network inputs.

    Includes:
    - Gaussian noise on sector signals
    - Random dropout (missed detections)
    - Internal state perception noise

    Returns modified inputs list.
    """
    if not settings.get('SENSORY_NOISE_ENABLED', True):
        return inputs

    inputs = list(inputs)  # Make a copy

    noise_std = settings.get('VISION_NOISE_STD', 0.05)
    dropout_rate = settings.get('SENSOR_DROPOUT_RATE', 0.05)
    internal_noise = settings.get('INTERNAL_STATE_NOISE', 0.03)

    # Apply noise and dropout to sector signals (inputs 0-14)
    for i in range(15):
        # Random dropout
        if random.random() < dropout_rate:
            inputs[i] = 0.0
        else:
            # Gaussian noise
            inputs[i] += random.gauss(0, noise_std)
            inputs[i] = max(-1, min(1, inputs[i]))

    # Apply noise to internal state signals (inputs 15-19)
    for i in range(15, 20):
        inputs[i] += random.gauss(0, internal_noise)
        inputs[i] = max(0, min(1, inputs[i]))

    return inputs


def update_context_signals(agent, dt, settings):
    """Update short-term context signals (time since events).

    Tracks:
    - Time since last food intake
    - Time since last damage received
    - Time since last mating

    These decay over time and can be used as additional inputs.
    """
    if not settings.get('CONTEXT_SIGNALS_ENABLED', False):
        return

    # Initialize if needed
    if not hasattr(agent, 'time_since_food'):
        agent.time_since_food = 10.0  # Start as if hungry
    if not hasattr(agent, 'time_since_damage'):
        agent.time_since_damage = 15.0  # Start as safe
    if not hasattr(agent, 'time_since_mating'):
        agent.time_since_mating = 20.0

    # Increment timers
    agent.time_since_food += dt
    agent.time_since_damage += dt
    agent.time_since_mating += dt

    # Cap at decay values
    food_decay = settings.get('TIME_SINCE_FOOD_DECAY', 10.0)
    damage_decay = settings.get('TIME_SINCE_DAMAGE_DECAY', 15.0)
    mating_decay = settings.get('TIME_SINCE_MATING_DECAY', 20.0)

    agent.time_since_food = min(agent.time_since_food, food_decay)
    agent.time_since_damage = min(agent.time_since_damage, damage_decay)
    agent.time_since_mating = min(agent.time_since_mating, mating_decay)


def get_context_signal_inputs(agent, settings):
    """Get normalized context signals as additional inputs.

    Returns list of 3 values in [0, 1]:
    - hunger_signal: Higher = longer since food (more hungry)
    - safety_signal: Higher = longer since damage (safer feeling)
    - mating_signal: Higher = longer since mating (more receptive)
    """
    if not settings.get('CONTEXT_SIGNALS_ENABLED', False):
        return []

    food_decay = settings.get('TIME_SINCE_FOOD_DECAY', 10.0)
    damage_decay = settings.get('TIME_SINCE_DAMAGE_DECAY', 15.0)
    mating_decay = settings.get('TIME_SINCE_MATING_DECAY', 20.0)

    time_since_food = getattr(agent, 'time_since_food', food_decay)
    time_since_damage = getattr(agent, 'time_since_damage', damage_decay)
    time_since_mating = getattr(agent, 'time_since_mating', mating_decay)

    # Add small noise for biological plausibility
    noise = settings.get('INTERNAL_STATE_NOISE', 0.03)

    hunger = time_since_food / food_decay + random.gauss(0, noise)
    safety = time_since_damage / damage_decay + random.gauss(0, noise)
    mating_receptivity = time_since_mating / mating_decay + random.gauss(0, noise)

    return [
        max(0, min(1, hunger)),
        max(0, min(1, safety)),
        max(0, min(1, mating_receptivity)),
    ]


def update_social_pressure(agent, world, settings, dt):
    """Update stress based on social pressure from nearby agents.

    Crowding increases stress. Larger/aggressive neighbors increase stress more.
    This creates emergent social dynamics through the stress system.
    """
    if not settings.get('SOCIAL_PRESSURE_ENABLED', True):
        return

    crowd_radius = settings.get('CROWD_STRESS_RADIUS', 50.0)
    crowd_threshold = settings.get('CROWD_STRESS_THRESHOLD', 3)
    crowd_rate = settings.get('CROWD_STRESS_RATE', 0.1)
    dominance_factor = settings.get('DOMINANCE_STRESS_FACTOR', 0.5)

    # Count nearby agents
    nearby = world.agent_grid.query_radius(agent.pos, crowd_radius, exclude=agent)
    nearby_count = sum(1 for a in nearby if a.alive)

    # Base crowding stress
    if nearby_count > crowd_threshold:
        crowd_stress = (nearby_count - crowd_threshold) * crowd_rate
    else:
        crowd_stress = 0.0

    # Dominance stress from larger/more aggressive neighbors
    own_threat = agent.phenotype.get('size', 6.0) * agent.phenotype.get('aggression', 1.0)
    dominance_stress = 0.0

    for other in nearby:
        if not other.alive:
            continue
        other_threat = other.phenotype.get('size', 6.0) * other.phenotype.get('aggression', 1.0)
        if other_threat > own_threat * 1.2:
            dominance_stress += (other_threat / own_threat - 1.0) * dominance_factor * 0.1

    # Apply social stress (added to existing stress system)
    total_social_stress = (crowd_stress + dominance_stress) * dt

    if not hasattr(agent, 'stress'):
        agent.stress = 0.0

    agent.stress += total_social_stress
    agent.stress = max(0, min(1, agent.stress))
