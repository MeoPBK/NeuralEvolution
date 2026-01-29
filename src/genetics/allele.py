import random


class Allele:
    __slots__ = ('value', 'dominance')

    def __init__(self, value, dominance=0.5):
        self.value = float(value)
        self.dominance = max(0.0, min(1.0, float(dominance)))

    def copy(self):
        return Allele(self.value, self.dominance)

    @staticmethod
    def random(mean, std=0.5):
        value = random.gauss(mean, std)
        dominance = random.uniform(0.2, 0.8)
        return Allele(value, dominance)

    def __repr__(self):
        return f"Allele(v={self.value:.2f}, d={self.dominance:.2f})"
