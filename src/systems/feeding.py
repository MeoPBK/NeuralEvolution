import config


def update_feeding(world, dt):
    """Handle agents eating nearby food."""
    for agent in world.agent_list:
        if not agent.alive:
            continue
        nearby_food = world.food_grid.query_radius(
            agent.pos, world.settings['EATING_DISTANCE']
        )
        for food in nearby_food:
            if not food.alive:
                continue
            agent.energy = min(world.settings['MAX_ENERGY'], agent.energy + food.energy)
            food.alive = False
            # Update dietary behavior to indicate food was eaten
            agent.update_dietary_behavior(attack_successful=False, ate_food=True)
            # Reset context signal for food (if context signals enabled)
            if hasattr(agent, 'time_since_food'):
                agent.time_since_food = 0.0
            break  # eat one food per tick
