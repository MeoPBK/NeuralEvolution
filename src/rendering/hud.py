"""
HUD (Heads-Up Display) module for the simulation.
This module handles the drawing of the side panel with statistics.
"""

import pygame
import math
import config
from .menu_Huddle.hud_main import draw_hud as draw_hud_refactored


def draw_hud(screen, simulation, font_s, font_m, font_l):
    """Wrapper function to maintain backward compatibility."""
    return draw_hud_refactored(screen, simulation, font_s, font_m, font_l)


def _draw_title(screen, font, text, x, y, color, width):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_title as func
    return func(screen, font, text, x, y, color, width)


def _draw_status_bar(screen, x, y, width, simulation):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_status_bar as func
    return func(screen, x, y, width, simulation)


def _draw_section_header(screen, font, text, x, y):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_section_header as func
    return func(screen, font, text, x, y)


def _draw_stat_row(screen, font, label, value, x, y, value_color):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_stat_row as func
    return func(screen, font, label, value, x, y, value_color)


def _draw_mini_bar(screen, font, name, value, max_val, x, y, bar_width, color):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_mini_bar as func
    return func(screen, font, name, value, max_val, x, y, bar_width, color)


def _draw_control_hint(screen, font, key, action, x, y):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_control_hint as func
    return func(screen, font, key, action, x, y)


def _draw_separator(screen, x, y, width):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _draw_separator as func
    return func(screen, x, y, width)


def _text(screen, font, text, x, y, color=None):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_components import _text as func
    return func(screen, font, text, x, y, color)


def _get_species_color(species_id):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_utils import _get_species_color as func
    return func(species_id)


def _get_species_name(species_id):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_utils import _get_species_name as func
    return func(species_id)


def _get_species_shape(species_id):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_utils import _get_species_shape as func
    return func(species_id)


def _draw_shape_indicator(screen, x, y, size, species_id, color):
    """Wrapper for backward compatibility."""
    from .menu_Huddle.hud_utils import _draw_shape_indicator as func
    return func(screen, x, y, size, species_id, color)