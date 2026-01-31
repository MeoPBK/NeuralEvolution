"""
Water exposure system for handling habitat-specific water effects.
Terrestrial agents suffer from water exposure, while aquatic agents thrive.
"""

import config


def update_water_exposure(world, dt):
    """Apply water exposure effects based on agent habitat preferences."""
    for agent in world.agent_list:
        if not agent.alive:
            continue

        # Check if agent is in water
        in_water = False
        agent_radius = agent.radius() if hasattr(agent, 'radius') else 5
        
        # Check water sources
        for water in world.water_list:
            dsq = agent.pos.distance_sq_to(water.pos)
            if dsq <= water.radius * water.radius:
                in_water = True
                break
        
        # Check river/obstacle water if not already in water
        if not in_water and hasattr(world, 'obstacle_list'):
            for obstacle in world.obstacle_list:
                if obstacle.alive and obstacle.obstacle_type in ['water_barrier', 'river', 'lake']:
                    # Check if this is a polygon river/lake
                    if hasattr(obstacle, 'river_polygon') and obstacle.river_polygon:
                        # Use polygon collision detection for rivers
                        if obstacle._point_in_polygon(agent.pos, obstacle.river_polygon):
                            in_water = True
                            break
                        # Also check if agent is close to the river boundary
                        elif obstacle._collides_with_polygon(agent.pos, agent_radius):
                            in_water = True
                            break
                    else:
                        # Find closest point on obstacle rectangle to agent
                        closest_x = max(obstacle.pos.x, min(agent.pos.x, obstacle.pos.x + obstacle.width))
                        closest_y = max(obstacle.pos.y, min(agent.pos.y, obstacle.pos.y + obstacle.height))

                        # Calculate distance to closest point
                        dx = agent.pos.x - closest_x
                        dy = agent.pos.y - closest_y
                        dist_sq = dx * dx + dy * dy

                        if dist_sq <= (agent_radius + 5) * (agent_radius + 5):  # Within 5 units of water
                            in_water = True
                            break

        # Initialize water exposure timer if not already present
        if not hasattr(agent, 'water_exposure_time'):
            agent.water_exposure_time = 0.0
        if not hasattr(agent, 'land_exposure_time'):
            agent.land_exposure_time = 0.0

        # Apply habitat-specific effects
        if in_water:
            # Reset land exposure time when in water
            agent.land_exposure_time = 0.0

            # Get numeric habitat preference (0.0 = aquatic, 1.0 = amphibious, 2.0 = terrestrial)
            habitat_pref = agent.phenotype.get('habitat_preference', 1.0)

            if habitat_pref >= 1.5:  # terrestrial (closer to 2.0)
                # Terrestrial agents suffer in water - accumulate exposure time
                agent.water_exposure_time += dt
                # Apply penalty based on settings
                water_penalty = world.settings.get('TERRESTRIAL_WATER_PENALTY', 0.6)
                # Apply increasing penalty based on exposure time
                exposure_factor = min(2.0, agent.water_exposure_time / 5.0)  # Starts affecting after 5 seconds
                agent.hydration -= world.settings.get('HYDRATION_DRAIN_RATE', config.HYDRATION_DRAIN_RATE) * dt * (1.0 + exposure_factor * water_penalty)

                # Kill if exposure is too long
                max_underwater_time = 15.0  # Default time before death
                if habitat_pref >= 1.5:  # terrestrial
                    max_underwater_time = 10.0  # Terrestrial agents die faster in water
                elif habitat_pref <= 0.5:  # aquatic
                    max_underwater_time = 30.0  # Aquatic agents can stay longer in water
                else:  # amphibious
                    max_underwater_time = 15.0  # Amphibious agents have moderate tolerance

                if agent.water_exposure_time > max_underwater_time:
                    agent.die()

            elif habitat_pref <= 0.5:  # aquatic (closer to 0.0)
                # Aquatic agents benefit from water - reset exposure time and hydrate faster
                agent.water_exposure_time = 0.0
                if agent.hydration < world.settings.get('MAX_HYDRATION', config.MAX_HYDRATION):
                    swim_efficiency = world.settings.get('AQUATIC_SWIMMING_EFFICIENCY', 2.0)
                    agent.hydration = min(
                        world.settings.get('MAX_HYDRATION', config.MAX_HYDRATION),
                        agent.hydration + world.settings.get('DRINK_RATE', config.DRINK_RATE) * dt * swim_efficiency
                    )
            else:  # amphibious (around 1.0)
                # Amphibious agents have normal hydration rate in water
                agent.water_exposure_time = 0.0
                if agent.hydration < world.settings.get('MAX_HYDRATION', config.MAX_HYDRATION):
                    agent.hydration = min(
                        world.settings.get('MAX_HYDRATION', config.MAX_HYDRATION),
                        agent.hydration + world.settings.get('DRINK_RATE', config.DRINK_RATE) * dt
                    )
        else:
            # Outside water - reset water exposure time
            agent.water_exposure_time = 0.0

            # Get numeric habitat preference (0.0 = aquatic, 1.0 = amphibious, 2.0 = terrestrial)
            habitat_pref = agent.phenotype.get('habitat_preference', 1.0)

            if habitat_pref <= 0.5:  # aquatic (closer to 0.0)
                # Aquatic agents suffer outside water - accumulate land exposure time
                agent.land_exposure_time += dt
                # Apply penalty based on settings
                land_penalty = world.settings.get('AQUATIC_TERRAIN_PENALTY', 0.7)
                dehydration_factor = min(2.0, agent.land_exposure_time / 10.0)  # Starts affecting after 10 seconds
                agent.hydration -= world.settings.get('HYDRATION_DRAIN_RATE', config.HYDRATION_DRAIN_RATE) * dt * (1.0 + dehydration_factor * land_penalty)

                # Kill if exposure is too long
                max_land_time = 20.0  # Default time before death
                if habitat_pref <= 0.5:  # aquatic
                    max_land_time = 15.0  # Aquatic agents die faster out of water
                elif habitat_pref >= 1.5:  # terrestrial
                    max_land_time = 30.0  # Terrestrial agents can stay longer out of water
                else:  # amphibious
                    max_land_time = 20.0  # Amphibious agents have moderate tolerance

                if agent.land_exposure_time > max_land_time:
                    agent.die()
            elif habitat_pref >= 1.5:  # terrestrial (closer to 2.0)
                # Terrestrial agents have normal dehydration rate outside water
                agent.land_exposure_time = 0.0
                agent.hydration -= world.settings.get('HYDRATION_DRAIN_RATE', config.HYDRATION_DRAIN_RATE) * dt
            else:  # amphibious (around 1.0)
                # Amphibious agents have normal dehydration rate outside water
                agent.land_exposure_time = 0.0
                agent.hydration -= world.settings.get('HYDRATION_DRAIN_RATE', config.HYDRATION_DRAIN_RATE) * dt