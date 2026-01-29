import random
from .genome import Genome
from .mutation import apply_mutations


def create_offspring(parent_a_genome, parent_b_genome, config_obj):
    """Full sexual reproduction pipeline:
    1. Parents undergo meiosis with crossover
    2. Gametes combine to form diploid offspring
    3. Apply mutations to offspring genome
    4. Sex determined randomly
    """
    # Create offspring via crossover
    offspring_genome = Genome.from_parents(
        parent_a_genome,
        parent_b_genome,
        getattr(config_obj, 'CROSSOVER_RATE', 0.3)
    )

    # Apply mutations
    mutations_applied = apply_mutations(
        offspring_genome,
        getattr(config_obj, 'MUTATION_RATE', 0.02),
        getattr(config_obj, 'LARGE_MUTATION_CHANCE', 0.05),
        getattr(config_obj, 'POINT_MUTATION_STDDEV', 0.3),
        getattr(config_obj, 'LARGE_MUTATION_STDDEV', 1.5),
        getattr(config_obj, 'DOMINANCE_MUTATION_RATE', 0.15),
    )

    return offspring_genome, mutations_applied
