import pygame
import math
import random


class ParticleSystem:
    """Manages particle effects like heart animations for mating."""
    
    def __init__(self):
        self.particles = []
        
    def add_heart_particles(self, pos, count=8):
        """Add heart particles at a position for mating animation."""
        for _ in range(count):
            # Generate random angle for initial velocity
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            particle = {
                'pos': [float(pos[0]), float(pos[1])],  # Ensure float values
                'vel': [vx, vy],
                'life': 1.0,  # Full life initially
                'decay': random.uniform(0.01, 0.03),  # How fast life decreases
                'size': random.uniform(3, 6),
                'color': (255, 100, 100),  # Red/pink color for hearts
                'shape': 'heart'  # Heart shape
            }
            self.particles.append(particle)

    def add_fighting_particles(self, pos, count=5):
        """Add cross particles at a position for fighting/attacking animation."""
        for _ in range(count):
            # Generate random angle for initial velocity (more directed outward for aggressive effect)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 3.0)  # Slightly faster for aggressive effect
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            particle = {
                'pos': [float(pos[0]), float(pos[1])],  # Ensure float values
                'vel': [vx, vy],
                'life': 1.0,  # Full life initially
                'decay': random.uniform(0.02, 0.05),  # Slightly faster decay for aggressive effect
                'size': random.uniform(4, 8),  # Slightly larger for visibility
                'color': (180, 80, 200),  # Purple color for fighting
                'shape': 'cross'  # Cross shape for fighting
            }
            self.particles.append(particle)

    def update(self, dt):
        """Update all particles."""
        for particle in self.particles[:]:  # Use slice to iterate over a copy
            # Update position
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            
            # Apply slight gravity/downward force
            particle['vel'][1] += 0.1
            
            # Apply friction to slow particles down over time
            particle['vel'][0] *= 0.98
            particle['vel'][1] *= 0.98
            
            # Update life
            particle['life'] -= particle['decay']
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen, scale_x=1.0, scale_y=1.0):
        """Draw all particles."""
        for particle in self.particles:
            if particle['life'] > 0:
                # Calculate color based on life (fade out effect)
                alpha = int(255 * particle['life'])
                color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)

                # Draw shape based on particle type
                # Scale the position
                pos = (int(particle['pos'][0] * scale_x), int(particle['pos'][1] * scale_y))
                # Scale the size
                size = int(particle['size'] * particle['life'] * scale_x)  # Shrink as it fades and scale

                if size > 0:
                    if particle['shape'] == 'heart':
                        # Draw a simple heart shape
                        self._draw_heart(screen, pos, size, color)
                    elif particle['shape'] == 'cross':
                        # Draw a cross shape for fighting/attacking
                        self._draw_cross(screen, pos, size, color)
                    elif particle['shape'] == 'cloud':
                        # Draw a cloud shape for disease/infection effect
                        self._draw_cloud(screen, pos, size, color)
                    elif particle['shape'] == 'disease':
                        # Draw a disease particle (spiky microbe shape)
                        self._draw_disease(screen, pos, size, color)
    
    def _draw_heart(self, screen, pos, size, color):
        """Draw a simple heart shape."""
        x, y = pos
        s = size / 2  # Use half size for easier scaling

        # Draw a heart shape using circles and triangles
        # Two upper circles for the top lobes
        pygame.draw.circle(screen, color[:3], (int(x - s/2), int(y - s/2)), max(1, int(s/2)))
        pygame.draw.circle(screen, color[:3], (int(x + s/2), int(y - s/2)), max(1, int(s/2)))

        # Triangle for the bottom point
        points = [(x - s, y), (x + s, y), (x, y + s)]
        pygame.draw.polygon(screen, color[:3], points)

    def _draw_cross(self, screen, pos, size, color):
        """Draw a cross shape for fighting/attacking animation."""
        x, y = pos
        s = size / 2  # Half size for cross arm length

        # Draw horizontal line
        pygame.draw.line(screen, color[:3], (x - s, y), (x + s, y), max(1, int(size/4)))
        # Draw vertical line
        pygame.draw.line(screen, color[:3], (x, y - s), (x, y + s), max(1, int(size/4)))

    def add_disease_particles(self, pos, count=8):
        """Add disease particles at a position for infection/transmission animation."""
        for _ in range(count):
            # Generate random angle for initial velocity (more directed outward for infectious effect)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)  # Moderate speed for disease effect
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            particle = {
                'pos': [float(pos[0]), float(pos[1])],  # Ensure float values
                'vel': [vx, vy],
                'life': 1.0,  # Full life initially
                'decay': random.uniform(0.01, 0.03),  # Moderate decay rate
                'size': random.uniform(3, 6),  # Medium size for visibility
                'color': (255, 150, 0),  # Orange color for disease/infection
                'shape': 'disease'  # Disease shape
            }
            self.particles.append(particle)

    def _draw_disease(self, screen, pos, size, color):
        """Draw a disease particle (looks like a spiky microbe)."""
        x, y = pos
        s = size / 2  # Half size for easier calculations

        # Draw a central circle
        pygame.draw.circle(screen, color[:3], (int(x), int(y)), max(1, int(s * 0.6)))

        # Draw spikes radiating outward
        for i in range(8):  # 8 spikes
            angle = (2 * math.pi / 8) * i
            spike_start_x = x + math.cos(angle) * s * 0.6
            spike_start_y = y + math.sin(angle) * s * 0.6
            spike_end_x = x + math.cos(angle) * s
            spike_end_y = y + math.sin(angle) * s
            pygame.draw.line(screen, color[:3], (spike_start_x, spike_start_y), (spike_end_x, spike_end_y), max(1, int(size/6)))

    def _draw_cloud(self, screen, pos, size, color):
        """Draw a cloud shape for disease/infection animation."""
        x, y = pos
        s = size / 2  # Half size for easier scaling

        # Draw a cloud-like shape using multiple connected circles
        # Main body of the cloud
        pygame.draw.circle(screen, color[:3], (int(x), int(y)), max(1, int(s * 0.6)))
        # Left bump
        pygame.draw.circle(screen, color[:3], (int(x - s * 0.4), int(y)), max(1, int(s * 0.5)))
        # Right bump
        pygame.draw.circle(screen, color[:3], (int(x + s * 0.4), int(y)), max(1, int(s * 0.5)))
        # Top bump
        pygame.draw.circle(screen, color[:3], (int(x), int(y - s * 0.3)), max(1, int(s * 0.4)))
        # Bottom bump
        pygame.draw.circle(screen, color[:3], (int(x), int(y + s * 0.2)), max(1, int(s * 0.4)))
    
    def clear(self):
        """Clear all particles."""
        self.particles = []
    
    def is_empty(self):
        """Check if there are no active particles."""
        return len(self.particles) == 0