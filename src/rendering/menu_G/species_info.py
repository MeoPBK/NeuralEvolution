"""
Species Information module for the genetics visualization.
Contains functions related to species data processing and display.
"""

import random
import math


def get_species_name(species_id):
    """Get a human-readable name for a species ID - Italian medieval names."""
    italian_medieval_names = [
        "Visconti", "Medici", "Este", "Sforza", "Gonzaga", "Farnese", "Pico", "Borgia",
        "Malatesta", "Montefeltro", "Doria", "Grimaldi", "Cybo", "Colonna", "Orsini",
        "Gentile", "Alberti", "Pazzi", "Salviati", "Rucellai", "Albizzi", "Capponi"
    ]
    return italian_medieval_names[species_id % len(italian_medieval_names)]


def get_species_color(species_id):
    """Get a color for a species using golden angle distribution."""
    hue = (species_id * 137.5) % 360
    h = hue / 360.0
    s, v = 0.75, 0.9

    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c

    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def get_species_shape(species_id):
    """Get the shape type for a species."""
    shapes = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']
    return shapes[species_id % len(shapes)]


def calculate_species_statistics(agents):
    """Calculate statistics for a group of agents belonging to a species."""
    if not agents:
        return {}
    
    # Calculate averages
    avg_speed = sum(a.speed for a in agents) / len(agents)
    avg_size = sum(a.size for a in agents) / len(agents)
    avg_aggression = sum(a.aggression for a in agents) / len(agents)
    avg_age = sum(a.age for a in agents) / len(agents)
    avg_generation = sum(a.generation for a in agents) / len(agents)
    avg_mutations = sum(a.total_mutations for a in agents) / len(agents)
    avg_offspring = sum(a.offspring_count for a in agents) / len(agents)
    avg_virus_res = sum(a.virus_resistance for a in agents) / len(agents)
    
    # Calculate dietary behaviors
    avg_herbivorous = sum(a.herbivorous_tendency for a in agents) / len(agents)
    avg_carnivorous = sum(a.carnivorous_tendency for a in agents) / len(agents)
    avg_hunting_success = sum(a.hunting_success_rate for a in agents) / len(agents)
    avg_herding_behavior = sum(a.herding_behavior for a in agents) / len(agents)
    
    # Count males/females
    males = sum(1 for a in agents if a.sex == 'male')
    females = len(agents) - males
    
    return {
        'avg_speed': avg_speed,
        'avg_size': avg_size,
        'avg_aggression': avg_aggression,
        'avg_age': avg_age,
        'avg_generation': avg_generation,
        'avg_mutations': avg_mutations,
        'avg_offspring': avg_offspring,
        'avg_virus_resistance': avg_virus_res,
        'avg_herbivorous': avg_herbivorous,
        'avg_carnivorous': avg_carnivorous,
        'avg_hunting_success': avg_hunting_success,
        'avg_herding_behavior': avg_herding_behavior,
        'males': males,
        'females': females,
        'count': len(agents)
    }


def get_representative_agent(agents):
    """Get a representative agent for a species (one with most mutations)."""
    if not agents:
        return None
    return max(agents, key=lambda a: a.total_mutations)


def calculate_mutation_hotspots(agents):
    """Calculate which weights vary most across agents in a species."""
    if len(agents) < 2 or not hasattr(agents[0], 'brain'):
        return {}

    # Collect all weights
    all_weights = []
    for agent in agents[:20]:  # Sample up to 20 agents for performance
        if hasattr(agent, 'brain'):
            weights = []
            # Flatten all weights
            for row in agent.brain.w_ih:
                weights.extend(row)
            weights.extend(agent.brain.b_h)
            for row in agent.brain.w_ho:
                weights.extend(row)
            weights.extend(agent.brain.b_o)
            all_weights.append(weights)

    if not all_weights:
        return {}

    # Calculate variance for each weight position
    n_weights = len(all_weights[0])
    variances = []
    for i in range(n_weights):
        values = [w[i] for w in all_weights]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        variances.append((i, variance))

    # Get top 10 most variable weights (mutation hotspots)
    variances.sort(key=lambda x: x[1], reverse=True)
    hotspots = {idx: var for idx, var in variances[:15] if var > 0.01}

    return hotspots


def _draw_shape_indicator(screen, x, y, size, species_id, color):
    """Draw a small shape indicator for a species."""
    shape = get_species_shape(species_id)

    if shape == 'circle':
        pygame.draw.circle(screen, color, (x, y), size // 2)
    elif shape == 'square':
        pygame.draw.rect(screen, color, (x - size//2, y - size//2, size, size))
    elif shape == 'triangle':
        points = [(x, y - size//2), (x - size//2, y + size//2), (x + size//2, y + size//2)]
        pygame.draw.polygon(screen, color, points)
    elif shape == 'diamond':
        points = [(x, y - size//2), (x + size//2, y), (x, y + size//2), (x - size//2, y)]
        pygame.draw.polygon(screen, color, points)
    elif shape == 'hexagon':
        points = [(x + size//2 * math.cos(math.radians(60*i - 30)),
                  y + size//2 * math.sin(math.radians(60*i - 30))) for i in range(6)]
        pygame.draw.polygon(screen, color, points)
    elif shape == 'parallelogram':
        offset = size * 0.25
        points = [
            (x - size//2 + offset, y - size//2),
            (x + size//2 + offset, y - size//2),
            (x + size//2 - offset, y + size//2),
            (x - size//2 - offset, y + size//2)
        ]
        pygame.draw.polygon(screen, color, points)
    elif shape == 'pentagon':
        points = [(x + size//2 * math.cos(math.radians(72*i - 90)),
                  y + size//2 * math.sin(math.radians(72*i - 90))) for i in range(5)]
        pygame.draw.polygon(screen, color, points)
    elif shape == 'star':
        star_points = []
        for i in range(5):
            # Outer point
            outer_angle = math.radians(72 * i - 90)
            star_points.append((x + size//2 * math.cos(outer_angle),
                               y + size//2 * math.sin(outer_angle)))
            # Inner point
            inner_angle = math.radians(72 * i + 36 - 90)
            star_points.append((x + size//4 * math.cos(inner_angle),
                               y + size//4 * math.sin(inner_angle)))

        pygame.draw.polygon(screen, color, star_points)
    else:
        pygame.draw.circle(screen, color, (x, y), size // 2)