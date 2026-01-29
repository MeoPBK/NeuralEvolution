"""
Recurrent Neural Network (RNN) brain for the simulation.
Architecture V2 with improved initialization and optional stochastic features.
"""
import math
import random


class RecurrentBrain:
    """Recurrent neural network: 24 inputs + 8 hidden state -> 8 hidden (tanh) -> 6 outputs (tanh).

    Architecture V2 features:
    - Sector-based sensing (24 inputs)
    - Decoupled behavioral drives (6 outputs)
    - Hidden-to-hidden recurrent connections for temporal memory
    - Optional stochastic noise in hidden state updates
    - Small random hidden state initialization to prevent saturation

    Total weights: (24*8) + (8*8) + 8 bias + (8*6) + 6 bias = 192 + 64 + 8 + 48 + 6 = 318
    Pure Python, no numpy.
    """

    N_INPUTS = 24
    N_HIDDEN = 8
    N_OUTPUTS = 6
    # FNN weights + recurrent hidden connections
    N_WEIGHTS = (N_INPUTS * N_HIDDEN) + (N_HIDDEN * N_HIDDEN) + N_HIDDEN + (N_HIDDEN * N_OUTPUTS) + N_OUTPUTS  # 318

    def __init__(self, weights, n_inputs=None, use_noise=False, noise_std=0.02):
        """Initialize brain from flat list of weights.

        Args:
            weights: Flat list of weights
            n_inputs: Override number of inputs (for n-step memory extension)
            use_noise: Add small stochastic noise to hidden state updates
            noise_std: Standard deviation of noise (if enabled)
        """
        if n_inputs is not None:
            self.n_inputs = n_inputs
            expected = (n_inputs * self.N_HIDDEN) + (self.N_HIDDEN * self.N_HIDDEN) + self.N_HIDDEN + (self.N_HIDDEN * self.N_OUTPUTS) + self.N_OUTPUTS
        else:
            self.n_inputs = self.N_INPUTS
            expected = self.N_WEIGHTS

        assert len(weights) >= expected, f"Expected at least {expected} weights, got {len(weights)}"

        self.use_noise = use_noise
        self.noise_std = noise_std

        idx = 0
        # Input -> Hidden weights
        self.w_ih = []
        for h in range(self.N_HIDDEN):
            row = weights[idx:idx + self.n_inputs]
            self.w_ih.append(list(row))
            idx += self.n_inputs

        # Hidden -> Hidden (recurrent) weights
        self.w_hh = []
        for h in range(self.N_HIDDEN):
            row = weights[idx:idx + self.N_HIDDEN]
            self.w_hh.append(list(row))
            idx += self.N_HIDDEN

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

        # Initialize hidden state with small random values to prevent immediate saturation
        self.hidden_state = [random.gauss(0, 0.1) for _ in range(self.N_HIDDEN)]

        # Store last hidden activations for visualization
        self.last_hidden_activations = self.hidden_state[:]

    def forward(self, inputs):
        """Run forward pass with recurrent hidden state.

        Args:
            inputs: List of input values (length should match n_inputs)

        Returns:
            List of 6 output values (all in range -1 to 1 via tanh)
        """
        # Validate input length
        if len(inputs) < self.n_inputs:
            inputs = list(inputs) + [0.0] * (self.n_inputs - len(inputs))

        # Compute new hidden state: h(t) = tanh(W_ih * input + W_hh * h(t-1) + bias)
        new_hidden = []
        for h in range(self.N_HIDDEN):
            s = self.b_h[h]

            # Input contribution
            for i in range(self.n_inputs):
                s += self.w_ih[h][i] * inputs[i]

            # Recurrent contribution from previous hidden state
            for h2 in range(self.N_HIDDEN):
                s += self.w_hh[h][h2] * self.hidden_state[h2]

            # Optional stochastic noise for exploration/robustness
            if self.use_noise:
                s += random.gauss(0, self.noise_std)

            new_hidden.append(_tanh(s))

        # Update hidden state
        self.hidden_state = new_hidden[:]

        # Output layer
        outputs = []
        for o in range(self.N_OUTPUTS):
            s = self.b_o[o]
            for h in range(self.N_HIDDEN):
                s += self.w_ho[o][h] * new_hidden[h]
            outputs.append(_tanh(s))

        # Store for visualization
        self.last_hidden_activations = new_hidden[:]

        return outputs

    def reset_hidden_state(self, randomize=True):
        """Reset the hidden state.

        Args:
            randomize: If True, use small random values. If False, use zeros.
        """
        if randomize:
            self.hidden_state = [random.gauss(0, 0.1) for _ in range(self.N_HIDDEN)]
        else:
            self.hidden_state = [0.0] * self.N_HIDDEN

    def get_hidden_state(self):
        """Return copy of current hidden state (for n-step memory)."""
        return self.hidden_state[:]

    def get_output_labels(self):
        """Return labels for the 6 outputs."""
        return ['move_x', 'move_y', 'avoid', 'attack', 'mate', 'effort']


def _tanh(x):
    """Fast tanh with clamping to avoid overflow."""
    x = max(-20.0, min(20.0, x))
    return math.tanh(x)


def get_rnn_weight_count(n_inputs=24, n_hidden=8, n_outputs=6):
    """Calculate total weight count for RNN architecture."""
    return (n_inputs * n_hidden) + (n_hidden * n_hidden) + n_hidden + (n_hidden * n_outputs) + n_outputs


class MemoryBuffer:
    """Circular buffer for storing past hidden states (n-step memory feature)."""

    def __init__(self, n_steps, hidden_size):
        """Initialize buffer.

        Args:
            n_steps: Number of past states to store
            hidden_size: Size of each hidden state vector
        """
        self.n_steps = n_steps
        self.hidden_size = hidden_size
        self.buffer = [[0.0] * hidden_size for _ in range(n_steps)]

    def push(self, hidden_state):
        """Add new hidden state, shift old ones out."""
        self.buffer.pop(0)
        self.buffer.append(list(hidden_state))

    def get_flat(self):
        """Return flattened buffer for input concatenation."""
        return [v for state in self.buffer for v in state]

    def reset(self):
        """Clear the buffer."""
        self.buffer = [[0.0] * self.hidden_size for _ in range(self.n_steps)]
