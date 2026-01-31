"""Obstacle entity for the simulation."""
import pygame
import math
import random
from src.utils.vector import Vector2


class Obstacle:
    """Static obstacle that agents cannot pass through."""

    _next_id = 0

    def __init__(self, pos, width, height, obstacle_type='wall', shape='rect', radius=None, tree_type=None, tree_foliage_color=None, rock_type=None, rock_mineral_veins=None):
        Obstacle._next_id += 1
        self.id = Obstacle._next_id
        self.pos = pos  # For circles, this is the center position
        self.width = width
        self.height = height
        self.obstacle_type = obstacle_type  # 'wall', 'mountain', 'water_barrier', 'tree', 'rock', etc.
        self.shape = shape  # 'rect', 'circle', 'tree', 'rock'
        self.radius = radius if radius else max(width, height) / 2  # For circular obstacles
        self.alive = True
        self.color = self._get_color_by_type()

        # Tree-specific properties
        self.tree_type = tree_type  # 'deciduous', 'coniferous', 'palm', etc.
        self.tree_foliage_color = tree_foliage_color or (30, 100, 30)  # Default green foliage

        # Rock-specific properties (initialize for all obstacles to prevent AttributeError)
        self.rock_type = rock_type or 'generic'  # 'granite', 'limestone', 'sandstone', 'basalt', 'generic'
        self.rock_mineral_veins = rock_mineral_veins or []  # List of mineral vein positions and colors
        self.rock_surface_details = []  # For storing surface texture details

        # For tree shape, calculate trunk and foliage dimensions
        if self.obstacle_type == 'tree':
            self.shape = 'tree'
            # Calculate trunk dimensions (typically 1/5 to 1/3 of the total size)
            self.trunk_width = width * 0.15
            self.trunk_height = height * 0.4
            self.foliage_width = width
            self.foliage_height = height * 0.7
            # Center the trunk at the bottom of the foliage
            self.trunk_pos = Vector2(
                pos.x + (width - self.trunk_width) / 2,
                pos.y + height - self.trunk_height
            )
            # Center the foliage above the trunk
            self.foliage_pos = Vector2(
                pos.x + (width - self.foliage_width) / 2,
                pos.y + height - self.foliage_height - self.trunk_height * 0.2
            )

        # For rock shape, initialize rock-specific properties
        elif self.obstacle_type == 'rock':
            self.shape = 'circle'  # Rocks are typically round/circular
            # Generate mineral veins for the rock
            self._generate_rock_mineral_veins()
            # Generate surface details for texture
            self._generate_rock_surface_details()
        else:
            # For non-rock obstacles, ensure empty lists to prevent errors
            self.rock_mineral_veins = []
            self.rock_surface_details = []

    def _generate_rock_mineral_veins(self):
        """Generate mineral veins for the rock to give it realistic internal structure."""
        if self.rock_type == 'granite':
            # Granite has distinctive mineral veins
            vein_count = int(self.radius / 8)  # More veins for larger rocks
            for _ in range(vein_count):
                # Vein position within the rock
                angle = random.uniform(0, 2 * math.pi)
                distance_from_center = random.uniform(0, self.radius * 0.8)
                x = self.pos.x + math.cos(angle) * distance_from_center
                y = self.pos.y + math.sin(angle) * distance_from_center
                # Vein characteristics
                vein_length = random.uniform(self.radius * 0.3, self.radius * 0.7)
                vein_thickness = random.uniform(1, 3)
                # Different minerals in granite
                vein_colors = [
                    (200, 200, 150),  # Quartz
                    (180, 160, 100),  # Feldspar
                    (50, 50, 100),    # Biotite
                    (100, 100, 100),  # Hornblende
                ]
                vein_color = random.choice(vein_colors)
                self.rock_mineral_veins.append({
                    'pos': Vector2(x, y),
                    'length': vein_length,
                    'thickness': vein_thickness,
                    'color': vein_color,
                    'angle': angle
                })
        elif self.rock_type == 'limestone':
            # Limestone often has fossil-like patterns
            pattern_count = int(self.radius / 10)
            for _ in range(pattern_count):
                angle = random.uniform(0, 2 * math.pi)
                distance_from_center = random.uniform(0, self.radius * 0.7)
                x = self.pos.x + math.cos(angle) * distance_from_center
                y = self.pos.y + math.sin(angle) * distance_from_center
                pattern_size = random.uniform(2, 6)
                pattern_color = (180, 170, 160)  # Light grayish
                self.rock_mineral_veins.append({
                    'pos': Vector2(x, y),
                    'size': pattern_size,
                    'color': pattern_color,
                    'type': 'fossil'
                })
        elif self.rock_type == 'sandstone':
            # Sandstone has layered patterns
            layer_count = int(self.radius / 5)
            for i in range(layer_count):
                angle = random.uniform(0, 2 * math.pi)
                distance_from_center = random.uniform(0, self.radius * 0.9)
                x = self.pos.x + math.cos(angle) * distance_from_center
                y = self.pos.y + math.sin(angle) * distance_from_center
                layer_width = random.uniform(1, 4)
                layer_color = random.choice([
                    (190, 170, 150),  # Reddish sandstone
                    (200, 180, 160),  # Tan sandstone
                    (180, 160, 140),  # Brown sandstone
                ])
                self.rock_mineral_veins.append({
                    'pos': Vector2(x, y),
                    'width': layer_width,
                    'color': layer_color,
                    'angle': angle
                })
        elif self.rock_type == 'basalt':
            # Basalt has crystalline patterns
            crystal_count = int(self.radius / 6)
            for _ in range(crystal_count):
                angle = random.uniform(0, 2 * math.pi)
                distance_from_center = random.uniform(0, self.radius * 0.8)
                x = self.pos.x + math.cos(angle) * distance_from_center
                y = self.pos.y + math.sin(angle) * distance_from_center
                crystal_size = random.uniform(1, 3)
                crystal_color = random.choice([
                    (80, 80, 100),   # Dark gray
                    (60, 60, 80),    # Very dark gray
                    (100, 100, 120), # Lighter gray
                ])
                self.rock_mineral_veins.append({
                    'pos': Vector2(x, y),
                    'size': crystal_size,
                    'color': crystal_color,
                    'type': 'crystal'
                })
        else:  # generic rock
            # Generic rock with random mineral patterns
            pattern_count = int(self.radius / 7)
            for _ in range(pattern_count):
                angle = random.uniform(0, 2 * math.pi)
                distance_from_center = random.uniform(0, self.radius * 0.8)
                x = self.pos.x + math.cos(angle) * distance_from_center
                y = self.pos.y + math.sin(angle) * distance_from_center
                pattern_size = random.uniform(1, 4)
                pattern_color = random.choice([
                    (120, 120, 120),  # Gray
                    (100, 100, 100),  # Darker gray
                    (140, 140, 140),  # Lighter gray
                    (150, 130, 110),  # Brownish-gray
                ])
                self.rock_mineral_veins.append({
                    'pos': Vector2(x, y),
                    'size': pattern_size,
                    'color': pattern_color,
                    'type': 'generic'
                })

    def _generate_rock_surface_details(self):
        """Generate surface details for the rock to add texture."""
        # Add some random surface details like small bumps or indentations
        detail_count = int(self.radius / 5)
        for _ in range(detail_count):
            angle = random.uniform(0, 2 * math.pi)
            distance_from_center = random.uniform(self.radius * 0.6, self.radius * 0.9)
            x = self.pos.x + math.cos(angle) * distance_from_center
            y = self.pos.y + math.sin(angle) * distance_from_center
            detail_size = random.uniform(1, 3)
            detail_depth = random.uniform(-2, 2)  # Positive for bump, negative for indentation
            self.rock_surface_details.append({
                'pos': Vector2(x, y),
                'size': detail_size,
                'depth': detail_depth
            })

    def _get_color_by_type(self):
        """Get color based on obstacle type."""
        colors = {
            'wall': (100, 100, 100),      # Gray
            'mountain': (139, 69, 19),    # Brown
            'water_barrier': (60, 130, 220),  # Blue
            'cliff': (120, 120, 120),     # Dark gray
            'tree': (101, 67, 33),        # Brown for tree trunk
            'rock': self._get_rock_color(),  # Dynamic rock color based on type
        }
        return colors.get(self.obstacle_type, (100, 100, 100))

    def _get_rock_color(self):
        """Get color based on rock type."""
        rock_colors = {
            'granite': (140, 130, 120),    # Light gray with brown tones
            'limestone': (180, 170, 160),  # Light grayish-white
            'sandstone': (190, 170, 150),  # Warm reddish-brown
            'basalt': (80, 80, 90),        # Dark gray-blue
        }
        # Safely get rock_type attribute, defaulting to 'generic' if not set
        rock_type = getattr(self, 'rock_type', 'generic')
        return rock_colors.get(rock_type, (120, 120, 120))  # Default gray

    def get_center(self):
        """Get the center position of the obstacle."""
        if self.shape == 'circle':
            return self.pos  # pos is already center for circles
        else:
            return Vector2(self.pos.x + self.width / 2, self.pos.y + self.height / 2)

    def contains_point(self, point):
        """Check if a point is inside this obstacle."""
        if self.obstacle_type == 'tree':
            # For trees, check collision with both trunk and foliage
            # Check trunk collision
            if (self.trunk_pos.x <= point.x <= self.trunk_pos.x + self.trunk_width and
                self.trunk_pos.y <= point.y <= self.trunk_pos.y + self.trunk_height):
                return True

            # Check foliage collision (approximate as circle or oval)
            foliage_center_x = self.foliage_pos.x + self.foliage_width / 2
            foliage_center_y = self.foliage_pos.y + self.foliage_height / 2
            foliage_radius = min(self.foliage_width, self.foliage_height) * 0.6

            dx = point.x - foliage_center_x
            dy = point.y - foliage_center_y
            return (dx * dx + dy * dy) <= (foliage_radius * foliage_radius)
        elif self.shape == 'circle':
            dx = point.x - self.pos.x
            dy = point.y - self.pos.y
            return (dx * dx + dy * dy) <= (self.radius * self.radius)
        else:
            return (self.pos.x <= point.x <= self.pos.x + self.width and
                    self.pos.y <= point.y <= self.pos.y + self.height)

    def intersects_rect(self, rect_pos, rect_size):
        """Check if a rectangle intersects with this obstacle."""
        if self.obstacle_type == 'tree':
            # For trees, check intersection with both trunk and foliage
            # Check trunk intersection
            if (self.trunk_pos.x <= rect_pos.x + rect_size and
                self.trunk_pos.x + self.trunk_width >= rect_pos.x and
                self.trunk_pos.y <= rect_pos.y + rect_size and
                self.trunk_pos.y + self.trunk_height >= rect_pos.y):
                return True

            # Check foliage intersection (approximate as circle)
            foliage_center_x = self.foliage_pos.x + self.foliage_width / 2
            foliage_center_y = self.foliage_pos.y + self.foliage_height / 2
            foliage_radius = min(self.foliage_width, self.foliage_height) * 0.6

            # Find closest point on rectangle to foliage center
            closest_x = max(rect_pos.x, min(foliage_center_x, rect_pos.x + rect_size))
            closest_y = max(rect_pos.y, min(foliage_center_y, rect_pos.y + rect_size))
            dx = foliage_center_x - closest_x
            dy = foliage_center_y - closest_y
            return (dx * dx + dy * dy) < (foliage_radius * foliage_radius)
        elif self.shape == 'circle':
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
        # Check if this obstacle has a polygon representation (for rivers)
        if hasattr(self, 'river_polygon') and self.river_polygon:
            # Use polygon collision detection for rivers
            return self._collides_with_polygon(circle_pos, circle_radius)
        elif self.obstacle_type == 'tree':
            # For trees, check collision with both trunk and foliage
            # Check trunk collision
            closest_x = max(self.trunk_pos.x, min(circle_pos.x, self.trunk_pos.x + self.trunk_width))
            closest_y = max(self.trunk_pos.y, min(circle_pos.y, self.trunk_pos.y + self.trunk_height))

            # Calculate distance between circle's center and closest point on trunk
            dist_x = circle_pos.x - closest_x
            dist_y = circle_pos.y - closest_y
            dist_sq = dist_x * dist_x + dist_y * dist_y

            if dist_sq < (circle_radius * circle_radius):
                return True

            # Check foliage collision (approximate as circle)
            foliage_center_x = self.foliage_pos.x + self.foliage_width / 2
            foliage_center_y = self.foliage_pos.y + self.foliage_height / 2
            foliage_radius = min(self.foliage_width, self.foliage_height) * 0.6

            dx = circle_pos.x - foliage_center_x
            dy = circle_pos.y - foliage_center_y
            dist_sq = dx * dx + dy * dy
            combined_radius = foliage_radius + circle_radius
            return dist_sq < (combined_radius * combined_radius)
        elif self.shape == 'circle':
            # Circle-circle collision
            dx = circle_pos.x - self.pos.x
            dy = circle_pos.y - self.pos.y
            dist_sq = dx * dx + dy * dy
            combined_radius = self.radius + circle_radius
            return dist_sq < (combined_radius * combined_radius)
        else:
            # Circle-rectangle collision - improved algorithm
            # Find the closest point on the rectangle to the circle's center
            closest_x = max(self.pos.x, min(circle_pos.x, self.pos.x + self.width))
            closest_y = max(self.pos.y, min(circle_pos.y, self.pos.y + self.height))

            # Calculate distance between circle's center and this closest point
            dist_x = circle_pos.x - closest_x
            dist_y = circle_pos.y - closest_y

            # If the distance is less than the circle's radius, there's a collision
            dist_sq = dist_x * dist_x + dist_y * dist_y
            return dist_sq < (circle_radius * circle_radius)

    def _collides_with_polygon(self, circle_pos, circle_radius):
        """Check if a circle collides with a polygon (used for rivers)."""
        if not hasattr(self, 'river_polygon') or not self.river_polygon:
            return False

        # Check if the circle center is inside the polygon
        if self._point_in_polygon(circle_pos, self.river_polygon):
            return True

        # Check if the circle collides with any of the polygon edges
        polygon = self.river_polygon
        for i in range(len(polygon)):
            p1 = Vector2(polygon[i][0], polygon[i][1])
            p2 = Vector2(polygon[(i + 1) % len(polygon)][0], polygon[(i + 1) % len(polygon)][1])

            # Calculate distance from circle center to line segment
            if self._distance_to_line_segment(circle_pos, p1, p2) < circle_radius:
                return True

        return False

    def _point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting algorithm."""
        x, y = point.x, point.y
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def _distance_to_line_segment(self, point, line_start, line_end):
        """Calculate the shortest distance from a point to a line segment."""
        # Vector from line_start to line_end
        line_vec = line_end - line_start
        line_len_sq = line_vec.length_sq()

        if line_len_sq == 0:
            # Line segment is actually a point
            return (point - line_start).length()

        # Calculate projection of point onto line
        t = max(0, min(1, (point - line_start).dot(line_vec) / line_len_sq))

        # Calculate closest point on line segment
        projection = line_start + line_vec * t

        # Return distance from point to closest point on line segment
        return (point - projection).length()

    def get_push_vector(self, circle_pos, circle_radius):
        """Calculate the push vector to move a circle out of this obstacle."""
        # Check if this is a polygon river
        if hasattr(self, 'river_polygon') and self.river_polygon:
            # For polygon rivers, find the closest edge and push away from it
            return self._get_push_vector_polygon(circle_pos, circle_radius)
        elif self.obstacle_type == 'tree':
            # For trees, calculate push vector considering both trunk and foliage
            # First check which part (trunk or foliage) is closer to the circle
            # Calculate distances to both trunk center and foliage center
            trunk_center_x = self.trunk_pos.x + self.trunk_width / 2
            trunk_center_y = self.trunk_pos.y + self.trunk_height / 2

            foliage_center_x = self.foliage_pos.x + self.foliage_width / 2
            foliage_center_y = self.foliage_pos.y + self.foliage_height / 2

            # Calculate distance to trunk center
            dx_trunk = circle_pos.x - trunk_center_x
            dy_trunk = circle_pos.y - trunk_center_y
            dist_trunk_sq = dx_trunk * dx_trunk + dy_trunk * dy_trunk

            # Calculate distance to foliage center
            dx_foliage = circle_pos.x - foliage_center_x
            dy_foliage = circle_pos.y - foliage_center_y
            dist_foliage_sq = dx_foliage * dx_foliage + dy_foliage * dy_foliage

            # Use the closer part to determine the push vector
            if dist_trunk_sq <= dist_foliage_sq:
                # Push away from trunk
                dist = math.sqrt(dist_trunk_sq)
                if dist < 0.001:
                    # If circle is at the trunk center, push in a default direction
                    return Vector2(1, 0) * (max(self.trunk_width, self.trunk_height)/2 + circle_radius + 1)
                # Normalize and scale to push out
                push_dist = max(self.trunk_width, self.trunk_height)/2 + circle_radius + 1 - dist
                return Vector2(dx_trunk / dist * push_dist, dy_trunk / dist * push_dist)
            else:
                # Push away from foliage
                foliage_radius = min(self.foliage_width, self.foliage_height) * 0.6
                dist = math.sqrt(dist_foliage_sq)
                if dist < 0.001:
                    # If circle is at the foliage center, push in a default direction
                    return Vector2(1, 0) * (foliage_radius + circle_radius + 1)
                # Normalize and scale to push out
                push_dist = foliage_radius + circle_radius + 1 - dist
                return Vector2(dx_foliage / dist * push_dist, dy_foliage / dist * push_dist)
        elif self.shape == 'circle':
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

    def _get_push_vector_polygon(self, circle_pos, circle_radius):
        """Calculate the push vector to move a circle out of a polygon obstacle."""
        if not hasattr(self, 'river_polygon') or not self.river_polygon:
            # Fallback to rectangle push if no polygon exists
            closest_x = max(self.pos.x, min(circle_pos.x, self.pos.x + self.width))
            closest_y = max(self.pos.y, min(circle_pos.y, self.pos.y + self.height))
            dx = circle_pos.x - closest_x
            dy = circle_pos.y - closest_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.001:
                return Vector2(0, -1) * (circle_radius + 1)
            push_dist = circle_radius + 1 - dist
            return Vector2(dx / dist * push_dist, dy / dist * push_dist)

        # Find the closest edge of the polygon to the circle
        min_dist = float('inf')
        closest_edge_normal = Vector2(0, 1)  # Default direction
        closest_edge_dist = 0

        polygon = self.river_polygon
        for i in range(len(polygon)):
            p1 = Vector2(polygon[i][0], polygon[i][1])
            p2 = Vector2(polygon[(i + 1) % len(polygon)][0], polygon[(i + 1) % len(polygon)][1])

            # Calculate distance from circle center to line segment
            dist, closest_point, normal = self._distance_and_normal_to_line_segment(circle_pos, p1, p2)

            if dist < min_dist:
                min_dist = dist
                closest_edge_normal = normal
                closest_edge_dist = dist

        # Calculate push distance to move the circle outside the polygon
        push_distance = circle_radius - min_dist + 1  # Add 1 for safety margin
        return closest_edge_normal * push_distance

    def _distance_and_normal_to_line_segment(self, point, line_start, line_end):
        """Calculate the shortest distance from a point to a line segment and the normal vector."""
        # Vector from line_start to line_end
        line_vec = line_end - line_start
        line_len_sq = line_vec.length_sq()

        if line_len_sq == 0:
            # Line segment is actually a point
            vec_to_point = point - line_start
            dist = vec_to_point.length()
            if dist == 0:
                return 0, line_start, Vector2(1, 0)  # Return arbitrary normal if point is on the point
            return dist, line_start, vec_to_point.normalized()

        # Calculate projection of point onto line
        t = max(0, min(1, (point - line_start).dot(line_vec) / line_len_sq))

        # Calculate closest point on line segment
        closest_point = line_start + line_vec * t

        # Calculate distance from point to closest point on line segment
        vec_to_closest = point - closest_point
        dist = vec_to_closest.length()

        # Calculate normal vector (perpendicular to the line segment, pointing away from it)
        normal = Vector2(-line_vec.y, line_vec.x).normalized()

        # Make sure the normal points away from the line segment in the direction of the point
        if vec_to_closest.dot(normal) < 0:
            normal = normal * -1

        return dist, closest_point, normal

    def draw(self, screen):
        """Draw the obstacle."""
        if self.alive:
            if self.obstacle_type == 'rock':
                # Draw rock with realistic features
                # Draw the main rock body
                pygame.draw.circle(screen, self.color,
                                  (int(self.pos.x), int(self.pos.y)), int(self.radius))

                # Draw mineral veins inside the rock
                for vein in self.rock_mineral_veins:
                    if 'length' in vein:  # Linear vein (like in granite)
                        # Draw a line for the vein
                        start_x = int(vein['pos'].x)
                        start_y = int(vein['pos'].y)
                        end_x = int(start_x + math.cos(vein['angle']) * vein['length'])
                        end_y = int(start_y + math.sin(vein['angle']) * vein['length'])
                        pygame.draw.line(screen, vein['color'],
                                       (start_x, start_y), (end_x, end_y), int(vein['thickness']))
                    elif 'size' in vein:  # Circular pattern (like fossils in limestone)
                        # Draw a circle for the pattern
                        pygame.draw.circle(screen, vein['color'],
                                         (int(vein['pos'].x), int(vein['pos'].y)), int(vein['size']))

                # Draw surface details (bumps and indentations)
                for detail in self.rock_surface_details:
                    # Draw small circles to represent surface texture
                    if detail['depth'] > 0:
                        detail_color = tuple(max(0, min(255, c + 20)) for c in self.color)
                    else:
                        detail_color = tuple(max(0, min(255, c - 20)) for c in self.color)
                    pygame.draw.circle(screen, detail_color,
                                     (int(detail['pos'].x), int(detail['pos'].y)),
                                     int(detail['size']))

                # Draw a subtle highlight to give 3D appearance
                highlight_pos = (int(self.pos.x - self.radius * 0.3), int(self.pos.y - self.radius * 0.3))
                highlight_radius = int(self.radius * 0.2)
                highlight_color = tuple(min(255, c + 40) for c in self.color)
                pygame.draw.circle(screen, highlight_color, highlight_pos, highlight_radius)

            elif self.shape == 'circle':
                pygame.draw.circle(screen, self.color,
                                  (int(self.pos.x), int(self.pos.y)), int(self.radius))
            elif self.obstacle_type == 'tree':
                # Draw tree with trunk and foliage
                # Draw trunk
                trunk_rect = pygame.Rect(
                    int(self.trunk_pos.x),
                    int(self.trunk_pos.y),
                    int(self.trunk_width),
                    int(self.trunk_height)
                )
                pygame.draw.rect(screen, self.color, trunk_rect)

                # Draw foliage based on tree type
                if self.tree_type == 'coniferous':
                    # Draw coniferous tree (triangular shape)
                    foliage_points = [
                        (int(self.foliage_pos.x + self.foliage_width / 2), int(self.foliage_pos.y)),  # Top
                        (int(self.foliage_pos.x), int(self.foliage_pos.y + self.foliage_height)),   # Bottom left
                        (int(self.foliage_pos.x + self.foliage_width), int(self.foliage_pos.y + self.foliage_height))  # Bottom right
                    ]
                    pygame.draw.polygon(screen, self.tree_foliage_color, foliage_points)
                elif self.tree_type == 'palm':
                    # Draw palm tree (trunk with top foliage)
                    # Draw trunk (taller and thinner than regular trees)
                    palm_trunk_rect = pygame.Rect(
                        int(self.pos.x + self.width / 2 - self.trunk_width / 3),
                        int(self.foliage_pos.y + self.foliage_height * 0.3),
                        int(self.trunk_width * 0.6),
                        int(self.trunk_height * 1.2)
                    )
                    pygame.draw.rect(screen, self.color, palm_trunk_rect)

                    # Draw palm fronds (simplified as a circle for now)
                    palm_foliage_center = (int(self.pos.x + self.width / 2), int(self.foliage_pos.y + self.foliage_height * 0.2))
                    pygame.draw.circle(screen, self.tree_foliage_color, palm_foliage_center, int(self.foliage_width * 0.4))
                else:  # Default to deciduous tree
                    # Draw deciduous tree (round/oval foliage)
                    foliage_center_x = int(self.foliage_pos.x + self.foliage_width / 2)
                    foliage_center_y = int(self.foliage_pos.y + self.foliage_height / 2)
                    foliage_radius = int(min(self.foliage_width, self.foliage_height) * 0.6)
                    pygame.draw.circle(screen, self.tree_foliage_color, (foliage_center_x, foliage_center_y), foliage_radius)

                    # Add some texture/detail to the foliage
                    pygame.draw.circle(screen, (25, 90, 25), (foliage_center_x - foliage_radius//3, foliage_center_y - foliage_radius//4), foliage_radius//2)
                    pygame.draw.circle(screen, (35, 110, 35), (foliage_center_x + foliage_radius//2, foliage_center_y + foliage_radius//3), foliage_radius//2)
            else:
                pygame.draw.rect(screen, self.color,
                                (self.pos.x, self.pos.y, self.width, self.height))