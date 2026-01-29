from collections import defaultdict


class StatsSnapshot:
    __slots__ = ('time', 'agent_count', 'avg_speed', 'avg_size', 'avg_aggression',
                 'max_generation', 'avg_energy', 'avg_hydration',
                 'genetic_diversity', 'num_attackers', 'num_maters',
                 'species_counts', 'species_males', 'species_females',
                 'total_males', 'total_females')

    def __init__(self):
        self.time = 0.0
        self.agent_count = 0
        self.avg_speed = 0.0
        self.avg_size = 0.0
        self.avg_aggression = 0.0
        self.max_generation = 0
        self.avg_energy = 0.0
        self.avg_hydration = 0.0
        self.genetic_diversity = 0.0
        self.num_attackers = 0
        self.num_maters = 0
        # Per-species tracking
        self.species_counts = {}  # {species_id: count}
        self.species_males = {}   # {species_id: male_count}
        self.species_females = {} # {species_id: female_count}
        # Total gender tracking
        self.total_males = 0
        self.total_females = 0


class StatsCollector:
    def __init__(self, interval=0.5):
        self.interval = interval
        self.last_record_time = 0.0
        self.snapshots = []
        self.max_snapshots = 600
        # Track all species IDs we've ever seen for consistent graphing
        self.known_species = set()

    def update(self, world, sim_time):
        if sim_time - self.last_record_time < self.interval:
            return
        self.last_record_time = sim_time

        snap = StatsSnapshot()
        snap.time = sim_time

        agent_list = world.agent_list
        snap.agent_count = len(agent_list)

        # Initialize species tracking for this snapshot
        species_counts = defaultdict(int)
        species_males = defaultdict(int)
        species_females = defaultdict(int)
        total_males = 0
        total_females = 0

        if agent_list:
            snap.avg_speed = sum(a.phenotype.get('speed', 0) for a in agent_list) / snap.agent_count
            snap.avg_size = sum(a.phenotype.get('size', 0) for a in agent_list) / snap.agent_count
            snap.avg_aggression = sum(a.phenotype.get('aggression', 0) for a in agent_list) / snap.agent_count
            snap.max_generation = max(a.generation for a in agent_list)
            snap.avg_energy = sum(a.energy for a in agent_list) / snap.agent_count
            snap.avg_hydration = sum(a.hydration for a in agent_list) / snap.agent_count
            snap.num_attackers = sum(1 for a in agent_list if a.attack_intent > 0.5)
            snap.num_maters = sum(1 for a in agent_list if a.mate_desire > 0.5 and a.can_reproduce())

            # Genetic diversity: variance in aggression trait
            if snap.agent_count > 1:
                aggros = [a.phenotype.get('aggression', 0) for a in agent_list]
                mean_aggro = sum(aggros) / snap.agent_count
                snap.genetic_diversity = sum((x - mean_aggro) ** 2 for x in aggros) / snap.agent_count

            # Collect per-species and gender data
            for agent in agent_list:
                if agent.alive:
                    species_id = agent.species_id
                    species_counts[species_id] += 1
                    self.known_species.add(species_id)

                    # Track gender
                    sex = agent.sex if hasattr(agent, 'sex') else (agent.genome.sex if hasattr(agent, 'genome') and agent.genome else 'unknown')
                    if sex == 'male':
                        species_males[species_id] += 1
                        total_males += 1
                    elif sex == 'female':
                        species_females[species_id] += 1
                        total_females += 1

        # Store species data
        snap.species_counts = dict(species_counts)
        snap.species_males = dict(species_males)
        snap.species_females = dict(species_females)
        snap.total_males = total_males
        snap.total_females = total_females

        self.snapshots.append(snap)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)

    def get_species_history(self, species_id, attribute='count'):
        """Get historical data for a specific species.

        Args:
            species_id: The species ID to get data for
            attribute: 'count', 'males', or 'females'

        Returns:
            List of (time, value) tuples
        """
        history = []
        for snap in self.snapshots:
            if attribute == 'count':
                value = snap.species_counts.get(species_id, 0)
            elif attribute == 'males':
                value = snap.species_males.get(species_id, 0)
            elif attribute == 'females':
                value = snap.species_females.get(species_id, 0)
            else:
                value = 0
            history.append((snap.time, value))
        return history

    def get_gender_history(self):
        """Get total male/female counts over time.

        Returns:
            List of (time, males, females) tuples
        """
        return [(snap.time, snap.total_males, snap.total_females) for snap in self.snapshots]

    @property
    def latest(self):
        if self.snapshots:
            return self.snapshots[-1]
        return StatsSnapshot()
