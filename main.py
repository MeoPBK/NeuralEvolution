import sys
import os
import random

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.core.simulation import Simulation
from src.rendering.renderer import Renderer
from src.rendering.settings_screen import draw_settings_screen, handle_settings_input
from src.rendering.main_menu import draw_main_menu, handle_main_menu_input
from src.entities.obstacle import Obstacle
from src.utils.vector import Vector2
from settings import SETTINGS
import config


def main():
    pygame.init()

    # Track fullscreen state globally
    is_fullscreen = False

    # Initially use config values for window setup, but will be updated based on settings later
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WORLD_HEIGHT), pygame.RESIZABLE)
    font_large = pygame.font.SysFont('monospace', 30)
    font_med = pygame.font.SysFont('monospace', 20)

    game_state = 'main_menu'  # Start with main menu
    settings = SETTINGS.copy()

    # Store renderer reference to maintain state
    renderer = None

    while True: # Main loop
        if game_state == 'main_menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle window resize
                if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Toggle fullscreen with F11
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    if is_fullscreen:
                        # Exit fullscreen
                        screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WORLD_HEIGHT), pygame.RESIZABLE)
                        is_fullscreen = False
                    else:
                        # Enter fullscreen
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        is_fullscreen = True

                action = handle_main_menu_input(event)
                if action == 'new_simulation':
                    game_state = 'settings'
                elif action == 'multiagent_mode':
                    game_state = 'multiagent_menu'
                elif action == 'load_simulation':
                    # TODO: Implement load simulation functionality
                    pass
                elif action == 'load_settings':
                    game_state = 'load_settings_menu'
                elif action == 'documentation':
                    game_state = 'documentation_view'
                elif action == 'exit':
                    pygame.quit()
                    sys.exit()

            draw_main_menu(screen, font_large, font_med)

        elif game_state == 'load_settings_menu':
            # Handle loading settings from the main menu
            from src.rendering.main_menu import draw_load_dialog, handle_load_dialog_input, load_settings_file

            # Draw the load dialog
            file_rects, close_rect = draw_load_dialog(screen, font_large, font_med, save_type='settings')

            # Wait for user input
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    result = handle_load_dialog_input(event, file_rects, close_rect)
                    if result == 'close':
                        game_state = 'main_menu'
                        waiting_for_input = False
                    elif result:
                        # Load the selected settings file
                        loaded_settings = load_settings_file(result)
                        if loaded_settings:
                            settings.update(loaded_settings)
                            # Refresh the input texts to reflect the loaded settings
                            from src.rendering.settings_screen import refresh_input_texts
                            refresh_input_texts(settings)
                        game_state = 'settings'
                        waiting_for_input = False

        elif game_state == 'documentation_view':
            # Handle documentation view from the main menu
            from src.rendering.main_menu import draw_documentation
            scroll_offset = 0

            viewing_doc = True
            while viewing_doc:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_state = 'main_menu'
                            viewing_doc = False
                        elif event.key == pygame.K_UP:
                            scroll_offset = max(0, scroll_offset - 30)
                        elif event.key == pygame.K_DOWN:
                            scroll_offset = scroll_offset + 30
                    elif event.type == pygame.MOUSEWHEEL:
                        scroll_offset = max(0, scroll_offset - event.y * 30)

                if viewing_doc:  # Only draw if still viewing
                    draw_documentation(screen, font_large, font_med, scroll_offset)

        elif game_state == 'multiagent_menu':
            # Handle multiagent mode menu
            from src.ui.multiagent_menu import MultiagentMenu
            from src.managers.config_manager import ConfigManager

            # Use the existing fonts from the main module
            class FontManager:
                def get_font(self, size):
                    sizes = {'small': 14, 'medium': 18, 'large': 24}
                    font_size = sizes.get(size, 18)
                    return pygame.font.SysFont('monospace', font_size)

            font_manager = FontManager()

            # Create multiagent menu instance
            multiagent_menu = MultiagentMenu(screen, font_manager)

            in_multiagent_menu = True
            while in_multiagent_menu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    # Handle multiagent menu input
                    result = multiagent_menu.handle_input(event)

                    if result == 'main_menu':
                        game_state = 'main_menu'
                        in_multiagent_menu = False
                    elif result == 'start_multiagent':
                        # Get the selected configurations from the config manager
                        config_manager = ConfigManager()
                        selected_configs = config_manager.get_all_agent_configs()
                        selected_config_names = config_manager.get_selected_config_names()

                        # Create a combined settings dictionary with multiagent configurations
                        multiagent_settings = settings.copy()
                        multiagent_settings['MULTIAGENT_CONFIGS'] = {}

                        # Load each selected configuration and add it to the multiagent configs
                        for config_name in selected_config_names:
                            full_config = config_manager.load_config(config_name)
                            # Extract only agent-specific settings (not environmental)
                            agent_settings = {}
                            for key, value in full_config.items():
                                # Skip environmental settings that should be shared
                                if key not in ['WORLD_WIDTH', 'WORLD_HEIGHT', 'FOOD_SPAWN_RATE', 'INITIAL_FOOD',
                                               'WORLD_BOUNDARY_TYPE', 'GRAVITY_ENABLED', 'WIND_EFFECTS',
                                               'SEASONAL_CHANGES', 'WEATHER_SYSTEM', 'TERRAIN_FEATURES',
                                               'SIMULATION_SPEED', 'PARTICLE_EFFECTS', 'BACKGROUND_ELEMENTS']:
                                    agent_settings[key] = value

                            multiagent_settings['MULTIAGENT_CONFIGS'][config_name] = agent_settings

                        # Update the global settings with multiagent configurations
                        settings.update(multiagent_settings)

                        # Transition to settings to allow final adjustments before simulation
                        game_state = 'settings'
                        in_multiagent_menu = False

                # Draw multiagent menu
                multiagent_menu.draw()
                pygame.display.flip()

        elif game_state == 'settings':
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # On ESC from settings, go back to main menu
                    game_state = 'main_menu'
                    continue

                # Handle window resize
                if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Toggle fullscreen with F11
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    if is_fullscreen:
                        # Exit fullscreen
                        screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WORLD_HEIGHT), pygame.RESIZABLE)
                        is_fullscreen = False
                    else:
                        # Enter fullscreen
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        is_fullscreen = True

                action = handle_settings_input(settings, event)
                if action == 'start':
                    # Maintain fullscreen state when starting simulation
                    if is_fullscreen:
                        # Stay in full-screen mode
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        # Update screen with new settings dimensions in windowed mode
                        screen = pygame.display.set_mode((settings['WINDOW_WIDTH'], settings['WINDOW_HEIGHT']), pygame.RESIZABLE)
                    game_state = 'simulation'
                elif action == 'toggle_fullscreen':
                    # Toggle fullscreen mode
                    if is_fullscreen:
                        # Exit fullscreen
                        screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WORLD_HEIGHT), pygame.RESIZABLE)
                        is_fullscreen = False
                    else:
                        # Enter fullscreen
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        is_fullscreen = True

            draw_settings_screen(screen, settings, font_large, font_med)

        elif game_state == 'simulation':
            # Initialize renderer and simulation objects now that settings are confirmed
            # Pass the current screen to maintain fullscreen state
            renderer = Renderer(settings, screen)
            simulation = Simulation(settings, renderer)

            # Add rocks if enabled (using the existing OBSTACLES_ENABLED flag)
            if settings.get('OBSTACLES_ENABLED', False):
                world_width = settings['WORLD_WIDTH']
                world_height = settings['WORLD_HEIGHT']

                num_rocks = settings.get('NUM_INTERNAL_OBSTACLES', 5)  # Use existing setting

                for _ in range(num_rocks):
                    # Random position with some padding from borders
                    padding = 30
                    pos_x = random.uniform(padding, world_width - padding)
                    pos_y = random.uniform(padding, world_height - padding)

                    # Random size for the rock
                    rock_radius = random.uniform(10, 30)

                    # Determine rock type if enabled
                    rock_type = 'generic'
                    if settings.get('ROCK_TYPES_ENABLED', True):
                        rock_types = ['granite', 'limestone', 'sandstone', 'basalt', 'generic']
                        rock_type = random.choice(rock_types)

                    # Create rock obstacle
                    rock = Obstacle(
                        Vector2(pos_x - rock_radius, pos_y - rock_radius),  # pos is top-left for rectangular bounds
                        rock_radius * 2,  # width
                        rock_radius * 2,  # height
                        'rock',  # obstacle type
                        shape='circle',  # rocks are circular
                        radius=rock_radius,  # actual radius for collision
                        rock_type=rock_type  # specific rock type
                    )
                    simulation.world.obstacle_list.append(rock)

            # Run the simulation loop
            while game_state == 'simulation':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.VIDEORESIZE:
                        # Handle window resize (only in windowed mode)
                        if not is_fullscreen:
                            screen = renderer.handle_resize(event.w, event.h)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_state = 'settings' # Go back to settings
                            # Maintain fullscreen state when returning to settings
                            if is_fullscreen:
                                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            else:
                                screen = pygame.display.set_mode((settings['WINDOW_WIDTH'], settings['WINDOW_HEIGHT']), pygame.RESIZABLE)
                        elif event.key == pygame.K_F11:  # Toggle fullscreen
                            screen = renderer.toggle_fullscreen()
                            is_fullscreen = renderer.is_fullscreen
                        elif event.key == pygame.K_SPACE:
                            simulation.toggle_pause()
                        elif event.key == pygame.K_UP:
                            simulation.speed_up()
                        elif event.key == pygame.K_DOWN:
                            simulation.speed_down()
                        elif event.key == pygame.K_g:  # Toggle genetics menu
                            renderer.show_genetics_menu = not renderer.show_genetics_menu
                        elif event.key == pygame.K_s:  # Toggle statistics menu
                            renderer.show_stats_menu = not renderer.show_stats_menu
                        elif event.key == pygame.K_h:  # Toggle species history menu
                            renderer.show_species_history_menu = not renderer.show_species_history_menu
                        elif event.key == pygame.K_c:  # Toggle creatures menu
                            renderer.show_creatures_menu = not renderer.show_creatures_menu
                        elif event.key == pygame.K_i:  # Toggle HUD sidebar (Information)
                            renderer.show_hud = not renderer.show_hud
                        elif event.key == pygame.K_ESCAPE and renderer.show_agent_info:
                            # Close agent info window when ESC is pressed
                            renderer.show_agent_info = False
                            if renderer.agent_info_window:
                                renderer.agent_info_window.toggle_visibility()
                        # Obstacle creation controls
                        elif event.key == pygame.K_o:  # Toggle obstacles on/off (now rocks)
                            settings['OBSTACLES_ENABLED'] = not settings.get('OBSTACLES_ENABLED', False)
                            # Reinitialize obstacles based on new setting
                            simulation.world.obstacle_list = []
                            # Initialize border obstacles if enabled
                            if settings.get('BORDER_ENABLED', True):
                                world_width = settings['WORLD_WIDTH']
                                world_height = settings['WORLD_HEIGHT']
                                border_width = settings.get('BORDER_WIDTH', 10)

                                # Top border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, 0), world_width, border_width, 'wall'))
                                # Bottom border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, world_height - border_width), world_width, border_width, 'wall'))
                                # Left border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, border_width), border_width, world_height - 2 * border_width, 'wall'))
                                # Right border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(world_width - border_width, border_width),
                                                                         border_width, world_height - 2 * border_width, 'wall'))

                            # Add trees if enabled
                            if settings.get('TREES_ENABLED', True):
                                # Determine number of trees based on either fixed count or density
                                if settings.get('TREE_DENSITY', 0) > 0:
                                    # Calculate number of trees based on density and world area
                                    world_area = world_width * world_height
                                    num_trees = int(settings.get('TREE_DENSITY', 0.0001) * world_area)
                                    # Limit to reasonable bounds
                                    num_trees = max(0, min(num_trees, 50))  # Cap at 50 trees to prevent excessive numbers
                                else:
                                    num_trees = settings.get('NUM_TREES', 15)

                                for _ in range(num_trees):
                                    # Random position with some padding from borders
                                    padding = 50
                                    pos = Vector2(
                                        random.uniform(padding, world_width - padding - 40),
                                        random.uniform(padding, world_height - padding - 40)
                                    )
                                    # Random size for the tree
                                    width = random.uniform(25, 50)
                                    height = random.uniform(40, 80)
                                    # Random tree type
                                    tree_types = ['deciduous', 'coniferous', 'palm']
                                    tree_type = random.choice(tree_types)
                                    # Random foliage color variation
                                    foliage_colors = [
                                        (30, 100, 30),   # Green
                                        (25, 85, 25),   # Darker green
                                        (35, 110, 35),  # Lighter green
                                        (40, 120, 40),  # Bright green
                                    ]
                                    foliage_color = random.choice(foliage_colors)
                                    simulation.world.obstacle_list.append(Obstacle(pos, width, height, 'tree', tree_type=tree_type, tree_foliage_color=foliage_color))

                            # Add rocks if enabled (now the main obstacle when O is pressed)
                            if settings.get('OBSTACLES_ENABLED', False):
                                world_width = settings['WORLD_WIDTH']
                                world_height = settings['WORLD_HEIGHT']

                                num_rocks = settings.get('NUM_INTERNAL_OBSTACLES', 5)  # Use existing setting

                                for _ in range(num_rocks):
                                    # Random position with some padding from borders
                                    padding = 30
                                    pos = Vector2(
                                        random.uniform(padding, world_width - padding - 30),
                                        random.uniform(padding, world_height - padding - 30)
                                    )
                                    # Random size for the rock
                                    rock_radius = random.uniform(10, 30)
                                    # Random rock type if enabled
                                    rock_type = 'generic'
                                    if settings.get('ROCK_TYPES_ENABLED', True):
                                        rock_types = ['granite', 'limestone', 'sandstone', 'basalt', 'generic']
                                        rock_type = random.choice(rock_types)
                                    simulation.world.obstacle_list.append(Obstacle(pos, rock_radius * 2, rock_radius * 2, 'rock', rock_type=rock_type))
                        elif event.key == pygame.K_b:  # Toggle border on/off
                            # Toggle border enabled/disabled
                            settings['BORDER_ENABLED'] = not settings.get('BORDER_ENABLED', True)
                            # Reinitialize obstacles with new border setting
                            simulation.world.obstacle_list = []
                            # Initialize border obstacles if enabled
                            if settings.get('BORDER_ENABLED', True):
                                world_width = settings['WORLD_WIDTH']
                                world_height = settings['WORLD_HEIGHT']
                                border_width = settings.get('BORDER_WIDTH', 10)

                                # Top border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, 0), world_width, border_width, 'wall'))
                                # Bottom border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, world_height - border_width), world_width, border_width, 'wall'))
                                # Left border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(0, border_width), border_width, world_height - 2 * border_width, 'wall'))
                                # Right border
                                simulation.world.obstacle_list.append(Obstacle(Vector2(world_width - border_width, border_width),
                                                                         border_width, world_height - 2 * border_width, 'wall'))

                            # Add trees if enabled
                            if settings.get('TREES_ENABLED', True):
                                # Determine number of trees based on either fixed count or density
                                if settings.get('TREE_DENSITY', 0) > 0:
                                    # Calculate number of trees based on density and world area
                                    world_area = world_width * world_height
                                    num_trees = int(settings.get('TREE_DENSITY', 0.0001) * world_area)
                                    # Limit to reasonable bounds
                                    num_trees = max(0, min(num_trees, 50))  # Cap at 50 trees to prevent excessive numbers
                                else:
                                    num_trees = settings.get('NUM_TREES', 15)

                                for _ in range(num_trees):
                                    # Random position with some padding from borders
                                    padding = 50
                                    pos = Vector2(
                                        random.uniform(padding, world_width - padding - 40),
                                        random.uniform(padding, world_height - padding - 40)
                                    )
                                    # Random size for the tree
                                    width = random.uniform(25, 50)
                                    height = random.uniform(40, 80)
                                    # Random tree type
                                    tree_types = ['deciduous', 'coniferous', 'palm']
                                    tree_type = random.choice(tree_types)
                                    # Random foliage color variation
                                    foliage_colors = [
                                        (30, 100, 30),   # Green
                                        (25, 85, 25),   # Darker green
                                        (35, 110, 35),  # Lighter green
                                        (40, 120, 40),  # Bright green
                                    ]
                                    foliage_color = random.choice(foliage_colors)
                                    simulation.world.obstacle_list.append(Obstacle(pos, width, height, 'tree', tree_type=tree_type, tree_foliage_color=foliage_color))

                            # Add rocks if enabled (now default when O is pressed)
                            if settings.get('OBSTACLES_ENABLED', False):
                                num_rocks = settings.get('NUM_INTERNAL_OBSTACLES', 5)  # Use existing setting

                                for _ in range(num_rocks):
                                    # Random position with some padding from borders
                                    padding = 30
                                    pos = Vector2(
                                        random.uniform(padding, world_width - padding - 30),
                                        random.uniform(padding, world_height - padding - 30)
                                    )
                                    # Random size for the rock
                                    rock_radius = random.uniform(10, 30)
                                    # Random rock type if enabled
                                    rock_type = 'generic'
                                    if settings.get('ROCK_TYPES_ENABLED', True):
                                        rock_types = ['granite', 'limestone', 'sandstone', 'basalt', 'generic']
                                        rock_type = random.choice(rock_types)
                                    simulation.world.obstacle_list.append(Obstacle(pos, rock_radius * 2, rock_radius * 2, 'rock', rock_type=rock_type))
                        elif event.key == pygame.K_m:  # Add horizontal mountain chain
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate a realistic horizontal mountain chain
                            mountains = TerrainGenerator.generate_mountain_chain(
                                world_width, world_height,
                                orientation='horizontal',
                                position_ratio=0.5,  # Middle of world
                                length_ratio=0.85,
                                roughness=0.35,
                                num_segments=18,
                                gap_probability=0.12
                            )
                            simulation.world.obstacle_list.extend(mountains)

                        elif event.key == pygame.K_n:  # Add vertical mountain chain
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate a realistic vertical mountain chain
                            mountains = TerrainGenerator.generate_mountain_chain(
                                world_width, world_height,
                                orientation='vertical',
                                position_ratio=0.5,
                                length_ratio=0.85,
                                roughness=0.35,
                                num_segments=18,
                                gap_probability=0.12
                            )
                            simulation.world.obstacle_list.extend(mountains)

                        elif event.key == pygame.K_r:  # Add vertical meandering river
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate a meandering vertical river
                            river = TerrainGenerator.generate_river(
                                world_width, world_height,
                                orientation='vertical',
                                position_ratio=0.5,
                                meander_strength=0.18,
                                river_width=settings.get('RIVER_WIDTH', 25.0),
                                num_points=25
                            )
                            simulation.world.obstacle_list.extend(river)

                        elif event.key == pygame.K_t:  # Add horizontal meandering river
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate a meandering horizontal river
                            river = TerrainGenerator.generate_river(
                                world_width, world_height,
                                orientation='horizontal',
                                position_ratio=0.5,
                                meander_strength=0.18,
                                river_width=settings.get('RIVER_WIDTH', 25.0),
                                num_points=25
                            )
                            simulation.world.obstacle_list.extend(river)

                        elif event.key == pygame.K_l:  # Add lake
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate a lake at a random position
                            lake = TerrainGenerator.generate_lake(
                                world_width, world_height,
                                center_x_ratio=random.uniform(0.25, 0.75),
                                center_y_ratio=random.uniform(0.25, 0.75),
                                size_ratio=0.12,
                                irregularity=settings.get('LAKE_IRREGULARITY', 0.4),
                                settings=settings
                            )
                            simulation.world.obstacle_list.extend(lake)

                        elif event.key == pygame.K_d:  # Add diagonal mountain range
                            from src.systems.terrain_generator import TerrainGenerator
                            world_width = settings['WORLD_WIDTH']
                            world_height = settings['WORLD_HEIGHT']

                            # Generate diagonal mountain range from random corner
                            corners = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
                            mountains = TerrainGenerator.generate_diagonal_mountain_range(
                                world_width, world_height,
                                start_corner=random.choice(corners),
                                coverage=0.65,
                                roughness=0.3
                            )
                            simulation.world.obstacle_list.extend(mountains)

                        elif event.key == pygame.K_k:  # Toggle rocks on/off (secondary toggle)
                            # Toggle rocks enabled/disabled
                            settings['ROCKS_ENABLED'] = not settings.get('ROCKS_ENABLED', True)
                            # Reinitialize obstacles with new rock setting
                            # Preserve borders and trees
                            preserved_obstacles = [
                                obs for obs in simulation.world.obstacle_list
                                if obs.obstacle_type == 'wall' and (
                                    obs.pos.x == 0 or obs.pos.y == 0 or
                                    obs.pos.x + obs.width >= settings['WORLD_WIDTH'] - 20 or
                                    obs.pos.y + obs.height >= settings['WORLD_HEIGHT'] - 20
                                )
                            ]

                            # Preserve trees if enabled
                            if settings.get('TREES_ENABLED', True):
                                preserved_obstacles.extend([
                                    obs for obs in simulation.world.obstacle_list
                                    if obs.obstacle_type == 'tree'
                                ])

                            # No longer preserving general internal obstacles - only rocks, trees, and borders

                            # Add rocks if enabled
                            if settings.get('ROCKS_ENABLED', True):
                                world_width = settings['WORLD_WIDTH']
                                world_height = settings['WORLD_HEIGHT']

                                # Determine number of rocks based on either fixed count or density
                                if settings.get('ROCK_DENSITY', 0) > 0:
                                    # Calculate number of rocks based on density and world area
                                    world_area = world_width * world_height
                                    num_rocks = int(settings.get('ROCK_DENSITY', 0.0002) * world_area)
                                    # Limit to reasonable bounds
                                    num_rocks = max(0, min(num_rocks, 100))  # Cap at 100 rocks to prevent excessive numbers
                                else:
                                    num_rocks = settings.get('NUM_ROCKS', 20)

                                for _ in range(num_rocks):
                                    # Random position with some padding from borders
                                    padding = 30
                                    pos = Vector2(
                                        random.uniform(padding, world_width - padding - 30),
                                        random.uniform(padding, world_height - padding - 30)
                                    )
                                    # Random size for the rock
                                    rock_radius = random.uniform(10, 30)
                                    # Random rock type if enabled
                                    rock_type = 'generic'
                                    if settings.get('ROCK_TYPES_ENABLED', True):
                                        rock_types = ['granite', 'limestone', 'sandstone', 'basalt', 'generic']
                                        rock_type = random.choice(rock_types)
                                    preserved_obstacles.append(Obstacle(pos, rock_radius * 2, rock_radius * 2, 'rock', rock_type=rock_type))

                            simulation.world.obstacle_list = preserved_obstacles
                        elif event.key == pygame.K_c:  # Clear all obstacles (except borders)
                            # Keep only border obstacles
                            preserved_obstacles = [
                                obs for obs in simulation.world.obstacle_list
                                if obs.obstacle_type == 'wall' and (
                                    obs.pos.x == 0 or obs.pos.y == 0 or
                                    obs.pos.x + obs.width >= settings['WORLD_WIDTH'] - 20 or
                                    obs.pos.y + obs.height >= settings['WORLD_HEIGHT'] - 20
                                )
                            ]

                            # If trees are enabled, also preserve trees
                            if settings.get('TREES_ENABLED', True):
                                preserved_obstacles.extend([
                                    obs for obs in simulation.world.obstacle_list
                                    if obs.obstacle_type == 'tree'
                                ])

                            # If obstacles are enabled, also preserve rocks
                            if settings.get('OBSTACLES_ENABLED', False):
                                preserved_obstacles.extend([
                                    obs for obs in simulation.world.obstacle_list
                                    if obs.obstacle_type == 'rock'
                                ])

                            simulation.world.obstacle_list = preserved_obstacles
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Handle mouse clicks for agent selection
                        if event.button == 1:  # Left mouse button
                            renderer.handle_mouse_click(event.pos, simulation.world)

                        # Handle mouse clicks for menu navigation
                        if renderer.show_species_history_menu and renderer.species_history_vis:
                            renderer.species_history_vis.handle_click(event.pos)
                        elif renderer.show_creatures_menu and renderer.creatures_menu:
                            renderer.creatures_menu.handle_click(event.pos)
                    elif event.type == pygame.MOUSEWHEEL:
                        # Handle scroll for genetics, stats, species history, and creatures menus
                        if renderer.show_genetics_menu and renderer.genetics_vis:
                            renderer.genetics_vis.handle_scroll(-event.y)
                        elif renderer.show_stats_menu and renderer.stats_vis:
                            renderer.stats_vis.scroll_y = max(0, min(
                                renderer.stats_vis.max_scroll,
                                renderer.stats_vis.scroll_y - event.y * 30
                            ))
                        elif renderer.show_species_history_menu and renderer.species_history_vis:
                            renderer.species_history_vis.handle_scroll(-event.y)
                        elif renderer.show_creatures_menu and renderer.creatures_menu:
                            renderer.creatures_menu.handle_scroll(-event.y)
                    elif event.type == pygame.KEYDOWN:
                        # Handle keyboard navigation for species history menu
                        if renderer.show_species_history_menu and renderer.species_history_vis:
                            renderer.species_history_vis.handle_key_press(event.key)
                        # Handle keyboard navigation for creatures menu
                        if renderer.show_creatures_menu and renderer.creatures_menu:
                            renderer.creatures_menu.handle_key_press(event.key)

                dt = renderer.tick()
                # Pass the renderer's particle system to the simulation update
                # We'll temporarily attach it to the simulation object
                simulation.particle_system = renderer.particle_system
                simulation.update(dt)
                renderer.render(simulation)

if __name__ == '__main__':
    main()