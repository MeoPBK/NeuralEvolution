from src.utils.vector import Vector2


class WaterSource:
    """A persistent water source. Agents within radius can drink."""

    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius
        self.alive = True  # Always True, water sources persist
