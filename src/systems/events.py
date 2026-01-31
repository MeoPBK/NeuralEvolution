import random
import pygame
from src.utils.vector import Vector2
import config


class EventManager:
    """Manages special events like epidemics that can occur during simulation."""

    def __init__(self, settings):
        self.settings = settings
        self.active_events = []
        self.event_history = []
        self.last_epidemic_check = 0
        self.epidemic_interval = settings.get('EPIDEMIC_INTERVAL', 100.0)  # seconds between epidemic checks
        self.epidemic_probability = settings.get('EPIDEMIC_BASE_PROBABILITY', 0.001)  # probability per second when conditions are met
        self.event_display_timer = 0
        self.current_event_message = ""
        self.epidemic_enabled = settings.get('EPIDEMIC_ENABLED', True)

        # Track species for extinction/new species events
        self.previous_species_counts = {}
        self.extinct_species = set()
        self.new_species_announced = set()
        
    def update(self, world, dt):
        """Update events and check for new ones."""
        self.last_epidemic_check += dt

        # Check for epidemic events if enabled
        if self.epidemic_enabled and self.last_epidemic_check >= self.epidemic_interval:
            self.check_for_epidemic(world)
            self.last_epidemic_check = 0

        # Update active events
        for event in self.active_events[:]:  # Copy list to avoid modification during iteration
            event.update(dt)
            if event.is_finished():
                self.active_events.remove(event)
                self.event_history.append(event)

        # Update event display timer
        if self.event_display_timer > 0:
            self.event_display_timer -= dt
            if self.event_display_timer <= 0:
                self.current_event_message = ""

        # Update infection timers for all agents
        for agent in world.agent_list:
            if agent.alive and agent.infected:
                agent.infection_timer -= dt
                if agent.infection_timer <= 0:
                    agent.infected = False
                    agent.infection_timer = 0.0

        # Check for species extinction and new species events
        self.check_species_events(world)
    
    def check_for_epidemic(self, world):
        """Check if conditions are right for an epidemic to occur."""
        # Epidemic is more likely when population density is high
        min_population_threshold = self.settings.get('INITIAL_AGENTS', 150) * self.settings.get('EPIDEMIC_MIN_POPULATION_RATIO', 0.8)  # configurable ratio
        if len(world.agent_list) > min_population_threshold:
            if random.random() < self.epidemic_probability:
                self.trigger_epidemic(world)
    
    def trigger_epidemic(self, world):
        """Trigger an epidemic event that affects a portion of the population."""
        affected_ratio = self.settings.get('EPIDEMIC_AFFECTED_RATIO', 0.3)  # configurable ratio
        affected_count = max(1, int(len(world.agent_list) * affected_ratio))
        affected_agents = random.sample(world.agent_list, min(affected_count, len(world.agent_list)))

        for agent in affected_agents:
            if agent.alive:
                # Apply virus resistance effect
                resistance = agent.virus_resistance
                # Higher resistance means less effect from the epidemic
                reduction_factor = affected_ratio * (1 - resistance)  # scaled by affected ratio and resistance
                new_energy = agent.energy * (1 - reduction_factor)

                # Reduce health significantly but don't necessarily kill
                agent.energy = max(10, new_energy)

                # Mark agent as infected and set infection timer
                agent.infected = True
                agent.infection_timer = 10.0  # Infect for 10 seconds (this can be adjusted)

                # Could add other effects like reduced speed, etc.

        self.current_event_message = f"Epidemic! {len(affected_agents)} agents affected!"
        self.event_display_timer = 5.0  # Show message for 5 seconds

        event = EpidemicEvent(len(affected_agents), len(world.agent_list))
        self.active_events.append(event)
        self.event_history.append(event)


    def check_species_events(self, world):
        """Check for species extinction and new species creation events."""
        # Get current species counts
        current_species_counts = {}
        for agent in world.agent_list:
            if agent.alive:
                species_id = agent.species_id
                current_species_counts[species_id] = current_species_counts.get(species_id, 0) + 1

        # Check for extinct species
        for species_id, prev_count in self.previous_species_counts.items():
            if species_id not in current_species_counts and species_id not in self.extinct_species:
                # Species has gone extinct
                species_name = f"Species {species_id}"  # Would use proper name from stats visualization in actual implementation
                self.current_event_message = f"EXTINCTION: {species_name} (ID: {species_id}) has gone extinct!"
                self.event_display_timer = 5.0  # Show message for 5 seconds
                self.extinct_species.add(species_id)

        # Check for new species
        for species_id, current_count in current_species_counts.items():
            if species_id not in self.previous_species_counts and species_id not in self.new_species_announced:
                # New species has appeared
                species_name = f"Species {species_id}"  # Would use proper name from stats visualization in actual implementation
                self.current_event_message = f"NEW SPECIES: {species_name} (ID: {species_id}) has emerged!"
                self.event_display_timer = 5.0  # Show message for 5 seconds
                self.new_species_announced.add(species_id)

        # Update previous counts for next check
        self.previous_species_counts = current_species_counts.copy()

    def get_current_event_message(self):
        """Return the current event message if any."""
        return self.current_event_message if self.event_display_timer > 0 else ""
    
    def draw_event_indicator(self, screen, font):
        """Draw visual indicator for current events."""
        if self.current_event_message:
            # Draw a warning banner at the top of the screen
            screen_width = screen.get_width()
            banner_height = 40
            banner_rect = pygame.Rect(0, 0, screen_width, banner_height)
            
            # Red semi-transparent overlay
            s = pygame.Surface((screen_width, banner_height))
            s.set_alpha(180)
            s.fill((200, 0, 0))
            screen.blit(s, (0, 0))
            
            # Draw text
            text_surf = font.render(self.current_event_message, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(screen_width // 2, banner_height // 2))
            screen.blit(text_surf, text_rect)


class EpidemicEvent:
    """Represents a single epidemic event."""
    
    def __init__(self, affected_count, total_population):
        self.affected_count = affected_count
        self.total_population = total_population
        self.duration = 0
        self.max_duration = 5.0  # 5 seconds
        
    def update(self, dt):
        self.duration += dt
        
    def is_finished(self):
        return self.duration >= self.max_duration


class SpecialEvent:
    """Base class for special events."""
    
    def __init__(self, name, duration):
        self.name = name
        self.duration = 0
        self.max_duration = duration
        
    def update(self, dt):
        self.duration += dt
        
    def is_finished(self):
        return self.duration >= self.max_duration