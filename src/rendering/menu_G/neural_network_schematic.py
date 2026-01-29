"""
Neural Network Schematic module for the genetics visualization.
Contains functions for drawing neural network diagrams for both FNN and RNN.
"""

import pygame
import math
from src.nn.rnn_brain import RecurrentBrain


# Create font at module level (will be initialized on first use)
font_small = None


def _get_font():
    """Get or create the small font."""
    global font_small
    if font_small is None:
        font_small = pygame.font.SysFont('monospace', 11)
    return font_small


def _draw_nn_schematic(screen, x, y, width, height, agent, mutation_hotspots, species_color):
    """Draw a neural network schematic with mutation indicator."""
    if not agent or not hasattr(agent, 'brain'):
        font = _get_font()
        no_nn = font.render("No neural network data", True, (150, 150, 160))
        screen.blit(no_nn, (x + 20, y + 20))
        return

    brain = agent.brain
    is_rnn = isinstance(brain, RecurrentBrain)

    if is_rnn:
        _draw_rnn_schematic(screen, x, y, width, height, agent, brain, mutation_hotspots, species_color)
    else:
        _draw_fnn_schematic(screen, x, y, width, height, agent, brain, mutation_hotspots, species_color)


def _draw_fnn_schematic(screen, x, y, width, height, agent, brain, mutation_hotspots, species_color):
    """Draw a feed-forward neural network schematic."""
    font = _get_font()

    # Layout parameters
    margin = 40
    layer_spacing = (width - 2 * margin) // 2

    # Neuron positions
    input_x = x + margin
    hidden_x = x + margin + layer_spacing
    output_x = x + width - margin

    # Calculate neuron Y positions
    input_neurons = []
    hidden_neurons = []
    output_neurons = []

    n_inputs_display = 16
    n_hidden = 6
    n_outputs = 4

    # Spread neurons vertically
    input_spacing = (height - 40) / (n_inputs_display + 1)
    hidden_spacing = (height - 40) / (n_hidden + 1)
    output_spacing = (height - 40) / (n_outputs + 1)

    for i in range(n_inputs_display):
        input_neurons.append((input_x, y + 20 + (i + 1) * input_spacing))

    for i in range(n_hidden):
        hidden_neurons.append((hidden_x, y + 20 + (i + 1) * hidden_spacing))

    for i in range(n_outputs):
        output_neurons.append((output_x, y + 20 + (i + 1) * output_spacing))

    # Draw connections with weight-based styling
    _draw_fnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, False)
    _draw_fnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, True)

    # Draw neurons
    _draw_input_neurons(screen, input_neurons, mutation_hotspots, font)
    _draw_hidden_neurons(screen, hidden_neurons, brain, mutation_hotspots, font, is_rnn=False)
    _draw_output_neurons(screen, output_neurons, brain, mutation_hotspots, font)

    # Draw legend
    _draw_legend(screen, x, y + height - 25, font, "FNN")

    # Layer labels
    _draw_layer_labels(screen, input_x, hidden_x, output_x, y, font, is_rnn=False)


def _draw_rnn_schematic(screen, x, y, width, height, agent, brain, mutation_hotspots, species_color):
    """Draw a recurrent neural network schematic with recurrent connections."""
    font = _get_font()

    # Layout parameters - need more space for recurrent arrows
    margin = 50
    layer_spacing = (width - 2 * margin) // 2

    # Neuron positions
    input_x = x + margin
    hidden_x = x + margin + layer_spacing
    output_x = x + width - margin - 10

    # Calculate neuron Y positions
    input_neurons = []
    hidden_neurons = []
    output_neurons = []

    n_inputs_display = 16
    n_hidden = 6
    n_outputs = 4

    # Spread neurons vertically
    input_spacing = (height - 50) / (n_inputs_display + 1)
    hidden_spacing = (height - 50) / (n_hidden + 1)
    output_spacing = (height - 50) / (n_outputs + 1)

    for i in range(n_inputs_display):
        input_neurons.append((input_x, y + 25 + (i + 1) * input_spacing))

    for i in range(n_hidden):
        hidden_neurons.append((hidden_x, y + 25 + (i + 1) * hidden_spacing))

    for i in range(n_outputs):
        output_neurons.append((output_x, y + 25 + (i + 1) * output_spacing))

    # Draw connections
    _draw_rnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, False)
    _draw_rnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, True)

    # Draw recurrent connections (the key difference from FNN)
    _draw_recurrent_connections(screen, brain, hidden_neurons, mutation_hotspots, species_color)

    # Draw neurons
    _draw_input_neurons(screen, input_neurons, mutation_hotspots, font)
    _draw_hidden_neurons(screen, hidden_neurons, brain, mutation_hotspots, font, is_rnn=True)
    _draw_output_neurons(screen, output_neurons, brain, mutation_hotspots, font)

    # Draw legend
    _draw_legend(screen, x, y + height - 25, font, "RNN")

    # Layer labels
    _draw_layer_labels(screen, input_x, hidden_x, output_x, y, font, is_rnn=True)


def _draw_recurrent_connections(screen, brain, hidden_neurons, mutation_hotspots, species_color):
    """Draw recurrent connections between hidden neurons."""
    if not hasattr(brain, 'w_hh'):
        return

    n_hidden = len(hidden_neurons)
    base_idx = 96  # After input-hidden weights

    # Draw recurrent connections as curved arrows
    for h1_idx in range(n_hidden):
        for h2_idx in range(n_hidden):
            idx = base_idx + h1_idx * n_hidden + h2_idx
            weight = brain.w_hh[h1_idx][h2_idx]
            is_mutated = idx in mutation_hotspots

            h1_pos = hidden_neurons[h1_idx]
            h2_pos = hidden_neurons[h2_idx]

            if h1_idx == h2_idx:
                # Self-connection - draw as a loop
                _draw_self_loop(screen, h1_pos, weight, is_mutated)
            else:
                # Connection to other hidden neuron
                _draw_curved_connection(screen, h1_pos, h2_pos, weight, is_mutated)


def _draw_self_loop(screen, pos, weight, is_mutated):
    """Draw a self-loop connection for recurrent self-connections."""
    abs_weight = abs(weight)
    if abs_weight < 0.1:
        return  # Don't draw very weak connections

    # Draw a small loop to the right of the neuron
    loop_x = pos[0] + 20
    loop_y = pos[1]
    loop_radius = 8 + int(abs_weight * 3)

    if is_mutated:
        color = (255, 180, 50)
        thickness = 2
    else:
        color = (180, 100, 255) if weight >= 0 else (255, 100, 180)
        thickness = 1

    # Draw arc
    rect = pygame.Rect(loop_x - loop_radius, loop_y - loop_radius, loop_radius * 2, loop_radius * 2)
    pygame.draw.arc(screen, color, rect, -math.pi/2, math.pi * 1.5, thickness)

    # Draw arrow head
    arrow_x = loop_x
    arrow_y = loop_y - loop_radius
    pygame.draw.polygon(screen, color, [
        (arrow_x, arrow_y),
        (arrow_x - 3, arrow_y - 5),
        (arrow_x + 3, arrow_y - 5)
    ])


def _draw_curved_connection(screen, start, end, weight, is_mutated):
    """Draw a curved connection between hidden neurons."""
    abs_weight = abs(weight)
    if abs_weight < 0.1:
        return  # Don't draw very weak connections

    if is_mutated:
        color = (255, 180, 50)
        thickness = 2
    else:
        color = (180, 100, 255, 100) if weight >= 0 else (255, 100, 180, 100)
        thickness = 1

    # Calculate control point for bezier curve (curve to the right)
    mid_x = (start[0] + end[0]) / 2 + 30
    mid_y = (start[1] + end[1]) / 2

    # Draw as series of line segments approximating a curve
    points = []
    for t in range(11):
        t = t / 10.0
        # Quadratic bezier
        x = (1-t)**2 * start[0] + 2*(1-t)*t * mid_x + t**2 * end[0]
        y = (1-t)**2 * start[1] + 2*(1-t)*t * mid_y + t**2 * end[1]
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, color[:3] if len(color) > 3 else color, False, points, thickness)


def _draw_fnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, draw_mutated_only):
    """Draw FNN neural network connections."""
    # Input -> Hidden connections
    for h_idx, h_pos in enumerate(hidden_neurons):
        for i_idx, i_pos in enumerate(input_neurons):
            idx = h_idx * 16 + i_idx
            weight = brain.w_ih[h_idx][i_idx]
            is_mutated = idx in mutation_hotspots

            if draw_mutated_only != is_mutated:
                continue

            # Only draw every 2nd connection to reduce clutter, BUT always draw mutation hotspots
            if i_idx % 2 != 0 and not is_mutated:
                continue

            _draw_weight_connection(screen, i_pos, h_pos, weight, is_mutated,
                                    mutation_hotspots.get(idx, 0), species_color)

    # Hidden -> Output connections
    base_idx = 96 + 6  # After input-hidden weights and hidden biases
    for o_idx, o_pos in enumerate(output_neurons):
        for h_idx, h_pos in enumerate(hidden_neurons):
            idx = base_idx + o_idx * 6 + h_idx
            weight = brain.w_ho[o_idx][h_idx]
            is_mutated = idx in mutation_hotspots

            if draw_mutated_only != is_mutated:
                continue

            _draw_weight_connection(screen, h_pos, o_pos, weight, is_mutated,
                                    mutation_hotspots.get(idx, 0), species_color)


def _draw_rnn_connections(screen, brain, input_neurons, hidden_neurons, output_neurons,
                          mutation_hotspots, species_color, draw_mutated_only):
    """Draw RNN neural network connections (excluding recurrent)."""
    # Input -> Hidden connections
    for h_idx, h_pos in enumerate(hidden_neurons):
        for i_idx, i_pos in enumerate(input_neurons):
            idx = h_idx * 16 + i_idx
            weight = brain.w_ih[h_idx][i_idx]
            is_mutated = idx in mutation_hotspots

            if draw_mutated_only != is_mutated:
                continue

            if i_idx % 2 != 0 and not is_mutated:
                continue

            _draw_weight_connection(screen, i_pos, h_pos, weight, is_mutated,
                                    mutation_hotspots.get(idx, 0), species_color)

    # Hidden -> Output connections (after recurrent weights in RNN)
    base_idx = 96 + 36 + 6  # After input-hidden, hidden-hidden, and hidden biases
    for o_idx, o_pos in enumerate(output_neurons):
        for h_idx, h_pos in enumerate(hidden_neurons):
            idx = base_idx + o_idx * 6 + h_idx
            weight = brain.w_ho[o_idx][h_idx]
            is_mutated = idx in mutation_hotspots

            if draw_mutated_only != is_mutated:
                continue

            _draw_weight_connection(screen, h_pos, o_pos, weight, is_mutated,
                                    mutation_hotspots.get(idx, 0), species_color)


def _draw_weight_connection(screen, start, end, weight, is_mutated, variance, species_color):
    """Draw a single weight connection."""
    abs_weight = abs(weight)
    thickness = max(1, min(3, int(1 + abs_weight * 1.5)))

    if is_mutated:
        alpha = min(255, int(150 + variance * 500))
        color = (255, 180, 50)
        thickness = max(2, thickness)
        pygame.draw.line(screen, (*color, 100), start, end, thickness + 2)
    else:
        if weight >= 0:
            color = (100, 120, 180, 80)
        else:
            color = (180, 100, 100, 80)

    pygame.draw.line(screen, color[:3], start, end, thickness)


def _draw_input_neurons(screen, input_neurons, mutation_hotspots, font):
    """Draw input neurons with labels."""
    input_labels = [
        "food_dx", "food_dy", "water_dx", "water_dy",
        "agent_dx", "agent_dy", "energy", "hydration",
        "age", "e_rate", "h_rate", "a_dens",
        "f_dens", "rel_sz", "aggro", "speed"
    ]

    for i, pos in enumerate(input_neurons):
        _draw_neuron(screen, pos, 5, (80, 180, 80), i, mutation_hotspots, 'input')
        if i < len(input_labels):
            label = input_labels[i][:6]
            label_text = font.render(label, True, (140, 140, 150))
            screen.blit(label_text, (pos[0] - 45, pos[1] - 5))


def _draw_hidden_neurons(screen, hidden_neurons, brain, mutation_hotspots, font, is_rnn=False):
    """Draw hidden neurons with activation values."""
    for i, pos in enumerate(hidden_neurons):
        is_mutated = _is_hidden_neuron_mutated(i, mutation_hotspots, brain, is_rnn)
        neuron_color = (255, 180, 50) if is_mutated else (80, 130, 200)

        # For RNN, add a slight purple tint to indicate recurrence
        if is_rnn:
            neuron_color = (255, 180, 50) if is_mutated else (120, 100, 200)

        _draw_neuron(screen, pos, 8, neuron_color, i, mutation_hotspots, 'hidden')

        if hasattr(brain, 'last_hidden_activations') and i < len(brain.last_hidden_activations):
            act = brain.last_hidden_activations[i]
            act_text = font.render(f"{act:.2f}", True, (180, 180, 190))
            screen.blit(act_text, (pos[0] - 15, pos[1] + 10))


def _draw_output_neurons(screen, output_neurons, brain, mutation_hotspots, font):
    """Draw output neurons with labels."""
    output_labels = ["move_x", "move_y", "attack", "mate"]

    for i, pos in enumerate(output_neurons):
        # Check output bias position
        if hasattr(brain, 'w_hh'):
            # RNN: biases after recurrent weights
            bias_idx = 96 + 36 + 6 + 24 + i
        else:
            # FNN
            bias_idx = 96 + 6 + 24 + i

        is_mutated = bias_idx in mutation_hotspots
        neuron_color = (255, 180, 50) if is_mutated else (200, 80, 80)
        _draw_neuron(screen, pos, 7, neuron_color, i, mutation_hotspots, 'output')

        if i < len(output_labels):
            label = output_labels[i]
            label_text = font.render(label, True, (140, 140, 150))
            screen.blit(label_text, (pos[0] + 12, pos[1] - 5))


def _draw_neuron(screen, pos, radius, color, index, mutation_hotspots, layer_type):
    """Draw a neuron with potential mutation indicator."""
    pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(pos[0]), int(pos[1])), radius, 1)


def _draw_legend(screen, x, y, font, nn_type):
    """Draw the legend."""
    pygame.draw.circle(screen, (255, 180, 50), (x + 10, y), 4)
    legend_text = font.render(f"= Mutation hotspot ({nn_type})", True, (150, 150, 160))
    screen.blit(legend_text, (x + 20, y - 6))

    if nn_type == 'RNN':
        # Add recurrent indicator
        pygame.draw.arc(screen, (180, 100, 255), pygame.Rect(x + 200, y - 8, 16, 16), 0, math.pi * 1.5, 2)
        recur_text = font.render("= Recurrent", True, (150, 150, 160))
        screen.blit(recur_text, (x + 220, y - 6))


def _draw_layer_labels(screen, input_x, hidden_x, output_x, y, font, is_rnn=False):
    """Draw layer labels."""
    hidden_label = "HIDDEN (6+R)" if is_rnn else "HIDDEN (6)"

    input_label_surf = font.render("INPUT (16)", True, (180, 185, 200))
    hidden_label_surf = font.render(hidden_label, True, (180, 185, 200))
    output_label_surf = font.render("OUTPUT (4)", True, (180, 185, 200))

    screen.blit(input_label_surf, (input_x - 25, y + 2))
    screen.blit(hidden_label_surf, (hidden_x - 35, y + 2))
    screen.blit(output_label_surf, (output_x - 30, y + 2))


def _is_hidden_neuron_mutated(h_idx, mutation_hotspots, brain, is_rnn=False):
    """Check if a hidden neuron has mutated connections."""
    # Check input connections to this hidden neuron
    for i in range(16):
        idx = h_idx * 16 + i
        if idx in mutation_hotspots:
            return True

    if is_rnn:
        # Check recurrent connections
        base_idx = 96
        for h in range(6):
            idx = base_idx + h_idx * 6 + h
            if idx in mutation_hotspots:
                return True
            idx = base_idx + h * 6 + h_idx
            if idx in mutation_hotspots:
                return True

        # Check hidden bias (after recurrent)
        bias_idx = 96 + 36 + h_idx
        if bias_idx in mutation_hotspots:
            return True

        # Check output connections from this hidden neuron
        base_idx = 96 + 36 + 6
        for o in range(4):
            idx = base_idx + o * 6 + h_idx
            if idx in mutation_hotspots:
                return True
    else:
        # Check hidden bias
        bias_idx = 96 + h_idx
        if bias_idx in mutation_hotspots:
            return True

        # Check output connections from this hidden neuron
        base_idx = 96 + 6
        for o in range(4):
            idx = base_idx + o * 6 + h_idx
            if idx in mutation_hotspots:
                return True

    return False
