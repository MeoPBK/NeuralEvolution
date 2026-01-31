"""
Multiagent Mode Menu for selecting multiple configurations and setting environmental parameters.
"""
import pygame
import os
from src.managers.config_manager import ConfigManager


class MultiagentMenu:
    """UI component for the multiagent mode menu."""

    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.config_manager = ConfigManager()

        # UI elements
        self.scroll_offset = 0
        self.selected_configs = set()
        self.hovered_item = None

        # Environmental settings state
        self.env_settings = {}
        self.active_input = None
        self.input_texts = {}
        self.setting_rects = {}
        self.plus_rects = {}
        self.minus_rects = {}
        self.input_rects = {}
        self.category_rects = {}

        # Initialize environmental settings categories dynamically
        self._initialize_env_categories()

        # Expanded state for categories
        self.expanded_categories = {cat: True for cat in self.env_categories.keys()}

        # Species overview state
        self.species_overviews = {}
        self.overview_expanded = {}
        self.custom_names = {}  # Maps config_name to custom name
        self.naming_mode = None  # Stores which config is currently being renamed
        self.rename_input = ""  # Stores the current rename input

        # Scrolling state
        self.scroll_y = 0
        self.max_scroll = 1000  # Placeholder, will be calculated dynamically
        self.dragging_scrollbar = False
        self.scrollbar_drag_start_y = 0
        self.scroll_start_y = 0

        # Colors
        self.colors = {
            'bg': (20, 25, 40),
            'panel': (30, 35, 55),
            'header': (40, 45, 65),
            'card': (42, 46, 58),
            'text': (210, 215, 225),
            'muted': (130, 135, 150),
            'accent': (90, 140, 220),
            'success': (80, 180, 100),
            'warning': (220, 160, 60),
            'border': (55, 60, 75),
            'input_bg': (50, 55, 68),
            'input_active': (60, 90, 140),
            'button': (70, 120, 190),
            'highlight': (100, 150, 255),
            'selected': (80, 180, 100),
            'hover': (60, 70, 90),
            'stat_good': (100, 200, 100),  # Green for good stats
            'stat_bad': (200, 100, 100),   # Red for bad stats
        }

        # Button rectangles
        self.buttons = {}
        self.config_rects = {}

    def _calculate_species_overview(self, config_name):
        """Calculate average stats for a species based on its configuration."""
        # Load the configuration
        config = self.config_manager.load_config(config_name)

        # Create a sample agent to extract stats
        from src.utils.vector import Vector2
        from src.entities.agent import Agent

        # Create a minimal agent to extract stats from the config
        # Since we don't have the full genome structure here, we'll estimate based on config values
        sample_stats = {
            'speed': config.get('speed', config.get('SPEED', 3.0)),
            'size': config.get('size', config.get('SIZE', 6.0)),
            'vision_range': config.get('vision_range', config.get('VISION_RANGE', 100.0)),
            'energy_efficiency': config.get('energy_efficiency', config.get('ENERGY_EFFICIENCY', 1.0)),
            'aggression': config.get('aggression', config.get('AGGRESSION', 1.0)),
            'max_age': config.get('max_age', config.get('MAX_AGE', 70.0)),
            'virus_resistance': config.get('virus_resistance', config.get('VIRUS_RESISTANCE', 0.5)),
            'agility': config.get('agility', config.get('AGILITY', 0.5)),
            'armor': config.get('armor', config.get('ARMOR', 0.5)),
            'diet_type': config.get('diet_type', config.get('DIET_TYPE', 'omnivore')),
            'habitat_preference': config.get('habitat_preference', config.get('HABITAT_PREFERENCE', 'amphibious')),
        }

        # Estimate neural structure based on config
        neural_structure = {
            'nn_type': config.get('NN_TYPE', config.get('NEURAL_NETWORK_TYPE', 'FNN')),
            'hidden_size': config.get('NN_HIDDEN_SIZE', config.get('HIDDEN_LAYER_SIZE', 8)),
            'weight_count': config.get('NN_TYPE', 'FNN') == 'FNN' and 254 or 318,  # Approximate weights
            'recurrent': config.get('NN_TYPE', 'FNN') == 'RNN'
        }

        return {
            'stats': sample_stats,
            'neural_structure': neural_structure,
            'config_name': config_name
        }

    def _initialize_env_categories(self):
        """Initialize environmental settings categories dynamically from settings.py"""
        from settings import SETTINGS

        # Get ALL settings from SETTINGS dictionary (except private ones)
        environmental_keys = set()
        for key in SETTINGS.keys():
            # Only exclude private/internal settings that start with underscore
            if not key.startswith('_'):
                environmental_keys.add(key)

        # Define categories based on setting prefixes/types
        categories_mapping = {
            'World': ['WORLD_', 'GRID_', 'HUD_', 'WINDOW_'],
            'Population': ['INITIAL_AGENTS', 'MAX_FOOD', 'FOOD_SPAWN_RATE', 'INITIAL_FOOD'],
            'Food Clusters': ['NUM_FOOD_CLUSTERS', 'FOOD_CLUSTER_', 'SEASON_'],
            'Water': ['NUM_WATER_', 'WATER_', 'RIVER_'],
            'Obstacles': ['OBSTACLE', 'BORDER_', 'NUM_INTERNAL_'],
            'Temperature': ['TEMPERATURE_'],
            'Regions': ['REGIONAL_', 'NUM_REGIONS_', 'REGION_'],
            'Epidemic': ['EPIDEMIC_'],
            'Disease': ['DISEASE_', 'NUM_DISEASE_'],
            'Genetics': ['MUTATION_', 'CROSSOVER_', 'LARGE_MUTATION_', 'DOMINANCE_', 'SOMATIC_', 'POINT_'],
            'Neural Network': ['NN_', 'N_STEP_'],
            'Sensing': ['SECTOR_', 'VISION_'],
            'Internal State': ['STRESS_', 'INTERNAL_STATE_'],
            'Effort System': ['EFFORT_'],
            'Energy': ['BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_', 'FOOD_ENERGY', 'ENERGY_'],
            'Hydration': ['BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_', 'DRINK_'],
            'Combat': ['ATTACK_', 'KILL_'],
            'Agents': ['MAX_SPEED_', 'EATING_', 'MATING_', 'WANDER_', 'STEER_'],
            'Aging': ['MATURITY_', 'MAX_AGE', 'RANDOM_AGE_'],
            'Reproduction': ['REPRODUCTION_', 'MATE_', 'MAX_SIMULTANEOUS_'],
            'Species': ['INITIAL_SAME_', 'SPECIES_', 'HYBRID_', 'NUMBER_OF_'],
            'Rendering': ['FPS', 'SIMULATION_SPEED', 'PARTICLE_', 'BACKGROUND_'],
            'Physics': ['WORLD_BOUNDARY_', 'GRAVITY_', 'WIND_', 'SEASONAL_', 'WEATHER_', 'TERRAIN_'],
            'Advanced Features': ['ADVANCED_SIZE_', 'SIZE_', 'SUPERLINEAR_', 'AGE_', 'ACTION_',
                                'MORPHOLOGY_', 'AGILITY_', 'ARMOR_', 'SENSORY_', 'CONTEXT_',
                                'SOCIAL_', 'CROWD_', 'DOMINANCE_', 'DIET_', 'HABITAT_']
        }

        # Create a mapping of settings to their categories
        settings_to_category = {}
        for category, prefixes in categories_mapping.items():
            for key in environmental_keys:
                if any(key.startswith(prefix) or key in prefixes for prefix in prefixes if not prefix.isupper()) or key in prefixes:
                    settings_to_category[key] = category

        # Group settings by category
        env_categories = {}
        for setting, category in settings_to_category.items():
            if category not in env_categories:
                env_categories[category] = []
            if setting not in env_categories[category]:  # Avoid duplicates
                env_categories[category].append(setting)

        # Sort settings within each category alphabetically
        for category in env_categories:
            env_categories[category].sort()

        # Add any remaining settings that weren't categorized
        all_categorized_settings = set()
        for settings_list in env_categories.values():
            all_categorized_settings.update(settings_list)

        uncategorized = [key for key in environmental_keys
                        if key not in all_categorized_settings and
                        not key.startswith('_')]  # Exclude private settings

        if uncategorized:
            env_categories['Other'] = sorted(uncategorized)

        self.env_categories = env_categories

    def refresh_categories(self):
        """Refresh the environmental settings categories to include any new settings"""
        self._initialize_env_categories()
        # Reset expanded state for categories
        self.expanded_categories = {cat: True for cat in self.env_categories.keys()}

    def draw(self):
        """Draw the multiagent menu."""
        # Fill background
        self.screen.fill(self.colors['bg'])

        # Calculate max scroll based on content
        # Content height includes all UI elements stacked vertically
        content_height = 470 + 1400 + 500 + 100  # header + species panel + environmental settings + padding
        screen_height = self.screen.get_height()
        self.max_scroll = max(0, content_height - screen_height + 200)  # Extra padding

        # Apply scrolling transformation
        scroll_offset = self.scroll_y

        # Draw header with scroll offset
        header_font = self.font_manager.get_font('large')
        title = header_font.render("Multiagent Mode", True, self.colors['highlight'])
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 30 - scroll_offset))

        # Draw instructions with scroll offset
        small_font = self.font_manager.get_font('small')
        instr1 = small_font.render("Select multiple configurations to run together", True, self.colors['text'])
        instr2 = small_font.render("Use checkboxes to select configurations", True, self.colors['text'])
        self.screen.blit(instr1, (self.screen.get_width() // 2 - instr1.get_width() // 2, 80 - scroll_offset))
        self.screen.blit(instr2, (self.screen.get_width() // 2 - instr2.get_width() // 2, 110 - scroll_offset))

        # Draw configuration selection area with scroll offset
        self._draw_config_selection(scroll_offset)

        # Draw species overview area with scroll offset
        self._draw_species_overview(scroll_offset)

        # Draw environmental settings area with scroll offset
        self._draw_environmental_settings(scroll_offset)

        # Draw control buttons with scroll offset
        self._draw_control_buttons(scroll_offset)

        # Draw navigation hint (fixed at bottom)
        nav_hint = small_font.render("Press ESC to return to main menu", True, (180, 180, 200))
        self.screen.blit(nav_hint, (20, self.screen.get_height() - 30))

        # Draw scrollbar
        self._draw_scrollbar()

    def _draw_config_selection(self, scroll_offset=0):
        """Draw the configuration selection panel."""
        panel_x, panel_y = 50, 150
        panel_width, panel_height = self.screen.get_width() - 100, 300  # Increased height to allow more space for configs

        # Adjust position based on scroll offset
        panel_y -= scroll_offset

        # Draw panel background
        pygame.draw.rect(self.screen, self.colors['panel'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['header'], (panel_x, panel_y, panel_width, 40))  # Header

        # Panel title
        med_font = self.font_manager.get_font('medium')
        title = med_font.render("Available Configurations", True, self.colors['highlight'])
        self.screen.blit(title, (panel_x + 20, panel_y + 10))

        # Draw scrollbar area
        scrollbar_area = pygame.Rect(panel_x + panel_width - 20, panel_y + 40, 15, panel_height - 40)

        # Get available configs from the correct directory
        configs = self.config_manager.get_available_configs()

        # Draw config list with scrolling
        item_height = 30
        items_per_page = (panel_height - 40) // item_height
        start_idx = max(0, min(self.scroll_offset, len(configs) - items_per_page))
        end_idx = min(start_idx + items_per_page, len(configs))

        y_offset = panel_y + 45
        self.config_rects = {}  # Store rectangles for click detection

        for i, config_name in enumerate(configs[start_idx:end_idx]):
            idx = start_idx + i
            item_y = y_offset + i * item_height

            # Check if mouse is hovering over this item
            item_rect = pygame.Rect(panel_x + 10, item_y, panel_width - 30, item_height)
            # Adjust mouse position for scroll
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = item_rect.collidepoint(mouse_pos)
            self.config_rects[config_name] = (item_rect, idx)

            # Draw item background
            bg_color = self.colors['hover'] if is_hovered else self.colors['panel']
            pygame.draw.rect(self.screen, bg_color, (panel_x + 10, item_y, panel_width - 30, item_height))

            # Draw checkbox
            checkbox_rect = pygame.Rect(panel_x + 20, item_y + 8, 16, 16)
            pygame.draw.rect(self.screen, self.colors['text'], checkbox_rect, 2)
            if config_name in self.selected_configs:
                # Draw checkmark
                pygame.draw.line(self.screen, self.colors['selected'],
                               (checkbox_rect.x + 4, checkbox_rect.y + 8),
                               (checkbox_rect.x + 7, checkbox_rect.y + 12), 2)
                pygame.draw.line(self.screen, self.colors['selected'],
                               (checkbox_rect.x + 7, checkbox_rect.y + 12),
                               (checkbox_rect.x + 12, checkbox_rect.y + 6), 2)

            # Draw config name
            name = med_font.render(config_name, True,
                                 self.colors['selected'] if config_name in self.selected_configs else self.colors['text'])
            self.screen.blit(name, (panel_x + 45, item_y + 4))

        # Draw scrollbar if needed
        if len(configs) > items_per_page:
            scrollbar_height = max(20, (items_per_page / len(configs)) * (panel_height - 40))
            scrollbar_pos = (self.scroll_offset / max(1, len(configs) - items_per_page)) * ((panel_height - 40) - scrollbar_height)
            scrollbar_rect = pygame.Rect(panel_x + panel_width - 18, panel_y + 40 + scrollbar_pos, 11, scrollbar_height)
            pygame.draw.rect(self.screen, self.colors['highlight'], scrollbar_rect)

    def _draw_species_overview(self, scroll_offset=0):
        """Draw the species overview panel showing stats and neural structures."""
        # Position the species overview panel between config selection and environmental settings
        panel_x, panel_y = 50, 470
        panel_width, panel_height = self.screen.get_width() - 100, 1400  # Increased height to accommodate larger schematic

        # Adjust position based on scroll offset
        panel_y -= scroll_offset

        # Draw panel background
        pygame.draw.rect(self.screen, self.colors['panel'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['header'], (panel_x, panel_y, panel_width, 40))  # Header

        # Panel title
        med_font = self.font_manager.get_font('medium')
        title = med_font.render("Selected Species Overview", True, self.colors['highlight'])
        self.screen.blit(title, (panel_x + 20, panel_y + 10))

        # Initialize fonts early so they're available in all branches
        small_font = self.font_manager.get_font('small')
        med_font = self.font_manager.get_font('medium')

        # Draw species overviews for selected configurations
        if self.selected_configs:
            y_offset = panel_y + 50

            # Calculate how many configs to display per row based on screen width
            configs_per_row = min(len(self.selected_configs), 1)  # Only 1 per row to maximize vertical space
            config_width = (panel_width - 40) // configs_per_row if configs_per_row > 0 else panel_width - 40

            row_configs = list(self.selected_configs)[:configs_per_row]
            for i, config_name in enumerate(row_configs):
                config_x = panel_x + 20 + i * config_width

                # Calculate species overview if not already cached
                if config_name not in self.species_overviews:
                    self.species_overviews[config_name] = self._calculate_species_overview(config_name)

                overview = self.species_overviews[config_name]

                # Get custom name if available, otherwise use config name
                custom_name = self.custom_names.get(config_name, config_name)

                # Draw config header with custom name
                config_header_rect = pygame.Rect(config_x, y_offset, config_width - 10, 40)
                pygame.draw.rect(self.screen, self.colors['header'], config_header_rect, border_radius=3)

                # Truncate custom name if too long
                display_name = custom_name[:30] + "..." if len(custom_name) > 30 else custom_name
                config_title = med_font.render(display_name, True, self.colors['accent'])
                self.screen.blit(config_title, (config_x + 5, y_offset + 10))

                # If this config is in renaming mode, draw input box
                if self.naming_mode == config_name:
                    # Draw input box for renaming
                    input_rect = pygame.Rect(config_x + 5, y_offset + 45, config_width - 20, 30)
                    pygame.draw.rect(self.screen, self.colors['input_active'], input_rect, border_radius=3)
                    pygame.draw.rect(self.screen, self.colors['accent'], input_rect, 1, border_radius=3)

                    # Render the current input text
                    input_text = med_font.render(self.rename_input, True, self.colors['text'])
                    self.screen.blit(input_text, (config_x + 8, y_offset + 48))

                    # Draw instructions
                    inst_text = small_font.render("Press ENTER to confirm, ESC to cancel", True, self.colors['muted'])
                    self.screen.blit(inst_text, (config_x + 5, y_offset + 80))
                else:
                    # Draw rename button
                    rename_btn_rect = pygame.Rect(config_x + config_width - 80, y_offset + 10, 70, 25)
                    pygame.draw.rect(self.screen, self.colors['button'], rename_btn_rect, border_radius=3)
                    rename_text = small_font.render("Rename", True, (255, 255, 255))
                    self.screen.blit(rename_text, (config_x + config_width - 75, y_offset + 14))

                    # Store rename button rect for click detection
                    if not hasattr(self, 'rename_buttons'):
                        self.rename_buttons = {}
                    self.rename_buttons[config_name] = rename_btn_rect

                    # Draw a cleaner stats panel with better formatting
                    stats = overview['stats']
                    stat_y = y_offset + 50

                    # Draw stat bars for better visualization
                    stat_bar_width = config_width - 20
                    stat_bar_height = 12
                    stat_bar_spacing = 25

                    # Define stats to display with their ranges
                    stats_to_display = [
                        ('Speed', stats['speed'], 1.0, 6.0),
                        ('Size', stats['size'], 3.0, 12.0),
                        ('Vision Range', stats['vision_range'], 40.0, 200.0),
                        ('Aggression', stats['aggression'], 0.3, 2.0),
                        ('Energy Efficiency', stats['energy_efficiency'], 0.5, 2.0),
                        ('Max Age', stats['max_age'], 10.0, 150.0),
                        ('Virus Resistance', stats['virus_resistance'], 0.0, 1.0),
                        ('Agility', stats['agility'], 0.0, 1.0),
                        ('Armor', stats['armor'], 0.0, 1.0),
                        ('Diet Type', str(stats['diet_type']), 0.0, 2.0),
                        ('Habitat Preference', str(stats['habitat_preference']), 0.0, 2.0),
                    ]

                    for idx, (stat_name, stat_value, min_val, max_val) in enumerate(stats_to_display):
                        stat_norm = (float(stat_value) - min_val) / (max_val - min_val) if max_val != min_val else 0  # Normalize to 0-1 range
                        stat_bar_x = config_x + 5
                        stat_bar_y = stat_y + idx * stat_bar_spacing

                        # Draw background bar
                        pygame.draw.rect(self.screen, self.colors['border'], (stat_bar_x, stat_bar_y, stat_bar_width, stat_bar_height))
                        # Draw filled portion with color gradient
                        fill_color = (int(255 * stat_norm), int(200 - 100 * stat_norm), int(100 - 100 * stat_norm))
                        pygame.draw.rect(self.screen, fill_color, (stat_bar_x, stat_bar_y, stat_bar_width * stat_norm, stat_bar_height))

                        # Draw stat label
                        stat_label = small_font.render(f"{stat_name}: {stat_value}", True, self.colors['text'])
                        self.screen.blit(stat_label, (stat_bar_x, stat_bar_y - 15))

                    # Draw neural structure visualization in a cleaner way
                    neural_info = overview['neural_structure']
                    neural_y = stat_y + len(stats_to_display) * stat_bar_spacing + 20
                    neural_title = med_font.render("Neural Network Architecture:", True, self.colors['text'])
                    self.screen.blit(neural_title, (config_x + 5, neural_y))

                    # Draw simple neural network diagram
                    nn_y = neural_y + 25
                    nn_width = config_width - 10
                    nn_height = 500  # Doubled height for larger schematic

                    # Define layer positions
                    input_x = config_x + 30
                    hidden_x = config_x + nn_width // 2
                    output_x = config_x + nn_width - 30

                    # Draw input layer (increased to 8 nodes)
                    input_nodes_y = nn_y + 20
                    for j in range(8):
                        pygame.draw.circle(self.screen, self.colors['accent'],
                                        (input_x, input_nodes_y + j * 55), 12)  # Increased size and spacing significantly
                        # Label input nodes
                        label = small_font.render(f"I{j+1}", True, self.colors['text'])
                        self.screen.blit(label, (input_x - 15, input_nodes_y + j * 55 - 5))

                    # Draw hidden layer (based on hidden size, up to 12 for visualization)
                    hidden_nodes_y = nn_y + 15
                    hidden_count = min(neural_info['hidden_size'], 12)
                    for j in range(hidden_count):
                        pygame.draw.circle(self.screen, self.colors['success'],
                                        (hidden_x, hidden_nodes_y + j * (440 // max(1, hidden_count-1))), 12)  # Increased size
                        # Label hidden nodes
                        label = small_font.render(f"H{j+1}", True, self.colors['text'])
                        self.screen.blit(label, (hidden_x - 15, hidden_nodes_y + j * (440 // max(1, hidden_count-1)) - 5))

                    # Draw output layer (increased to 12 nodes)
                    output_nodes_y = nn_y + 25
                    for j in range(12):
                        pygame.draw.circle(self.screen, self.colors['warning'],
                                        (output_x, output_nodes_y + j * 35), 12)  # Increased size and spacing
                        # Label output nodes
                        label = small_font.render(f"O{j+1}", True, self.colors['text'])
                        self.screen.blit(label, (output_x - 15, output_nodes_y + j * 35 - 5))

                    # Draw connections between layers (simplified)
                    # Input to Hidden
                    for i in range(8):  # input nodes
                        for h in range(hidden_count):  # hidden nodes
                            start_pos = (input_x, input_nodes_y + i * 55)
                            end_pos = (hidden_x, hidden_nodes_y + h * (440 // max(1, hidden_count-1)))
                            pygame.draw.line(self.screen, (100, 100, 120), start_pos, end_pos, 1)

                    # Hidden to Output
                    for h in range(hidden_count):  # hidden nodes
                        for o in range(12):  # output nodes
                            start_pos = (hidden_x, hidden_nodes_y + h * (440 // max(1, hidden_count-1)))
                            end_pos = (output_x, output_nodes_y + o * 35)
                            pygame.draw.line(self.screen, (100, 100, 120), start_pos, end_pos, 1)

                    # Draw network type info
                    nn_info_y = nn_y + nn_height + 15
                    nn_type_text = med_font.render(f"Network Type: {neural_info['nn_type']} | Hidden Units: {neural_info['hidden_size']}", True, self.colors['text'])
                    self.screen.blit(nn_type_text, (config_x + 5, nn_info_y))

                    # Draw additional info
                    additional_info_y = nn_info_y + 25

                    # Convert diet type to readable format
                    diet_value = stats['diet_type']
                    if isinstance(diet_value, (int, float)):
                        if diet_value < 0.7:
                            diet_display = "Carnivore"
                        elif diet_value > 1.3:
                            diet_display = "Herbivore"
                        else:
                            diet_display = "Omnivore"
                    else:
                        diet_display = str(diet_value)

                    # Convert habitat preference to readable format
                    habitat_value = stats['habitat_preference']
                    if isinstance(habitat_value, (int, float)):
                        if habitat_value < 0.7:
                            habitat_display = "Aquatic"
                        elif habitat_value > 1.3:
                            habitat_display = "Terrestrial"
                        else:
                            habitat_display = "Amphibious"
                    else:
                        habitat_display = str(habitat_value)

                    diet_text = small_font.render(f"Diet Type: {diet_display}", True, self.colors['text'])
                    habitat_text = small_font.render(f"Habitat Preference: {habitat_display}", True, self.colors['text'])

                    # Draw additional stats if available
                    additional_stats = [
                        f"Reproduction Urge: {stats.get('reproduction_urge', 'N/A')}",
                        f"Camouflage: {stats.get('camouflage', 'N/A')}",
                        f"Max Age: {stats.get('max_age', 'N/A')}",
                        f"Virus Resistance: {stats.get('virus_resistance', 'N/A')}",
                        f"Agility: {stats.get('agility', 'N/A')}",
                        f"Armor: {stats.get('armor', 'N/A')}",
                        f"Energy Efficiency: {stats.get('energy_efficiency', 'N/A')}",
                        f"Vision Range: {stats.get('vision_range', 'N/A')}",
                        f"Aggression: {stats.get('aggression', 'N/A')}",
                        f"Size: {stats.get('size', 'N/A')}",
                        f"Speed: {stats.get('speed', 'N/A')}",
                        f"Color (RGB): ({stats.get('color_red', 'N/A')}, {stats.get('color_green', 'N/A')}, {stats.get('color_blue', 'N/A')})"
                    ]

                    self.screen.blit(diet_text, (config_x + 5, additional_info_y))
                    self.screen.blit(habitat_text, (config_x + 5, additional_info_y + 20))

                    # Draw additional stats
                    for idx, stat_text in enumerate(additional_stats):
                        y_pos = additional_info_y + 40 + (idx * 20)
                        if y_pos < panel_y + panel_height - 20:  # Check if within panel bounds
                            stat_render = small_font.render(stat_text, True, self.colors['text'])
                            self.screen.blit(stat_render, (config_x + 5, y_pos))
        else:
            # If no configs selected, show a message
            no_configs_text = med_font.render("No configurations selected", True, self.colors['muted'])
            self.screen.blit(no_configs_text, (panel_x + 20, panel_y + 50))

    def _draw_environmental_settings(self, scroll_offset=0):
        """Draw the environmental settings panel with editable fields."""
        # Adjust position to account for species overview panel
        species_panel_height = 1400  # Updated to match the new height
        panel_x, panel_y = 50, 470
        panel_y -= scroll_offset  # Apply scroll offset
        panel_y += species_panel_height  # Start after species overview panel
        panel_width, panel_height = self.screen.get_width() - 100, 500  # Increased height to ensure visibility

        # Draw panel background
        pygame.draw.rect(self.screen, self.colors['panel'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['header'], (panel_x, panel_y, panel_width, 40))  # Header

        # Panel title
        med_font = self.font_manager.get_font('medium')
        title = med_font.render("Shared Environmental Settings", True, self.colors['highlight'])
        self.screen.blit(title, (panel_x + 20, panel_y + 10))

        # Initialize environmental settings with default values if not already set
        if not self.env_settings:
            from settings import SETTINGS

            # Load ALL environmental settings from SETTINGS dictionary
            # In the multiagent menu, we want all global settings that affect the simulation
            # The only settings we exclude are private/internal settings
            for key, value in SETTINGS.items():
                # Only skip private/internal settings that start with underscore
                if not key.startswith('_'):
                    self.env_settings[key] = value

            # Initialize input texts
            for key, value in self.env_settings.items():
                self.input_texts[key] = str(value)

        # Draw categories with expand/collapse functionality
        y_offset = panel_y + 50
        small_font = self.font_manager.get_font('small')
        value_font = pygame.font.SysFont('monospace', 12)

        # Clear rectangles
        self.setting_rects = {}
        self.plus_rects = {}
        self.minus_rects = {}
        self.input_rects = {}
        self.category_rects = {}

        for category, keys in self.env_categories.items():
            # Check if we have enough space to draw this category
            if y_offset >= panel_y + panel_height - 30:
                break  # Stop if we run out of space in the panel

            # Draw category header
            header_rect = pygame.Rect(panel_x + 10, y_offset, panel_width - 20, 30)
            pygame.draw.rect(self.screen, self.colors['header'], header_rect, border_radius=3)

            # Expand/collapse indicator
            indicator = "[-]" if self.expanded_categories[category] else "[+]"
            ind_text = pygame.font.SysFont('monospace', 14).render(indicator, True, self.colors['accent'])
            self.screen.blit(ind_text, (panel_x + 15, y_offset + 6))

            # Category name
            cat_text = med_font.render(category, True, self.colors['text'])
            self.screen.blit(cat_text, (panel_x + 45, y_offset + 5))

            self.category_rects[category] = header_rect

            y_offset += 35

            # Draw settings if expanded
            if self.expanded_categories[category]:
                for key in keys:
                    if key in self.env_settings:
                        # Check if we have enough space to draw this setting
                        if y_offset >= panel_y + panel_height - 30:
                            break  # Stop if we run out of space in the panel

                        value = self.env_settings[key]

                        # Draw setting row
                        setting_y = y_offset

                        # Format key name nicely
                        display_name = key.replace('_', ' ').title()
                        if len(display_name) > 25:
                            display_name = display_name[:22] + "..."

                        # Label
                        label = small_font.render(display_name, True, self.colors['muted'])
                        self.screen.blit(label, (panel_x + 20, setting_y + 5))

                        # Value controls on right side
                        controls_x = panel_x + panel_width - 150

                        if isinstance(value, bool):
                            # Boolean toggle
                            toggle_x = controls_x
                            toggle_rect = pygame.Rect(toggle_x, setting_y + 4, 40, 20)

                            if value:
                                pygame.draw.rect(self.screen, self.colors['success'], toggle_rect, border_radius=10)
                                # Knob on right
                                pygame.draw.circle(self.screen, (255, 255, 255), (toggle_x + 30, setting_y + 14), 8)
                            else:
                                pygame.draw.rect(self.screen, self.colors['panel'], toggle_rect, border_radius=10)
                                pygame.draw.rect(self.screen, self.colors['border'], toggle_rect, 1, border_radius=10)
                                # Knob on left
                                pygame.draw.circle(self.screen, self.colors['muted'], (toggle_x + 10, setting_y + 14), 8)

                            self.setting_rects[key] = toggle_rect
                        elif isinstance(value, (int, float)):
                            # Numeric controls with increment/decrement
                            # Minus button
                            minus_rect = pygame.Rect(controls_x, setting_y + 2, 24, 24)
                            pygame.draw.rect(self.screen, self.colors['panel'], minus_rect, border_radius=3)
                            pygame.draw.rect(self.screen, self.colors['border'], minus_rect, 1, border_radius=3)
                            minus_text = value_font.render("-", True, self.colors['warning'])
                            self.screen.blit(minus_text, (minus_rect.centerx - 3, minus_rect.centery - 7))
                            self.minus_rects[key] = minus_rect

                            # Input box
                            input_rect = pygame.Rect(controls_x + 28, setting_y + 2, 80, 24)
                            is_active = self.active_input == key
                            bg_color = self.colors['input_active'] if is_active else self.colors['input_bg']
                            pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=3)
                            border_color = self.colors['accent'] if is_active else self.colors['border']
                            pygame.draw.rect(self.screen, border_color, input_rect, 1, border_radius=3)

                            # Value text
                            val_str = self.input_texts.get(key, str(value))
                            if len(val_str) > 10:
                                val_str = val_str[:9] + ".."
                            val_text = value_font.render(val_str, True, self.colors['text'])
                            self.screen.blit(val_text, (input_rect.x + 5, input_rect.y + 5))
                            self.input_rects[key] = input_rect
                            self.setting_rects[key] = input_rect

                            # Plus button
                            plus_rect = pygame.Rect(controls_x + 112, setting_y + 2, 24, 24)
                            pygame.draw.rect(self.screen, self.colors['panel'], plus_rect, border_radius=3)
                            pygame.draw.rect(self.screen, self.colors['border'], plus_rect, 1, border_radius=3)
                            plus_text = value_font.render("+", True, self.colors['success'])
                            self.screen.blit(plus_text, (plus_rect.centerx - 4, plus_rect.centery - 7))
                            self.plus_rects[key] = plus_rect
                        else:
                            # String input (no increment/decrement buttons)
                            # Input box only
                            input_rect = pygame.Rect(controls_x, setting_y + 2, 136, 24)  # Full width
                            is_active = self.active_input == key
                            bg_color = self.colors['input_active'] if is_active else self.colors['input_bg']
                            pygame.draw.rect(self.screen, bg_color, input_rect, border_radius=3)
                            border_color = self.colors['accent'] if is_active else self.colors['border']
                            pygame.draw.rect(self.screen, border_color, input_rect, 1, border_radius=3)

                            # Value text
                            val_str = self.input_texts.get(key, str(value))
                            if len(val_str) > 18:
                                val_str = val_str[:17] + ".."
                            val_text = value_font.render(val_str, True, self.colors['text'])
                            self.screen.blit(val_text, (input_rect.x + 5, input_rect.y + 5))
                            self.input_rects[key] = input_rect
                            self.setting_rects[key] = input_rect

                        y_offset += 32

                y_offset += 10  # Extra spacing after expanded category

    def _draw_control_buttons(self, scroll_offset=0):
        """Draw control buttons at the bottom."""
        # Position buttons after the environmental settings panel
        species_panel_height = 1400  # Updated to match the new height
        environmental_panel_height = 500  # Height of environmental settings panel
        # Start Simulation button - positioned on the right
        button_width, button_height = 200, 50
        start_x = self.screen.get_width() - button_width - 20  # Positioned on the right side
        start_y = 470 + species_panel_height + environmental_panel_height + 50  # Position after both panels
        start_y -= scroll_offset  # Apply scroll offset

        start_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, self.colors['highlight'], start_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 220), start_rect, 2, border_radius=5)

        med_font = self.font_manager.get_font('medium')
        start_text = med_font.render("Start Simulation", True, (255, 255, 255))
        self.screen.blit(start_text, (start_x + button_width // 2 - start_text.get_width() // 2,
                                     start_y + button_height // 2 - start_text.get_height() // 2))

        self.buttons['start'] = start_rect

        # Clear Selection button - positioned on the left, close to other buttons
        clear_x = 20  # Positioned on the left side
        clear_y = start_y

        clear_rect = pygame.Rect(clear_x, clear_y, button_width, button_height)
        pygame.draw.rect(self.screen, (180, 60, 60), clear_rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 220, 220), clear_rect, 2, border_radius=5)

        clear_text = med_font.render("Clear All", True, (255, 255, 255))
        self.screen.blit(clear_text, (clear_x + button_width // 2 - clear_text.get_width() // 2,
                                     clear_y + button_height // 2 - clear_text.get_height() // 2))

        self.buttons['clear'] = clear_rect

        # Select All button - positioned in the middle, close to other buttons
        select_x = self.screen.get_width() // 2 - button_width // 2  # Centered
        select_y = start_y

        select_rect = pygame.Rect(select_x, select_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 150, 60), select_rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 220, 220), select_rect, 2, border_radius=5)

        select_text = med_font.render("Select All", True, (255, 255, 255))
        self.screen.blit(select_text, (select_x + button_width // 2 - select_text.get_width() // 2,
                                      select_y + button_height // 2 - select_text.get_height() // 2))

        self.buttons['select_all'] = select_rect

    def _draw_scrollbar(self):
        """Draw the scrollbar on the right side of the screen."""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Scrollbar dimensions
        scrollbar_width = 12
        scrollbar_height = max(30, int((screen_height / (screen_height + self.max_scroll)) * screen_height))
        scrollbar_x = screen_width - scrollbar_width - 5

        # Calculate scrollbar position based on current scroll
        if self.max_scroll > 0:
            scrollbar_y = int((self.scroll_y / self.max_scroll) * (screen_height - scrollbar_height))
        else:
            scrollbar_y = 0

        # Draw scrollbar track
        track_rect = pygame.Rect(scrollbar_x, 0, scrollbar_width, screen_height)
        pygame.draw.rect(self.screen, self.colors['panel'], track_rect)

        # Draw scrollbar thumb
        thumb_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.screen, self.colors['highlight'], thumb_rect)
        pygame.draw.rect(self.screen, self.colors['border'], thumb_rect, 1)

        return thumb_rect

    def handle_input(self, event):
        """Handle input events for the multiagent menu."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on scrollbar
            screen_width = self.screen.get_width()
            scrollbar_x = screen_width - 12 - 5
            scrollbar_track = pygame.Rect(scrollbar_x, 0, 12, self.screen.get_height())

            if scrollbar_track.collidepoint(mouse_pos):
                # Calculate new scroll position based on click
                screen_height = self.screen.get_height()
                scrollbar_height = max(30, int((screen_height / (screen_height + self.max_scroll)) * screen_height))

                # Calculate proportional position
                click_rel_pos = (mouse_pos[1] - scrollbar_height/2) / screen_height
                new_scroll = int(click_rel_pos * self.max_scroll)
                self.scroll_y = max(0, min(self.max_scroll, new_scroll))
                return None

            # Adjust mouse position for scroll when checking other elements
            adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_y)

            # Check if clicked on a config checkbox
            configs = self.config_manager.get_available_configs()
            # Only check the configs that are currently visible based on scroll position
            items_per_page = (300 - 40) // 30  # panel_height calculation
            start_idx = max(0, min(self.scroll_offset, len(configs) - items_per_page))
            end_idx = min(start_idx + items_per_page, len(configs))

            for i in range(start_idx, end_idx):
                config_name = configs[i]
                if config_name in self.config_rects:
                    rect, idx = self.config_rects[config_name]
                    if rect.collidepoint(adjusted_mouse_pos):
                        if config_name in self.selected_configs:
                            self.selected_configs.remove(config_name)
                        else:
                            self.selected_configs.add(config_name)
                        return None  # Continue in multiagent menu

            # Check if clicked on rename buttons
            if hasattr(self, 'rename_buttons'):
                for config_name, btn_rect in self.rename_buttons.items():
                    if btn_rect.collidepoint(adjusted_mouse_pos):
                        self.naming_mode = config_name
                        self.rename_input = self.custom_names.get(config_name, config_name)
                        return None

            # Check if clicked on environmental setting categories
            for category, rect in self.category_rects.items():
                if rect.collidepoint(adjusted_mouse_pos):
                    self.expanded_categories[category] = not self.expanded_categories.get(category, True)
                    return None

            # Check plus buttons for environmental settings
            for key, rect in self.plus_rects.items():
                if rect.collidepoint(adjusted_mouse_pos) and key in self.env_settings:
                    self._increment_setting(key)
                    return None

            # Check minus buttons for environmental settings
            for key, rect in self.minus_rects.items():
                if rect.collidepoint(adjusted_mouse_pos) and key in self.env_settings:
                    self._decrement_setting(key)
                    return None

            # Check environmental setting inputs
            for key, rect in self.setting_rects.items():
                if rect.collidepoint(adjusted_mouse_pos):
                    if key in self.env_settings:
                        value = self.env_settings[key]
                        if isinstance(value, bool):
                            # Toggle boolean value
                            self.env_settings[key] = not value
                            self.input_texts[key] = str(self.env_settings[key])
                        else:
                            # Activate text input
                            self.active_input = key
                    return None

            # Check if clicked on control buttons
            if 'start' in self.buttons and self.buttons['start'].collidepoint(adjusted_mouse_pos):
                if self.selected_configs:
                    # Start simulation with selected configurations
                    # Update config manager with environmental settings
                    self.config_manager.custom_environmental_settings = self.env_settings
                    self.config_manager.select_configs(list(self.selected_configs))
                    # Also store custom names as metadata
                    self.config_manager.custom_names = self.custom_names
                    return 'start_multiagent'
                else:
                    # No configs selected - maybe show a message
                    return None

            if 'clear' in self.buttons and self.buttons['clear'].collidepoint(adjusted_mouse_pos):
                self.selected_configs.clear()
                # Clear species overviews when configs are cleared
                self.species_overviews.clear()
                return None

            if 'select_all' in self.buttons and self.buttons['select_all'].collidepoint(adjusted_mouse_pos):
                all_configs = self.config_manager.get_available_configs()
                self.selected_configs = set(all_configs)
                # Clear cached overviews to force recalculation
                self.species_overviews.clear()
                return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # If in naming mode, cancel the rename
                if self.naming_mode is not None:
                    self.naming_mode = None
                    self.rename_input = ""
                    return None
                else:
                    return 'main_menu'
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                configs = self.config_manager.get_available_configs()
                items_per_page = (300 - 40) // 30  # panel_height calculation
                max_scroll = max(0, len(configs) - items_per_page)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 10)
            elif event.key == pygame.K_PAGEDOWN:
                configs = self.config_manager.get_available_configs()
                items_per_page = (300 - 40) // 30
                max_scroll = max(0, len(configs) - items_per_page)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 10)

            # Handle rename input
            if self.naming_mode is not None:
                if event.key == pygame.K_RETURN:
                    # Confirm the rename
                    if self.rename_input.strip():  # Only rename if there's input
                        self.custom_names[self.naming_mode] = self.rename_input.strip()
                    self.naming_mode = None
                    self.rename_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.rename_input = self.rename_input[:-1]
                elif event.unicode:  # Any other character
                    # Limit input length
                    if len(self.rename_input) < 30:
                        self.rename_input += event.unicode
            # Handle text input for environmental settings
            elif self.active_input is not None:
                if event.key == pygame.K_RETURN:
                    self._apply_single_input(self.active_input)
                    self.active_input = None
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_input in self.input_texts:
                        self.input_texts[self.active_input] = self.input_texts[self.active_input][:-1]
                elif event.unicode.isdigit() or event.unicode in '.-+e':
                    if self.active_input in self.input_texts:
                        self.input_texts[self.active_input] += event.unicode
                    else:
                        self.input_texts[self.active_input] = event.unicode

        elif event.type == pygame.MOUSEWHEEL:
            # Handle scrolling with mouse wheel
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))

        return None  # Stay in multiagent menu

    def _increment_setting(self, key):
        """Increment a numeric environmental setting."""
        if key not in self.env_settings:
            return

        value = self.env_settings[key]
        if not isinstance(value, (int, float)):
            return

        # Determine increment amount based on the setting
        if key in ['MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE', 'DOMINANCE_MUTATION_RATE',
                   'SOMATIC_MUTATION_RATE', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR', 'HYDRATION_DRAIN_RATE',
                   'VISION_NOISE_STD', 'NN_WEIGHT_INIT_STD', 'NN_HIDDEN_NOISE_STD', 'POINT_MUTATION_STDDEV',
                   'LARGE_MUTATION_STDDEV', 'STRESS_GAIN_RATE', 'STRESS_DECAY_RATE', 'STRESS_THREAT_WEIGHT',
                   'STRESS_RESOURCE_WEIGHT', 'EFFORT_SPEED_SCALE', 'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE',
                   'BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_THRESHOLD', 'REPRODUCTION_COST', 'FOOD_ENERGY',
                   'BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_DRAIN_RATE', 'DRINK_RATE',
                   'ATTACK_DISTANCE', 'ATTACK_DAMAGE_BASE', 'ATTACK_ENERGY_COST', 'KILL_ENERGY_GAIN',
                   'MAX_SPEED_BASE', 'EATING_DISTANCE', 'MATING_DISTANCE', 'WANDER_STRENGTH', 'STEER_STRENGTH',
                   'MATURITY_AGE', 'REPRODUCTION_COOLDOWN', 'MATE_SEARCH_RADIUS', 'MAX_AGE',
                   'CANNIBALISM_ENERGY_BONUS', 'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE',
                   'HYBRID_FERTILITY_RATE', 'NUMBER_OF_INITIAL_SPECIES', 'FPS',
                   'AGE_PRIME_START', 'AGE_PRIME_END', 'AGE_SPEED_DECLINE', 'AGE_STAMINA_DECLINE',
                   'AGE_EXPERIENCE_BONUS', 'LOW_ENERGY_ATTACK_PENALTY', 'LOW_HYDRATION_SPEED_PENALTY',
                   'HIGH_STRESS_EFFORT_BOOST', 'EXHAUSTION_THRESHOLD', 'COST_HIGH_SPEED_MULTIPLIER',
                   'COST_SHARP_TURN_MULTIPLIER', 'COST_PURSUIT_MULTIPLIER', 'COST_ATTACK_BASE',
                   'COST_MATING_BASE', 'AGILITY_SPEED_BONUS', 'AGILITY_STAMINA_COST', 'ARMOR_DAMAGE_REDUCTION',
                   'ARMOR_SPEED_PENALTY', 'ARMOR_ENERGY_COST', 'SENSOR_DROPOUT_RATE', 'INTERNAL_STATE_NOISE',
                   'PERCEPTION_LAG', 'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY', 'TIME_SINCE_MATING_DECAY',
                   'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD', 'CROWD_STRESS_RATE', 'DOMINANCE_STRESS_FACTOR']:
            increment = 0.001
        elif isinstance(value, int):
            increment = 1
        else:
            increment = 0.1

        self.env_settings[key] += increment
        if isinstance(self.env_settings[key], float):
            self.env_settings[key] = round(self.env_settings[key], 4)
        self.input_texts[key] = str(self.env_settings[key])

    def _decrement_setting(self, key):
        """Decrement a numeric environmental setting."""
        if key not in self.env_settings:
            return

        value = self.env_settings[key]
        if not isinstance(value, (int, float)):
            return

        # Determine decrement amount based on the setting
        if key in ['MUTATION_RATE', 'CROSSOVER_RATE', 'LARGE_MUTATION_CHANCE', 'DOMINANCE_MUTATION_RATE',
                   'SOMATIC_MUTATION_RATE', 'ENERGY_DRAIN_BASE', 'MOVEMENT_ENERGY_FACTOR', 'HYDRATION_DRAIN_RATE',
                   'VISION_NOISE_STD', 'NN_WEIGHT_INIT_STD', 'NN_HIDDEN_NOISE_STD', 'POINT_MUTATION_STDDEV',
                   'LARGE_MUTATION_STDDEV', 'STRESS_GAIN_RATE', 'STRESS_DECAY_RATE', 'STRESS_THREAT_WEIGHT',
                   'STRESS_RESOURCE_WEIGHT', 'EFFORT_SPEED_SCALE', 'EFFORT_DAMAGE_SCALE', 'EFFORT_ENERGY_SCALE',
                   'BASE_ENERGY', 'MAX_ENERGY', 'REPRODUCTION_THRESHOLD', 'REPRODUCTION_COST', 'FOOD_ENERGY',
                   'BASE_HYDRATION', 'MAX_HYDRATION', 'HYDRATION_DRAIN_RATE', 'DRINK_RATE',
                   'ATTACK_DISTANCE', 'ATTACK_DAMAGE_BASE', 'ATTACK_ENERGY_COST', 'KILL_ENERGY_GAIN',
                   'MAX_SPEED_BASE', 'EATING_DISTANCE', 'MATING_DISTANCE', 'WANDER_STRENGTH', 'STEER_STRENGTH',
                   'MATURITY_AGE', 'REPRODUCTION_COOLDOWN', 'MATE_SEARCH_RADIUS', 'MAX_AGE',
                   'CANNIBALISM_ENERGY_BONUS', 'SPECIES_GENETIC_SIMILARITY_THRESHOLD', 'SPECIES_DRIFT_RATE',
                   'HYBRID_FERTILITY_RATE', 'NUMBER_OF_INITIAL_SPECIES', 'FPS',
                   'AGE_PRIME_START', 'AGE_PRIME_END', 'AGE_SPEED_DECLINE', 'AGE_STAMINA_DECLINE',
                   'AGE_EXPERIENCE_BONUS', 'LOW_ENERGY_ATTACK_PENALTY', 'LOW_HYDRATION_SPEED_PENALTY',
                   'HIGH_STRESS_EFFORT_BOOST', 'EXHAUSTION_THRESHOLD', 'COST_HIGH_SPEED_MULTIPLIER',
                   'COST_SHARP_TURN_MULTIPLIER', 'COST_PURSUIT_MULTIPLIER', 'COST_ATTACK_BASE',
                   'COST_MATING_BASE', 'AGILITY_SPEED_BONUS', 'AGILITY_STAMINA_COST', 'ARMOR_DAMAGE_REDUCTION',
                   'ARMOR_SPEED_PENALTY', 'ARMOR_ENERGY_COST', 'SENSOR_DROPOUT_RATE', 'INTERNAL_STATE_NOISE',
                   'PERCEPTION_LAG', 'TIME_SINCE_FOOD_DECAY', 'TIME_SINCE_DAMAGE_DECAY', 'TIME_SINCE_MATING_DECAY',
                   'CROWD_STRESS_RADIUS', 'CROWD_STRESS_THRESHOLD', 'CROWD_STRESS_RATE', 'DOMINANCE_STRESS_FACTOR']:
            decrement = 0.001
        elif isinstance(value, int):
            decrement = 1
        else:
            decrement = 0.1

        self.env_settings[key] = max(0, self.env_settings[key] - decrement)
        if isinstance(self.env_settings[key], float):
            self.env_settings[key] = round(self.env_settings[key], 4)
        self.input_texts[key] = str(self.env_settings[key])

    def _apply_single_input(self, key):
        """Apply a single input text to environmental settings."""
        if key not in self.env_settings:
            return

        try:
            text = self.input_texts.get(key, str(self.env_settings[key]))
            original = self.env_settings[key]

            if isinstance(original, int):
                self.env_settings[key] = int(float(text))
            elif isinstance(original, float):
                self.env_settings[key] = float(text)
            elif isinstance(original, bool):
                # Handle boolean conversion from text
                self.env_settings[key] = text.lower() in ['true', '1', 'yes', 'on', 'y', 't']
            elif isinstance(original, str):
                self.env_settings[key] = text
            elif isinstance(original, list):
                # For list types, try to parse as JSON or comma-separated values
                import json
                try:
                    # Try parsing as JSON first
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        self.env_settings[key] = parsed
                    else:
                        # If not a list, treat as comma-separated values
                        self.env_settings[key] = [item.strip() for item in text.split(',')]
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as comma-separated values
                    self.env_settings[key] = [item.strip() for item in text.split(',')]
            elif isinstance(original, dict):
                # For dict types, try to parse as JSON
                import json
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        self.env_settings[key] = parsed
                    else:
                        # If not a dict, keep original
                        pass
                except json.JSONDecodeError:
                    # If JSON parsing fails, keep original
                    pass
            else:
                # For other types, just convert to string
                self.env_settings[key] = text
        except (ValueError, TypeError):
            # If conversion fails, restore original value in input text
            self.input_texts[key] = str(self.env_settings[key])