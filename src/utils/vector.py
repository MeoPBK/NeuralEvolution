import math
import random


class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __repr__(self):
        return f"Vector2({self.x:.2f}, {self.y:.2f})"

    def length_sq(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return math.sqrt(self.length_sq())

    def normalized(self):
        mag = self.length()
        if mag < 1e-8:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def distance_sq_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def limit(self, max_length):
        lsq = self.length_sq()
        if lsq > max_length * max_length:
            mag = math.sqrt(lsq)
            return Vector2(self.x / mag * max_length, self.y / mag * max_length)
        return Vector2(self.x, self.y)

    def copy(self):
        return Vector2(self.x, self.y)

    def tuple(self):
        return (self.x, self.y)

    def int_tuple(self):
        return (int(self.x), int(self.y))

    @staticmethod
    def random_unit():
        angle = random.uniform(0, 2 * math.pi)
        return Vector2(math.cos(angle), math.sin(angle))

    @staticmethod
    def random_in_rect(width, height):
        return Vector2(random.uniform(0, width), random.uniform(0, height))
