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
    version = version_font.render("v0.0.1", True, (80, 85, 100))
    screen.blit(version, (screen_width // 2 - version.get_width() // 2, title_y + 75))

    # Menu buttons - centered vertically
    button_width = 320
    button_height = 50
    button_spacing = 15
    buttons = [
        ('new_simulation', 'New Simulation', SUCCESS_COLOR, 'Start a new simulation with custom settings'),
        ('multiagent_mode', 'Multiagent Mode', ACCENT_COLOR, 'Run multiple agent configurations together'),
        ('load_simulation', 'Load Simulation', ACCENT_COLOR, 'Load a previously saved simulation'),
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
    elif event.type == pygame.KEYDOWN:
        # Keyboard shortcuts for menu options
        if event.key == pygame.K_1:
            return 'new_simulation'
        elif event.key == pygame.K_2:
            return 'multiagent_mode'  # Multiagent mode is now option 2
        elif event.key == pygame.K_3:
            return 'load_simulation'  # Load simulation is now option 3
        elif event.key == pygame.K_4:
            return 'load_settings'  # Load settings is now option 4
        elif event.key == pygame.K_5:
            return 'documentation'  # Documentation is now option 5
        elif event.key == pygame.K_6:
            return 'exit'  # Exit is now option 6
        elif event.key == pygame.K_ESCAPE:
            return 'exit'
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


def handle_load_dialog_input(event, file_rects, close_rect):
    """Handle input for the load dialog. Returns filename or 'close' or None."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        # Check close button
        if close_rect.collidepoint(pos):
            return 'close'
        # Check file entries
        for filename, rect in file_rects.items():
            if rect.collidepoint(pos):
                return filename
    return None


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
    subsection_font = pygame.font.SysFont('monospace', 14, bold=True)

    # Load documentation from the comprehensive file
    try:
        doc_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'final_comprehensive_documentation.md')
        with open(doc_file_path, 'r', encoding='utf-8') as f:
            doc_lines = f.readlines()

        # Parse the documentation into sections
        sections = []
        current_section = None
        current_content = []

        for line in doc_lines:
            stripped_line = line.rstrip()  # Keep internal spacing but remove trailing newline

            # Check for section headers (lines starting with ##)
            if stripped_line.startswith('## ') and not stripped_line.startswith('###'):
                # Save previous section if exists
                if current_section:
                    sections.append((current_section, current_content))

                # Start new section
                current_section = stripped_line[3:]  # Remove '## ' prefix
                current_content = []
            elif stripped_line.startswith('### ') and not stripped_line.startswith('####'):
                # Add subsection as a special formatted line
                current_content.append(f"SUBSECTION: {stripped_line[4:]}")  # Remove '### ' prefix
            elif stripped_line and not stripped_line.startswith('#'):  # Regular content line
                # Remove markdown formatting but preserve content
                clean_line = stripped_line.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                # Remove markdown links but keep the text
                if '](' in clean_line:
                    # Handle markdown links: [text](link) -> text
                    import re
                    clean_line = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', clean_line)

                clean_line = clean_line.replace('*', '')  # Remove bold/italic markers
                clean_line = clean_line.replace('_', '')  # Remove underscore markers

                if clean_line.strip() and not clean_line.startswith('---') and not clean_line.startswith('<'):
                    current_content.append(clean_line.strip())

        # Add the last section
        if current_section:
            sections.append((current_section, current_content))

    except FileNotFoundError:
        # Fallback to original content if file not found
        sections = [
            ("Project Overview", [
                "This is an advanced evolutionary simulation that models a population of agents in a 2D world.",
                "Each agent's behavior is controlled by a genetically-encoded neural network.",
                "The simulation explores how complex behaviors like herbivory, cannibalism, and social",
                "dynamics can emerge through evolutionary processes.",
                "",
                "Key features:",
                "  - Sector-based spatial sensing (5 angular sectors)",
                "  - Decoupled behavioral drives (avoid, attack, mate, effort)",
                "  - V2 Neural Architecture: 24 inputs -> 8 hidden -> 6 outputs",
                "  - Optional RNN with recurrent connections for temporal memory",
                "  - Advanced modulation features (size, age, morphology effects)",
            ]),
            ("Core Architecture", [
                "The simulation follows a modular architecture with clearly defined systems that",
                "interact through well-defined interfaces. The main components include the Simulation",
                "class, World class, Entity classes, and System classes."
            ]),
            ("Neural Network System", [
                "The simulation uses sophisticated neural networks with sector-based sensing and",
                "decoupled behavioral drives. Two network types are available: Feed-Forward",
                "Neural Network (FNN) and Recurrent Neural Network (RNN)."
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
        ]

    y = content_y
    for section_title, lines in sections:
        # Section header
        section_text = section_font.render(section_title, True, ACCENT_COLOR)
        if y > -30 and y < screen_height + 30:  # Extended visibility range
            screen.blit(section_text, (content_x, y))
        y += 30

        # Section content
        for line in lines:
            # Check if this is a subsection
            if line.startswith("SUBSECTION:"):
                subsection_text = subsection_font.render(line[11:], True, (180, 180, 220))  # Lighter blue for subsections
                if y > -20 and y < screen_height + 20:  # Extended visibility range
                    screen.blit(subsection_text, (content_x + 10, y))
                y += 20
            else:
                line_text = small_font.render(line, True, TEXT_COLOR if line.strip() else MUTED_COLOR)
                if y > -20 and y < screen_height + 20:  # Extended visibility range
                    screen.blit(line_text, (content_x + 20, y))
                y += 18

        y += 25  # Section spacing

    # Calculate max scroll
    total_height = max(screen_height, y - content_y + scroll_offset + 100)
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
