import random
from src.utils.vector import Vector2
import config


class FoodClusterManager:
    """Manages food cluster centers that drift over time."""

    def __init__(self, settings=None):
        self.settings = settings or {}
        self.centers = []
        self.time_since_shift = 0.0
        self._init_centers()

    def _init_centers(self):
        for _ in range(self.settings.get('NUM_FOOD_CLUSTERS', 5)):
            pos = Vector2(
                random.uniform(50, self.settings.get('WORLD_WIDTH', 1000) - 50),
                random.uniform(50, self.settings.get('WORLD_HEIGHT', 800) - 50)
            )
            self.centers.append(pos)

    def update(self, dt):
        """Drift cluster centers periodically."""
        self.time_since_shift += dt
        if self.time_since_shift >= self.settings.get('SEASON_SHIFT_INTERVAL', 30.0):
            self.time_since_shift = 0.0
            self._shift_centers()

    def _shift_centers(self):
        """Shift each center by Gaussian offset."""
        for i in range(len(self.centers)):
            dx = random.gauss(0, 30.0)
            dy = random.gauss(0, 30.0)
            new_x = self.centers[i].x + dx
            new_y = self.centers[i].y + dy
            # Keep within world bounds with margin
            new_x = max(30, min(self.settings.get('WORLD_WIDTH', 1000) - 30, new_x))
            new_y = max(30, min(self.settings.get('WORLD_HEIGHT', 800) - 30, new_y))
            self.centers[i] = Vector2(new_x, new_y)

    def get_spawn_position(self):
        """Get a food spawn position near a random cluster center."""
        center = random.choice(self.centers)
        dx = random.gauss(0, self.settings.get('FOOD_CLUSTER_SPREAD', 40.0))
        dy = random.gauss(0, self.settings.get('FOOD_CLUSTER_SPREAD', 40.0))
        x = (center.x + dx) % self.settings.get('WORLD_WIDTH', 1000)
        y = (center.y + dy) % self.settings.get('WORLD_HEIGHT', 800)
        return Vector2(x, y)
