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

# Current view state
current_view = 'environmental'  # 'environmental' or 'agent'

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

# Tooltip state
tooltip_rects = {}  # Maps setting keys to their tooltip rect (asterisk position)
tooltip_visible = None  # Currently visible tooltip key
tooltip_timer = 0  # Timer for tooltip delay
TOOLTIP_DELAY = 500  # Delay in milliseconds before showing tooltip

# Hierarchical Categories Configuration
# Parent categories contain sub-categories that are visually grouped
HIERARCHICAL_CATEGORIES = {
    'environmental': {
        'World': {
            'type': 'category',
            'settings': ['WORLD_WIDTH', 'WORLD_HEIGHT', 'GRID_CELL_SIZE', 'HUD_WIDTH']  # Removed WINDOW_WIDTH, WINDOW_HEIGHT
        },
        'Population': {
            'type': 'category',
            'settings': ['INITIAL_AGENTS', 'MAX_FOOD', 'FOOD_SPAWN_RATE']
        },
        'Food Clusters': {
            'type': 'category',
            'settings': ['NUM_FOOD_CLUSTERS', 'FOOD_CLUSTER_SPREAD', 'SEASON_SHIFT_INTERVAL']
        },
        'Water': {
            'type': 'category',
            'settings': ['NUM_WATER_SOURCES', 'WATER_SOURCE_RADIUS', 'RIVER_WIDTH', 'LAKE_SIZE_UNIFORM', 'LAKE_SIZE', 'LAKE_IRREGULARITY']
        },
        'Obstacles': {
            'type': 'category',
            'settings': ['OBSTACLES_ENABLED', 'TREES_ENABLED', 'BORDER_ENABLED', 'BORDER_WIDTH', 'NUM_INTERNAL_OBSTACLES', 'NUM_TREES', 'TREE_DENSITY', 'ENABLE_TREE_FOOD_SOURCES', 'TREE_FOOD_PROXIMITY', 'TREE_FOOD_SPAWN_RATE']
        },
        'Temperature': {
            'type': 'category',
            'settings': ['TEMPERATURE_ENABLED', 'TEMPERATURE_ZONES_X', 'TEMPERATURE_ZONES_Y']
        },
        'Regions': {
            'type': 'category',
            'settings': ['REGIONAL_VARIATIONS_ENABLED', 'NUM_REGIONS_X', 'NUM_REGIONS_Y',
                         'REGION_SPEED_MODIFIER', 'REGION_SIZE_MODIFIER', 'REGION_AGGRESSION_MODIFIER', 'REGION_EFFICIENCY_MODIFIER'],
        },
        'Epidemic': {
            'type': 'category',
            'settings': ['EPIDEMIC_ENABLED', 'EPIDEMIC_INTERVAL', 'EPIDEMIC_MIN_POPULATION_RATIO',
                         'EPIDEMIC_AFFECTED_RATIO', 'EPIDEMIC_BASE_PROBABILITY'],
        },
        'Disease': {
            'type': 'category',
            'settings': ['DISEASE_TRANSMISSION_ENABLED', 'DISEASE_TRANSMISSION_DISTANCE', 'DISEASE_NAMES', 'NUM_DISEASE_TYPES'],
        },
    },
    'agent': {
        'Agents': {
            'type': 'category',
            'settings': ['MAX_SPEED_BASE', 'EATING_DISTANCE', 'MATING_DISTANCE', 'WANDER_STRENGTH', 'STEER_STRENGTH']
        },
        'Genetics & Heredity': {  # Parent category for all genetics-related settings
            'type': 'parent',
            'children': {
                'Genetics': {
                    'type': 'category',
                    'settings': ['MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE', 'DOMINANCE_MUTATION_RATE',
                                 'POINT_MUTATION_STDDEV', 'LARGE_MUTATION_STDDEV', 'SOMATIC_MUTATION_RATE']
                },
                'Species': {
                    'type': 'category',
                    'settings': ['INITIAL_SAME_SPECIES_PERCENTAGE', 'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE',
                                 'HYBRID_FERTILITY_RATE', 'NUMBER_OF_INITIAL_SPECIES']
                },
                'Age Initialization': {
                    'type': 'category',
                    'settings': ['MAX_AGE', 'MATURITY_AGE', 'RANDOM_AGE_INITIALIZATION', 'NUMBER_OF_INITIAL_SPECIES']
                },
                'Diet & Habitat': {
                    'type': 'category',
                    'settings': ['diet_type', 'habitat_preference', 'diet_speed_efficiency', 'habitat_energy_cost', 'diet_energy_conversion', 'habitat_movement_efficiency', 'RANDOMIZE_DIET_TYPE', 'RANDOMIZE_HABITAT_PREF']
                },
                'Specific Specs': {
                    'type': 'category',
                    'settings': ['AQUATIC_TERRAIN_PENALTY', 'TERRESTRIAL_WATER_PENALTY', 'HABITAT_TRANSITION_COST', 'AQUATIC_SWIMMING_EFFICIENCY', 'TERRESTRIAL_LAND_EFFICIENCY', 'DIET_FOOD_PREFERENCE_CARNIVORE', 'DIET_FOOD_PREFERENCE_HERBIVORE', 'DIET_FOOD_PREFERENCE_OMNIVORE', 'speed_in_water_aquatic', 'speed_in_water_amphibious', 'speed_in_water_terrestrial', 'land_speed_aquatic', 'land_speed_amphibious', 'land_speed_terrestrial', 'energy_consumption_aquatic', 'energy_consumption_amphibious', 'energy_consumption_terrestrial', 'vision_range_aquatic', 'vision_range_amphibious', 'vision_range_terrestrial']
                }
            }
        },
        'Brain': {  # Parent category for brain-related settings
            'type': 'parent',
            'children': {
                'Neural Network': {
                    'type': 'category',
                    'settings': ['NN_TYPE', 'NN_HIDDEN_SIZE', 'NN_WEIGHT_INIT_STD', 'NN_RECURRENT_IDENTITY_BIAS',
                                 'NN_HIDDEN_NOISE_ENABLED', 'NN_HIDDEN_NOISE_STD']
                },
                'N-Step Memory': {
                    'type': 'category',
                    'settings': ['N_STEP_MEMORY_ENABLED', 'N_STEP_MEMORY_DEPTH']
                },
                'Sensing': {
                    'type': 'category',
                    'settings': ['SECTOR_COUNT', 'VISION_NOISE_STD']
                },
                'Sensory Noise': {
                    'type': 'category',
                    'settings': ['SENSORY_NOISE_ENABLED', 'SENSOR_DROPOUT_RATE', 'INTERNAL_STATE_NOISE', 'PERCEPTION_LAG']
                }
            }
        },
        'Advanced Features': {  # Parent category for all advanced features
            'type': 'parent',
            'children': {
                'Stress System': {
                    'type': 'category',
                    'settings': ['STRESS_GAIN_RATE', 'STRESS_DECAY_RATE', 'STRESS_THREAT_WEIGHT', 'STRESS_RESOURCE_WEIGHT']
                },
                'Effort System': {
                    'type': 'category',
                    'settings': ['EFFORT_SPEED_SCALE', 'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE']
                },
                'Size Effects': {
                    'type': 'category',
                    'settings': ['ADVANCED_SIZE_EFFECTS_ENABLED', 'SIZE_ATTACK_SCALING', 'SIZE_SPEED_PENALTY',
                                 'SIZE_TURN_PENALTY', 'SIZE_METABOLIC_SCALING', 'SIZE_PERCEPTION_BONUS']
                },
                'Energy Scaling': {
                    'type': 'category',
                    'settings': ['SUPERLINEAR_ENERGY_SCALING', 'ENERGY_SIZE_EXPONENT', 'EFFORT_SIZE_INTERACTION']
                },
                'Age Effects': {
                    'type': 'category',
                    'settings': ['AGE_EFFECTS_ENABLED', 'AGE_PRIME_START', 'AGE_PRIME_END', 'AGE_SPEED_DECLINE',
                                'AGE_STAMINA_DECLINE', 'AGE_EXPERIENCE_BONUS', 'AGE_REPRODUCTION_CURVE']
                },
                'Internal State': {
                    'type': 'category',
                    'settings': ['INTERNAL_STATE_MODULATION_ENABLED', 'LOW_ENERGY_ATTACK_PENALTY',
                                'LOW_HYDRATION_SPEED_PENALTY', 'HIGH_STRESS_EFFORT_BOOST', 'EXHAUSTION_THRESHOLD']
                },
                'Action Costs': {
                    'type': 'category',
                    'settings': ['ACTION_COSTS_ENABLED', 'COST_HIGH_SPEED_MULTIPLIER', 'COST_SHARP_TURN_MULTIPLIER',
                            'COST_PURSUIT_MULTIPLIER', 'COST_ATTACK_BASE', 'COST_MATING_BASE']
                },
                'Morphology': {
                    'type': 'category',
                    'settings': ['MORPHOLOGY_TRAITS_ENABLED', 'AGILITY_SPEED_BONUS', 'AGILITY_STAMINA_COST',
                                'ARMOR_DAMAGE_REDUCTION', 'ARMOR_SPEED_PENALTY', 'ARMOR_ENERGY_COST']
                },
                'Context Signals': {
                    'type': 'category',
                    'settings': ['CONTEXT_SIGNALS_ENABLED', 'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY',
                            'TIME_SINCE_MATING_DECAY']
                },
                'Social Pressure': {
                    'type': 'category',
                    'settings': ['SOCIAL_PRESSURE_ENABLED', 'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD',
                            'CROWD_STRESS_RATE', 'DOMINANCE_STRESS_FACTOR']
                }
            }
        },
        'Physiology & Behavior': {  # Parent category for core physiological and behavioral settings
            'type': 'parent',
            'children': {
                'Energy': {
                    'type': 'category',
                    'settings': ['BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_THRESHOLD', 'REPRODUCTION_COST',
                                 'FOOD_ENERGY', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR']
                },
                'Hydration': {
                    'type': 'category',
                    'settings': ['BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_DRAIN_RATE', 'DRINK_RATE']
                },
                'Combat': {
                    'type': 'category',
                    'settings': ['ATTACK_DISTANCE', 'ATTACK_DAMAGE_BASE', 'ATTACK_ENERGY_COST', 'KILL_ENERGY_GAIN', 'CANNIBALISM_ENERGY_BONUS']
                },
                'Reproduction': {
                    'type': 'category',
                    'settings': ['REPRODUCTION_COOLDOWN', 'MATE_SEARCH_RADIUS', 'MAX_SIMULTANEOUS_OFFSPRING']
                }
            }
        }
    }
}

# Initialize categories as expanded
for cat_name, cat_data in HIERARCHICAL_CATEGORIES['environmental'].items():
    if cat_data['type'] == 'parent':
        expanded_categories[cat_name] = True
        # Also initialize children
        for child_name in cat_data['children']:
            expanded_categories[child_name] = True
    else:
        expanded_categories[cat_name] = True

for cat_name, cat_data in HIERARCHICAL_CATEGORIES['agent'].items():
    if cat_data['type'] == 'parent':
        expanded_categories[cat_name] = True
        # Also initialize children
        for child_name in cat_data['children']:
            expanded_categories[child_name] = True
    else:
        expanded_categories[cat_name] = True


def draw_settings_screen(screen, settings, font_large, font_med):
    """Draw the settings screen with improved layout."""
    global scroll_y, max_scroll, input_texts, setting_rects, plus_rects, minus_rects, input_rects, category_rects, current_view

    screen_width, screen_height = screen.get_size()

    # Sync region arrays before initializing input texts
    _sync_region_arrays(settings)

    # Initialize input texts based on current view using hierarchical structure
    categories_to_use = HIERARCHICAL_CATEGORIES[current_view]
    _initialize_input_texts_for_hierarchy(categories_to_use, settings)


def _initialize_input_texts_for_hierarchy(categories_dict, settings):
    """Initialize input texts for hierarchical category structure."""
    for category_name, category_data in categories_dict.items():
        if category_data['type'] == 'parent':
            # Process children of parent category
            for child_name, child_data in category_data['children'].items():
                for key in child_data['settings']:
                    if key in settings:
                        if isinstance(settings[key], list):
                            input_texts[key] = str(settings[key])
                            # Always update array elements to match current array size
                            for i, value in enumerate(settings[key]):
                                input_texts[f"{key}_element_{i}"] = str(value)
                        elif key not in input_texts:
                            input_texts[key] = str(settings[key])
        else:
            # Process regular category
            for key in category_data['settings']:
                if key in settings:
                    if isinstance(settings[key], list):
                        input_texts[key] = str(settings[key])
                        # Always update array elements to match current array size
                        for i, value in enumerate(settings[key]):
                            input_texts[f"{key}_element_{i}"] = str(value)
                    elif key not in input_texts:
                        input_texts[key] = str(settings[key])


def draw_settings_screen(screen, settings, font_large, font_med):
    """Draw the settings screen with improved layout."""
    global scroll_y, max_scroll, input_texts, setting_rects, plus_rects, minus_rects, input_rects, category_rects, current_view

    screen_width, screen_height = screen.get_size()

    # Sync region arrays before initializing input texts
    _sync_region_arrays(settings)

    # Initialize input texts based on current view using hierarchical structure
    categories_to_use = HIERARCHICAL_CATEGORIES[current_view]
    _initialize_input_texts_for_hierarchy(categories_to_use, settings)

    # Clear rects
    setting_rects = {}
    plus_rects = {}
    minus_rects = {}
    input_rects = {}
    category_rects = {}

    # Background
    screen.fill(BG_COLOR)

    # Content area (without header initially)
    content_x = 30
    content_width = screen_width - 60
    header_height = 100  # Increased height to accommodate view tabs
    y_offset = header_height + 15

    # Calculate layout - two columns if wide enough
    use_two_columns = screen_width > 1200
    col_width = (content_width - 20) // 2 if use_two_columns else content_width

    # Draw categories based on current view using hierarchical structure
    categories_to_use = HIERARCHICAL_CATEGORIES[current_view]
    category_items = list(categories_to_use.items())
    col = 0
    col_y = [y_offset, y_offset]  # Track Y for each column

    # Define brain-related categories for visual grouping
    brain_categories = {'Neural Network', 'N-Step Memory', 'Sensing'}

    for cat_idx, (category_name, category_data) in enumerate(category_items):
        if use_two_columns:
            # Alternate columns
            col = 0 if col_y[0] <= col_y[1] else 1
            x = content_x + col * (col_width + 20)
            y = col_y[col]
        else:
            x = content_x
            y = y_offset

        # Handle hierarchical categories
        if category_data['type'] == 'parent':
            # Draw parent category with its children
            y = _draw_parent_category(screen, x, y, col_width, category_name, category_data, settings, font_med, col_y if use_two_columns else None, col if use_two_columns else None)
        else:
            # Draw regular category
            card_height = _calculate_category_height(category_name, category_data['settings'], settings, expanded_categories.get(category_name, True))
            visible_y = y - scroll_y

            if visible_y + card_height > header_height and visible_y < screen_height - 80:
                _draw_category_card(screen, x, visible_y, col_width, card_height, category_name, category_data['settings'], settings, font_med)

            # Store category rect for click detection
            category_rects[category_name] = pygame.Rect(x, visible_y, col_width, 35)

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

    # Define subtitle font once to be used in both buttons and header
    subtitle_font = pygame.font.SysFont('monospace', 12)

    # Bottom buttons
    button_y = screen_height - 65

    # Start button
    start_rect = pygame.Rect(screen_width // 2 - 110, button_y, 220, 45)
    pygame.draw.rect(screen, BUTTON_COLOR, start_rect, border_radius=5)
    pygame.draw.rect(screen, ACCENT_COLOR, start_rect, 2, border_radius=5)
    start_text = font_med.render("START SIMULATION", True, (255, 255, 255))
    screen.blit(start_text, (start_rect.centerx - start_text.get_width() // 2,
                             start_rect.centery - start_text.get_height() // 2))

    # Save Configuration button (to the left of Start)
    save_rect = pygame.Rect(screen_width // 2 - 250, button_y + 5, 130, 35)
    pygame.draw.rect(screen, PANEL_COLOR, save_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, save_rect, 1, border_radius=3)
    save_text = subtitle_font.render("Save Config", True, MUTED_COLOR)
    screen.blit(save_text, (save_rect.centerx - save_text.get_width() // 2,
                            save_rect.centery - save_text.get_height() // 2))

    # Load Configuration button (to the right of Start)
    load_rect = pygame.Rect(screen_width // 2 + 140, button_y + 5, 130, 35)
    pygame.draw.rect(screen, PANEL_COLOR, load_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, load_rect, 1, border_radius=3)
    load_text = subtitle_font.render("Load Config", True, MUTED_COLOR)
    screen.blit(load_text, (load_rect.centerx - load_text.get_width() // 2,
                            load_rect.centery - load_text.get_height() // 2))

    # Fullscreen button (far right)
    fs_rect = pygame.Rect(screen_width - 180, button_y + 5, 150, 35)
    pygame.draw.rect(screen, PANEL_COLOR, fs_rect, border_radius=3)
    pygame.draw.rect(screen, BORDER_COLOR, fs_rect, 1, border_radius=3)
    fs_text = subtitle_font.render("Toggle Fullscreen", True, MUTED_COLOR)
    screen.blit(fs_text, (fs_rect.centerx - fs_text.get_width() // 2,
                          fs_rect.centery - fs_text.get_height() // 2))

    # Create a surface for the header to draw on top
    header_surface = pygame.Surface((screen_width, header_height), pygame.SRCALPHA)
    header_surface.fill((0, 0, 0, 0))  # Transparent background
    pygame.draw.rect(header_surface, HEADER_COLOR, (0, 0, screen_width, header_height))
    pygame.draw.line(header_surface, BORDER_COLOR, (0, header_height-2), (screen_width, header_height-2), 2)

    # Title
    title = font_large.render("Simulation Configuration", True, ACCENT_COLOR)
    header_surface.blit(title, (screen_width // 2 - title.get_width() // 2, 15))

    # Subtitle
    subtitle = subtitle_font.render("Neural Network Evolution Simulation", True, MUTED_COLOR)
    header_surface.blit(subtitle, (screen_width // 2 - subtitle.get_width() // 2, 43))

    # View tabs (Environmental and Agent Settings)
    # Calculate tab widths based on text to ensure proper fitting
    env_text = font_med.render("Environmental Settings", True, TEXT_COLOR if current_view == 'environmental' else MUTED_COLOR)
    agent_text = font_med.render("Agent Settings", True, TEXT_COLOR if current_view == 'agent' else MUTED_COLOR)

    # Add padding to text width to ensure proper fit
    tab_padding = 20
    env_tab_width = max(180, env_text.get_width() + tab_padding)
    agent_tab_width = max(120, agent_text.get_width() + tab_padding)
    tab_height = 35  # Increased height for better text visibility
    env_tab_x = screen_width // 2 - env_tab_width - 10
    agent_tab_x = screen_width // 2 + 10

    # Environmental Tab
    env_tab_color = ACCENT_COLOR if current_view == 'environmental' else PANEL_COLOR
    env_border_color = ACCENT_COLOR if current_view == 'environmental' else BORDER_COLOR
    pygame.draw.rect(header_surface, env_tab_color, (env_tab_x, 60, env_tab_width, tab_height), border_radius=5)
    pygame.draw.rect(header_surface, env_border_color, (env_tab_x, 60, env_tab_width, tab_height), 2, border_radius=5)
    header_surface.blit(env_text, (env_tab_x + env_tab_width // 2 - env_text.get_width() // 2,
                           60 + tab_height // 2 - env_text.get_height() // 2))

    # Agent Tab
    agent_tab_color = ACCENT_COLOR if current_view == 'agent' else PANEL_COLOR
    agent_border_color = ACCENT_COLOR if current_view == 'agent' else BORDER_COLOR
    pygame.draw.rect(header_surface, agent_tab_color, (agent_tab_x, 60, agent_tab_width, tab_height), border_radius=5)
    pygame.draw.rect(header_surface, agent_border_color, (agent_tab_x, 60, agent_tab_width, tab_height), 2, border_radius=5)
    header_surface.blit(agent_text, (agent_tab_x + agent_tab_width // 2 - agent_text.get_width() // 2,
                             60 + tab_height // 2 - agent_text.get_height() // 2))

    # Blit the header surface on top of everything else
    screen.blit(header_surface, (0, 0))

    # Draw tooltip if mouse is hovering over a parameter
    mouse_pos = pygame.mouse.get_pos()
    for key, rect in tooltip_rects.items():
        if rect.collidepoint(mouse_pos):
            explanation = _get_parameter_explanation(key)
            _draw_tooltip(screen, mouse_pos[0] + 10, mouse_pos[1] + 10, explanation, font_med)
            break  # Only show one tooltip at a time

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

    # Diet and Habitat specific settings visibility based on selected preferences
    if category == 'Diet & Habitat':
        # For all settings in Diet & Habitat category (like diet_type, habitat_preference, etc.), show them
        return True

    # Specific Specs settings - show only relevant settings based on current diet and habitat preferences
    if category == 'Specific Specs':
        # Return True only if the setting is relevant to current selections
        return _is_setting_relevant(key, settings)

    return True


def _is_setting_relevant(key, settings):
    """Determine if a setting is particularly relevant based on current selections."""
    current_diet = settings.get('diet_type', 1.0)
    current_habitat = settings.get('habitat_preference', 1.0)

    # Determine diet type
    is_carnivore = abs(current_diet - 0.0) < 0.5  # 0.0
    is_omnivore = abs(current_diet - 1.0) < 0.5   # 1.0
    is_herbivore = abs(current_diet - 2.0) < 0.5  # 2.0

    # Determine habitat type
    is_aquatic = current_habitat <= 0.5      # 0.0
    is_amphibious = 0.5 < current_habitat < 1.5  # 1.0
    is_terrestrial = current_habitat >= 1.5  # 2.0

    # Diet-specific settings
    if key.startswith('DIET_FOOD_PREFERENCE_'):
        if key == 'DIET_FOOD_PREFERENCE_CARNIVORE':
            return is_carnivore
        elif key == 'DIET_FOOD_PREFERENCE_HERBIVORE':
            return is_herbivore
        elif key == 'DIET_FOOD_PREFERENCE_OMNIVORE':
            return is_omnivore

    # Habitat-specific settings
    if key == 'AQUATIC_TERRAIN_PENALTY':
        return is_aquatic or is_amphibious  # Relevant for aquatic or amphibious agents on land
    elif key == 'TERRESTRIAL_WATER_PENALTY':
        return is_terrestrial or is_amphibious  # Relevant for terrestrial or amphibious agents in water
    elif key == 'AQUATIC_SWIMMING_EFFICIENCY':
        return is_aquatic or is_amphibious  # Relevant for aquatic or amphibious agents in water
    elif key == 'TERRESTRIAL_LAND_EFFICIENCY':
        return is_terrestrial or is_amphibious  # Relevant for terrestrial or amphibious agents on land
    elif key == 'HABITAT_TRANSITION_COST':
        return is_amphibious  # Relevant for amphibious agents transitioning between habitats
    elif key == 'speed_in_water_aquatic':
        return is_aquatic  # Relevant only for aquatic agents
    elif key == 'speed_in_water_amphibious':
        return is_amphibious  # Relevant only for amphibious agents
    elif key == 'speed_in_water_terrestrial':
        return is_terrestrial  # Relevant only for terrestrial agents
    elif key == 'land_speed_aquatic':
        return is_aquatic  # Relevant only for aquatic agents
    elif key == 'land_speed_amphibious':
        return is_amphibious  # Relevant only for amphibious agents
    elif key == 'land_speed_terrestrial':
        return is_terrestrial  # Relevant only for terrestrial agents
    elif key == 'energy_consumption_aquatic':
        return is_aquatic  # Relevant only for aquatic agents
    elif key == 'energy_consumption_amphibious':
        return is_amphibious  # Relevant only for amphibious agents
    elif key == 'energy_consumption_terrestrial':
        return is_terrestrial  # Relevant only for terrestrial agents
    elif key == 'vision_range_aquatic':
        return is_aquatic  # Relevant only for aquatic agents
    elif key == 'vision_range_amphibious':
        return is_amphibious  # Relevant only for amphibious agents
    elif key == 'vision_range_terrestrial':
        return is_terrestrial  # Relevant only for terrestrial agents

    # If none of the specific conditions matched, the setting is not relevant to current selections
    return False


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


def _draw_category_card(screen, x, y, width, height, category, keys, settings, font, is_grouped=False, is_last_in_group=False):
    """Draw a category card with its settings."""
    global setting_rects, plus_rects, minus_rects, input_rects

    # Sync region arrays if this is the Regions category
    if category == 'Regions':
        _sync_region_arrays(settings)

    # Card background - for grouped categories, adjust appearance
    if is_grouped:
        # For grouped categories, use a more subtle border to show connection
        if is_last_in_group:
            # Last in group gets full rounded corners
            pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height), border_radius=5)
            pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 1, border_radius=5)
        else:
            # Middle items in group connect to next item with no bottom border
            pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height), border_radius=5)
            # Draw only top and sides, not bottom to connect with next
            pygame.draw.line(screen, BORDER_COLOR, (x, y), (x + width, y), 1)  # Top
            pygame.draw.line(screen, BORDER_COLOR, (x, y), (x, y + height), 1)  # Left
            pygame.draw.line(screen, BORDER_COLOR, (x + width, y), (x + width, y + height), 1)  # Right
    else:
        # Normal card appearance
        pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height), border_radius=5)
        pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 1, border_radius=5)

    # Get expansion state for this category
    category_expanded = expanded_categories.get(category, True)

    if not category_expanded:
        # Just draw the header for collapsed categories
        header_rect = pygame.Rect(x, y, width, 35)
        pygame.draw.rect(screen, PANEL_COLOR, header_rect, border_top_left_radius=5, border_top_right_radius=5)

        # Expand/collapse indicator
        indicator = "[-]" if category_expanded else "[+]"
        ind_font = pygame.font.SysFont('monospace', 14)
        ind_text = ind_font.render(indicator, True, ACCENT_COLOR)
        screen.blit(ind_text, (x + 10, y + 10))

        # Category name
        cat_text = font.render(category, True, TEXT_COLOR)
        screen.blit(cat_text, (x + 40, y + 9))
        return

    # Header
    header_rect = pygame.Rect(x, y, width, 35)
    pygame.draw.rect(screen, PANEL_COLOR, header_rect, border_top_left_radius=5, border_top_right_radius=5)

    # Expand/collapse indicator
    indicator = "[-]" if category_expanded else "[+]"
    ind_font = pygame.font.SysFont('monospace', 14)
    ind_text = ind_font.render(indicator, True, ACCENT_COLOR)
    screen.blit(ind_text, (x + 10, y + 10))

    # Category name
    cat_text = font.render(category, True, TEXT_COLOR)
    screen.blit(cat_text, (x + 40, y + 9))

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
        elif key == 'diet_type':
            _draw_enum_setting(screen, x + 10, row_y, width - 20, key, value, small_font, ['Carnivore', 'Omnivore', 'Herbivore'])
            row_y += row_height
        elif key == 'habitat_preference':
            _draw_enum_setting(screen, x + 10, row_y, width - 20, key, value, small_font, ['Aquatic', 'Amphibious', 'Terrestrial'])
            row_y += row_height
        else:
            _draw_numeric_setting(screen, x + 10, row_y, width - 20, key, value, small_font, value_font)
            row_y += row_height


def _draw_numeric_setting(screen, x, y, width, key, value, label_font, value_font):
    """Draw a numeric setting with +/- buttons."""
    global setting_rects, plus_rects, minus_rects, input_rects, tooltip_rects

    # Format key name nicely
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 25:
        display_name = display_name[:22] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Draw asterisk next to the label
    asterisk = label_font.render("*", True, ACCENT_COLOR)
    asterisk_x = x + label.get_width() + 5
    asterisk_y = y + 5
    screen.blit(asterisk, (asterisk_x, asterisk_y))

    # Store tooltip rect for hover detection
    tooltip_rects[key] = pygame.Rect(asterisk_x, asterisk_y, asterisk.get_width(), asterisk.get_height())

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
    global setting_rects, tooltip_rects

    # Format key name
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 30:
        display_name = display_name[:27] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Draw asterisk next to the label
    asterisk = label_font.render("*", True, ACCENT_COLOR)
    asterisk_x = x + label.get_width() + 5
    asterisk_y = y + 5
    screen.blit(asterisk, (asterisk_x, asterisk_y))

    # Store tooltip rect for hover detection
    tooltip_rects[key] = pygame.Rect(asterisk_x, asterisk_y, asterisk.get_width(), asterisk.get_height())

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
    global setting_rects, tooltip_rects

    # Format key name
    display_name = key.replace('_', ' ').title()
    if len(display_name) > 25:
        display_name = display_name[:22] + "..."

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y + 5))

    # Draw asterisk next to the label
    asterisk = label_font.render("*", True, ACCENT_COLOR)
    asterisk_x = x + label.get_width() + 5
    asterisk_y = y + 5
    screen.blit(asterisk, (asterisk_x, asterisk_y))

    # Store tooltip rect for hover detection
    tooltip_rects[key] = pygame.Rect(asterisk_x, asterisk_y, asterisk.get_width(), asterisk.get_height())

    # Options buttons
    option_width = 60
    option_height = 22
    option_spacing = 5
    options_x = x + width - (len(options) * (option_width + option_spacing))

    value_font = pygame.font.SysFont('monospace', 11)

    # For diet_type and habitat_preference, map numeric values to string options
    if key == 'diet_type':
        # Map numeric value to string option
        if value == 0.0:
            current_option = 'Carnivore'
        elif value == 1.0:
            current_option = 'Omnivore'
        elif value == 2.0:
            current_option = 'Herbivore'
        else:
            current_option = str(value)  # fallback
    elif key == 'habitat_preference':
        # Map numeric value to string option
        if value == 0.0:
            current_option = 'Aquatic'
        elif value == 1.0:
            current_option = 'Amphibious'
        elif value == 2.0:
            current_option = 'Terrestrial'
        else:
            current_option = str(value)  # fallback
    else:
        # For other enum settings, use the value directly
        current_option = value

    for i, option in enumerate(options):
        opt_x = options_x + i * (option_width + option_spacing)
        opt_rect = pygame.Rect(opt_x, y + 2, option_width, option_height)

        is_selected = (current_option == option)

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
    global setting_rects, input_rects, tooltip_rects

    # Format key name - make it more readable
    display_name = key.replace('_', ' ').title()
    # Shorten common prefixes for region modifiers
    display_name = display_name.replace('Region ', '').replace(' Modifier', '')

    # Label
    label = label_font.render(display_name, True, MUTED_COLOR)
    screen.blit(label, (x, y))

    # Draw asterisk next to the label
    asterisk = label_font.render("*", True, ACCENT_COLOR)
    asterisk_x = x + label.get_width() + 5
    asterisk_y = y
    screen.blit(asterisk, (asterisk_x, asterisk_y))

    # Store tooltip rect for hover detection
    tooltip_rects[key] = pygame.Rect(asterisk_x, asterisk_y, asterisk.get_width(), asterisk.get_height())

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


import json
import os

def handle_settings_input(settings, event):
    """Handle input on the settings screen."""
    global scroll_y, active_input, input_texts, expanded_categories, current_view, tooltip_rects

    # Get screen dimensions from pygame surface
    # Handle the case where pygame surface might not be available
    try:
        screen_surface = pygame.display.get_surface()
        screen_width, screen_height = screen_surface.get_size()
    except:
        # Default values if pygame surface is not available
        screen_width, screen_height = 1200, 800

    # Calculate tab rectangles to match the display
    # Use a default font since we don't have access to the font parameters here
    font_med = pygame.font.SysFont('monospace', 14)
    env_text = font_med.render("Environmental Settings", True, TEXT_COLOR if current_view == 'environmental' else MUTED_COLOR)
    agent_text = font_med.render("Agent Settings", True, TEXT_COLOR if current_view == 'agent' else MUTED_COLOR)

    tab_padding = 20
    env_tab_width = max(180, env_text.get_width() + tab_padding)
    agent_tab_width = max(120, agent_text.get_width() + tab_padding)
    tab_height = 35
    env_tab_x = screen_width // 2 - env_tab_width - 10
    agent_tab_x = screen_width // 2 + 10
    tab_y = 60

    # Start button
    start_rect = pygame.Rect(screen_width // 2 - 110, screen_height - 65, 220, 45)

    # Save Configuration button
    save_rect = pygame.Rect(screen_width // 2 - 250, screen_height - 60, 130, 35)

    # Load Configuration button
    load_rect = pygame.Rect(screen_width // 2 + 140, screen_height - 60, 130, 35)

    # Fullscreen button
    fs_rect = pygame.Rect(screen_width - 180, screen_height - 60, 150, 35)

    # Scroll handling
    if event.type == pygame.MOUSEWHEEL:
        scroll_y = max(0, min(max_scroll, scroll_y - event.y * SCROLL_STEP))
        return None

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos

        # Check tab switches
        env_tab_rect = pygame.Rect(env_tab_x, tab_y, env_tab_width, tab_height)
        agent_tab_rect = pygame.Rect(agent_tab_x, tab_y, agent_tab_width, tab_height)

        if env_tab_rect.collidepoint(pos):
            current_view = 'environmental'
            return None
        elif agent_tab_rect.collidepoint(pos):
            current_view = 'agent'
            return None

        # Check fullscreen button
        if fs_rect.collidepoint(pos):
            return "toggle_fullscreen"

        # Check start button
        if start_rect.collidepoint(pos):
            _apply_input_texts(settings)
            return "start"

        # Check save button
        if save_rect.collidepoint(pos):
            _save_configuration(settings)
            return None

        # Check load button
        if load_rect.collidepoint(pos):
            loaded_settings = _load_configuration_dialog()
            if loaded_settings:
                settings.update(loaded_settings)
                # Update input texts to reflect loaded settings
                for key, value in settings.items():
                    if isinstance(value, list):
                        input_texts[key] = str(value)
                        # Update array elements
                        for i, elem in enumerate(value):
                            input_texts[f"{key}_element_{i}"] = str(elem)
                    else:
                        input_texts[key] = str(value)
            return None

        # Check category headers
        for category, rect in category_rects.items():
            if rect.collidepoint(pos):
                expanded_categories[category] = not expanded_categories.get(category, True)
                return None

        # Check plus buttons
        for key, rect in plus_rects.items():
            if rect.collidepoint(pos) and key in settings:
                prev_value = settings[key]
                _increment_setting(settings, key)
                # Check if this setting affects conditional visibility
                if key in ['diet_type', 'habitat_preference']:
                    # Need to refresh the UI to update visibility of dependent settings
                    refresh_input_texts(settings)
                    # Force a screen update to reflect the changes immediately
                    pygame.display.flip()
                return None

        # Check minus buttons
        for key, rect in minus_rects.items():
            if rect.collidepoint(pos) and key in settings:
                prev_value = settings[key]
                _decrement_setting(settings, key)
                # Check if this setting affects conditional visibility
                if key in ['diet_type', 'habitat_preference']:
                    # Need to refresh the UI to update visibility of dependent settings
                    refresh_input_texts(settings)
                    # Force a screen update to reflect the changes immediately
                    pygame.display.flip()
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
                        # Store previous value to check if it changed
                        prev_value = settings[base_key]

                        # Map string options to numeric values for diet and habitat settings
                        if base_key == 'diet_type':
                            if option_value == 'Carnivore':
                                settings[base_key] = 0.0
                            elif option_value == 'Omnivore':
                                settings[base_key] = 1.0
                            elif option_value == 'Herbivore':
                                settings[base_key] = 2.0
                        elif base_key == 'habitat_preference':
                            if option_value == 'Aquatic':
                                settings[base_key] = 0.0
                            elif option_value == 'Amphibious':
                                settings[base_key] = 1.0
                            elif option_value == 'Terrestrial':
                                settings[base_key] = 2.0
                        else:
                            # For other enum settings, assign the string value directly
                            settings[base_key] = option_value

                        input_texts[base_key] = str(settings[base_key])

                        # Check if the value actually changed and if it affects conditional visibility
                        if base_key in ['diet_type', 'habitat_preference'] and prev_value != settings[base_key]:
                            # Need to refresh the UI to update visibility of dependent settings
                            refresh_input_texts(settings)
                            # Force a screen update to reflect the changes immediately
                            pygame.display.flip()
                    return None
                elif "_element_" in key:
                    active_input = key
                elif key in settings:
                    old_value = settings[key]
                    if isinstance(settings[key], bool):
                        settings[key] = not settings[key]
                        input_texts[key] = str(settings[key])
                        # Check if this setting affects conditional visibility
                        if key in ['diet_type', 'habitat_preference']:
                            # Need to refresh the UI to update visibility of dependent settings
                            refresh_input_texts(settings)
                            # Force a screen update to reflect the changes immediately
                            pygame.display.flip()
                    elif isinstance(settings[key], str):
                        # String settings handled by enum options, skip here
                        pass
                    else:
                        # For numeric settings, check if it's diet_type or habitat_preference
                        # If so, we need to update the UI to reflect the new conditional visibility
                        active_input = key
                        # The value will be updated by _apply_single_input later
                    return None

        # Click outside - deactivate input
        active_input = None

    # Text input handling
    if event.type == pygame.KEYDOWN and active_input is not None:
        if event.key == pygame.K_RETURN:
            prev_value = settings.get(active_input, None)
            _apply_single_input(settings, active_input)
            # Check if this setting affects conditional visibility
            if active_input in ['diet_type', 'habitat_preference'] and prev_value != settings.get(active_input):
                # Need to refresh the UI to update visibility of dependent settings
                refresh_input_texts(settings)
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
    # Create a list of keys to avoid RuntimeError if dict changes during iteration
    keys_to_process = [key for key in input_texts.keys() if "_element_" not in key]
    for key in keys_to_process:
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

        # Check if this setting affects conditional visibility
        if key in ['diet_type', 'habitat_preference']:
            # Need to refresh the UI to update visibility of dependent settings
            refresh_input_texts(settings)
            # Force a screen update to reflect the changes immediately
            pygame.display.flip()


def refresh_input_texts(settings):
    """Refresh the input_texts dictionary to match current settings values."""
    global input_texts

    # Initialize input texts for both environmental and agent categories using hierarchical structure
    all_categories = {}

    # Add environmental categories
    for cat_name, cat_data in HIERARCHICAL_CATEGORIES['environmental'].items():
        if cat_data['type'] == 'parent':
            # Add child categories
            for child_name, child_data in cat_data['children'].items():
                all_categories[child_name] = child_data['settings']
        else:
            all_categories[cat_name] = cat_data['settings']

    # Add agent categories
    for cat_name, cat_data in HIERARCHICAL_CATEGORIES['agent'].items():
        if cat_data['type'] == 'parent':
            # Add child categories
            for child_name, child_data in cat_data['children'].items():
                all_categories[child_name] = child_data['settings']
        else:
            all_categories[cat_name] = cat_data['settings']

    for category, keys in all_categories.items():
        for key in keys:
            if key in settings:
                # Only update input text if the setting should be visible based on conditional logic
                if _should_show_setting(key, settings, category):
                    if isinstance(settings[key], list):
                        input_texts[key] = str(settings[key])
                        # Always update array elements to match current array size
                        for i, value in enumerate(settings[key]):
                            input_texts[f"{key}_element_{i}"] = str(value)
                    else:
                        input_texts[key] = str(settings[key])
                else:
                    # Remove from input_texts if it shouldn't be visible anymore
                    if key in input_texts:
                        del input_texts[key]


def _save_configuration(settings):
    """Save the current configuration to a file."""
    import os
    from datetime import datetime

    # Apply all current input texts to settings before saving
    _apply_input_texts(settings)

    # Create saves directory if it doesn't exist
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'configs')
    os.makedirs(saves_dir, exist_ok=True)

    # Show a simple input dialog to get filename
    filename = _get_user_input_filename("Enter filename for saving:")
    if not filename:
        return  # User cancelled

    if not filename.endswith('.json'):
        filename += '.json'

    file_path = os.path.join(saves_dir, filename)

    # Prepare settings for saving (filter out internal-only keys)
    settings_to_save = {}
    for key, value in settings.items():
        # Save all settings that are not internal (don't start with '_')
        # We should save all settings that are meant to be configurable
        if not key.startswith('_'):
            # Only save values that are serializable
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                settings_to_save[key] = value

    try:
        with open(file_path, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
        print(f"Configuration saved to {file_path}")
    except Exception as e:
        print(f"Error saving configuration: {e}")


def _get_user_input_filename(prompt):
    """Show a simple input dialog to get a filename from the user."""
    import pygame

    # Get the current screen
    screen = pygame.display.get_surface()
    screen_width, screen_height = screen.get_size()

    # Create a temporary input box
    input_box = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 30, 300, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = True
    text = ''
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    # Create overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable
                    active = not active
                else:
                    active = False
                # Change the current color of the input box
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                if event.key == pygame.K_ESCAPE:
                    return None

        screen.blit(overlay, (0, 0))

        # Render prompt
        prompt_surface = font.render(prompt, True, pygame.Color('white'))
        screen.blit(prompt_surface, (screen_width // 2 - prompt_surface.get_width() // 2, screen_height // 2 - 80))

        # Render the current text
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width
        # Draw the input_box
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.draw.rect(screen, (30, 30, 40), input_box)  # Background
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.display.flip()
        clock.tick(30)

    return text if text else None


def _load_configuration_dialog():
    """Open a dialog to load a configuration file."""
    import os

    # Look for saved configurations in the saves directory
    saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'configs')

    if not os.path.exists(saves_dir):
        print("No saved configurations found.")
        return None

    # List all JSON files in the configs directory
    config_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]

    if not config_files:
        print("No saved configurations found.")
        return None

    # Show a file selection dialog
    selected_file = _show_file_selection_dialog(config_files, "Select configuration to load:")
    if not selected_file:
        return None  # User cancelled

    file_path = os.path.join(saves_dir, selected_file)

    try:
        with open(file_path, 'r') as f:
            loaded_settings = json.load(f)
        print(f"Configuration loaded from {file_path}")
        # Refresh the input texts to reflect the loaded settings
        refresh_input_texts(loaded_settings)
        return loaded_settings
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None


def _show_file_selection_dialog(files, prompt):
    """Show a dialog to select a file from a list."""
    import pygame
    import os

    # Get the current screen
    screen = pygame.display.get_surface()
    screen_width, screen_height = screen.get_size()

    # Create overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black

    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    # Calculate dimensions for the selection box
    box_width = 500
    box_height = min(400, len(files) * 35 + 180)  # Adjust height based on number of files
    box_x = screen_width // 2 - box_width // 2
    box_y = screen_height // 2 - box_height // 2

    # Create rectangles for each file (with delete buttons)
    file_rects = []
    delete_rects = []
    for i, file in enumerate(files):
        # File selection rectangle
        file_rect = pygame.Rect(box_x + 20, box_y + 60 + i * 35, box_width - 120, 25)
        file_rects.append((file, file_rect))

        # Delete button rectangle
        delete_rect = pygame.Rect(box_x + box_width - 80, box_y + 60 + i * 35, 60, 25)
        delete_rects.append((file, delete_rect))

    # Create cancel button
    cancel_button = pygame.Rect(screen_width // 2 - 60, box_y + box_height - 40, 120, 30)

    selected_file = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any file was clicked
                for file, rect in file_rects:
                    if rect.collidepoint(event.pos):
                        selected_file = file
                        running = False
                        break
                # Check if any delete button was clicked
                for file, rect in delete_rects:
                    if rect.collidepoint(event.pos):
                        # Confirm deletion
                        if _confirm_delete_dialog(file):
                            # Delete the file
                            saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'configs')
                            file_path = os.path.join(saves_dir, file)
                            try:
                                os.remove(file_path)
                                print(f"Deleted configuration: {file}")
                                # Refresh the file list and redraw
                                new_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
                                if not new_files:
                                    return None  # No files left
                                # Recreate the dialog with updated files
                                return _show_file_selection_dialog(new_files, prompt)
                            except OSError as e:
                                print(f"Error deleting file {file}: {e}")
                        break
                # Check if cancel button was clicked
                if cancel_button.collidepoint(event.pos):
                    return None
                # Check if clicked outside the dialog to cancel
                if not pygame.Rect(box_x, box_y, box_width, box_height - 50).collidepoint(event.pos):
                    return None

        # Draw the dialog
        screen.blit(overlay, (0, 0))

        # Draw the dialog box
        pygame.draw.rect(screen, (50, 50, 60), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 140, 200), (box_x, box_y, box_width, box_height), 2)

        # Draw the prompt
        prompt_surface = font.render(prompt, True, pygame.Color('white'))
        screen.blit(prompt_surface, (screen_width // 2 - prompt_surface.get_width() // 2, box_y + 20))

        # Draw the file list with delete buttons
        for i, (file, file_rect) in enumerate(file_rects):
            delete_rect = delete_rects[i][1]

            # Check if mouse is hovering over the file
            mouse_pos = pygame.mouse.get_pos()
            if file_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (70, 70, 80), file_rect)
            else:
                pygame.draw.rect(screen, (40, 40, 50), file_rect)

            file_surface = small_font.render(file, True, pygame.Color('white'))
            screen.blit(file_surface, (file_rect.x + 5, file_rect.y + 3))

            # Draw delete button
            delete_color = (200, 80, 80) if delete_rect.collidepoint(mouse_pos) else (180, 60, 60)
            pygame.draw.rect(screen, delete_color, delete_rect, border_radius=3)
            pygame.draw.rect(screen, (220, 220, 220), delete_rect, 1, border_radius=3)
            delete_text = small_font.render("Del", True, (255, 255, 255))
            screen.blit(delete_text, (delete_rect.centerx - delete_text.get_width() // 2,
                                     delete_rect.centery - delete_text.get_height() // 2))

        # Draw cancel button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (200, 80, 80) if cancel_button.collidepoint(mouse_pos) else (180, 60, 60)
        pygame.draw.rect(screen, button_color, cancel_button, border_radius=5)
        pygame.draw.rect(screen, (220, 220, 220), cancel_button, 2, border_radius=5)
        cancel_text = small_font.render("Cancel", True, (255, 255, 255))
        screen.blit(cancel_text, (cancel_button.centerx - cancel_text.get_width() // 2,
                                 cancel_button.centery - cancel_text.get_height() // 2))

        # Draw instructions
        inst_surface = small_font.render("Click a file to load, Del to delete, or Cancel", True, pygame.Color('gray'))
        screen.blit(inst_surface, (screen_width // 2 - inst_surface.get_width() // 2, box_y + box_height - 80))

        pygame.display.flip()
        clock.tick(30)

    return selected_file


def _confirm_delete_dialog(filename):
    """Show a confirmation dialog before deleting a file."""
    import pygame

    # Get the current screen
    screen = pygame.display.get_surface()
    screen_width, screen_height = screen.get_size()

    # Create overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # More opaque for modal dialog

    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    # Dialog dimensions
    box_width = 400
    box_height = 150
    box_x = screen_width // 2 - box_width // 2
    box_y = screen_height // 2 - box_height // 2

    # Buttons
    yes_button = pygame.Rect(box_x + 50, box_y + 90, 100, 40)
    no_button = pygame.Rect(box_x + box_width - 150, box_y + 90, 100, 40)

    confirmed = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                    running = False
                elif event.key == pygame.K_y or event.key == pygame.K_RETURN:
                    confirmed = True
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    confirmed = True
                    running = False
                elif no_button.collidepoint(event.pos):
                    running = False

        # Draw the dialog
        screen.blit(overlay, (0, 0))

        # Draw the dialog box
        pygame.draw.rect(screen, (50, 50, 60), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (220, 100, 100), (box_x, box_y, box_width, box_height), 2)

        # Draw the question
        question = font.render("Delete file?", True, pygame.Color('white'))
        screen.blit(question, (box_x + box_width // 2 - question.get_width() // 2, box_y + 20))

        # Draw the filename
        filename_surface = small_font.render(filename, True, pygame.Color('yellow'))
        screen.blit(filename_surface, (box_x + box_width // 2 - filename_surface.get_width() // 2, box_y + 50))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()

        # Yes button
        yes_color = (80, 180, 80) if yes_button.collidepoint(mouse_pos) else (60, 160, 60)
        pygame.draw.rect(screen, yes_color, yes_button, border_radius=5)
        pygame.draw.rect(screen, (220, 220, 220), yes_button, 2, border_radius=5)
        yes_text = small_font.render("Yes", True, (255, 255, 255))
        screen.blit(yes_text, (yes_button.centerx - yes_text.get_width() // 2,
                              yes_button.centery - yes_text.get_height() // 2))

        # No button
        no_color = (200, 80, 80) if no_button.collidepoint(mouse_pos) else (180, 60, 60)
        pygame.draw.rect(screen, no_color, no_button, border_radius=5)
        pygame.draw.rect(screen, (220, 220, 220), no_button, 2, border_radius=5)
        no_text = small_font.render("No", True, (255, 255, 255))
        screen.blit(no_text, (no_button.centerx - no_text.get_width() // 2,
                             no_button.centery - no_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(30)

    return confirmed


def _draw_parent_category(screen, x, y, width, parent_name, parent_data, settings, font, col_y=None, col_idx=None):
    """Draw a parent category with its child categories."""
    global category_rects

    # Draw parent header - account for scroll offset
    expanded = expanded_categories.get(parent_name, True)
    header_height = 40  # Increased height for better readability
    header_y = y - scroll_y  # Apply scroll offset to header position

    # Parent header background with distinctive styling
    header_rect = pygame.Rect(x, header_y, width, header_height)
    pygame.draw.rect(screen, HEADER_COLOR, header_rect, border_top_left_radius=5, border_top_right_radius=5)
    # Add accent line at top
    pygame.draw.rect(screen, ACCENT_COLOR, (x, header_y, width, 2), border_top_left_radius=5, border_top_right_radius=5)

    # Expand/collapse indicator
    indicator = "[-]" if expanded else "[+]"
    ind_font = pygame.font.SysFont('monospace', 16, bold=True)
    ind_text = ind_font.render(indicator, True, ACCENT_COLOR)
    screen.blit(ind_text, (x + 10, header_y + 12))

    # Parent category name with white text for better contrast
    cat_text = font.render(parent_name, True, (255, 255, 255))
    screen.blit(cat_text, (x + 40, header_y + 12))

    # Store parent rect for click detection (with scroll offset applied)
    category_rects[parent_name] = pygame.Rect(x, header_y, width, header_height)

    current_y = y + header_height  # Use original y (before scroll offset) for internal calculations

    if expanded:
        # Draw a visual container around the child categories to show parent-child relationship
        child_categories = list(parent_data['children'].items())
        if child_categories:
            # Calculate total height of child categories
            total_child_height = 0
            for child_name, child_data in child_categories:
                if child_data['type'] == 'category':
                    child_expanded = expanded_categories.get(child_name, True)
                    child_height = _calculate_category_height(child_name, child_data['settings'], settings, child_expanded)
                    if child_expanded:
                        total_child_height += child_height + 5  # Include gap
                    else:
                        total_child_height += 40  # Header height only

            # Draw a more distinct background to indicate the parent container - apply scroll offset
            parent_bg_rect = pygame.Rect(x + 5, current_y - scroll_y - 5, width - 10, total_child_height + 10)
            parent_bg_surface = pygame.Surface((width - 10, total_child_height + 10), pygame.SRCALPHA)
            alpha = 25  # More visible transparency
            parent_bg_surface.fill((*CARD_COLOR[:3], alpha))
            # Draw border to clearly delineate the parent container
            pygame.draw.rect(parent_bg_surface, (*BORDER_COLOR[:3], 80), parent_bg_surface.get_rect(), 1, border_radius=3)
            screen.blit(parent_bg_surface, (x + 5, current_y - scroll_y - 5))

            # Draw child categories with indentation and visual grouping
            for i, (child_name, child_data) in enumerate(child_categories):
                if child_data['type'] == 'category':
                    # Calculate height for child category
                    child_expanded = expanded_categories.get(child_name, True)
                    child_height = _calculate_category_height(child_name, child_data['settings'], settings, child_expanded)

                    visible_y = current_y - scroll_y
                    if visible_y + child_height > 100 and visible_y < screen.get_height() - 80:  # header_height is 100
                        # Draw child category with indentation and visual grouping
                        is_last_child = (i == len(child_categories) - 1)
                        _draw_category_card(screen, x + 15, visible_y, width - 30, child_height, child_name, child_data['settings'], settings, font, is_grouped=True, is_last_in_group=is_last_child)

                    # Store child rect for click detection (with scroll offset applied)
                    category_rects[child_name] = pygame.Rect(x + 15, current_y - scroll_y, width - 30, 35)

                    if child_expanded:
                        current_y += child_height + 5  # Small gap between expanded children
                    else:
                        current_y += 40  # Height of header only

    # Calculate total height for column tracking
    total_height = current_y - y
    if col_y is not None and col_idx is not None:
        col_y[col_idx] = current_y + 15  # Update column y position with more spacing

    return current_y + 15  # Add more spacing after parent category


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

def _get_parameter_explanation(key):
    """Return explanation for a parameter."""
    explanations = {
        # Environmental Settings
        'WORLD_WIDTH': 'Width of the simulation world in pixels\nLarger worlds allow for more complex ecosystems\nbut require more computational resources\nTypical range: 800-4000, extremes: 400 (tiny) to 8000 (massive)',
        'WORLD_HEIGHT': 'Height of the simulation world in pixels\nLarger worlds allow for more complex ecosystems\nbut require more computational resources\nTypical range: 600-3000, extremes: 300 (tiny) to 6000 (massive)',
        'GRID_CELL_SIZE': 'Size of grid cells for spatial partitioning\nUsed for optimization of collision detection\nand spatial queries. Smaller values increase accuracy\nbut decrease performance\nTypical range: 20-100, extremes: 10 (very accurate, slow) to 200 (fast, inaccurate)',
        'HUD_WIDTH': 'Width of the heads-up display panel\nDetermines the space reserved for statistics\nand controls on the right side of the screen\nTypical range: 200-400, extremes: 100 (minimal) to 600 (maximum)',
        'WINDOW_WIDTH': 'Width of the application window\nSets the initial window size when the simulation starts\nTypical range: 1000-4000, extremes: 800 (minimum) to 5000 (maximum)',
        'WINDOW_HEIGHT': 'Height of the application window\nSets the initial window size when the simulation starts\nTypical range: 700-3000, extremes: 600 (minimum) to 4000 (maximum)',
        'INITIAL_AGENTS': 'Number of agents to start the simulation with\nAffects initial competition and resource pressure\non the ecosystem\nTypical range: 50-500, extremes: 10 (sparse) to 2000 (dense)',
        'MAX_FOOD': 'Maximum number of food items in the world\nWhen this limit is reached, no more food will spawn\nuntil some is consumed\nTypical range: 200-1000, extremes: 50 (scarce) to 5000 (abundant)',
        'FOOD_SPAWN_RATE': 'Rate at which food spawns per second\nHigher rates create abundance, lower rates\ncreate scarcity and competition\nTypical range: 10-100, extremes: 1 (very slow) to 500 (very fast)',
        'NUM_FOOD_CLUSTERS': 'Number of food cluster centers in the world\nMore clusters create distributed resources\nwhile fewer create focal points of competition\nTypical range: 3-15, extremes: 1 (single focal point) to 50 (evenly distributed)',
        'FOOD_CLUSTER_SPREAD': 'Radius of food distribution around cluster centers\nLarger values create more dispersed food\nsmaller values create concentrated patches\nTypical range: 20-100, extremes: 5 (very concentrated) to 200 (very dispersed)',
        'SEASON_SHIFT_INTERVAL': 'Time interval for food cluster movement\nSimulates seasonal changes affecting\nresource distribution patterns\nTypical range: 10-300, extremes: 1 (rapidly shifting) to 1000 (almost static)',
        'NUM_WATER_BODIES': 'Number of water bodies in the world\nCritical for agent hydration\ncreates focal points for behavior\nTypical range: 2-10, extremes: 0 (no water) to 30 (abundant water)',
        'WATER_BODY_RADIUS': 'Radius of each water body\nDetermines the area where agents can hydrate\nlarger radii allow more simultaneous access\nTypical range: 20-100, extremes: 5 (small) to 200 (large)',
        'RIVER_WIDTH': 'Width of generated rivers\nAffects the amount of aquatic habitat\navailable for agents with aquatic preferences\nTypical range: 10-50, extremes: 5 (narrow stream) to 100 (wide river)',
        'WATER_BODY_SIZE_UNIFORM': 'Whether to make all water bodies the same size\nWhen enabled, all water bodies will use the fixed size\ninstead of varying sizes\nTypical range: True/False',
        'WATER_BODY_SIZE': 'Fixed size for water bodies when WATER_BODY_SIZE_UNIFORM is True\nDetermines the diameter of all generated water bodies\nwhen uniform sizing is enabled\nTypical range: 30-200, extremes: 10 (tiny) to 500 (huge)',
        'WATER_BODY_IRREGULARITY': 'How irregular the water body shape is\nControls the complexity of the shoreline\nwith higher values creating more complex shapes\nTypical range: 0.0-1.0, extremes: 0.0 (perfectly round) to 1.0 (highly irregular)',
        'OBSTACLES_ENABLED': 'Enable or disable obstacle generation\nObstacles create complex terrain\naffecting movement and strategy',
        'TREES_ENABLED': 'Enable or disable tree generation\nTrees provide environmental features\nand food sources for herbivores\nwhen ENABLE_TREE_FOOD_SOURCES is True',
        'BORDER_ENABLED': 'Enable or disable border walls\nWhen disabled, agents can wrap around\nthe world edges (toroidal world)',
        'BORDER_WIDTH': 'Width of border obstacles around the world\nThicker borders prevent edge exploitation\nby agents\nTypical range: 5-50, extremes: 1 (thin) to 100 (thick)',
        'NUM_INTERNAL_OBSTACLES': 'Number of internal obstacles to create\nAdds complexity to the terrain\ncreating niches and barriers\nTypical range: 2-20, extremes: 0 (open) to 100 (maze-like)',
        'NUM_TREES': 'Number of trees to generate in the world\nTrees provide environmental features\nand food sources for herbivores\nTypical range: 5-50, extremes: 0 (none) to 200 (dense forest)',
        'TREE_DENSITY': 'Density of trees per unit area\nAlternative to NUM_TREES for controlling\ntree population based on world size\nTypical range: 0.001-0.05, extremes: 0.0001 (sparse) to 0.1 (very dense)',
        'ENABLE_TREE_FOOD_SOURCES': 'Enable food generation around trees\nWhen enabled, food will spawn near trees\nproviding resources for herbivores/omnivores',
        'TREE_FOOD_PROXIMITY': 'Distance from trees where food appears\nControls how close to trees food sources\nwill be generated\nTypical range: 10-60, extremes: 5 (very close) to 100 (far)',
        'TREE_FOOD_SPAWN_RATE': 'Rate at which food spawns near trees\nControls how frequently food appears\naround trees\nTypical range: 5-50, extremes: 1 (rare) to 200 (frequent)',
        'TEMPERATURE_ENABLED': 'Enable or disable temperature zones\nCreates environmental variation\naffecting agent survival and behavior',
        'TEMPERATURE_ZONES_X': 'Number of temperature zones horizontally\nDivides the world into horizontal bands\nwith different thermal properties\nTypical range: 2-8, extremes: 1 (uniform) to 20 (fine-grained)',
        'TEMPERATURE_ZONES_Y': 'Number of temperature zones vertically\nDivides the world into vertical bands\nwith different thermal properties\nTypical range: 2-8, extremes: 1 (uniform) to 20 (fine-grained)',
        'REGIONAL_VARIATIONS_ENABLED': 'Enable or disable regional modifiers\nCreates spatial variation in agent traits\nbased on location in the world',
        'NUM_REGIONS_X': 'Number of regions horizontally\nDivides the world into horizontal sections\nwith different environmental modifiers\nTypical range: 2-10, extremes: 1 (uniform) to 20 (fine-grained)',
        'NUM_REGIONS_Y': 'Number of regions vertically\nDivides the world into vertical sections\nwith different environmental modifiers\nTypical range: 2-10, extremes: 1 (uniform) to 20 (fine-grained)',
        'REGION_SPEED_MODIFIER': 'Speed modifiers for each region\nMultiplies agent speed in each region\ncreating spatial advantages\nTypical range: 0.5-2.0, extremes: 0.1 (very slow) to 5.0 (very fast)',
        'REGION_SIZE_MODIFIER': 'Size modifiers for each region\nMultiplies agent size in each region\naffecting resource consumption and combat\nTypical range: 0.5-2.0, extremes: 0.1 (very small) to 5.0 (very large)',
        'REGION_AGGRESSION_MODIFIER': 'Aggression modifiers for each region\nModifies aggressive tendencies\nchanging behavioral patterns\nTypical range: 0.5-2.0, extremes: 0.1 (very passive) to 5.0 (very aggressive)',
        'REGION_EFFICIENCY_MODIFIER': 'Energy efficiency modifiers for each region\nAffects energy consumption rates\ncreating spatial fitness differences\nTypical range: 0.5-2.0, extremes: 0.1 (very inefficient) to 5.0 (very efficient)',
        'EPIDEMIC_ENABLED': 'Enable or disable epidemic events\nTriggers population-wide health crises\nunder certain conditions',
        'EPIDEMIC_INTERVAL': 'Time between epidemic checks\nHow often the system evaluates\nconditions for epidemic outbreaks\nTypical range: 10-1000, extremes: 1 (constant checks) to 10000 (rare checks)',
        'EPIDEMIC_MIN_POPULATION_RATIO': 'Minimum population ratio to trigger epidemic\nPrevents epidemics when population is too low\nto sustain transmission\nTypical range: 0.5-0.95, extremes: 0.1 (low threshold) to 0.99 (high threshold)',
        'EPIDEMIC_AFFECTED_RATIO': 'Fraction of population affected by epidemic\nDetermines the severity of each outbreak\nwhen conditions are met\nTypical range: 0.1-0.8, extremes: 0.01 (minor) to 0.99 (devastating)',
        'EPIDEMIC_BASE_PROBABILITY': 'Base probability of epidemic when conditions met\nControls the likelihood of outbreaks\noccurring when thresholds are reached\nTypical range: 0.0001-0.1, extremes: 0.00001 (rare) to 0.5 (frequent)',
        'DISEASE_TRANSMISSION_ENABLED': 'Enable or disable disease transmission\nAllows pathogens to spread between agents\nthrough proximity',
        'DISEASE_TRANSMISSION_DISTANCE': 'Distance threshold for disease transmission\nMaximum range for pathogen transfer\nbetween infected and susceptible agents\nTypical range: 5-50, extremes: 1 (contact only) to 100 (long-range)',
        'DISEASE_NAMES': 'Names for different diseases in the simulation\nProvides variety in pathogen types\nwith different characteristics',
        'NUM_DISEASE_TYPES': 'Number of different disease types\nIncreases complexity of epidemiological\ndynamics in the population\nTypical range: 2-10, extremes: 1 (simple) to 20 (complex)',

        # Agent Settings
        'MUTATION_RATE': 'Chance of mutation per gene per reproduction event\nControls genetic diversity in offspring\nhigher rates increase evolutionary pace\nTypical range: 0.01-0.5, extremes: 0.001 (stable) to 0.9 (chaotic)',
        'CROSSOVER_RATE': 'Chance of crossover per chromosome per meiosis\nDetermines genetic recombination frequency\naffecting trait inheritance patterns\nTypical range: 0.1-0.8, extremes: 0.01 (rare) to 0.99 (frequent)',
        'LARGE_MUTATION_CHANCE': 'Chance of large-effect mutations within mutations\nRare but significant genetic changes\nthat can create major adaptations\nTypical range: 0.01-0.2, extremes: 0.001 (very rare) to 0.5 (common)',
        'DOMINANCE_MUTATION_RATE': 'Chance a mutation affects dominance instead of value\nControls how often mutations affect\ngenetic dominance relationships\nTypical range: 0.05-0.5, extremes: 0.01 (rare) to 0.9 (frequent)',
        'POINT_MUTATION_STDDEV': 'Standard deviation for point mutations\nDetermines the magnitude of small genetic changes\naffecting gradual adaptation\nTypical range: 0.1-1.0, extremes: 0.01 (minimal) to 5.0 (major)',
        'LARGE_MUTATION_STDDEV': 'Standard deviation for large-effect mutations\nDetermines the magnitude of rare\nsignificant genetic changes\nTypical range: 0.5-3.0, extremes: 0.1 (small) to 10.0 (extreme)',
        'SOMATIC_MUTATION_RATE': 'Rate of mutations occurring during agent lifetime\nCauses genetic changes during life\naffecting phenotypes mid-life\nTypical range: 0.001-0.1, extremes: 0.0001 (rare) to 0.5 (frequent)',
        'NN_TYPE': 'Type of neural network (FNN or RNN)\nFNN: Feed-forward network, simpler\nRNN: Recurrent network, has memory',
        'NN_HIDDEN_SIZE': 'Number of neurons in the hidden layer\nLarger networks can represent more\ncomplex behaviors but are slower\nTypical range: 4-32, extremes: 2 (simple) to 128 (complex)',
        'NN_WEIGHT_INIT_STD': 'Standard deviation for initial weight randomization\nControls initial network variability\naffecting early learning dynamics\nTypical range: 0.1-1.0, extremes: 0.01 (similar) to 5.0 (diverse)',
        'NN_RECURRENT_IDENTITY_BIAS': 'Identity bias for RNN stability\nHelps prevent vanishing gradients\nin recurrent networks\nTypical range: 0.0-1.0, extremes: -2.0 (negative) to 2.0 (strong positive)',
        'NN_HIDDEN_NOISE_ENABLED': 'Add stochastic noise to RNN hidden state\nIntroduces randomness in neural processing\nfor behavioral variation',
        'NN_HIDDEN_NOISE_STD': 'Standard deviation of noise added to hidden state\nControls the amount of neural noise\naffecting decision consistency\nTypical range: 0.01-0.1, extremes: 0.001 (low) to 0.5 (high)',
        'N_STEP_MEMORY_ENABLED': 'Store past hidden states as inputs\nGives feed-forward networks memory-like\nproperties',
        'N_STEP_MEMORY_DEPTH': 'Number of past states to store\nDeeper memory allows longer-term\nbehavioral patterns\nTypical range: 1-10, extremes: 1 (shallow) to 50 (deep)',
        'SECTOR_COUNT': 'Number of angular vision sectors\nDivides the visual field into directional\nsegments for spatial awareness\nTypical range: 3-12, extremes: 1 (basic) to 24 (detailed)',
        'VISION_NOISE_STD': 'Noise added to sensor inputs\nIntroduces uncertainty in perception\nmaking agents less precise\nTypical range: 0.01-0.2, extremes: 0.001 (precise) to 0.8 (very noisy)',
        'STRESS_GAIN_RATE': 'Rate at which stress accumulates\nControls how quickly agents become stressed\nunder adverse conditions\nTypical range: 0.1-2.0, extremes: 0.01 (slow) to 10.0 (fast)',
        'STRESS_DECAY_RATE': 'Rate at which stress naturally decays\nDetermines recovery speed from stressful situations\naffecting resilience\nTypical range: 0.05-1.0, extremes: 0.001 (slow) to 5.0 (fast)',
        'STRESS_THREAT_WEIGHT': 'Weight for nearby threat stress\nIncreases stress from dangerous neighbors\naffecting fight-or-flight responses\nTypical range: 0.1-2.0, extremes: 0.01 (low sensitivity) to 10.0 (high sensitivity)',
        'STRESS_RESOURCE_WEIGHT': 'Weight for low resource stress\nIncreases stress when resources are scarce\nmotivating exploration\nTypical range: 0.1-1.5, extremes: 0.01 (low sensitivity) to 5.0 (high sensitivity)',
        'EFFORT_SPEED_SCALE': 'How much effort affects speed\nHigher effort allows faster movement\nat energy cost\nTypical range: 0.5-2.0, extremes: 0.1 (minimal) to 10.0 (highly amplified)',
        'EFFORT_DAMAGE_SCALE': 'How much effort affects attack damage\nHigher effort increases combat effectiveness\nat energy cost\nTypical range: 0.1-1.0, extremes: 0.01 (minimal) to 5.0 (highly amplified)',
        'EFFORT_ENERGY_SCALE': 'How much effort affects energy cost\nControls the energy penalty for high-effort\nactivities\nTypical range: 0.5-3.0, extremes: 0.1 (low cost) to 10.0 (high cost)',
        'BASE_ENERGY': 'Starting energy for new agents\nDetermines initial survival capacity\nand reproductive readiness\nTypical range: 100-300, extremes: 10 (fragile) to 1000 (robust)',
        'MAX_ENERGY': 'Maximum energy capacity\nUpper limit for energy storage\naffecting survival during scarcity\nTypical range: 200-600, extremes: 50 (low) to 2000 (high)',
        'REPRODUCTION_THRESHOLD': 'Energy needed to reproduce\nMinimum energy required for reproduction\naffects reproductive timing\nTypical range: 50-200, extremes: 10 (easy) to 500 (difficult)',
        'REPRODUCTION_COST': 'Energy cost of reproduction\nReduces parent energy after reproduction\naffecting post-birth survival\nTypical range: 20-100, extremes: 5 (cheap) to 300 (expensive)',
        'FOOD_ENERGY': 'Energy gained from eating food\nAmount of energy restored by consuming food\naffects foraging motivation\nTypical range: 30-100, extremes: 5 (poor) to 300 (rich)',
        'ENERGY_DRAIN_BASE': 'Base energy loss per second\nConstant energy drain regardless of activity\nforcing active foraging\nTypical range: 0.1-1.0, extremes: 0.01 (slow) to 5.0 (fast)',
        'MOVEMENT_ENERGY_FACTOR': 'Energy cost factor for movement\nHigher speeds cost more energy\ncreating speed/endurance trade-offs\nTypical range: 0.005-0.05, extremes: 0.001 (efficient) to 0.2 (costly)',
        'BASE_HYDRATION': 'Starting hydration for new agents\nDetermines initial water balance\nand immediate survival needs\nTypical range: 50-200, extremes: 10 (fragile) to 500 (robust)',
        'MAX_HYDRATION': 'Maximum hydration capacity\nUpper limit for water storage\naffecting survival during drought\nTypical range: 100-300, extremes: 20 (low) to 1000 (high)',
        'HYDRATION_DRAIN_RATE': 'Hydration loss per second\nRate of water loss over time\nrequiring regular water access\nTypical range: 0.1-1.0, extremes: 0.01 (slow) to 5.0 (fast)',
        'DRINK_RATE': 'Hydration gain per second when in water\nSpeed of water intake\naffects time needed for hydration\nTypical range: 10-50, extremes: 1 (slow) to 200 (fast)',
        'ATTACK_DISTANCE': 'Distance at which attacks land\nMaximum range for combat\naffects tactical positioning\nTypical range: 5-20, extremes: 1 (melee only) to 50 (long range)',
        'ATTACK_DAMAGE_BASE': 'Base damage per second for attacks\nDetermines combat lethality\naffecting risk/reward of fighting\nTypical range: 10-50, extremes: 1 (weak) to 200 (lethal)',
        'ATTACK_ENERGY_COST': 'Energy cost per second to attack\nPenalizes prolonged combat\nencouraging decisive action\nTypical range: 1-10, extremes: 0.1 (cheap) to 50 (expensive)',
        'KILL_ENERGY_GAIN': 'Energy gained on successful kill\nReward for successful predation\nencouraging carnivorous strategies\nTypical range: 20-100, extremes: 5 (poor reward) to 500 (rich reward)',
        'MAX_SPEED_BASE': 'Base maximum movement speed\nDetermines locomotion capability\naffecting escape and hunting\nTypical range: 3-10, extremes: 0.5 (slow) to 30 (very fast)',
        'EATING_DISTANCE': 'Distance for eating food\nMaximum range for food consumption\naffects feeding efficiency\nTypical range: 5-20, extremes: 1 (very close) to 50 (long reach)',
        'MATING_DISTANCE': 'Distance for mating\nMaximum range for reproduction\naffects mate-finding success\nTypical range: 20-100, extremes: 5 (close) to 200 (distant)',
        'WANDER_STRENGTH': 'Strength of random wandering movement\nControls exploration vs. directed movement\naffecting resource discovery\nTypical range: 0.1-2.0, extremes: 0.01 (direct) to 5.0 (random)',
        'STEER_STRENGTH': 'Strength of steering behaviors\nControls precision of movement toward\ngoals and away from threats\nTypical range: 0.05-0.5, extremes: 0.01 (imprecise) to 2.0 (precise)',
        'MATURITY_AGE': 'Age at which agents can reproduce\nDetermines generation time\naffecting evolutionary pace\nTypical range: 2-20, extremes: 0.1 (early) to 100 (late)',
        'RANDOM_AGE_INITIALIZATION': 'Initialize agents with random ages\nCreates age diversity in starting population\naffecting early dynamics',
        'REPRODUCTION_COOLDOWN': 'Time between reproduction attempts\nPrevents continuous reproduction\nallowing recovery between births\nTypical range: 1-10, extremes: 0.1 (frequent) to 50 (rare)',
        'MATE_SEARCH_RADIUS': 'Radius to search for mates\nDetermines mate-finding range\naffecting reproductive success\nTypical range: 50-200, extremes: 10 (short) to 500 (long)',
        'MAX_AGE': 'Maximum age before dying of old age\nControls lifespan limits\naffecting generation turnover\nTypical range: 30-200, extremes: 5 (short) to 1000 (long)',
        'CANNIBALISM_ENERGY_BONUS': 'Additional energy from eating other agents\nReward for successful predation\nencouraging carnivorous strategies\nTypical range: 10-100, extremes: 1 (minimal) to 500 (generous)',
        'diet_type': 'Diet classification (0=Carnivore, 1=Omnivore, 2=Herbivore)\nDetermines food preferences and\nefficiency of different food sources',
        'habitat_preference': 'Habitat preference (0=Aquatic, 1=Amphibious, 2=Terrestrial)\nAffects movement and survival in\ndifferent environmental zones',
        'diet_speed_efficiency': 'Speed efficiency based on diet appropriateness\nAffects movement speed depending\non dietary specialization\nTypical range: 0.5-2.0, extremes: 0.1 (inefficient) to 5.0 (efficient)',
        'habitat_energy_cost': 'Energy cost factor based on habitat match\nReduces energy drain when in\npreferred habitat\nTypical range: 0.5-2.0, extremes: 0.1 (efficient) to 5.0 (costly)',
        'diet_energy_conversion': 'Energy conversion efficiency based on diet\nAffects how well different foods\nare converted to usable energy\nTypical range: 0.5-2.0, extremes: 0.1 (inefficient) to 5.0 (efficient)',
        'habitat_movement_efficiency': 'Movement efficiency based on habitat match\nImproves speed when in\npreferred habitat\nTypical range: 0.5-2.0, extremes: 0.1 (inefficient) to 5.0 (efficient)',
        'AQUATIC_TERRAIN_PENALTY': 'Movement penalty for aquatic agents on land\nMost relevant when habitat is Aquatic or Amphibious\nAquatic agents struggle on dry land\nTypical range: 0.1-0.8, extremes: 0.01 (slight) to 0.99 (severe)',
        'TERRESTRIAL_WATER_PENALTY': 'Movement penalty for terrestrial agents in water\nMost relevant when habitat is Amphibious or Terrestrial\nTerrestrial agents struggle in water\nTypical range: 0.1-0.9, extremes: 0.01 (slight) to 0.99 (severe)',
        'HABITAT_TRANSITION_COST': 'Energy cost for habitat transitions\nMost relevant when habitat is Amphibious\nPenalizes agents moving between habitats\nTypical range: 0.5-5.0, extremes: 0.1 (low) to 20.0 (high)',
        'AQUATIC_SWIMMING_EFFICIENCY': 'Swimming efficiency for aquatic agents\nMost relevant when habitat is Aquatic or Amphibious\nHow well aquatic agents move in water\nTypical range: 1.0-3.0, extremes: 0.5 (poor) to 10.0 (excellent)',
        'TERRESTRIAL_LAND_EFFICIENCY': 'Land movement efficiency for terrestrial agents\nMost relevant when habitat is Amphibious or Terrestrial\nHow well terrestrial agents move on land\nTypical range: 1.0-3.0, extremes: 0.5 (poor) to 10.0 (excellent)',
        'DIET_FOOD_PREFERENCE_CARNIVORE': 'Food preference strength for carnivores\nMost relevant when diet is Carnivore\nHow strongly carnivores prefer meat\nTypical range: 0.5-2.0, extremes: 0.1 (weak) to 5.0 (strong)',
        'DIET_FOOD_PREFERENCE_HERBIVORE': 'Food preference strength for herbivores\nMost relevant when diet is Herbivore\nHow strongly herbivores prefer plants\nTypical range: 0.5-2.0, extremes: 0.1 (weak) to 5.0 (strong)',
        'DIET_FOOD_PREFERENCE_OMNIVORE': 'Food preference strength for omnivores\nMost relevant when diet is Omnivore\nHow strongly omnivores prefer mixed foods\nTypical range: 0.5-1.5, extremes: 0.1 (weak) to 3.0 (strong)',
        'speed_in_water_aquatic': 'Speed of aquatic agents when in water\nControls how fast aquatic-type agents move in water\nAffects their ability to navigate aquatic environments\nTypical range: 2.0-8.0, extremes: 0.5 (very slow) to 10.0 (very fast)',
        'speed_in_water_amphibious': 'Speed of amphibious agents when in water\nControls how fast amphibious-type agents move in water\nAffects their ability to navigate between land and water\nTypical range: 1.0-5.0, extremes: 0.5 (very slow) to 8.0 (fast)',
        'speed_in_water_terrestrial': 'Speed of terrestrial agents when in water\nControls how fast land-type agents move in water\nAffects their ability to cross water bodies\nTypical range: 0.5-2.0, extremes: 0.1 (very slow) to 5.0 (moderate)',
        'land_speed_aquatic': 'Speed of aquatic agents on land\nControls how fast aquatic-type agents move on land\nAffects their ability to traverse terrestrial areas\nTypical range: 1.0-4.0, extremes: 0.5 (very slow) to 6.0 (fast)',
        'land_speed_amphibious': 'Speed of amphibious agents on land\nControls how fast amphibious-type agents move on land\nAffects their terrestrial mobility\nTypical range: 2.0-6.0, extremes: 1.0 (slow) to 8.0 (fast)',
        'land_speed_terrestrial': 'Speed of terrestrial agents on land\nControls how fast land-type agents move on land\nAffects their terrestrial mobility\nTypical range: 3.0-7.0, extremes: 1.5 (slow) to 9.0 (very fast)',
        'energy_consumption_aquatic': 'Energy consumption rate for aquatic agents\nControls how quickly aquatic agents consume energy\nAffects their survival duration\nTypical range: 0.5-1.5, extremes: 0.1 (very efficient) to 3.0 (inefficient)',
        'energy_consumption_amphibious': 'Energy consumption rate for amphibious agents\nControls how quickly amphibious agents consume energy\nAffects their survival duration\nTypical range: 0.7-1.3, extremes: 0.2 (efficient) to 2.5 (inefficient)',
        'energy_consumption_terrestrial': 'Energy consumption rate for terrestrial agents\nControls how quickly land agents consume energy\nAffects their survival duration\nTypical range: 0.6-1.4, extremes: 0.2 (efficient) to 2.5 (inefficient)',
        'vision_range_aquatic': 'Vision range for aquatic agents in water\nControls how far aquatic agents can see in water\nAffects their ability to detect resources and threats\nTypical range: 60.0-120.0, extremes: 30.0 (limited) to 200.0 (excellent)',
        'vision_range_amphibious': 'Vision range for amphibious agents\nControls how far amphibious agents can see\nAffects their ability to detect resources and threats\nTypical range: 80.0-140.0, extremes: 40.0 (limited) to 250.0 (excellent)',
        'vision_range_terrestrial': 'Vision range for terrestrial agents on land\nControls how far land agents can see on land\nAffects their ability to detect resources and threats\nTypical range: 100.0-160.0, extremes: 50.0 (limited) to 300.0 (excellent)',
        'RANDOMIZE_DIET_TYPE': 'Randomly assign initial diet type\nCreates dietary diversity in\nstarting population',
        'RANDOMIZE_HABITAT_PREF': 'Randomly assign initial habitat preference\nCreates habitat diversity in\nstarting population',
        'INITIAL_SAME_SPECIES_PERCENTAGE': 'Percentage of initial population from same species\nControls initial genetic diversity\nin the founding population\nTypical range: 0.1-1.0, extremes: 0.01 (diverse) to 1.0 (identical)',
        'SPECIES_GENETIC_SIMILARITY_THRESHOLD': 'Threshold for same species classification\nDetermines how genetically similar\nagents must be to be same species\nTypical range: 0.5-0.95, extremes: 0.1 (inclusive) to 0.999 (exclusive)',
        'SPECIES_DRIFT_RATE': 'Rate at which genetic differences accumulate\nControls how quickly populations diverge\ninto separate species\nTypical range: 0.1-0.8, extremes: 0.01 (slow) to 0.99 (fast)',
        'HYBRID_FERTILITY_RATE': 'Fertility rate for cross-species offspring\nDetermines reproductive success\nof inter-species matings\nTypical range: 0.01-0.5, extremes: 0.001 (sterile) to 1.0 (normal)',
        'MAX_SIMULTANEOUS_OFFSPRING': 'Maximum number of offspring per mating\nControls litter size\naffecting reproductive strategy\nTypical range: 1-5, extremes: 1 (single) to 20 (large litter)',
        'NUMBER_OF_INITIAL_SPECIES': 'Number of different species in initial population\nCreates initial biodiversity\nfor evolutionary dynamics\nTypical range: 2-10, extremes: 1 (monoculture) to 50 (diverse)',
        'FPS': 'Frames per second for the simulation\nControls simulation speed\nand visual smoothness\nTypical range: 30-120, extremes: 10 (slow) to 240 (smooth)',
        'TRAIT_RANGES': 'Ranges for clamping phenotype values\nSets boundaries for trait expression\npreventing extreme values',
        'TRAIT_DEFAULTS': 'Default values for traits in initial population\nSets starting values for\nheritable characteristics',

        # Advanced Features
        'ADVANCED_SIZE_EFFECTS_ENABLED': 'Enable size-based trade-offs\nCreates realistic scaling relationships\nbetween body size and performance',
        'SIZE_ATTACK_SCALING': 'Larger agents have stronger attacks\nAttack power scales with body size\nfollowing realistic allometric relationships\nTypical range: 1.0-2.5, extremes: 0.5 (weak scaling) to 5.0 (strong scaling)',
        'SIZE_SPEED_PENALTY': 'Larger agents move slower\nSpeed decreases with size\nreflecting biomechanical constraints\nTypical range: 0.1-0.5, extremes: 0.01 (minimal) to 1.0 (severe)',
        'SIZE_TURN_PENALTY': 'Larger agents turn slower\nManeuverability decreases with size\naffecting tactical abilities\nTypical range: 0.1-0.6, extremes: 0.01 (minimal) to 1.0 (severe)',
        'SIZE_METABOLIC_SCALING': 'Superlinear metabolic cost exponent\nEnergy costs scale allometrically\nwith body size\nTypical range: 1.0-1.5, extremes: 0.5 (sublinear) to 3.0 (superlinear)',
        'SIZE_PERCEPTION_BONUS': 'Larger agents have better perception\nVision range increases with size\nfor better environmental awareness\nTypical range: 0.05-0.3, extremes: 0.01 (minimal) to 1.0 (large bonus)',
        'SUPERLINEAR_ENERGY_SCALING': 'Use superlinear scaling for large agents\nEnergy costs increase faster than linearly\nwith body size',
        'ENERGY_SIZE_EXPONENT': 'Metabolic cost scales as size^exponent\nControls allometric scaling relationship\nbetween size and metabolism\nTypical range: 1.0-2.0, extremes: 0.5 (sublinear) to 5.0 (highly superlinear)',
        'EFFORT_SIZE_INTERACTION': 'How much effort amplifies size cost\nLarger agents pay greater energy penalties\nfor high-effort activities\nTypical range: 0.1-1.0, extremes: 0.01 (minimal) to 5.0 (strong)',
        'AGE_EFFECTS_ENABLED': 'Enable age-based performance changes\nCreates senescence and age-related\ndeclines in performance',
        'AGE_PRIME_START': 'Age ratio when prime years begin\nDetermines when agents reach peak\nperformance levels\nTypical range: 0.1-0.4, extremes: 0.01 (early) to 0.8 (late)',
        'AGE_PRIME_END': 'Age ratio when prime years end\nDetermines when performance begins to decline\nwith age\nTypical range: 0.4-0.8, extremes: 0.2 (early decline) to 0.99 (late decline)',
        'AGE_SPEED_DECLINE': 'Max speed reduction in old age\nOlder agents become slower\nreflecting senescence\nTypical range: 0.1-0.7, extremes: 0.01 (minimal) to 0.99 (severe)',
        'AGE_STAMINA_DECLINE': 'Max stamina reduction in old age\nOlder agents tire more easily\naffecting endurance\nTypical range: 0.1-0.8, extremes: 0.01 (minimal) to 0.99 (severe)',
        'AGE_EXPERIENCE_BONUS': 'Combat bonus from experience\nCompensates for age decline\nwith accumulated skill\nTypical range: 0.05-0.5, extremes: 0.01 (minimal) to 2.0 (strong)',
        'AGE_REPRODUCTION_CURVE': 'Reproduction effectiveness varies with age\nYoung and old agents have reduced\nreproductive success',
        'INTERNAL_STATE_MODULATION_ENABLED': 'Enable soft internal state effects\nAllows internal conditions to\nmodulate behavior subtly',
        'LOW_ENERGY_ATTACK_PENALTY': 'Attack effectiveness when energy is low\nWeak agents fight poorly\naffecting survival during scarcity\nTypical range: 0.1-0.8, extremes: 0.01 (minimal) to 0.99 (severe)',
        'LOW_HYDRATION_SPEED_PENALTY': 'Speed penalty when dehydrated\nDehydrated agents move slowly\nforcing water-seeking behavior\nTypical range: 0.1-0.7, extremes: 0.01 (minimal) to 0.99 (severe)',
        'HIGH_STRESS_EFFORT_BOOST': 'Stress can boost short-term effort\nAcute stress temporarily enhances\nperformance at cost of homeostasis\nTypical range: 0.05-0.5, extremes: 0.01 (minimal) to 2.0 (strong)',
        'EXHAUSTION_THRESHOLD': 'Energy level below which penalties apply\nWhen energy is low, agents suffer\nperformance penalties\nTypical range: 0.1-0.5, extremes: 0.01 (early) to 0.9 (late)',
        'ACTION_COSTS_ENABLED': 'Enable differentiated action costs\nDifferent activities have different\nenergy costs',
        'COST_HIGH_SPEED_MULTIPLIER': 'Extra cost for max speed movement\nMoving at maximum speed is\nespecially energy-intensive\nTypical range: 1.2-3.0, extremes: 1.0 (no extra cost) to 10.0 (very costly)',
        'COST_SHARP_TURN_MULTIPLIER': 'Extra cost for sharp turns\nRapid direction changes\nrequire more energy\nTypical range: 1.1-2.5, extremes: 1.0 (no extra cost) to 8.0 (very costly)',
        'COST_PURSUIT_MULTIPLIER': 'Extra cost for sustained pursuit\nChasing targets is more expensive\nthan other movements\nTypical range: 1.1-2.0, extremes: 1.0 (no extra cost) to 5.0 (very costly)',
        'COST_ATTACK_BASE': 'Base energy cost per attack tick\nContinuous energy drain during combat\naffecting engagement duration\nTypical range: 1-10, extremes: 0.1 (cheap) to 50 (expensive)',
        'COST_MATING_BASE': 'Energy cost for mating attempt\nReproductive investment\naffects mating strategy\nTypical range: 2-20, extremes: 0.5 (cheap) to 100 (expensive)',
        'MORPHOLOGY_TRAITS_ENABLED': 'Enable agility and armor traits\nAdds morphological trade-offs\nbetween mobility and protection',
        'AGILITY_SPEED_BONUS': 'High agility = faster turning/acceleration\nAgile agents maneuver better\nat cost of other attributes\nTypical range: 0.1-1.0, extremes: 0.01 (minimal) to 5.0 (strong)',
        'AGILITY_STAMINA_COST': 'High agility = higher base metabolism\nAgile agents burn more energy\nat rest\nTypical range: 0.05-0.5, extremes: 0.01 (minimal) to 2.0 (high)',
        'ARMOR_DAMAGE_REDUCTION': 'High armor = reduced incoming damage\nProtected agents survive better\nat cost of mobility\nTypical range: 0.1-0.7, extremes: 0.01 (minimal) to 0.99 (near immunity)',
        'ARMOR_SPEED_PENALTY': 'High armor = slower movement\nHeavy armor impedes locomotion\ncreating defense/mobility trade-off\nTypical range: 0.1-0.6, extremes: 0.01 (minimal) to 0.9 (severe)',
        'ARMOR_ENERGY_COST': 'High armor = higher maintenance cost\nProtected agents burn more energy\nto maintain defenses\nTypical range: 0.05-0.3, extremes: 0.01 (minimal) to 1.0 (high)',
        'SENSORY_NOISE_ENABLED': 'Enable sensory noise\nIntroduces uncertainty in perception\nmaking agents less reliable',
        'SENSOR_DROPOUT_RATE': 'Probability of missing a sector signal\nSometimes agents fail to detect\nobjects in their environment\nTypical range: 0.01-0.2, extremes: 0.001 (rare) to 0.8 (frequent)',
        'INTERNAL_STATE_NOISE': 'Noise on internal state perception\nAgents have imperfect awareness\nof their own condition\nTypical range: 0.01-0.1, extremes: 0.001 (precise) to 0.5 (noisy)',
        'PERCEPTION_LAG': 'Delay in perception (0 = disabled)\nCreates reaction time delays\naffecting response to stimuli\nTypical range: 0.0-0.5, extremes: 0.0 (instant) to 2.0 (very delayed)',
        'CONTEXT_SIGNALS_ENABLED': 'Enable time-since signals as inputs\nAgents remember how long since\nlast food, damage, or mating',
        'TIME_SINCE_FOOD_DECAY': 'Seconds for food signal to decay\nMemory of food availability fades\nover time\nTypical range: 5-30, extremes: 1 (quick) to 100 (persistent)',
        'TIME_SINCE_DAMAGE_DECAY': 'Seconds for damage signal to decay\nMemory of danger fades\nover time\nTypical range: 5-40, extremes: 1 (quick) to 100 (persistent)',
        'TIME_SINCE_MATING_DECAY': 'Seconds for mating signal to decay\nReproductive urges fade\nover time\nTypical range: 10-60, extremes: 1 (quick) to 200 (persistent)',
        'SOCIAL_PRESSURE_ENABLED': 'Enable crowding/social stress\nAgents become stressed when\nsurrounded by others',
        'CROWD_STRESS_RADIUS': 'Radius for counting nearby agents\nDetermines how close agents need\nto be to cause stress\nTypical range: 20-100, extremes: 5 (very close) to 300 (distant)',
        'CROWD_STRESS_THRESHOLD': 'Number of agents before stress increases\nMore than this many neighbors\ncauses stress accumulation\nTypical range: 2-10, extremes: 1 (sensitive) to 50 (tolerant)',
        'CROWD_STRESS_RATE': 'Stress increase per extra agent\nEach agent beyond the threshold\nadds to stress level\nTypical range: 0.05-0.5, extremes: 0.01 (minimal) to 2.0 (strong)',
        'DOMINANCE_STRESS_FACTOR': 'Stress from larger/aggressive neighbors\nBeing near dominant agents\nincreases stress levels\nTypical range: 0.1-1.0, extremes: 0.01 (minimal) to 5.0 (strong)',
    }

    return explanations.get(key, f"Parameter: {key}\nNo description available.")
    
def _draw_tooltip(screen, x, y, text, font):
    """Draw a tooltip at the specified position."""
    # Split text into lines
    lines = text.split('\n')
    
    # Calculate tooltip dimensions
    padding = 10
    line_height = 20
    max_line_width = max(font.size(line)[0] for line in lines)
    
    tooltip_width = max_line_width + 2 * padding
    tooltip_height = len(lines) * line_height + 2 * padding
    
    # Adjust position to stay within screen bounds
    screen_width, screen_height = screen.get_size()
    if x + tooltip_width > screen_width:
        x = screen_width - tooltip_width
    if y + tooltip_height > screen_height:
        y = y - tooltip_height - 5  # Position above if needed
    
    # Draw tooltip background
    tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    tooltip_surface.fill((30, 30, 40, 220))  # Slightly transparent dark panel
    pygame.draw.rect(tooltip_surface, (100, 140, 200), (0, 0, tooltip_width, tooltip_height), 2, border_radius=5)
    
    # Draw text lines
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (220, 220, 225))
        tooltip_surface.blit(text_surface, (padding, padding + i * line_height))
    
    screen.blit(tooltip_surface, (x, y))

