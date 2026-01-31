"""
Main Genetics Visualization module for the simulation.
This module handles the primary genetics menu (G) display functionality.
"""

import pygame
import math
from collections import defaultdict
from src.nn.rnn_brain import RecurrentBrain


class GeneticsVisualization:
    """Enhanced genetics visualization with species info and neural network schematics."""

    def __init__(self, world, settings):
        self.world = world
        self.settings = settings
        self.visible = False
        self.selected_agent = None
        self.selected_species_id = None
        self.scroll_offset = 0
        self.max_scroll = 2000

        # Fonts
        self.font_small = pygame.font.SysFont('monospace', 11)
        self.font_medium = pygame.font.SysFont('monospace', 13)
        self.font_large = pygame.font.SysFont('monospace', 15)
        self.font_title = pygame.font.SysFont('monospace', 18, bold=True)

        # Species names cache
        self.species_names = {}
        self.species_colors = {}

        # Shape types for species
        self.species_shapes = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']

        # UI Colors (matching stats_visualization style)
        self.bg_color = (35, 38, 45)
        self.panel_color = (28, 31, 38)
        self.card_color = (42, 45, 55)
        self.border_color = (70, 75, 85)
        self.text_color = (220, 220, 225)
        self.header_color = (180, 185, 200)
        self.accent_color = (100, 150, 255)
        self.mutation_color = (255, 180, 50)  # Orange/gold for mutations

        # Input/Output labels for NN visualization
        self.input_labels = [
            "food_dx", "food_dy", "water_dx", "water_dy",
            "agent_dx", "agent_dy", "energy", "hydration",
            "nearest_size", "nearest_aggr", "food_dist", "water_dist",
            "agent_dist", "age_ratio", "repro_urge", "velocity"
        ]
        self.output_labels = ["move_x", "move_y", "attack", "mate"]

    def toggle_visibility(self):
        """Toggle the visibility of the genetics menu."""
        self.visible = not self.visible

    def set_selected_agent(self, agent):
        """Set the agent to focus on in the visualization."""
        self.selected_agent = agent
        if agent:
            self.selected_species_id = agent.species_id

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
        """Draw the genetics visualization menu."""
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
        header_height = 40
        pygame.draw.rect(screen, self.panel_color, (window_x, window_y, window_width, header_height))
        pygame.draw.line(screen, self.border_color, (window_x, window_y + header_height),
                        (window_x + window_width, window_y + header_height), 1)

        # Title
        title = self.font_title.render("Genetics & Neural Network Analysis", True, self.accent_color)
        screen.blit(title, (window_x + 15, window_y + 10))

        # Close hint
        close_hint = self.font_small.render("[G] to close | Scroll: Mouse wheel", True, (150, 150, 160))
        screen.blit(close_hint, (window_x + window_width - 220, window_y + 14))

        # Create clipping region for content
        content_y = window_y + header_height + 5
        content_height = window_height - header_height - 10

        # Set clipping rectangle to content area
        clip_rect = pygame.Rect(window_x, content_y, window_width, content_height)
        screen.set_clip(clip_rect)

        # Draw NN architecture info panel at top
        info_panel_height = self._draw_nn_info_panel(screen, window_x + 10, content_y - self.scroll_offset, window_width - 20)

        # Get species data
        species_data = self._get_species_data()

        if not species_data:
            no_data = self.font_medium.render("No living agents in the population", True, (200, 100, 100))
            screen.blit(no_data, (window_x + 20, content_y + info_panel_height + 20))
            screen.set_clip(None)
            return

        # Draw species cards with NN schematics (after info panel)
        self._draw_species_cards(screen, window_x + 10, content_y + info_panel_height + 10 - self.scroll_offset,
                                 window_width - 20, content_height, species_data)

        # Reset clipping
        screen.set_clip(None)

        # Update max scroll based on content
        num_species = len(species_data)
        card_height = 495  # 480 + 15 margin
        total_content_height = info_panel_height + 10 + num_species * card_height
        self.max_scroll = max(0, total_content_height - content_height + 50)

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

                # Get representative agent (one with most mutations for interesting NN)
                rep_agent = max(agents, key=lambda a: a.total_mutations)

                # Calculate mutation hotspots (weights that vary most across species)
                mutation_hotspots = self._calculate_mutation_hotspots(agents)

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
                    'representative': rep_agent,
                    'mutation_hotspots': mutation_hotspots
                }

        # Sort by species_id to keep stable ordering (not by population)
        return dict(sorted(species_data.items(), key=lambda x: x[0]))

    def _draw_nn_info_panel(self, screen, x, y, width):
        """Draw the neural network architecture information panel."""
        panel_height = 240

        # Panel background
        pygame.draw.rect(screen, self.card_color, (x, y, width, panel_height))
        pygame.draw.rect(screen, self.accent_color, (x, y, width, panel_height), 2)

        # Header
        header_rect = pygame.Rect(x, y, width, 32)
        pygame.draw.rect(screen, self.panel_color, header_rect)
        title = self.font_title.render("Neural Network Architecture", True, self.accent_color)
        screen.blit(title, (x + 15, y + 6))

        # Architecture summary
        arch_text = self.font_medium.render("3-Layer Feed-Forward Network: 16 Input -> 6 Hidden (tanh) -> 4 Output (tanh)", True, self.text_color)
        screen.blit(arch_text, (x + 15, y + 40))

        weights_text = self.font_small.render("Total: 130 genetically-encoded weights  (96 input-hidden + 6 hidden bias + 24 hidden-output + 4 output bias)", True, self.header_color)
        screen.blit(weights_text, (x + 15, y + 60))

        # Three columns: Inputs, Hidden, Outputs
        col_width = (width - 40) // 3
        col1_x = x + 15
        col2_x = x + 15 + col_width
        col3_x = x + 15 + col_width * 2

        # Column headers
        row_y = y + 85
        input_header = self.font_medium.render("INPUTS (16)", True, (100, 200, 100))
        hidden_header = self.font_medium.render("HIDDEN (6)", True, (100, 150, 220))
        output_header = self.font_medium.render("OUTPUTS (4)", True, (220, 100, 100))
        screen.blit(input_header, (col1_x, row_y))
        screen.blit(hidden_header, (col2_x, row_y))
        screen.blit(output_header, (col3_x, row_y))

        row_y += 22

        # Input descriptions (in two sub-columns)
        inputs_left = [
            "0: food_dx",
            "1: food_dy",
            "2: water_dx",
            "3: water_dy",
            "4: agent_dx",
            "5: agent_dy",
            "6: energy",
            "7: hydration",
        ]
        inputs_right = [
            "8: nearest_size",
            "9: nearest_aggr",
            "10: food_dist",
            "11: water_dist",
            "12: agent_dist",
            "13: age_ratio",
            "14: repro_urge",
            "15: velocity",
        ]

        line_height = 15
        for i, inp in enumerate(inputs_left):
            text = self.font_small.render(inp, True, (150, 200, 150))
            screen.blit(text, (col1_x, row_y + i * line_height))

        for i, inp in enumerate(inputs_right):
            text = self.font_small.render(inp, True, (150, 200, 150))
            screen.blit(text, (col1_x + 100, row_y + i * line_height))

        # Hidden layer description
        hidden_desc = [
            "6 neurons with",
            "tanh activation",
            "",
            "Processes all",
            "inputs to create",
            "internal state",
            "",
            "96 input weights",
        ]
        for i, line in enumerate(hidden_desc):
            text = self.font_small.render(line, True, (150, 180, 220))
            screen.blit(text, (col2_x, row_y + i * line_height))

        # Output descriptions
        outputs = [
            "0: move_x (-1 to 1)",
            "1: move_y (-1 to 1)",
            "2: attack (>0.5=attack)",
            "3: mate (>0.5=reproduce)",
            "",
            "Behaviors EMERGE",
            "through evolution,",
            "not programmed",
        ]
        for i, out in enumerate(outputs):
            color = (220, 150, 150) if i < 4 else (180, 180, 100)
            text = self.font_small.render(out, True, color)
            screen.blit(text, (col3_x, row_y + i * line_height))

        return panel_height + 10

    def _calculate_mutation_hotspots(self, agents):
        """Calculate which weights vary most across agents in a species."""
        if len(agents) < 2 or not hasattr(agents[0], 'brain'):
            return {}

        # Collect all weights
        all_weights = []
        for agent in agents[:20]:  # Sample up to 20 agents for performance
            if hasattr(agent, 'brain'):
                weights = []
                # Flatten all weights
                for row in agent.brain.w_ih:
                    weights.extend(row)
                weights.extend(agent.brain.b_h)
                for row in agent.brain.w_ho:
                    weights.extend(row)
                weights.extend(agent.brain.b_o)
                all_weights.append(weights)

        if not all_weights:
            return {}

        # Calculate variance for each weight position
        n_weights = len(all_weights[0])
        variances = []
        for i in range(n_weights):
            values = [w[i] for w in all_weights]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            variances.append((i, variance))

        # Get top 10 most variable weights (mutation hotspots)
        variances.sort(key=lambda x: x[1], reverse=True)
        hotspots = {idx: var for idx, var in variances[:15] if var > 0.01}

        return hotspots

    def _draw_species_cards(self, screen, x, y, width, height, species_data):
        """Draw cards for each species with NN schematic."""
        card_height = 480
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
        """Draw a single species card with info, weight stats, and NN schematic."""
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

        # Mutation indicator
        if data['avg_mutations'] > 0:
            mut_text = self.font_small.render(f"Mutations: {data['avg_mutations']:.1f}", True, self.mutation_color)
            screen.blit(mut_text, (x + width - 120, y + 10))

        # === LEFT PANEL: Stats and Weight Heatmap ===
        left_panel_width = 240
        stats_x = x + 12
        stats_y = y + 40

        # Stats section header
        stats_header = self.font_small.render("TRAITS", True, self.accent_color)
        screen.blit(stats_header, (stats_x, stats_y))
        stats_y += 16

        # Compact stats in two columns
        col1_stats = [
            ("Gen", f"{data['avg_generation']:.0f}"),
            ("Age", f"{data['avg_age']:.1f}"),
            ("Speed", f"{data['avg_speed']:.2f}"),
            ("Size", f"{data['avg_size']:.2f}"),
        ]
        col2_stats = [
            ("Aggr", f"{data['avg_aggression']:.2f}"),
            ("Virus", f"{data['avg_virus_resistance']:.2f}"),
            ("Offspr", f"{data['avg_offspring']:.1f}"),
        ]

        for i, (label, value) in enumerate(col1_stats):
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (stats_x, stats_y + i * 16))
            screen.blit(value_text, (stats_x + 50, stats_y + i * 16))

        for i, (label, value) in enumerate(col2_stats):
            label_text = self.font_small.render(f"{label}:", True, self.header_color)
            value_text = self.font_small.render(value, True, self.text_color)
            screen.blit(label_text, (stats_x + 110, stats_y + i * 16))
            screen.blit(value_text, (stats_x + 160, stats_y + i * 16))

        stats_y += max(len(col1_stats), len(col2_stats)) * 16 + 12

        # Add diet and habitat information
        # Get representative agent to access genetic traits
        rep_agent = data['representative']
        if hasattr(rep_agent, 'diet_type'):
            diet_text = self.font_small.render(f"Diet: {rep_agent.diet_type}", True, self.text_color)
            screen.blit(diet_text, (stats_x, stats_y))
            stats_y += 16

        if hasattr(rep_agent, 'habitat_preference'):
            habitat_text = self.font_small.render(f"Habitat: {rep_agent.habitat_preference}", True, self.text_color)
            screen.blit(habitat_text, (stats_x, stats_y))
            stats_y += 16

        # === WEIGHT STATISTICS ===
        if data['representative'] and hasattr(data['representative'], 'brain'):
            brain = data['representative'].brain
            weights = self._get_all_weights(brain)

            # Calculate weight statistics
            active_weights = sum(1 for w in weights if abs(w) > 0.1)
            strong_weights = sum(1 for w in weights if abs(w) > 0.5)
            avg_weight = sum(abs(w) for w in weights) / len(weights) if weights else 0
            max_weight = max(abs(w) for w in weights) if weights else 0

            # Weight stats header
            weight_header = self.font_small.render("NEURAL WEIGHTS", True, self.accent_color)
            screen.blit(weight_header, (stats_x, stats_y))
            stats_y += 16

            # Weight counts
            total_text = self.font_small.render(f"Total: 130", True, self.header_color)
            active_text = self.font_small.render(f"Active (>0.1): {active_weights}", True, (100, 200, 100))
            strong_text = self.font_small.render(f"Strong (>0.5): {strong_weights}", True, (200, 180, 100))
            screen.blit(total_text, (stats_x, stats_y))
            screen.blit(active_text, (stats_x, stats_y + 14))
            screen.blit(strong_text, (stats_x, stats_y + 28))
            stats_y += 48

            # === WEIGHT HEATMAP ===
            heatmap_label = self.font_small.render("Weight Heatmap (130 weights)", True, self.header_color)
            screen.blit(heatmap_label, (stats_x, stats_y))
            stats_y += 16

            # Draw weight heatmap - 13 columns x 10 rows = 130 cells
            heatmap_x = stats_x
            heatmap_y = stats_y
            cell_size = 16
            cols = 13
            rows = 10

            for i, weight in enumerate(weights[:130]):
                row = i // cols
                col = i % cols
                cx = heatmap_x + col * cell_size
                cy = heatmap_y + row * cell_size

                # Color based on weight value
                # Positive = green, Negative = red, Zero = gray
                intensity = min(1.0, abs(weight) / 2.0)
                if weight >= 0:
                    r = int(50 + 50 * (1 - intensity))
                    g = int(80 + 175 * intensity)
                    b = int(50 + 50 * (1 - intensity))
                else:
                    r = int(80 + 175 * intensity)
                    g = int(50 + 50 * (1 - intensity))
                    b = int(50 + 50 * (1 - intensity))

                pygame.draw.rect(screen, (r, g, b), (cx, cy, cell_size - 1, cell_size - 1))

                # Highlight mutation hotspots
                if i in data['mutation_hotspots']:
                    pygame.draw.rect(screen, self.mutation_color, (cx, cy, cell_size - 1, cell_size - 1), 1)

            stats_y += rows * cell_size + 12

            # Heatmap legend - horizontal layout
            legend_y = stats_y

            # Positive
            pygame.draw.rect(screen, (80, 255, 80), (stats_x, legend_y, 10, 10))
            pos_text = self.font_small.render("+", True, (150, 150, 160))
            screen.blit(pos_text, (stats_x + 12, legend_y - 2))

            # Negative
            pygame.draw.rect(screen, (255, 80, 80), (stats_x + 30, legend_y, 10, 10))
            neg_text = self.font_small.render("-", True, (150, 150, 160))
            screen.blit(neg_text, (stats_x + 42, legend_y - 2))

            # Neutral
            pygame.draw.rect(screen, (128, 128, 128), (stats_x + 60, legend_y, 10, 10))
            zero_text = self.font_small.render("0", True, (150, 150, 160))
            screen.blit(zero_text, (stats_x + 72, legend_y - 2))

            # Mutated
            pygame.draw.rect(screen, self.mutation_color, (stats_x + 90, legend_y, 10, 10), 1)
            mut_text = self.font_small.render("mut", True, (150, 150, 160))
            screen.blit(mut_text, (stats_x + 102, legend_y - 2))

        # === RIGHT PANEL: Neural Network Schematic ===
        nn_x = x + left_panel_width + 15
        nn_y = y + 38
        nn_width = width - left_panel_width - 30
        nn_height = height - 50

        # Draw separator line
        pygame.draw.line(screen, self.border_color, (nn_x - 8, y + 35), (nn_x - 8, y + height - 5), 1)

        self._draw_nn_schematic(screen, nn_x, nn_y, nn_width, nn_height,
                               data['representative'], data['mutation_hotspots'], color)

    def _get_all_weights(self, brain):
        """Extract all weights from a brain as a flat list."""
        weights = []
        # Input-hidden weights (16 * 6 = 96)
        for row in brain.w_ih:
            weights.extend(row)
        # Recurrent hidden-hidden weights for RNN (6 * 6 = 36)
        if isinstance(brain, RecurrentBrain) and hasattr(brain, 'w_hh'):
            for row in brain.w_hh:
                weights.extend(row)
        # Hidden biases (6)
        weights.extend(brain.b_h)
        # Hidden-output weights (6 * 4 = 24)
        for row in brain.w_ho:
            weights.extend(row)
        # Output biases (4)
        weights.extend(brain.b_o)
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

    def _draw_nn_schematic(self, screen, x, y, width, height, agent, mutation_hotspots, species_color):
        """Draw a complete neural network schematic with all connections, biases, and weight info."""
        if not agent or not hasattr(agent, 'brain'):
            no_nn = self.font_small.render("No neural network data", True, (150, 150, 160))
            screen.blit(no_nn, (x + 20, y + 20))
            return

        brain = agent.brain

        # Layout parameters - more space for labels
        left_margin = 60
        right_margin = 55
        top_margin = 25
        bottom_margin = 45

        # Three columns for layers
        usable_width = width - left_margin - right_margin
        layer_spacing = usable_width // 2

        # Neuron positions
        input_x = x + left_margin
        hidden_x = x + left_margin + layer_spacing
        output_x = x + left_margin + usable_width

        # Calculate neuron Y positions
        input_neurons = []
        hidden_neurons = []
        output_neurons = []

        n_inputs = 16
        n_hidden = 6
        n_outputs = 4

        usable_height = height - top_margin - bottom_margin

        # Spread neurons vertically with proper centering
        input_spacing = usable_height / (n_inputs + 1)
        hidden_spacing = usable_height / (n_hidden + 1)
        output_spacing = usable_height / (n_outputs + 1)

        for i in range(n_inputs):
            input_neurons.append((input_x, y + top_margin + (i + 1) * input_spacing))

        for i in range(n_hidden):
            hidden_neurons.append((hidden_x, y + top_margin + (i + 1) * hidden_spacing))

        for i in range(n_outputs):
            output_neurons.append((output_x, y + top_margin + (i + 1) * output_spacing))

        # === DRAW ALL CONNECTIONS ===
        # Draw in order: weak connections first, then strong, then mutated on top

        # Collect all connections with their properties
        all_connections = []

        # Input -> Hidden connections (96 weights)
        for h_idx in range(n_hidden):
            for i_idx in range(n_inputs):
                weight_idx = h_idx * n_inputs + i_idx
                weight = brain.w_ih[h_idx][i_idx]
                is_mutated = weight_idx in mutation_hotspots
                variance = mutation_hotspots.get(weight_idx, 0)
                all_connections.append({
                    'start': input_neurons[i_idx],
                    'end': hidden_neurons[h_idx],
                    'weight': weight,
                    'idx': weight_idx,
                    'is_mutated': is_mutated,
                    'variance': variance,
                    'layer': 'ih'
                })

        # Hidden -> Output connections (24 weights)
        # For FNN: base_idx = 96 + 6 = 102
        # For RNN: base_idx = 96 + 36 + 6 = 138 (after recurrent weights)
        is_rnn = isinstance(brain, RecurrentBrain)
        if is_rnn:
            base_idx = 96 + 36 + 6  # After input-hidden, recurrent, and hidden biases
        else:
            base_idx = 96 + 6  # After input-hidden and hidden biases
        for o_idx in range(n_outputs):
            for h_idx in range(n_hidden):
                weight_idx = base_idx + o_idx * n_hidden + h_idx
                weight = brain.w_ho[o_idx][h_idx]
                is_mutated = weight_idx in mutation_hotspots
                variance = mutation_hotspots.get(weight_idx, 0)
                all_connections.append({
                    'start': hidden_neurons[h_idx],
                    'end': output_neurons[o_idx],
                    'weight': weight,
                    'idx': weight_idx,
                    'is_mutated': is_mutated,
                    'variance': variance,
                    'layer': 'ho'
                })

        # Sort connections: weak first, then strong, then mutated
        all_connections.sort(key=lambda c: (c['is_mutated'], abs(c['weight'])))

        # Draw all connections
        for conn in all_connections:
            self._draw_weight_connection_v2(screen, conn['start'], conn['end'],
                                           conn['weight'], conn['is_mutated'],
                                           conn['variance'], conn['layer'])

        # === DRAW RECURRENT CONNECTIONS (RNN only) ===
        if is_rnn and hasattr(brain, 'w_hh'):
            # Draw self-loops on each hidden neuron
            for h_idx, h_pos in enumerate(hidden_neurons):
                weight = brain.w_hh[h_idx][h_idx]  # Self-connection
                if abs(weight) < 0.05:
                    continue

                cx, cy = int(h_pos[0]), int(h_pos[1])

                # Color based on weight sign
                if weight >= 0:
                    color = (120, 80, 180)  # Purple for positive
                else:
                    color = (180, 80, 140)  # Magenta for negative

                thickness = max(1, min(2, int(abs(weight) * 2)))

                # Draw small self-loop arc on the right side of neuron
                loop_r = 8
                arc_points = []
                for angle in range(-60, 240, 20):
                    rad = math.radians(angle)
                    px = cx + 12 + int(loop_r * math.cos(rad))
                    py = cy + int(loop_r * math.sin(rad))
                    arc_points.append((px, py))

                if len(arc_points) > 1:
                    pygame.draw.lines(screen, color, False, arc_points, thickness)
                    # Small arrowhead
                    end_pt = arc_points[-1]
                    pygame.draw.circle(screen, color, end_pt, 2)

            # Draw curved connections between different hidden neurons (only strong ones)
            for h_from in range(n_hidden):
                for h_to in range(n_hidden):
                    if h_from == h_to:
                        continue  # Skip self-connections (already drawn)

                    weight = brain.w_hh[h_from][h_to]
                    if abs(weight) < 0.25:  # Only show stronger connections
                        continue

                    start_pos = hidden_neurons[h_from]
                    end_pos = hidden_neurons[h_to]

                    # Color based on weight sign
                    if weight >= 0:
                        color = (100, 70, 160)
                    else:
                        color = (160, 70, 120)

                    thickness = max(1, min(2, int(abs(weight) * 1.5)))

                    sx, sy = int(start_pos[0]) + 12, int(start_pos[1])
                    ex, ey = int(end_pos[0]) + 12, int(end_pos[1])

                    # Draw curved line bulging to the right
                    mid_x = max(sx, ex) + 15 + abs(h_from - h_to) * 4
                    mid_y = (sy + ey) // 2

                    # Quadratic bezier
                    points = []
                    for t in [i / 8.0 for i in range(9)]:
                        bx = (1-t)**2 * sx + 2*(1-t)*t * mid_x + t**2 * ex
                        by = (1-t)**2 * sy + 2*(1-t)*t * mid_y + t**2 * ey
                        points.append((int(bx), int(by)))

                    if len(points) > 1:
                        pygame.draw.lines(screen, color, False, points, thickness)

            # === DRAW RNN DETAIL PANEL (Zoom View) ===
            # Position the panel to the right of the main schematic
            panel_x = x + width - 95
            panel_y = y + 25
            panel_w = 88
            panel_h = 110

            # Panel background
            pygame.draw.rect(screen, (38, 42, 52), (panel_x, panel_y, panel_w, panel_h), border_radius=4)
            pygame.draw.rect(screen, (100, 80, 160), (panel_x, panel_y, panel_w, panel_h), 1, border_radius=4)

            # Panel title
            title = self.font_small.render("RECURRENT", True, (140, 120, 180))
            screen.blit(title, (panel_x + 12, panel_y + 3))

            # Draw 6x6 weight matrix visualization
            matrix_x = panel_x + 8
            matrix_y = panel_y + 18
            cell_size = 12

            # Matrix labels
            from_label = self.font_small.render("from", True, (100, 100, 110))
            to_label = self.font_small.render("to", True, (100, 100, 110))
            screen.blit(from_label, (matrix_x + cell_size * 3 - 8, matrix_y - 1))

            # Draw the 6x6 grid with color-coded weights
            for i in range(n_hidden):
                for j in range(n_hidden):
                    weight = brain.w_hh[i][j]
                    cx = matrix_x + j * cell_size + cell_size // 2
                    cy = matrix_y + 12 + i * cell_size + cell_size // 2

                    # Color intensity based on weight magnitude
                    intensity = min(1.0, abs(weight) * 1.5)

                    if abs(weight) < 0.1:
                        # Very weak - dark gray
                        color = (50, 50, 55)
                    elif weight >= 0:
                        # Positive - blue/purple
                        color = (
                            int(50 + 70 * intensity),
                            int(50 + 50 * intensity),
                            int(80 + 120 * intensity)
                        )
                    else:
                        # Negative - red/magenta
                        color = (
                            int(80 + 120 * intensity),
                            int(50 + 30 * intensity),
                            int(60 + 80 * intensity)
                        )

                    # Draw cell
                    pygame.draw.rect(screen, color,
                                   (cx - cell_size//2 + 1, cy - cell_size//2 + 1,
                                    cell_size - 2, cell_size - 2))

                    # Highlight diagonal (self-connections)
                    if i == j:
                        pygame.draw.rect(screen, (180, 150, 200),
                                       (cx - cell_size//2 + 1, cy - cell_size//2 + 1,
                                        cell_size - 2, cell_size - 2), 1)

            # Draw grid lines
            for i in range(n_hidden + 1):
                # Horizontal
                pygame.draw.line(screen, (60, 60, 70),
                               (matrix_x, matrix_y + 12 + i * cell_size),
                               (matrix_x + n_hidden * cell_size, matrix_y + 12 + i * cell_size), 1)
                # Vertical
                pygame.draw.line(screen, (60, 60, 70),
                               (matrix_x + i * cell_size, matrix_y + 12),
                               (matrix_x + i * cell_size, matrix_y + 12 + n_hidden * cell_size), 1)

            # Row/column indices
            for i in range(n_hidden):
                idx_text = self.font_small.render(str(i), True, (90, 90, 100))
                # Column header
                screen.blit(idx_text, (matrix_x + i * cell_size + 4, matrix_y + 2))
                # Row header (on left)
                screen.blit(idx_text, (matrix_x - 9, matrix_y + 14 + i * cell_size))

            # Legend for matrix
            leg_y = matrix_y + n_hidden * cell_size + 16
            pygame.draw.rect(screen, (80, 70, 150), (panel_x + 8, leg_y, 8, 8))
            pos_txt = self.font_small.render("+", True, (120, 120, 130))
            screen.blit(pos_txt, (panel_x + 18, leg_y - 2))

            pygame.draw.rect(screen, (150, 60, 100), (panel_x + 32, leg_y, 8, 8))
            neg_txt = self.font_small.render("-", True, (120, 120, 130))
            screen.blit(neg_txt, (panel_x + 42, leg_y - 2))

            pygame.draw.rect(screen, (50, 50, 55), (panel_x + 54, leg_y, 8, 8))
            zero_txt = self.font_small.render("~0", True, (120, 120, 130))
            screen.blit(zero_txt, (panel_x + 64, leg_y - 2))

        # === DRAW BIAS INDICATORS ===
        # Hidden biases: FNN indices 96-101, RNN indices 132-137 (after recurrent)
        hidden_bias_start = 96 + 36 if is_rnn else 96
        for h_idx, h_pos in enumerate(hidden_neurons):
            bias_idx = hidden_bias_start + h_idx
            bias_val = brain.b_h[h_idx]
            is_mutated = bias_idx in mutation_hotspots

            # Draw small bias indicator above neuron
            bias_y = h_pos[1] - 15
            bias_x = h_pos[0]

            # Color based on bias value
            if abs(bias_val) > 0.1:
                if bias_val > 0:
                    bias_color = (80, 200, 80) if not is_mutated else self.mutation_color
                else:
                    bias_color = (200, 80, 80) if not is_mutated else self.mutation_color

                # Draw bias arrow/indicator
                pygame.draw.line(screen, bias_color, (bias_x, bias_y + 8), (bias_x, bias_y + 2), 2)
                pygame.draw.polygon(screen, bias_color, [
                    (bias_x, bias_y),
                    (bias_x - 3, bias_y + 4),
                    (bias_x + 3, bias_y + 4)
                ])

        # Output biases: FNN indices 126-129, RNN indices 162-165
        output_bias_start = hidden_bias_start + 6 + 24
        for o_idx, o_pos in enumerate(output_neurons):
            bias_idx = output_bias_start + o_idx
            bias_val = brain.b_o[o_idx]
            is_mutated = bias_idx in mutation_hotspots

            if abs(bias_val) > 0.1:
                bias_y = o_pos[1] - 15
                bias_x = o_pos[0]

                if bias_val > 0:
                    bias_color = (80, 200, 80) if not is_mutated else self.mutation_color
                else:
                    bias_color = (200, 80, 80) if not is_mutated else self.mutation_color

                pygame.draw.line(screen, bias_color, (bias_x, bias_y + 8), (bias_x, bias_y + 2), 2)
                pygame.draw.polygon(screen, bias_color, [
                    (bias_x, bias_y),
                    (bias_x - 3, bias_y + 4),
                    (bias_x + 3, bias_y + 4)
                ])

        # === DRAW NEURONS ===
        # Input neurons with labels
        for i, pos in enumerate(input_neurons):
            is_mutated = any(i + h * n_inputs in mutation_hotspots for h in range(n_hidden))
            color = self.mutation_color if is_mutated else (80, 180, 80)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 6)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 6, 1)

            # Full input label on left
            if i < len(self.input_labels):
                label = self.input_labels[i][:8]  # 8 chars max
                label_text = self.font_small.render(label, True, (150, 180, 150))
                screen.blit(label_text, (pos[0] - 55, pos[1] - 5))

        # Hidden neurons with activation values
        for i, pos in enumerate(hidden_neurons):
            is_mutated = self._is_hidden_neuron_mutated(i, mutation_hotspots, brain)
            color = self.mutation_color if is_mutated else (80, 130, 200)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 10)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 10, 1)

            # Neuron index inside
            idx_text = self.font_small.render(str(i), True, (255, 255, 255))
            screen.blit(idx_text, (pos[0] - 3, pos[1] - 5))

        # Output neurons with labels
        for i, pos in enumerate(output_neurons):
            bias_idx = 96 + 6 + 24 + i
            is_mutated = bias_idx in mutation_hotspots
            color = self.mutation_color if is_mutated else (200, 100, 100)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 9)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 9, 1)

            # Output label on right
            if i < len(self.output_labels):
                label = self.output_labels[i]
                label_text = self.font_small.render(label, True, (200, 150, 150))
                screen.blit(label_text, (pos[0] + 14, pos[1] - 5))

        # === LAYER LABELS ===
        input_label = self.font_medium.render("INPUT", True, (100, 180, 100))
        hidden_label = self.font_medium.render("HIDDEN", True, (100, 150, 200))
        output_label = self.font_medium.render("OUTPUT", True, (200, 120, 120))

        screen.blit(input_label, (input_x - 22, y + 5))
        screen.blit(hidden_label, (hidden_x - 25, y + 5))
        screen.blit(output_label, (output_x - 25, y + 5))

        # === LEGEND ===
        legend_y = y + height - 40
        legend_x = x + 5

        # Positive weight
        pygame.draw.line(screen, (100, 180, 100), (legend_x, legend_y), (legend_x + 20, legend_y), 2)
        pos_text = self.font_small.render("+weight", True, (150, 150, 160))
        screen.blit(pos_text, (legend_x + 25, legend_y - 5))

        # Negative weight
        pygame.draw.line(screen, (180, 100, 100), (legend_x, legend_y + 14), (legend_x + 20, legend_y + 14), 2)
        neg_text = self.font_small.render("-weight", True, (150, 150, 160))
        screen.blit(neg_text, (legend_x + 25, legend_y + 9))

        # Mutation indicator
        pygame.draw.circle(screen, self.mutation_color, (legend_x + 100, legend_y + 7), 5)
        mut_text = self.font_small.render("mutation", True, (150, 150, 160))
        screen.blit(mut_text, (legend_x + 110, legend_y + 2))

        # Bias indicator
        pygame.draw.polygon(screen, (150, 150, 200), [
            (legend_x + 175, legend_y),
            (legend_x + 172, legend_y + 6),
            (legend_x + 178, legend_y + 6)
        ])
        bias_text = self.font_small.render("bias", True, (150, 150, 160))
        screen.blit(bias_text, (legend_x + 182, legend_y + 2))

        # Recurrent indicator (RNN only)
        if is_rnn:
            # Draw self-loop symbol
            rx, ry = legend_x + 210, legend_y + 7
            pygame.draw.arc(screen, (120, 80, 180), (rx - 4, ry - 6, 10, 10), 0.3, 5.5, 2)
            pygame.draw.circle(screen, (120, 80, 180), (rx + 5, ry - 3), 2)
            rec_text = self.font_small.render("self-loop", True, (150, 150, 160))
            screen.blit(rec_text, (legend_x + 225, legend_y + 2))

        # Weight count summary with architecture info
        weights = self._get_all_weights(brain)
        strong = sum(1 for w in weights if abs(w) > 0.5)
        total_weights = 166 if is_rnn else 130
        nn_type = "RNN" if is_rnn else "FNN"
        if is_rnn:
            # Count strong recurrent weights
            recurrent_weights = [brain.w_hh[i][j] for i in range(6) for j in range(6)]
            strong_rec = sum(1 for w in recurrent_weights if abs(w) > 0.3)
            summary = self.font_small.render(f"RNN: {total_weights} weights (36 recurrent, {strong_rec} active)", True, (120, 120, 130))
        else:
            summary = self.font_small.render(f"FNN: {total_weights} weights | Strong (>0.5): {strong}", True, (120, 120, 130))
        screen.blit(summary, (x + width - 285, legend_y + 20))

    def _draw_weight_connection_v2(self, screen, start, end, weight, is_mutated, variance, layer):
        """Draw a connection with proper styling based on weight value and mutation status."""
        abs_weight = abs(weight)

        # Skip very weak connections to reduce visual noise
        if abs_weight < 0.05 and not is_mutated:
            return

        # Determine line thickness based on weight magnitude
        if abs_weight < 0.2:
            thickness = 1
            alpha = 40
        elif abs_weight < 0.5:
            thickness = 1
            alpha = 80
        elif abs_weight < 1.0:
            thickness = 2
            alpha = 150
        else:
            thickness = 3
            alpha = 200

        # Determine color based on weight sign
        if is_mutated:
            color = self.mutation_color
            thickness = max(2, thickness)
            alpha = 255
        elif weight >= 0:
            color = (100, 180, 100)  # Green for positive
        else:
            color = (180, 100, 100)  # Red for negative

        # Draw the connection
        # For transparency effect, draw lighter version first
        if not is_mutated and alpha < 150:
            # Blend color towards background for weak connections
            blend = alpha / 255
            bg = (42, 45, 55)
            blended = (
                int(color[0] * blend + bg[0] * (1 - blend)),
                int(color[1] * blend + bg[1] * (1 - blend)),
                int(color[2] * blend + bg[2] * (1 - blend))
            )
            pygame.draw.line(screen, blended, start, end, thickness)
        else:
            pygame.draw.line(screen, color, start, end, thickness)

            # For strong or mutated connections, add glow effect
            if abs_weight > 0.8 or is_mutated:
                glow_color = (
                    min(255, color[0] + 30),
                    min(255, color[1] + 30),
                    min(255, color[2] + 30)
                )
                pygame.draw.line(screen, glow_color, start, end, thickness + 1)

    def _is_hidden_neuron_mutated(self, h_idx, mutation_hotspots, brain):
        """Check if a hidden neuron has mutated connections."""
        is_rnn = isinstance(brain, RecurrentBrain)

        # Check input connections to this hidden neuron
        for i in range(16):
            idx = h_idx * 16 + i
            if idx in mutation_hotspots:
                return True

        # Check recurrent connections for RNN
        if is_rnn:
            for h_from in range(6):
                idx = 96 + h_from * 6 + h_idx  # Connection from h_from to h_idx
                if idx in mutation_hotspots:
                    return True
                idx = 96 + h_idx * 6 + h_from  # Connection from h_idx to h_from
                if idx in mutation_hotspots:
                    return True

        # Check hidden bias (different index for RNN)
        bias_start = 96 + 36 if is_rnn else 96
        bias_idx = bias_start + h_idx
        if bias_idx in mutation_hotspots:
            return True

        # Check output connections from this hidden neuron
        base_idx = bias_start + 6  # After hidden biases
        for o in range(4):
            idx = base_idx + o * 6 + h_idx
            if idx in mutation_hotspots:
                return True

        return False

    def handle_scroll(self, direction):
        """Handle scroll input."""
        scroll_amount = 40
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
        if (window_x <= pos[0] <= window_x + window_width and
            window_y <= pos[1] <= window_y + window_height):
            return True
        return False