#-*- coding: utf-8 -*-

import pygame
import config
import ast

# UI Colors - Modern dark theme
BG_COLOR = (30, 33, 40)
PANEL_COLOR = (38, 42, 52)
HEADER_COLOR = (45, 50, 62)
CARD_COLOR = (42, 46, 58)
TEXT_COLOR = (210, 215, 225)
MUTED_COLOR = (130, 135, 150)
ACCENT_COLOR = (90, 140, 220)
SUCCESS_COLOR = (80, 180, 100)
WARNING_COLOR = (220, 160, 60)
BORDER_COLOR = (55, 60, 75)
INPUT_BG = (50, 55, 68)
INPUT_ACTIVE = (60, 90, 140)
BUTTON_COLOR = (70, 120, 190)
BUTTON_HOVER = (90, 140, 210)

# Scrolling state
scroll_y = 0
max_scroll = 0
SCROLL_STEP = 35

# Input state
setting_rects = {}
plus_rects = {}
minus_rects = {}
input_rects = {}
category_rects = {}
active_input = None
input_texts = {}

# Category expansion state
expanded_categories = {}

# Categories configuration
CATEGORIES = {
    'Population': ['INITIAL_AGENTS', 'MAX_FOOD', 'FOOD_SPAWN_RATE'],
    'Genetics': ['MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE', 'DOMINANCE_MUTATION_RATE',
                 'POINT_MUTATION_STDDEV', 'LARGE_MUTATION_STDDEV', 'SOMATIC_MUTATION_RATE'],
    'Neural Network': ['NN_TYPE', 'NN_HIDDEN_SIZE', 'NN_WEIGHT_INIT_STD', 'NN_RECURRENT_IDENTITY_BIAS',
                       'NN_HIDDEN_NOISE_ENABLED', 'NN_HIDDEN_NOISE_STD'],
    'N-Step Memory': ['N_STEP_MEMORY_ENABLED', 'N_STEP_MEMORY_DEPTH'],
    'Sensing': ['SECTOR_COUNT', 'VISION_NOISE_STD'],
    'Stress System': ['STRESS_GAIN_RATE', 'STRESS_DECAY_RATE', 'STRESS_THREAT_WEIGHT', 'STRESS_RESOURCE_WEIGHT'],
    'Effort System': ['EFFORT_SPEED_SCALE', 'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE'],
    'Energy': ['BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_THRESHOLD', 'REPRODUCTION_COST',
               'FOOD_ENERGY', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR'],
    'Hydration': ['BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_DRAIN_RATE', 'DRINK_RATE'],
    'Water': ['NUM_WATER_SOURCES', 'WATER_SOURCE_RADIUS'],
    'Combat': ['ATTACK_DISTANCE', 'ATTACK_DAMAGE_BASE', 'ATTACK_ENERGY_COST', 'KILL_ENERGY_GAIN', 'CANNIBALISM_ENERGY_BONUS'],
    'Food Clusters': ['NUM_FOOD_CLUSTERS', 'FOOD_CLUSTER_SPREAD', 'SEASON_SHIFT_INTERVAL'],
    'World': ['WORLD_WIDTH', 'WORLD_HEIGHT', 'GRID_CELL_SIZE', 'HUD_WIDTH', 'WINDOW_WIDTH', 'WINDOW_HEIGHT'],
    'Agents': ['MAX_SPEED_BASE', 'EATING_DISTANCE', 'MATING_DISTANCE', 'WANDER_STRENGTH', 'STEER_STRENGTH'],
    'Reproduction': ['MATURITY_AGE', 'REPRODUCTION_COOLDOWN', 'MATE_SEARCH_RADIUS', 'MAX_AGE', 'MAX_SIMULTANEOUS_OFFSPRING'],
    'Species': ['INITIAL_SAME_SPECIES_PERCENTAGE', 'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE',
                'HYBRID_FERTILITY_RATE', 'NUMBER_OF_INITIAL_SPECIES'],
    'Initialization': ['RANDOM_AGE_INITIALIZATION'],
    'Epidemic': ['EPIDEMIC_ENABLED', 'EPIDEMIC_INTERVAL', 'EPIDEMIC_MIN_POPULATION_RATIO',
                 'EPIDEMIC_AFFECTED_RATIO', 'EPIDEMIC_BASE_PROBABILITY'],
    'Regions': ['REGIONAL_VARIATIONS_ENABLED', 'NUM_REGIONS_X', 'NUM_REGIONS_Y',
                'REGION_SPEED_MODIFIER', 'REGION_SIZE_MODIFIER', 'REGION_AGGRESSION_MODIFIER', 'REGION_EFFICIENCY_MODIFIER'],
    'Temperature': ['TEMPERATURE_ENABLED', 'TEMPERATURE_ZONES_X', 'TEMPERATURE_ZONES_Y'],
    'Obstacles': ['OBSTACLES_ENABLED', 'BORDER_ENABLED', 'BORDER_WIDTH', 'NUM_INTERNAL_OBSTACLES'],
    'Rendering': ['FPS'],
    # === ADVANCED FEATURES ===
    'Size Effects': ['ADVANCED_SIZE_EFFECTS_ENABLED', 'SIZE_ATTACK_SCALING', 'SIZE_SPEED_PENALTY',
                     'SIZE_TURN_PENALTY', 'SIZE_METABOLIC_SCALING', 'SIZE_PERCEPTION_BONUS'],
    'Energy Scaling': ['SUPERLINEAR_ENERGY_SCALING', 'ENERGY_SIZE_EXPONENT', 'EFFORT_SIZE_INTERACTION'],
    'Age Effects': ['AGE_EFFECTS_ENABLED', 'AGE_PRIME_START', 'AGE_PRIME_END', 'AGE_SPEED_DECLINE',
                    'AGE_STAMINA_DECLINE', 'AGE_EXPERIENCE_BONUS', 'AGE_REPRODUCTION_CURVE'],
    'Internal State': ['INTERNAL_STATE_MODULATION_ENABLED', 'LOW_ENERGY_ATTACK_PENALTY',
                       'LOW_HYDRATION_SPEED_PENALTY', 'HIGH_STRESS_EFFORT_BOOST', 'EXHAUSTION_THRESHOLD'],
    'Action Costs': ['ACTION_COSTS_ENABLED', 'COST_HIGH_SPEED_MULTIPLIER', 'COST_SHARP_TURN_MULTIPLIER',
                     'COST_PURSUIT_MULTIPLIER', 'COST_ATTACK_BASE', 'COST_MATING_BASE'],
    'Morphology': ['MORPHOLOGY_TRAITS_ENABLED', 'AGILITY_SPEED_BONUS', 'AGILITY_STAMINA_COST',
                   'ARMOR_DAMAGE_REDUCTION', 'ARMOR_SPEED_PENALTY', 'ARMOR_ENERGY_COST'],
    'Sensory Noise': ['SENSORY_NOISE_ENABLED', 'SENSOR_DROPOUT_RATE', 'INTERNAL_STATE_NOISE', 'PERCEPTION_LAG'],
    'Context Signals': ['CONTEXT_SIGNALS_ENABLED', 'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY',
                        'TIME_SINCE_MATING_DECAY'],
    'Social Pressure': ['SOCIAL_PRESSURE_ENABLED', 'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD',
                        'CROWD_STRESS_RATE', 'DOMINANCE_STRESS_FACTOR'],
}

# Initialize categories as expanded
for cat in CATEGORIES:
    expanded_categories[cat] = True


def draw_settings_screen(screen, settings, font_large, font_med):
    """Draw the settings screen with improved layout."""
    global scroll_y, max_scroll, input_texts, setting_rects, plus_rects, minus_rects, input_rects, category_rects

    screen_width, screen_height = screen.get_size()

    # Sync region arrays before initializing input texts
    _sync_region_arrays(settings)

    # Initialize input texts
    for category, keys in CATEGORIES.items():
        for key in keys:
            if key in settings:
                if isinstance(settings[key], list):
                    input_texts[key] = str(settings[key])
                    # Always update array elements to match current array size
                    for i, value in enumerate(settings[key]):
                        input_texts[f"{key}_element_{i}"] = str(value)
                elif key not in input_texts:
                    input_texts[key] = str(settings[key])

    # Clear rects
    setting_rects = {}
    plus_rects = {}
    minus_rects = {}
    input_rects = {}
    category_rects = {}

    # Background
    screen.fill(BG_COLOR)

    # Header
    header_height = 70
    pygame.draw.rect(screen, HEADER_COLOR, (0, 0, screen_width, header_height))
    pygame.draw.line(screen, BORDER_COLOR, (0, header_height), (screen_width, header_height), 2)

    # Title
    title = font_large.render("Simulation Configuration", True, ACCENT_COLOR)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))

    # Subtitle
    subtitle_font = pygame.font.SysFont('monospace', 12)
    subtitle = subtitle_font.render("Neural Network Evolution Simulation", True, MUTED_COLOR)
    screen.blit(subtitle, (screen_width // 2 - subtitle.get_width() // 2, 48))

    # Content area
    content_x = 30
    content_width = screen_width - 60
    y_offset = header_height + 15

    # Calculate layout - two columns if wide enough
    use_two_columns = screen_width > 1200
    col_width = (content_width - 20) // 2 if use_two_columns else content_width

    # Draw categories
    category_list = list(CATEGORIES.items())
    col = 0
    col_y = [y_offset, y_offset]  # Track Y for each column

    for cat_idx, (category, keys) in enumerate(category_list):
        if use_two_columns:
            # Alternate columns
            col = 0 if col_y[0] <= col_y[1] else 1
            x = content_x + col * (col_width + 20)
            y = col_y[col]
        else:
            x = content_x
            y = y_offset

        # Draw category card
        card_height = _calculate_category_height(category, keys, settings, expanded_categories.get(category, True))
        visible_y = y - scroll_y

        if visible_y + card_height > header_height and visible_y < screen_height - 80:
            _draw_category_card(screen, x, visible_y, col_width, card_height, category, keys, settings, font_med)

        # Store category rect for click detection
        category_rects[category] = pygame.Rect(x, visible_y, col_width, 35)

        if use_two_columns:
            col_y[col] = y + card_height + 10
        else:
            y_offset = y + card_height + 10

    # Update max scroll
    if use_two_columns:
        total_height = max(col_y[0], col_y[1])
    else:
        total_height = y_offset
    max_scroll = max(0, total_height - screen_height + 150)

    # Draw scrollbar
    _draw_scrollbar(screen, screen_width, header_height, screen_height - header_height - 80)

    # Bottom buttons
    button_y = screen_height - 65

    # Start button
    start_rect = pygame.Rect(screen_width // 2 - 110, button_y, 220, 45)
    pygame.draw.rect(screen, BUTTON_COLOR, start_rect, border_radius=5)
    pygame.draw.rect(screen, ACCENT_COLOR, start_rect, 2, border_radius=5)
    start_text = font_med.render("START SIMULATION", True, (255, 255, 255))
    screen.blit(start_text, (start_rect.centerx - start_text.get_width() // 2,
                             start_rect.centery - start_text.get_height() // 2))

    # Fullscreen button
    fs_rect = pygame.Rect(screen_width - 180, button_y + 5, 150, 35)
    pygame.draw.rect(screen, PANEL_COLOR, fs_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, fs_rect, 1, border_radius=3)
    fs_text = subtitle_font.render("Toggle Fullscreen", True, MUTED_COLOR)
    screen.blit(fs_text, (fs_rect.centerx - fs_text.get_width() // 2,
                          fs_rect.centery - fs_text.get_height() // 2))

    pygame.display.flip()


def _should_show_setting(key, settings, category):
    """Determine if a setting should be shown based on parent toggles."""
    # Temperature settings only visible when TEMPERATURE_ENABLED
    if category == 'Temperature':
        if key in ['TEMPERATURE_ZONES_X', 'TEMPERATURE_ZONES_Y']:
            return settings.get('TEMPERATURE_ENABLED', False)

    # Region modifier arrays only visible when REGIONAL_VARIATIONS_ENABLED
    if category == 'Regions':
        if key.startswith('REGION_') and key.endswith('_MODIFIER'):
            return settings.get('REGIONAL_VARIATIONS_ENABLED', False)

    # N-Step Memory settings only visible when N_STEP_MEMORY_ENABLED
    if category == 'N-Step Memory':
        if key == 'N_STEP_MEMORY_DEPTH':
            return settings.get('N_STEP_MEMORY_ENABLED', False)

    # RNN-specific settings only visible when NN_TYPE is RNN
    if category == 'Neural Network':
        if key in ['NN_RECURRENT_IDENTITY_BIAS', 'NN_HIDDEN_NOISE_ENABLED', 'NN_HIDDEN_NOISE_STD']:
            return settings.get('NN_TYPE', 'FNN') == 'RNN'
        if key == 'NN_HIDDEN_NOISE_STD':
            return settings.get('NN_HIDDEN_NOISE_ENABLED', False) and settings.get('NN_TYPE', 'FNN') == 'RNN'

    # Size Effects sub-settings only visible when ADVANCED_SIZE_EFFECTS_ENABLED
    if category == 'Size Effects':
        if key != 'ADVANCED_SIZE_EFFECTS_ENABLED':
            return settings.get('ADVANCED_SIZE_EFFECTS_ENABLED', False)

    # Age Effects sub-settings only visible when AGE_EFFECTS_ENABLED
    if category == 'Age Effects':
        if key != 'AGE_EFFECTS_ENABLED':
            return settings.get('AGE_EFFECTS_ENABLED', False)

    # Internal State sub-settings only visible when INTERNAL_STATE_MODULATION_ENABLED
    if category == 'Internal State':
        if key != 'INTERNAL_STATE_MODULATION_ENABLED':
            return settings.get('INTERNAL_STATE_MODULATION_ENABLED', False)

    # Action Costs sub-settings only visible when ACTION_COSTS_ENABLED
    if category == 'Action Costs':
        if key != 'ACTION_COSTS_ENABLED':
            return settings.get('ACTION_COSTS_ENABLED', False)

    # Morphology sub-settings only visible when MORPHOLOGY_TRAITS_ENABLED
    if category == 'Morphology':
        if key != 'MORPHOLOGY_TRAITS_ENABLED':
            return settings.get('MORPHOLOGY_TRAITS_ENABLED', False)

    # Sensory Noise sub-settings only visible when SENSORY_NOISE_ENABLED
    if category == 'Sensory Noise':
        if key != 'SENSORY_NOISE_ENABLED':
            return settings.get('SENSORY_NOISE_ENABLED', True)

    # Context Signals sub-settings only visible when CONTEXT_SIGNALS_ENABLED
    if category == 'Context Signals':
        if key != 'CONTEXT_SIGNALS_ENABLED':
            return settings.get('CONTEXT_SIGNALS_ENABLED', False)

    # Social Pressure sub-settings only visible when SOCIAL_PRESSURE_ENABLED
    if category == 'Social Pressure':
        if key != 'SOCIAL_PRESSURE_ENABLED':
            return settings.get('SOCIAL_PRESSURE_ENABLED', True)

    return True


def _get_expected_region_count(settings):
    """Get the expected number of region modifiers based on NUM_REGIONS_X * NUM_REGIONS_Y."""
    nx = settings.get('NUM_REGIONS_X', 2)
    ny = settings.get('NUM_REGIONS_Y', 2)
    return max(1, nx * ny)


def _sync_region_arrays(settings):
    """Ensure region modifier arrays match the expected size."""
    expected_count = _get_expected_region_count(settings)

    array_keys = ['REGION_SPEED_MODIFIER', 'REGION_SIZE_MODIFIER',
                  'REGION_AGGRESSION_MODIFIER', 'REGION_EFFICIENCY_MODIFIER']

    for key in array_keys:
        if key in settings:
            current = settings[key]
            if len(current) < expected_count:
                # Extend with default value 1.0
                settings[key] = current + [1.0] * (expected_count - len(current))
            elif len(current) > expected_count:
                # Truncate
                settings[key] = current[:expected_count]


def _calculate_category_height(category, keys, settings, expanded):
    """Calculate the height needed for a category card."""
    base_height = 40  # Header
    if not expanded:
        return base_height

    row_height = 32
    for key in keys:
        if key not in settings:
            continue
        if not _should_show_setting(key, settings, category):
            continue

        value = settings[key]
        if isinstance(value, list):
            # Array settings - calculate based on grid layout
            n = len(value)
            cols = min(4, n)  # Up to 4 columns
            rows = (n + cols - 1) // cols
            cell_height = 45  # Taller cells for better visibility
            base_height += 25 + rows * cell_height + 15  # Label + grid + spacing
        else:
            base_height += row_height

    return base_height + 10  # Padding


def _draw_category_card(screen, x, y, width, height, category, keys, settings, font):
    """Draw a category card with its settings."""
    global setting_rects, plus_rects, minus_rects, input_rects

    # Sync region arrays if this is the Regions category
    if category == 'Regions':
        _sync_region_arrays(settings)

    # Card background
    pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 1, border_radius=5)

    # Header
    header_rect = pygame.Rect(x, y, width, 35)
    pygame.draw.rect(screen, PANEL_COLOR, header_rect, border_top_left_radius=5, border_top_right_radius=5)

    # Expand/collapse indicator
    expanded = expanded_categories.get(category, True)
    indicator = "[-]" if expanded else "[+]"
    ind_font = pygame.font.SysFont('monospace', 14)
    ind_text = ind_font.render(indicator, True, ACCENT_COLOR)
    screen.blit(ind_text, (x + 10, y + 10))

    # Category name
    cat_text = font.render(category, True, TEXT_COLOR)
    screen.blit(cat_text, (x + 40, y + 9))

    if not expanded:
        return

    # Settings
    row_y = y + 42
    row_height = 32
    small_font = pygame.font.SysFont('monospace', 11)
    value_font = pygame.font.SysFont('monospace', 12)

    for key in keys:
        if key not in settings:
            continue

        # Check if this setting should be shown
        if not _should_show_setting(key, settings, category):
            continue

        value = settings[key]

        # Handle array settings
        if isinstance(value, list):
            _draw_array_setting(screen, x + 10, row_y, width - 20, key, value, small_font, value_font, settings, category)
            n = len(value)
            cols = min(4, n)
            rows = (n + cols - 1) // cols
            cell_height = 45
            row_y += 25 + rows * cell_height + 15
        elif isinstance(value, bool):
            _draw_bool_setting(screen, x + 10, row_y, width - 20, key, value, small_font)
            row_y += row_height
        elif key == 'NN_TYPE':
            _draw_enum_setting(screen, x + 10, row_y, width - 20, key, value, small_font, ['FNN', 'RNN'])
            row_y += row_height
        else:
            _draw_numeric_setting(screen, x + 10, row_y, width - 20, key, value, small_font, value_font)
            row_y += row_height


def _draw_numeric_setting(screen, x, y, width, key, value, label_font, value_font):
    """Draw a numeric setting with +/- buttons."""
    global setting_rects, plus_rects, minus_rects, input_rects

    # Format key name nicely
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 25:
        display_name = display_name[:22] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Value controls on right side
    controls_x = x + width - 150

    # Minus button
    minus_rect = pygame.Rect(controls_x, y + 2, 24, 24)
    pygame.draw.rect(screen, PANEL_COLOR, minus_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, minus_rect, 1, border_radius=3)
    minus_text = value_font.render("-", True, WARNING_COLOR)
    screen.blit(minus_text, (minus_rect.centerx - 3, minus_rect.centery - 7))
    minus_rects[key] = minus_rect

    # Input box
    input_rect = pygame.Rect(controls_x + 28, y + 2, 80, 24)
    is_active = active_input == key
    bg_color = INPUT_ACTIVE if is_active else INPUT_BG
    pygame.draw.rect(screen, bg_color, input_rect, border_radius=3)
    border_color = ACCENT_COLOR if is_active else BORDER_COLOR
    pygame.draw.rect(screen, border_color, input_rect, 1, border_radius=3)

    # Value text
    val_str = input_texts.get(key, str(value))
    if len(val_str) > 10:
        val_str = val_str[:9] + ".."
    val_text = value_font.render(val_str, True, TEXT_COLOR)
    screen.blit(val_text, (input_rect.x + 5, input_rect.y + 5))
    input_rects[key] = input_rect
    setting_rects[key] = input_rect

    # Plus button
    plus_rect = pygame.Rect(controls_x + 112, y + 2, 24, 24)
    pygame.draw.rect(screen, PANEL_COLOR, plus_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, plus_rect, 1, border_radius=3)
    plus_text = value_font.render("+", True, SUCCESS_COLOR)
    screen.blit(plus_text, (plus_rect.centerx - 4, plus_rect.centery - 7))
    plus_rects[key] = plus_rect


def _draw_bool_setting(screen, x, y, width, key, value, label_font):
    """Draw a boolean setting as a toggle."""
    global setting_rects

    # Format key name
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 30:
        display_name = display_name[:27] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Toggle switch
    toggle_x = x + width - 50
    toggle_rect = pygame.Rect(toggle_x, y + 4, 40, 20)

    if value:
        pygame.draw.rect(screen, SUCCESS_COLOR, toggle_rect, border_radius=10)
        # Knob on right
        pygame.draw.circle(screen, (255, 255, 255), (toggle_x + 30, y + 14), 8)
    else:
        pygame.draw.rect(screen, PANEL_COLOR, toggle_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, toggle_rect, 1, border_radius=10)
        # Knob on left
        pygame.draw.circle(screen, MUTED_COLOR, (toggle_x + 10, y + 14), 8)

    setting_rects[key] = toggle_rect


def _draw_enum_setting(screen, x, y, width, key, value, label_font, options):
    """Draw an enum/choice setting with clickable options."""
    global setting_rects

    # Format key name
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 25:
        display_name = display_name[:22] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Options buttons
    option_width = 60
    option_height = 22
    option_spacing = 5
    options_x = x + width - (len(options) * (option_width + option_spacing))

    value_font = pygame.font.SysFont('monospace', 11)

    for i, option in enumerate(options):
        opt_x = options_x + i * (option_width + option_spacing)
        opt_rect = pygame.Rect(opt_x, y + 2, option_width, option_height)

        is_selected = (value == option)

        if is_selected:
            pygame.draw.rect(screen, ACCENT_COLOR, opt_rect, border_radius=4)
            text_color = (255, 255, 255)
        else:
            pygame.draw.rect(screen, INPUT_BG, opt_rect, border_radius=4)
            pygame.draw.rect(screen, BORDER_COLOR, opt_rect, 1, border_radius=4)
            text_color = MUTED_COLOR

        opt_text = value_font.render(option, True, text_color)
        screen.blit(opt_text, (opt_rect.centerx - opt_text.get_width() // 2,
                               opt_rect.centery - opt_text.get_height() // 2))

        # Store rect for click handling with option info
        setting_rects[f"{key}_option_{option}"] = opt_rect

    # Store main key rect (covers all options)
    total_rect = pygame.Rect(options_x, y + 2, len(options) * (option_width + option_spacing), option_height)
    setting_rects[key] = total_rect


def _draw_array_setting(screen, x, y, width, key, values, label_font, value_font, settings=None, category=None):
    """Draw an array setting as a grid with better formatting."""
    global setting_rects, input_rects

    # Format key name - make it more readable
    display_name = key.replace('_', ' ').title()
    # Shorten common prefixes for region modifiers
    display_name = display_name.replace('Region ', '').replace(' Modifier', '')

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y))

    # Calculate grid layout - use more columns for better space usage
    n = len(values)
    cols = min(4, n)  # Up to 4 columns
    if n <= 2:
        cols = n
    elif n <= 4:
        cols = n
    elif n <= 6:
        cols = 3
    elif n <= 8:
        cols = 4

    # Larger cells for better readability
    cell_width = 70
    cell_height = 38
    spacing = 8

    # Calculate grid position - align to right side of the card
    grid_width = cols * cell_width + (cols - 1) * spacing
    grid_x = x + width - grid_width - 5
    grid_y = y + 22

    # Draw region position hints if this is a region modifier array
    is_region_modifier = key.startswith('REGION_') and key.endswith('_MODIFIER')
    hint_font = pygame.font.SysFont('monospace', 9) if is_region_modifier else None

    for i, val in enumerate(values):
        row = i // cols
        col = i % cols
        cell_x = grid_x + col * (cell_width + spacing)
        cell_y = grid_y + row * (cell_height + spacing)

        element_key = f"{key}_element_{i}"
        is_active = active_input == element_key

        # Cell background with gradient effect for visual depth
        cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
        bg_color = INPUT_ACTIVE if is_active else INPUT_BG
        pygame.draw.rect(screen, bg_color, cell_rect, border_radius=4)
        border_color = ACCENT_COLOR if is_active else BORDER_COLOR
        pygame.draw.rect(screen, border_color, cell_rect, 1, border_radius=4)

        # Region position label (e.g., "TL", "TR", etc.)
        if is_region_modifier and settings:
            nx = settings.get('NUM_REGIONS_X', 2)
            ny = settings.get('NUM_REGIONS_Y', 2)
            region_row = i // nx
            region_col = i % nx

            # Generate position label
            if ny <= 2 and nx <= 2:
                pos_labels = ['TL', 'TR', 'BL', 'BR']
                if i < len(pos_labels):
                    pos_label = pos_labels[i]
                else:
                    pos_label = f"R{i}"
            else:
                pos_label = f"({region_col},{region_row})"

            pos_text = hint_font.render(pos_label, True, (100, 105, 115))
            screen.blit(pos_text, (cell_x + 3, cell_y + 2))

        # Value - centered in cell
        val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
        val_text = value_font.render(val_str, True, TEXT_COLOR)

        # Position value text - if region modifier, offset down slightly for position label
        if is_region_modifier:
            text_y = cell_y + cell_height // 2 + 3
        else:
            text_y = cell_y + cell_height // 2 - val_text.get_height() // 2

        text_x = cell_x + cell_width // 2 - val_text.get_width() // 2
        screen.blit(val_text, (text_x, text_y - val_text.get_height() // 2))

        setting_rects[element_key] = cell_rect
        input_rects[element_key] = cell_rect

    # Store main key rect
    rows = (n + cols - 1) // cols
    total_rect = pygame.Rect(grid_x, grid_y, grid_width, rows * (cell_height + spacing))
    setting_rects[key] = total_rect


def _draw_scrollbar(screen, screen_width, top, height):
    """Draw the scrollbar."""
    if max_scroll <= 0:
        return

    bar_width = 10
    bar_x = screen_width - bar_width - 5

    # Track
    pygame.draw.rect(screen, PANEL_COLOR, (bar_x, top + 5, bar_width, height - 10), border_radius=5)

    # Thumb
    thumb_height = max(30, int((height / (height + max_scroll)) * (height - 10)))
    thumb_y = top + 5 + int((scroll_y / max_scroll) * (height - 10 - thumb_height))
    pygame.draw.rect(screen, BORDER_COLOR, (bar_x, thumb_y, bar_width, thumb_height), border_radius=5)


def handle_settings_input(settings, event):
    """Handle input on the settings screen."""
    global scroll_y, active_input, input_texts, expanded_categories

    screen_width, screen_height = pygame.display.get_surface().get_size()

    # Start button
    start_rect = pygame.Rect(screen_width // 2 - 110, screen_height - 65, 220, 45)

    # Fullscreen button
    fs_rect = pygame.Rect(screen_width - 180, screen_height - 60, 150, 35)

    # Scroll handling
    if event.type == pygame.MOUSEWHEEL:
        scroll_y = max(0, min(max_scroll, scroll_y - event.y * SCROLL_STEP))
        return None

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos

        # Check fullscreen button
        if fs_rect.collidepoint(pos):
            return "toggle_fullscreen"

        # Check start button
        if start_rect.collidepoint(pos):
            _apply_input_texts(settings)
            return "start"

        # Check category headers
        for category, rect in category_rects.items():
            if rect.collidepoint(pos):
                expanded_categories[category] = not expanded_categories.get(category, True)
                return None

        # Check plus buttons
        for key, rect in plus_rects.items():
            if rect.collidepoint(pos) and key in settings:
                _increment_setting(settings, key)
                return None

        # Check minus buttons
        for key, rect in minus_rects.items():
            if rect.collidepoint(pos) and key in settings:
                _decrement_setting(settings, key)
                return None

        # Check setting inputs
        for key, rect in setting_rects.items():
            if rect.collidepoint(pos):
                # Handle enum option clicks
                if "_option_" in key:
                    parts = key.rsplit("_option_", 1)
                    base_key = parts[0]
                    option_value = parts[1]
                    if base_key in settings:
                        settings[base_key] = option_value
                        input_texts[base_key] = option_value
                    return None
                elif "_element_" in key:
                    active_input = key
                elif key in settings:
                    if isinstance(settings[key], bool):
                        settings[key] = not settings[key]
                        input_texts[key] = str(settings[key])
                    elif isinstance(settings[key], str):
                        # String settings handled by enum options, skip here
                        pass
                    else:
                        active_input = key
                return None

        # Click outside - deactivate input
        active_input = None

    # Text input handling
    if event.type == pygame.KEYDOWN and active_input is not None:
        if event.key == pygame.K_RETURN:
            _apply_single_input(settings, active_input)
            active_input = None
        elif event.key == pygame.K_BACKSPACE:
            if active_input in input_texts:
                input_texts[active_input] = input_texts[active_input][:-1]
        elif event.unicode.isdigit() or event.unicode in '.-+e':
            if active_input in input_texts:
                input_texts[active_input] += event.unicode
            else:
                input_texts[active_input] = event.unicode

    return None


def _increment_setting(settings, key):
    """Increment a numeric setting."""
    if isinstance(settings[key], bool) or isinstance(settings[key], list):
        return

    increment = _get_increment(key, settings[key])
    settings[key] += increment
    if isinstance(settings[key], float):
        settings[key] = round(settings[key], 4)
    input_texts[key] = str(settings[key])


def _decrement_setting(settings, key):
    """Decrement a numeric setting."""
    if isinstance(settings[key], bool) or isinstance(settings[key], list):
        return

    decrement = _get_increment(key, settings[key])
    settings[key] = max(0, settings[key] - decrement)
    if isinstance(settings[key], float):
        settings[key] = round(settings[key], 4)
    input_texts[key] = str(settings[key])


def _get_increment(key, value):
    """Get the appropriate increment for a setting."""
    if isinstance(value, int):
        return 1

    small_floats = ['MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE', 'DOMINANCE_MUTATION_RATE',
                    'SOMATIC_MUTATION_RATE', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR', 'HYDRATION_DRAIN_RATE']
    if key in small_floats:
        return 0.001

    return 0.1


def _apply_input_texts(settings):
    """Apply all input texts to settings."""
    for key, text in input_texts.items():
        if "_element_" in key:
            continue
        _apply_single_input(settings, key)


def _apply_single_input(settings, key):
    """Apply a single input text to settings."""
    if "_element_" in key:
        # Handle array element
        parts = key.rsplit("_element_", 1)
        base_key = parts[0]
        idx = int(parts[1])

        if base_key in settings and idx < len(settings[base_key]):
            try:
                text = input_texts.get(key, "")
                original = settings[base_key][idx]
                if isinstance(original, int):
                    settings[base_key][idx] = int(float(text))
                elif isinstance(original, float):
                    settings[base_key][idx] = float(text)
            except (ValueError, IndexError):
                pass
    elif key in settings:
        try:
            text = input_texts.get(key, str(settings[key]))
            original = settings[key]

            if isinstance(original, int):
                settings[key] = int(float(text))
            elif isinstance(original, float):
                settings[key] = float(text)
            elif isinstance(original, list):
                parsed = ast.literal_eval(text)
                if isinstance(parsed, list):
                    settings[key] = parsed
        except (ValueError, SyntaxError):
            input_texts[key] = str(settings[key])
