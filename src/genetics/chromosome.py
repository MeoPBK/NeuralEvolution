import random
from .gene import Gene
from .allele import Allele


class Chromosome:
    __slots__ = ('genes',)

    def __init__(self, genes):
        self.genes = genes

    def create_gamete_alleles(self):
        """Select one allele per gene for a gamete."""
        return [gene.get_gamete_allele() for gene in self.genes]

    def copy(self):
        return Chromosome([g.copy() for g in self.genes])

    @staticmethod
    def crossover(chrom_a, chrom_b, crossover_rate):
        """Single-point crossover between two chromosomes.
        Returns two new offspring chromosomes."""
        n = len(chrom_a.genes)
        if n == 0:
            return chrom_a.copy(), chrom_b.copy()

        # Get gamete alleles from each parent chromosome
        gamete_a = chrom_a.create_gamete_alleles()
        gamete_b = chrom_b.create_gamete_alleles()

        if random.random() < crossover_rate and n > 1:
            # Single-point crossover
            point = random.randint(1, n - 1)
            child_alleles_1 = gamete_a[:point] + gamete_b[point:]
            child_alleles_2 = gamete_b[:point] + gamete_a[point:]
        else:
            child_alleles_1 = gamete_a
            child_alleles_2 = gamete_b

        # Build offspring chromosomes (pair alleles from each parent)
        genes_1 = []
        genes_2 = []
        for i in range(n):
            name = chrom_a.genes[i].name
            genes_1.append(Gene(name, child_alleles_1[i], child_alleles_2[i]))
            genes_2.append(Gene(name, child_alleles_2[i].copy(), child_alleles_1[i].copy()))

        return Chromosome(genes_1), Chromosome(genes_2)

    def __repr__(self):
        return f"Chromosome({len(self.genes)} genes)"
