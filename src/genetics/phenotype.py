TRAIT_GENE_MAP = {
    'speed': ['speed_1', 'speed_2', 'speed_3', 'speed_3_mod'],
    'size': ['size_1', 'size_2', 'size_mod'],
    'vision_range': ['vision_1', 'vision_2'],
    'energy_efficiency': ['efficiency_1', 'efficiency_2', 'efficiency_3'],
    'reproduction_urge': ['repro_1', 'repro_2'],
    'camouflage': ['camo_1'],
    'aggression': ['aggro_1', 'aggro_2'],
    'max_age': ['max_age_1', 'max_age_2'],
    'virus_resistance': ['virus_resistance_1', 'virus_resistance_2'],
    # Color traits for genetic inheritance
    'color_red': ['color_red_1', 'color_red_2'],
    'color_green': ['color_green_1', 'color_green_2'],
    'color_blue': ['color_blue_1', 'color_blue_2'],
    # Disease resistance traits for genetic inheritance
    'disease_resistance_1': ['disease_resistance_1'],
    'disease_resistance_2': ['disease_resistance_2'],
    'disease_resistance_3': ['disease_resistance_3'],
    'disease_resistance_4': ['disease_resistance_4'],
    # Morphological traits (used when MORPHOLOGY_TRAITS_ENABLED)
    'agility': ['agility_1', 'agility_2'],
    'armor': ['armor_1', 'armor_2'],
}

# Sex-based modifiers (subtle)
SEX_MODIFIERS = {
    'male': {
        'speed': 1.05,
        'size': 1.05,
        'energy_efficiency': 0.97,
        'max_age': 0.95,  # Males might have slightly shorter lifespans
    },
    'female': {
        'speed': 0.97,
        'size': 0.97,
        'energy_efficiency': 1.05,
        'max_age': 1.05,  # Females might have slightly longer lifespans
    },
}


def compute_phenotype(genome, trait_ranges):
    """Compute observable traits from genome.

    For each trait, average the expression of its contributing genes,
    apply sex-based modifiers, and clamp to valid range.
    """
    phenotype = {}

    for trait_name, gene_names in TRAIT_GENE_MAP.items():
        values = []
        for gene_name in gene_names:
            gene = genome.get_gene(gene_name)
            if gene is not None:
                values.append(gene.express())

        if not values:
            phenotype[trait_name] = 0.0
            continue

        raw_value = sum(values) / len(values)

        # Apply sex modifier
        sex_mods = SEX_MODIFIERS.get(genome.sex, {})
        modifier = sex_mods.get(trait_name, 1.0)
        raw_value *= modifier

        # Clamp to valid range
        if trait_name in trait_ranges:
            lo, hi = trait_ranges[trait_name]
            raw_value = max(lo, min(hi, raw_value))

        phenotype[trait_name] = raw_value

    return phenotype
