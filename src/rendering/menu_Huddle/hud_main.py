"""
Main HUD (Heads-Up Display) module for the simulation.
This module handles the primary drawing of the HUD panel with statistics.
"""

import pygame
import math
import config
from .hud_components import (
    _draw_title,
    _draw_status_bar,
    _draw_section_header,
    _draw_stat_row,
    _draw_mini_bar,
    _draw_control_hint,
    _draw_separator,
    _text,
    _get_species_color,
    _get_species_name,
    _get_species_shape,
    _draw_shape_indicator
)


def draw_hud(screen, simulation, font_s, font_m, font_l):
    """Draw the side panel with statistics - responsive to window size."""
    screen_width, screen_height = screen.get_size()
    world_width = simulation.settings.get('WORLD_WIDTH', config.WORLD_WIDTH)
    scale_x = getattr(simulation, 'renderer', None) and getattr(simulation.renderer, 'scale_x', 1.0) or 1.0
    world_width_scaled = int(world_width * scale_x)
    hud_width = simulation.settings.get('HUD_WIDTH', config.HUD_WIDTH)

    # Calculate HUD position - adapt to screen size
    hud_x = min(world_width_scaled, screen_width - hud_width)

    # Calculate available height and adapt content
    available_height = screen_height - 20
    compact_mode = available_height < 600

    # Draw HUD background panel with gradient effect
    hud_rect = pygame.Rect(hud_x - 5, 0, hud_width + 10, screen_height)
    pygame.draw.rect(screen, (25, 28, 35), hud_rect)
    pygame.draw.line(screen, (50, 55, 65), (hud_x - 5, 0), (hud_x - 5, screen_height), 2)

    # Padding and spacing
    padding = 8
    x = hud_x + padding
    y = 10
    line_height_s = 13 if compact_mode else 15
    line_height_m = 15 if compact_mode else 17
    section_gap = 5 if compact_mode else 8

    world = simulation.world
    stats = simulation.stats.latest

    # Title with accent
    title_color = (100, 150, 255)
    _draw_title(screen, font_l, "NEURAL EVOLUTION", x, y, title_color, hud_width - padding * 2)
    y += 22 if compact_mode else 26

    # Simulation status bar
    _draw_status_bar(screen, x, y, hud_width - padding * 2, simulation)
    y += 20 if compact_mode else 24

    # Separator
    _draw_separator(screen, x, y, hud_width - padding * 2)
    y += section_gap

    # Column positions
    col1_x = x
    col2_x = x + (hud_width - padding * 2) // 2

    # Gather all live agent data
    live_agents = [a for a in world.agent_list if a.alive]
    total_agents = len(live_agents)
    males = sum(1 for a in live_agents if a.sex == 'male')
    females = total_agents - males
    species_count = len(set(a.species_id for a in live_agents))

    # === POPULATION SECTION ===
    _draw_section_header(screen, font_m, "POPULATION", x, y)
    y += line_height_m

    _draw_stat_row(screen, font_s, "Agents", str(total_agents), col1_x, y, config.GRAPH_AGENT_COLOR)
    _draw_stat_row(screen, font_s, "Species", str(species_count), col2_x, y, (180, 180, 220))
    y += line_height_s

    _draw_stat_row(screen, font_s, "Males", str(males), col1_x, y, (100, 150, 255))
    _draw_stat_row(screen, font_s, "Females", str(females), col2_x, y, (255, 130, 180))
    y += line_height_s

    _draw_stat_row(screen, font_s, "Food", str(len(world.food_list)), col1_x, y, config.FOOD_COLOR)
    _draw_stat_row(screen, font_s, "Water", str(len(world.water_list)), col2_x, y, config.WATER_COLOR)
    y += line_height_s + section_gap

    _draw_separator(screen, x, y, hud_width - padding * 2)
    y += section_gap

    # === BEHAVIOR SECTION ===
    if total_agents > 0:
        _draw_section_header(screen, font_m, "BEHAVIOR", x, y)
        y += line_height_m

        # Count behavioral states
        attacking = sum(1 for a in live_agents if a.attack_intent > 0.5)
        fleeing = sum(1 for a in live_agents if a.attack_intent < -0.5)
        mating = sum(1 for a in live_agents if a.mate_desire > 0.5)
        neutral = total_agents - attacking - fleeing - mating

        _draw_stat_row(screen, font_s, "Attack", str(attacking), col1_x, y, (220, 80, 80))
        _draw_stat_row(screen, font_s, "Flee", str(fleeing), col2_x, y, (220, 180, 80))
        y += line_height_s

        _draw_stat_row(screen, font_s, "Mating", str(mating), col1_x, y, (255, 130, 180))
        _draw_stat_row(screen, font_s, "Neutral", str(neutral), col2_x, y, (150, 150, 160))
        y += line_height_s + section_gap

        _draw_separator(screen, x, y, hud_width - padding * 2)
        y += section_gap

    # === VITALS SECTION ===
    if total_agents > 0:
        _draw_section_header(screen, font_m, "AVG VITALS", x, y)
        y += line_height_m

        avg_energy = sum(a.energy for a in live_agents) / total_agents
        avg_hydration = sum(a.hydration for a in live_agents) / total_agents
        avg_age = sum(a.age for a in live_agents) / total_agents
        max_age_agent = max(live_agents, key=lambda a: a.age)

        max_energy = simulation.settings.get('MAX_ENERGY', 300)
        max_hydration = simulation.settings.get('MAX_HYDRATION', 150)

        bar_width = hud_width - padding * 2 - 60

        # Energy bar
        _draw_mini_bar(screen, font_s, "Energy", avg_energy, max_energy, x, y, bar_width, (100, 200, 100))
        y += line_height_s + 2

        # Hydration bar
        _draw_mini_bar(screen, font_s, "Hydra", avg_hydration, max_hydration, x, y, bar_width, (100, 150, 220))
        y += line_height_s + 2

        # Age stats
        _draw_stat_row(screen, font_s, "Avg Age", f"{avg_age:.1f}", col1_x, y, (180, 180, 190))
        _draw_stat_row(screen, font_s, "Oldest", f"{max_age_agent.age:.1f}", col2_x, y, (200, 180, 140))
        y += line_height_s + section_gap

        _draw_separator(screen, x, y, hud_width - padding * 2)
        y += section_gap

    # === TRAITS SECTION ===
    if total_agents > 0:
        _draw_section_header(screen, font_m, "AVG TRAITS", x, y)
        y += line_height_m

        bar_width = hud_width - padding * 2 - 60
        traits = [
            ("Speed", stats.avg_speed, 6.0, (100, 200, 100)),
            ("Size", stats.avg_size, 12.0, (100, 150, 200)),
            ("Aggr", stats.avg_aggression, 2.0, (200, 100, 100)),
        ]

        for name, value, max_val, color in traits:
            _draw_mini_bar(screen, font_s, name, value, max_val, x, y, bar_width, color)
            y += line_height_s + 2

        y += 2
        _draw_stat_row(screen, font_s, "Gen", str(stats.max_generation), col1_x, y, (180, 180, 220))
        _draw_stat_row(screen, font_s, "Diversity", f"{stats.genetic_diversity:.2f}", col2_x, y, (180, 180, 220))
        y += line_height_s + section_gap

        _draw_separator(screen, x, y, hud_width - padding * 2)
        y += section_gap
    else:
        _draw_section_header(screen, font_m, "STATUS", x, y)
        y += line_height_m
        _text(screen, font_m, "POPULATION EXTINCT", x, y, (255, 80, 80))
        y += line_height_m + section_gap
        _draw_separator(screen, x, y, hud_width - padding * 2)
        y += section_gap

    # === TOP SPECIES SECTION ===
    if species_count > 0 and not compact_mode:
        _draw_section_header(screen, font_m, "TOP SPECIES", x, y)
        y += line_height_m

        species_data = {}
        for agent in live_agents:
            sid = agent.species_id
            if sid not in species_data:
                species_data[sid] = {'count': 0, 'males': 0, 'females': 0, 'avg_energy': 0}
            species_data[sid]['count'] += 1
            species_data[sid]['avg_energy'] += agent.energy
            if agent.sex == 'male':
                species_data[sid]['males'] += 1
            else:
                species_data[sid]['females'] += 1

        # Calculate averages
        for sid, data in species_data.items():
            data['avg_energy'] /= data['count']

        sorted_species = sorted(species_data.items(), key=lambda item: item[1]['count'], reverse=True)[:4]

        for species_id, data in sorted_species:
            color = _get_species_color(species_id)
            name = _get_species_name(species_id)
            shape = _get_species_shape(species_id)

            # Draw species shape indicator
            _draw_shape_indicator(screen, x + 8, y + 6, 10, species_id, color)

            # Species name and count
            name_text = font_s.render(f"{name}", True, color)
            screen.blit(name_text, (x + 20, y))

            # Count and sex ratio
            count_text = font_s.render(f"{data['count']}", True, (200, 200, 210))
            ratio_text = font_s.render(f"M{data['males']}:F{data['females']}", True, (140, 140, 150))
            screen.blit(count_text, (col2_x - 5, y))
            screen.blit(ratio_text, (col2_x + 25, y))
            y += line_height_s

        y += section_gap
        _draw_separator(screen, x, y, hud_width - padding * 2)
        y += section_gap

    # === CONTROLS SECTION ===
    _draw_section_header(screen, font_m, "CONTROLS", x, y)
    y += line_height_m

    controls = [
        ("SPACE", "Pause"),
        ("\u2191\u2193", "Speed"),
        ("G", "Genetics"),
        ("S", "Stats"),
        ("H", "HideHUD"),
        ("F11", "Fullscr"),
        ("ESC", "Menu"),
        ("M/N", "Mtns"),
        ("R/T", "River"),
        ("L", "Lake"),
        ("D", "Diag"),
        ("C", "Clear"),
    ]

    # Draw controls in two columns
    for i, (key, action) in enumerate(controls):
        cx = col1_x if i % 2 == 0 else col2_x
        cy = y + (i // 2) * line_height_s
        _draw_control_hint(screen, font_s, key, action, cx, cy)
    y += (len(controls) // 2 + len(controls) % 2) * line_height_s