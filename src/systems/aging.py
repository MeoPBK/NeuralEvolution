import config


def update_aging(world, dt, settings):
    """Age all agents and kill those past max age."""
    for agent in world.agent_list:
        if not agent.alive:
            continue
        agent.age += dt
        agent.reproduction_cooldown = max(0, agent.reproduction_cooldown - dt)
        agent.somatic_mutation_timer = max(0, agent.somatic_mutation_timer - dt)
        # Use the minimum of the global setting and the genetic max_age
        global_max_age = settings['MAX_AGE']
        genetic_max_age = agent.max_age
        max_age = min(global_max_age, genetic_max_age)
        if agent.age >= max_age:
            agent.die()
