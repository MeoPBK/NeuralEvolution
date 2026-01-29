import random
import config
from src.genetics.mutation import mutate_gene


def update_somatic_mutations(world, dt, settings):
    """Apply somatic mutations to living agents at a low per-gene rate."""
    rate = settings['SOMATIC_MUTATION_RATE'] * dt

    for agent in world.agent_list:
        if not agent.alive:
            continue

        mutations_this_tick = 0
        for gene in agent.genome.all_genes():
            if random.random() < rate:
                # Apply mutation with halved effect sizes
                mutate_gene(gene, half_effect=True)
                mutations_this_tick += 1

        if mutations_this_tick > 0:
            # Recompute phenotype and rebuild brain
            from src.genetics.phenotype import compute_phenotype
            # Need to get the world's trait ranges somehow - for now, use config
            # In a more robust implementation, agents would have access to world settings
            trait_ranges = getattr(world, 'trait_ranges', config.TRAIT_RANGES)
            agent.phenotype = compute_phenotype(agent.genome, trait_ranges)
            agent.rebuild_brain(settings)  # Pass settings for NN type
            agent.somatic_mutation_timer = 0.5
            agent.total_mutations += mutations_this_tick  # Increment mutation counter
