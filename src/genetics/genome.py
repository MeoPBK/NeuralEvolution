import random
from .chromosome import Chromosome
from .gene import Gene
from .allele import Allele
import config

# V2 Architecture: FNN = 254 weights, RNN = 318 weights
# Distributed across chromosomes 4-9

# Chromosome layout: which genes go on which chromosome
CHROMOSOME_LAYOUT = [
    # Chromosome 0: Speed, Size, Efficiency, Max Age
    ['speed_1', 'speed_2', 'speed_3', 'size_1', 'size_2', 'efficiency_1', 'efficiency_2', 'max_age_1', 'max_age_2', 'virus_resistance_1'],
    # Chromosome 1: Vision, Efficiency, Reproduction, Camouflage
    ['vision_1', 'vision_2', 'efficiency_3', 'repro_1', 'repro_2', 'camo_1', 'virus_resistance_2'],
    # Chromosome 2: Aggression, Agility, Armor (morphological traits)
    ['aggro_1', 'aggro_2', 'agility_1', 'agility_2', 'armor_1', 'armor_2'],
    # Chromosome 3: Color genes and disease resistance genes
    ['color_red_1', 'color_red_2', 'color_green_1', 'color_green_2', 'color_blue_1', 'color_blue_2',
     'disease_resistance_1', 'disease_resistance_2', 'disease_resistance_3', 'disease_resistance_4'],
    # Chromosome 4: Brain weights 0-63 (input→hidden partial)
    [f'brain_w{i}' for i in range(0, 64)],
    # Chromosome 5: Brain weights 64-127 (input→hidden partial)
    [f'brain_w{i}' for i in range(64, 128)],
    # Chromosome 6: Brain weights 128-191 (input→hidden rest + recurrent partial)
    [f'brain_w{i}' for i in range(128, 192)],
    # Chromosome 7: Brain weights 192-255 (recurrent rest + biases + output weights partial)
    [f'brain_w{i}' for i in range(192, 256)],
    # Chromosome 8: Brain weights 256-317 (output weights rest + output biases)
    [f'brain_w{i}' for i in range(256, 318)],
]

# Default mean values for each gene (used for initial population)
GENE_DEFAULTS = {
    'speed_1': 3.0, 'speed_2': 3.0, 'speed_3': 3.0,
    'size_1': 6.0, 'size_2': 6.0,
    'vision_1': 100.0, 'vision_2': 100.0,
    'efficiency_1': 1.0, 'efficiency_2': 1.0, 'efficiency_3': 1.0,
    'repro_1': 0.8, 'repro_2': 0.8,
    'camo_1': 0.5,
    'aggro_1': 1.0, 'aggro_2': 1.0,
    'speed_3_mod': 0.0, 'size_mod': 0.0,
    'max_age_1': 70.0, 'max_age_2': 70.0,
    'virus_resistance_1': 0.5, 'virus_resistance_2': 0.5,
    # Color gene defaults
    'color_red_1': 128.0, 'color_red_2': 128.0,
    'color_green_1': 128.0, 'color_green_2': 128.0,
    'color_blue_1': 128.0, 'color_blue_2': 128.0,
    # Disease resistance gene defaults
    'disease_resistance_1': 0.5, 'disease_resistance_2': 0.5,
    'disease_resistance_3': 0.5, 'disease_resistance_4': 0.5,
    # Morphological trait gene defaults (agility and armor)
    'agility_1': 0.5, 'agility_2': 0.5,
    'armor_1': 0.5, 'armor_2': 0.5,
}

# Add brain weight defaults (all 0.0 mean)
# V2 Architecture supports up to 318 weights for RNN
for i in range(318):
    GENE_DEFAULTS[f'brain_w{i}'] = 0.0

# Standard deviation for initial allele generation
GENE_STDS = {
    'speed_1': 0.5, 'speed_2': 0.5, 'speed_3': 0.5,
    'size_1': 1.0, 'size_2': 1.0,
    'vision_1': 20.0, 'vision_2': 20.0,
    'efficiency_1': 0.2, 'efficiency_2': 0.2, 'efficiency_3': 0.2,
    'repro_1': 0.15, 'repro_2': 0.15,
    'camo_1': 0.15,
    'aggro_1': 0.3, 'aggro_2': 0.3,
    'speed_3_mod': 0.3, 'size_mod': 0.5,
    'max_age_1': 10.0, 'max_age_2': 10.0,
    'virus_resistance_1': 0.2, 'virus_resistance_2': 0.2,
    # Color gene standard deviations
    'color_red_1': 50.0, 'color_red_2': 50.0,
    'color_green_1': 50.0, 'color_green_2': 50.0,
    'color_blue_1': 50.0, 'color_blue_2': 50.0,
    # Disease resistance gene standard deviations
    'disease_resistance_1': 0.2, 'disease_resistance_2': 0.2,
    'disease_resistance_3': 0.2, 'disease_resistance_4': 0.2,
    # Morphological trait gene standard deviations
    'agility_1': 0.15, 'agility_2': 0.15,
    'armor_1': 0.15, 'armor_2': 0.15,
}

# Brain gene std uses config value
# V2 Architecture supports up to 318 weights for RNN
for i in range(318):
    GENE_STDS[f'brain_w{i}'] = config.NN_WEIGHT_INIT_STD


class Genome:
    __slots__ = ('chromosomes', 'sex')

    def __init__(self, chromosomes, sex=None):
        self.chromosomes = chromosomes
        self.sex = sex or random.choice(['male', 'female'])

    def get_gene(self, name):
        """Find a gene by name across all chromosomes."""
        for chrom in self.chromosomes:
            for gene in chrom.genes:
                if gene.name == name:
                    return gene
        return None

    def all_genes(self):
        """Iterator over all genes in the genome."""
        for chrom in self.chromosomes:
            for gene in chrom.genes:
                yield gene

    def copy(self):
        return Genome(
            [c.copy() for c in self.chromosomes],
            self.sex
        )

    @staticmethod
    def create_random(sex=None):
        """Create a genome with random alleles based on defaults."""
        chromosomes = []
        for chrom_genes in CHROMOSOME_LAYOUT:
            genes = []
            for gene_name in chrom_genes:
                mean = GENE_DEFAULTS[gene_name]
                std = GENE_STDS[gene_name]
                genes.append(Gene.create_random(gene_name, mean, std))
            chromosomes.append(Chromosome(genes))
        return Genome(chromosomes, sex or random.choice(['male', 'female']))

    @staticmethod
    def from_parents(parent_a, parent_b, crossover_rate):
        """Create offspring genome via sexual reproduction with crossover."""
        offspring_chromosomes = []
        for i in range(len(parent_a.chromosomes)):
            child_chrom, _ = Chromosome.crossover(
                parent_a.chromosomes[i],
                parent_b.chromosomes[i],
                crossover_rate
            )
            offspring_chromosomes.append(child_chrom)
        sex = random.choice(['male', 'female'])
        return Genome(offspring_chromosomes, sex)

    def __repr__(self):
        return f"Genome({self.sex}, {len(self.chromosomes)} chroms)"
