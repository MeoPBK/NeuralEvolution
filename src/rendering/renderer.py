import pygame
import config
import random
from src.utils.vector import Vector2
from .hud import draw_hud
from .graph import draw_graph
from .genetics_visualization import GeneticsVisualization
from .stats_visualization import StatsVisualization
from .particle_system import ParticleSystem


class Renderer:
    def __init__(self, settings=None, screen=None):
        self.settings = settings or {}
        pygame.init()

        # Use provided screen or create a new one
        if screen is not None:
            self.screen = screen
        else:
            # Use settings if available, otherwise fall back to config
            width = self.settings.get('WINDOW_WIDTH', config.WINDOW_WIDTH)
            height = self.settings.get('WINDOW_HEIGHT', config.WORLD_HEIGHT)
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        pygame.display.set_caption("Population Simulation - Neural Network Evolution")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont('monospace', 12)
        self.font_med = pygame.font.SysFont('monospace', 14)
        self.font_large = pygame.font.SysFont('monospace', 16)

        # Track fullscreen state
        self.is_fullscreen = bool(self.screen.get_flags() & pygame.FULLSCREEN)

        # HUD visibility (always visible by default)
        self.show_hud = True

        # Initialize genetics visualization
        self.genetics_vis = None  # Will be initialized with world reference later
        self.show_genetics_menu = False

        # Initialize statistics visualization
        self.stats_vis = None  # Will be initialized with world reference later
        self.show_stats_menu = False

        # Initialize particle system for mating animations
        self.particle_system = ParticleSystem()

        # Cache for temperature zone surfaces to improve performance
        self.zone_surfaces_cache = None
        self.last_world_dimensions = None

        # Scaling factors for adapting to window size
        self.scale_x = 1.0
        self.scale_y = 1.0
        self._update_scale_factors()

    def _update_scale_factors(self):
        """Update scale factors based on window size vs world size."""
        screen_width, screen_height = self.screen.get_size()
        world_width = self.settings.get('WORLD_WIDTH', config.WORLD_WIDTH)
        world_height = self.settings.get('WORLD_HEIGHT', config.WORLD_HEIGHT)

        # Calculate scale factors to fit world in window while maintaining aspect ratio
        self.scale_x = screen_width / world_width
        self.scale_y = screen_height / world_height

        # Use the smaller scale to ensure the entire world fits in the window
        min_scale = min(self.scale_x, self.scale_y)
        self.scale_x = min_scale
        self.scale_y = min_scale

    def render(self, simulation):
        world = simulation.world
        settings = world.settings  # Use world's settings

        # Clear the entire screen first to prevent trail artifacts
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(config.BG_COLOR)

        # Update scale factors if screen size changed
        current_scale_x = screen_width / settings['WORLD_WIDTH']
        current_scale_y = screen_height / settings['WORLD_HEIGHT']
        min_scale = min(current_scale_x, current_scale_y)
        if abs(self.scale_x - min_scale) > 0.001 or abs(self.scale_y - min_scale) > 0.001:
            self.scale_x = min_scale
            self.scale_y = min_scale

        # Initialize genetics visualization if not already done
        if self.genetics_vis is None:
            self.genetics_vis = GeneticsVisualization(world, settings)
        else:
            # Update the world reference each frame to ensure it's current
            self.genetics_vis.world = world

        # Initialize statistics visualization if not already done
        if self.stats_vis is None:
            self.stats_vis = StatsVisualization(world, simulation.stats)
        else:
            # Update the world reference each frame to ensure it's current
            self.stats_vis.world = world
            # Ensure stats collector is set
            if self.stats_vis.stats_collector is None:
                self.stats_vis.set_stats_collector(simulation.stats)

        # Draw continuous temperature gradient for geographic visualization
        # Only draw if temperature is enabled in settings
        if (hasattr(world, 'temperature_zones') and
            settings.get('TEMPERATURE_ENABLED', False) and
            settings.get('TEMPERATURE_ZONES_X', 2) > 0 and
            settings.get('TEMPERATURE_ZONES_Y', 2) > 0):

            # Debug print to check if this code is being executed
            # print(f"Drawing temperature gradient. Zones: {settings.get('TEMPERATURE_ZONES_X')}x{settings.get('TEMPERATURE_ZONES_Y')}")

            # Create a smooth temperature gradient across the entire world
            world_width = settings['WORLD_WIDTH']
            world_height = settings['WORLD_HEIGHT']

            # Create a single surface for the entire world background
            gradient_surface = pygame.Surface((world_width, world_height))

            # Calculate temperature at each pixel for a smooth gradient
            # To optimize performance, we'll sample at intervals and interpolate
            sample_interval = 20  # Sample every 20 pixels

            for y in range(0, world_height, sample_interval):
                for x in range(0, world_width, sample_interval):
                    # Get temperature at this position using the world's method
                    temp_pos = Vector2(x, y)
                    temperature = world.get_temperature_at_position(temp_pos)

                    # Calculate color based on temperature (hotter = more red, cooler = more blue)
                    temp_normalized = max(0, min(1, (temperature - 10) / 20))  # Normalize to 0-1 range

                    # Interpolate between blue (cool) and red (hot) - make colors more intense
                    r = int(0 + 255 * temp_normalized)  # Full red intensity for higher temperature
                    g = 5    # Very low green for maximum contrast
                    b = int(0 + 255 * (1 - temp_normalized))  # Full blue intensity for lower temperature

                    # Draw a rectangle with this color
                    color_rect = pygame.Rect(x, y, sample_interval, sample_interval)
                    pygame.draw.rect(gradient_surface, (r, g, b), color_rect)

            gradient_surface.set_alpha(30)  # Increased alpha for more visible effect
            # Draw the gradient surface scaled to fit the screen
            scaled_gradient = pygame.transform.smoothscale(gradient_surface,
                                                          (int(world_width * self.scale_x),
                                                           int(world_height * self.scale_y)))
            self.screen.blit(scaled_gradient, (0, 0))

        # Draw water sources
        for water in world.water_list:
            # Scale the position and size
            scaled_x = int(water.pos.x * self.scale_x)
            scaled_y = int(water.pos.y * self.scale_y)
            scaled_radius = int(water.radius * self.scale_x)  # Use x scale for uniform scaling
            pos = (scaled_x, scaled_y)
            # Translucent circle effect: draw filled then a lighter ring
            pygame.draw.circle(self.screen, (30, 70, 130), pos, scaled_radius)
            pygame.draw.circle(self.screen, config.WATER_COLOR, pos, scaled_radius, max(1, int(2 * self.scale_x)))

        # Draw food
        for food in world.food_list:
            if food.alive:
                # Scale the position and size
                scaled_x = int(food.pos.x * self.scale_x)
                scaled_y = int(food.pos.y * self.scale_y)
                scaled_size = max(1, int(2 * self.scale_x))  # Minimum size of 1
                pos = (scaled_x, scaled_y)
                pygame.draw.circle(self.screen, config.FOOD_COLOR, pos, scaled_size)

        # Draw obstacles with improved visuals
        if hasattr(world, 'obstacle_list'):
            for obstacle in world.obstacle_list:
                if obstacle.alive:
                    # Scale the position and size
                    scaled_x = int(obstacle.pos.x * self.scale_x)
                    scaled_y = int(obstacle.pos.y * self.scale_y)
                    scaled_width = max(1, int(obstacle.width * self.scale_x))
                    scaled_height = max(1, int(obstacle.height * self.scale_y))

                    if obstacle.obstacle_type == 'mountain':
                        # Mountain colors for top-down view
                        outer_rock = (90, 75, 55)     # Outer edge / foothills
                        mid_rock = (120, 100, 75)     # Middle elevation
                        inner_rock = (150, 130, 100)  # Higher elevation
                        peak_color = (180, 165, 140)  # Near peak
                        snow_color = (240, 245, 250)  # Snow cap
                        shadow_color = (60, 50, 40)   # Shadow

                        if obstacle.shape == 'circle':
                            # Circular mountain (top-down view)
                            scaled_radius = max(3, int(obstacle.radius * self.scale_x))
                            center_x = int(obstacle.pos.x * self.scale_x)
                            center_y = int(obstacle.pos.y * self.scale_y)

                            # Draw shadow
                            shadow_offset = max(2, int(3 * self.scale_x))
                            pygame.draw.circle(self.screen, shadow_color,
                                             (center_x + shadow_offset, center_y + shadow_offset),
                                             scaled_radius)

                            # Draw concentric circles for elevation effect
                            pygame.draw.circle(self.screen, outer_rock, (center_x, center_y), scaled_radius)

                            if scaled_radius > 6:
                                pygame.draw.circle(self.screen, mid_rock, (center_x, center_y),
                                                 int(scaled_radius * 0.75))

                            if scaled_radius > 10:
                                pygame.draw.circle(self.screen, inner_rock, (center_x, center_y),
                                                 int(scaled_radius * 0.5))

                            if scaled_radius > 15:
                                pygame.draw.circle(self.screen, peak_color, (center_x, center_y),
                                                 int(scaled_radius * 0.3))

                            # Snow cap for larger mountains
                            if scaled_radius > 20:
                                pygame.draw.circle(self.screen, snow_color, (center_x, center_y),
                                                 int(scaled_radius * 0.15))

                            # Outline
                            pygame.draw.circle(self.screen, (70, 60, 45), (center_x, center_y),
                                             scaled_radius, 1)
                        else:
                            # Rectangular mountain (fallback)
                            shadow_offset = max(2, int(2 * self.scale_x))
                            pygame.draw.rect(self.screen, shadow_color,
                                            (scaled_x + shadow_offset, scaled_y + shadow_offset,
                                             scaled_width, scaled_height))
                            pygame.draw.rect(self.screen, outer_rock,
                                            (scaled_x, scaled_y, scaled_width, scaled_height))
                            pygame.draw.rect(self.screen, (60, 45, 35),
                                            (scaled_x, scaled_y, scaled_width, scaled_height), 1)

                    elif obstacle.obstacle_type == 'water_barrier':
                        # Draw realistic water/river (optimized - no particles)
                        deep_water = (35, 85, 150)     # Deep blue
                        mid_water = (55, 115, 180)     # Medium blue
                        shallow_water = (75, 145, 200) # Lighter blue

                        # Draw deep water base
                        pygame.draw.rect(self.screen, deep_water,
                                        (scaled_x, scaled_y, scaled_width, scaled_height))

                        # Draw mid-water layer (slightly inset)
                        if scaled_width > 6 and scaled_height > 6:
                            inset = max(2, int(2 * self.scale_x))
                            pygame.draw.rect(self.screen, mid_water,
                                            (scaled_x + inset, scaled_y + inset,
                                             scaled_width - inset * 2, scaled_height - inset * 2))

                        # Draw shallow water center
                        if scaled_width > 12 and scaled_height > 12:
                            inset2 = max(4, int(4 * self.scale_x))
                            pygame.draw.rect(self.screen, shallow_water,
                                            (scaled_x + inset2, scaled_y + inset2,
                                             scaled_width - inset2 * 2, scaled_height - inset2 * 2))

                        # Dark border for depth/banks
                        bank_color = (60, 50, 40)  # Muddy brown bank
                        pygame.draw.rect(self.screen, bank_color,
                                        (scaled_x, scaled_y, scaled_width, scaled_height), 2)

                    elif obstacle.obstacle_type == 'wall':
                        # Simple wall/border
                        pygame.draw.rect(self.screen, obstacle.color,
                                        (scaled_x, scaled_y, scaled_width, scaled_height))
                        pygame.draw.rect(self.screen, (150, 150, 150),
                                        (scaled_x, scaled_y, scaled_width, scaled_height), 1)

                    else:
                        # Default obstacle rendering
                        pygame.draw.rect(self.screen, obstacle.color,
                                        (scaled_x, scaled_y, scaled_width, scaled_height))
                        pygame.draw.rect(self.screen, (200, 200, 200),
                                        (scaled_x, scaled_y, scaled_width, scaled_height), 1)

        # Draw agents
        for agent in world.agent_list:
            if agent.alive:
                # Scale the position and size
                scaled_x = int(agent.pos.x * self.scale_x)
                scaled_y = int(agent.pos.y * self.scale_y)
                pos = (scaled_x, scaled_y)

                # We need to modify the agent's draw_with_shape method to accept scale
                # For now, we'll draw using scaled parameters
                scaled_radius = max(1, int(agent.radius() * self.scale_x))

                # Draw the agent with its specific shape based on species, but scaled
                color = agent.get_color()

                if agent.shape_type == 'circle':
                    pygame.draw.circle(self.screen, color, pos, scaled_radius)
                elif agent.shape_type == 'square':
                    rect_size = scaled_radius * 2
                    pygame.draw.rect(self.screen, color, (pos[0] - scaled_radius, pos[1] - scaled_radius, rect_size, rect_size))
                elif agent.shape_type == 'triangle':
                    # Draw an upward-pointing triangle
                    points = [
                        (pos[0], pos[1] - scaled_radius),  # Top point
                        (pos[0] - scaled_radius, pos[1] + scaled_radius),  # Bottom left
                        (pos[0] + scaled_radius, pos[1] + scaled_radius)   # Bottom right
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                elif agent.shape_type == 'diamond':
                    # Draw a diamond/rhombus shape
                    points = [
                        (pos[0], pos[1] - scaled_radius),  # Top
                        (pos[0] + scaled_radius, pos[1]),  # Right
                        (pos[0], pos[1] + scaled_radius),  # Bottom
                        (pos[0] - scaled_radius, pos[1])   # Left
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                elif agent.shape_type == 'parallelogram':
                    # Draw a parallelogram shape (slanted rectangle)
                    offset = scaled_radius * 0.5  # Horizontal slant
                    points = [
                        (pos[0] - scaled_radius + offset, pos[1] - scaled_radius),  # Top-left shifted right
                        (pos[0] + scaled_radius + offset, pos[1] - scaled_radius),  # Top-right shifted right
                        (pos[0] + scaled_radius - offset, pos[1] + scaled_radius),  # Bottom-right shifted left
                        (pos[0] - scaled_radius - offset, pos[1] + scaled_radius)   # Bottom-left shifted left
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                elif agent.shape_type == 'hexagon':
                    # Draw a hexagon shape
                    points = []
                    for i in range(6):
                        angle_deg = 60 * i - 30  # Offset by -30 to make flat side on top
                        angle_rad = math.radians(angle_deg)
                        x = pos[0] + scaled_radius * math.cos(angle_rad)
                        y = pos[1] + scaled_radius * math.sin(angle_rad)
                        points.append((x, y))
                    pygame.draw.polygon(self.screen, color, points)
                else:
                    # Default to circle if unknown shape
                    pygame.draw.circle(self.screen, color, pos, scaled_radius)

                # Visual effect for infected agents - draw yellow cloud
                if agent.infected:
                    # Draw a yellow cloud around infected agents
                    cloud_radius = scaled_radius + max(2, int(5 * self.scale_x))  # Slightly larger than agent
                    # Draw multiple translucent circles to create a cloud effect
                    for i in range(3):  # Draw 3 overlapping circles for cloud effect
                        offset_x = random.uniform(-scaled_radius/2, scaled_radius/2)
                        offset_y = random.uniform(-scaled_radius/2, scaled_radius/2)
                        cloud_pos = (pos[0] + int(offset_x), pos[1] + int(offset_y))
                        # Use yellow color with transparency
                        cloud_color = (255, 255, 0, 100)  # Yellow with 40% opacity
                        s = pygame.Surface((cloud_radius * 2, cloud_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(s, cloud_color, (cloud_radius, cloud_radius), cloud_radius)
                        self.screen.blit(s, (cloud_pos[0] - cloud_radius, cloud_pos[1] - cloud_radius))

                # Visual effect for recent somatic mutation - use green circle to distinguish from other effects
                if agent.somatic_mutation_timer > 0:
                    effect_radius = scaled_radius + max(1, int(3 * self.scale_x))
                    # Fade effect
                    alpha = int(255 * (agent.somatic_mutation_timer / 0.5))
                    # Use green color to distinguish from other effects
                    pygame.draw.circle(self.screen, (100, 255, 100), pos, effect_radius, max(1, int(2 * self.scale_x)))  # Thicker green outline

                # Direction indicator for aggressive agents
                if agent.attack_intent > 0.5 and agent.velocity.length_sq() > 0.01:
                    # Calculate tip position in world coordinates first
                    tip = agent.pos + agent.velocity.normalized() * (agent.radius() + 3)
                    # Then scale to screen coordinates
                    scaled_tip_x = int(tip.x * self.scale_x)
                    scaled_tip_y = int(tip.y * self.scale_y)
                    pygame.draw.line(self.screen, (255, 100, 100),
                                     pos, (scaled_tip_x, scaled_tip_y), max(1, int(1 * self.scale_x)))


        # Draw event indicators
        event_msg = simulation.event_manager.get_current_event_message()
        if event_msg:
            simulation.event_manager.draw_event_indicator(self.screen, self.font_large)

        # Draw HUD panel - position it on the right side of the world area
        # Calculate HUD position based on actual screen dimensions
        screen_width, screen_height = self.screen.get_size()
        world_width_scaled = int(settings.get('WORLD_WIDTH', config.WORLD_WIDTH) * self.scale_x)
        hud_width = settings.get('HUD_WIDTH', config.HUD_WIDTH)

        # Only draw HUD if enabled
        if self.show_hud:
            # Position HUD on the right side of the scaled world area, but ensure it fits on screen
            hud_x = min(world_width_scaled, screen_width - hud_width)
            hud_rect = pygame.Rect(hud_x, 0, hud_width, screen_height)
            self.screen.fill(config.HUD_BG_COLOR, hud_rect)
            draw_hud(self.screen, simulation, self.font_small, self.font_med, self.font_large)

            # Draw population graph
            draw_graph(self.screen, simulation.stats, self.font_small)

        # Draw genetics visualization if enabled
        if self.show_genetics_menu and self.genetics_vis:
            self.genetics_vis.world = world  # Update world reference
            self.genetics_vis.draw(self.screen)

        # Draw statistics visualization if enabled
        if self.show_stats_menu and self.stats_vis:
            self.stats_vis.world = world  # Update world reference
            self.stats_vis.visible = True  # Sync visibility
            self.stats_vis.draw(self.screen)
        elif self.stats_vis:
            self.stats_vis.visible = False  # Sync visibility when hidden

        # Draw genetics menu hint
        if not self.show_genetics_menu:
            hint_text = self.font_small.render("Press 'G' for Genetics Menu", True, (180, 180, 200))
            self.screen.blit(hint_text, (5, 30))
        else:
            hint_text = self.font_small.render("Press 'G' to Hide Genetics Menu", True, (180, 180, 200))
            self.screen.blit(hint_text, (5, 30))

        # Draw statistics menu hint
        if not self.show_stats_menu:
            hint_text = self.font_small.render("Press 'S' for Statistics Window", True, (180, 180, 200))
            self.screen.blit(hint_text, (5, 50))
        else:
            hint_text = self.font_small.render("Press 'S' to Hide Statistics Window", True, (180, 180, 200))
            self.screen.blit(hint_text, (5, 50))

        # Draw particle effects (like mating hearts)
        self.particle_system.draw(self.screen, self.scale_x, self.scale_y)

        # Draw event indicators
        event_msg = simulation.event_manager.get_current_event_message()
        if event_msg:
            simulation.event_manager.draw_event_indicator(self.screen, self.font_large)

        # FPS counter
        fps = self.clock.get_fps()
        fps_surf = self.font_small.render(f"FPS: {fps:.0f}", True, (150, 150, 150))
        self.screen.blit(fps_surf, (5, 5))

        pygame.display.flip()

    def tick(self):
        # Update particle system
        dt = self.clock.tick(self.settings.get('FPS', config.FPS)) / 1000.0
        self.particle_system.update(dt)
        return dt

    def update_screen_reference(self, new_screen):
        """Update the screen reference when switching between windowed/fullscreen modes."""
        self.screen = new_screen
        # Update fullscreen state
        self.is_fullscreen = bool(new_screen.get_flags() & pygame.FULLSCREEN)
        # Update scale factors when screen changes
        self._update_scale_factors()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode, returning the new screen."""
        if self.is_fullscreen:
            # Exit fullscreen - use settings dimensions
            width = self.settings.get('WINDOW_WIDTH', config.WINDOW_WIDTH)
            height = self.settings.get('WINDOW_HEIGHT', config.WORLD_HEIGHT)
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            self.is_fullscreen = False
        else:
            # Enter fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True

        # Update scale factors for new screen size
        self._update_scale_factors()
        return self.screen

    def handle_resize(self, new_width, new_height):
        """Handle window resize events."""
        if not self.is_fullscreen:
            self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            self._update_scale_factors()
        return self.screen
