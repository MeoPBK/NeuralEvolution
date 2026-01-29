import random
import config


def apply_mutations(genome, mutation_rate, large_mutation_chance,
                    point_stddev, large_stddev, dominance_mutation_rate):
    """Apply mutations to a genome with realistic type distribution.

    Mutation types:
    - 70% point mutation: Gaussian shift to allele value
    - 15% dominance mutation: shift allele dominance coefficient
    - 10% allele swap: swap maternal/paternal alleles at a locus
    - 5% large-effect mutation: bigger jump in value

    Returns:
    - Number of mutations applied
    """
    mutations_applied = 0
    for gene in genome.all_genes():
        if random.random() >= mutation_rate:
            continue
        mutate_gene(gene, half_effect=False)
        mutations_applied += 1
    return mutations_applied


def mutate_gene(gene, half_effect=False):
    """Apply a single mutation to a gene.

    If half_effect=True (somatic mutations), effect sizes are halved.
    """
    scale = 0.5 if half_effect else 1.0
    point_stddev = config.POINT_MUTATION_STDDEV * scale
    large_stddev = config.LARGE_MUTATION_STDDEV * scale

    roll = random.random()

    if roll < 0.70:
        # Point mutation on a random allele
        allele = random.choice([gene.allele_a, gene.allele_b])
        allele.value += random.gauss(0, point_stddev)

    elif roll < 0.85:
        # Dominance mutation
        allele = random.choice([gene.allele_a, gene.allele_b])
        allele.dominance += random.gauss(0, 0.1 * scale)
        allele.dominance = max(0.0, min(1.0, allele.dominance))

    elif roll < 0.95:
        # Allele swap
        gene.allele_a, gene.allele_b = gene.allele_b, gene.allele_a

    else:
        # Large-effect mutation
        allele = random.choice([gene.allele_a, gene.allele_b])
        allele.value += random.gauss(0, large_stddev)
