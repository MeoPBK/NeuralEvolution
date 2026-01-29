from src.utils.vector import Vector2


class Food:
    __slots__ = ('pos', 'energy', 'alive')

    def __init__(self, pos, energy=30.0):
        self.pos = pos
        self.energy = energy
        self.alive = True
