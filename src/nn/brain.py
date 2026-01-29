import math
import random


class NeuralBrain:
    """Feed-forward neural network: 24 inputs -> 8 hidden (tanh) -> 6 outputs (tanh).

    Architecture V2 with sector-based sensing and decoupled behavioral drives.

    Total weights: (24*8) + 8 bias + (8*6) + 6 bias = 192 + 8 + 48 + 6 = 254
    Pure Python, no numpy.
    """

    N_INPUTS = 24
    N_HIDDEN = 8
    N_OUTPUTS = 6
    N_WEIGHTS = (N_INPUTS * N_HIDDEN) + N_HIDDEN + (N_HIDDEN * N_OUTPUTS) + N_OUTPUTS  # 254

    def __init__(self, weights, n_inputs=None):
        """Initialize brain from flat list of weights.

        Args:
            weights: Flat list of weights
            n_inputs: Override number of inputs (for n-step memory extension)
        """
        if n_inputs is not None:
            self.n_inputs = n_inputs
            expected = (n_inputs * self.N_HIDDEN) + self.N_HIDDEN + (self.N_HIDDEN * self.N_OUTPUTS) + self.N_OUTPUTS
        else:
            self.n_inputs = self.N_INPUTS
            expected = self.N_WEIGHTS

        assert len(weights) >= expected, f"Expected at least {expected} weights, got {len(weights)}"

        idx = 0
        # Input -> Hidden weights
        self.w_ih = []
        for h in range(self.N_HIDDEN):
            row = weights[idx:idx + self.n_inputs]
            self.w_ih.append(list(row))
            idx += self.n_inputs

        # Hidden biases
        self.b_h = list(weights[idx:idx + self.N_HIDDEN])
        idx += self.N_HIDDEN

        # Hidden -> Output weights
        self.w_ho = []
        for o in range(self.N_OUTPUTS):
            row = weights[idx:idx + self.N_HIDDEN]
            self.w_ho.append(list(row))
            idx += self.N_HIDDEN

        # Output biases
        self.b_o = list(weights[idx:idx + self.N_OUTPUTS])

        # Store last hidden activations for visualization
        self.last_hidden_activations = [0.0] * self.N_HIDDEN

    def forward(self, inputs):
        """Run forward pass.

        Args:
            inputs: List of input values (length should match n_inputs)

        Returns:
            List of 6 output values (all in range -1 to 1 via tanh)
        """
        # Validate input length
        if len(inputs) < self.n_inputs:
            # Pad with zeros if needed
            inputs = list(inputs) + [0.0] * (self.n_inputs - len(inputs))

        # Hidden layer
        hidden = []
        for h in range(self.N_HIDDEN):
            s = self.b_h[h]
            for i in range(self.n_inputs):
                s += self.w_ih[h][i] * inputs[i]
            hidden.append(_tanh(s))

        # Output layer
        outputs = []
        for o in range(self.N_OUTPUTS):
            s = self.b_o[o]
            for h in range(self.N_HIDDEN):
                s += self.w_ho[o][h] * hidden[h]
            outputs.append(_tanh(s))

        # Store for visualization
        self.last_hidden_activations = hidden[:]

        return outputs

    def get_output_labels(self):
        """Return labels for the 6 outputs."""
        return ['move_x', 'move_y', 'avoid', 'attack', 'mate', 'effort']


def _tanh(x):
    """Fast tanh with clamping to avoid overflow."""
    x = max(-20.0, min(20.0, x))
    return math.tanh(x)


def get_weight_count(n_inputs=24, n_hidden=8, n_outputs=6):
    """Calculate total weight count for given architecture."""
    return (n_inputs * n_hidden) + n_hidden + (n_hidden * n_outputs) + n_outputs
