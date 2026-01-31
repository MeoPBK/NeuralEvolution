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

    # Apply habitat-specific movement modifiers
    habitat_preference = agent.phenotype.get('habitat_preference', 1.0)  # 0=aquatic, 1=amphibious, 2=terrestrial
    current_terrain = _get_current_terrain_type(agent, world)  # Determine if in water, on land, etc.

    # Apply habitat-specific penalties
    if current_terrain == 'water':
        # Apply penalty for terrestrial agents in water
        if habitat_preference >= 1.5:  # terrestrial (closer to 2.0)
            terrestial_penalty = settings.get('TERRESTRIAL_WATER_PENALTY', 0.6)
            base_effort_speed *= (1.0 - terrestial_penalty)
        elif habitat_preference <= 0.5:  # aquatic (closer to 0.0)
            # Aquatic agents get bonus in water
            aquatic_bonus = settings.get('AQUATIC_SWIMMING_EFFICIENCY', 2.0) - 1.0
            base_effort_speed *= (1.0 + aquatic_bonus)
        # Amphibious agents have no penalty in water
    elif current_terrain == 'land':
        # Apply penalty for aquatic agents on land
        if habitat_preference <= 0.5:  # aquatic (closer to 0.0)
            aquatic_penalty = settings.get('AQUATIC_TERRAIN_PENALTY', 0.7)
            base_effort_speed *= (1.0 - aquatic_penalty)
        elif habitat_preference >= 1.5:  # terrestrial (closer to 2.0)
            # Terrestrial agents get bonus on land
            terrestrial_bonus = settings.get('TERRESTRIAL_LAND_EFFICIENCY', 2.0) - 1.0
            base_effort_speed *= (1.0 + terrestrial_bonus)
        # Amphibious agents have no penalty on land

    # Apply stress boost if available
    stress_boost = modifiers.get('stress_boost', 0.0)
    effort_with_boost = min(1.0, base_effort_speed + stress_boost)

    # Apply effort capacity limit (exhaustion)
    effort_capacity = modifiers.get('effective_effort_capacity', 1.0)
    final_effort = effort_with_boost * effort_capacity

    # Calculate effective speed with all modifiers
    # Use habitat-specific base speed based on terrain
    current_terrain = _get_current_terrain_type(agent, world)
    if current_terrain == 'water':
        # Use the agent's specific water speed
        base_speed = agent.speed_in_water
    elif current_terrain == 'land':
        # Use the agent's specific land speed
        base_speed = agent.speed_on_land
    else:
        # Default to the general speed
        base_speed = agent.speed

    effective_speed = base_speed * final_effort * modifiers.get('effective_speed', 1.0)

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
    new_pos = _handle_collision(agent, new_pos, world, settings, dt)

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

        dist_sq = dx * dx + dy * dy
        if dist_sq > 0.01:  # Use squared distance to avoid sqrt when possible
            dist = math.sqrt(dist_sq)
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


def _handle_collision(agent, new_pos, world, settings, dt):
    """Handle collision with terrain obstacles."""
    has_terrain = hasattr(world, 'obstacle_list') and len(world.obstacle_list) > 0
    border_enabled = settings.get('BORDER_ENABLED', True)

    if not has_terrain:
        return new_pos

    agent_radius = agent.radius()
    agent_radius_sq = agent_radius * agent_radius  # Precompute squared radius
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

            # Check if agent is in water obstacle based on habitat preference
            if obstacle.obstacle_type in ['water_barrier', 'river', 'lake']:
                # Check if this is a polygon river/lake
                if hasattr(obstacle, 'river_polygon') and obstacle.river_polygon:
                    # Use polygon collision detection for rivers
                    in_water = obstacle._point_in_polygon(proposed_pos, obstacle.river_polygon) or \
                               obstacle._collides_with_polygon(proposed_pos, agent_radius)
                else:
                    # Use circle collision for regular water sources
                    in_water = obstacle.collides_with_circle(proposed_pos, agent_radius)

                if in_water:
                    # Mark that the agent is in water
                    agent.is_in_water = True

                    # All agents can enter water, but apply different speeds based on habitat preference
                    # Use the new speed_in_water property that incorporates genetic traits
                    habitat_pref = agent.phenotype.get('habitat_preference', 1.0)

                    if habitat_pref <= 0.5:  # aquatic (closer to 0.0)
                        # Aquatic agents use their specific water speed
                        agent.velocity = agent.velocity.normalized() * agent.speed_in_water
                    elif habitat_pref >= 1.5:  # terrestrial (closer to 2.0)
                        # Terrestrial agents use their specific water speed (typically slower)
                        agent.velocity = agent.velocity.normalized() * agent.speed_in_water
                    else:  # amphibious (around 1.0)
                        # Amphibious agents use their specific water speed
                        agent.velocity = agent.velocity.normalized() * agent.speed_in_water
            elif obstacle.obstacle_type in ['mountain', 'cliff', 'wall', 'rock', 'land']:
                # Check if this is a land obstacle that aquatic agents cannot enter
                habitat_preference = agent.phenotype.get('habitat_preference', 1.0)

                # Aquatic agents (habitat_preference closer to 0.0) cannot enter land obstacles
                if habitat_preference <= 0.5 and obstacle.obstacle_type in ['mountain', 'cliff', 'wall', 'rock', 'land']:
                    if obstacle.collides_with_circle(proposed_pos, agent_radius):
                        collision_occurred = True
                        # Push agent away from land obstacle
                        if hasattr(obstacle, 'get_push_vector'):
                            push = obstacle.get_push_vector(proposed_pos, agent_radius)
                            proposed_pos = proposed_pos + push
                        else:
                            # Fallback for rectangular obstacles
                            closest_x = max(obstacle.pos.x, min(proposed_pos.x, obstacle.pos.x + obstacle.width))
                            closest_y = max(obstacle.pos.y, min(proposed_pos.y, obstacle.pos.y + obstacle.height))

                            push_vector = Vector2(proposed_pos.x - closest_x, proposed_pos.y - closest_y)
                            distance_sq = push_vector.length_sq()  # Use squared distance

                            if distance_sq < agent_radius_sq:
                                distance = math.sqrt(distance_sq) if distance_sq > 0 else 0
                                if distance < 0.001:
                                    # If agent is stuck inside, push in opposite direction of velocity
                                    if agent.velocity.length_sq() > 0.001:
                                        push_direction = agent.velocity.normalized() * -1
                                    else:
                                        # If no velocity, push in a random direction
                                        push_direction = Vector2.random_unit()
                                    # Push far enough to clear the obstacle with extra margin
                                    push_vector = push_direction * (agent_radius + max(obstacle.width, obstacle.height)/2 + 5)
                                else:
                                    # Normalize and extend to push agent completely out with extra margin
                                    if distance > 0:
                                        push_vector = push_vector.normalized() * (agent_radius + 5)  # Increased margin from 1 to 5
                                    else:
                                        # If distance is zero, push in a random direction
                                        push_vector = Vector2.random_unit() * (agent_radius + 5)  # Increased margin

                                proposed_pos = Vector2(closest_x, closest_y) + push_vector
                # SPECIAL CASE: MOUNTAINS ARE COMPLETELY IMPASSABLE TO ALL AGENTS
                elif obstacle.obstacle_type == 'mountain':
                    if obstacle.collides_with_circle(proposed_pos, agent_radius):
                        collision_occurred = True
                        # Push agent away from mountain with extra force to ensure complete impassability
                        if hasattr(obstacle, 'get_push_vector'):
                            push = obstacle.get_push_vector(proposed_pos, agent_radius) * 3.0  # Triple the push force
                            proposed_pos = proposed_pos + push
                        else:
                            # Fallback for rectangular obstacles
                            closest_x = max(obstacle.pos.x, min(proposed_pos.x, obstacle.pos.x + obstacle.width))
                            closest_y = max(obstacle.pos.y, min(proposed_pos.y, obstacle.pos.y + obstacle.height))

                            push_vector = Vector2(proposed_pos.x - closest_x, proposed_pos.y - closest_y)
                            distance_sq = push_vector.length_sq()  # Use squared distance

                            if distance_sq < agent_radius_sq:
                                distance = math.sqrt(distance_sq) if distance_sq > 0 else 0
                                if distance < 0.001:
                                    # If agent is stuck inside, push in opposite direction of velocity with extra force
                                    if agent.velocity.length_sq() > 0.001:
                                        push_direction = agent.velocity.normalized() * -1
                                    else:
                                        # If no velocity, push in a random direction
                                        push_direction = Vector2.random_unit()
                                    # Push far enough to clear the obstacle with extra margin
                                    push_vector = push_direction * (agent_radius + max(obstacle.width, obstacle.height)/2 + 10)  # Increased margin
                                else:
                                    # Normalize and extend to push agent completely out with extra margin
                                    if distance > 0:
                                        push_vector = push_vector.normalized() * (agent_radius + 10)  # Increased margin
                                    else:
                                        # If distance is zero, push in a random direction
                                        push_vector = Vector2.random_unit() * (agent_radius + 10)  # Increased margin

                                proposed_pos = Vector2(closest_x, closest_y) + push_vector
            elif obstacle.collides_with_circle(proposed_pos, agent_radius):
                # Regular collision handling for other obstacles
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
                    distance_sq = push_vector.length_sq()  # Use squared distance

                    if distance_sq < agent_radius_sq:
                        distance = math.sqrt(distance_sq) if distance_sq > 0 else 0
                        if distance < 0.001:
                            # If agent is stuck inside, push in opposite direction of velocity
                            if agent.velocity.length_sq() > 0.001:
                                push_direction = agent.velocity.normalized() * -1
                            else:
                                # If no velocity, push in a random direction
                                push_direction = Vector2.random_unit()
                            # Push far enough to clear the obstacle with extra margin
                            push_vector = push_direction * (agent_radius + max(obstacle.width, obstacle.height)/2 + 5)
                        else:
                            # Normalize and extend to push agent completely out with extra margin
                            if distance > 0:
                                push_vector = push_vector.normalized() * (agent_radius + 5)  # Increased margin from 1 to 5
                            else:
                                # If distance is zero, push in a random direction
                                push_vector = Vector2.random_unit() * (agent_radius + 5)  # Increased margin

                        proposed_pos = Vector2(closest_x, closest_y) + push_vector

                # Additional check: ensure the new position doesn't still collide with the same obstacle
                # This prevents agents from getting stuck oscillating back and forth
                if obstacle.collides_with_circle(proposed_pos, agent_radius):
                    # If still colliding, apply additional push to ensure separation
                    if obstacle.obstacle_type == 'mountain':
                        # For mountains, use even more force to ensure complete impassability
                        if hasattr(obstacle, 'get_push_vector'):
                            additional_push = obstacle.get_push_vector(proposed_pos, agent_radius) * 4.0  # Quadruple the push
                            proposed_pos = proposed_pos + additional_push
                        else:
                            # Calculate direction from obstacle to agent for additional push
                            if obstacle.shape == 'circle':
                                # For circular obstacles, push away from center
                                dir_to_agent = (proposed_pos - obstacle.pos).normalized()
                                additional_push = dir_to_agent * (agent_radius + obstacle.radius + 15)  # Extra margin for mountains
                                proposed_pos = obstacle.pos + additional_push
                            else:
                                # For rectangular obstacles, use the push vector from above but with more force
                                closest_x = max(obstacle.pos.x, min(proposed_pos.x, obstacle.pos.x + obstacle.width))
                                closest_y = max(obstacle.pos.y, min(proposed_pos.y, obstacle.pos.y + obstacle.height))
                                repulsion_vec = Vector2(proposed_pos.x - closest_x, proposed_pos.y - closest_y)
                                distance_repulsion = repulsion_vec.length()
                                if distance_repulsion > 0:
                                    repulsion_dir = repulsion_vec.normalized()
                                    additional_push = repulsion_dir * (agent_radius + 15)  # Extra margin for mountains
                                    proposed_pos = Vector2(closest_x, closest_y) + additional_push
                                else:
                                    # If no clear direction, push in a random direction
                                    random_dir = Vector2.random_unit()
                                    additional_push = random_dir * (agent_radius + 15)  # Extra margin for mountains
                                    proposed_pos = proposed_pos + additional_push
                    else:
                        # For non-mountain obstacles, use the original logic
                        if hasattr(obstacle, 'get_push_vector'):
                            additional_push = obstacle.get_push_vector(proposed_pos, agent_radius) * 2.0  # Double the push
                            proposed_pos = proposed_pos + additional_push
                        else:
                            # Calculate direction from obstacle to agent for additional push
                            if obstacle.shape == 'circle':
                                # For circular obstacles, push away from center
                                dir_to_agent = (proposed_pos - obstacle.pos).normalized()
                                additional_push = dir_to_agent * (agent_radius + obstacle.radius + 5)  # Extra margin
                                proposed_pos = obstacle.pos + additional_push
                            else:
                                # For rectangular obstacles, use the push vector from above but with more force
                                closest_x = max(obstacle.pos.x, min(proposed_pos.x, obstacle.pos.x + obstacle.width))
                                closest_y = max(obstacle.pos.y, min(proposed_pos.y, obstacle.pos.y + obstacle.height))
                                repulsion_vec = Vector2(proposed_pos.x - closest_x, proposed_pos.y - closest_y)
                                distance_repulsion = repulsion_vec.length()
                                if distance_repulsion > 0:
                                    repulsion_dir = repulsion_vec.normalized()
                                    additional_push = repulsion_dir * (agent_radius + 5)  # Extra margin
                                    proposed_pos = Vector2(closest_x, closest_y) + additional_push
                                else:
                                    # If no clear direction, push in a random direction
                                    random_dir = Vector2.random_unit()
                                    additional_push = random_dir * (agent_radius + 5)
                                    proposed_pos = proposed_pos + additional_push

        if not collision_occurred:
            break

    # Update water exposure tracking
    if agent.is_in_water:
        # Increment time spent in water
        agent.time_in_water += dt
    else:
        # Reset time in water when not in water
        agent.time_in_water = 0.0
        agent.is_in_water = False

    # Apply penalties for extended time in water for non-aquatic agents
    if agent.is_in_water and agent.habitat_preference != 'aquatic':
        # Calculate penalty based on time in water
        max_underwater_time = 5.0  # seconds before severe penalties
        if agent.habitat_preference == 'amphibious':
            max_underwater_time = 10.0  # amphibious agents can stay longer

        # Apply increasing penalty as time underwater increases
        if agent.time_in_water > max_underwater_time:
            # Severe penalty for staying too long underwater
            agent.velocity = agent.velocity * 0.1  # Very slow
            # Apply severe energy drain when underwater too long
            if agent.habitat_preference == 'terrestrial':
                # Terrestrial agents take more severe penalties
                agent.energy -= agent.energy * 0.05 * dt  # Higher energy drain
                # Also increase recent damage to simulate stress
                agent.recent_damage += 0.05 * dt
            else:  # amphibious
                # Amphibious agents take moderate penalties
                agent.energy -= agent.energy * 0.02 * dt  # Moderate energy drain
        elif agent.time_in_water > max_underwater_time * 0.7:
            # Moderate penalty as they approach limit
            agent.velocity = agent.velocity * 0.4
            # Moderate energy drain
            if agent.habitat_preference == 'terrestrial':
                agent.energy -= agent.energy * 0.02 * dt  # Moderate energy drain for terrestrial
                # Add some recent damage for stress
                agent.recent_damage += 0.02 * dt
            else:  # amphibious
                agent.energy -= agent.energy * 0.01 * dt  # Light energy drain for amphibious

    # Reduce velocity if collision occurred
    if proposed_pos.x != new_pos.x or proposed_pos.y != new_pos.y:
        agent.velocity = agent.velocity * 0.1

    return proposed_pos


def _get_current_terrain_type(agent, world):
    """Determine the current terrain type for the agent based on position."""
    # Check if agent is in water
    for water_source in world.water_list:
        distance = (agent.pos - water_source.pos).length()
        if distance < water_source.radius:
            return 'water'

    # Check if agent is in specific terrain features (rivers, lakes, etc.)
    for obstacle in world.obstacle_list:
        if obstacle.obstacle_type in ['river', 'lake', 'water', 'water_barrier']:
            if obstacle.contains_point(agent.pos):
                return 'water'

    # Default to land if not in water
    return 'land'


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
