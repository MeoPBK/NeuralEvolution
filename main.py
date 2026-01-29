import sys
import os
import random

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.core.simulation import Simulation
from src.rendering.renderer import Renderer
from src.rendering.settings_screen import draw_settings_screen, handle_settings_input
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

    game_state = 'settings'
    settings = SETTINGS.copy()

    # Store renderer reference to maintain state
    renderer = None

    while True: # Main loop
        if game_state == 'settings':
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
                        elif event.key == pygame.K_h:  # Toggle HUD sidebar
                            renderer.show_hud = not renderer.show_hud
                        # Obstacle creation controls
                        elif event.key == pygame.K_o:  # Toggle obstacles on/off
                            settings['OBSTACLES_ENABLED'] = not settings.get('OBSTACLES_ENABLED', False)
                            # Reinitialize obstacles based on new setting
                            simulation.world.obstacle_list = []
                            if settings['OBSTACLES_ENABLED']:
                                simulation.world._init_obstacles()
                        elif event.key == pygame.K_b:  # Toggle border on/off
                            # Toggle border enabled/disabled
                            settings['BORDER_ENABLED'] = not settings.get('BORDER_ENABLED', True)
                            # Reinitialize obstacles with new border setting
                            simulation.world.obstacle_list = []
                            if settings.get('OBSTACLES_ENABLED', False):
                                simulation.world._init_obstacles()
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
                                river_width=25,
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
                                river_width=25,
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
                                irregularity=0.4
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

                        elif event.key == pygame.K_c:  # Clear all obstacles (except borders)
                            # Keep only border obstacles
                            simulation.world.obstacle_list = [
                                obs for obs in simulation.world.obstacle_list
                                if obs.obstacle_type == 'wall' and (
                                    obs.pos.x == 0 or obs.pos.y == 0 or
                                    obs.pos.x + obs.width >= settings['WORLD_WIDTH'] - 20 or
                                    obs.pos.y + obs.height >= settings['WORLD_HEIGHT'] - 20
                                )
                            ]
                    elif event.type == pygame.MOUSEWHEEL:
                        # Handle scroll for genetics and stats menus
                        if renderer.show_genetics_menu and renderer.genetics_vis:
                            renderer.genetics_vis.handle_scroll(-event.y)
                        elif renderer.show_stats_menu and renderer.stats_vis:
                            renderer.stats_vis.scroll_y = max(0, min(
                                renderer.stats_vis.max_scroll,
                                renderer.stats_vis.scroll_y - event.y * 30
                            ))

                dt = renderer.tick()
                # Pass the renderer's particle system to the simulation update
                # We'll temporarily attach it to the simulation object
                simulation.particle_system = renderer.particle_system
                simulation.update(dt)
                renderer.render(simulation)

if __name__ == '__main__':
    main()
