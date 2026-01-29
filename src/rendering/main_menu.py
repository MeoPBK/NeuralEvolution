#-*- coding: utf-8 -*-

"""
Main Menu for the Neural Network Evolution Simulation.
Provides access to new simulation, load simulation, settings, documentation, and exit.
"""

import pygame
import os
import json
from datetime import datetime

# UI Colors - Modern dark theme
BG_COLOR = (22, 25, 32)
PANEL_COLOR = (32, 36, 45)
CARD_COLOR = (40, 44, 55)
TEXT_COLOR = (220, 225, 235)
MUTED_COLOR = (120, 125, 140)
ACCENT_COLOR = (80, 140, 220)
ACCENT_HOVER = (100, 160, 240)
SUCCESS_COLOR = (70, 180, 100)
WARNING_COLOR = (220, 160, 50)
DANGER_COLOR = (200, 80, 80)
BORDER_COLOR = (55, 60, 75)

# Button rects (will be populated during draw)
button_rects = {}


def draw_main_menu(screen, font_large, font_med):
    """Draw the main menu screen."""
    global button_rects
    button_rects = {}

    screen_width, screen_height = screen.get_size()
    screen.fill(BG_COLOR)

    # Title area with gradient effect
    title_y = screen_height // 6

    # Main title
    title_font = pygame.font.SysFont('monospace', 42, bold=True)
    title = title_font.render("Neural Network Evolution", True, ACCENT_COLOR)
    title_x = screen_width // 2 - title.get_width() // 2
    screen.blit(title, (title_x, title_y))

    # Subtitle
    subtitle_font = pygame.font.SysFont('monospace', 18)
    subtitle = subtitle_font.render("A Genetic Algorithm Simulation", True, MUTED_COLOR)
    subtitle_x = screen_width // 2 - subtitle.get_width() // 2
    screen.blit(subtitle, (subtitle_x, title_y + 50))

    # Version info
    version_font = pygame.font.SysFont('monospace', 12)
    version = version_font.render("v2.0 - Advanced Features Edition", True, (80, 85, 100))
    screen.blit(version, (screen_width // 2 - version.get_width() // 2, title_y + 75))

    # Menu buttons - centered vertically
    button_width = 320
    button_height = 50
    button_spacing = 15
    buttons = [
        ('new_simulation', 'New Simulation', SUCCESS_COLOR, 'Start a new simulation with custom settings'),
        ('load_simulation', 'Load Simulation', ACCENT_COLOR, 'Load a previously saved simulation'),
        ('load_settings', 'Load Settings', ACCENT_COLOR, 'Load saved configuration settings'),
        ('documentation', 'Documentation', WARNING_COLOR, 'View the simulation manual and guides'),
        ('exit', 'Exit', DANGER_COLOR, 'Exit the program'),
    ]

    total_height = len(buttons) * (button_height + button_spacing) - button_spacing
    start_y = screen_height // 2 - total_height // 2 + 30
    button_x = screen_width // 2 - button_width // 2

    mouse_pos = pygame.mouse.get_pos()

    for i, (action, label, color, description) in enumerate(buttons):
        y = start_y + i * (button_height + button_spacing)
        rect = pygame.Rect(button_x, y, button_width, button_height)
        button_rects[action] = rect

        # Check hover
        is_hover = rect.collidepoint(mouse_pos)

        # Draw button with hover effect
        if is_hover:
            # Hover: brighter color and subtle glow
            hover_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(screen, (color[0]//4, color[1]//4, color[2]//4),
                           (rect.x - 3, rect.y - 3, rect.width + 6, rect.height + 6), border_radius=10)
            pygame.draw.rect(screen, hover_color, rect, border_radius=8)
        else:
            pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=8)
            pygame.draw.rect(screen, color, rect, 2, border_radius=8)

        # Button text
        text_color = (255, 255, 255) if is_hover else color
        button_text = font_med.render(label, True, text_color)
        text_x = rect.centerx - button_text.get_width() // 2
        text_y = rect.centery - button_text.get_height() // 2
        screen.blit(button_text, (text_x, text_y))

        # Description on hover
        if is_hover:
            desc_text = version_font.render(description, True, MUTED_COLOR)
            desc_x = screen_width // 2 - desc_text.get_width() // 2
            screen.blit(desc_text, (desc_x, y + button_height + 5))

    # Footer with controls hint
    footer_y = screen_height - 60
    footer_font = pygame.font.SysFont('monospace', 11)
    controls = [
        "F11: Toggle Fullscreen",
        "ESC: Back/Exit",
    ]
    footer_text = "  |  ".join(controls)
    footer_surf = footer_font.render(footer_text, True, (70, 75, 90))
    screen.blit(footer_surf, (screen_width // 2 - footer_surf.get_width() // 2, footer_y))

    # Credits
    credits = footer_font.render("Powered by Genetic Algorithms & Neural Networks", True, (50, 55, 65))
    screen.blit(credits, (screen_width // 2 - credits.get_width() // 2, footer_y + 18))

    pygame.display.flip()


def handle_main_menu_input(event):
    """Handle input on the main menu. Returns action string or None."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        for action, rect in button_rects.items():
            if rect.collidepoint(pos):
                return action
    return None


def draw_load_dialog(screen, font_large, font_med, save_type='simulation'):
    """Draw a dialog for loading saves."""
    screen_width, screen_height = screen.get_size()

    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Dialog box
    dialog_width = min(700, screen_width - 100)
    dialog_height = min(500, screen_height - 100)
    dialog_x = screen_width // 2 - dialog_width // 2
    dialog_y = screen_height // 2 - dialog_height // 2

    pygame.draw.rect(screen, PANEL_COLOR, (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
    pygame.draw.rect(screen, ACCENT_COLOR, (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=10)

    # Title
    title = f"Load {'Simulation' if save_type == 'simulation' else 'Settings'}"
    title_text = font_large.render(title, True, ACCENT_COLOR)
    screen.blit(title_text, (dialog_x + dialog_width // 2 - title_text.get_width() // 2, dialog_y + 20))

    # Get save files
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves')
    if save_type == 'simulation':
        saves_dir = os.path.join(saves_dir, 'simulations')
    else:
        saves_dir = os.path.join(saves_dir, 'settings')

    file_rects = {}

    if os.path.exists(saves_dir):
        files = sorted([f for f in os.listdir(saves_dir) if f.endswith('.json')], reverse=True)
        small_font = pygame.font.SysFont('monospace', 12)

        y = dialog_y + 70
        for i, filename in enumerate(files[:10]):  # Show max 10 files
            file_rect = pygame.Rect(dialog_x + 20, y, dialog_width - 40, 35)
            file_rects[filename] = file_rect

            # Get file info
            filepath = os.path.join(saves_dir, filename)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                time_str = mtime.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = "Unknown"

            # Draw file entry
            is_hover = file_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = CARD_COLOR if not is_hover else (60, 65, 80)
            pygame.draw.rect(screen, bg_color, file_rect, border_radius=5)
            pygame.draw.rect(screen, BORDER_COLOR, file_rect, 1, border_radius=5)

            # Filename
            name_text = small_font.render(filename[:-5], True, TEXT_COLOR)  # Remove .json
            screen.blit(name_text, (file_rect.x + 10, file_rect.y + 5))

            # Date
            date_text = small_font.render(time_str, True, MUTED_COLOR)
            screen.blit(date_text, (file_rect.x + file_rect.width - date_text.get_width() - 10, file_rect.y + 10))

            y += 40
    else:
        no_saves = font_med.render("No saves found", True, MUTED_COLOR)
        screen.blit(no_saves, (dialog_x + dialog_width // 2 - no_saves.get_width() // 2, dialog_y + 150))

    # Close button
    close_rect = pygame.Rect(dialog_x + dialog_width - 90, dialog_y + dialog_height - 50, 70, 35)
    pygame.draw.rect(screen, DANGER_COLOR, close_rect, border_radius=5)
    close_text = font_med.render("Close", True, (255, 255, 255))
    screen.blit(close_text, (close_rect.centerx - close_text.get_width() // 2,
                             close_rect.centery - close_text.get_height() // 2))

    pygame.display.flip()

    return file_rects, close_rect


def draw_documentation(screen, font_large, font_med, scroll_offset=0):
    """Draw the documentation/manual screen."""
    screen_width, screen_height = screen.get_size()
    screen.fill(BG_COLOR)

    # Header
    header_height = 60
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, screen_width, header_height))
    pygame.draw.line(screen, BORDER_COLOR, (0, header_height), (screen_width, header_height), 2)

    title = font_large.render("Documentation & Manual", True, ACCENT_COLOR)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 15))

    # Back hint
    hint_font = pygame.font.SysFont('monospace', 12)
    hint = hint_font.render("Press ESC to return to menu | Scroll: Mouse wheel", True, MUTED_COLOR)
    screen.blit(hint, (screen_width - hint.get_width() - 20, 22))

    # Content area
    content_x = 40
    content_y = header_height + 20 - scroll_offset
    content_width = screen_width - 80
    small_font = pygame.font.SysFont('monospace', 13)
    section_font = pygame.font.SysFont('monospace', 16, bold=True)

    # Documentation content
    sections = [
        ("Overview", [
            "This simulation demonstrates emergent behaviors through genetic algorithms",
            "and neural networks. Agents evolve their behavior over generations by",
            "optimizing their neural network weights for survival and reproduction.",
            "",
            "Key features:",
            "  - Sector-based spatial sensing (5 angular sectors)",
            "  - Decoupled behavioral drives (avoid, attack, mate, effort)",
            "  - V2 Neural Architecture: 24 inputs -> 8 hidden -> 6 outputs",
            "  - Optional RNN with recurrent connections for temporal memory",
            "  - Advanced modulation features (size, age, morphology effects)",
        ]),
        ("Controls", [
            "SPACE      - Pause/Resume simulation",
            "UP/DOWN    - Speed up/slow down simulation",
            "ESC        - Return to settings/menu",
            "F11        - Toggle fullscreen",
            "G          - Toggle Genetics visualization (Menu G)",
            "S          - Toggle Statistics visualization",
            "H          - Toggle HUD sidebar",
            "O          - Toggle obstacles",
            "B          - Toggle border walls",
            "M          - Add horizontal mountain chain",
            "N          - Add vertical mountain chain",
            "R          - Add vertical river",
            "T          - Add horizontal river",
            "L          - Add lake",
            "D          - Add diagonal mountain range",
            "C          - Clear all obstacles (except borders)",
        ]),
        ("Neural Network Architecture", [
            "The V2 architecture uses sector-based sensing:",
            "",
            "INPUTS (24 total):",
            "  [0-4]   Food signals per sector (5 sectors)",
            "  [5-9]   Water signals per sector",
            "  [10-14] Agent signals per sector (+prey, -threat)",
            "  [15]    Energy (normalized)",
            "  [16]    Hydration (normalized)",
            "  [17]    Age ratio",
            "  [18]    Stress level",
            "  [19]    Health (combined vitality)",
            "  [20-21] Egocentric velocity (forward, lateral)",
            "  [22-23] Self traits (size, speed normalized)",
            "",
            "OUTPUTS (6 total):",
            "  [0-1]   Movement direction (x, y)",
            "  [2]     Avoid drive (flee tendency)",
            "  [3]     Attack drive",
            "  [4]     Mate desire",
            "  [5]     Effort (energy expenditure)",
            "",
            "FNN: 254 weights total",
            "RNN: 318 weights total (includes 8x8 recurrent matrix)",
        ]),
        ("Advanced Features", [
            "All optional features can be enabled in settings:",
            "",
            "SIZE EFFECTS: Large agents are stronger but slower",
            "AGE EFFECTS: Life stages (young, prime, old) affect capabilities",
            "INTERNAL STATE: Energy/hydration affect performance",
            "ACTION COSTS: Different actions have asymmetric energy costs",
            "MORPHOLOGY: Agility and armor traits with trade-offs",
            "SENSORY NOISE: Realistic perception imperfection",
            "CONTEXT SIGNALS: Time-since events as extra inputs",
            "SOCIAL PRESSURE: Crowding and dominance affect stress",
        ]),
        ("Tips for Evolution", [
            "- Start with smaller populations for faster initial evolution",
            "- Higher mutation rates accelerate evolution but reduce stability",
            "- RNN agents can develop more complex temporal behaviors",
            "- Enable advanced features gradually to observe their effects",
            "- Food cluster movement simulates seasonal resource changes",
            "- Water scarcity forces agents to develop resource-seeking behavior",
        ]),
    ]

    y = content_y
    for section_title, lines in sections:
        # Section header
        section_text = section_font.render(section_title, True, ACCENT_COLOR)
        if y > 0 and y < screen_height:
            screen.blit(section_text, (content_x, y))
        y += 30

        # Section content
        for line in lines:
            line_text = small_font.render(line, True, TEXT_COLOR if line.strip() else MUTED_COLOR)
            if y > 0 and y < screen_height:
                screen.blit(line_text, (content_x + 20, y))
            y += 18

        y += 25  # Section spacing

    # Calculate max scroll
    total_height = y - content_y + scroll_offset + 100
    max_scroll = max(0, total_height - screen_height + header_height + 50)

    pygame.display.flip()
    return max_scroll


def save_settings(settings, filename=None):
    """Save current settings to a file."""
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'settings')
    os.makedirs(saves_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"settings_{timestamp}.json"

    filepath = os.path.join(saves_dir, filename)

    # Convert settings to JSON-serializable format
    serializable = {}
    for key, value in settings.items():
        if isinstance(value, (dict, list, str, int, float, bool, type(None))):
            serializable[key] = value

    with open(filepath, 'w') as f:
        json.dump(serializable, f, indent=2)

    return filepath


def load_settings_file(filename):
    """Load settings from a file."""
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'settings')
    filepath = os.path.join(saves_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def save_simulation(simulation, settings, filename=None):
    """Save simulation state to a file."""
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'simulations')
    os.makedirs(saves_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sim_{timestamp}.json"

    filepath = os.path.join(saves_dir, filename)

    # Serialize simulation state
    state = {
        'settings': {},
        'world_time': simulation.world.time,
        'agents': [],
        'food': [],
        'water': [],
    }

    # Copy serializable settings
    for key, value in settings.items():
        if isinstance(value, (dict, list, str, int, float, bool, type(None))):
            state['settings'][key] = value

    # Serialize agents (simplified - just key attributes)
    for agent in simulation.world.agent_list:
        if agent.alive:
            agent_data = {
                'pos': (agent.pos.x, agent.pos.y),
                'energy': agent.energy,
                'hydration': agent.hydration,
                'age': agent.age,
                'generation': agent.generation,
                'species_id': agent.species_id,
                # Store genome as serializable format
                'phenotype': agent.phenotype,
            }
            state['agents'].append(agent_data)

    # Serialize food
    for food in simulation.world.food_list:
        if food.alive:
            state['food'].append({
                'pos': (food.pos.x, food.pos.y),
                'energy': food.energy,
            })

    # Serialize water
    for water in simulation.world.water_list:
        state['water'].append({
            'pos': (water.pos.x, water.pos.y),
            'radius': water.radius,
        })

    with open(filepath, 'w') as f:
        json.dump(state, f, indent=2)

    return filepath


def load_simulation_file(filename):
    """Load simulation state from a file."""
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'simulations')
    filepath = os.path.join(saves_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None
