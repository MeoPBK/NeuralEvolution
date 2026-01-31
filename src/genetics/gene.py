import random
from .allele import Allele


class Gene:
    __slots__ = ('name', 'allele_a', 'allele_b')

    def __init__(self, name, allele_a, allele_b):
        self.name = name
        self.allele_a = allele_a
        self.allele_b = allele_b

    def express(self):
        """Phenotypic expression using dominance-weighted average."""
        total_dom = self.allele_a.dominance + self.allele_b.dominance
        if total_dom < 1e-8:
            return (self.allele_a.value + self.allele_b.value) / 2.0
        w_a = self.allele_a.dominance / total_dom
        w_b = self.allele_b.dominance / total_dom
        return self.allele_a.value * w_a + self.allele_b.value * w_b

    def get_gamete_allele(self):
        """Randomly select one allele for a gamete."""
        if random.random() < 0.5:
            return self.allele_a.copy()
        return self.allele_b.copy()

    def copy(self):
        return Gene(self.name, self.allele_a.copy(), self.allele_b.copy())

    @staticmethod
    def create_fixed(name, value):
        """Create a gene with both alleles set to the same fixed value."""
        a = Allele(value, 0.5)  # Use standard dominance
        b = Allele(value, 0.5)  # Use standard dominance
        return Gene(name, a, b)

    @staticmethod
    def create_random(name, mean, std=0.5):
        a = Allele.random(mean, std)
        b = Allele.random(mean, std)
        return Gene(name, a, b)

    def __repr__(self):
        return f"Gene({self.name}: {self.allele_a}, {self.allele_b} -> {self.express():.2f})"
