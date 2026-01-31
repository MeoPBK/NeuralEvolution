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
    # Chromosome 3: Color genes, disease resistance genes, and new diet/habitat traits
    ['color_red_1', 'color_red_2', 'color_green_1', 'color_green_2', 'color_blue_1', 'color_blue_2',
     'disease_resistance_1', 'disease_resistance_2', 'disease_resistance_3', 'disease_resistance_4',
     'diet_type_1', 'diet_type_2', 'habitat_preference_1', 'habitat_preference_2',
     'speed_in_water_aquatic_1', 'speed_in_water_aquatic_2', 'speed_in_water_amphibious_1', 'speed_in_water_amphibious_2',
     'speed_in_water_terrestrial_1', 'speed_in_water_terrestrial_2',
     'land_speed_aquatic_1', 'land_speed_aquatic_2', 'land_speed_amphibious_1', 'land_speed_amphibious_2',
     'land_speed_terrestrial_1', 'land_speed_terrestrial_2',
     'energy_consumption_aquatic_1', 'energy_consumption_aquatic_2', 'energy_consumption_amphibious_1', 'energy_consumption_amphibious_2',
     'energy_consumption_terrestrial_1', 'energy_consumption_terrestrial_2',
     'vision_range_aquatic_1', 'vision_range_aquatic_2', 'vision_range_amphibious_1', 'vision_range_amphibious_2',
     'vision_range_terrestrial_1', 'vision_range_terrestrial_2'],
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
    # Diet and habitat preference gene defaults
    'diet_type_1': 1.0, 'diet_type_2': 1.0,  # 0=carnivore, 1=omnivore, 2=herbivore
    'habitat_preference_1': 1.0, 'habitat_preference_2': 1.0,  # 0=aquatic, 1=amphibious, 2=terrestrial
    # Speed in water gene defaults
    'speed_in_water_aquatic_1': 5.0, 'speed_in_water_aquatic_2': 5.0,      # Default speed in water for aquatic agents
    'speed_in_water_amphibious_1': 3.0, 'speed_in_water_amphibious_2': 3.0, # Default speed in water for amphibious agents
    'speed_in_water_terrestrial_1': 1.0, 'speed_in_water_terrestrial_2': 1.0, # Default speed in water for terrestrial agents
    # Speed on land gene defaults
    'land_speed_aquatic_1': 2.0, 'land_speed_aquatic_2': 2.0,          # Default speed on land for aquatic agents
    'land_speed_amphibious_1': 4.0, 'land_speed_amphibious_2': 4.0,       # Default speed on land for amphibious agents
    'land_speed_terrestrial_1': 5.5, 'land_speed_terrestrial_2': 5.5,      # Default speed on land for terrestrial agents
    # Energy consumption gene defaults
    'energy_consumption_aquatic_1': 0.8, 'energy_consumption_aquatic_2': 0.8,  # Default energy consumption rate for aquatic agents
    'energy_consumption_amphibious_1': 1.0, 'energy_consumption_amphibious_2': 1.0, # Default energy consumption rate for amphibious agents
    'energy_consumption_terrestrial_1': 0.9, 'energy_consumption_terrestrial_2': 0.9, # Default energy consumption rate for terrestrial agents
    # Vision range gene defaults
    'vision_range_aquatic_1': 80.0, 'vision_range_aquatic_2': 80.0,       # Default vision range for aquatic agents in water
    'vision_range_amphibious_1': 100.0, 'vision_range_amphibious_2': 100.0,   # Default vision range for amphibious agents
    'vision_range_terrestrial_1': 120.0, 'vision_range_terrestrial_2': 120.0,  # Default vision range for terrestrial agents on land
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
    # Diet and habitat preference gene standard deviations
    'diet_type_1': 0.3, 'diet_type_2': 0.3,
    'habitat_preference_1': 0.3, 'habitat_preference_2': 0.3,
    # Speed in water gene standard deviations
    'speed_in_water_aquatic_1': 0.5, 'speed_in_water_aquatic_2': 0.5,
    'speed_in_water_amphibious_1': 0.5, 'speed_in_water_amphibious_2': 0.5,
    'speed_in_water_terrestrial_1': 0.5, 'speed_in_water_terrestrial_2': 0.5,
    # Speed on land gene standard deviations
    'land_speed_aquatic_1': 0.3, 'land_speed_aquatic_2': 0.3,
    'land_speed_amphibious_1': 0.3, 'land_speed_amphibious_2': 0.3,
    'land_speed_terrestrial_1': 0.3, 'land_speed_terrestrial_2': 0.3,
    # Energy consumption gene standard deviations
    'energy_consumption_aquatic_1': 0.1, 'energy_consumption_aquatic_2': 0.1,
    'energy_consumption_amphibious_1': 0.1, 'energy_consumption_amphibious_2': 0.1,
    'energy_consumption_terrestrial_1': 0.1, 'energy_consumption_terrestrial_2': 0.1,
    # Vision range gene standard deviations
    'vision_range_aquatic_1': 5.0, 'vision_range_aquatic_2': 5.0,
    'vision_range_amphibious_1': 5.0, 'vision_range_amphibious_2': 5.0,
    'vision_range_terrestrial_1': 5.0, 'vision_range_terrestrial_2': 5.0,
}

# Brain gene std uses config value
# V2 Architecture supports up to 318 weights for RNN
for i in range(318):
    GENE_STDS[f'brain_w{i}'] = config.NN_WEIGHT_INIT_STD


class Genome:
    __slots__ = ('chromosomes', 'sex', '_gene_index')

    def __init__(self, chromosomes, sex=None):
        self.chromosomes = chromosomes
        self.sex = sex or random.choice(['male', 'female'])
        self._gene_index = None  # Lazy-loaded gene index

    def _build_gene_index(self):
        """Build an index of gene names to gene objects for fast lookup."""
        self._gene_index = {}
        for chrom in self.chromosomes:
            for gene in chrom.genes:
                self._gene_index[gene.name] = gene

    def get_gene(self, name):
        """Find a gene by name across all chromosomes."""
        # Build index lazily if not already built
        if self._gene_index is None:
            self._build_gene_index()

        return self._gene_index.get(name)

    def all_genes(self):
        """Iterator over all genes in the genome."""
        for chrom in self.chromosomes:
            for gene in chrom.genes:
                yield gene

    def copy(self):
        new_genome = Genome(
            [c.copy() for c in self.chromosomes],
            self.sex
        )
        # Don't copy the gene index since it will be rebuilt lazily when needed
        return new_genome

    @staticmethod
    def create_with_traits(trait_dict, sex=None):
        """
        Create a genome with specific trait values.

        Args:
            trait_dict: Dictionary mapping trait names to desired values
            sex: Sex of the agent ('male' or 'female'), randomly chosen if None

        Returns:
            Genome instance with specified traits
        """
        chromosomes = []
        for chrom_genes in CHROMOSOME_LAYOUT:
            genes = []
            for gene_name in chrom_genes:
                # Check if this gene's trait is specified in the trait dictionary
                trait_key = gene_name.replace('_1', '').replace('_2', '').replace('_3', '').replace('_mod', '')
                if trait_key in trait_dict:
                    # Use the specified value for this trait
                    value = trait_dict[trait_key]
                    # Create gene with the specific value (using both alleles set to the same value for consistency)
                    genes.append(Gene.create_fixed(gene_name, value))
                else:
                    # Use default random generation if not specified
                    mean = GENE_DEFAULTS.get(gene_name, 0.0)
                    std = GENE_STDS.get(gene_name, 1.0)
                    genes.append(Gene.create_random(gene_name, mean, std))
            chromosomes.append(Chromosome(genes))
        return Genome(chromosomes, sex or random.choice(['male', 'female']))

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
