import config


def update_feeding(world, dt):
    """Handle agents eating nearby food."""
    for agent in world.agent_list:
        if not agent.alive:
            continue

        # Only herbivores and omnivores can eat regular food
        if not agent.can_eat_plants():
            continue

        nearby_food = world.food_grid.query_radius(
            agent.pos, world.settings['EATING_DISTANCE']
        )
        for food in nearby_food:
            if not food.alive:
                continue

            # Apply diet-specific energy conversion efficiency
            base_energy = food.energy
            diet_type = agent.diet_type_numeric

            # Apply diet-specific food preference and conversion efficiency
            if diet_type <= 0.5:  # Carnivore (though carnivores can't eat plants)
                # This shouldn't happen since carnivores can't eat plants, but just in case
                food_preference = agent.phenotype.get('DIET_FOOD_PREFERENCE_CARNIVORE', 1.5)
                energy_conversion = agent.diet_energy_conversion_rate
                # Carnivores get little benefit from plant food
                adjusted_energy = base_energy * 0.3  # Very inefficient for carnivores to eat plants
            elif diet_type >= 1.5:  # Herbivore
                # Apply herbivore-specific food preference and conversion
                food_preference = agent.phenotype.get('DIET_FOOD_PREFERENCE_HERBIVORE', 1.5)
                energy_conversion = agent.diet_energy_conversion_rate
                # Adjust energy based on preference (higher preference = more efficient)
                adjusted_energy = base_energy * (0.7 + 0.3 * food_preference / 2.0)
            else:  # Omnivore
                # Apply omnivore-specific food preference and conversion
                food_preference = agent.phenotype.get('DIET_FOOD_PREFERENCE_OMNIVORE', 1.0)
                energy_conversion = agent.diet_energy_conversion_rate
                # Adjust energy based on preference (higher preference = more efficient)
                adjusted_energy = base_energy * (0.8 + 0.2 * food_preference / 2.0)

            # Apply the diet-specific energy conversion
            final_energy = adjusted_energy * energy_conversion
            agent.energy = min(world.settings['MAX_ENERGY'], agent.energy + final_energy)

            food.alive = False
            # Update dietary behavior to indicate food was eaten
            agent.update_dietary_behavior(attack_successful=False, ate_food=True)
            # Reset context signal for food (if context signals enabled)
            if hasattr(agent, 'time_since_food'):
                agent.time_since_food = 0.0
            break  # eat one food per tick
