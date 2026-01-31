import random
from src.utils.vector import Vector2
import config


class Food:
    __slots__ = ('pos', 'energy', 'alive', 'color', 'is_tree_food')

    def __init__(self, pos, energy=30.0, is_tree_food=False):
        self.pos = pos
        self.energy = energy
        self.alive = True
        self.is_tree_food = is_tree_food
        # Set color based on whether it's tree food or regular food
        if is_tree_food:
            # Different colors for tree food (fruits/nuts)
            # Randomly choose from fruit-like colors
            fruit_colors = [
                (255, 165, 0),   # Orange (orange)
                (255, 0, 0),     # Red (apple)
                (255, 192, 203), # Pink (cherry)
                (139, 69, 19),   # Brown (nut)
                (255, 215, 0),   # Gold (apricot)
                (0, 128, 0),     # Green (apple)
                (128, 0, 128),   # Purple (grape)
            ]
            self.color = random.choice(fruit_colors)  # Random fruit color for tree food
        else:
            self.color = config.FOOD_COLOR  # Regular food color
