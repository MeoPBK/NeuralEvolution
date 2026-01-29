"""
Brain phenotype extraction and building utilities.
Handles conversion from genome brain genes to neural network instances.
"""
import random
from .brain import NeuralBrain, get_weight_count
from .rnn_brain import RecurrentBrain, get_rnn_weight_count, MemoryBuffer


def extract_brain_weights(genome, nn_type='FNN', n_inputs=None, settings=None):
    """Extract neural network weights from brain genes in the genome.

    Brain genes are named brain_w0 through brain_wN, distributed
    across chromosomes 4-7. Each gene's expressed value IS the weight.

    Args:
        genome: The genome to extract weights from
        nn_type: 'FNN' for feed-forward or 'RNN' for recurrent
        n_inputs: Override input count (for n-step memory extension)
        settings: Optional settings dict for initialization parameters

    Returns:
        List of weight values
    """
    if n_inputs is None:
        n_inputs = 24  # Default V2 architecture

    if nn_type == 'RNN':
        n_weights = get_rnn_weight_count(n_inputs=n_inputs)
    else:
        n_weights = get_weight_count(n_inputs=n_inputs)

    # Get initialization parameters
    weight_init_std = 0.3
    identity_bias = 0.1
    if settings:
        weight_init_std = settings.get('NN_WEIGHT_INIT_STD', 0.3)
        identity_bias = settings.get('NN_RECURRENT_IDENTITY_BIAS', 0.1)

    weights = []
    for i in range(n_weights):
        gene_name = f"brain_w{i}"
        gene = genome.get_gene(gene_name)
        if gene is not None:
            weights.append(gene.express())
        else:
            # Gene not found - use initialized value
            # For RNN, add slight identity bias to recurrent weights
            if nn_type == 'RNN':
                # Check if this is a recurrent weight (after input-hidden weights)
                ih_count = n_inputs * 8  # input-hidden
                hh_count = 64  # hidden-hidden (8x8)
                if ih_count <= i < ih_count + hh_count:
                    # This is a recurrent weight
                    local_idx = i - ih_count
                    row = local_idx // 8
                    col = local_idx % 8
                    if row == col:
                        # Diagonal - add identity bias for stability
                        weights.append(random.gauss(identity_bias, weight_init_std))
                    else:
                        weights.append(random.gauss(0, weight_init_std))
                else:
                    weights.append(random.gauss(0, weight_init_std))
            else:
                weights.append(random.gauss(0, weight_init_std))

    return weights


def build_brain(genome, nn_type='FNN', settings=None):
    """Build a neural network brain from genome's brain genes.

    Args:
        genome: The genome containing brain weight genes
        nn_type: 'FNN' for feed-forward or 'RNN' for recurrent
        settings: Optional settings dict for configuration

    Returns:
        NeuralBrain or RecurrentBrain instance
    """
    # Check for n-step memory extension
    n_step_enabled = False
    n_step_depth = 0
    use_noise = False
    noise_std = 0.02

    if settings:
        n_step_enabled = settings.get('N_STEP_MEMORY_ENABLED', False)
        n_step_depth = settings.get('N_STEP_MEMORY_DEPTH', 2)
        use_noise = settings.get('NN_HIDDEN_NOISE_ENABLED', False)
        noise_std = settings.get('NN_HIDDEN_NOISE_STD', 0.02)

    # Calculate input size
    base_inputs = 24
    if n_step_enabled:
        n_inputs = base_inputs + (n_step_depth * 8)  # 8 = hidden size
    else:
        n_inputs = base_inputs

    weights = extract_brain_weights(genome, nn_type, n_inputs, settings)

    if nn_type == 'RNN':
        brain = RecurrentBrain(weights, n_inputs=n_inputs, use_noise=use_noise, noise_std=noise_std)
    else:
        brain = NeuralBrain(weights, n_inputs=n_inputs)

    return brain


def get_brain_weight_count(nn_type='FNN', n_inputs=24):
    """Get the number of weights required for the specified neural network type.

    Args:
        nn_type: 'FNN' or 'RNN'
        n_inputs: Number of inputs (default 24 for V2 architecture)

    Returns:
        Total weight count
    """
    if nn_type == 'RNN':
        return get_rnn_weight_count(n_inputs=n_inputs)
    else:
        return get_weight_count(n_inputs=n_inputs)


def create_memory_buffer(settings):
    """Create a memory buffer for n-step memory feature.

    Args:
        settings: Settings dict

    Returns:
        MemoryBuffer instance or None if feature disabled
    """
    if settings and settings.get('N_STEP_MEMORY_ENABLED', False):
        n_steps = settings.get('N_STEP_MEMORY_DEPTH', 2)
        hidden_size = 8  # V2 hidden layer size
        return MemoryBuffer(n_steps, hidden_size)
    return None


# Input labels for the V2 architecture (24 inputs)
INPUT_LABELS = [
    # Sector-based food sensing (5 sectors)
    'food_s0', 'food_s1', 'food_s2', 'food_s3', 'food_s4',
    # Sector-based water sensing (5 sectors)
    'water_s0', 'water_s1', 'water_s2', 'water_s3', 'water_s4',
    # Sector-based agent sensing (5 sectors)
    'agent_s0', 'agent_s1', 'agent_s2', 'agent_s3', 'agent_s4',
    # Internal state
    'energy', 'hydration', 'age_ratio', 'stress', 'health',
    # Egocentric velocity
    'vel_fwd', 'vel_lat',
    # Self traits
    'own_size', 'own_speed',
]

# Output labels for the V2 architecture (6 outputs)
OUTPUT_LABELS = [
    'move_x',      # Movement direction X
    'move_y',      # Movement direction Y
    'avoid',       # Avoidance/flee drive
    'attack',      # Attack drive
    'mate',        # Reproduction drive
    'effort',      # Energy expenditure level
]
