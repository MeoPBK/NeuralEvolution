from src.core.world import World
from src.systems.movement import update_movement
from src.systems.combat import update_combat
from src.systems.feeding import update_feeding
from src.systems.hydration import update_hydration
from src.systems.energy import update_energy
from src.systems.reproduction import update_reproduction
from src.systems.aging import update_aging
from src.systems.somatic_mutation import update_somatic_mutations
from src.systems.events import EventManager
from src.systems.disease_transmission import DiseaseTransmissionSystem
from src.systems.water_exposure import update_water_exposure
from src.utils.stats import StatsCollector
import config


class Simulation:
    def __init__(self, settings, renderer=None):
        self.settings = settings
        self.world = World(settings)
        self.stats = StatsCollector(interval=0.5)
        self.event_manager = EventManager(settings)
        self.disease_transmission_system = DiseaseTransmissionSystem(settings)  # Initialize disease transmission system
        self.renderer = renderer  # Store reference to renderer for animations
        self.sim_time = 0.0
        self.paused = False
        self.speed_multiplier = 1.0

    def update(self, dt):
        """Main simulation update loop."""
        if self.paused:
            return

        effective_dt = dt * self.speed_multiplier
        self.sim_time += effective_dt

        # 1. Rebuild spatial grids
        self.world.rebuild_grids()

        # 2. Movement (NN forward pass + position update)
        update_movement(self.world, effective_dt)

        # 3. Combat (attack resolution)
        particle_system = getattr(self, 'particle_system', None)
        update_combat(self.world, effective_dt, particle_system)

        # 4. Feeding (agents eat food)
        update_feeding(self.world, effective_dt)

        # 5. Hydration (drain + drink)
        update_hydration(self.world, effective_dt)

        # 6. Energy (metabolic costs)
        update_energy(self.world, effective_dt)

        # 7. Reproduction
        # Store reproduction events to handle animations later
        self.world.mating_events = []  # Clear previous mating events
        update_reproduction(self.world, effective_dt)

        # Handle mating animations
        if hasattr(self.world, 'mating_events'):
            for event in self.world.mating_events:
                if self.renderer and hasattr(self.renderer, 'particle_system'):
                    self.renderer.particle_system.add_heart_particles(event['position'], count=8)

        # 8. Aging
        update_aging(self.world, effective_dt, self.settings)

        # 9. Somatic mutations
        update_somatic_mutations(self.world, effective_dt, self.settings)

        # 10. Update agent infection statuses
        for agent in self.world.agent_list:
            if agent.alive:
                agent.update_infection_status(effective_dt)

        # 11. Water exposure effects
        update_water_exposure(self.world, effective_dt)

        # 12. Disease transmission
        # Pass the renderer's particle system to the disease transmission system for visual effects
        particle_system = getattr(self.renderer, 'particle_system', None) if self.renderer else None
        self.disease_transmission_system.update(self.world, effective_dt, particle_system)

        # 12. Special events
        self.event_manager.update(self.world, effective_dt)

        # 13. Cleanup dead + spawn food + drift clusters
        self.world.cleanup()
        self.world.spawn_food(effective_dt)
        self.world.food_clusters.update(effective_dt)

        # 14. Stats
        self.stats.update(self.world, self.sim_time)

    def toggle_pause(self):
        self.paused = not self.paused

    def speed_up(self):
        self.speed_multiplier = min(8.0, self.speed_multiplier * 1.5)

    def speed_down(self):
        self.speed_multiplier = max(0.25, self.speed_multiplier / 1.5)
