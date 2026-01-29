"""
HUD Components module for the simulation.
Contains helper functions for drawing various HUD elements.
"""

import pygame
import math


def _draw_title(screen, font, text, x, y, color, width):
    """Draw centered title with subtle underline."""
    surf = font.render(text, True, color)
    text_x = x + (width - surf.get_width()) // 2
    screen.blit(surf, (text_x, y))
    line_y = y + surf.get_height() + 2
    pygame.draw.line(screen, (50, 60, 80), (x + 10, line_y), (x + width - 10, line_y), 1)


def _draw_status_bar(screen, x, y, width, simulation):
    """Draw simulation status bar with time and speed."""
    bar_rect = pygame.Rect(x, y, width, 16)
    pygame.draw.rect(screen, (35, 40, 50), bar_rect, border_radius=3)

    font = pygame.font.SysFont('monospace', 10)

    # Time on left
    time_text = font.render(f"T:{simulation.sim_time:.1f}s", True, (180, 180, 190))
    screen.blit(time_text, (x + 4, y + 2))

    # Speed/pause on right
    if simulation.paused:
        status_text = font.render("PAUSED", True, (255, 180, 80))
    else:
        status_text = font.render(f"{simulation.speed_multiplier:.1f}x", True, (120, 200, 120))
    screen.blit(status_text, (x + width - status_text.get_width() - 4, y + 2))


def _draw_section_header(screen, font, text, x, y):
    """Draw a section header."""
    color = (140, 150, 170)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def _draw_stat_row(screen, font, label, value, x, y, value_color):
    """Draw a stat label and value."""
    label_surf = font.render(f"{label}:", True, (120, 125, 135))
    value_surf = font.render(value, True, value_color)
    screen.blit(label_surf, (x, y))
    screen.blit(value_surf, (x + label_surf.get_width() + 3, y))


def _draw_mini_bar(screen, font, name, value, max_val, x, y, bar_width, color):
    """Draw a compact trait bar with value."""
    # Label
    label_surf = font.render(f"{name}:", True, (120, 125, 135))
    screen.blit(label_surf, (x, y))

    # Bar
    bar_x = x + 50
    bar_height = 8
    bar_actual_width = bar_width - 50
    pygame.draw.rect(screen, (40, 45, 55), (bar_x, y + 3, bar_actual_width, bar_height), border_radius=2)

    fill_width = int(bar_actual_width * min(1.0, value / max_val))
    if fill_width > 0:
        pygame.draw.rect(screen, color, (bar_x, y + 3, fill_width, bar_height), border_radius=2)

    # Value
    value_surf = font.render(f"{value:.1f}", True, (180, 180, 190))
    screen.blit(value_surf, (x + bar_width + 5, y))


def _draw_control_hint(screen, font, key, action, x, y):
    """Draw a control hint with key and action."""
    key_color = (100, 140, 180)
    action_color = (120, 125, 135)

    key_surf = font.render(f"[{key}]", True, key_color)
    action_surf = font.render(action, True, action_color)

    screen.blit(key_surf, (x, y))
    screen.blit(action_surf, (x + key_surf.get_width() + 3, y))


def _draw_separator(screen, x, y, width):
    """Draw a horizontal separator line."""
    pygame.draw.line(screen, (50, 55, 65), (x, y), (x + width, y), 1)


def _text(screen, font, text, x, y, color=None):
    """Simple text rendering helper."""
    if color is None:
        import config
        color = config.TEXT_COLOR
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


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
