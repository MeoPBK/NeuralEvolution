"""
Movement system using V2 neural network architecture.

Uses sector-based sensing (24 inputs) and decoupled behavioral drives (6 outputs).
"""
import math
from src.utils.vector import Vector2
from src.systems.sensing import compute_sector_inputs, update_agent_stress
from src.nn.brain_phenotype import create_memory_buffer
import config


def update_movement(world, dt):
    """Update movement for all agents using neural network outputs."""
    from src.systems.modulation import update_context_signals, update_social_pressure

    for agent in world.agent_list:
        if not agent.alive:
            continue

        # Update stress level (base system)
        update_agent_stress(agent, world, world.settings, dt)

        # Update social pressure stress (advanced feature)
        update_social_pressure(agent, world, world.settings, dt)

        # Update context signals (advanced feature)
        update_context_signals(agent, dt, world.settings)

        # Process movement
        _move_agent(agent, world, dt)


def _move_agent(agent, world, dt):
    """Compute NN inputs, run forward pass, apply outputs."""
    settings = world.settings

    # Compute sector-based inputs (24 values)
    inputs = compute_sector_inputs(agent, world, settings)

    # If n-step memory is enabled, append past hidden states
    if settings.get('N_STEP_MEMORY_ENABLED', False):
        if not hasattr(agent, 'memory_buffer') or agent.memory_buffer is None:
            agent.memory_buffer = create_memory_buffer(settings)

        if agent.memory_buffer:
            memory_inputs = agent.memory_buffer.get_flat()
            inputs = inputs + memory_inputs

    # Run forward pass through brain
    outputs = agent.brain.forward(inputs)

    # If using RNN with n-step memory, store current hidden state
    if settings.get('N_STEP_MEMORY_ENABLED', False) and hasattr(agent, 'memory_buffer'):
        if agent.memory_buffer and hasattr(agent.brain, 'get_hidden_state'):
            agent.memory_buffer.push(agent.brain.get_hidden_state())

    # Extract and scale outputs (6 values)
    move_x = outputs[0]  # -1 to 1
    move_y = outputs[1]  # -1 to 1
    avoid_drive = (outputs[2] + 1) / 2  # Scale to 0-1
    attack_drive = (outputs[3] + 1) / 2  # Scale to 0-1
    mate_desire = (outputs[4] + 1) / 2   # Scale to 0-1
    effort = (outputs[5] + 1) / 2        # Scale to 0-1

    # Store outputs for other systems
    agent.avoid_drive = avoid_drive
    agent.attack_drive = attack_drive
    agent.mate_desire = mate_desire
    agent.effort = effort

    # Legacy compatibility
    agent.attack_intent = attack_drive - avoid_drive  # Positive = attack, negative = flee

    # Store the neural network inputs and outputs for visualization
    agent.last_nn_inputs = inputs[:24]  # Store base inputs only
    agent.last_nn_outputs = outputs[:]

    # Store the hidden layer activations for visualization
    if hasattr(agent.brain, 'last_hidden_activations'):
        agent.last_hidden_activations = agent.brain.last_hidden_activations[:]

    # Apply movement direction
    desired = Vector2(move_x, move_y)

    # Modify movement based on behavioral drives
    desired = _apply_behavioral_drives(agent, desired, world, settings)

    # === Compute effective speed with all modifiers ===
    from src.systems.modulation import compute_combined_modifiers

    modifiers = compute_combined_modifiers(agent, settings)

    # Base speed with effort scaling
    effort_scale = settings.get('EFFORT_SPEED_SCALE', 1.0)
    base_effort_speed = 0.3 + 0.7 * effort * effort_scale

    # Apply stress boost if available
    stress_boost = modifiers.get('stress_boost', 0.0)
    effort_with_boost = min(1.0, base_effort_speed + stress_boost)

    # Apply effort capacity limit (exhaustion)
    effort_capacity = modifiers.get('effective_effort_capacity', 1.0)
    final_effort = effort_with_boost * effort_capacity

    # Calculate effective speed with all modifiers
    effective_speed = agent.speed * final_effort * modifiers.get('effective_speed', 1.0)

    # Store modifiers for use by other systems
    agent.current_modifiers = modifiers

    if desired.length_sq() > 0.001:
        desired = desired.normalized() * effective_speed
    else:
        desired = Vector2(0, 0)

    # Smooth steering toward desired velocity (affected by turn rate modifier)
    turn_modifier = modifiers.get('effective_turn_rate', 1.0)
    steer_strength = settings['STEER_STRENGTH'] * 3.0 * turn_modifier

    steer = desired - agent.velocity
    steer = steer.limit(steer_strength)
    agent.velocity = agent.velocity + steer
    agent.velocity = agent.velocity.limit(effective_speed)

    # Calculate new position
    new_pos = agent.pos + agent.velocity * (dt * 60)

    # Check for terrain obstacles
    new_pos = _handle_collision(agent, new_pos, world, settings)

    agent.pos = new_pos

    # Handle world boundaries
    _handle_boundaries(agent, world, settings)

    # Update region if the agent has moved to a new region
    agent.update_region(settings)


def _apply_behavioral_drives(agent, base_movement, world, settings):
    """Modify movement based on avoid and approach drives."""
    result = base_movement

    # Find nearest agent for behavioral responses
    nearest_agent = world.agent_grid.query_nearest(
        agent.pos, agent.vision_range, exclude=agent
    )

    if nearest_agent and nearest_agent.alive:
        # Direction to nearest agent
        dx = nearest_agent.pos.x - agent.pos.x
        dy = nearest_agent.pos.y - agent.pos.y

        # Handle toroidal wrapping
        world_w = settings.get('WORLD_WIDTH', 1200)
        world_h = settings.get('WORLD_HEIGHT', 600)
        if abs(dx) > world_w / 2:
            dx = dx - math.copysign(world_w, dx)
        if abs(dy) > world_h / 2:
            dy = dy - math.copysign(world_h, dy)

        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0.1:
            agent_dir = Vector2(dx / dist, dy / dist)

            # Apply avoidance (flee from threats)
            if agent.avoid_drive > 0.3:
                flee_strength = (agent.avoid_drive - 0.3) * 1.5
                flee_dir = agent_dir * -1
                result = result + flee_dir * flee_strength

            # Apply approach (for potential attack or mating)
            if agent.attack_drive > 0.5 or agent.mate_desire > 0.5:
                approach_strength = max(agent.attack_drive, agent.mate_desire) - 0.5
                result = result + agent_dir * approach_strength * 0.5

    return result


def _handle_collision(agent, new_pos, world, settings):
    """Handle collision with terrain obstacles."""
    has_terrain = hasattr(world, 'obstacle_list') and len(world.obstacle_list) > 0
    border_enabled = settings.get('BORDER_ENABLED', True)

    if not has_terrain:
        return new_pos

    agent_radius = agent.radius()
    proposed_pos = new_pos

    # Multiple collision resolution passes
    for _ in range(3):
        collision_occurred = False

        for obstacle in world.obstacle_list:
            if not obstacle.alive:
                continue

            # Skip border walls if border is disabled
            if not border_enabled and obstacle.obstacle_type == 'wall':
                continue

            if obstacle.collides_with_circle(proposed_pos, agent_radius):
                collision_occurred = True

                # Use obstacle's push vector method if available
                if hasattr(obstacle, 'get_push_vector'):
                    push = obstacle.get_push_vector(proposed_pos, agent_radius)
                    proposed_pos = proposed_pos + push
                else:
                    # Fallback for rectangular obstacles
                    closest_x = max(obstacle.pos.x, min(proposed_pos.x, obstacle.pos.x + obstacle.width))
                    closest_y = max(obstacle.pos.y, min(proposed_pos.y, obstacle.pos.y + obstacle.height))

                    push_vector = Vector2(proposed_pos.x - closest_x, proposed_pos.y - closest_y)
                    distance = push_vector.length()

                    if distance < agent_radius:
                        if distance < 0.001:
                            if agent.velocity.length_sq() > 0.001:
                                push_vector = agent.velocity.normalized() * -1 * (agent_radius + 2)
                            else:
                                push_vector = Vector2.random_unit() * (agent_radius + 2)
                        else:
                            push_vector = push_vector.normalized() * (agent_radius + 1)

                        proposed_pos = Vector2(closest_x, closest_y) + push_vector

        if not collision_occurred:
            break

    # Reduce velocity if collision occurred
    if proposed_pos.x != new_pos.x or proposed_pos.y != new_pos.y:
        agent.velocity = agent.velocity * 0.1

    return proposed_pos


def _handle_boundaries(agent, world, settings):
    """Handle world boundaries based on border setting."""
    world_width = settings['WORLD_WIDTH']
    world_height = settings['WORLD_HEIGHT']
    border_enabled = settings.get('BORDER_ENABLED', True)

    if border_enabled:
        # Keep agent within bounds (borders block)
        agent_radius = agent.radius()
        margin = agent_radius + 2
        agent.pos.x = max(margin, min(world_width - margin, agent.pos.x))
        agent.pos.y = max(margin, min(world_height - margin, agent.pos.y))
    else:
        # Wrap around world edges (no borders)
        if agent.pos.x < 0:
            agent.pos.x += world_width
        elif agent.pos.x >= world_width:
            agent.pos.x -= world_width

        if agent.pos.y < 0:
            agent.pos.y += world_height
        elif agent.pos.y >= world_height:
            agent.pos.y -= world_height
