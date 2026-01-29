import config


def update_hydration(world, dt):
    """Drain hydration and allow drinking from water sources and rivers."""
    for agent in world.agent_list:
        if not agent.alive:
            continue

        # Drain hydration
        agent.hydration -= world.settings['HYDRATION_DRAIN_RATE'] * dt

        drinking = False

        # Check if within any water source radius (circular water sources)
        for water in world.water_list:
            dsq = agent.pos.distance_sq_to(water.pos)
            if dsq <= water.radius * water.radius:
                agent.hydration = min(
                    world.settings['MAX_HYDRATION'],
                    agent.hydration + world.settings['DRINK_RATE'] * dt
                )
                drinking = True
                break  # Only drink from one source per tick

        # Check if near any river/water_barrier obstacles (can drink from edges)
        if not drinking and hasattr(world, 'obstacle_list'):
            agent_radius = agent.radius() if hasattr(agent, 'radius') else 5
            drink_distance = agent_radius + 10  # Can drink when close to water edge

            for obstacle in world.obstacle_list:
                if obstacle.alive and obstacle.obstacle_type == 'water_barrier':
                    # Check if agent is close enough to the water obstacle edge to drink
                    # Find closest point on obstacle rectangle to agent
                    closest_x = max(obstacle.pos.x, min(agent.pos.x, obstacle.pos.x + obstacle.width))
                    closest_y = max(obstacle.pos.y, min(agent.pos.y, obstacle.pos.y + obstacle.height))

                    # Calculate distance to closest point
                    dx = agent.pos.x - closest_x
                    dy = agent.pos.y - closest_y
                    dist_sq = dx * dx + dy * dy

                    if dist_sq <= drink_distance * drink_distance:
                        # Agent is close enough to drink from the river
                        agent.hydration = min(
                            world.settings['MAX_HYDRATION'],
                            agent.hydration + world.settings['DRINK_RATE'] * dt * 0.8  # Slightly slower from rivers
                        )
                        drinking = True
                        break

        # Death by dehydration
        if agent.hydration <= 0:
            agent.die()
