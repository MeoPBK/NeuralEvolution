class SpatialGrid:
    """Spatial partitioning for O(1) neighbor queries."""

    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width // cell_size) + 1
        self.rows = int(height // cell_size) + 1
        self.cells = {}

    def clear(self):
        self.cells.clear()

    def _key(self, x, y):
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        return (col, row)

    def insert(self, entity):
        key = self._key(entity.pos.x, entity.pos.y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(entity)

    def query_radius(self, pos, radius, exclude=None):
        """Find all entities within radius of pos."""
        results = []
        r_sq = radius * radius
        min_col = int((pos.x - radius) // self.cell_size)
        max_col = int((pos.x + radius) // self.cell_size)
        min_row = int((pos.y - radius) // self.cell_size)
        max_row = int((pos.y + radius) // self.cell_size)

        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                cell = self.cells.get((col, row))
                if cell is None:
                    continue
                for entity in cell:
                    if entity is exclude:
                        continue
                    if not entity.alive:
                        continue
                    dx = entity.pos.x - pos.x
                    dy = entity.pos.y - pos.y
                    if dx * dx + dy * dy <= r_sq:
                        results.append(entity)
        return results

    def query_nearest(self, pos, radius, exclude=None):
        """Find the nearest entity within radius."""
        candidates = self.query_radius(pos, radius, exclude)
        if not candidates:
            return None
        best = None
        best_dist = float('inf')
        for entity in candidates:
            dx = entity.pos.x - pos.x
            dy = entity.pos.y - pos.y
            d = dx * dx + dy * dy
            if d < best_dist:
                best_dist = d
                best = entity
        return best
