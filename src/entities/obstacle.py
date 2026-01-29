"""Obstacle entity for the simulation."""
import pygame
import math
from src.utils.vector import Vector2


class Obstacle:
    """Static obstacle that agents cannot pass through."""

    _next_id = 0

    def __init__(self, pos, width, height, obstacle_type='wall', shape='rect', radius=None):
        Obstacle._next_id += 1
        self.id = Obstacle._next_id
        self.pos = pos  # For circles, this is the center position
        self.width = width
        self.height = height
        self.obstacle_type = obstacle_type  # 'wall', 'mountain', 'water_barrier', etc.
        self.shape = shape  # 'rect' or 'circle'
        self.radius = radius if radius else max(width, height) / 2  # For circular obstacles
        self.alive = True
        self.color = self._get_color_by_type()

    def _get_color_by_type(self):
        """Get color based on obstacle type."""
        colors = {
            'wall': (100, 100, 100),      # Gray
            'mountain': (139, 69, 19),    # Brown
            'water_barrier': (60, 130, 220),  # Blue
            'cliff': (120, 120, 120),     # Dark gray
        }
        return colors.get(self.obstacle_type, (100, 100, 100))

    def get_center(self):
        """Get the center position of the obstacle."""
        if self.shape == 'circle':
            return self.pos  # pos is already center for circles
        else:
            return Vector2(self.pos.x + self.width / 2, self.pos.y + self.height / 2)

    def contains_point(self, point):
        """Check if a point is inside this obstacle."""
        if self.shape == 'circle':
            dx = point.x - self.pos.x
            dy = point.y - self.pos.y
            return (dx * dx + dy * dy) <= (self.radius * self.radius)
        else:
            return (self.pos.x <= point.x <= self.pos.x + self.width and
                    self.pos.y <= point.y <= self.pos.y + self.height)

    def intersects_rect(self, rect_pos, rect_size):
        """Check if a rectangle intersects with this obstacle."""
        if self.shape == 'circle':
            # Find closest point on rectangle to circle center
            closest_x = max(rect_pos.x, min(self.pos.x, rect_pos.x + rect_size))
            closest_y = max(rect_pos.y, min(self.pos.y, rect_pos.y + rect_size))
            dx = self.pos.x - closest_x
            dy = self.pos.y - closest_y
            return (dx * dx + dy * dy) < (self.radius * self.radius)
        else:
            return (self.pos.x <= rect_pos.x + rect_size and
                    self.pos.x + self.width >= rect_pos.x and
                    self.pos.y <= rect_pos.y + rect_size and
                    self.pos.y + self.height >= rect_pos.y)

    def collides_with_circle(self, circle_pos, circle_radius):
        """Check if a circle collides with this obstacle."""
        if self.shape == 'circle':
            # Circle-circle collision
            dx = circle_pos.x - self.pos.x
            dy = circle_pos.y - self.pos.y
            dist_sq = dx * dx + dy * dy
            combined_radius = self.radius + circle_radius
            return dist_sq < (combined_radius * combined_radius)
        else:
            # Circle-rectangle collision
            closest_x = max(self.pos.x, min(circle_pos.x, self.pos.x + self.width))
            closest_y = max(self.pos.y, min(circle_pos.y, self.pos.y + self.height))
            dist_x = circle_pos.x - closest_x
            dist_y = circle_pos.y - closest_y
            return (dist_x * dist_x + dist_y * dist_y) < (circle_radius * circle_radius)

    def get_push_vector(self, circle_pos, circle_radius):
        """Calculate the push vector to move a circle out of this obstacle."""
        if self.shape == 'circle':
            # Push away from circle center
            dx = circle_pos.x - self.pos.x
            dy = circle_pos.y - self.pos.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.001:
                return Vector2(1, 0) * (self.radius + circle_radius + 1)
            # Normalize and scale to push out
            push_dist = self.radius + circle_radius + 1 - dist
            return Vector2(dx / dist * push_dist, dy / dist * push_dist)
        else:
            # Push away from rectangle
            closest_x = max(self.pos.x, min(circle_pos.x, self.pos.x + self.width))
            closest_y = max(self.pos.y, min(circle_pos.y, self.pos.y + self.height))
            dx = circle_pos.x - closest_x
            dy = circle_pos.y - closest_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.001:
                return Vector2(0, -1) * (circle_radius + 1)
            push_dist = circle_radius + 1 - dist
            return Vector2(dx / dist * push_dist, dy / dist * push_dist)

    def draw(self, screen):
        """Draw the obstacle."""
        if self.alive:
            if self.shape == 'circle':
                pygame.draw.circle(screen, self.color,
                                  (int(self.pos.x), int(self.pos.y)), int(self.radius))
            else:
                pygame.draw.rect(screen, self.color,
                                (self.pos.x, self.pos.y, self.width, self.height))