"""
Terrain generator for creating realistic mountain chains and rivers.
"""
import math
import random
from src.entities.obstacle import Obstacle
from src.utils.vector import Vector2


class TerrainGenerator:
    """Generates realistic terrain features like mountain chains and rivers."""

    @staticmethod
    def generate_mountain_chain(world_width, world_height, orientation='horizontal',
                                position_ratio=0.5, length_ratio=0.8, roughness=0.3,
                                num_segments=15, gap_probability=0.10):
        """
        Generate a realistic mountain chain with circular peaks (top-down view).

        Args:
            world_width: Width of the world
            world_height: Height of the world
            orientation: 'horizontal' or 'vertical'
            position_ratio: Position along the perpendicular axis (0.0-1.0)
            length_ratio: How much of the world the chain spans (0.0-1.0)
            roughness: How much the chain curves (0.0-1.0)
            num_segments: Number of main mountain peaks
            gap_probability: Probability of gaps (passes) in the chain

        Returns:
            List of Obstacle objects forming the mountain chain
        """
        obstacles = []

        # Base radius for mountains
        base_radius = min(world_width, world_height) * 0.035

        # Generate a smooth path using sine waves
        def generate_path_offset(t, roughness):
            offset = 0
            offset += math.sin(t * 2.5 + random.random() * 10) * roughness * 0.6
            offset += math.sin(t * 5.0 + random.random() * 10) * roughness * 0.3
            return offset

        if orientation == 'horizontal':
            start_x = world_width * (1 - length_ratio) / 2
            end_x = world_width - start_x
            base_y = world_height * position_ratio
            chain_length = end_x - start_x

            # Determine gaps
            gap_positions = set()
            for i in range(num_segments):
                if random.random() < gap_probability and 2 < i < num_segments - 2:
                    gap_positions.add(i)

            for i in range(num_segments):
                if i in gap_positions:
                    continue

                t = i / num_segments
                path_offset = generate_path_offset(t * math.pi * 2, roughness) * world_height * 0.12

                x_pos = start_x + t * chain_length
                y_center = base_y + path_offset

                # Size varies - larger in the middle
                distance_from_center = abs(t - 0.5) * 2
                size_factor = 1.0 - distance_from_center * 0.3

                # Main peak
                main_radius = base_radius * size_factor * random.uniform(0.9, 1.3)
                obstacles.append(Obstacle(
                    Vector2(x_pos, y_center),
                    main_radius * 2, main_radius * 2,
                    'mountain', shape='circle', radius=main_radius
                ))

                # Overlapping smaller peaks to create a ridge
                num_sub_peaks = random.randint(2, 4)
                for _ in range(num_sub_peaks):
                    sub_radius = main_radius * random.uniform(0.4, 0.7)
                    offset_angle = random.uniform(0, math.pi * 2)
                    offset_dist = main_radius * random.uniform(0.3, 0.8)
                    sub_x = x_pos + math.cos(offset_angle) * offset_dist
                    sub_y = y_center + math.sin(offset_angle) * offset_dist

                    obstacles.append(Obstacle(
                        Vector2(sub_x, sub_y),
                        sub_radius * 2, sub_radius * 2,
                        'mountain', shape='circle', radius=sub_radius
                    ))

        else:
            # Vertical chain
            start_y = world_height * (1 - length_ratio) / 2
            end_y = world_height - start_y
            base_x = world_width * position_ratio
            chain_length = end_y - start_y

            gap_positions = set()
            for i in range(num_segments):
                if random.random() < gap_probability and 2 < i < num_segments - 2:
                    gap_positions.add(i)

            for i in range(num_segments):
                if i in gap_positions:
                    continue

                t = i / num_segments
                path_offset = generate_path_offset(t * math.pi * 2, roughness) * world_width * 0.12

                y_pos = start_y + t * chain_length
                x_center = base_x + path_offset

                distance_from_center = abs(t - 0.5) * 2
                size_factor = 1.0 - distance_from_center * 0.3

                main_radius = base_radius * size_factor * random.uniform(0.9, 1.3)
                obstacles.append(Obstacle(
                    Vector2(x_center, y_pos),
                    main_radius * 2, main_radius * 2,
                    'mountain', shape='circle', radius=main_radius
                ))

                num_sub_peaks = random.randint(2, 4)
                for _ in range(num_sub_peaks):
                    sub_radius = main_radius * random.uniform(0.4, 0.7)
                    offset_angle = random.uniform(0, math.pi * 2)
                    offset_dist = main_radius * random.uniform(0.3, 0.8)
                    sub_x = x_center + math.cos(offset_angle) * offset_dist
                    sub_y = y_pos + math.sin(offset_angle) * offset_dist

                    obstacles.append(Obstacle(
                        Vector2(sub_x, sub_y),
                        sub_radius * 2, sub_radius * 2,
                        'mountain', shape='circle', radius=sub_radius
                    ))

        return obstacles

    @staticmethod
    def generate_river(world_width, world_height, orientation='vertical',
                       position_ratio=0.5, meander_strength=0.15, river_width=20,
                       num_points=20):
        """
        Generate a realistic meandering river.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            orientation: 'vertical' (north-south) or 'horizontal' (east-west)
            position_ratio: Base position along the perpendicular axis (0.0-1.0)
            meander_strength: How much the river meanders (0.0-0.5)
            river_width: Width of the river
            num_points: Number of segments

        Returns:
            List of Obstacle objects forming the river
        """
        obstacles = []

        if orientation == 'vertical':
            # River flows from top to bottom
            base_x = world_width * position_ratio
            segment_height = world_height / num_points

            # Generate meander path using sine waves with noise
            points = []
            phase = random.random() * math.pi * 2
            frequency = random.uniform(1.5, 3.0)

            for i in range(num_points + 1):
                y = i * segment_height
                # Combine sine wave with noise for natural meander
                meander = (math.sin(frequency * i / num_points * math.pi + phase) *
                          world_width * meander_strength)
                meander += (random.random() - 0.5) * world_width * meander_strength * 0.3
                x = base_x + meander
                points.append((x, y))

            # Create river segments connecting the points
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]

                # Calculate segment parameters
                seg_x = min(x1, x2) - river_width / 2
                seg_y = y1
                seg_width = abs(x2 - x1) + river_width
                seg_height = y2 - y1 + 2  # Small overlap to prevent gaps

                obstacles.append(Obstacle(
                    Vector2(seg_x, seg_y),
                    seg_width,
                    seg_height,
                    'water_barrier'
                ))
        else:
            # River flows from left to right
            base_y = world_height * position_ratio
            segment_width = world_width / num_points

            # Generate meander path
            points = []
            phase = random.random() * math.pi * 2
            frequency = random.uniform(1.5, 3.0)

            for i in range(num_points + 1):
                x = i * segment_width
                meander = (math.sin(frequency * i / num_points * math.pi + phase) *
                          world_height * meander_strength)
                meander += (random.random() - 0.5) * world_height * meander_strength * 0.3
                y = base_y + meander
                points.append((x, y))

            # Create river segments
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]

                seg_x = x1
                seg_y = min(y1, y2) - river_width / 2
                seg_width = x2 - x1 + 2
                seg_height = abs(y2 - y1) + river_width

                obstacles.append(Obstacle(
                    Vector2(seg_x, seg_y),
                    seg_width,
                    seg_height,
                    'water_barrier'
                ))

        return obstacles

    @staticmethod
    def generate_diagonal_mountain_range(world_width, world_height,
                                         start_corner='top_left',
                                         coverage=0.6, roughness=0.25):
        """
        Generate a diagonal mountain range with circular peaks from one corner towards another.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            start_corner: 'top_left', 'top_right', 'bottom_left', 'bottom_right'
            coverage: How far the range extends (0.0-1.0)
            roughness: Variation in the path (0.0-1.0)

        Returns:
            List of Obstacle objects
        """
        obstacles = []
        base_radius = min(world_width, world_height) * 0.03

        corners = {
            'top_left': ((0, 0), (world_width * coverage, world_height * coverage)),
            'top_right': ((world_width, 0), (world_width * (1 - coverage), world_height * coverage)),
            'bottom_left': ((0, world_height), (world_width * coverage, world_height * (1 - coverage))),
            'bottom_right': ((world_width, world_height), (world_width * (1 - coverage), world_height * (1 - coverage))),
        }

        start, end = corners.get(start_corner, corners['top_left'])

        num_segments = 12
        dx = (end[0] - start[0]) / num_segments
        dy = (end[1] - start[1]) / num_segments

        for i in range(num_segments):
            if random.random() < 0.12 and i > 0 and i < num_segments - 1:
                continue

            base_x = start[0] + i * dx
            base_y = start[1] + i * dy

            offset_x = (random.random() - 0.5) * world_width * roughness * 0.15
            offset_y = (random.random() - 0.5) * world_height * roughness * 0.15

            # Main peak
            main_radius = base_radius * random.uniform(0.9, 1.4)
            obstacles.append(Obstacle(
                Vector2(base_x + offset_x, base_y + offset_y),
                main_radius * 2, main_radius * 2,
                'mountain', shape='circle', radius=main_radius
            ))

            # Secondary peaks
            num_sub = random.randint(1, 3)
            for _ in range(num_sub):
                sub_radius = main_radius * random.uniform(0.4, 0.7)
                angle = random.uniform(0, math.pi * 2)
                dist = main_radius * random.uniform(0.4, 0.9)
                sub_x = base_x + offset_x + math.cos(angle) * dist
                sub_y = base_y + offset_y + math.sin(angle) * dist

                obstacles.append(Obstacle(
                    Vector2(sub_x, sub_y),
                    sub_radius * 2, sub_radius * 2,
                    'mountain', shape='circle', radius=sub_radius
                ))

        return obstacles

    @staticmethod
    def generate_lake(world_width, world_height, center_x_ratio=0.5,
                      center_y_ratio=0.5, size_ratio=0.15, irregularity=0.3):
        """
        Generate an irregular lake shape.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of lake center (0.0-1.0)
            center_y_ratio: Y position of lake center (0.0-1.0)
            size_ratio: Size of the lake relative to world (0.0-0.3)
            irregularity: How irregular the shape is (0.0-1.0)

        Returns:
            List of Obstacle objects forming the lake
        """
        obstacles = []

        center_x = world_width * center_x_ratio
        center_y = world_height * center_y_ratio
        base_radius = min(world_width, world_height) * size_ratio

        # Create lake from overlapping circles/ellipses
        num_circles = random.randint(4, 8)

        for _ in range(num_circles):
            # Random offset from center
            angle = random.random() * math.pi * 2
            dist = random.random() * base_radius * 0.4
            cx = center_x + math.cos(angle) * dist
            cy = center_y + math.sin(angle) * dist

            # Random size
            width = base_radius * random.uniform(0.5, 1.0) * (1 + irregularity * (random.random() - 0.5))
            height = base_radius * random.uniform(0.5, 1.0) * (1 + irregularity * (random.random() - 0.5))

            obstacles.append(Obstacle(
                Vector2(cx - width/2, cy - height/2),
                width,
                height,
                'water_barrier'
            ))

        return obstacles
