"""
Disease transmission system for the simulation.
Handles disease spread between agents based on proximity and genetic resistance.
"""
import random
import math
from src.utils.vector import Vector2


class DiseaseTransmissionSystem:
    """Handles disease transmission between agents based on proximity and genetic resistance."""
    
    def __init__(self, settings):
        self.settings = settings
        self.disease_names = settings.get('DISEASE_NAMES', ['Flu', 'Plague', 'Malaria', 'Pox'])
        self.transmission_distance = settings.get('DISEASE_TRANSMISSION_DISTANCE', 15.0)
        self.enabled = settings.get('DISEASE_TRANSMISSION_ENABLED', True)
        
    def update(self, world, dt, particle_system=None):
        """Update disease transmission between agents."""
        if not self.enabled:
            return

        # Get all infected agents
        infected_agents = [agent for agent in world.agent_list if agent.alive and agent.infected]

        # For each infected agent, check for nearby susceptible agents
        for infected_agent in infected_agents:
            if not infected_agent.alive or not infected_agent.infected:
                continue

            # Query nearby agents within transmission distance
            nearby_agents = world.agent_grid.query_radius(
                infected_agent.pos,
                self.transmission_distance,
                exclude=infected_agent
            )

            # Attempt to transmit disease to each nearby agent
            for nearby_agent in nearby_agents:
                if (nearby_agent.alive and
                    not nearby_agent.infected and  # Only transmit to non-infected agents
                    nearby_agent.can_catch_disease(infected_agent.current_disease)):

                    # Calculate transmission probability based on distance
                    distance = infected_agent.pos.distance_to(nearby_agent.pos)
                    max_distance = self.transmission_distance
                    transmission_prob = 1.0 - (distance / max_distance)  # Closer = higher probability

                    # Apply genetic resistance
                    resistance = nearby_agent.get_disease_resistance(infected_agent.current_disease)
                    effective_transmission_prob = transmission_prob * (1 - resistance)

                    # Transmit disease if successful
                    if random.random() < effective_transmission_prob:
                        nearby_agent.infect_with_disease(
                            infected_agent.current_disease,
                            duration=random.uniform(5.0, 15.0)  # Random duration between 5-15 seconds
                        )

                        # Add visual effect for transmission if particle system is available
                        if particle_system:
                            # Add a visual indicator for disease transmission
                            mid_pos = (infected_agent.pos + nearby_agent.pos) / 2
                            particle_system.add_disease_particles(mid_pos, count=6)
    
    def get_random_disease(self):
        """Get a random disease name from the available diseases."""
        return random.choice(self.disease_names)
    
    def apply_epidemic(self, world):
        """Apply an epidemic event that affects a portion of the population."""
        if not self.enabled:
            return
            
        affected_ratio = self.settings.get('EPIDEMIC_AFFECTED_RATIO', 0.3)  # 30% affected by default
        affected_count = max(1, int(len(world.agent_list) * affected_ratio))
        
        # Select random agents to infect
        living_agents = [agent for agent in world.agent_list if agent.alive]
        if not living_agents:
            return
            
        affected_agents = random.sample(living_agents, min(affected_count, len(living_agents)))
        
        # Select a random disease for the epidemic
        epidemic_disease = self.get_random_disease()
        
        for agent in affected_agents:
            if not agent.infected:  # Only infect agents that aren't already infected
                agent.infect_with_disease(
                    epidemic_disease,
                    duration=random.uniform(8.0, 20.0)  # Longer duration for epidemic diseases
                )