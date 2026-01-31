"""
Agent Info Window module for the simulation.
This module handles the agent info window that appears when clicking on an agent.
"""

import pygame
import math
from src.nn.rnn_brain import RecurrentBrain
from .creatures_menu import CreatureSaver


class AgentInfoWindow:
    """Agent info window that appears when clicking on an agent during simulation."""

    def __init__(self, world, settings):
        self.world = world
        self.settings = settings
        self.visible = False
        self.selected_agent = None

        # Position and size (increased size for better layout - 50% taller)
        self.window_width = 1200
        self.window_height = 1350

        # Store agent names persistently
        self.agent_names = {}

        # Creature saver instance
        self.creature_saver = CreatureSaver()

        # Fonts
        self.font_tiny = pygame.font.SysFont('monospace', 9)
        self.font_small = pygame.font.SysFont('monospace', 11)
        self.font_medium = pygame.font.SysFont('monospace', 13)
        self.font_large = pygame.font.SysFont('monospace', 15)
        self.font_title = pygame.font.SysFont('monospace', 18, bold=True)

        # UI Colors (matching genetics visualization style)
        self.bg_color = (35, 38, 45)
        self.panel_color = (28, 31, 38)
        self.card_color = (42, 45, 55)
        self.border_color = (70, 75, 85)
        self.text_color = (220, 220, 225)
        self.header_color = (180, 185, 200)
        self.accent_color = (100, 150, 255)
        self.mutation_color = (255, 180, 50)  # Orange/gold for mutations

        # Input/Output labels for NN visualization (same as in genetics menu)
        self.input_labels = [
            "food_dx", "food_dy", "water_dx", "water_dy",
            "agent_dx", "agent_dy", "energy", "hydration",
            "nearest_size", "nearest_aggr", "food_dist", "water_dist",
            "agent_dist", "age_ratio", "repro_urge", "velocity"
        ]
        self.output_labels = ["move_x", "move_y", "attack", "mate"]

    def set_selected_agent(self, agent):
        """Set the agent to display in the info window."""
        self.selected_agent = agent
        if agent:
            self.visible = True
        else:
            self.visible = False

    def toggle_visibility(self):
        """Toggle the visibility of the agent info window."""
        self.visible = not self.visible
        if not self.visible:
            self.selected_agent = None

    def is_clicked(self, pos):
        """Check if the click is inside the window."""
        if not self.visible or not self.selected_agent:
            return False

        return (self.window_x <= pos[0] <= self.window_x + self.window_width and
                self.window_y <= pos[1] <= self.window_y + self.window_height)

    def handle_click_outside(self, pos):
        """Hide the window if clicked outside."""
        if self.visible and not self.is_clicked(pos):
            self.visible = False
            self.selected_agent = None

    def draw(self, screen):
        """Draw the agent info window."""
        if not self.visible or not self.selected_agent:
            return

        # Check if the selected agent is still alive
        if not self.selected_agent.alive:
            self.visible = False
            return

        # Center the window on the screen
        screen_width, screen_height = screen.get_size()
        self.window_x = (screen_width - self.window_width) // 2
        self.window_y = (screen_height - self.window_height) // 2

        # Draw window background with shadow
        pygame.draw.rect(screen, (20, 20, 25), (self.window_x + 5, self.window_y + 5, self.window_width, self.window_height))
        pygame.draw.rect(screen, self.bg_color, (self.window_x, self.window_y, self.window_width, self.window_height))
        pygame.draw.rect(screen, self.border_color, (self.window_x, self.window_y, self.window_width, self.window_height), 2)

        # Header bar
        header_height = 70
        pygame.draw.rect(screen, self.panel_color, (self.window_x, self.window_y, self.window_width, header_height))
        pygame.draw.line(screen, self.border_color, (self.window_x, self.window_y + header_height),
                        (self.window_x + self.window_width, self.window_y + header_height), 1)

        # Title
        title = self.font_title.render("Agent Information", True, self.accent_color)
        screen.blit(title, (self.window_x + 15, self.window_y + 10))

        # Subtitle with agent ID, generation, and funny name
        agent_name = self._get_agent_name(self.selected_agent.id)
        subtitle = self.font_medium.render(f"ID: {self.selected_agent.id} | Generation: {self.selected_agent.generation}", True, self.text_color)
        name_subtitle = self.font_large.render(f"Name: {agent_name}", True, self.accent_color)
        screen.blit(subtitle, (self.window_x + 15, self.window_y + 30))
        screen.blit(name_subtitle, (self.window_x + 15, self.window_y + 50))

        # Save button
        save_button_rect = pygame.Rect(self.window_x + self.window_width - 150, self.window_y + 10, 60, 25)
        pygame.draw.rect(screen, self.panel_color, save_button_rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, save_button_rect, 1, border_radius=3)
        save_text = self.font_small.render("Save", True, self.text_color)
        screen.blit(save_text, (save_button_rect.centerx - save_text.get_width() // 2,
                               save_button_rect.centery - save_text.get_height() // 2))

        # Close hint
        close_hint = self.font_small.render("[ESC] to close", True, (150, 150, 160))
        screen.blit(close_hint, (self.window_x + self.window_width - 100, self.window_y + 14))

        # Content area
        content_y = self.window_y + header_height + 5
        content_height = self.window_height - header_height - 10

        # Draw agent stats
        self._draw_agent_stats(screen, self.window_x + 10, content_y, self.window_width - 20, content_height)

    def _draw_agent_stats(self, screen, x, y, width, height):
        """Draw agent statistics and neural network schematic."""
        agent = self.selected_agent
        if not agent:
            return

        # Species info
        species_name = self._get_species_name(agent.species_id)
        species_text = self.font_medium.render(f"Species: {species_name}", True, self.get_species_color(agent.species_id))
        screen.blit(species_text, (x, y))

        # Organize stats in a grid layout (4 columns)
        stats_y = y + 25
        all_stats = [
            ("Energy", f"{agent.energy:.1f}/{self.settings.get('MAX_ENERGY', 300.0):.0f}"),
            ("Hydration", f"{agent.hydration:.1f}/{self.settings.get('MAX_HYDRATION', 150.0):.0f}"),
            ("Age", f"{agent.age:.1f}/{agent.max_age:.1f}"),
            ("Max Age", f"{agent.max_age:.1f}"),
            ("Size", f"{agent.size:.2f}"),
            ("Speed", f"{agent.speed:.2f}"),
            ("Vision", f"{agent.vision_range:.1f}"),
            ("Aggression", f"{agent.aggression:.2f}"),
            ("Efficiency", f"{agent.efficiency:.2f}"),
            ("Offspring", f"{agent.offspring_count}"),
            ("Mutations", f"{agent.total_mutations}"),
            ("Virus Res", f"{agent.virus_resistance:.2f}"),
            ("Armor", f"{agent.armor:.2f}"),
            ("Agility", f"{agent.agility:.2f}"),
            ("Diet", f"{agent.diet_type}"),
            ("Habitat", f"{agent.habitat_preference}"),
        ]

        # Define layout parameters
        col_width = width // 4  # 4 columns
        row_height = 20
        cols = 4
        rows = (len(all_stats) + cols - 1) // cols  # Calculate rows needed

        # Draw stats in a grid
        for i, (label, value) in enumerate(all_stats):
            col = i % cols
            row = i // cols

            pos_x = x + col * col_width
            pos_y = stats_y + row * row_height

            label_text = self.font_medium.render(f"{label}:", True, self.header_color)
            value_text = self.font_medium.render(value, True, self.text_color)

            screen.blit(label_text, (pos_x, pos_y))
            screen.blit(value_text, (pos_x + 70, pos_y))

        # Calculate where to place the neural network schematic after the stats grid
        stats_grid_rows = rows
        nn_y = stats_y + stats_grid_rows * row_height + 20  # Add some padding

        # Neural network schematic
        self._draw_nn_schematic(screen, x, nn_y, width, 500, agent)  # Significantly increased height

        # Draw behavioral stats and graphs after the neural network
        behavior_y = nn_y + 510  # Increased to match new height
        self._draw_behavioral_stats(screen, x, behavior_y, width, height - (behavior_y - y) - 10, agent)

    def _get_agent_name(self, agent_id):
        """Get a random funny name for an agent, storing it persistently."""
        if agent_id not in self.agent_names:
            # Funny animal names
            funny_names = [
                "Sir Wiggles", "Lady Fluffernutter", "Captain Niblet", "Princess Snugglebottom",
                "Baron Von Woofington", "Duchess Quackers", "Lord Whiskersworth", "Miss Bumblebee",
                "Professor Paws", "Dr. Meowington", "General Fluff", "Colonel Featherbottom",
                "Sergeant Biscuit", "Private Pickles", "Master Mischief", "Count Cuddles",
                "Dame Sparkles", "Mr. Jingles", "Ms. Ticklefeet", "Lord Lollipop",
                "Baroness Bingleberry", "Sir Snuggles", "Lady Wigglebutt", "Captain Chaos",
                "Princess Puddles", "Duke Doodle", "Queen Quacksworth", "Emperor Earwig",
                "King Kibble", "Prince Puff", "Princess Poppycock", "Earl Errington",
                "Countess Confetti", "Sir Sirloin", "Lady Larks", "Baron Bingle",
                "Duchess Dillydally", "Lord Larkspur", "Miss Mayhem", "Mr. Muffin",
                "Ms. Muffet", "Dr. Dilly", "Professor Piddle", "General Giggles",
                "Colonel Cuddles", "Sergeant Snickerdoodle", "Private Peanuts", "Master Mischief",
                "Count Confetti", "Dame Doodles", "Sir Snugglewumps", "Lady Larkspur"
            ]

            import random
            self.agent_names[agent_id] = random.choice(funny_names)

        return self.agent_names[agent_id]

    def _get_species_name(self, species_id):
        """Get a human-readable name for a species ID - Italian medieval names."""
        italian_medieval_names = [
            "Visconti", "Medici", "Este", "Sforza", "Gonzaga", "Farnese", "Pico", "Borgia",
            "Malatesta", "Montefeltro", "Doria", "Grimaldi", "Cybo", "Colonna", "Orsini",
            "Gentile", "Alberti", "Pazzi", "Salviati", "Rucellai", "Albizzi", "Capponi"
        ]
        return italian_medieval_names[species_id % len(italian_medieval_names)]

    def get_species_color(self, species_id):
        """Get a color for a species using golden angle distribution."""
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

        return (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )

    def _draw_nn_schematic(self, screen, x, y, width, height, agent):
        """Draw a neural network schematic for the selected agent."""
        if not agent or not hasattr(agent, 'brain'):
            no_nn = self.font_small.render("No neural network data", True, (150, 150, 160))
            screen.blit(no_nn, (x + 20, y + 20))
            return

        brain = agent.brain

        # Layout parameters - more compact for the agent info window
        left_margin = 40
        right_margin = 35
        top_margin = 15
        bottom_margin = 25

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

        usable_height = min(height - top_margin - bottom_margin, 500)  # Increased height for better layout

        # Spread neurons vertically with proper centering
        input_spacing = usable_height / (n_inputs + 1) if n_inputs > 0 else 0
        hidden_spacing = usable_height / (n_hidden + 1) if n_hidden > 0 else 0
        output_spacing = usable_height / (n_outputs + 1) if n_outputs > 0 else 0

        for i in range(n_inputs):
            input_neurons.append((input_x, y + top_margin + (i + 1) * input_spacing))

        for i in range(n_hidden):
            hidden_neurons.append((hidden_x, y + top_margin + (i + 1) * hidden_spacing))

        for i in range(n_outputs):
            output_neurons.append((output_x, y + top_margin + (i + 1) * output_spacing))

        # Draw connections
        # Input -> Hidden connections
        try:
            for h_idx in range(n_hidden):
                for i_idx in range(n_inputs):
                    if hasattr(brain, 'w_ih') and brain.w_ih is not None and \
                       h_idx < len(brain.w_ih) and i_idx < len(brain.w_ih[0]):
                        weight = brain.w_ih[h_idx][i_idx]
                        self._draw_weight_connection(screen, input_neurons[i_idx], hidden_neurons[h_idx], weight)
        except (IndexError, TypeError):
            # Handle cases where brain structure doesn't match expected format
            pass

        # Hidden -> Output connections
        try:
            for o_idx in range(n_outputs):
                for h_idx in range(n_hidden):
                    if hasattr(brain, 'w_ho') and brain.w_ho is not None and \
                       o_idx < len(brain.w_ho) and h_idx < len(brain.w_ho[0]):
                        weight = brain.w_ho[o_idx][h_idx]
                        self._draw_weight_connection(screen, hidden_neurons[h_idx], output_neurons[o_idx], weight)
        except (IndexError, TypeError):
            # Handle cases where brain structure doesn't match expected format
            pass

        # Draw recurrent connections for RNN
        try:
            if hasattr(brain, 'w_hh') and brain.w_hh is not None:
                for h_from in range(n_hidden):
                    for h_to in range(n_hidden):
                        if h_from < len(brain.w_hh) and h_to < len(brain.w_hh[0]):
                            weight = brain.w_hh[h_from][h_to]
                            if abs(weight) > 0.1:  # Only draw significant recurrent connections
                                self._draw_weight_connection(screen, hidden_neurons[h_from], hidden_neurons[h_to], weight)
        except (IndexError, TypeError):
            # Handle cases where brain structure doesn't match expected format
            pass

        # Draw neurons
        # Input neurons with labels
        for i, pos in enumerate(input_neurons):
            color = (80, 180, 80)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 5)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 5, 1)

            # Full input label on left
            if i < len(self.input_labels):
                label = self.input_labels[i][:10]  # 10 chars max to fit better
                label_text = self.font_small.render(label, True, (150, 180, 150))
                screen.blit(label_text, (pos[0] - 70, pos[1] - 5))

        # Hidden neurons
        for i, pos in enumerate(hidden_neurons):
            color = (80, 130, 200)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 8)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 8, 1)

            # Neuron index inside
            idx_text = self.font_small.render(str(i), True, (255, 255, 255))
            screen.blit(idx_text, (pos[0] - 3, pos[1] - 5))

        # Output neurons with labels
        for i, pos in enumerate(output_neurons):
            color = (200, 100, 100)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 7)
            pygame.draw.circle(screen, (220, 220, 220), (int(pos[0]), int(pos[1])), 7, 1)

            # Output label on right
            if i < len(self.output_labels):
                label = self.output_labels[i]
                label_text = self.font_small.render(label, True, (200, 150, 150))
                screen.blit(label_text, (pos[0] + 10, pos[1] - 5))

        # Layer labels
        input_label = self.font_medium.render("INPUT", True, (100, 180, 100))
        hidden_label = self.font_medium.render("HIDDEN", True, (100, 150, 200))
        output_label = self.font_medium.render("OUTPUT", True, (200, 120, 120))

        screen.blit(input_label, (input_x - 22, y + 5))
        screen.blit(hidden_label, (hidden_x - 25, y + 5))
        screen.blit(output_label, (output_x - 25, y + 5))

    def _draw_weight_connection(self, screen, start, end, weight):
        """Draw a connection with proper styling based on weight value."""
        abs_weight = abs(weight)

        # Skip very weak connections to reduce visual noise
        if abs_weight < 0.05:
            return

        # Determine line thickness based on weight magnitude
        if abs_weight < 0.2:
            thickness = 1
        elif abs_weight < 0.5:
            thickness = 1
        elif abs_weight < 1.0:
            thickness = 2
        else:
            thickness = 3

        # Determine color based on weight sign
        if weight >= 0:
            color = (100, 180, 100)  # Green for positive
        else:
            color = (180, 100, 100)  # Red for negative

        # Draw the connection
        pygame.draw.line(screen, color, start, end, thickness)

        # For strong connections, add glow effect
        if abs_weight > 0.8:
            glow_color = (
                min(255, color[0] + 30),
                min(255, color[1] + 30),
                min(255, color[2] + 30)
            )
            pygame.draw.line(screen, glow_color, start, end, thickness + 1)

    def _draw_behavioral_stats(self, screen, x, y, width, height, agent):
        """Draw behavioral statistics and graphs."""
        # Header
        header = self.font_medium.render("Behavioral Patterns", True, self.accent_color)
        screen.blit(header, (x, y))

        # Draw behavioral bars for recent activity
        bar_y = y + 20
        bar_width = 120
        bar_height = 18

        # Draw bars for recent behavioral outputs
        behaviors = [
            ("Avoid Drive", agent.avoid_drive, (100, 150, 220)),
            ("Attack Drive", agent.attack_drive, (220, 100, 100)),
            ("Mate Desire", agent.mate_desire, (180, 100, 220)),
            ("Effort Level", agent.effort, (220, 220, 100)),
            ("Metabolism", getattr(agent, 'metabolism_rate', 0.0), (150, 200, 100)),
            ("Social Drive", getattr(agent, 'social_drive', 0.0), (200, 150, 100)),
            ("Exploration", getattr(agent, 'exploration_drive', 0.0), (100, 200, 200)),
        ]

        for i, (label, value, color) in enumerate(behaviors):
            # Draw label
            label_text = self.font_medium.render(label, True, self.text_color)
            screen.blit(label_text, (x, bar_y + i * 30))

            # Draw bar background
            pygame.draw.rect(screen, (50, 50, 60), (x + 120, bar_y + i * 30, bar_width, bar_height))

            # Draw filled portion of bar
            fill_width = int(bar_width * min(1.0, abs(value)))  # Clamp value to 0-1 range
            pygame.draw.rect(screen, color, (x + 120, bar_y + i * 30, fill_width, bar_height))

            # Draw value text
            value_text = self.font_medium.render(f"{value:.2f}", True, self.text_color)
            screen.blit(value_text, (x + 120 + bar_width + 8, bar_y + i * 30))

        # Draw stress level
        stress_y = bar_y + len(behaviors) * 30 + 15
        stress_label = self.font_medium.render(f"Stress Level: {agent.stress:.2f}", True, self.text_color)
        screen.blit(stress_label, (x, stress_y))

        # Draw stress bar
        pygame.draw.rect(screen, (50, 50, 60), (x + 120, stress_y, bar_width, bar_height))
        stress_fill_width = int(bar_width * min(1.0, agent.stress))  # Clamp value to 0-1 range
        stress_color = (255, 100, 100) if agent.stress > 0.7 else (255, 180, 100) if agent.stress > 0.3 else (100, 200, 100)
        pygame.draw.rect(screen, stress_color, (x + 120, stress_y, stress_fill_width, bar_height))

        # Draw additional agent stats
        additional_y = stress_y + 30
        additional_stats = [
            ("Health", agent.health if hasattr(agent, 'health') else agent.energy, (100, 200, 100)),
            ("Fitness", getattr(agent, 'fitness', agent.energy * agent.size), (150, 150, 255)),
            ("Lifespan", f"{agent.age:.1f}/{agent.max_age:.1f}", (200, 180, 100))
        ]

        for i, (label, value, color) in enumerate(additional_stats):
            if isinstance(value, str):
                # Special case for lifespan which is a string
                label_text = self.font_medium.render(f"{label}:", True, self.text_color)
                value_text = self.font_medium.render(value, True, color)
            else:
                label_text = self.font_medium.render(f"{label}:", True, self.text_color)
                value_text = self.font_medium.render(f"{value:.2f}", True, color)

            screen.blit(label_text, (x, additional_y + i * 25))
            if not isinstance(value, str):
                # Draw bar for numeric values
                bar_fill = int(bar_width * min(1.0, value / 100.0 if label == "Fitness" else value / agent.max_age if label == "Lifespan" else value / agent.energy))
                pygame.draw.rect(screen, (50, 50, 60), (x + 120, additional_y + i * 25, bar_width, bar_height))
                pygame.draw.rect(screen, color, (x + 120, additional_y + i * 25, bar_fill, bar_height))
            screen.blit(value_text, (x + 120 + bar_width + 8, additional_y + i * 25))

        # Draw recent stats if available
        if hasattr(agent, 'last_nn_inputs'):
            # Show some of the most recent neural network inputs
            inputs_y = additional_y + len(additional_stats) * 25 + 10
            inputs_header = self.font_medium.render("Recent Neural Inputs", True, self.accent_color)
            screen.blit(inputs_header, (x, inputs_y))

            # Show first few inputs as examples - use smaller font for better fit
            for i in range(min(8, len(agent.last_nn_inputs))):  # Increased to show more inputs
                input_val = agent.last_nn_inputs[i]
                input_label = self.font_small.render(f"{self.input_labels[i]}: {input_val:.2f}", True, self.text_color)
                screen.blit(input_label, (x, inputs_y + 25 + i * 18))

        # Draw recent outputs
        outputs_y = inputs_y + 25 + min(8, len(agent.last_nn_inputs)) * 18 + 10
        outputs_header = self.font_medium.render("Recent Neural Outputs", True, self.accent_color)
        screen.blit(outputs_header, (x, outputs_y))

        if hasattr(agent, 'last_nn_outputs'):
            for i in range(min(4, len(agent.last_nn_outputs))):
                output_val = agent.last_nn_outputs[i]
                output_label = self.font_medium.render(f"{self.output_labels[i]}: {output_val:.2f}", True, self.text_color)
                screen.blit(output_label, (x, outputs_y + 25 + i * 20))

    def handle_click(self, pos):
        """Handle mouse clicks on the agent info window."""
        if not self.visible or not self.selected_agent:
            return False

        # Check if click is inside the window
        if not (self.window_x <= pos[0] <= self.window_x + self.window_width and
                self.window_y <= pos[1] <= self.window_y + self.window_height):
            return False

        # Check if click is on the save button
        save_button_rect = pygame.Rect(self.window_x + self.window_width - 150, self.window_y + 10, 60, 25)
        if save_button_rect.collidepoint(pos):
            # Save the current agent
            agent_name = self._get_agent_name(self.selected_agent.id)
            try:
                # Ensure the creature saver is initialized
                if self.creature_saver is None:
                    from .creatures_menu import CreatureSaver
                    self.creature_saver = CreatureSaver()

                result = self.creature_saver.save_creature(self.selected_agent, agent_name)
                print(f"Creature saved: {agent_name} to file: {result}")
                return True
            except Exception as e:
                print(f"Error saving creature: {e}")
                import traceback
                traceback.print_exc()
                return False

        return True