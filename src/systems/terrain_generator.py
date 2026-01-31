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
    def generate_rock(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                     size_ratio=0.05, rock_type='generic', num_rocks=1):
        """
        Generate realistic rocks with rounded shapes and mineral compositions.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of rock center (0.0-1.0)
            center_y_ratio: Y position of rock center (0.0-1.0)
            size_ratio: Size of the rock relative to world (0.0-0.1)
            rock_type: Type of rock ('granite', 'limestone', 'sandstone', 'basalt', 'generic')
            num_rocks: Number of rocks to generate

        Returns:
            List of Obstacle objects representing rocks
        """
        obstacles = []

        # Calculate base radius based on world dimensions and size ratio
        base_radius = min(world_width, world_height) * size_ratio

        for i in range(num_rocks):
            # Add some random positioning to spread rocks
            center_x = world_width * center_x_ratio + random.uniform(-world_width * 0.1, world_width * 0.1)
            center_y = world_height * center_y_ratio + random.uniform(-world_height * 0.1, world_height * 0.1)

            # Ensure rocks stay within world boundaries
            center_x = max(base_radius, min(world_width - base_radius, center_x))
            center_y = max(base_radius, min(world_height - base_radius, center_y))

            # Add some random variation to size
            radius = base_radius * random.uniform(0.8, 1.2)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(center_x - radius, center_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_rock_cluster(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                             cluster_size=0.1, rock_density=0.3, rock_type='generic'):
        """
        Generate a cluster of rocks in a specific area.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of cluster center (0.0-1.0)
            center_y_ratio: Y position of cluster center (0.0-1.0)
            cluster_size: Size of the cluster area (0.0-0.3)
            rock_density: Density of rocks in the cluster (0.0-1.0)
            rock_type: Type of rocks ('granite', 'limestone', 'sandstone', 'basalt', 'generic')

        Returns:
            List of Obstacle objects representing rock cluster
        """
        obstacles = []

        # Calculate cluster area
        cluster_width = world_width * cluster_size
        cluster_height = world_height * cluster_size

        # Calculate cluster center
        cluster_center_x = world_width * center_x_ratio
        cluster_center_y = world_height * center_y_ratio

        # Calculate number of rocks based on density
        estimated_rock_area = (cluster_width * cluster_height) * rock_density
        avg_rock_size = min(world_width, world_height) * 0.03  # Average rock size
        num_rocks = int(estimated_rock_area / (avg_rock_size * avg_rock_size))

        # Generate rocks within the cluster area
        for _ in range(num_rocks):
            # Random position within cluster area
            pos_x = cluster_center_x + random.uniform(-cluster_width/2, cluster_width/2)
            pos_y = cluster_center_y + random.uniform(-cluster_height/2, cluster_height/2)

            # Ensure position stays within world boundaries
            pos_x = max(avg_rock_size, min(world_width - avg_rock_size, pos_x))
            pos_y = max(avg_rock_size, min(world_height - avg_rock_size, pos_y))

            # Random rock size
            radius = avg_rock_size * random.uniform(0.5, 1.5)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(pos_x - radius, pos_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_river(world_width, world_height, orientation='vertical',
                       position_ratio=0.5, meander_strength=0.15, river_width=20,
                       num_points=20):
        """
        Generate a realistic meandering river as a smooth curved polygon.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            orientation: 'vertical' (north-south) or 'horizontal' (east-west)
            position_ratio: Base position along the perpendicular axis (0.0-1.0)
            meander_strength: How much the river meanders (0.0-0.5)
            river_width: Width of the river
            num_points: Number of points to define the river path

        Returns:
            List of Obstacle objects forming the river as a smooth curved polygon
        """
        # Try to use scipy for smooth interpolation, fallback to simple approach if not available
        scipy_available = False
        try:
            from scipy.interpolate import interp1d
            import numpy as np
            scipy_available = True
        except ImportError:
            pass  # scipy not available, will use simple approach

        obstacles = []

        if orientation == 'vertical':
            # River flows from top to bottom
            base_x = world_width * position_ratio

            # Generate meander path using sine waves with noise
            points = []
            phase = random.random() * math.pi * 2
            frequency = random.uniform(1.5, 3.0)

            for i in range(num_points + 1):
                y = i * (world_height / num_points)
                # Combine sine wave with noise for natural meander
                meander = (math.sin(frequency * i / num_points * math.pi + phase) *
                          world_width * meander_strength)
                meander += (random.random() - 0.5) * world_width * meander_strength * 0.3
                x = base_x + meander
                points.append((x, y))

            # Create a smooth curve using interpolation
            if len(points) >= 4 and scipy_available:  # Need at least 4 points for interpolation
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                
                # Create cubic spline interpolation
                # Use scipy for smooth interpolation
                t_values = np.linspace(0, 1, len(ys))
                f_x = interp1d(t_values, xs, kind='cubic', fill_value='extrapolate')
                f_y = interp1d(t_values, ys, kind='cubic', fill_value='extrapolate')
                
                # Generate more points for a smoother curve
                t_smooth = np.linspace(0, 1, num_points * 3)  # 3x more points
                smooth_xs = f_x(t_smooth)
                smooth_ys = f_y(t_smooth)
                
                # Create a polygonal approximation of the river
                river_points = [(float(x), float(y)) for x, y in zip(smooth_xs, smooth_ys)]
            else:
                river_points = points

            # Create a single polygon obstacle representing the entire river
            if len(river_points) > 1:
                # Create a polygon by expanding the centerline to both sides
                river_polygon = []
                
                # Calculate the polygon points by expanding perpendicular to the river path
                for i in range(len(river_points)):
                    if i == 0:
                        # For the first point, use the direction to the next point
                        dx = river_points[1][0] - river_points[0][0]
                        dy = river_points[1][1] - river_points[0][1]
                    elif i == len(river_points) - 1:
                        # For the last point, use the direction from the previous point
                        dx = river_points[-1][0] - river_points[-2][0]
                        dy = river_points[-1][1] - river_points[-2][1]
                    else:
                        # For middle points, average the directions to previous and next points
                        dx1 = river_points[i][0] - river_points[i-1][0]
                        dy1 = river_points[i][1] - river_points[i-1][1]
                        dx2 = river_points[i+1][0] - river_points[i][0]
                        dy2 = river_points[i+1][1] - river_points[i][1]
                        dx = (dx1 + dx2) / 2
                        dy = (dy1 + dy2) / 2
                    
                    # Calculate perpendicular direction (normal to the river)
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        nx = -dy / length  # Perpendicular vector
                        ny = dx / length
                    else:
                        nx, ny = 0, 1  # Default perpendicular if no direction
                    
                    # Add points on both sides of the river
                    left_point = (river_points[i][0] + nx * river_width/2, river_points[i][1] + ny * river_width/2)
                    right_point = (river_points[i][0] - nx * river_width/2, river_points[i][1] - ny * river_width/2)
                    
                    river_polygon.append(left_point)
                
                # Add the right-side points in reverse order to close the polygon
                for i in range(len(river_points)-1, -1, -1):
                    if i == 0:
                        dx = river_points[1][0] - river_points[0][0]
                        dy = river_points[1][1] - river_points[0][1]
                    elif i == len(river_points) - 1:
                        dx = river_points[-1][0] - river_points[-2][0]
                        dy = river_points[-1][1] - river_points[-2][1]
                    else:
                        dx1 = river_points[i][0] - river_points[i-1][0]
                        dy1 = river_points[i][1] - river_points[i-1][1]
                        dx2 = river_points[i+1][0] - river_points[i][0]
                        dy2 = river_points[i+1][1] - river_points[i][1]
                        dx = (dx1 + dx2) / 2
                        dy = (dy1 + dy2) / 2
                    
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        nx = -dy / length
                        ny = dx / length
                    else:
                        nx, ny = 0, 1
                    
                    right_point = (river_points[i][0] - nx * river_width/2, river_points[i][1] - ny * river_width/2)
                    river_polygon.append(right_point)

                # Create a single polygon obstacle for the river
                # Since the Obstacle class doesn't support polygons directly, we'll create a bounding rectangle
                # and note that the actual shape is the polygon
                min_x = min(p[0] for p in river_polygon)
                max_x = max(p[0] for p in river_polygon)
                min_y = min(p[1] for p in river_polygon)
                max_y = max(p[1] for p in river_polygon)
                
                # Create a rectangular obstacle that encompasses the river
                width = max_x - min_x
                height = max_y - min_y
                pos = Vector2(min_x, min_y)
                
                # Create the main river obstacle
                river_obstacle = Obstacle(
                    pos,
                    width,
                    height,
                    'water_barrier',
                    shape='rect'
                )
                
                # Store the polygon points as an attribute for more accurate collision detection
                river_obstacle.river_polygon = river_polygon
                river_obstacle.river_centerline = river_points
                river_obstacle.river_width = river_width  # Store the original width for reference
                obstacles.append(river_obstacle)

        else:
            # River flows from left to right
            base_y = world_height * position_ratio

            # Generate meander path
            points = []
            phase = random.random() * math.pi * 2
            frequency = random.uniform(1.5, 3.0)

            for i in range(num_points + 1):
                x = i * (world_width / num_points)
                meander = (math.sin(frequency * i / num_points * math.pi + phase) *
                          world_height * meander_strength)
                meander += (random.random() - 0.5) * world_height * meander_strength * 0.3
                y = base_y + meander
                points.append((x, y))

            # Create a smooth curve using interpolation
            if len(points) >= 4 and scipy_available:  # Need at least 4 points for interpolation
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                
                # Create cubic spline interpolation
                # Use scipy for smooth interpolation
                t_values = np.linspace(0, 1, len(ys))
                f_x = interp1d(t_values, xs, kind='cubic', fill_value='extrapolate')
                f_y = interp1d(t_values, ys, kind='cubic', fill_value='extrapolate')
                
                # Generate more points for a smoother curve
                t_smooth = np.linspace(0, 1, num_points * 3)  # 3x more points
                smooth_xs = f_x(t_smooth)
                smooth_ys = f_y(t_smooth)
                
                # Create a polygonal approximation of the river
                river_points = [(float(x), float(y)) for x, y in zip(smooth_xs, smooth_ys)]
            else:
                river_points = points

            # Create a single polygon obstacle representing the entire river
            if len(river_points) > 1:
                # Create a polygon by expanding the centerline to both sides
                river_polygon = []
                
                # Calculate the polygon points by expanding perpendicular to the river path
                for i in range(len(river_points)):
                    if i == 0:
                        # For the first point, use the direction to the next point
                        dx = river_points[1][0] - river_points[0][0]
                        dy = river_points[1][1] - river_points[0][1]
                    elif i == len(river_points) - 1:
                        # For the last point, use the direction from the previous point
                        dx = river_points[-1][0] - river_points[-2][0]
                        dy = river_points[-1][1] - river_points[-2][1]
                    else:
                        # For middle points, average the directions to previous and next points
                        dx1 = river_points[i][0] - river_points[i-1][0]
                        dy1 = river_points[i][1] - river_points[i-1][1]
                        dx2 = river_points[i+1][0] - river_points[i][0]
                        dy2 = river_points[i+1][1] - river_points[i][1]
                        dx = (dx1 + dx2) / 2
                        dy = (dy1 + dy2) / 2
                    
                    # Calculate perpendicular direction (normal to the river)
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        nx = -dy / length  # Perpendicular vector
                        ny = dx / length
                    else:
                        nx, ny = 0, 1  # Default perpendicular if no direction
                    
                    # Add points on both sides of the river
                    left_point = (river_points[i][0] + nx * river_width/2, river_points[i][1] + ny * river_width/2)
                    right_point = (river_points[i][0] - nx * river_width/2, river_points[i][1] - ny * river_width/2)
                    
                    river_polygon.append(left_point)
                
                # Add the right-side points in reverse order to close the polygon
                for i in range(len(river_points)-1, -1, -1):
                    if i == 0:
                        dx = river_points[1][0] - river_points[0][0]
                        dy = river_points[1][1] - river_points[0][1]
                    elif i == len(river_points) - 1:
                        dx = river_points[-1][0] - river_points[-2][0]
                        dy = river_points[-1][1] - river_points[-2][1]
                    else:
                        dx1 = river_points[i][0] - river_points[i-1][0]
                        dy1 = river_points[i][1] - river_points[i-1][1]
                        dx2 = river_points[i+1][0] - river_points[i][0]
                        dy2 = river_points[i+1][1] - river_points[i][1]
                        dx = (dx1 + dx2) / 2
                        dy = (dy1 + dy2) / 2
                    
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        nx = -dy / length
                        ny = dx / length
                    else:
                        nx, ny = 0, 1
                    
                    right_point = (river_points[i][0] - nx * river_width/2, river_points[i][1] - ny * river_width/2)
                    river_polygon.append(right_point)

                # Create a single polygon obstacle for the river
                # Since the Obstacle class doesn't support polygons directly, we'll create a bounding rectangle
                # and note that the actual shape is the polygon
                min_x = min(p[0] for p in river_polygon)
                max_x = max(p[0] for p in river_polygon)
                min_y = min(p[1] for p in river_polygon)
                max_y = max(p[1] for p in river_polygon)
                
                # Create a rectangular obstacle that encompasses the river
                width = max_x - min_x
                height = max_y - min_y
                pos = Vector2(min_x, min_y)
                
                # Create the main river obstacle
                river_obstacle = Obstacle(
                    pos,
                    width,
                    height,
                    'water_barrier',
                    shape='rect'
                )
                
                # Store the polygon points as an attribute for more accurate collision detection
                river_obstacle.river_polygon = river_polygon
                river_obstacle.river_centerline = river_points
                river_obstacle.river_width = river_width  # Store the original width for reference
                obstacles.append(river_obstacle)

        return obstacles

    @staticmethod
    def generate_rock(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                     size_ratio=0.05, rock_type='generic', num_rocks=1):
        """
        Generate realistic rocks with rounded shapes and mineral compositions.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of rock center (0.0-1.0)
            center_y_ratio: Y position of rock center (0.0-1.0)
            size_ratio: Size of the rock relative to world (0.0-0.1)
            rock_type: Type of rock ('granite', 'limestone', 'sandstone', 'basalt', 'generic')
            num_rocks: Number of rocks to generate

        Returns:
            List of Obstacle objects representing rocks
        """
        obstacles = []

        # Calculate base radius based on world dimensions and size ratio
        base_radius = min(world_width, world_height) * size_ratio

        for i in range(num_rocks):
            # Add some random positioning to spread rocks
            center_x = world_width * center_x_ratio + random.uniform(-world_width * 0.1, world_width * 0.1)
            center_y = world_height * center_y_ratio + random.uniform(-world_height * 0.1, world_height * 0.1)

            # Ensure rocks stay within world boundaries
            center_x = max(base_radius, min(world_width - base_radius, center_x))
            center_y = max(base_radius, min(world_height - base_radius, center_y))

            # Add some random variation to size
            radius = base_radius * random.uniform(0.8, 1.2)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(center_x - radius, center_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_rock_cluster(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                             cluster_size=0.1, rock_density=0.3, rock_type='generic'):
        """
        Generate a cluster of rocks in a specific area.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of cluster center (0.0-1.0)
            center_y_ratio: Y position of cluster center (0.0-1.0)
            cluster_size: Size of the cluster area (0.0-0.3)
            rock_density: Density of rocks in the cluster (0.0-1.0)
            rock_type: Type of rocks ('granite', 'limestone', 'sandstone', 'basalt', 'generic')

        Returns:
            List of Obstacle objects representing rock cluster
        """
        obstacles = []

        # Calculate cluster area
        cluster_width = world_width * cluster_size
        cluster_height = world_height * cluster_size

        # Calculate cluster center
        cluster_center_x = world_width * center_x_ratio
        cluster_center_y = world_height * center_y_ratio

        # Calculate number of rocks based on density
        estimated_rock_area = (cluster_width * cluster_height) * rock_density
        avg_rock_size = min(world_width, world_height) * 0.03  # Average rock size
        num_rocks = int(estimated_rock_area / (avg_rock_size * avg_rock_size))

        # Generate rocks within the cluster area
        for _ in range(num_rocks):
            # Random position within cluster area
            pos_x = cluster_center_x + random.uniform(-cluster_width/2, cluster_width/2)
            pos_y = cluster_center_y + random.uniform(-cluster_height/2, cluster_height/2)

            # Ensure position stays within world boundaries
            pos_x = max(avg_rock_size, min(world_width - avg_rock_size, pos_x))
            pos_y = max(avg_rock_size, min(world_height - avg_rock_size, pos_y))

            # Random rock size
            radius = avg_rock_size * random.uniform(0.5, 1.5)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(pos_x - radius, pos_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

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
    def generate_rock(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                     size_ratio=0.05, rock_type='generic', num_rocks=1):
        """
        Generate realistic rocks with rounded shapes and mineral compositions.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of rock center (0.0-1.0)
            center_y_ratio: Y position of rock center (0.0-1.0)
            size_ratio: Size of the rock relative to world (0.0-0.1)
            rock_type: Type of rock ('granite', 'limestone', 'sandstone', 'basalt', 'generic')
            num_rocks: Number of rocks to generate

        Returns:
            List of Obstacle objects representing rocks
        """
        obstacles = []

        # Calculate base radius based on world dimensions and size ratio
        base_radius = min(world_width, world_height) * size_ratio

        for i in range(num_rocks):
            # Add some random positioning to spread rocks
            center_x = world_width * center_x_ratio + random.uniform(-world_width * 0.1, world_width * 0.1)
            center_y = world_height * center_y_ratio + random.uniform(-world_height * 0.1, world_height * 0.1)

            # Ensure rocks stay within world boundaries
            center_x = max(base_radius, min(world_width - base_radius, center_x))
            center_y = max(base_radius, min(world_height - base_radius, center_y))

            # Add some random variation to size
            radius = base_radius * random.uniform(0.8, 1.2)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(center_x - radius, center_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_rock_cluster(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                             cluster_size=0.1, rock_density=0.3, rock_type='generic'):
        """
        Generate a cluster of rocks in a specific area.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of cluster center (0.0-1.0)
            center_y_ratio: Y position of cluster center (0.0-1.0)
            cluster_size: Size of the cluster area (0.0-0.3)
            rock_density: Density of rocks in the cluster (0.0-1.0)
            rock_type: Type of rocks ('granite', 'limestone', 'sandstone', 'basalt', 'generic')

        Returns:
            List of Obstacle objects representing rock cluster
        """
        obstacles = []

        # Calculate cluster area
        cluster_width = world_width * cluster_size
        cluster_height = world_height * cluster_size

        # Calculate cluster center
        cluster_center_x = world_width * center_x_ratio
        cluster_center_y = world_height * center_y_ratio

        # Calculate number of rocks based on density
        estimated_rock_area = (cluster_width * cluster_height) * rock_density
        avg_rock_size = min(world_width, world_height) * 0.03  # Average rock size
        num_rocks = int(estimated_rock_area / (avg_rock_size * avg_rock_size))

        # Generate rocks within the cluster area
        for _ in range(num_rocks):
            # Random position within cluster area
            pos_x = cluster_center_x + random.uniform(-cluster_width/2, cluster_width/2)
            pos_y = cluster_center_y + random.uniform(-cluster_height/2, cluster_height/2)

            # Ensure position stays within world boundaries
            pos_x = max(avg_rock_size, min(world_width - avg_rock_size, pos_x))
            pos_y = max(avg_rock_size, min(world_height - avg_rock_size, pos_y))

            # Random rock size
            radius = avg_rock_size * random.uniform(0.5, 1.5)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(pos_x - radius, pos_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_lake(world_width, world_height, center_x_ratio=0.5,
                      center_y_ratio=0.5, size_ratio=0.15, irregularity=0.3, settings=None):
        """
        Generate a realistic lake with irregular shoreline and depth variations.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of lake center (0.0-1.0)
            center_y_ratio: Y position of lake center (0.0-1.0)
            size_ratio: Size of the lake relative to world (0.0-0.3) - used when not uniform
            irregularity: How irregular the shape is (0.0-1.0)
            settings: Simulation settings dictionary (optional, for uniform lake size)

        Returns:
            List of Obstacle objects forming the lake
        """
        obstacles = []

        center_x = world_width * center_x_ratio
        center_y = world_height * center_y_ratio

        # Determine lake size based on settings
        if settings and settings.get('LAKE_SIZE_UNIFORM', False):
            # Use fixed size from settings
            base_radius = settings.get('LAKE_SIZE', 80.0) / 2.0
        else:
            # Use proportional size
            base_radius = min(world_width, world_height) * size_ratio

        # Create a main central body for the lake with more organic shape
        main_width = base_radius * 1.8
        main_height = base_radius * 1.8

        # Choose a lake type for more varied shapes
        lake_types = ['irregular', 'meandering', 'branching', 'crescent', 'multi_basin']
        lake_type = random.choice(lake_types)

        if lake_type == 'irregular':
            # Create an irregular lake with multiple overlapping parts to form organic shape
            # Start with a main body
            main_obstacle = Obstacle(
                Vector2(center_x - main_width/2, center_y - main_height/2),
                main_width,
                main_height,
                'water_barrier'
            )
            main_obstacle.shape = 'lake_main'
            obstacles.append(main_obstacle)

            # Add irregular extensions to make it look more organic
            num_extensions = random.randint(3, 7)
            for i in range(num_extensions):
                # Random angle for extension
                angle = random.uniform(0, 2 * math.pi)
                # Position extension at the edge of the main lake
                extension_dist = min(main_width, main_height) * 0.4
                ext_center_x = center_x + math.cos(angle) * extension_dist * 0.5
                ext_center_y = center_y + math.sin(angle) * extension_dist * 0.5

                # Extension size (smaller than main body)
                ext_width = main_width * random.uniform(0.2, 0.5)
                ext_height = main_height * random.uniform(0.2, 0.5)

                # Create extension part
                extension_obstacle = Obstacle(
                    Vector2(ext_center_x - ext_width/2, ext_center_y - ext_height/2),
                    ext_width,
                    ext_height,
                    'water_barrier'
                )
                extension_obstacle.shape = 'lake_main'
                obstacles.append(extension_obstacle)

            # Add some irregular bulges to the main body
            num_bulges = random.randint(2, 5)
            for i in range(num_bulges):
                angle = random.uniform(0, 2 * math.pi)
                # Position bulge at the edge of the main lake
                bulge_dist = min(main_width, main_height) * 0.45
                bulge_x = center_x + math.cos(angle) * bulge_dist
                bulge_y = center_y + math.sin(angle) * bulge_dist

                # Bulge size (smaller)
                bulge_width = main_width * random.uniform(0.15, 0.3)
                bulge_height = main_height * random.uniform(0.15, 0.3)

                bulge_obstacle = Obstacle(
                    Vector2(bulge_x - bulge_width/2, bulge_y - bulge_height/2),
                    bulge_width,
                    bulge_height,
                    'water_barrier'
                )
                bulge_obstacle.shape = 'lake_shoreline'
                obstacles.append(bulge_obstacle)

        elif lake_type == 'meandering':
            # Create a meandering, winding lake
            # Start with a main serpentine body
            num_segments = random.randint(4, 8)
            for i in range(num_segments):
                # Create segments that form a meandering path
                segment_angle = (i / num_segments) * math.pi * 2
                # Add some randomness to make it meander
                offset_distance = base_radius * 0.4 * (i / num_segments) + random.uniform(-0.1, 0.1) * base_radius
                # Add extra randomness to make it more natural
                pos_x = center_x + math.cos(segment_angle) * offset_distance * random.uniform(0.7, 1.3)
                pos_y = center_y + math.sin(segment_angle) * offset_distance * random.uniform(0.7, 1.3)

                # Each segment has different dimensions to create meandering effect
                width = main_width * random.uniform(0.2, 0.4)
                height = main_height * random.uniform(0.15, 0.35)

                main_obstacle = Obstacle(
                    Vector2(pos_x - width/2, pos_y - height/2),
                    width,
                    height,
                    'water_barrier'
                )
                main_obstacle.shape = 'lake_main'
                obstacles.append(main_obstacle)

            # Add connecting segments to make it look more like a continuous body of water
            for i in range(num_segments - 1):
                # Connect adjacent segments
                angle1 = (i / num_segments) * math.pi * 2
                angle2 = ((i + 1) / num_segments) * math.pi * 2

                x1 = center_x + math.cos(angle1) * base_radius * 0.4 * (i / num_segments) * random.uniform(0.7, 1.3)
                y1 = center_y + math.sin(angle1) * base_radius * 0.4 * (i / num_segments) * random.uniform(0.7, 1.3)

                x2 = center_x + math.cos(angle2) * base_radius * 0.4 * ((i + 1) / num_segments) * random.uniform(0.7, 1.3)
                y2 = center_y + math.sin(angle2) * base_radius * 0.4 * ((i + 1) / num_segments) * random.uniform(0.7, 1.3)

                # Midpoint between segments
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                connector_width = main_width * random.uniform(0.15, 0.3)
                connector_height = main_height * random.uniform(0.15, 0.3)

                connector_obstacle = Obstacle(
                    Vector2(mid_x - connector_width/2, mid_y - connector_height/2),
                    connector_width,
                    connector_height,
                    'water_barrier'
                )
                connector_obstacle.shape = 'lake_main'
                obstacles.append(connector_obstacle)

        elif lake_type == 'branching':
            # Create a branching lake with a main body and branches
            # Main body
            main_obstacle = Obstacle(
                Vector2(center_x - main_width/3, center_y - main_height/3),
                main_width * 0.6,
                main_height * 0.6,
                'water_barrier'
            )
            main_obstacle.shape = 'lake_main'
            obstacles.append(main_obstacle)

            # Branches
            num_branches = random.randint(2, 4)
            for i in range(num_branches):
                branch_angle = (i / num_branches) * 2 * math.pi
                branch_length = base_radius * random.uniform(0.4, 0.7)

                branch_x = center_x + math.cos(branch_angle) * branch_length * 0.5
                branch_y = center_y + math.sin(branch_angle) * branch_length * 0.5

                branch_width = main_width * random.uniform(0.2, 0.4)
                branch_height = main_height * random.uniform(0.15, 0.3)

                branch_obstacle = Obstacle(
                    Vector2(branch_x - branch_width/2, branch_y - branch_height/2),
                    branch_width,
                    branch_height,
                    'water_barrier'
                )
                branch_obstacle.shape = 'lake_main'
                obstacles.append(branch_obstacle)

            # Add some smaller tributaries to the branches
            for i in range(num_branches):
                branch_angle = (i / num_branches) * 2 * math.pi
                # Position tributary at the end of the branch
                branch_length = base_radius * random.uniform(0.4, 0.7)
                branch_x = center_x + math.cos(branch_angle) * branch_length * 0.5
                branch_y = center_y + math.sin(branch_angle) * branch_length * 0.5

                # Tributary angle slightly different from main branch
                tributary_angle = branch_angle + random.uniform(-0.5, 0.5)
                tributary_length = branch_length * 0.5

                tributary_x = branch_x + math.cos(tributary_angle) * tributary_length * 0.3
                tributary_y = branch_y + math.sin(tributary_angle) * tributary_length * 0.3

                tributary_width = main_width * random.uniform(0.1, 0.2)
                tributary_height = main_height * random.uniform(0.1, 0.2)

                tributary_obstacle = Obstacle(
                    Vector2(tributary_x - tributary_width/2, tributary_y - tributary_height/2),
                    tributary_width,
                    tributary_height,
                    'water_barrier'
                )
                tributary_obstacle.shape = 'lake_main'
                obstacles.append(tributary_obstacle)

        elif lake_type == 'crescent':
            # Create a crescent-shaped lake
            # Main curved body
            main_width_adj = main_width * 0.8
            main_height_adj = main_height * 0.5

            # Position the main body in a curved fashion
            main_obstacle = Obstacle(
                Vector2(center_x - main_width_adj/2, center_y - main_height_adj/2),
                main_width_adj,
                main_height_adj,
                'water_barrier'
            )
            main_obstacle.shape = 'lake_main'
            obstacles.append(main_obstacle)

            # Add a smaller curved section to create the crescent shape (this acts as a "cutout" effect)
            cutout_width = main_width_adj * 0.6
            cutout_height = main_height_adj * 0.8
            # Position it to create the crescent shape
            cutout_x = center_x - main_width_adj * 0.3  # Offset to create crescent
            cutout_y = center_y - main_height_adj * 0.1

            crescent_part = Obstacle(
                Vector2(cutout_x - cutout_width/2, cutout_y - cutout_height/2),
                cutout_width,
                cutout_height,
                'water_barrier'
            )
            crescent_part.shape = 'lake_shoreline'
            obstacles.append(crescent_part)

            # Add some irregularities around the crescent
            num_irregularities = random.randint(2, 4)
            for i in range(num_irregularities):
                angle = random.uniform(0, 2 * math.pi)
                distance = min(main_width_adj, main_height_adj) * random.uniform(0.3, 0.6)
                irreg_x = center_x + math.cos(angle) * distance
                irreg_y = center_y + math.sin(angle) * distance

                irreg_width = main_width_adj * random.uniform(0.1, 0.25)
                irreg_height = main_height_adj * random.uniform(0.1, 0.25)

                irreg_obstacle = Obstacle(
                    Vector2(irreg_x - irreg_width/2, irreg_y - irreg_height/2),
                    irreg_width,
                    irreg_height,
                    'water_barrier'
                )
                irreg_obstacle.shape = 'lake_shoreline'
                obstacles.append(irreg_obstacle)

        elif lake_type == 'multi_basin':
            # Create a lake with multiple connected basins
            num_basins = random.randint(2, 4)
            basin_positions = []

            for i in range(num_basins):
                # Position each basin with some overlap to create connections
                angle = (i / num_basins) * 2 * math.pi
                distance = base_radius * 0.3 * random.uniform(0.7, 1.0)

                basin_x = center_x + math.cos(angle) * distance * 0.5
                basin_y = center_y + math.sin(angle) * distance * 0.5
                basin_positions.append((basin_x, basin_y))

                # Each basin has slightly different size
                width = main_width * random.uniform(0.25, 0.45)
                height = main_height * random.uniform(0.25, 0.45)

                basin_obstacle = Obstacle(
                    Vector2(basin_x - width/2, basin_y - height/2),
                    width,
                    height,
                    'water_barrier'
                )
                basin_obstacle.shape = 'lake_main'
                obstacles.append(basin_obstacle)

            # Connect the basins with narrow channels
            for i in range(len(basin_positions) - 1):
                x1, y1 = basin_positions[i]
                x2, y2 = basin_positions[i + 1]

                # Calculate midpoint for channel
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Channel dimensions (narrower than basins)
                channel_width = main_width * random.uniform(0.1, 0.2)
                channel_height = main_height * random.uniform(0.1, 0.2)

                # Add channel to connect basins
                channel_obstacle = Obstacle(
                    Vector2(mid_x - channel_width/2, mid_y - channel_height/2),
                    channel_width,
                    channel_height,
                    'water_barrier'
                )
                channel_obstacle.shape = 'lake_main'
                obstacles.append(channel_obstacle)

            # Add some smaller pools connected to the main basins
            for basin_x, basin_y in basin_positions:
                if random.random() < 0.6:  # 60% chance to add a small pool
                    # Position small pool connected to main basin
                    angle = random.uniform(0, 2 * math.pi)
                    distance = main_width * random.uniform(0.2, 0.4)

                    small_pool_x = basin_x + math.cos(angle) * distance
                    small_pool_y = basin_y + math.sin(angle) * distance

                    small_pool_width = main_width * random.uniform(0.1, 0.2)
                    small_pool_height = main_height * random.uniform(0.1, 0.2)

                    small_pool_obstacle = Obstacle(
                        Vector2(small_pool_x - small_pool_width/2, small_pool_y - small_pool_height/2),
                        small_pool_width,
                        small_pool_height,
                        'water_barrier'
                    )
                    small_pool_obstacle.shape = 'lake_main'
                    obstacles.append(small_pool_obstacle)

        # Generate irregular shoreline using organic shapes
        # Instead of simple circular distribution, create more natural shoreline
        num_shoreline_parts = random.randint(8, 15)
        for _ in range(num_shoreline_parts):
            # Create more natural shoreline by placing parts along the perimeter with irregularities
            angle = random.random() * math.pi * 2
            # Vary the distance based on the lake type to create natural irregularities
            dist_base = base_radius * random.uniform(0.8, 1.1)  # Go slightly beyond the main lake
            dist_variation = base_radius * irregularity * random.uniform(-0.3, 0.3)  # Add irregularity
            dist = dist_base + dist_variation

            cx = center_x + math.cos(angle) * dist
            cy = center_y + math.sin(angle) * dist

            # Size of shoreline part with organic variation
            width = base_radius * random.uniform(0.1, 0.3) * (1 + irregularity * (random.random() - 0.5))
            height = base_radius * random.uniform(0.1, 0.3) * (1 + irregularity * (random.random() - 0.5))

            # Create shoreline part
            shoreline_part = Obstacle(
                Vector2(cx - width/2, cy - height/2),
                width,
                height,
                'water_barrier'
            )
            shoreline_part.shape = 'lake_shoreline'  # Mark as shoreline part
            obstacles.append(shoreline_part)

        # Add some depth variation areas (shallower and deeper parts)
        # Place these more strategically within the lake
        num_depth_areas = random.randint(3, 6)
        for _ in range(num_depth_areas):
            # Position within the lake area with organic distribution
            # Use a more natural distribution within the lake
            angle = random.random() * math.pi * 2
            # Keep within the lake but vary based on lake type
            dist = random.uniform(0, base_radius * 0.7)
            cx = center_x + math.cos(angle) * dist
            cy = center_y + math.sin(angle) * dist

            # Size of depth area
            width = base_radius * random.uniform(0.2, 0.4)
            height = base_radius * random.uniform(0.2, 0.4)

            # Create depth variation area
            depth_area = Obstacle(
                Vector2(cx - width/2, cy - height/2),
                width,
                height,
                'water_barrier'
            )
            depth_area.shape = 'lake_depth'  # Mark as depth area
            obstacles.append(depth_area)

        return obstacles

    @staticmethod
    def generate_rock(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                     size_ratio=0.05, rock_type='generic', num_rocks=1):
        """
        Generate realistic rocks with rounded shapes and mineral compositions.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of rock center (0.0-1.0)
            center_y_ratio: Y position of rock center (0.0-1.0)
            size_ratio: Size of the rock relative to world (0.0-0.1)
            rock_type: Type of rock ('granite', 'limestone', 'sandstone', 'basalt', 'generic')
            num_rocks: Number of rocks to generate

        Returns:
            List of Obstacle objects representing rocks
        """
        obstacles = []

        # Calculate base radius based on world dimensions and size ratio
        base_radius = min(world_width, world_height) * size_ratio

        for i in range(num_rocks):
            # Add some random positioning to spread rocks
            center_x = world_width * center_x_ratio + random.uniform(-world_width * 0.1, world_width * 0.1)
            center_y = world_height * center_y_ratio + random.uniform(-world_height * 0.1, world_height * 0.1)

            # Ensure rocks stay within world boundaries
            center_x = max(base_radius, min(world_width - base_radius, center_x))
            center_y = max(base_radius, min(world_height - base_radius, center_y))

            # Add some random variation to size
            radius = base_radius * random.uniform(0.8, 1.2)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(center_x - radius, center_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles

    @staticmethod
    def generate_rock_cluster(world_width, world_height, center_x_ratio=0.5, center_y_ratio=0.5,
                             cluster_size=0.1, rock_density=0.3, rock_type='generic'):
        """
        Generate a cluster of rocks in a specific area.

        Args:
            world_width: Width of the world
            world_height: Height of the world
            center_x_ratio: X position of cluster center (0.0-1.0)
            center_y_ratio: Y position of cluster center (0.0-1.0)
            cluster_size: Size of the cluster area (0.0-0.3)
            rock_density: Density of rocks in the cluster (0.0-1.0)
            rock_type: Type of rocks ('granite', 'limestone', 'sandstone', 'basalt', 'generic')

        Returns:
            List of Obstacle objects representing rock cluster
        """
        obstacles = []

        # Calculate cluster area
        cluster_width = world_width * cluster_size
        cluster_height = world_height * cluster_size

        # Calculate cluster center
        cluster_center_x = world_width * center_x_ratio
        cluster_center_y = world_height * center_y_ratio

        # Calculate number of rocks based on density
        estimated_rock_area = (cluster_width * cluster_height) * rock_density
        avg_rock_size = min(world_width, world_height) * 0.03  # Average rock size
        num_rocks = int(estimated_rock_area / (avg_rock_size * avg_rock_size))

        # Generate rocks within the cluster area
        for _ in range(num_rocks):
            # Random position within cluster area
            pos_x = cluster_center_x + random.uniform(-cluster_width/2, cluster_width/2)
            pos_y = cluster_center_y + random.uniform(-cluster_height/2, cluster_height/2)

            # Ensure position stays within world boundaries
            pos_x = max(avg_rock_size, min(world_width - avg_rock_size, pos_x))
            pos_y = max(avg_rock_size, min(world_height - avg_rock_size, pos_y))

            # Random rock size
            radius = avg_rock_size * random.uniform(0.5, 1.5)

            # Create rock obstacle
            rock = Obstacle(
                Vector2(pos_x - radius, pos_y - radius),  # pos is top-left for rectangular bounds
                radius * 2,  # width
                radius * 2,  # height
                'rock',  # obstacle type
                shape='circle',  # rocks are circular
                radius=radius,  # actual radius for collision
                rock_type=rock_type  # specific rock type
            )

            obstacles.append(rock)

        return obstacles