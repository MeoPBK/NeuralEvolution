"""
Combat system using V2 neural network architecture.

Uses decoupled attack_drive and avoid_drive, with effort-scaled damage and energy costs.
Supports advanced modulation features (size effects, age effects, morphology traits).
"""
import config


def update_combat(world, dt, particle_system=None):
    """Resolve attacks between agents.

    Attack conditions (V2):
    - attack_drive > 0.5 (agent wants to attack)
    - attack_drive > avoid_drive (not fleeing)
    - Target within attack distance
    """
    settings = world.settings

    for agent in world.agent_list:
        if not agent.alive:
            continue

        # Get behavioral drives (V2 architecture)
        attack_drive = getattr(agent, 'attack_drive', 0.0)
        avoid_drive = getattr(agent, 'avoid_drive', 0.0)
        effort = getattr(agent, 'effort', 0.5)

        # Attack conditions: want to attack AND not fleeing
        if attack_drive <= 0.5:
            continue
        if attack_drive <= avoid_drive:
            continue  # Can't attack while fleeing

        # Find nearest agent within attack distance
        target = world.agent_grid.query_nearest(
            agent.pos, settings['ATTACK_DISTANCE'], exclude=agent
        )
        if target is None or not target.alive:
            continue

        # Get modifiers from agent (set by movement system)
        modifiers = getattr(agent, 'current_modifiers', {})
        effective_attack = modifiers.get('effective_attack', 1.0)

        # Calculate damage with effort scaling and modifiers
        size_ratio = agent.size / max(0.1, target.size)
        effort_damage_scale = settings.get('EFFORT_DAMAGE_SCALE', 0.5)
        damage_multiplier = 0.5 + effort * effort_damage_scale

        base_damage = size_ratio * agent.aggression * settings['ATTACK_DAMAGE_BASE']
        damage = base_damage * damage_multiplier * effective_attack * dt

        # Apply target's damage reduction (from armor)
        target_modifiers = getattr(target, 'current_modifiers', {})
        damage_reduction = target_modifiers.get('damage_reduction', 0.0)
        damage *= (1.0 - damage_reduction)

        # Energy cost with action cost system
        base_cost = settings['ATTACK_ENERGY_COST']
        if settings.get('ACTION_COSTS_ENABLED', False):
            from src.systems.modulation import compute_action_costs
            energy_cost = compute_action_costs(agent, 'attack', base_cost, settings) * dt
        else:
            effort_energy_scale = settings.get('EFFORT_ENERGY_SCALE', 1.5)
            energy_cost = base_cost * (0.5 + effort * effort_energy_scale) * dt

        agent.energy -= energy_cost

        # Apply damage to target
        target.energy -= damage

        # Track recent damage on target (for stress system)
        if not hasattr(target, 'recent_damage'):
            target.recent_damage = 0.0
        target.recent_damage += damage * 0.1  # Scaled for stress calculation

        # Reset context signal for damage (if context signals enabled)
        if hasattr(target, 'time_since_damage'):
            target.time_since_damage = 0.0

        # Add fighting particles when attack occurs
        if particle_system:
            mid_x = (agent.pos.x + target.pos.x) / 2
            mid_y = (agent.pos.y + target.pos.y) / 2
            # More particles for high-effort attacks
            particle_count = int(3 + effort * 5)
            particle_system.add_fighting_particles((mid_x, mid_y), count=particle_count)

        # Check for kill
        if target.energy <= 0:
            target.die()

            # Killer gains energy from cannibalism
            energy_gain = settings['KILL_ENERGY_GAIN']
            if agent != target:
                energy_gain += settings.get('CANNIBALISM_ENERGY_BONUS', 20.0)

            agent.energy = min(settings['MAX_ENERGY'], agent.energy + energy_gain)

            # Reset context signal for food (kill provides energy like food)
            if hasattr(agent, 'time_since_food'):
                agent.time_since_food = 0.0

            # Update dietary behavior
            agent.update_dietary_behavior(attack_successful=True, ate_food=False)

            # Update carnivorous tendency
            if agent != target:
                agent.carnivorous_tendency += 0.05
