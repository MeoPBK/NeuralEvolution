"""
HUD Utilities module for the simulation.
Contains utility functions for HUD elements.
"""

import pygame
import math


def _get_species_color(species_id):
    """Get color for a species using golden angle distribution."""
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


def _get_species_name(species_id):
    """Get a human-readable name for a species ID - Italian medieval names."""
    names = [
        "Visconti", "Medici", "Este", "Sforza", "Gonzaga", "Farnese", "Pico", "Borgia",
        "Malatesta", "Montefeltro", "Doria", "Grimaldi", "Cybo", "Colonna", "Orsini",
        "Gentile", "Alberti", "Pazzi", "Salviati", "Rucellai", "Albizzi", "Capponi"
    ]
    return names[species_id % len(names)]


def _get_species_shape(species_id):
    """Get the shape type for a species."""
    shapes = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']
    return shapes[species_id % len(shapes)]


def _draw_shape_indicator(screen, x, y, size, species_id, color):
    """Draw a small shape indicator for a species."""
    shape = _get_species_shape(species_id)

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