"""
Species History Visualization module for the simulation.
This module handles the species history menu (H) display functionality.
"""

import pygame
import math
from collections import defaultdict


class SpeciesHistoryVisualization:
    """Species history visualization with evolutionary tracking."""

    def __init__(self, world, settings):
        self.world = world
        self.settings = settings
        self.visible = False
        self.selected_species_id = None
        self.scroll_offset = 0
        self.max_scroll = 2000
        self.current_page = 0  # Track which species page is currently displayed

        # Fonts
        self.font_tiny = pygame.font.SysFont('monospace', 9)
        self.font_small = pygame.font.SysFont('monospace', 11)
        self.font_medium = pygame.font.SysFont('monospace', 13)
        self.font_large = pygame.font.SysFont('monospace', 15)
        self.font_title = pygame.font.SysFont('monospace', 18, bold=True)

        # Species names cache
        self.species_names = {}
        self.species_colors = {}

        # Shape types for species
        self.species_shapes = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']

        # UI Colors (matching other visualizations)
        self.bg_color = (35, 38, 45)
        self.panel_color = (28, 31, 38)
        self.card_color = (42, 45, 55)
        self.border_color = (70, 75, 85)
        self.text_color = (220, 220, 225)
        self.header_color = (180, 185, 200)
        self.accent_color = (100, 150, 255)
        self.mutation_color = (255, 180, 50)  # Orange/gold for mutations

        # Evolutionary history tracking
        self.evolution_history = {}  # Track trait changes over generations

    def toggle_visibility(self):
        """Toggle the visibility of the species history menu."""
        self.visible = not self.visible

    def set_selected_species(self, species_id):
        """Set the species to focus on in the visualization."""
        self.selected_species_id = species_id

    def get_species_name(self, species_id):
        """Get a human-readable name for a species ID - Italian medieval names."""
        if species_id not in self.species_names:
            italian_medieval_names = [
                "Visconti", "Medici", "Este", "Sforza", "Gonzaga", "Farnese", "Pico", "Borgia",
                "Malatesta", "Montefeltro", "Doria", "Grimaldi", "Cybo", "Colonna", "Orsini",
                "Gentile", "Alberti", "Pazzi", "Salviati", "Rucellai", "Albizzi", "Capponi"
            ]
            self.species_names[species_id] = italian_medieval_names[species_id % len(italian_medieval_names)]
        return self.species_names[species_id]

    def get_species_color(self, species_id):
        """Get a color for a species using golden angle distribution."""
        if species_id not in self.species_colors:
            hue = (species_id * 137.5) % 360
            h = hue / 360.0
            s, v = 0.75, 0.9

            c = v * s
            x = c * (1 - abs((h * 6) % 2 - 1))
            m = v - c

            if h < 1/6:
                r, g, b = c, x, 0
            elif h < 2/6:
                r, g, b = x, c, 0
            elif h < 3/6:
                r, g, b = 0, c, x
            elif h < 4/6:
                r, g, b = 0, x, c
            elif h < 5/6:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x

            self.species_colors[species_id] = (
                int((r + m) * 255),
                int((g + m) * 255),
                int((b + m) * 255)
            )
        return self.species_colors[species_id]

    def get_species_shape(self, species_id):
        """Get the shape type for a species."""
        return self.species_shapes[species_id % len(self.species_shapes)]

    def draw(self, screen):
        """Draw the species history visualization menu."""
        if not self.world:
            return

        screen_width, screen_height = screen.get_size()
        window_width = min(1450, screen_width - 30)
        window_height = min(950, screen_height - 30)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        # Draw window background with shadow
        pygame.draw.rect(screen, (20, 20, 25), (window_x + 5, window_y + 5, window_width, window_height))
        pygame.draw.rect(screen, self.bg_color, (window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, self.border_color, (window_x, window_y, window_width, window_height), 2)

        # Header bar
        header_height = 60  # Increased height for navigation
        pygame.draw.rect(screen, self.panel_color, (window_x, window_y, window_width, header_height))
        pygame.draw.line(screen, self.border_color, (window_x, window_y + header_height),
                        (window_x + window_width, window_y + header_height), 1)

        # Title
        title = self.font_title.render("Species Evolution History", True, self.accent_color)
        screen.blit(title, (window_x + 15, window_y + 10))

        # Navigation controls
        species_data = self._get_species_data()
        num_species = len(species_data)

        # Navigation buttons (only show if there are multiple species to navigate between)
        nav_y = window_y + 35
        if num_species > 1:
            # Previous button
            prev_rect = pygame.Rect(window_x + window_width - 150, nav_y, 60, 25)
            pygame.draw.rect(screen, self.panel_color, prev_rect, border_radius=3)
            pygame.draw.rect(screen, self.border_color, prev_rect, 1, border_radius=3)
            prev_text = self.font_small.render("< Prev", True, self.text_color)
            screen.blit(prev_text, (prev_rect.centerx - prev_text.get_width() // 2,
                                   prev_rect.centery - prev_text.get_height() // 2))

            # Next button
            next_rect = pygame.Rect(window_x + window_width - 80, nav_y, 60, 25)
            pygame.draw.rect(screen, self.panel_color, next_rect, border_radius=3)
            pygame.draw.rect(screen, self.border_color, next_rect, 1, border_radius=3)
            next_text = self.font_small.render("Next >", True, self.text_color)
            screen.blit(next_text, (next_rect.centerx - next_text.get_width() // 2,
                                   next_rect.centery - next_text.get_height() // 2))

            # Page indicator
            page_text = self.font_small.render(f"Page {self.current_page + 1} of {num_species}", True, self.text_color)
            screen.blit(page_text, (window_x + window_width - 250, nav_y))
        elif num_species == 1:
            # Show a message indicating there's only one species
            single_species_text = self.font_small.render("Only one species exists", True, (150, 150, 160))
            screen.blit(single_species_text, (window_x + window_width - 180, nav_y + 5))

        # Close hint
        close_hint = self.font_small.render("[H] to close", True, (150, 150, 160))
        screen.blit(close_hint, (window_x + window_width - 100, window_y + 14))

        # Create clipping region for content
        content_y = window_y + header_height + 5
        content_height = window_height - header_height - 10

        # Set clipping rectangle to content area
        clip_rect = pygame.Rect(window_x, content_y, window_width, content_height)
        screen.set_clip(clip_rect)

        # Draw species history info panel at top
        info_panel_height = self._draw_info_panel(screen, window_x + 10, content_y - self.scroll_offset, window_width - 20)

        if not species_data:
            no_data = self.font_medium.render("No living agents in the population", True, (200, 100, 100))
            screen.blit(no_data, (window_x + 20, content_y + info_panel_height + 20))
            screen.set_clip(None)
            return

        # Draw specific species page if there are species
        species_ids = sorted(species_data.keys())  # Sort by ID for consistent ordering
        if num_species > 0:
            # Make sure current page is within valid range
            if self.current_page >= num_species:
                self.current_page = max(0, num_species - 1)
            elif self.current_page < 0:
                self.current_page = 0

            species_id = species_ids[self.current_page]
            species_info = species_data[species_id]
            self._draw_single_species_page(screen, window_x + 10, content_y + info_panel_height + 10 - self.scroll_offset,
                                          window_width - 20, species_id, species_info)

        # Reset clipping
        screen.set_clip(None)

        # Update max scroll based on content (improved calculation)
        # Calculate actual content height based on the current species page
        actual_content_height = info_panel_height + 650  # Approximate height of species page content
        self.max_scroll = max(0, actual_content_height - content_height + 100)  # Extra space for better scrolling

        # Draw scrollbar if needed
        if self.max_scroll > 0:
            self._draw_scrollbar(screen, window_x, content_y, window_width, content_height)

    def _get_species_data(self):
        """Collect and organize species data."""
        species_agents = defaultdict(list)

        for agent in self.world.agent_list:
            if agent.alive:
                species_agents[agent.species_id].append(agent)

        species_data = {}
        for species_id, agents in species_agents.items():
            if agents:
                # Calculate averages
                avg_speed = sum(a.speed for a in agents) / len(agents)
                avg_size = sum(a.size for a in agents) / len(agents)
                avg_aggression = sum(a.aggression for a in agents) / len(agents)
                avg_age = sum(a.age for a in agents) / len(agents)
                avg_generation = sum(a.generation for a in agents) / len(agents)
                avg_mutations = sum(a.total_mutations for a in agents) / len(agents)
                avg_offspring = sum(a.offspring_count for a in agents) / len(agents)
                avg_virus_res = sum(a.virus_resistance for a in agents) / len(agents)

                # Get representative agent (one with most mutations for interesting traits)
                rep_agent = max(agents, key=lambda a: a.total_mutations)

                # Count males/females
                males = sum(1 for a in agents if a.sex == 'male')
                females = len(agents) - males

                species_data[species_id] = {
                    'agents': agents,
                    'count': len(agents),
                    'males': males,
                    'females': females,
                    'avg_speed': avg_speed,
                    'avg_size': avg_size,
                    'avg_aggression': avg_aggression,
                    'avg_age': avg_age,
                    'avg_generation': avg_generation,
                    'avg_mutations': avg_mutations,
                    'avg_offspring': avg_offspring,
                    'avg_virus_resistance': avg_virus_res,
                    'representative': rep_agent
                }

        # Sort by species_id to keep stable ordering (not by population)
        return dict(sorted(species_data.items(), key=lambda x: x[0]))

    def _draw_single_species_page(self, screen, x, y, width, species_id, species_info):
        """Draw a single species page with detailed information."""
        color = self.get_species_color(species_id)
        name = self.get_species_name(species_id)

        # Card background
        card_height = 580  # Increased height for more content
        pygame.draw.rect(screen, self.card_color, (x, y, width, card_height))
        pygame.draw.rect(screen, color, (x, y, width, card_height), 2)

        # Header with species name and shape
        header_rect = pygame.Rect(x, y, width, 32)
        pygame.draw.rect(screen, self.panel_color, header_rect)

        # Draw shape indicator
        self._draw_shape_indicator(screen, x + 18, y + 16, 12, species_id)

        # Species name
        name_text = self.font_large.render(f"House of {name}", True, color)
        screen.blit(name_text, (x + 35, y + 7))

        # Population info (right side of header)
        pop_text = self.font_medium.render(f"Pop: {species_info['count']}", True, self.text_color)
        sex_text = self.font_small.render(f"M:{species_info['males']} F:{species_info['females']}", True, (150, 150, 160))
        screen.blit(pop_text, (x + 220, y + 8))
        screen.blit(sex_text, (x + 290, y + 10))

        # Generation info
        gen_text = self.font_small.render(f"Gen: {species_info['avg_generation']:.1f}", True, self.text_color)
        screen.blit(gen_text, (x + 360, y + 10))

        # === LEFT PANEL: Evolution History ===
        left_panel_width = 300
        history_x = x + 12
        history_y = y + 40

        # History section header
        history_header = self.font_small.render("EVOLUTION HISTORY", True, self.accent_color)
        screen.blit(history_header, (history_x, history_y))
        history_y += 16

        # Evolution metrics
        metrics = [
            ("Avg Speed", f"{species_info['avg_speed']:.2f}"),
            ("Avg Size", f"{species_info['avg_size']:.2f}"),
            ("Avg Aggression", f"{species_info['avg_aggression']:.2f}"),
            ("Avg Age", f"{species_info['avg_age']:.1f}"),
            ("Avg Generation", f"{species_info['avg_generation']:.1f}"),
            ("Avg Mutations", f"{species_info['avg_mutations']:.1f}"),
            ("Avg Offspring", f"{species_info['avg_offspring']:.1f}"),
            ("Avg Virus Res", f"{species_info['avg_virus_resistance']:.2f}")
        ]

        for i, (label, value) in enumerate(metrics):
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (history_x, history_y + i * 16))
            screen.blit(value_text, (history_x + 120, history_y + i * 16))

        history_y += len(metrics) * 16 + 12

        # Add diet and habitat information
        # Get representative agent to access genetic traits
        rep_agent = species_info['representative']
        if hasattr(rep_agent, 'diet_type'):
            diet_text = self.font_small.render(f"Diet: {rep_agent.diet_type}", True, self.text_color)
            screen.blit(diet_text, (history_x, history_y))
            history_y += 16

        if hasattr(rep_agent, 'habitat_preference'):
            habitat_text = self.font_small.render(f"Habitat: {rep_agent.habitat_preference}", True, self.text_color)
            screen.blit(habitat_text, (history_x, history_y))
            history_y += 16

        # === MIDDLE PANEL: Trait Evolution Timeline ===
        middle_panel_x = x + left_panel_width + 15
        middle_panel_width = 250
        timeline_y = y + 40

        # Timeline header
        timeline_header = self.font_small.render("TRAIT EVOLUTION", True, self.accent_color)
        screen.blit(timeline_header, (middle_panel_x, timeline_y))
        timeline_y += 16

        # Draw trait evolution graphs
        trait_data = [
            ('Speed', species_info['avg_speed'], (100, 200, 100)),
            ('Size', species_info['avg_size'], (100, 150, 220)),
            ('Aggression', species_info['avg_aggression'], (220, 100, 100)),
            ('Virus Res', species_info['avg_virus_resistance'], (200, 180, 100))
        ]

        graph_area_x = middle_panel_x
        graph_area_y = timeline_y
        graph_width = middle_panel_width - 20
        graph_height = 150

        for i, (trait_name, avg_value, trait_color) in enumerate(trait_data):
            # Draw trait label
            label_text = self.font_small.render(trait_name, True, trait_color)
            screen.blit(label_text, (graph_area_x, graph_area_y + i * 40))

            # Draw value
            value_text = self.font_small.render(f"{avg_value:.2f}", True, self.text_color)
            screen.blit(value_text, (graph_area_x + 70, graph_area_y + i * 40))

            # Draw simple bar graph
            bar_max = 10  # Max value for visualization
            bar_width = max(1, int((avg_value / bar_max) * (graph_width - 80)))
            pygame.draw.rect(screen, (50, 50, 60), (graph_area_x + 120, graph_area_y + 5 + i * 40, graph_width - 80, 12))
            pygame.draw.rect(screen, trait_color, (graph_area_x + 120, graph_area_y + 5 + i * 40, bar_width, 12))

        timeline_y += len(trait_data) * 40 + 20

        # === GENERATION EVOLUTION GRAPH ===
        # Draw a simple line graph showing trait changes over generations
        gen_graph_y = timeline_y
        gen_graph_header = self.font_small.render("GENERATION TREND", True, self.accent_color)
        screen.blit(gen_graph_header, (middle_panel_x, gen_graph_y))
        gen_graph_y += 16

        # Draw a simple generation trend graph
        self._draw_generation_trend_graph(screen, middle_panel_x, gen_graph_y, graph_width, 120, species_info)

        # === RIGHT PANEL: Neural Network Changes ===
        nn_x = x + left_panel_width + middle_panel_width + 30
        nn_width = width - left_panel_width - middle_panel_width - 45
        nn_y = y + 38

        # Draw separator line
        pygame.draw.line(screen, self.border_color, (nn_x - 8, y + 35), (nn_x - 8, y + card_height - 5), 1)

        # Neural network header
        nn_header = self.font_small.render("NEURAL NETWORK", True, self.accent_color)
        screen.blit(nn_header, (nn_x, nn_y))
        nn_y += 16

        # Show neural network information
        if species_info['representative'] and hasattr(species_info['representative'], 'brain'):
            brain = species_info['representative'].brain

            # Show brain type
            brain_type = "RNN" if hasattr(brain, 'w_hh') else "FNN"
            type_text = self.font_small.render(f"Type: {brain_type}", True, self.text_color)
            screen.blit(type_text, (nn_x, nn_y))
            nn_y += 16

            # Show weight statistics
            weights = self._get_all_weights(brain)
            active_weights = sum(1 for w in weights if abs(w) > 0.1)
            strong_weights = sum(1 for w in weights if abs(w) > 0.5)

            active_text = self.font_small.render(f"Active: {active_weights}", True, (100, 200, 100))
            screen.blit(active_text, (nn_x, nn_y))
            nn_y += 16

            strong_text = self.font_small.render(f"Strong: {strong_weights}", True, (200, 180, 100))
            screen.blit(strong_text, (nn_x, nn_y))
            nn_y += 16

            # Draw simple neural network visualization
            self._draw_simple_nn(screen, nn_x, nn_y, nn_width - 20, 150, brain, color)
            nn_y += 160

        # Draw species lineage information
        lineage_y = y + 300
        lineage_header = self.font_small.render("LINEAGE & DIVERSITY", True, self.accent_color)
        screen.blit(lineage_header, (x + 12, lineage_y))
        lineage_y += 16

        # Show genetic diversity metrics
        diversity_metrics = [
            ("Genetic Similarity", f"{species_info['representative'].genetic_similarity_score:.3f}"),
            ("Avg Offspring", f"{species_info['avg_offspring']:.1f}"),
            ("Mutation Rate", f"{species_info['avg_mutations']:.2f}")
        ]

        for label, value in diversity_metrics:
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (x + 12, lineage_y))
            screen.blit(value_text, (x + 150, lineage_y))
            lineage_y += 16

        # Draw generational tree graph
        tree_y = lineage_y + 20
        self._draw_generational_tree(screen, x + 12, tree_y, width - 24, 180, species_info)

    def _draw_generation_trend_graph(self, screen, x, y, width, height, species_info):
        """Draw a simple line graph showing trait changes over generations."""
        # Draw graph area
        pygame.draw.rect(screen, (35, 38, 45), (x, y, width, height))
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 1)

        # Draw grid lines
        for i in range(5):
            # Horizontal grid lines
            grid_y = y + i * (height // 4)
            pygame.draw.line(screen, (50, 55, 65), (x, grid_y), (x + width, grid_y), 1)

        # Draw axis labels
        pygame.draw.line(screen, self.text_color, (x, y), (x, y + height), 2)  # Y-axis
        pygame.draw.line(screen, self.text_color, (x, y + height), (x + width, y + height), 2)  # X-axis

        # Draw sample data points (this would normally come from historical data)
        # For now, we'll simulate some data
        generations = list(range(0, 10))
        trait_values = [species_info['avg_speed']] * len(generations)  # Placeholder values
        # Add some variation to make it look more realistic
        import random
        for i in range(len(trait_values)):
            trait_values[i] += random.uniform(-0.5, 0.5)

        # Normalize values to fit in graph
        max_val = max(trait_values) if trait_values else 1
        min_val = min(trait_values) if trait_values else 0
        val_range = max_val - min_val if max_val != min_val else 1

        # Draw the line
        points = []
        for i, val in enumerate(trait_values):
            px = x + 10 + i * (width - 20) // (len(generations) - 1 if len(generations) > 1 else 1)
            py = y + height - 10 - ((val - min_val) / val_range) * (height - 20) if val_range > 0 else y + height // 2
            points.append((px, py))

        if len(points) > 1:
            pygame.draw.lines(screen, (100, 200, 100), False, points, 2)

        # Draw axis labels
        gen_label = self.font_tiny.render("Generation", True, self.text_color)
        screen.blit(gen_label, (x + width // 2 - gen_label.get_width() // 2, y + height + 5))

        trait_label = self.font_tiny.render("Trait Value", True, self.text_color)
        # Rotate the label
        rotated_label = pygame.transform.rotate(trait_label, 90)
        screen.blit(rotated_label, (x - 20, y + height // 2 - rotated_label.get_height() // 2))

    def _draw_generational_tree(self, screen, x, y, width, height, species_info):
        """Draw a generational tree showing evolutionary lineages."""
        # Draw graph area
        pygame.draw.rect(screen, (35, 38, 45), (x, y, width, height))
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 1)

        # Draw title
        title_text = self.font_small.render("Evolutionary Tree", True, self.accent_color)
        screen.blit(title_text, (x + 10, y + 5))

        # Draw axis labels
        gen_label = self.font_tiny.render("Generation", True, self.text_color)
        screen.blit(gen_label, (x + width // 2 - gen_label.get_width() // 2, y + height - 15))

        # Draw sample generational tree
        # This would normally visualize actual evolutionary lineages
        # For now, we'll draw a simplified tree structure
        generations = list(range(0, 10))
        max_gen = max(generations) if generations else 1

        # Draw nodes for each generation
        for gen in generations:
            # Calculate x position based on generation
            node_x = x + 20 + (gen / max_gen) * (width - 40)

            # Draw generation number
            gen_text = self.font_tiny.render(str(gen), True, self.text_color)
            screen.blit(gen_text, (node_x - gen_text.get_width() // 2, y + height - 30))

            # Draw a node representing agents in this generation
            # The size could represent population or fitness
            node_size = max(2, min(8, 5 + species_info['avg_generation'] / 10))  # Adjust size based on avg generation
            pygame.draw.circle(screen, self.accent_color, (int(node_x), y + height // 2), int(node_size))

            # Draw connections between generations
            if gen > 0:
                prev_gen = gen - 1
                prev_x = x + 20 + (prev_gen / max_gen) * (width - 40)
                pygame.draw.line(screen, (80, 100, 120), (prev_x, y + height // 2), (node_x, y + height // 2), 1)

        # Draw a vertical line to represent the timeline
        pygame.draw.line(screen, self.text_color, (x + 10, y + 25), (x + 10, y + height - 25), 2)

    def _draw_info_panel(self, screen, x, y, width):
        """Draw the species history information panel."""
        panel_height = 180

        # Panel background
        pygame.draw.rect(screen, self.card_color, (x, y, width, panel_height))
        pygame.draw.rect(screen, self.accent_color, (x, y, width, panel_height), 2)

        # Header
        header_rect = pygame.Rect(x, y, width, 32)
        pygame.draw.rect(screen, self.panel_color, header_rect)
        title = self.font_title.render("Species Evolution Overview", True, self.accent_color)
        screen.blit(title, (x + 15, y + 6))

        # Evolution summary
        evolution_text = self.font_medium.render("Tracking evolutionary changes across generations", True, self.text_color)
        screen.blit(evolution_text, (x + 15, y + 40))

        # Key metrics
        metrics_text = self.font_small.render("• Trait evolution over time", True, self.header_color)
        screen.blit(metrics_text, (x + 15, y + 65))
        
        metrics_text2 = self.font_small.render("• Neural network changes", True, self.header_color)
        screen.blit(metrics_text2, (x + 15, y + 80))
        
        metrics_text3 = self.font_small.render("• Genetic diversity tracking", True, self.header_color)
        screen.blit(metrics_text3, (x + 15, y + 95))
        
        metrics_text4 = self.font_small.render("• Species lineage and branching", True, self.header_color)
        screen.blit(metrics_text4, (x + 15, y + 110))

        # Legend
        legend_y = y + 130
        pygame.draw.circle(screen, (100, 200, 100), (x + 15, legend_y + 5), 5)
        legend_text = self.font_small.render("Trait Improvement", True, (150, 150, 160))
        screen.blit(legend_text, (x + 25, legend_y))

        pygame.draw.circle(screen, (200, 100, 100), (x + 160, legend_y + 5), 5)
        legend_text2 = self.font_small.render("Trait Decline", True, (150, 150, 160))
        screen.blit(legend_text2, (x + 170, legend_y))

        pygame.draw.circle(screen, self.mutation_color, (x + 320, legend_y + 5), 5)
        legend_text3 = self.font_small.render("Mutation Hotspot", True, (150, 150, 160))
        screen.blit(legend_text3, (x + 330, legend_y))

        return panel_height + 10

    def _draw_species_cards(self, screen, x, y, width, height, species_data):
        """Draw cards for each species with history and evolution data."""
        card_height = 500  # Increased height for more content
        card_margin = 15
        current_y = y

        # Get screen dimensions for viewport culling
        screen_height = screen.get_height()

        for species_id, data in species_data.items():
            # Skip if card is completely above visible area (off top of screen)
            if current_y + card_height < 0:
                current_y += card_height + card_margin
                continue

            # Skip if card is completely below visible area (off bottom of screen)
            if current_y > screen_height:
                current_y += card_height + card_margin
                continue

            self._draw_species_card(screen, x, current_y, width, card_height, species_id, data)
            current_y += card_height + card_margin

    def _draw_species_card(self, screen, x, y, width, height, species_id, data):
        """Draw a single species card with history and evolution data."""
        color = self.get_species_color(species_id)
        name = self.get_species_name(species_id)

        # Card background
        pygame.draw.rect(screen, self.card_color, (x, y, width, height))
        pygame.draw.rect(screen, color, (x, y, width, height), 2)

        # Header with species name and shape
        header_rect = pygame.Rect(x, y, width, 32)
        pygame.draw.rect(screen, self.panel_color, header_rect)

        # Draw shape indicator
        self._draw_shape_indicator(screen, x + 18, y + 16, 12, species_id)

        # Species name
        name_text = self.font_large.render(f"House of {name}", True, color)
        screen.blit(name_text, (x + 35, y + 7))

        # Population info (right side of header)
        pop_text = self.font_medium.render(f"Pop: {data['count']}", True, self.text_color)
        sex_text = self.font_small.render(f"M:{data['males']} F:{data['females']}", True, (150, 150, 160))
        screen.blit(pop_text, (x + 220, y + 8))
        screen.blit(sex_text, (x + 290, y + 10))

        # Generation info
        gen_text = self.font_small.render(f"Gen: {data['avg_generation']:.1f}", True, self.text_color)
        screen.blit(gen_text, (x + 360, y + 10))

        # === LEFT PANEL: Evolution History ===
        left_panel_width = 300
        history_x = x + 12
        history_y = y + 40

        # History section header
        history_header = self.font_small.render("EVOLUTION HISTORY", True, self.accent_color)
        screen.blit(history_header, (history_x, history_y))
        history_y += 16

        # Evolution metrics
        metrics = [
            ("Avg Speed", f"{data['avg_speed']:.2f}"),
            ("Avg Size", f"{data['avg_size']:.2f}"),
            ("Avg Aggression", f"{data['avg_aggression']:.2f}"),
            ("Avg Age", f"{data['avg_age']:.1f}"),
            ("Avg Generation", f"{data['avg_generation']:.1f}"),
            ("Avg Mutations", f"{data['avg_mutations']:.1f}"),
            ("Avg Offspring", f"{data['avg_offspring']:.1f}"),
            ("Avg Virus Res", f"{data['avg_virus_resistance']:.2f}")
        ]

        for i, (label, value) in enumerate(metrics):
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (history_x, history_y + i * 16))
            screen.blit(value_text, (history_x + 120, history_y + i * 16))

        history_y += len(metrics) * 16 + 12

        # Add diet and habitat information
        # Get representative agent to access genetic traits
        rep_agent = data['representative']
        if hasattr(rep_agent, 'diet_type'):
            diet_text = self.font_small.render(f"Diet: {rep_agent.diet_type}", True, self.text_color)
            screen.blit(diet_text, (history_x, history_y))
            history_y += 16

        if hasattr(rep_agent, 'habitat_preference'):
            habitat_text = self.font_small.render(f"Habitat: {rep_agent.habitat_preference}", True, self.text_color)
            screen.blit(habitat_text, (history_x, history_y))
            history_y += 16

        # === MIDDLE PANEL: Trait Evolution Timeline ===
        middle_panel_x = x + left_panel_width + 15
        middle_panel_width = 250
        timeline_y = y + 40

        # Timeline header
        timeline_header = self.font_small.render("TRAIT EVOLUTION", True, self.accent_color)
        screen.blit(timeline_header, (middle_panel_x, timeline_y))
        timeline_y += 16

        # Draw trait evolution graphs
        trait_data = [
            ('Speed', data['avg_speed'], (100, 200, 100)),
            ('Size', data['avg_size'], (100, 150, 220)),
            ('Aggression', data['avg_aggression'], (220, 100, 100)),
            ('Virus Res', data['avg_virus_resistance'], (200, 180, 100))
        ]

        graph_area_x = middle_panel_x
        graph_area_y = timeline_y
        graph_width = middle_panel_width - 20
        graph_height = 150

        for i, (trait_name, avg_value, trait_color) in enumerate(trait_data):
            # Draw trait label
            label_text = self.font_small.render(trait_name, True, trait_color)
            screen.blit(label_text, (graph_area_x, graph_area_y + i * 40))

            # Draw value
            value_text = self.font_small.render(f"{avg_value:.2f}", True, self.text_color)
            screen.blit(value_text, (graph_area_x + 70, graph_area_y + i * 40))

            # Draw simple bar graph
            bar_max = 10  # Max value for visualization
            bar_width = max(1, int((avg_value / bar_max) * (graph_width - 80)))
            pygame.draw.rect(screen, (50, 50, 60), (graph_area_x + 120, graph_area_y + 5 + i * 40, graph_width - 80, 12))
            pygame.draw.rect(screen, trait_color, (graph_area_x + 120, graph_area_y + 5 + i * 40, bar_width, 12))

        timeline_y += len(trait_data) * 40 + 20

        # === RIGHT PANEL: Neural Network Changes ===
        nn_x = x + left_panel_width + middle_panel_width + 30
        nn_width = width - left_panel_width - middle_panel_width - 45
        nn_y = y + 38

        # Draw separator line
        pygame.draw.line(screen, self.border_color, (nn_x - 8, y + 35), (nn_x - 8, y + height - 5), 1)

        # Neural network header
        nn_header = self.font_small.render("NEURAL NETWORK", True, self.accent_color)
        screen.blit(nn_header, (nn_x, nn_y))
        nn_y += 16

        # Show neural network information
        if data['representative'] and hasattr(data['representative'], 'brain'):
            brain = data['representative'].brain
            
            # Show brain type
            brain_type = "RNN" if hasattr(brain, 'w_hh') else "FNN"
            type_text = self.font_small.render(f"Type: {brain_type}", True, self.text_color)
            screen.blit(type_text, (nn_x, nn_y))
            nn_y += 16

            # Show weight statistics
            weights = self._get_all_weights(brain)
            active_weights = sum(1 for w in weights if abs(w) > 0.1)
            strong_weights = sum(1 for w in weights if abs(w) > 0.5)
            
            active_text = self.font_small.render(f"Active: {active_weights}", True, (100, 200, 100))
            screen.blit(active_text, (nn_x, nn_y))
            nn_y += 16
            
            strong_text = self.font_small.render(f"Strong: {strong_weights}", True, (200, 180, 100))
            screen.blit(strong_text, (nn_x, nn_y))
            nn_y += 16

            # Draw simple neural network visualization
            self._draw_simple_nn(screen, nn_x, nn_y, nn_width - 20, 150, brain, color)
            nn_y += 160

        # Draw species lineage information
        lineage_y = y + 300
        lineage_header = self.font_small.render("LINEAGE & DIVERSITY", True, self.accent_color)
        screen.blit(lineage_header, (x + 12, lineage_y))
        lineage_y += 16

        # Show genetic diversity metrics
        diversity_metrics = [
            ("Genetic Similarity", f"{data['representative'].genetic_similarity_score:.3f}"),
            ("Avg Offspring", f"{data['avg_offspring']:.1f}"),
            ("Mutation Rate", f"{data['avg_mutations']:.2f}")
        ]

        for label, value in diversity_metrics:
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (x + 12, lineage_y))
            screen.blit(value_text, (x + 150, lineage_y))
            lineage_y += 16

    def _get_all_weights(self, brain):
        """Extract all weights from a brain as a flat list."""
        weights = []
        try:
            # Input-hidden weights
            for row in brain.w_ih:
                weights.extend(row)
            # Hidden biases
            weights.extend(brain.b_h)
            # Hidden-output weights
            for row in brain.w_ho:
                weights.extend(row)
            # Output biases
            weights.extend(brain.b_o)
        except AttributeError:
            # For RNN brains
            try:
                for row in brain.w_ih:
                    weights.extend(row)
                for row in brain.w_hh:
                    weights.extend(row)
                weights.extend(brain.b_h)
                for row in brain.w_ho:
                    weights.extend(row)
                weights.extend(brain.b_o)
            except AttributeError:
                pass
        return weights

    def _draw_shape_indicator(self, screen, x, y, size, species_id):
        """Draw a small shape indicator for a species."""
        color = self.get_species_color(species_id)
        shape = self.get_species_shape(species_id)

        if shape == 'circle':
            pygame.draw.circle(screen, color, (x, y), size // 2)
        elif shape == 'square':
            pygame.draw.rect(screen, color, (x - size//2, y - size//2, size, size))
        elif shape == 'triangle':
            points = [(x, y - size//2), (x - size//2, y + size//2), (x + size//2, y + size//2)]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'diamond':
            points = [(x, y - size//2), (x + size//2, y), (x, y + size//2), (x - size//2, y)]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'hexagon':
            points = [(x + size//2 * math.cos(math.radians(60*i - 30)),
                      y + size//2 * math.sin(math.radians(60*i - 30))) for i in range(6)]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'parallelogram':
            offset = size * 0.25
            points = [
                (x - size//2 + offset, y - size//2),
                (x + size//2 + offset, y - size//2),
                (x + size//2 - offset, y + size//2),
                (x - size//2 - offset, y + size//2)
            ]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'pentagon':
            points = [(x + size//2 * math.cos(math.radians(72*i - 90)),
                      y + size//2 * math.sin(math.radians(72*i - 90))) for i in range(5)]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'star':
            star_points = []
            for i in range(5):
                # Outer point
                outer_angle = math.radians(72 * i - 90)
                star_points.append((x + size//2 * math.cos(outer_angle),
                                   y + size//2 * math.sin(outer_angle)))
                # Inner point
                inner_angle = math.radians(72 * i + 36 - 90)
                star_points.append((x + size//4 * math.cos(inner_angle),
                                   y + size//4 * math.sin(inner_angle)))
            pygame.draw.polygon(screen, color, star_points)
        else:
            pygame.draw.circle(screen, color, (x, y), size // 2)

    def _draw_simple_nn(self, screen, x, y, width, height, brain, color):
        """Draw a simple neural network visualization."""
        # Layout parameters
        left_margin = 20
        right_margin = 20
        top_margin = 20
        bottom_margin = 20

        # Three columns for layers
        usable_width = width - left_margin - right_margin
        layer_spacing = usable_width // 2

        # Neuron positions (simplified)
        input_x = x + left_margin
        hidden_x = x + left_margin + layer_spacing
        output_x = x + left_margin + usable_width

        # Calculate neuron Y positions
        n_inputs = min(16, 8)  # Limit for visualization
        n_hidden = min(6, 6)   # Limit for visualization
        n_outputs = min(4, 4)  # Limit for visualization

        usable_height = height - top_margin - bottom_margin

        # Spread neurons vertically with proper centering
        input_spacing = usable_height / (n_inputs + 1) if n_inputs > 0 else 0
        hidden_spacing = usable_height / (n_hidden + 1) if n_hidden > 0 else 0
        output_spacing = usable_height / (n_outputs + 1) if n_outputs > 0 else 0

        input_neurons = []
        hidden_neurons = []
        output_neurons = []

        for i in range(n_inputs):
            input_neurons.append((input_x, y + top_margin + (i + 1) * input_spacing))

        for i in range(n_hidden):
            hidden_neurons.append((hidden_x, y + top_margin + (i + 1) * hidden_spacing))

        for i in range(n_outputs):
            output_neurons.append((output_x, y + top_margin + (i + 1) * output_spacing))

        # Draw connections with proper error handling
        try:
            # Input -> Hidden connections
            for h_idx in range(n_hidden):
                for i_idx in range(n_inputs):
                    if hasattr(brain, 'w_ih') and brain.w_ih is not None and \
                       h_idx < len(brain.w_ih) and i_idx < len(brain.w_ih[0]):
                        weight = brain.w_ih[h_idx][i_idx]
                        # Only draw connections with significant weights to reduce clutter
                        if abs(weight) > 0.1:
                            start_pos = input_neurons[i_idx]
                            end_pos = hidden_neurons[h_idx]

                            # Determine color based on weight value
                            if weight > 0:
                                conn_color = (100, 180, 100)  # Green for positive
                            else:
                                conn_color = (180, 100, 100)  # Red for negative

                            # Determine thickness based on weight magnitude
                            thickness = max(1, min(3, int(abs(weight) * 5)))

                            pygame.draw.line(screen, conn_color, start_pos, end_pos, thickness)
        except (IndexError, TypeError):
            # If brain structure doesn't match expected format, skip drawing connections
            pass

        try:
            # Hidden -> Output connections
            for o_idx in range(n_outputs):
                for h_idx in range(n_hidden):
                    if hasattr(brain, 'w_ho') and brain.w_ho is not None and \
                       o_idx < len(brain.w_ho) and h_idx < len(brain.w_ho[0]):
                        weight = brain.w_ho[o_idx][h_idx]
                        # Only draw connections with significant weights to reduce clutter
                        if abs(weight) > 0.1:
                            start_pos = hidden_neurons[h_idx]
                            end_pos = output_neurons[o_idx]

                            # Determine color based on weight value
                            if weight > 0:
                                conn_color = (180, 100, 180)  # Purple for positive
                            else:
                                conn_color = (100, 180, 180)  # Cyan for negative

                            # Determine thickness based on weight magnitude
                            thickness = max(1, min(3, int(abs(weight) * 5)))

                            pygame.draw.line(screen, conn_color, start_pos, end_pos, thickness)
        except (IndexError, TypeError):
            # If brain structure doesn't match expected format, skip drawing connections
            pass

        # Draw recurrent connections for RNN if they exist
        try:
            if hasattr(brain, 'w_hh') and brain.w_hh is not None:
                for h_from in range(n_hidden):
                    for h_to in range(n_hidden):
                        if h_from < len(brain.w_hh) and h_to < len(brain.w_hh[0]):
                            weight = brain.w_hh[h_from][h_to]
                            # Only draw significant recurrent connections
                            if abs(weight) > 0.3:  # Higher threshold for recurrent to reduce clutter
                                start_pos = hidden_neurons[h_from]
                                end_pos = hidden_neurons[h_to]

                                # Determine color based on weight value
                                if weight > 0:
                                    conn_color = (100, 100, 180)  # Blue for positive
                                else:
                                    conn_color = (180, 180, 100)  # Yellow for negative

                                # Determine thickness based on weight magnitude
                                thickness = max(1, min(2, int(abs(weight) * 3)))

                                pygame.draw.line(screen, conn_color, start_pos, end_pos, thickness)
        except (IndexError, TypeError):
            # If brain structure doesn't match expected format, skip drawing connections
            pass

        # Draw neurons
        for pos in input_neurons:
            pygame.draw.circle(screen, (80, 180, 80), (int(pos[0]), int(pos[1])), 6)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 6, 1)

        for pos in hidden_neurons:
            pygame.draw.circle(screen, (80, 130, 200), (int(pos[0]), int(pos[1])), 8)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 8, 1)

        for pos in output_neurons:
            pygame.draw.circle(screen, (200, 100, 100), (int(pos[0]), int(pos[1])), 7)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 7, 1)

        # Layer labels
        input_label = self.font_small.render("Input", True, (100, 180, 100))
        hidden_label = self.font_small.render("Hidden", True, (100, 150, 200))
        output_label = self.font_small.render("Output", True, (200, 120, 120))

        screen.blit(input_label, (input_x - 15, y + 5))
        screen.blit(hidden_label, (hidden_x - 20, y + 5))
        screen.blit(output_label, (output_x - 20, y + 5))

    def _draw_scrollbar(self, screen, window_x, content_y, window_width, content_height):
        """Draw a scrollbar on the right side of the content area."""
        scrollbar_width = 12
        scrollbar_x = window_x + window_width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = content_height

        # Draw scrollbar track
        pygame.draw.rect(screen, (45, 48, 55), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        pygame.draw.rect(screen, self.border_color, (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 1)

        # Calculate thumb size and position based on scroll position
        if self.max_scroll > 0:
            thumb_height = max(20, int((content_height / (content_height + self.max_scroll)) * scrollbar_height))
            thumb_y_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            thumb_y = scrollbar_y + int(thumb_y_ratio * (scrollbar_height - thumb_height))

            # Draw scrollbar thumb
            pygame.draw.rect(screen, (100, 150, 200), (scrollbar_x + 2, thumb_y, scrollbar_width - 4, thumb_height))
            pygame.draw.rect(screen, self.border_color, (scrollbar_x + 2, thumb_y, scrollbar_width - 4, thumb_height), 1)

    def handle_scroll(self, direction):
        """Handle scroll input."""
        scroll_amount = 60  # Increased scroll amount for better navigation
        self.scroll_offset += direction * scroll_amount
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))

    def handle_click(self, pos):
        """Handle clicks on the menu."""
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_size()
        window_width = min(1450, screen_width - 30)
        window_height = min(950, screen_height - 30)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        # Check if click is inside the window
        if not (window_x <= pos[0] <= window_x + window_width and
                window_y <= pos[1] <= window_y + window_height):
            return False

        # Check for navigation button clicks
        nav_y = window_y + 35
        num_species = len(self._get_species_data())

        if num_species > 1:  # Only allow navigation if there are multiple species
            # Previous button
            prev_rect = pygame.Rect(window_x + window_width - 150, nav_y, 60, 25)
            if prev_rect.collidepoint(pos):
                self.current_page = max(0, self.current_page - 1)
                return True

            # Next button
            next_rect = pygame.Rect(window_x + window_width - 80, nav_y, 60, 25)
            if next_rect.collidepoint(pos):
                self.current_page = min(num_species - 1, self.current_page + 1)
                return True

        # Check for scrollbar click
        content_y = window_y + 65  # header_height + 5
        content_height = window_height - 75  # window_height - header_height - 10
        scrollbar_width = 12
        scrollbar_x = window_x + window_width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = content_height

        if (scrollbar_x <= pos[0] <= scrollbar_x + scrollbar_width and
            scrollbar_y <= pos[1] <= scrollbar_y + scrollbar_height):
            # Calculate new scroll position based on click
            if self.max_scroll > 0:
                # Calculate the relative position in the scrollbar
                relative_y = (pos[1] - scrollbar_y) / scrollbar_height
                # Calculate new scroll offset
                new_scroll = int(relative_y * self.max_scroll)
                # Apply bounds
                self.scroll_offset = max(0, min(self.max_scroll, new_scroll))
            return True

        return True

    def handle_key_press(self, key):
        """Handle keyboard navigation for species pages."""
        species_data = self._get_species_data()
        species_ids = sorted(species_data.keys())  # Sort by ID for consistent ordering
        num_species = len(species_ids)

        if num_species <= 1:
            return False

        old_page = self.current_page

        if key == pygame.K_LEFT or key == pygame.K_PAGEUP:
            self.current_page = max(0, self.current_page - 1)
        elif key == pygame.K_RIGHT or key == pygame.K_PAGEDOWN:
            # Make sure we don't go past the last species
            self.current_page = min(num_species - 1, self.current_page + 1)
        elif key == pygame.K_HOME:
            self.current_page = 0
        elif key == pygame.K_END:
            self.current_page = num_species - 1 if num_species > 0 else 0
        else:
            return False  # No navigation key pressed

        # Ensure current page is within valid range
        self.current_page = max(0, min(num_species - 1, self.current_page))

        # Return True if the page actually changed
        return self.current_page != old_page