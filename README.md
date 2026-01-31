# Population Simulation v2 - Complete Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Core Architecture](#core-architecture)
3. [Neural Network System](#neural-network-system)
4. [Genetic System](#genetic-system)
5. [Simulation Systems](#simulation-systems)
6. [Environment and Entities](#environment-and-entities)
7. [Advanced Features](#advanced-features)
8. [User Interface and Controls](#user-interface-and-controls)
9. [Configuration Parameters](#configuration-parameters)
10. [Data Structures](#data-structures)
11. [Implementation Details](#implementation-details)

---

## Chapter 1: Project Overview {#project-overview}

This is an advanced evolutionary simulation that models a population of agents in a 2D world. Each agent's behavior is controlled by a genetically-encoded neural network. The simulation explores how complex behaviors like herbivory, cannibalism, and social dynamics can emerge through evolutionary processes.

### Key Concepts

**Evolutionary Simulation**: The core concept is that agents with different genetic traits compete for resources, reproduce, and pass on their traits to offspring. Over generations, beneficial traits become more common in the population while detrimental traits are selected against. The simulation implements Darwinian evolution with natural selection acting on heritable variation in traits that affect survival and reproduction.

**Neural Network Brains**: Each agent has a neural network brain that processes environmental inputs and produces behavioral outputs. The neural network weights are encoded in the agent's genome and are subject to evolutionary pressure. This creates a direct link between genetic variation and behavioral differences, allowing for the evolution of complex decision-making strategies.

**Emergent Behaviors**: Rather than hard-coding specific behaviors, the simulation allows complex behaviors to emerge from the interaction of the neural network outputs with the environment and other agents. This includes foraging strategies, social behaviors, territoriality, and complex predator-prey dynamics.

**Resource Management**: Agents must balance multiple resources (energy, hydration) while navigating environmental challenges and competing with other agents. The system implements realistic metabolic costs that scale with agent traits, creating trade-offs between different capabilities.

**Genetic Inheritance**: Traits are passed from parents to offspring through a sophisticated genetic system with diploid chromosomes, dominance effects, and mutation. The system implements realistic Mendelian inheritance with crossover and mutation during meiosis.

### Main Objectives

1. **Study Evolution**: Understand how complex behaviors evolve in response to environmental pressures and resource competition
2. **Model Ecology**: Simulate ecological interactions between agents and resources, including population dynamics and species interactions
3. **Explore AI**: Investigate how neural networks can develop complex behaviors without explicit programming through evolutionary processes
4. **Demonstrate Emergence**: Show how complex behaviors emerge from simple rules and interactions between agents and environment
5. **Research Adaptation**: Study how populations adapt to changing environmental conditions and resource availability

---

## Chapter 2: Core Architecture {#core-architecture}

The simulation follows a modular architecture with clearly defined systems that interact through well-defined interfaces:

### Main Components

**Simulation Class**: The main orchestrator that manages the simulation loop, coordinates between systems, and maintains the world state. It handles the main update cycle where all systems are called in sequence, ensuring proper temporal ordering of operations. The class also manages simulation speed, pause states, and overall timing.

**World Class**: Manages the simulation environment including all entities (agents, food, water, obstacles), spatial grids for efficient queries, and environmental parameters. It serves as the central repository for all simulation entities and coordinates their interactions. The World class also handles cleanup of dead entities and spawning of new resources.

**Entity Classes**: Individual objects in the world (Agent, Food, Water, Obstacle) that have their own state and behaviors but are managed by the World. Each entity type implements appropriate interfaces for interaction with the various systems.

**System Classes**: Specialized modules that handle specific aspects of the simulation (movement, combat, feeding, etc.) and operate on the entities in the world. Systems are designed to be independent but can access shared data through the World object.

**Genetics Classes**: Handle all genetic operations including genome creation, crossover, mutation, and phenotype expression. These classes implement the biological mechanisms of inheritance and variation.

**Rendering Classes**: Handle visualization of the simulation including the main renderer, HUD, and specialized visualization tools. The rendering system is designed to be efficient while providing rich visual feedback.

### Data Flow Architecture

The simulation operates in a continuous cycle with each system contributing to the overall state:

1. **Spatial Grid Rebuilding**: Update spatial partitioning for efficient neighbor queries. This is critical for performance as the population grows, converting O(n²) operations to O(n) by dividing the world into grid cells.

2. **Movement System**: Process neural network inputs, run forward pass, update positions. This system computes sector-based inputs, runs the agent's brain, and applies the outputs to movement and behavioral decisions.

3. **Combat System**: Resolve attacks and cannibalism. This system checks for agents within attack distance with high attack drive and resolves combat outcomes based on size, aggression, and other factors.

4. **Feeding System**: Process food consumption. Agents consume food within eating distance, gaining energy and removing the food from the world.

5. **Hydration System**: Process water consumption and hydration drain. Agents drink from water sources when in range, and hydration drains continuously.

6. **Energy System**: Apply metabolic costs based on agent traits, size, speed, and activity level. This system implements realistic metabolic scaling with size and activity.

7. **Reproduction System**: Handle mating and offspring creation. This system manages mate selection, genetic inheritance, and offspring creation with proper initialization.

8. **Aging System**: Increment age and handle death from old age. Each agent has a genetically-determined maximum age that can evolve over generations.

9. **Somatic Mutation System**: Apply lifetime mutations to agent genomes. These mutations can occur during the agent's lifetime and may be inherited if the agent reproduces after mutation.

10. **Disease Transmission System**: Update infection statuses and spread diseases between agents. This system models realistic disease transmission dynamics.

11. **Events System**: Check for and trigger special events like epidemics. These events can dramatically affect population dynamics.

12. **Cleanup**: Remove dead agents, spawn food, update statistics. This system maintains simulation health by cleaning up dead entities and maintaining resource levels.

---

## Chapter 3: Neural Network System {#neural-network-system}

### Architecture Overview

The simulation uses a sophisticated V2 neural network architecture with sector-based sensing and decoupled behavioral drives. Two network types are available:

#### Feed-Forward Neural Network (FNN)
- **Structure**: 24 inputs → 8 hidden neurons (tanh) → 6 outputs (tanh)
- **Total Weights**: 254 (192 input-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)
- **Characteristics**: Reactive behaviors, simpler and faster processing, no memory of past states
- **Use Case**: Suitable for immediate response behaviors without memory requirements
- **Implementation**: Pure Python implementation without NumPy dependencies for portability

#### Recurrent Neural Network (RNN)
- **Structure**: 24 inputs → 8 hidden neurons (tanh with recurrent connections) → 6 outputs (tanh)
- **Total Weights**: 318 (192 input-hidden + 64 hidden-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)
- **Characteristics**: Memory-based behaviors, complex strategies with temporal reasoning, ability to maintain state across time steps
- **Use Case**: Suitable for behaviors requiring memory of past events or temporal patterns
- **Implementation**: Includes optional stochastic noise injection for exploration and robustness

### Mathematical Formulas for Neural Network Operations

#### Feed-Forward Neural Network (FNN) Equations

For the FNN architecture with 24 inputs, 8 hidden neurons, and 6 outputs:

**Hidden Layer Computation:**
$$ h_j^{(t)} = \tanh\left(\sum_{i=1}^{24} W_{ij}^{(input-hidden)} \cdot x_i^{(t)} + b_j^{(hidden)}\right) $$

Where:
- $ h_j^{(t)} $ is the activation of hidden neuron $ j $ at time $ t $
- $ W_{ij}^{(input-hidden)} $ is the weight connecting input $ i $ to hidden neuron $ j $
- $ x_i^{(t)} $ is the $ i $-th input at time $ t $
- $ b_j^{(hidden)} $ is the bias for hidden neuron $ j $

**Output Layer Computation:**
$$ y_k^{(t)} = \tanh\left(\sum_{j=1}^{8} W_{jk}^{(hidden-output)} \cdot h_j^{(t)} + b_k^{(output)}\right) $$

Where:
- $ y_k^{(t)} $ is the $ k $-th output at time $ t $
- $ W_{jk}^{(hidden-output)} $ is the weight connecting hidden neuron $ j $ to output $ k $
- $ b_k^{(output)} $ is the bias for output $ k $

#### Recurrent Neural Network (RNN) Equations

For the RNN architecture with 24 inputs, 8 hidden neurons, and 6 outputs:

**Hidden State Update:**
$$ h_j^{(t)} = \tanh\left(\sum_{i=1}^{24} W_{ij}^{(input-hidden)} \cdot x_i^{(t)} + \sum_{k=1}^{8} W_{kj}^{(hidden-hidden)} \cdot h_k^{(t-1)} + b_j^{(hidden)} + \epsilon_j^{(t)}\right) $$

Where:
- $ h_j^{(t)} $ is the activation of hidden neuron $ j $ at time $ t $
- $ W_{ij}^{(input-hidden)} $ is the weight connecting input $ i $ to hidden neuron $ j $
- $ W_{kj}^{(hidden-hidden)} $ is the recurrent weight connecting hidden neuron $ k $ at time $ t-1 $ to hidden neuron $ j $ at time $ t $
- $ h_k^{(t-1)} $ is the activation of hidden neuron $ k $ at time $ t-1 $
- $ b_j^{(hidden)} $ is the bias for hidden neuron $ j $
- $ \epsilon_j^{(t)} $ is optional stochastic noise at time $ t $

**Output Layer Computation:**
$$ y_k^{(t)} = \tanh\left(\sum_{j=1}^{8} W_{jk}^{(hidden-output)} \cdot h_j^{(t)} + b_k^{(output)}\right) $$

### Genome Structure

The simulation uses a **diploid chromosome system** with 8 pairs of chromosomes (16 total chromosomes), each containing multiple genes that encode all heritable traits including neural network weights.

**Chromosome Layout:**
- **Chromosome 0**: Physical traits - Speed, Size, Energy Efficiency, Max Age, Virus Resistance
- **Chromosome 1**: Sensory and Reproductive traits - Vision, Efficiency, Reproduction Urge, Camouflage
- **Chromosome 2**: Behavioral traits - Aggression, Agility, Armor (morphological traits)
- **Chromosome 3**: Color, Disease Resistance, and Ecological traits - Color genes, Disease resistance, Diet/Habitat preferences
- **Chromosome 4**: Neural Network weights 0-63 (partial input→hidden weights)
- **Chromosome 5**: Neural Network weights 64-127 (partial input→hidden weights)
- **Chromosome 6**: Neural Network weights 128-191 (remaining input→hidden + partial recurrent weights)
- **Chromosome 7**: Neural Network weights 192-255 (remaining recurrent + biases + partial output weights)
- **Chromosome 8**: Neural Network weights 256-317 (remaining output weights + output biases)

**Gene Organization:**
Each gene consists of two alleles (diploid system):
- `allele_a`: Maternal allele
- `allele_b`: Paternal allele
- Each allele has a `value` (phenotypic effect) and `dominance` (0.0-1.0 scale)

### Gene Expression System

Gene expression uses **dominance-weighted averaging** to determine the phenotypic value:

**Expression Formula:**
```
total_dom = allele_a.dominance + allele_b.dominance
if total_dom < 1e-8:
    expressed_value = (allele_a.value + allele_b.value) / 2.0  # Equal contribution if both dominance near 0
else:
    w_a = allele_a.dominance / total_dom  # Weight for allele A
    w_b = allele_b.dominance / total_dom  # Weight for allele B
    expressed_value = allele_a.value * w_a + allele_b.value * w_b
```

**Default Dominance Values:**
- Standard dominance: 0.5 (equal contribution from both alleles)
- Range: 0.0 (completely recessive) to 1.0 (completely dominant)

### Neural Network Gene Distribution

The neural network weights are distributed across chromosomes 4-8:

**FNN (254 total weights):**
- Chromosomes 4-6: 192 input-to-hidden weights (24 inputs × 8 hidden neurons)
- Chromosome 6: 8 hidden bias weights
- Chromosomes 6-7: 48 hidden-to-output weights (8 hidden × 6 outputs)
- Chromosome 7: 6 output bias weights

**RNN (318 total weights):**
- Chromosomes 4-6: 192 input-to-hidden weights (24 inputs × 8 hidden neurons)
- Chromosomes 6-7: 64 hidden-to-hidden recurrent weights (8 × 8)
- Chromosome 7: 8 hidden bias weights
- Chromosome 7: 48 hidden-to-output weights (8 hidden × 6 outputs)
- Chromosome 8: 6 output bias weights

### Physical Trait Genes

**Speed Genes:**
- `speed_1`, `speed_2`, `speed_3`, `speed_3_mod`: Control maximum movement speed
- Default: 3.0 (mean), with standard deviation 0.5

**Size Genes:**
- `size_1`, `size_2`, `size_mod`: Control agent size and associated traits
- Default: 6.0 (mean), with standard deviation 1.0

**Vision Genes:**
- `vision_1`, `vision_2`: Control vision range for sensing
- Default: 100.0 (mean), with standard deviation 20.0

**Efficiency Genes:**
- `efficiency_1`, `efficiency_2`, `efficiency_3`: Control energy efficiency
- Default: 1.0 (mean), with standard deviation 0.2

**Aggression Genes:**
- `aggro_1`, `aggro_2`: Control aggressive behavior and combat effectiveness
- Default: 1.0 (mean), with standard deviation 0.3

**Max Age Genes:**
- `max_age_1`, `max_age_2`: Control genetic lifespan
- Default: 70.0 (mean), with standard deviation 10.0

**Virus Resistance Genes:**
- `virus_resistance_1`, `virus_resistance_2`: Control resistance to diseases
- Default: 0.5 (mean), with standard deviation 0.2

**Morphological Trait Genes:**
- `agility_1`, `agility_2`: Control turning/acceleration abilities
- `armor_1`, `armor_2`: Control damage reduction
- Default: 0.5 (mean), with standard deviation 0.15

**Ecological Trait Genes:**
- `diet_type_1`, `diet_type_2`: Control dietary preferences (0=carnivore, 1=omnivore, 2=herbivore)
- `habitat_preference_1`, `habitat_preference_2`: Control habitat preferences (0=aquatic, 1=amphibious, 2=terrestrial)
- Default: 1.0 (mean), with standard deviation 0.3

### Mutation System

Mutations occur during reproduction with the following distribution:

**Mutation Types:**
- **Point Mutations (70%)**: Gaussian shift to allele value
  - Formula: `allele.value += random.gauss(0, POINT_MUTATION_STDDEV)`
  - Standard deviation: Configurable via `POINT_MUTATION_STDDEV` (default 0.3)

- **Dominance Mutations (15%)**: Shift to dominance coefficient
  - Formula: `allele.dominance += random.gauss(0, 0.1)`
  - Clamped to range [0.0, 1.0]

- **Allele Swaps (10%)**: Swap maternal and paternal alleles at a locus
  - Formula: `gene.allele_a, gene.allele_b = gene.allele_b, gene.allele_a`

- **Large-Effect Mutations (5%)**: Bigger jumps in value
  - Formula: `allele.value += random.gauss(0, LARGE_MUTATION_STDDEV)`
  - Standard deviation: Configurable via `LARGE_MUTATION_STDDEV` (default 1.5)

**Mutation Parameters:**
- `MUTATION_RATE`: Probability of mutation per gene per reproduction (default 0.2)
- `LARGE_MUTATION_CHANCE`: Probability that a mutation is large-effect (default 0.05)
- `DOMINANCE_MUTATION_RATE`: Probability that a mutation affects dominance (default 0.15)

**Somatic Mutations:**
- Occur during agent lifetime with configurable rate
- Effects are halved compared to reproductive mutations
- Formula: `scale = 0.5` applied to all mutation effects

### Reproduction System

**Sexual Reproduction:**
- Cross between male and female agents
- Crossover occurs between homologous chromosomes
- `CROSSOVER_RATE`: Probability of crossover per chromosome (default 0.3)

**Gamete Formation:**
- Each parent contributes one allele from each gene pair
- Random selection with equal probability (50% chance per allele)

**Offspring Generation:**
- Combines alleles from both parents
- Sex randomly assigned (male or female)
- Mutations applied to offspring genome

### Phenotype Computation

The phenotype is computed by averaging the expression of contributing genes:

**Trait Computation Formula:**
```
for trait_name, gene_names in TRAIT_GENE_MAP.items():
    values = []
    for gene_name in gene_names:
        gene = genome.get_gene(gene_name)
        if gene is not None:
            values.append(gene.express())  # Apply dominance-weighted averaging

raw_value = sum(values) / len(values)  # Average of contributing genes

# Apply sex modifier
sex_mods = SEX_MODIFIERS.get(genome.sex, {})
modifier = sex_mods.get(trait_name, 1.0)
raw_value *= modifier

# Clamp to valid range
if trait_name in trait_ranges:
    lo, hi = trait_ranges[trait_name]
    raw_value = max(lo, min(hi, raw_value))

phenotype[trait_name] = raw_value
```

**Sex-Based Modifiers:**
- **Male modifiers**: +5% speed/size, -3% energy efficiency, -5% max age
- **Female modifiers**: -3% speed/size, +5% energy efficiency, +5% max age

### Genetic Inheritance Patterns

**Mendelian Inheritance:**
- Diploid system with two alleles per gene
- Dominance relationships affect phenotypic expression
- Segregation during gamete formation

**Trait Correlations:**
- Shared genetic basis creates correlations between traits
- Pleiotropy: Single genes affecting multiple traits
- Linkage: Genes on same chromosome inherited together

**Evolutionary Pathways:**
- Selection acts on phenotypic traits
- Genetic variation maintained through mutation
- Heritability enables response to selection

### Evolutionary Divergence and Speciation

**When Evolutionary Divergence Happens:**
- **Selection Pressures**: Different environments favor different traits, leading to adaptive divergence
- **Genetic Drift**: Random changes in allele frequencies, especially pronounced in small populations
- **Mutation Accumulation**: New mutations create genetic differences between populations over time
- **Geographic Isolation**: Physical barriers (mountains, rivers, etc.) prevent gene flow between populations
- **Reproductive Isolation**: Behavioral or genetic changes that prevent successful interbreeding

---

## Enhanced RNN Memory System {#enhanced-rnn-memory-system}

The RNN memory system is a critical component that enables agents to exhibit temporal reasoning and memory-based behaviors. The system operates through recurrent connections that maintain state across time steps.

#### Mathematical Foundation of RNN Memory

The RNN's memory capability stems from its recurrent connections, which create a dynamic system that can maintain information about past states:

$$ \mathbf{h}^{(t)} = f(\mathbf{W}_{ih}\mathbf{x}^{(t)} + \mathbf{W}_{hh}\mathbf{h}^{(t-1)} + \mathbf{b}_h) $$

Where:
- $ \mathbf{h}^{(t)} $ is the hidden state vector at time $ t $
- $ \mathbf{x}^{(t)} $ is the input vector at time $ t $
- $ \mathbf{W}_{ih} $ is the input-to-hidden weight matrix (24×8)
- $ \mathbf{W}_{hh} $ is the hidden-to-hidden (recurrent) weight matrix (8×8)
- $ \mathbf{b}_h $ is the hidden bias vector
- $ f $ is the activation function (tanh)

The recurrent weight matrix $ \mathbf{W}_{hh} $ is what enables memory. Each element $ W_{hh,ij} $ determines how the activation of hidden unit $ j $ at time $ t-1 $ influences the activation of hidden unit $ i $ at time $ t $.

#### Memory Persistence and Decay

The memory in the RNN system exhibits both persistence and decay characteristics:

$$ \lim_{t \to \infty} \mathbf{h}^{(t)} = \lim_{t \to \infty} f\left(\sum_{\tau=0}^{t} \mathbf{W}_{hh}^{t-\tau} \mathbf{W}_{ih}\mathbf{x}^{(\tau)} + \text{bias terms}\right) $$

This equation shows that the current hidden state is influenced by all previous inputs, weighted by powers of the recurrent weight matrix. The eigenvalues of $ \mathbf{W}_{hh} $ determine how quickly information from the past fades.

#### Information Retention Analysis

The information retention in the RNN can be quantified by the spectral radius of the recurrent weight matrix:

$$ \rho(\mathbf{W}_{hh}) = \max_i |\lambda_i| $$

Where $ \lambda_i $ are the eigenvalues of $ \mathbf{W}_{hh} $. When $ \rho(\mathbf{W}_{hh}) < 1 $, the network exhibits exponential forgetting, while when $ \rho(\mathbf{W}_{hh}) > 1 $, it may become unstable. The ideal range for memory retention is when $ \rho(\mathbf{W}_{hh}) \approx 1 $.

The memory capacity can be estimated by the number of time steps over which information remains accessible:

$$ T_{memory} \approx \frac{1}{|\log(\rho(\mathbf{W}_{hh}))|} $$

This represents the approximate number of time steps after which the influence of a past input has decayed to $ 1/e \approx 0.37 $ of its original value.

#### Initialization Strategy for Stable Memory

To ensure stable memory formation, the RNN uses a specific initialization strategy:

$$ W_{hh,ij} = \begin{cases}
\alpha + \mathcal{N}(0, \sigma^2) & \text{if } i = j \\
\mathcal{N}(0, \sigma^2) & \text{if } i \neq j
\end{cases} $$

Where:
- $ \alpha $ is the identity bias (typically 0.1) that promotes stability
- $ \mathcal{N}(0, \sigma^2) $ is Gaussian noise with mean 0 and variance $ \sigma^2 $

This initialization biases the recurrent connections toward identity mapping, which helps preserve information across time steps while allowing for learning of more complex temporal patterns.

#### Memory Gradient Flow

The gradient flow through time in the RNN is governed by the chain rule:

$$ \frac{\partial L}{\partial h_j^{(t-k)}} = \sum_{i=1}^{8} \frac{\partial L}{\partial h_i^{(t-k+1)}} \cdot \frac{\partial h_i^{(t-k+1)}}{\partial h_j^{(t-k)}} $$

Where:
$$ \frac{\partial h_i^{(t-k+1)}}{\partial h_j^{(t-k)}} = W_{ji}^{(hh)} \cdot f'(net_i^{(t-k+1)}) $$

This recursive relationship shows how gradients propagate backward through time, with the magnitude of gradients potentially vanishing or exploding depending on the eigenvalues of $ \mathbf{W}_{hh} $.

#### Optional Stochastic Noise for Exploration

The RNN can include optional stochastic noise to promote exploration:

$$ h_j^{(t)} = \tanh\left(\sum_{i=1}^{24} W_{ij}^{(input-hidden)} \cdot x_i^{(t)} + \sum_{k=1}^{8} W_{kj}^{(hidden-hidden)} \cdot h_k^{(t-1)} + b_j^{(hidden)} + \eta_j^{(t)}\right) $$

Where $ \eta_j^{(t)} \sim \mathcal{N}(0, \sigma_{noise}^2) $ is the noise term added to hidden unit $ j $ at time $ t $.

### N-Step Memory Extension

When enabled, the system stores past hidden states and provides them as additional inputs to the neural network, giving FNN agents pseudo-memory and enhancing RNN temporal reasoning capabilities. The depth is configurable (typically 1-2 steps) and the system maintains a circular buffer of past hidden states. This allows agents to make decisions based on recent history, enabling more sophisticated temporal strategies.

#### Mathematical Representation of N-Step Memory

When N-step memory is enabled, the input vector is augmented with historical hidden states:

$$ \mathbf{x}_{augmented}^{(t)} = [\mathbf{x}^{(t)}, \mathbf{h}^{(t-1)}, \mathbf{h}^{(t-2)}, ..., \mathbf{h}^{(t-n)}] $$

Where:
- $ \mathbf{x}^{(t)} $ is the original 24-dimensional input vector
- $ \mathbf{h}^{(t-i)} $ is the hidden state from $ i $ time steps ago
- $ n $ is the memory depth (typically 1-2)

This augmented input vector has dimension $ 24 + n \times 8 $, which is then processed by the neural network as usual.

#### Memory Buffer Implementation

The memory buffer operates as a circular queue with the following mathematical operations:

$$ \text{buffer}[t \bmod n] = \mathbf{h}^{(t)} $$

Where:
- $ n $ is the memory depth
- $ \mathbf{h}^{(t)} $ is the current hidden state vector
- $ \bmod $ is the modulo operator

The flattened memory vector is constructed as:

$$ \mathbf{m}^{(t)} = [\mathbf{h}^{(t-1)}, \mathbf{h}^{(t-2)}, ..., \mathbf{h}^{(t-n)}] $$

Where each $ \mathbf{h}^{(t-i)} $ is an 8-dimensional vector, resulting in a total of $ 8n $ additional input dimensions.

#### Memory Decay and Forgetting

The effective memory retention in the N-step memory system follows an exponential decay pattern:

$$ R(t) = e^{-\lambda t} $$

Where:
- $ R(t) $ is the retention of information after $ t $ time steps
- $ \lambda $ is the decay constant
- $ t $ is the number of time steps since the information was stored

For the N-step memory system, information beyond $ n $ time steps is completely forgotten, so the effective retention function becomes:

$$ R_{effective}(t) = \begin{cases}
e^{-\lambda t} & \text{if } t \leq n \\
0 & \text{if } t > n
\end{cases} $$

### Stress System

Agents maintain an internal stress level that influences their behavior and neural network inputs:
- **Gain Sources**: Nearby threats, low resources, recent damage
- **Decay**: Natural decay over time with configurable rate
- **Effects**: Influences decision-making, energy consumption, and behavioral thresholds
- **Computation**: Stress increases based on threat level, resource stress, and recent damage, then decays naturally

Mathematical representation of stress dynamics:

$$ \frac{dS}{dt} = G(t) - D \cdot S(t) $$

Where:
- $ S(t) $ is the stress level at time $ t $
- $ G(t) $ is the stress gain function at time $ t $
- $ D $ is the decay rate constant

Discretized version:
$$ S^{(t+1)} = S^{(t)} + (G^{(t)} \cdot \Delta t - D \cdot S^{(t)} \cdot \Delta t) $$

---

## Chapter 4: Genetic System {#genetic-system}

### Genome Structure

The genome consists of 8 pairs of diploid chromosomes with sophisticated organization and realistic inheritance patterns:

**Chromosome Organization**:
- **Chromosomes 0-2**: Physical and behavioral traits (speed, size, aggression, etc.)
- **Chromosome 3**: Additional trait genes and regulatory elements
- **Chromosomes 4-7**: Neural network weights (130 genes for FNN, 166 for RNN)
- **Chromosome 7**: Additional genetic information and regulatory elements

**Brain Genes**: Chromosomes 4-7 encode neural network weights with different organizations for FNN vs RNN architectures:
  - **FNN Mode**: 130 brain genes (96 input-to-hidden weights, 6 hidden biases, 24 hidden-to-output weights, 4 output biases)
  - **RNN Mode**: 166 brain genes (same as FNN plus 36 hidden-to-hidden recurrent weights)

**Trait Genes**: Chromosomes 0-2 encode physical and behavioral traits including speed, size, aggression, vision range, energy efficiency, reproduction urge, camouflage, and max age. Each trait is controlled by multiple genes for polygenic inheritance, creating realistic continuous variation.

**Gene Structure**: Each gene consists of two alleles (one from each parent) that determine trait expression through dominance relationships. The system implements complex dominance effects where one allele may partially or completely mask the expression of the other, creating realistic inheritance patterns.

**Allele Pairing**: Each gene has two alleles that form pairs, with dominance relationships determining how the paired alleles express in the phenotype. Dominance effects can be complete, incomplete, or codominant, creating complex inheritance patterns.

### Reproduction Process

**Mate Selection**: Agents must be mature, have sufficient energy, be hydrated, and be within mating distance. Mate selection is driven by the mate_desire neural network output, which is influenced by the agent's current state and genetic traits.

**Crossover**: During reproduction, chromosomes undergo crossover with configurable probability, mixing parental genetic material. The crossover rate determines how often genetic material is exchanged between parental chromosomes during meiosis.

**Mutation**: Offspring genomes undergo mutation with configurable rates, introducing genetic diversity. Both point mutations and larger mutations are possible, with different effects on fitness and behavior.

**Inheritance**: Offspring inherit mixed parental genomes with proper chromosome segregation and gene expression. The inheritance system maintains genetic diversity while preserving beneficial traits.

### Somatic Mutations

Agents can undergo lifetime mutations at a configurable rate. These mutations occur randomly throughout the agent's life and can affect any aspect of the genome, including neural network weights and physical traits. Somatic mutations can be inherited if the agent reproduces after the mutation occurs, allowing for rapid adaptation within an individual's lifetime that can be passed to offspring.

---

## Chapter 5: Simulation Systems {#simulation-systems}

### Movement System

The movement system is the most complex behavioral system, implementing sophisticated decision-making and physics:

**Sector-Based Input Computation**: Divides the agent's vision into 5 angular sectors of 72° each, computing food, water, and agent signals for each sector. This provides spatial awareness without perfect point-location knowledge, making the agents' decision-making more realistic and challenging.

**Neural Network Forward Pass**: Each frame, the system performs a forward pass through the agent's neural network brain, processing the 24 inputs (or more with memory) and producing 6 outputs that control movement and behavior. The system handles both FNN and RNN architectures appropriately.

**Position Update**: Calculates movement based on neural outputs, applying steering behaviors and physics. The system implements momentum, friction, and realistic movement dynamics.

**Behavioral Drive Application**: Interprets neural outputs as behavioral drives (avoid, approach, attack, mate) and applies them to modify the agent's movement and decision-making. For example, a high avoid drive might cause the agent to flee from threats while a high approach drive might lead it toward resources.

**Collision Handling**: Sophisticated collision detection and resolution prevents agents from passing through obstacles or terrain features. When collisions occur, the system calculates appropriate response vectors to push agents away from obstacles while preserving momentum where possible.

**Steering Behaviors**: Implements various steering behaviors like seeking, fleeing, wandering, and obstacle avoidance to create natural-looking movement patterns that respond intelligently to the environment.

**Velocity Limiting**: Ensures agents don't exceed their maximum speed capabilities based on their genetic traits and current effort level.

**Boundary Handling**: Manages world boundaries and wrapping behavior, allowing agents to move seamlessly across the world edges in torus mode or bounce off walls in bounded mode.

**Region Updates**: Updates the agent's geographic region information based on position and world settings, which affects regional trait modifiers.

### Combat System

The combat system implements sophisticated aggressive interactions with multiple factors:

**Attack Resolution**: When agents are within ATTACK_DISTANCE and have a high attack drive, the system resolves combat encounters. Damage is calculated based on the attacking agent's size, aggression trait, effort level, and other factors, as well as the defending agent's armor and other defensive traits.

**Damage Calculation**: Implements sophisticated damage calculation that considers multiple factors including size differential, aggression levels, effort investment, armor protection, and random variation. Larger, more aggressive agents deal more damage, but armored agents take less.

**Cannibalism Implementation**: Allows successful attackers to gain energy from kills, creating a viable but risky survival strategy. The KILL_ENERGY_GAIN setting determines how much energy is transferred from the killed agent to the killer.

**Attack Intent Processing**: Processes the attack intent from neural outputs and translates it into actual combat behavior, considering factors like target proximity, threat assessment, and energy costs.

**Proximity Detection**: Detects when agents are close enough to engage in combat, using efficient spatial queries to minimize computational overhead.

**Damage Application**: Applies calculated damage to attacked agents, tracking health status and determining when agents die from combat.

**Kill Handling**: Manages the consequences of successful kills, including energy transfer, removal of the killed agent from the simulation, and updating statistics.

**Combat Cooldowns**: Implements cooldown periods after combat to prevent continuous fighting and allow agents to recover.

### Feeding System

The feeding system manages all aspects of food consumption with realistic foraging dynamics:

**Food Consumption**: Allows agents to eat nearby food items when they come within eating distance. The system efficiently detects food in the agent's vicinity using spatial queries and handles consumption priority.

**Energy Restoration**: Restores energy based on the food's energy value and the agent's digestive efficiency. The amount of energy gained may be modified by the agent's traits and current state.

**Proximity Detection**: Detects food items within EATING_DISTANCE of agents, using efficient spatial queries to minimize computational overhead.

**Consumption Priority**: Implements consumption priority systems that determine which food items agents should target when multiple options are available.

**Food Competition**: Handles competition for food resources when multiple agents attempt to consume the same food item simultaneously.

**Foraging Behavior**: Implements sophisticated foraging behaviors that guide agents toward food sources based on their current energy levels and other factors.

### Hydration System

The hydration system manages water consumption and fluid balance with realistic physiological modeling:

**Hydration Drain**: Implements continuous drainage of hydration over time at a rate determined by HYDRATION_DRAIN_RATE. The drainage rate may be modified by agent traits like size and activity level.

**Drinking Behavior**: Allows agents to drink from water sources when they are within drinking range. The system efficiently detects water sources in the agent's vicinity.

**Hydration Restoration**: Restores hydration based on the DRINK_RATE and the agent's drinking efficiency. The rate of hydration gain may be affected by the agent's current state and traits.

**Water Proximity Detection**: Detects water sources within drinking range of agents using efficient spatial queries.

**Thirst Modeling**: Models thirst levels that drive agents to seek water when hydration is low. Thirst may become a priority when hydration falls below critical thresholds.

### Energy System

The energy system implements realistic metabolic processes with multiple factors affecting consumption:

**Metabolic Costs**: Applies metabolic costs based on agent traits like size, speed, and efficiency. Larger agents have higher baseline metabolic costs, while more efficient agents have lower costs.

**Energy Drain**: Implements continuous energy drain based on BASE_ENERGY_DRAIN and various activity multipliers. The drain rate may be affected by agent traits, current activity, and environmental conditions.

**Size-based Costs**: Implements metabolic scaling where larger agents pay proportionally higher energy costs. This creates a trade-off between size advantages and energy demands.

**Speed-based Costs**: Implements energy costs that scale with movement speed, making faster agents consume more energy during locomotion.

**Efficiency Factors**: Applies efficiency factors that can reduce or increase energy costs based on genetic traits and current state.

**Activity-based Costs**: Implements different energy costs for different activities like movement, combat, reproduction, and other behaviors.

### Reproduction System

The reproduction system manages all aspects of genetic inheritance and offspring creation:

**Mating Eligibility**: Determines when agents are eligible to mate based on maturity age, energy levels, hydration, and reproduction cooldown status. Agents must meet multiple criteria before they can reproduce.

**Mate Seeking**: Implements mate-seeking behaviors that guide agents toward potential partners. The system uses spatial queries to locate nearby potential mates.

**Mate Selection**: Implements mate selection criteria that may consider factors like genetic compatibility, trait quality, and availability.

**Reproduction Costs**: Implements energy costs associated with reproduction that agents must pay to successfully reproduce. The cost is determined by REPRODUCTION_COST.

**Maturity Requirements**: Implements maturity requirements that prevent young agents from reproducing until they reach MATURITY_AGE.

**Cooldown Periods**: Implements reproduction cooldowns that prevent agents from reproducing continuously. The cooldown period is determined by REPRODUCTION_COOLDOWN.

**Genetic Inheritance**: Handles the inheritance of genetic material from parents to offspring, including proper chromosome pairing and trait expression.

**Crossover Implementation**: Implements genetic crossover during meiosis that combines parental genetic material to create offspring genomes.

**Mutation Introduction**: Introduces mutations during reproduction with configurable rates, allowing for genetic diversity in offspring.

**Offspring Creation**: Creates new offspring agents with mixed genomes from their parents, properly initializing all attributes and traits.

### Aging System

The aging system implements realistic life-history dynamics with multiple age-related effects:

**Age Increment**: Continuously increments agent age over time based on simulation time passage. The aging rate may be affected by various factors.

**Death from Old Age**: Agents die when their age exceeds their genetically-determined maximum age. This creates natural mortality and population turnover.

**Individual Max Age**: Uses individual genetic max_age values that can vary between agents, creating diversity in lifespan within the population.

**Aging Effects**: Implements various aging effects on agent abilities, including reduced speed, decreased efficiency, and other age-related declines.

**Life Stages**: Implements different life stages (young, prime, old) that affect agent capabilities and behaviors differently.

### Somatic Mutation System

The somatic mutation system implements lifetime genetic changes with inheritance possibilities:

**Lifetime Mutations**: Applies mutations during agent lifetime at the rate determined by SOMATIC_MUTATION_RATE. These mutations occur randomly throughout the agent's life.

**Mutation Tracking**: Tracks accumulated mutations for visualization purposes, with more mutated agents appearing brighter in color.

**Mutation Effects**: Applies various effects of mutations, which can affect any aspect of the agent's genome, including neural network weights, physical traits, and behavioral tendencies.

### Disease Transmission System

The disease system models pathogen spread and effects with realistic epidemiological modeling:

**Transmission Modeling**: Models disease transmission between agents based on proximity and transmission probability. The system considers factors like agent health, immunity, and environmental conditions.

**Transmission Distance**: Implements distance-based transmission where diseases spread between agents within DISEASE_TRANSMISSION_DISTANCE of each other.

**Transmission Probability**: Implements probabilistic transmission that determines the likelihood of disease spread when agents are in proximity.

**Resistance Modeling**: Models genetic resistance to diseases that varies between agents based on their genetic makeup.

**Infection Tracking**: Tracks infection status of agents, monitoring which agents are infected, which diseases they carry, and the progression of infections.

**Recovery Modeling**: Models recovery from diseases with recovery rates that may vary by disease type and agent traits.

**Disease Effects**: Implements various effects of diseases on agent behavior and physiology, including reduced performance, altered behavior, and potential death.

### Events System

The events system manages special population-wide phenomena with complex triggering conditions:

**Special Event Management**: Manages special events like epidemics, resource booms, environmental changes, and other population-wide phenomena.

**Event Triggering**: Triggers events based on various conditions including population density, resource availability, time elapsed, and random probability.

**Event Effects**: Applies effects of events to agents, which may include temporary changes to behavior, physiology, or environmental conditions.

**Epidemic Management**: Manages epidemic events with special rules for disease spread, population impact, and recovery.

**Population Thresholds**: Uses population thresholds for triggering certain events, such as epidemics that require sufficient population density.

---

## Chapter 6: Environment and Entities {#environment-and-entities}

### World Structure

The world implements a sophisticated 2D environment with multiple layers of complexity:

**Spatial Grids**: Implements spatial partitioning grids to efficiently manage collision detection and neighbor queries. Instead of checking every agent against every other agent (O(n²)), the world is divided into grid cells, and agents only check for neighbors within their cell and adjacent cells (O(n)). This dramatically improves performance as the population grows.

**Boundaries**: The world can operate as a torus (wraps around at edges) or as a bounded environment with walls. Torus mode creates a continuous world where agents can travel infinitely in any direction, while bounded mode creates a finite world with defined edges.

**Dynamic Elements**: The world contains multiple dynamic elements: food clusters that drift slowly over time according to seasonal patterns, multiple water sources distributed throughout the world, and configurable terrain obstacles like mountains, rivers, and lakes.

**Environmental Complexity**: The environment includes realistic features like temperature zones, geographic regions with different trait modifiers, and seasonal resource patterns that create complex selective pressures.

### Agent Properties

The agent class implements a comprehensive individual with multiple interacting systems:

**Position and Movement**: Each agent has a Vector2 position in the world and a velocity vector that determines its movement direction and speed. The position is updated each frame based on the neural network's movement outputs and physics calculations. The velocity is subject to steering behaviors, collision responses, and momentum effects.

**Energy System**: The primary resource consumed by existing and moving. Energy drains continuously based on metabolic costs that scale with the agent's size, speed, and activity level. If energy drops to 0, the agent dies. Energy can be replenished by consuming food, with the amount gained determined by the food's energy value and the agent's efficiency traits.

**Hydration System**: The secondary resource that drains at a constant rate. If hydration drops to 0, the agent dies. Hydration can be replenished by drinking from water sources. The rate of hydration gain depends on the agent's drinking efficiency and the proximity to water.

**Age Tracking**: Increases over time and is subject to genetic maximum age limits. When age exceeds the individual's genetically-determined max_age, the agent dies. Age affects various aspects of the agent's behavior and physiology, with younger agents typically being more energetic and older agents potentially having accumulated wisdom or experience.

**Genome Structure**: The agent's complete genetic code consisting of 8 pairs of diploid chromosomes. Each chromosome contains multiple genes, and each gene has two alleles that determine trait expression.

**Phenotype Expression**: The expressed traits derived from the genome through a complex expression system that considers dominance effects, environmental factors, and developmental processes. The phenotype includes all measurable traits like speed, size, aggression, vision range, energy efficiency, reproduction urge, camouflage, and max age.

**Neural Brain**: The `NeuralBrain` instance built from the genome, which can be either a Feed-Forward Neural Network (FNN) or a Recurrent Neural Network (RNN) depending on settings. The brain processes inputs from the environment and internal state to produce behavioral outputs.

**Mutation Tracking**: Tracks accumulated mutations for visualization purposes, with more mutated agents appearing brighter in color. This provides a visual indication of genetic diversity and evolutionary activity in the population.

**Visual Diversity**: Each agent has a unique appearance based on its species and genetic makeup, with different shapes representing different species (circle, square, triangle, parallelogram, diamond, hexagon, pentagon, star). The color indicates traits like aggression (green to red gradient) and energy level (brightness), while the shape represents species membership.

### Environmental Features

The simulation includes sophisticated environmental features that create realistic ecological dynamics:

**Food System**: Spawns in drifting clusters that simulate changing seasons or resource patches. Each food item provides energy when consumed, and the system implements realistic foraging dynamics where agents must locate and compete for resources.

**Water Sources**: Fixed locations where agents can drink to restore hydration. Multiple sources create focal points for agent activity and influence spatial distribution patterns.

**Obstacles**: Terrain features including mountains, rivers, and walls that agents cannot pass through. These create environmental complexity and challenge navigation, forcing agents to develop spatial awareness and pathfinding abilities.

**Terrain Generation**: Sophisticated terrain generator creates realistic features like mountain chains, meandering rivers, and irregular lakes with configurable parameters. The generator uses realistic topographical principles to create natural-looking terrain.

---

## Chapter 7: Advanced Features {#advanced-features}

### Body Size Effects

When enabled, body size creates meaningful trade-offs that affect multiple aspects of agent behavior and physiology:

**Attack Strength**: Scales with size^SIZE_ATTACK_SCALING, making larger agents more effective in combat but creating metabolic costs.

**Speed Penalty**: Larger agents move slower due to increased mass and energy requirements, creating a trade-off between size advantages and mobility.

**Turn Penalty**: Larger agents turn more slowly due to increased moment of inertia, affecting maneuverability in combat and navigation.

**Metabolic Cost**: Scales superlinearly with size^SIZE_METABOLIC_SCALING, making larger agents pay disproportionately higher energy costs.

**Perception Bonus**: Slightly better perception range for larger agents, providing some advantages for size.

### Age-Dependent Modulation

Implements realistic life-history stages with different capabilities and strategies:

**Young Stage (0-20%)**: Lower speed/stamina but potential for rapid learning and adaptation. Young agents may be more exploratory and less risk-averse.

**Prime Stage (20-60%)**: Peak performance in all areas with optimal balance of physical capabilities and accumulated experience.

**Old Stage (60-100%)**: Reduced physical capabilities but potential wisdom benefits from accumulated experience and knowledge.

### Internal State Modulation

Implements soft penalties based on resource levels that create realistic behavioral responses:

**Low Energy**: Reduced attack effectiveness and effort capacity when energy is critically low, forcing agents to prioritize feeding.

**Low Hydration**: Reduced speed and performance when dehydrated, creating urgency for water access.

**High Stress**: Potential short-term effort boost (fight-or-flight) that can provide temporary advantages during crises.

### Action-Specific Cost Asymmetry

Implements differentiated energy costs for different activities that create realistic behavioral economics:

**High Speed**: 1.5x multiplier for maximum speed movement, making sustained high-speed travel costly.

**Sharp Turns**: 1.3x multiplier for sudden direction changes, encouraging smoother movement patterns.

**Sustained Pursuit**: 1.2x multiplier for prolonged chasing, making extended hunting costly.

**Combat**: Higher base costs for attacking, creating risk-reward calculations for aggressive behaviors.

**Reproduction**: Significant energy investment that requires careful resource management.

### Morphological Trade-offs

Introduces agility and armor traits that create sophisticated trade-offs:

**Agility**: Improves turning/acceleration but increases metabolic cost, creating a trade-off between mobility and efficiency.

**Armor**: Reduces damage but penalizes speed and increases energy cost, creating a trade-off between protection and mobility.

### Sensory Imperfection

Adds realistic perception limitations that make decision-making more challenging:

**Sensor Noise**: Gaussian noise on inputs that creates uncertainty in environmental perception.

**Sensor Dropout**: Chance of missing signals that creates occasional perceptual failures.

**Internal State Noise**: Noise on energy/hydration perception that affects decision-making accuracy.

### Context Signals

Provides additional neural network inputs tracking time since key events:

**Time Since Food**: Tracks time since last food consumption, potentially affecting hunger motivation.

**Time Since Damage**: Tracks time since last damage received, potentially affecting caution levels.

**Time Since Mating**: Tracks time since last reproduction, potentially affecting mate-seeking behavior.

### Social Pressure Effects

Models crowding and dominance effects that create realistic social dynamics:

**Crowding Stress**: Increases stress in dense areas, potentially affecting behavior and decision-making.

**Dominance Stress**: Stress from larger/aggressive neighbors, creating realistic social hierarchies.

**Social Dynamics**: Emergent social behaviors based on population density and individual characteristics.

---

## Chapter 8: User Interface and Controls {#user-interface-and-controls}

### Keyboard Controls

The simulation provides comprehensive keyboard controls for interaction and management:

| Key | Function |
|-----|----------|
| SPACE | Pause/Resume simulation - Toggles simulation execution |
| UP/DOWN | Increase/Decrease simulation speed - Adjusts simulation speed multiplier (0.25x to 8x) |
| G | Toggle Genetics Visualization menu - Shows detailed neural network and genetic information |
| S | Toggle Statistics Visualization menu - Shows population and trait evolution charts |
| F11 | Toggle fullscreen mode - Switches between windowed and fullscreen display |
| ESC | Return to settings screen - Exits simulation to main settings interface |
| H | Toggle HUD sidebar - Shows/hides heads-up display with statistics |
| O | Toggle obstacles on/off - Enables/disables terrain obstacles |
| B | Toggle border on/off - Enables/disables border walls |
| M | Add horizontal mountain chain - Creates realistic mountain chain across world |
| N | Add vertical mountain chain - Creates realistic mountain chain up/down world |
| R | Add vertical meandering river - Creates meandering river from top to bottom |
| T | Add horizontal meandering river - Creates meandering river from left to right |
| L | Add lake - Creates irregular lake shape |
| D | Add diagonal mountain range - Creates mountain range from corner to corner |
| C | Clear all obstacles (except borders) - Removes all generated obstacles |

### Settings Interface

The settings interface provides comprehensive configuration with intuitive organization:

**Card-Based Design**: Settings are organized into expandable/collapsible category cards with intuitive grouping by function (Population, Genetics, Neural Network, Energy, etc.). Each card contains related parameters that logically belong together.

**Two-Column Layout**: Efficient use of screen space with two-column layout on wide screens, maximizing the number of visible settings while maintaining readability.

**Interactive Controls**: Toggle switches for boolean settings, numeric inputs with +/- buttons, and editable fields for precise value adjustment. All controls provide immediate visual feedback.

**Conditional Visibility**: Settings only appear when their parent feature is enabled, reducing interface clutter and improving usability. For example, RNN-specific settings only appear when RNN mode is selected.

**Real-Time Updates**: Changes take effect immediately without requiring restart, allowing for experimentation with different parameter combinations.

**Category Organization**: Settings are grouped into logical categories:
- Population: Initial agents, food limits, spawn rates
- Genetics: Mutation rates, crossover rates, somatic mutations
- Neural Network: Architecture type, hidden size, weight initialization
- N-Step Memory: Memory depth and enable/disable
- Sensing: Sector count, vision noise
- Internal State: Stress parameters, health metrics
- Effort System: Effort scaling parameters
- Energy: Energy-related parameters
- Hydration: Hydration-related parameters
- Water: Water source parameters
- Combat: Attack-related parameters
- Food Clusters: Food cluster parameters
- World: World size and display parameters
- Agents: Agent-specific parameters
- Aging: Age-related parameters
- Reproduction: Reproduction parameters
- Other: Miscellaneous parameters
- Temperature Zones: Environmental temperature settings
- Initialization: Startup configuration
- Epidemic: Disease outbreak parameters
- Species: Species-related parameters
- Disease: Disease transmission parameters
- Geographic Variations: Regional trait modifiers
- Obstacles: Terrain obstacle parameters
- Rendering: Display parameters
- Trait Ranges: Valid ranges for genetic traits
- Trait Defaults: Default values for traits
- Advanced Features: Optional complex behaviors

### Visualization Systems

The simulation includes multiple sophisticated visualization systems:

**Genetics Visualization**: Detailed neural network architecture visualization showing connections and weights, species overview with population statistics, and agent detail views with genetic information. The system provides insight into how neural networks and genetics influence behavior.

**Statistics Visualization**: Historical tracking of population over time, trait evolution charts showing how genetic traits change across generations, species distribution breakdown, behavioral statistics tracking, and resource availability trends. The system provides quantitative insights into evolutionary and ecological dynamics.

**HUD Display**: Real-time statistics including population counts, species diversity, resource availability, average trait values (speed, size, aggression), top species with color-coded indicators, simulation time and speed, and keyboard shortcut hints. The HUD provides immediate feedback on simulation state.

---

## Chapter 9: Configuration Parameters {#configuration-parameters}

### Population Settings
- `INITIAL_AGENTS`: Starting number of agents in the simulation (default 150)
- `MAX_FOOD`: Maximum number of food items allowed in the world (default 400)
- `FOOD_SPAWN_RATE`: Rate at which new food items are created per second (default 30)

### Genetics Settings
- `MUTATION_RATE`: Probability of mutation per gene during reproduction (default 0.2)
- `CROSSOVER_RATE`: Probability of crossover per chromosome during meiosis (default 0.3)
- `LARGE_MUTATION_CHANCE`: Within mutations, chance of large effect (default 0.05)
- `DOMINANCE_MUTATION_RATE`: Chance a mutation affects dominance instead of value (default 0.15)
- `POINT_MUTATION_STDDEV`: Standard deviation for point mutations (default 0.3)
- `LARGE_MUTATION_STDDEV`: Standard deviation for large-effect mutations (default 1.5)
- `SOMATIC_MUTATION_RATE`: Rate of lifetime mutations per agent (default 0.2)

### Neural Network Settings
- `NN_TYPE`: Network architecture ('FNN' or 'RNN') (default 'FNN')
- `NN_HIDDEN_SIZE`: Number of hidden neurons (default 8)
- `NN_WEIGHT_INIT_STD`: Standard deviation for initial weight randomization (default 0.3)
- `NN_RECURRENT_IDENTITY_BIAS`: Stability bias for RNN hidden-to-hidden connections (default 0.1)
- `NN_HIDDEN_NOISE_ENABLED`: Add stochastic noise to RNN hidden state (default False)
- `NN_HIDDEN_NOISE_STD`: Noise standard deviation (default 0.02)

### N-Step Memory Settings
- `N_STEP_MEMORY_ENABLED`: Enable memory buffer (default False)
- `N_STEP_MEMORY_DEPTH`: Number of past states to store (default 2)

### Sensing Settings
- `SECTOR_COUNT`: Number of angular vision sectors (default 5)
- `VISION_NOISE_STD`: Noise added to sensor inputs (default 0.05)

### Internal State Settings
- `STRESS_GAIN_RATE`: Stress accumulation rate (default 0.5)
- `STRESS_DECAY_RATE`: Stress natural decay rate (default 0.2)
- `STRESS_THREAT_WEIGHT`: Weight for nearby threat stress (default 1.0)
- `STRESS_RESOURCE_WEIGHT`: Weight for low resource stress (default 0.5)

### Effort System Settings
- `EFFORT_SPEED_SCALE`: How much effort affects speed (default 1.0)
- `EFFORT_DAMAGE_SCALE`: How much effort affects attack damage (default 0.5)
- `EFFORT_ENERGY_SCALE`: How much effort affects energy cost (default 1.5)

### Energy Settings
- `BASE_ENERGY`: Starting energy value (default 150.0)
- `MAX_ENERGY`: Maximum energy capacity (default 300.0)
- `REPRODUCTION_THRESHOLD`: Energy needed to reproduce (default 80.0)
- `REPRODUCTION_COST`: Energy cost of reproduction (default 40.0)
- `FOOD_ENERGY`: Energy gained from food (default 60.0)
- `ENERGY_DRAIN_BASE`: Base energy loss per second (default 0.3)
- `MOVEMENT_ENERGY_FACTOR`: Energy cost of movement (default 0.01)

### Hydration Settings
- `BASE_HYDRATION`: Starting hydration value (default 100.0)
- `MAX_HYDRATION`: Maximum hydration capacity (default 150.0)
- `HYDRATION_DRAIN_RATE`: Hydration loss per second (default 0.4)
- `DRINK_RATE`: Hydration gain per second when drinking (default 30.0)

### Water Settings
- `NUM_WATER_SOURCES`: Number of water sources (default 4)
- `WATER_SOURCE_RADIUS`: Radius of water sources (default 40.0)

### Combat Settings
- `ATTACK_DISTANCE`: Distance threshold for attacks (default 10.0)
- `ATTACK_DAMAGE_BASE`: Base damage per second of attack (default 20.0)
- `ATTACK_ENERGY_COST`: Energy cost per second of attacking (default 2.0)
- `KILL_ENERGY_GAIN`: Energy gained from successful kills (default 30.0)

### Food Cluster Settings
- `NUM_FOOD_CLUSTERS`: Number of food cluster centers (default 5)
- `FOOD_CLUSTER_SPREAD`: Gaussian sigma for food scatter (default 40.0)
- `SEASON_SHIFT_INTERVAL`: Seconds between cluster drift (default 30.0)

### World Settings
- `WORLD_WIDTH`: Width of the simulation world (default 1200)
- `WORLD_HEIGHT`: Height of the simulation world (default 600)
- `GRID_CELL_SIZE`: Size of spatial grid cells for neighbor queries (default 50)
- `HUD_WIDTH`: Width of the heads-up display panel (default 280)
- `WINDOW_WIDTH`: Width of the display window (default 3280)
- `WINDOW_HEIGHT`: Height of the display window (default 1400)

### Agent Settings
- `MAX_SPEED_BASE`: Base maximum speed capability (default 6.0)
- `EATING_DISTANCE`: Distance threshold for food consumption (default 10.0)
- `MATING_DISTANCE`: Distance for reproduction (default 50.0)
- `WANDER_STRENGTH`: Strength of wandering behavior (default 0.5)
- `STEER_STRENGTH`: Strength of steering behavior (default 0.3)

### Aging Settings
- `MATURITY_AGE`: Age when agents become capable of reproduction (default 5.0)
- `MAX_AGE`: Maximum genetic age limit (default 70.0)

### Reproduction Settings
- `REPRODUCTION_COOLDOWN`: Time between reproduction attempts in seconds (default 3.0)
- `MATE_SEARCH_RADIUS`: Search radius for finding mates (default 100.0)
- `MAX_SIMULTANEOUS_OFFSPRING`: Maximum offspring per mating session (default 1)

### Other Settings
- `CANNIBALISM_ENERGY_BONUS`: Additional energy gained from eating another agent (default 20.0)

### Temperature Zone Settings
- `TEMPERATURE_ENABLED`: Enable/disable temperature zones (default False)
- `TEMPERATURE_ZONES_X`: Number of temperature zones horizontally (default 2)
- `TEMPERATURE_ZONES_Y`: Number of temperature zones vertically (default 2)

### Initialization Settings
- `RANDOM_AGE_INITIALIZATION`: Initialize agents with random ages (default True)

### Epidemic Settings
- `EPIDEMIC_ENABLED`: Enable/disable epidemic events (default False)
- `EPIDEMIC_INTERVAL`: Seconds between epidemic checks (default 100.0)
- `EPIDEMIC_MIN_POPULATION_RATIO`: Minimum population ratio to trigger epidemic (default 0.8)
- `EPIDEMIC_AFFECTED_RATIO`: Fraction of population affected by epidemic (default 0.3)
- `EPIDEMIC_BASE_PROBABILITY`: Base probability when conditions met (default 0.001)

### Species Settings
- `INITIAL_SAME_SPECIES_PERCENTAGE`: Percentage from same species initially (default 1.0)
- `SPECIES_GENETIC_SIMILARITY_THRESHOLD`: Similarity threshold for same species (default 0.8)
- `SPECIES_DRIFT_RATE`: Rate of genetic difference accumulation (default 0.4)
- `HYBRID_FERTILITY_RATE`: Fertility for cross-species offspring (default 0.1)
- `NUMBER_OF_INITIAL_SPECIES`: Number of different species initially (default 4)

### Geographic Variation Settings
- `REGIONAL_VARIATIONS_ENABLED`: Enable/disable regional trait modifiers (default False)
- `NUM_REGIONS_X`: Number of regions horizontally (default 2)
- `NUM_REGIONS_Y`: Number of regions vertically (default 2)
- `REGION_SPEED_MODIFIER`: Speed modifiers for each region (TL, TR, BL, BR) (default [1.1, 0.9, 1.0, 1.2])
- `REGION_SIZE_MODIFIER`: Size modifiers for each region (default [0.9, 1.1, 1.0, 0.8])
- `REGION_AGGRESSION_MODIFIER`: Aggression modifiers for each region (default [1.2, 0.8, 1.0, 1.3])
- `REGION_EFFICIENCY_MODIFIER`: Energy efficiency modifiers for each region (default [0.95, 1.05, 1.0, 0.85])

### Disease Settings
- `DISEASE_TRANSMISSION_ENABLED`: Enable/disable disease transmission (default True)
- `DISEASE_TRANSMISSION_DISTANCE`: Distance threshold for transmission (default 15.0)
- `DISEASE_NAMES`: Names for different diseases (default ['Flu', 'Plague', 'Malaria', 'Pox', 'Fever', 'Rot', 'Blight', 'Wilt'])
- `NUM_DISEASE_TYPES`: Number of different disease types (default 4)

### Obstacle Settings
- `OBSTACLES_ENABLED`: Enable/disable obstacles (default False)
- `BORDER_ENABLED`: Enable/disable border walls (default True)
- `BORDER_WIDTH`: Width of border obstacles (default 10)
- `NUM_INTERNAL_OBSTACLES`: Number of internal obstacles (default 5)

### Rendering Settings
- `FPS`: Target frames per second (default 60)

### Trait Range Settings
- `TRAIT_RANGES`: Dictionary defining valid ranges for each trait:
  - `speed`: (1.0, 6.0)
  - `size`: (3.0, 12.0)
  - `vision_range`: (40.0, 200.0)
  - `energy_efficiency`: (0.5, 2.0)
  - `reproduction_urge`: (0.3, 1.5)
  - `camouflage`: (0.0, 1.0)
  - `aggression`: (0.3, 2.0)
  - `max_age`: (10.0, 150.0)
  - `virus_resistance`: (0.0, 1.0)
  - `agility`: (0.0, 1.0)
  - `armor`: (0.0, 1.0)

### Trait Default Settings
- `TRAIT_DEFAULTS`: Dictionary defining default values for each trait:
  - `speed`: 3.0
  - `size`: 6.0
  - `vision_range`: 100.0
  - `energy_efficiency`: 1.0
  - `reproduction_urge`: 0.8
  - `camouflage`: 0.5
  - `aggression`: 1.0
  - `max_age`: 70.0
  - `virus_resistance`: 0.5
  - `agility`: 0.5
  - `armor`: 0.5

### Advanced Feature Flags
- `ADVANCED_SIZE_EFFECTS_ENABLED`: Enable size-based trade-offs (default False)
- `AGE_EFFECTS_ENABLED`: Enable age-based modulation (default False)
- `INTERNAL_STATE_MODULATION_ENABLED`: Enable soft internal state effects (default False)
- `ACTION_COSTS_ENABLED`: Enable differentiated action costs (default False)
- `MORPHOLOGY_TRAITS_ENABLED`: Enable agility and armor traits (default False)
- `SENSORY_NOISE_ENABLED`: Enable sensory noise (default True)
- `CONTEXT_SIGNALS_ENABLED`: Enable time-since-event signals (default False)
- `SOCIAL_PRESSURE_ENABLED`: Enable crowding/social stress (default True)

### Advanced Feature Parameters
#### Body Size Effects Parameters
- `SIZE_ATTACK_SCALING`: Exponent for attack strength scaling (1.5)
- `SIZE_SPEED_PENALTY`: Linear penalty per size unit for speed (0.3)
- `SIZE_TURN_PENALTY`: Penalty for turning (0.4)
- `SIZE_METABOLIC_SCALING`: Exponent for metabolic cost (1.3)
- `SIZE_PERCEPTION_BONUS`: Bonus for perception range (0.1)

#### Size-Scaled Energy Costs Parameters
- `SUPERLINEAR_ENERGY_SCALING`: Use superlinear scaling (True)
- `ENERGY_SIZE_EXPONENT`: Exponent for metabolic cost scaling (1.4)
- `EFFORT_SIZE_INTERACTION`: How effort amplifies size cost (0.5)

#### Age-Dependent Modulation Parameters
- `AGE_PRIME_START`: Age ratio when prime begins (0.2)
- `AGE_PRIME_END`: Age ratio when prime ends (0.6)
- `AGE_SPEED_DECLINE`: Max speed reduction in old age (0.3)
- `AGE_STAMINA_DECLINE`: Max stamina reduction in old age (0.4)
- `AGE_EXPERIENCE_BONUS`: Combat bonus from experience (0.2)
- `AGE_REPRODUCTION_CURVE`: Reproduction effectiveness varies with age (True)

#### Internal State Modulation Parameters
- `LOW_ENERGY_ATTACK_PENALTY`: Attack effectiveness penalty when energy low (0.5)
- `LOW_HYDRATION_SPEED_PENALTY`: Speed penalty when dehydrated (0.3)
- `HIGH_STRESS_EFFORT_BOOST`: Stress boost for short-term effort (0.2)
- `EXHAUSTION_THRESHOLD`: Energy level for penalties (0.2)

#### Action-Specific Cost Asymmetry Parameters
- `COST_HIGH_SPEED_MULTIPLIER`: Extra cost for max speed (1.5)
- `COST_SHARP_TURN_MULTIPLIER`: Extra cost for sharp turns (1.3)
- `COST_PURSUIT_MULTIPLIER`: Extra cost for sustained pursuit (1.2)
- `COST_ATTACK_BASE`: Base energy cost per attack tick (3.0)
- `COST_MATING_BASE`: Energy cost for mating attempt (5.0)

#### Morphological Trade-offs Parameters
- `AGILITY_SPEED_BONUS`: Turning/acceleration bonus (0.4)
- `AGILITY_STAMINA_COST`: Metabolism cost for agility (0.2)
- `ARMOR_DAMAGE_REDUCTION`: Damage reduction from armor (0.4)
- `ARMOR_SPEED_PENALTY`: Speed penalty from armor (0.3)
- `ARMOR_ENERGY_COST`: Maintenance cost for armor (0.15)

#### Sensory Imperfection Parameters
- `SENSOR_DROPOUT_RATE`: Probability of missing sector signals (0.05)
- `INTERNAL_STATE_NOISE`: Noise on internal state perception (0.03)
- `PERCEPTION_LAG`: Delay in perception (0.0 = disabled)

#### Context Signals Parameters
- `TIME_SINCE_FOOD_DECAY`: Seconds for food signal to decay (10.0)
- `TIME_SINCE_DAMAGE_DECAY`: Seconds for damage signal to decay (15.0)
- `TIME_SINCE_MATING_DECAY`: Seconds for mating signal to decay (20.0)

#### Social Pressure Effects Parameters
- `CROWD_STRESS_RADIUS`: Radius for counting nearby agents (50.0)
- `CROWD_STRESS_THRESHOLD`: Number of agents before stress increases (3)
- `CROWD_STRESS_RATE`: Stress increase per extra agent (0.1)
- `DOMINANCE_STRESS_FACTOR`: Stress from larger/aggressive neighbors (0.5)

---

## Chapter 10: Data Structures {#data-structures}

### Agent Class
The Agent class represents individual creatures in the simulation with comprehensive attributes and methods:

**Core Attributes**:
- **ID**: Sequentially assigned unique identifier for the agent
- **Position**: Vector2 position in the world
- **Velocity**: Vector2 movement direction and speed
- **Genome**: The agent's complete genetic code
- **Phenotype**: Expressed traits derived from the genome
- **Brain**: Neural network controller (FNN or RNN based on settings)
- **Energy/Hydration/Age**: Vital statistics
- **Generation**: Genetic generation number of the agent
- **State flags**: Alive status, reproduction cooldown, etc.
- **Total Mutations**: Accumulated mutations for visualization purposes

**Neural Network Attributes**:
- **NN Type**: Neural network architecture type (FNN or RNN)
- **Brain Rebuild Capability**: Ability to rebuild brain from current genome after somatic mutations
- **Brain State Reset**: Ability to reset RNN hidden state on significant events
- **Saved Hidden State Preservation**: Preserves RNN hidden state during brain rebuilds when possible
- **Neural outputs**: Last computed movement and behavioral drives (move_x, move_y, avoid, attack, mate, effort)
- **Attack Drive**: Tendency to engage in combat behavior
- **Mate Desire**: Tendency to seek reproduction opportunities
- **Avoid Drive**: Tendency to flee from threats
- **Behavioral Drives**: Decoupled behavioral tendencies (avoid, attack, mate) that influence movement
- **Effort System**: Global intensity/energy expenditure level that scales all activities
- **Internal state**: Stress level, recent damage, memory buffer
- **Recent Damage**: Tracking of damage recently received for stress calculations
- **Last Velocity**: Previous velocity for calculating sharp turn detection in energy costs
- **Memory Buffer**: N-step memory storage for temporal context (when enabled)
- **Last NN Inputs/Outputs**: Stored for visualization
- **Last Hidden Activations**: Stored for visualization

**Genetic Attributes**:
- **Genetic Similarity Calculation**: Method for comparing genetic makeup between agents
- **Calculate Genetic Similarity Method**: Function for computing genetic similarity with another agent
- **Genetic Distance Calculation**: Method for measuring how genetically different an agent is from population mean
- **Calculate Genetic Distance From Mean Method**: Function for computing genetic difference from population average
- **Species Classification**: Based on genetic similarity
- **Determine Shape Type Method**: Function for determining visual shape based on species ID
- **Same Species Check Method**: Function for determining if another agent belongs to the same species
- **Genetic Similarity Score**: Measure of similarity to original species (0.0-1.0)
- **Genetic Similarity Score Property**: Getter for genetic similarity score
- **Calculate Genetic Distance From Mean Method**: Function for computing genetic difference from population average
- **Genetic Distance Calculation**: Method for measuring how genetically different an agent is from population mean
- **Calculate Genetic Similarity Method**: Function for computing genetic similarity with another agent
- **Genetic Similarity Calculation**: Method for comparing genetic makeup between agents
- **Same Species Check Method**: Function for determining if another agent belongs to the same species
- **Determine Shape Type Method**: Function for determining visual shape based on species ID
- **Species Classification**: Based on genetic similarity

**Behavioral Attributes**:
- **Dietary Classification**: Updated based on behavior ('omnivore', 'carnivore', 'herbivore')
- **Dietary Classification Property**: Getter for current dietary classification
- **Hunting Success Rate**: Tracked based on attack success
- **Hunting Success Rate Property**: Getter for hunting success rate
- **Herding Behavior**: Tendency to stay near food sources
- **Herding Behavior Property**: Getter for herding behavior value
- **Carnivorous Tendency**: Tracked based on behavior
- **Carnivorous Tendency Property**: Getter for carnivorous tendency value
- **Herbivorous Tendency**: Tracked based on behavior
- **Herbivorous Tendency Property**: Getter for herbivorous tendency value
- **Dietary Behavior Tracking**: Continuous monitoring of feeding patterns and classification
- **Dietary Behavior Tracking Property**: Getter for dietary behavior tracking status
- **Dietary Behavior Update Method**: Function for updating dietary classification based on recent actions

**Mutation Attributes**:
- **Mutation History**: Complete record of all mutations over agent's lifetime
- **Mutation History Property**: Getter for complete mutation history
- **Dominant Mutations**: Significant mutations that define the agent's characteristics
- **Dominant Mutations Property**: Getter for dominant mutations list
- **Somatic Mutation Timer**: Countdown for recent lifetime mutations
- **Somatic Mutation Timer Property**: Getter for somatic mutation countdown timer
- **Total Mutations**: Accumulated mutations for visualization purposes
- **Total Mutations Property**: Getter for accumulated mutation count

**Disease Attributes**:
- **Disease Resistances**: Genetic resistances to different diseases
- **Disease Resistances Property**: Getter for genetic disease resistances
- **Disease Recovery Rates**: How quickly agents recover from diseases
- **Disease Recovery Rates Property**: Getter for disease recovery rate values
- **Get Disease Resistance Method**: Function for retrieving resistance to a specific disease
- **Can Catch Disease Method**: Function for checking if agent can contract a specific disease
- **Apply Disease Effects Method**: Function for applying specific effects of a disease to the agent
- **Reverse Disease Effects Method**: Function for reversing disease effects upon recovery
- **Infection Status**: Whether agent is currently infected
- **Infection Status Property**: Getter for current infection status
- **Current Disease**: Name of the disease affecting the agent
- **Current Disease Property**: Getter for current disease name
- **Infection Timer**: Duration remaining for infection effects
- **Infection Timer Property**: Getter for infection duration timer
- **Infection Methods**: Functions for infecting, recovering, and checking disease resistance
- **Infection Status Update Method**: Function for updating infection status and handling recovery

**Physical Attributes**:
- **Radius**: Calculated based on the agent's size trait
- **Radius Property**: Getter for agent's display radius based on size and species
- **Speed Property**: Getter for speed with regional modifiers applied
- **Size Property**: Getter for size with regional modifiers applied
- **Vision Range Property**: Getter for vision range from phenotype
- **Efficiency Property**: Getter for efficiency with regional modifiers applied
- **Aggression Property**: Getter for aggression with regional modifiers applied
- **Max Age Property**: Getter for genetic maximum age
- **Virus Resistance Property**: Getter for genetic virus resistance
- **Agility Property**: Getter for morphological agility trait
- **Armor Property**: Getter for morphological armor trait
- **Sex Property**: Getter for genetic sex determination
- **Shape Type**: Determined based on species ID (circle, square, triangle, parallelogram, diamond, hexagon, pentagon, star)
- **Shape Type Property**: Getter for visual shape based on species ID
- **Facing Angle**: Determined by velocity direction for sector-based sensing
- **Region**: Determined based on position and world settings
- **Region Property**: Getter for current geographic region
- **Determine Region Method**: Function for calculating which geographic region the agent is in
- **Region Update Method**: Function for updating agent's region when it moves to a new area
- **Region Trait Modifiers**: Specific modifiers for speed, size, aggression, efficiency, etc. based on geographic region
- **Get Region Trait Modifiers Method**: Function for retrieving trait modifiers based on current region
- **Modified Traits**: Traits adjusted by regional modifiers
- **Modified Traits Property**: Getter for traits with regional adjustments applied
- **Get Modified Trait Method**: Function for retrieving trait values with regional modifications applied
- **Get Modified Trait Method Property**: Getter for trait modification retrieval method

**Reproduction and Survival Attributes**:
- **Offspring Count**: Number of successful reproductions
- **Offspring Count Property**: Getter for number of successful reproductions
- **Reproduction Success Tracking**: Monitoring of successful reproduction events
- **Can Reproduce Method**: Function for checking if agent meets reproduction requirements
- **Death Handling**: Function for managing agent death and cleanup
- **Reproduction Cooldown Property**: Getter for reproduction cooldown timer
- **Energy Property**: Getter for current energy level
- **Hydration Property**: Getter for current hydration level
- **Age Property**: Getter for current age
- **Generation Property**: Getter for genetic generation number

**Visual and Sensory Attributes**:
- **Base Color**: Fixed color based on genetic makeup (calculated once at initialization)
- **Base Color Property**: Getter for fixed base color
- **Color Calculation**: Method for determining base color from genetic color traits
- **Color Calculation Property**: Getter for color calculation method
- **Get Color Method**: Function for retrieving agent's current color with energy brightness applied
- **Get Color Method Property**: Getter for color retrieval method
- **Current Modifiers**: Dynamic modifiers from advanced features
- **Current Modifiers Property**: Getter for current dynamic modifiers
- **Visual properties**: Base color, shape type, size
- **Visual Properties**: Contains base color, shape type, and size getters
- **Species info**: Species ID and genetic similarity score
- **Species ID Property**: Getter for species identifier
- **Disease tracking**: Infection status and resistances
- **Disease Tracking Properties**: Contains infection status, current disease, and resistance getters

**System Integration Attributes**:
- **Legacy Compatibility**: Attack intent for backward compatibility with older systems
- **Brain Rebuild Capability**: Ability to rebuild brain from current genome after somatic mutations
- **Brain State Reset**: Ability to reset RNN hidden state on significant events
- **Saved Hidden State Preservation**: Preserves RNN hidden state during brain rebuilds when possible
- **Behavioral Drives Property**: Getter for behavioral drive values
- **Effort Property**: Getter for current effort level
- **Stress Property**: Getter for current stress level
- **Recent Damage Property**: Getter for recent damage value
- **Memory Buffer Property**: Getter for memory buffer reference
- **Last NN Inputs Property**: Getter for last neural network inputs
- **Last NN Outputs Property**: Getter for last neural network outputs
- **Last Hidden Activations Property**: Getter for last hidden layer activations
- **Neural Outputs Property**: Getter for last computed neural network outputs
- **Behavioral Drives**: Decoupled behavioral tendencies (avoid, attack, mate) that influence movement
- **Effort System**: Global intensity/energy expenditure level that scales all activities
- **Internal state**: Stress level, recent damage, memory buffer
- **Memory Buffer Property**: Getter for memory buffer reference
- **Recent Damage**: Tracking of damage recently received for stress calculations
- **Last Velocity Property**: Getter for previous velocity value
- **Attack Drive Property**: Getter for attack tendency value
- **Mate Desire Property**: Getter for mate desire value
- **Avoid Drive Property**: Getter for avoid tendency value
- **Effort Property**: Getter for current effort level
- **Stress Property**: Getter for current stress level
- **Recent Damage Property**: Getter for recent damage value
- **Species ID Property**: Getter for species identifier
- **Visual Properties**: Contains base color, shape type, and size getters
- **Disease Tracking Properties**: Contains infection status, current disease, and resistance getters

### World Class
The World class manages the simulation environment with comprehensive entity and system management:

**Entity Lists**:
- **Agent List**: All living agents in the world
- **Food List**: All food items in the world
- **Water List**: All water sources in the world
- **Obstacle List**: All terrain obstacles in the world

**Spatial Grids**:
- **Agent Grid**: Spatial grid for efficient agent neighbor queries
- **Food Grid**: Spatial grid for efficient food neighbor queries
- **Water Grid**: Spatial grid for efficient water neighbor queries
- **Obstacle Grid**: Spatial grid for efficient obstacle neighbor queries

**Environmental Systems**:
- **Food Clusters**: System for managing drifting food cluster spawn points
- **Settings Reference**: Reference to current simulation parameters
- **Temperature Zones**: System for geographic temperature variations
- **World Dimensions**: Width and height of the simulation world
- **Spatial Grid System**: Optimized data structures for neighbor queries

**Management Functions**:
- **Cleanup Method**: Function for removing dead agents and expired items
- **Spawn Food Method**: Function for creating new food items based on settings
- **Food Clusters Update**: Function for drifting food cluster positions over time
- **Get Temperature At Position Method**: Function for calculating temperature at specific locations
- **Rebuild Grids Method**: Function for updating spatial grids each frame
- **Query Nearest Method**: Function for finding nearest entities of specific types
- **Query Radius Method**: Function for finding entities within a radius
- **World Boundary Handling**: Methods for handling agent movement across world boundaries
- **World Wrapping**: Torus implementation (agents wrap around edges)
- **Collision Detection**: Methods for detecting collisions between agents and obstacles
- **Event Manager Reference**: Connection to the event management system
- **Disease Transmission System**: Connection to the disease spread system
- **Statistics Collector**: Connection to the statistical tracking system

### Neural Network Classes

#### NeuralBrain (FNN)
The Feed-Forward Neural Network implementation with 24 inputs → 8 hidden → 6 outputs:

**Architecture**:
- **N_INPUTS**: 24 inputs (sector-based sensing)
- **N_HIDDEN**: 8 hidden neurons with tanh activation
- **N_OUTPUTS**: 6 outputs (movement and behavioral drives)
- **N_WEIGHTS**: 254 total weights (192 input-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)

**Weights and Biases**:
- **Input-to-Hidden Weights**: 192 weights (24 inputs × 8 hidden)
- **Hidden Biases**: 8 bias values for hidden neurons
- **Hidden-to-Output Weights**: 48 weights (8 hidden × 6 outputs)
- **Output Biases**: 6 bias values for output neurons

**Processing**:
- **Forward Method**: Performs forward pass through the network
- **Input Validation**: Ensures proper input length with padding if needed
- **Hidden Activation Storage**: Stores last hidden activations for visualization
- **Output Labels**: Provides labels for the 6 outputs (move_x, move_y, avoid, attack, mate, effort)

#### RecurrentBrain (RNN)
The Recurrent Neural Network implementation with memory and temporal processing:

**Architecture**:
- **N_INPUTS**: 24 inputs (sector-based sensing)
- **N_HIDDEN**: 8 hidden neurons with tanh activation and recurrent connections
- **N_OUTPUTS**: 6 outputs (movement and behavioral drives)
- **N_WEIGHTS**: 318 total weights (192 input-hidden + 64 hidden-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)

**Recurrent Connections**:
- **Input-to-Hidden Weights**: 192 weights (24 inputs × 8 hidden)
- **Hidden-to-Hidden Weights**: 64 recurrent weights (8 hidden × 8 hidden) for memory
- **Hidden Biases**: 8 bias values for hidden neurons
- **Hidden-to-Output Weights**: 48 weights (8 hidden × 6 outputs)
- **Output Biases**: 6 bias values for output neurons

**Memory and State**:
- **Hidden State**: Maintains temporal memory across time steps
- **Initial State**: Initialized with small random values to prevent saturation
- **Identity Bias**: Stability bias for recurrent connections
- **Noise Options**: Optional stochastic noise for exploration
- **State Reset**: Ability to reset hidden state when needed
- **State Retrieval**: Method to get current hidden state for memory systems

#### MemoryBuffer Class
The N-step memory buffer for temporal context:

**Structure**:
- **N Steps**: Number of past states to store
- **Hidden Size**: Size of each hidden state vector
- **Buffer**: Circular buffer storing past hidden states

**Operations**:
- **Push Method**: Adds new hidden state, shifts old ones out
- **Get Flat Method**: Returns flattened buffer for input concatenation
- **Reset Method**: Clears the buffer
- **Memory Depth**: Configurable number of past states to remember

### SpatialGrid Class
The spatial partitioning system for efficient neighbor queries:

**Grid Structure**:
- **Grid Cells**: Divides world into discrete cells for spatial queries
- **Efficient Queries**: Fast neighbor and range queries
- **Dynamic Updates**: Handles moving entities

**Query Methods**:
- **Query Radius Method**: Finds entities within a specified radius
- **Query Nearest Method**: Finds nearest entity of a specific type
- **Insert Method**: Adds entities to the grid
- **Remove Method**: Removes entities from the grid
- **Clear Method**: Empties all grid cells
- **Update Method**: Updates entity positions in the grid

**Performance**:
- **Cell Size**: Configurable size of each grid cell
- **World Partitioning**: Efficient partitioning of world space
- **Neighbor Optimization**: Dramatically improves performance of spatial queries

### ParticleSystem Class
The visual effects system for animations and particles:

**Particle Types**:
- **Heart Particles**: Created during mating events
- **Cloud Particles**: Created for infection effects
- **Other Effects**: Various visual enhancement particles

**Animation**:
- **Update Method**: Updates particle positions and lifecycles
- **Draw Method**: Renders particles to the screen
- **Lifecycle Management**: Birth, movement, and death of particles
- **Performance Optimization**: Efficient handling of large numbers of particles

---

## Chapter 11: Implementation Details {#implementation-details}

### Performance Considerations

The simulation implements several performance optimizations to handle large populations efficiently:

**Spatial Partitioning**: Uses grid-based spatial partitioning to reduce collision detection from O(n²) to O(n) complexity. Instead of checking every agent against every other agent, the world is divided into grid cells, and agents only check for neighbors within their cell and adjacent cells. This dramatically improves performance as the population grows.

**Efficient Queries**: Implements optimized spatial queries that can quickly find nearby entities without iterating through all entities in the world.

**Batch Processing**: Groups similar operations together to reduce function call overhead and improve cache locality.

**Memory Management**: Uses efficient data structures and avoids unnecessary object creation during the simulation loop.

**Selective Updates**: Only updates agents that are alive and active, skipping dead or inactive entities.

**Optimized Neural Networks**: Implements neural network computations efficiently without external dependencies like NumPy, using pure Python with optimized matrix operations.

### Scalability Features

The simulation is designed to scale with population size:

**Grid-Based Spatial Queries**: As mentioned, this reduces computational complexity from quadratic to linear with respect to population size.

**Modular Systems**: Each system operates independently but can be optimized separately for performance.

**Configurable Parameters**: Many parameters can be adjusted to balance between biological realism and computational efficiency.

**Event-Driven Architecture**: Uses event-driven systems that only activate when conditions are met, rather than continuously checking all agents.

### Extensibility

The simulation is designed to be extensible:

**Modular Architecture**: Systems are designed to be independent and can be modified or replaced without affecting other systems.

**Plugin System**: The architecture supports adding new features and behaviors through modular components.

**Configuration-Driven**: Most behaviors can be modified through configuration parameters without code changes.

**Genetic Flexibility**: The genetic system is flexible enough to accommodate new traits and behaviors through evolution.

### Error Handling and Robustness

The simulation includes robust error handling:

**Input Validation**: Validates neural network inputs and ensures proper ranges.

**Bounds Checking**: Prevents agents from exceeding valid trait ranges.

**Exception Handling**: Gracefully handles exceptions without crashing the simulation.

**Recovery Mechanisms**: Implements recovery from various failure states.

### Visualization and Monitoring

The simulation includes comprehensive visualization and monitoring:

**Real-Time Statistics**: Tracks and displays population statistics, trait evolution, and behavioral patterns.

**Genetic Visualization**: Shows neural network architecture and genetic information for selected agents.

**Historical Tracking**: Maintains historical data for long-term analysis.

**Performance Metrics**: Monitors simulation performance and provides feedback.

### Biological Accuracy

The simulation incorporates realistic biological principles:

**Genetic Inheritance**: Implements realistic diploid inheritance with dominance effects.

**Metabolic Scaling**: Uses realistic metabolic scaling laws based on body size.

**Resource Management**: Models realistic energy and hydration management with trade-offs.

**Life History**: Implements realistic aging and life-history strategies.

**Behavioral Ecology**: Models realistic behavioral strategies based on resource availability and competition.

### Evolutionary Dynamics

The simulation captures important evolutionary dynamics:

**Selection Pressure**: Implements selection based on survival and reproduction success.

**Genetic Drift**: Models random genetic drift effects in small populations.

**Mutation-Selection Balance**: Balances mutation introduction with selection pressure.

**Trade-offs**: Implements realistic biological trade-offs that constrain evolution.

**Adaptive Landscapes**: Creates complex adaptive landscapes with multiple possible strategies.

### Emergent Complexity

The simulation demonstrates emergent complexity through:

**Behavioral Strategies**: Complex strategies emerge from simple neural network outputs.

**Social Dynamics**: Social behaviors emerge from agent interactions.

**Ecological Interactions**: Complex ecological relationships emerge from resource competition.

**Evolutionary Arms Races**: Competitive interactions drive evolutionary change.

**Niche Construction**: Agents modify their environment, creating new selection pressures.

This comprehensive documentation covers all major aspects of the population simulation, including its architecture, systems, parameters, and implementation details. The simulation provides a rich platform for studying evolutionary and ecological processes through computational modeling.

**Species Formation Criteria:**
- **Genetic Similarity Threshold**: Populations with less than 80% genetic similarity are considered separate species
- **Reproductive Compatibility**: Members of the same species can successfully reproduce
- **Morphological Differences**: Gradual accumulation of physical trait differences
- **Behavioral Divergence**: Changes in mating behaviors, feeding strategies, or habitat preferences

**Speciation Process:**
- **Initial Separation**: Geographic, temporal, or behavioral barriers arise
- **Independent Evolution**: Populations evolve independently under different selective pressures
- **Character Displacement**: Traits diverge to reduce competition between species
- **Reinforcement**: Natural selection favors individuals that avoid hybrid matings
- **Completion**: Reproductive isolation becomes complete, forming distinct species

**Factors Influencing Speciation Rate:**
- **Mutation Rate**: Higher mutation rates accelerate divergence
- **Population Size**: Smaller populations experience faster genetic drift
- **Selection Intensity**: Stronger selection pressures drive faster adaptation
- **Environmental Heterogeneity**: Greater environmental variation promotes niche specialization
- **Migration Rates**: Lower migration between populations allows faster divergence

---

## The World

The world is a continuous 2D space that wraps around at the edges (a torus). It contains agents, food pellets, and water sources.

- **Dimensions**: Configurable via settings (default 1000x800 units).
- **Food**: Spawns in clusters. There are a fixed number of cluster centers that drift slowly over time. New food items appear at a steady rate, scattered with a Gaussian distribution around one of the random cluster centers.
- **Water**: The world contains several persistent `WaterSource` entities. These are large circular areas where agents can drink.

### World Boundaries and Physics

**Boundary Types:**
- **Wrap Mode**: Agents exiting one edge reappear on the opposite edge (toroidal topology)
- **Bounce Mode**: Agents reverse direction when hitting boundaries
- **Solid Mode**: Agents cannot cross world boundaries

**Physics System:**
- **Gravity**: Optional gravity effects that pull agents downward
- **Wind Forces**: Environmental wind that affects agent movement
- **Friction**: Movement resistance that slows agents over time
- **Collision Response**: Realistic collision handling between agents and obstacles

### Environmental Systems

**Seasonal Changes:**
- **Resource Availability**: Seasonal fluctuations in food and water availability
- **Climate Variations**: Temperature and weather pattern changes
- **Habitat Shifts**: Seasonal changes in optimal habitats for different agent types

**Weather System:**
- **Precipitation**: Rain events that affect water availability
- **Storms**: Temporary environmental disturbances that affect agent behavior
- **Temperature Fluctuations**: Daily and seasonal temperature changes

**Geographic Variations:**
- **Temperature Zones**: Gradient-based temperature distribution across the world
- **Regional Modifiers**: Local environmental factors that affect agent traits
- **Altitude Effects**: Elevation-based environmental variations
- **Resource Distribution**: Spatial heterogeneity in resource availability

### Agent Ecology

**Diet Types:**
- **Carnivores**: Feed primarily on other agents (higher risk, higher reward)
- **Herbivores**: Feed on plant resources (lower risk, moderate reward)
- **Omnivores**: Flexible diet including both plants and other agents

**Habitat Preferences:**
- **Aquatic**: Prefer water-rich environments, excel in swimming
- **Amphibious**: Balanced performance in water and land environments
- **Terrestrial**: Prefer dry land environments, limited water mobility

**Energy Management:**
- **Metabolic Rate**: Species-specific energy consumption rates
- **Efficiency Factors**: How effectively agents convert resources to energy
- **Storage Capacity**: Maximum energy and hydration storage limits
- **Consumption Strategies**: How agents prioritize different resource types

### Population Dynamics

**Carrying Capacity:**
- **Resource-Based Limits**: Population size constrained by available resources
- **Density-Dependent Effects**: Increasing competition as population grows
- **Allee Effects**: Potential benefits of small populations (rarely modeled)

**Demographics:**
- **Age Structure**: Distribution of ages across the population
- **Sex Ratio**: Proportion of males to females
- **Generation Turnover**: Rate of replacement of older generations

**Extinction Risk:**
- **Small Population Effects**: Increased vulnerability of small populations
- **Environmental Stochasticity**: Random environmental changes affecting survival
- **Genetic Bottlenecks**: Loss of genetic diversity in small populations

---

## Agent Anatomy

The simulation uses a single, unified `Agent` class.

### Core Attributes
- **`pos`**: `Vector2` position in the world.
- **`energy`**: Primary resource, consumed by existing and moving. Replenished by eating. If it drops to 0, the agent dies.
- **`hydration`**: Secondary resource, drains at a constant rate. Replenished by drinking from water sources. If it drops to 0, the agent dies.
- **`age`**: Increases over time. Agents die if they exceed their individual `max_age`.
- **`genome`**: The agent's complete genetic code.
- **`phenotype`**: The expressed traits derived from the genome.
- **`brain`**: The `NeuralBrain` instance, built from the genome.
- **`total_mutations`**: Tracks accumulated mutations for visual identification.

### Phenotype (Expressed Traits)
The `phenotype` is a dictionary of traits computed from the agent's `genome`. Key traits include:
- **`speed`**: Maximum movement speed.
- **`size`**: Affects energy consumption and combat.
- **`aggression`**: A factor influencing combat damage.
- **`vision_range`**: The distance an agent can "see" resources and other agents.
- **`max_age`**: Individual maximum age determined genetically (can vary between agents).

### Advanced Phenotypic Traits

**Morphological Traits:**
- **`agility`**: Determines turning speed and acceleration/deceleration capabilities
- **`armor`**: Provides damage reduction against attacks from other agents
- **`body_mass`**: Influences energy storage capacity and metabolic requirements

**Physiological Traits:**
- **`energy_efficiency`**: How effectively the agent converts resources to energy
- **`hydration_rate`**: Rate of water consumption and recovery
- **`stress_tolerance`**: Resistance to stress accumulation from environmental factors
- **`disease_resistance`**: Ability to resist infections and recover from illness

**Behavioral Traits:**
- **`risk_aversion`**: Tendency to avoid dangerous situations
- **`sociality`**: Preference for grouping with other agents
- **`exploration_drive`**: Motivation to explore new areas of the world
- **`learning_rate`**: Ability to adapt behavior based on experience

**Ecological Traits:**
- **`diet_type`**: Carnivore (0), Omnivore (1), or Herbivore (2)
- **`habitat_preference`**: Aquatic (0), Amphibious (1), or Terrestrial (2)
- **`resource_selectivity`**: How choosy the agent is about food sources
- **`territoriality`**: Tendency to defend territory from other agents

### Agent Behavior Systems

**Decision-Making Process:**
- **Neural Processing**: Sensory inputs processed through neural network to generate behavioral outputs
- **State Integration**: Internal state (energy, hydration, stress) influences decision-making
- **Memory Utilization**: Past experiences influence current decisions when memory is enabled
- **Risk Assessment**: Evaluation of potential rewards versus dangers

**Action Selection:**
- **Movement**: Directed locomotion based on environmental cues and internal drives
- **Feeding**: Resource acquisition based on hunger and nutritional needs
- **Mating**: Reproductive behavior based on readiness and partner availability
- **Combat**: Aggressive or defensive actions based on threat assessment
- **Resting**: Energy conservation when resources are low or stress is high

**Learning and Adaptation:**
- **Experience-Based Learning**: Behavioral adjustments based on consequences of previous actions
- **Social Learning**: Observational learning from other agents' successes/failures
- **Habituation**: Reduced response to repeated stimuli
- **Conditioning**: Association of environmental cues with outcomes

---

## Genetics

The genetic system is based on diploid chromosomes. Each gene has two alleles, and their combined expression (weighted by a dominance value) determines a trait value.

### Genome
- **8 Chromosomes**: The genome consists of 8 pairs of chromosomes.
- **Brain Genes**: Chromosomes 4 through 7 are dedicated to encoding the weights of the neural network:
  - **FNN Mode**: 130 brain genes (96 input-to-hidden + 6 hidden biases + 24 hidden-to-output + 4 output biases)
  - **RNN Mode**: 166 brain genes (adds 36 hidden-to-hidden recurrent weights)
- **Trait Genes**: Chromosomes 0 through 2 encode the agent's physical and behavioral traits (speed, size, max_age, etc.).

### Genetic Architecture

**Chromosome Organization:**
- **Chromosome 0**: Speed, Size, Efficiency, Max Age, Virus Resistance genes
- **Chromosome 1**: Vision, Efficiency, Reproduction, Camouflage genes
- **Chromosome 2**: Aggression, Agility, Armor (morphological traits) genes
- **Chromosome 3**: Color, Disease Resistance, Diet/Habitat preference genes
- **Chromosomes 4-8**: Neural network weights (distributed across 318 total weights for RNN)

**Gene Structure:**
- Each gene has two alleles (allele_a, allele_b) with values and dominance coefficients
- Expression follows dominance-weighted averaging: `expr = val_a * dom_a/(dom_a+dom_b) + val_b * dom_b/(dom_a+dom_b)`
- Dominance coefficients range from 0.0 (completely recessive) to 1.0 (completely dominant)

**Genetic Linkage:**
- Genes on the same chromosome tend to be inherited together
- Crossover during meiosis can separate linked genes
- Linkage groups affect co-evolution of trait combinations

### Reproduction
- Two agents of the opposite sex can reproduce if they are mature, have sufficient energy, and are close to each other.
- Reproduction is driven by the `mate_desire` NN output.
- Offspring are created via crossover and mutation, inheriting a mix of their parents' genomes.

### Meiosis and Crossover

**Gamete Formation:**
- Each parent contributes one allele from each gene pair
- Crossover occurs between homologous chromosomes with probability `CROSSOVER_RATE`
- Crossover points are randomly distributed along chromosomes

**Genetic Recombination:**
- Creates novel allele combinations in offspring
- Increases genetic diversity in population
- Affects linkage disequilibrium between genes

### Mutations
- **Reproductive Mutations**: Occur during reproduction with a relatively high probability. This is the primary driver of evolution.
- **Somatic Mutations**: Occur at a very low rate throughout an agent's life. They directly modify the agent's own genome, causing small changes to its phenotype and brain during its lifetime. These changes can be inherited if the agent reproduces after the mutation occurs.
- **Mutation Tracking**: Accumulated mutations are tracked and visually represented by increased brightness in agent color.

### Mutation Mechanisms

**Types of Mutations:**
- **Point Mutations (70%)**: Small Gaussian shifts to allele values
- **Dominance Mutations (15%)**: Changes to dominance coefficients
- **Allele Swaps (10%)**: Exchange of maternal/paternal alleles
- **Large-Effect Mutations (5%)**: Major shifts in allele values

**Mutation Parameters:**
- `MUTATION_RATE`: Probability per gene per reproduction (default 0.2)
- `LARGE_MUTATION_CHANCE`: Probability of large-effect mutation (default 0.05)
- `POINT_MUTATION_STDDEV`: Standard deviation for small mutations (default 0.3)
- `LARGE_MUTATION_STDDEV`: Standard deviation for large mutations (default 1.5)
- `DOMINANCE_MUTATION_RATE`: Probability of dominance mutation (default 0.15)

**Somatic Mutation Process:**
- Occurs during agent lifetime with configurable rate
- Effects are halved compared to reproductive mutations
- Can be inherited if agent reproduces after mutation
- Creates within-lifetime genetic variation

### Selection and Evolution

**Selection Pressures:**
- **Viability Selection**: Differential survival based on fitness traits
- **Fertility Selection**: Differential reproductive success
- **Sexual Selection**: Mate choice based on phenotypic traits
- **Ecological Selection**: Environmental filtering of phenotypes

**Fitness Components:**
- **Survival Fitness**: Ability to live to reproductive age
- **Reproductive Fitness**: Success in producing viable offspring
- **Competitive Fitness**: Success in resource competition
- **Environmental Fitness**: Adaptation to local conditions

**Evolutionary Dynamics:**
- **Directional Selection**: Favors extreme trait values
- **Stabilizing Selection**: Favors intermediate trait values
- **Disruptive Selection**: Favors multiple trait optima
- **Balancing Selection**: Maintains genetic polymorphism

---

## Neural Network Architecture (V2)

The simulation uses a **V2 architecture** with sector-based sensing and decoupled behavioral drives. Two neural network types are available via the `NN_TYPE` setting:

### Feed-Forward Neural Network (FNN) - Default
A feed-forward neural network with 24 inputs, 8 hidden neurons (tanh), and 6 outputs (tanh). All **254 weights and biases** are encoded in the genome:
- 192 input-to-hidden weights (24 × 8)
- 8 hidden biases
- 48 hidden-to-output weights (8 × 6)
- 6 output biases

### Recurrent Neural Network (RNN)
An RNN extends the FNN architecture by adding recurrent connections between hidden neurons, giving agents short-term memory. All **318 weights and biases** are encoded in the genome:
- 192 input-to-hidden weights (24 × 8)
- 64 hidden-to-hidden recurrent weights (8 × 8)
- 8 hidden biases
- 48 hidden-to-output weights (8 × 6)
- 6 output biases

The RNN hidden state is initialized with small random values (N(0, 0.1)) to prevent immediate saturation, and recurrent weights have a slight identity bias for stability.

### Optional N-Step Memory Extension
When `N_STEP_MEMORY_ENABLED` is true, the last N hidden states are stored and provided as additional inputs, giving FNN agents pseudo-memory and enhancing RNN temporal reasoning.

### Network Architecture Details

**Network Topology:**
- **Input Layer**: 24 nodes processing environmental and internal state information
- **Hidden Layer**: 8 nodes with tanh activation function
- **Output Layer**: 6 nodes controlling behavioral drives
- **Activation Function**: Hyperbolic tangent (tanh) for bounded output range

**Forward Propagation:**
- Input → Hidden: `h_j = tanh(Σ_i w_ij * input_i + bias_j)`
- Hidden → Output: `out_k = tanh(Σ_j w_jk * hidden_j + bias_k)`
- RNN Hidden Update: `h_j(t) = tanh(Σ_i w_ij * input_i + Σ_k w_kj * h_k(t-1) + bias_j)`

**Network Plasticity:**
- **Synaptic Strength**: Connection weights evolve through genetic algorithms
- **Network Architecture**: Fixed topology with evolving weights
- **Functional Specialization**: Different hidden units specialize for different input modalities

### Inputs (24) - Sector-Based Sensing

The V2 architecture uses **sector-based sensing** instead of single-point nearest-entity detection. The agent's vision is divided into 5 angular sectors of 72° each.

| # | Input | Description | Range |
|---|-------|-------------|-------|
| 0-4 | `food_s0-s4` | Food presence signal per sector | 0 to 1 |
| 5-9 | `water_s0-s4` | Water proximity signal per sector | 0 to 1 |
| 10-14 | `agent_s0-s4` | Agent signal per sector (+smaller/-larger) | -1 to 1 |
| 15 | `energy` | Current energy / MAX_ENERGY | 0 to 1 |
| 16 | `hydration` | Current hydration / MAX_HYDRATION | 0 to 1 |
| 17 | `age_ratio` | Current age / genetic max_age | 0 to 1 |
| 18 | `stress` | Internal arousal/stress level | 0 to 1 |
| 19 | `health` | Combined vitality metric | 0 to 1 |
| 20 | `vel_forward` | Velocity in facing direction | -1 to 1 |
| 21 | `vel_lateral` | Velocity perpendicular to facing | -1 to 1 |
| 22 | `own_size` | Own size normalized | 0 to 1 |
| 23 | `own_speed` | Own speed capability normalized | 0 to 1 |

### Outputs (6) - Decoupled Behavioral Drives

| # | Output | Interpretation | Range |
|---|--------|----------------|-------|
| 0 | `move_x` | Desired X movement direction | -1 to 1 |
| 1 | `move_y` | Desired Y movement direction | -1 to 1 |
| 2 | `avoid` | Flee/avoidance tendency | 0 to 1 |
| 3 | `attack` | Attack tendency | 0 to 1 |
| 4 | `mate` | Reproduction seeking | 0 to 1 |
| 5 | `effort` | Energy expenditure level | 0 to 1 |

**Effort System**: Scales movement speed, attack damage, and energy cost. High effort = powerful but costly.

### Neural Processing Principles

**Distributed Representation:**
- Information encoded across multiple hidden units
- Robust to partial damage or noise
- Allows for generalization across similar inputs

**Temporal Integration:**
- RNN maintains internal state across time steps
- N-step memory extends temporal horizon for FNN
- Allows for delayed response to environmental cues

**Modular Processing:**
- Different hidden units may specialize for different input types
- Functional segregation of sensory modalities
- Parallel processing of multiple environmental factors

### Stress System
Agents have internal stress that increases from threats, low resources, and damage, then decays over time. This influences behavior through the neural network.

### Learning and Adaptation

**Genetic Learning:**
- Network weights evolve through selection and mutation
- Population-level adaptation to environmental challenges
- Multi-generational improvement in behavioral strategies

**Phenotypic Plasticity:**
- Somatic mutations allow within-lifetime behavioral changes
- Individual adaptation to changing conditions
- Behavioral flexibility without genetic changes

### RNN Hidden State (RNN Mode Only)
When using RNN mode, each agent maintains a hidden state vector (8 values):
- **Initialization**: Small random values N(0, 0.1) to prevent saturation
- **Identity Bias**: Recurrent weights have slight identity bias for stability
- **Update Rule**: `h(t) = tanh(W_ih × input + W_hh × h(t-1) + bias)`
- **Death Reset**: Offspring start with fresh random hidden state

### Behavioral Emergence

**Complex Behaviors**: The neural network architecture enables the emergence of complex behaviors without hard-coding:
- **Foraging Strategies**: Efficient resource collection based on environmental cues
- **Predator-Prey Dynamics**: Evolving hunting and evasion tactics
- **Social Behaviors**: Grouping, territoriality, and cooperative behaviors
- **Mating Strategies**: Mate selection and courtship behaviors

**Adaptive Responses:**
- **Risk Assessment**: Evaluating threats vs. rewards before acting
- **Energy Management**: Balancing activity with resource conservation
- **Environmental Adaptation**: Adjusting behavior to changing conditions
- **Learning from Experience**: Modifying behavior based on outcomes

### Cognitive Capabilities

**Pattern Recognition:**
- **Environmental Patterns**: Recognizing resource distribution patterns
- **Agent Behaviors**: Identifying predictable behaviors in other agents
- **Temporal Patterns**: Detecting cyclical environmental changes

**Decision Making:**
- **Multi-Criteria Evaluation**: Balancing multiple competing needs
- **Uncertainty Handling**: Making decisions with incomplete information
- **Trade-off Assessment**: Evaluating costs vs. benefits of actions

**Memory and Planning:**
- **Short-term Memory**: Maintained through RNN hidden states
- **Spatial Memory**: Remembering locations of resources and hazards
- **Behavioral Memory**: Learning from past experiences
- **Identity Bias**: Recurrent weights have slight identity bias for stability
- **Update**: `h(t) = tanh(W_ih × input + W_hh × h(t-1) + bias)`
- **Death Reset**: Offspring start with fresh random hidden state

---

## Systems

The simulation logic is organized into several systems that run each tick.

### Core Systems
- **`Movement`**: Computes NN inputs, performs a forward pass through the brain, and updates the agent's position based on the `move_x` and `move_y` outputs.
- **`Combat`**: Resolves attacks. If an agent's `attack_intent > 0.5` and it is near another agent, it deals damage. Damage is influenced by size and the `aggression` trait. On a kill, the attacker gains energy, allowing cannibalism to be a viable (though risky) strategy.
- **`Feeding`**: Allows agents to eat food pellets they are close to.
- **`Hydration`**: Drains hydration over time. If an agent is within a `WaterSource`, it replenishes its hydration.
- **`Energy`**: Applies a metabolic cost each tick based on the agent's size, speed, and efficiency.
- **`Reproduction`**: Manages mating between agents whose `mate_desire > 0.5`.
- **`Aging`**: Increments agent age and handles death from old age. Agents die when they reach the minimum of the global `MAX_AGE` setting and their individual genetic `max_age`.
- **`Somatic Mutation`**: Applies random, small mutations to agent genomes over their lifetime.
- **`Food Clusters`**: Manages the drifting of food cluster spawn points.

---

## Controls

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| **SPACE** | Pause/Resume simulation |
| **UP/DOWN** | Increase/Decrease simulation speed |
| **G** | Toggle Genetics Visualization menu |
| **S** | Toggle Statistics Visualization menu |
| **F11** | Toggle fullscreen mode |
| **ESC** | Return to settings screen |

### Mouse Controls
- **Mouse Wheel**: Scroll through menus (Genetics, Statistics, Settings)
- **Click**: Select agents, interact with UI elements

---

## User Interface

The simulation features a modern, comprehensive settings interface with the following capabilities:

### Full-Screen Support
- Resizable window with F11 toggle for full-screen mode
- Adaptive layout that scales to different screen resolutions

### Settings Screen (Modern Card-Based Design)
- **Card-Based Categories**: Settings are organized into expandable/collapsible category cards with a modern dark theme
- **Two-Column Layout**: Wide screens (>1200px) display categories in two columns for efficient use of space
- **Toggle Switches**: Boolean settings use visual toggle switches instead of checkboxes
- **Clean Numeric Inputs**: +/- buttons with editable text fields for precise value entry
- **Dynamic Array Settings**: Region modifier arrays automatically resize based on NUM_REGIONS_X × NUM_REGIONS_Y
- **Conditional Visibility**: Settings appear only when their parent feature is enabled (e.g., region modifiers only show when Regional Variations is ON)
- **Scrollable Interface**: Smooth scrolling with visual scrollbar indicator
- **Categories Include**: Population, Genetics, Neural Network, Energy, Hydration, Water, Combat, Food Clusters, World, Agents, Reproduction, Species, Initialization, Epidemic, Regions, Temperature, Obstacles, and Rendering

### Neural Network Settings
The Neural Network category includes:
- **NN_TYPE**: Choose between "FNN" (Feed-Forward) or "RNN" (Recurrent). This setting determines the brain architecture for all agents.
  - **FNN**: Standard feed-forward network with 130 weights. Simpler and faster, suitable for reactive behaviors.
  - **RNN**: Recurrent network with 166 weights including temporal feedback. Enables memory-based behaviors and more complex strategies.
- **NN_WEIGHT_INIT_STD**: Standard deviation for initial weight randomization (default 0.5)

### Geographic Variations
The simulation supports two independent types of geographic variations:

**Temperature Zones** (Temperature category):
- Toggle with `TEMPERATURE_ENABLED`
- Configure grid size with `TEMPERATURE_ZONES_X` and `TEMPERATURE_ZONES_Y`
- Creates a smooth temperature gradient across the world (visualized as blue/red overlay)
- Temperature affects agent comfort and behavior

**Regional Modifiers** (Regions category):
- Toggle with `REGIONAL_VARIATIONS_ENABLED`
- Configure grid size with `NUM_REGIONS_X` and `NUM_REGIONS_Y`
- Each region has modifier arrays that scale agent traits:
  - Speed Modifier, Size Modifier, Aggression Modifier, Efficiency Modifier
- Array size automatically matches the number of regions (X × Y)
- Position labels (TL, TR, BL, BR or coordinates) shown in each cell

### HUD (Heads-Up Display) - Adaptive Sidebar
The simulation HUD adapts intelligently to different window sizes:

- **Status Bar**: Shows simulation time and speed/pause state with color-coded indicators
- **Two-Column Layout**: Statistics displayed efficiently in two columns (Agents/Species, Males/Females, Food/Water)
- **Trait Progress Bars**: Visual bars showing average Speed, Size, and Aggression with numeric values
- **Top Species Panel**: Lists top 3 species with colored dots and Italian medieval family names (Visconti, Medici, Este, Sforza, Gonzaga, etc.)
- **Compact Mode**: Automatically activates on smaller screens (<600px height) with reduced spacing and streamlined content
- **Control Hints**: Displays available keyboard shortcuts

### Special Features
- **Random Age Initialization**: Toggle to start agents with random ages between 0 and the maximum age
- **Genetic Lifespan**: Individual agents have genetically determined lifespans that can evolve over generations
- **Visual Mutation Indicators**: More mutated agents appear brighter in color

---

## Special Events

The simulation includes dynamic events that can occur during runtime:

### Epidemic Events
- **Enabled**: Can be toggled on/off via the 'EPIDEMIC_ENABLED' setting in the UI
- **Trigger Conditions**: Occur when population density is high (configurable via 'EPIDEMIC_MIN_POPULATION_RATIO', default 80% of initial population)
- **Effects**: Affects configurable percentage of population (via 'EPIDEMIC_AFFECTED_RATIO', default 30%), with impact modulated by individual virus resistance
- **Virus Resistance**: Agents with higher virus resistance suffer less energy reduction during epidemics
- **Frequency**: Checked every configurable interval (via 'EPIDEMIC_INTERVAL', default 100 seconds) of simulation time
- **Probability**: Base probability when conditions are met is configurable (via 'EPIDEMIC_BASE_PROBABILITY', default 0.001)
- **Visual Indicator**: A red banner appears at the top of the screen with a message about the event

## Genetics Visualization Menu (G Key)

The simulation includes a comprehensive genetics visualization system accessible during runtime:

### Accessing the Menu
- Press the **G** key during simulation to toggle the genetics menu
- The menu appears as a large overlay panel (1450x950 pixels)
- **Note**: Press **G** again to hide the menu

### Features
- **Neural Network Info Panel**: Displays complete NN architecture at the top:
  - FNN: "3-Layer Feed-Forward Network: 16 Input → 6 Hidden (tanh) → 4 Output (tanh)" with 130 weights
  - RNN: "3-Layer Recurrent Network: 16 Input → 6 Hidden (tanh, recurrent) → 4 Output (tanh)" with 166 weights
  - Lists all 16 inputs with descriptions
  - Shows hidden layer details and all 4 outputs
- **Species Overview**: Lists all species with stable ordering (sorted by species ID, not population)
- **Population Summary**: Shows overall population statistics when no agent is selected
- **Agent Detail View**: Shows detailed genetic information when an agent is selected
- **Neural Network Visualization**: Displays a diagram of the neural network architecture
- **Trait Information**: Lists all genetic traits including speed, size, aggression, max_age, virus_resistance, etc.
- **Weight Information**: Shows sample neural network weights for inspection
- **Scrollable Content**: Mouse wheel scrolling for viewing all content

### Neural Network Diagram
- **Structure**: Shows the 16→6→4 architecture visually
- **Connections**: Displays weighted connections between layers with color-coding:
  - Green lines: Positive weights
  - Red lines: Negative weights
  - Orange highlights: Recently mutated weights
  - Line thickness indicates weight magnitude
- **RNN Visualization**: When using RNN, displays additional elements:
  - **Self-loops**: Small circular arcs on each hidden neuron showing self-connections
  - **Inter-neuron connections**: Curved purple/magenta lines between hidden neurons for stronger weights
  - **Recurrent Detail Panel**: A 6×6 matrix visualization in the top-right corner showing:
    - All 36 recurrent connection weights as colored cells
    - Blue/purple cells for positive weights, red/magenta for negative
    - Gray cells for near-zero weights
    - Highlighted diagonal showing self-connections
    - Row/column indices (0-5) for each hidden neuron
    - Color legend (+, -, ~0)
  - Weight summary shows "RNN: 166 weights (36 recurrent, X active)"
- **Neurons**: Color-coded neurons for inputs (green), hidden layer (blue), and outputs (red)
- **Bias Indicators**: Small arrows above neurons showing bias direction

---

## Statistics Visualization Menu (S Key)

The simulation includes a detailed statistics visualization system:

### Accessing the Menu
- Press the **S** key during simulation to toggle the statistics menu
- The menu appears as an overlay panel
- **Note**: Press **S** again to hide the menu

### Features
- **Population Graphs**: Historical tracking of population over time
- **Trait Evolution**: Charts showing how traits evolve across generations
- **Species Distribution**: Breakdown of population by species
- **Behavioral Statistics**: Counts of agents attacking, mating, fleeing
- **Resource Statistics**: Food and water availability tracking
- **Scrollable Interface**: Mouse wheel scrolling for viewing all statistics

## Visualization

The simulation is visualized using Pygame.

### Agent Color
An agent's color indicates its dominant traits:
- **Hue**: Varies from Green (low aggression) to Red (high aggression). This allows for at-a-glance identification of "passive herbivores" vs. "aggressive cannibals".
- **Brightness**: Proportional to the agent's current energy level. Brighter agents are healthier.
- **Mutation Visibility**: Agents with more accumulated mutations appear brighter, making evolutionary changes visually apparent.

### HUD (Side Panel)
The Heads-Up Display is an adaptive side panel showing real-time statistics:

- **Title**: "NEURAL EVOLUTION" with accent styling
- **Status Bar**: Shows simulation time (T: X.Xs) and speed multiplier or PAUSED state
- **Population Section** (two-column layout):
  - Agents count / Species count
  - Males / Females breakdown
  - Food / Water resource counts
- **Average Traits Section**:
  - Visual progress bars for Speed, Size, and Aggression
  - Shows current values and visual fill relative to maximum
- **Generation & Diversity**: Current max generation and genetic diversity metric
- **Top Species Section**: Top 3 species with:
  - Colored indicator dots (using golden angle color distribution)
  - Italian medieval family names (Visconti, Medici, Este, Sforza, Gonzaga, Farnese, etc.)
  - Population breakdown by sex (M: / F:)
- **Controls Section**: Keyboard shortcut hints (SPACE, UP/DOWN, G, S, F11, ESC)
- **Population Graph**: Historical graph of agent population over time

The HUD automatically switches to **compact mode** on smaller screens (<600px height), reducing spacing and optimizing content display.

### Special Event Indicators
- **Banner Notifications**: Red banners appear at the top of the screen when special events occur
- **Event Messages**: Descriptive text indicating what event has occurred and its impact
- **Duration**: Event notifications remain visible for 5 seconds

---

## Enhanced Features: Realistic Obstacles and Rock System

The simulation now features an enhanced obstacle system with realistic rocks and improved environmental features that include advanced visual and behavioral properties.

### Rock Features
- **Rounded Shapes**: Rocks have circular shapes that appear more natural and realistic
- **Color Gradients**: Different rock types display unique color gradients:
  - **Granite**: Light gray with brown tones and distinctive mineral patterns
  - **Limestone**: Light grayish-white with fossil-like patterns
  - **Sandstone**: Warm reddish-brown with layered patterns
  - **Basalt**: Dark gray-blue with crystalline patterns
  - **Generic**: Various shades of gray
- **Internal Mineral Veins**: Each rock displays realistic mineral compositions inside:
  - Quartz, feldspar, biotite, and hornblende patterns in granite
  - Fossil-like patterns in limestone
  - Layered sedimentary patterns in sandstone
  - Crystalline structures in basalt
- **Animated Internal Bounce Effects**: Subtle animated highlights inside rocks simulate light reflecting off internal crystal structures
- **Surface Texture Details**: Realistic surface textures with bumps and indentations
- **3D Appearance**: Shadows and highlights give rocks a three-dimensional appearance

### Obstacle System Improvements
- **Enhanced Obstacle Class**: Added rock-specific properties including rock types, mineral veins, and surface details
- **Improved Collision Detection**: Enhanced collision system that properly handles circular rock obstacles
- **Solid Obstacles**: All obstacles (including rocks) are properly implemented as solid barriers that agents cannot cross
- **Habitat Interaction**: Aquatic agents cannot enter land-based rock obstacles, maintaining realistic habitat preferences

### Visual Enhancement Features
- **Dynamic Rock Rendering**: Advanced rendering system that scales properly with window resizing
- **Animated Highlights**: Subtle animated highlights inside rocks simulate internal light reflection
- **Mineral Pattern Visualization**: Each rock type displays unique internal mineral compositions
- **Surface Texture Mapping**: Surface details enhance the realism of each rock
- **Proper Scaling**: All rock features properly scale with window resizing and zoom levels

### Generation and Control Features
- **Rock Generation Functions**: Added functions to generate individual rocks and rock clusters
- **Settings Integration**: Rocks are integrated with existing obstacle settings (`OBSTACLES_ENABLED`, `NUM_INTERNAL_OBSTACLES`, `ROCK_TYPES_ENABLED`)
- **Keyboard Controls**:
  - **O Key**: Toggle rocks on/off during simulation
  - **C Key**: Clear all obstacles (preserves borders, trees, and rocks based on settings)
- **Environmental Settings**: Adjust rock quantity and types in the "Obstacles" section of environmental settings
- **Individual Placement**: Rocks are randomly placed throughout the world with appropriate spacing
- **Size Variation**: Rocks come in various sizes for natural appearance
- **Type Variation**: When enabled, rocks appear in different geological types with corresponding visual properties

### Technical Implementation Features
- **Robust Attribute Handling**: All obstacle types properly initialize rock-specific attributes to prevent AttributeError
- **Performance Optimization**: Animated effects are limited to prevent performance degradation
- **Backward Compatibility**: Existing obstacle types (trees, borders) continue to function normally
- **Proper Initialization**: Rocks are properly initialized when simulation starts based on settings
- **Memory Management**: Rock-specific data structures are properly managed to prevent memory leaks

### Rock Settings
The rocks are integrated with the existing obstacle settings:
- **`OBSTACLES_ENABLED`**: Toggle to enable/disable rocks (default: False)
- **`NUM_INTERNAL_OBSTACLES`**: Controls the number of rocks generated when enabled (default: 5)
- **`ROCK_TYPES_ENABLED`**: Enable different rock types with unique appearances (default: True)

### Collision Properties
- **Solid Obstacles**: Agents cannot cross through rocks
- **Advanced Collision Detection**: Ensures agents properly navigate around rocks
- **Habitat Interaction**: Maintains realistic habitat preferences for different agent types

### Generation Methods
- **Individual Placement**: Rocks are randomly placed throughout the world with appropriate spacing
- **Size Variation**: Rocks come in various sizes for natural appearance
- **Type Variation**: When enabled, rocks appear in different geological types with corresponding visual properties
- **Cluster Generation**: Option to create rock clusters for more natural formations

The enhanced obstacle system adds significant visual and ecological depth to the simulation while maintaining performance and integration with existing systems.

## Systems and Interactions

### Core Systems

**Movement System:**
- Computes sector-based inputs and runs neural network forward pass
- Updates agent position based on `move_x` and `move_y` outputs
- Incorporates behavioral drives (avoid, attack, mate) into movement decisions
- Applies effort scaling to movement speed

**Combat System:**
- Resolves attacks when `attack_intent > 0.5` and agents are near each other
- Damage influenced by size and aggression traits
- Cannibalism allows energy transfer from killed agents
- Armor trait provides damage reduction

**Feeding System:**
- Agents consume food pellets when in proximity
- Energy replenishment based on food value
- Feeding behavior influenced by hunger state and neural outputs

**Hydration System:**
- Hydration decreases over time at constant rate
- Replenished when agent is within water source boundaries
- Low hydration affects performance and survival

**Energy System:**
- Metabolic cost based on size, speed, and efficiency traits
- Movement and activity increase energy consumption
- Energy depletion leads to death

**Reproduction System:**
- Mating occurs when `mate_desire > 0.5` and compatible partners are nearby
- Offspring inherit genetic traits from both parents
- Reproduction requires sufficient energy and maturity

**Aging System:**
- Age increases over time
- Death occurs at genetic maximum age
- Age affects various physiological and behavioral traits

**Somatic Mutation System:**
- Applies random, small mutations to agent genomes during lifetime
- Mutations can alter phenotype and brain during agent's lifetime
- Mutations may be inherited if agent reproduces after mutation
- Creates within-lifetime genetic variation

### Environmental Interactions

**Resource Competition:**
- Agents compete for limited food and water resources
- Competition intensity varies with population density
- Competitive abilities influenced by speed, aggression, and efficiency

**Habitat Preferences:**
- Aquatic agents excel in water environments
- Terrestrial agents perform better on land
- Amphibious agents have balanced performance in both environments
- Habitat mismatch incurs performance penalties

**Obstacle Navigation:**
- Agents must navigate around static obstacles (walls, rocks, trees)
- Dynamic pathfinding based on neural network outputs
- Collision avoidance behaviors emerge from neural processing

### Population Dynamics

**Density-Dependent Effects:**
- High population density increases competition
- Resource scarcity affects survival and reproduction
- Carrying capacity limits maximum sustainable population

**Age Structure:**
- Populations have varying age distributions
- Different age classes have different survival and reproductive rates
- Senescence affects older individuals' performance

**Sex Ratios:**
- Male and female ratios affect mating dynamics
- Sexual selection pressures vary with sex ratio
- Reproductive success depends on mate availability

### Evolutionary Mechanisms

**Natural Selection:**
- Differential survival based on trait values
- Fitness correlates with survival and reproductive success
- Environmental pressures shape trait distributions

**Genetic Drift:**
- Random changes in allele frequencies
- More pronounced in small populations
- Contributes to genetic diversity loss over time

**Gene Flow:**
- Movement of genes between populations
- Maintains genetic diversity
- Counteracts divergence between populations

**Co-evolution:**
- Interacting species evolve together
- Predator-prey arms races
- Mutualistic relationships

### Evolutionary Divergence Triggers

**When Evolutionary Divergence Happens:**
- **Selection Pressures**: Different environments favor different traits, leading to adaptive divergence
- **Genetic Drift**: Random changes in allele frequencies, especially pronounced in small populations
- **Mutation Accumulation**: New mutations create genetic differences between populations over time
- **Geographic Isolation**: Physical barriers (mountains, rivers, etc.) prevent gene flow between populations
- **Reproductive Isolation**: Behavioral or genetic changes that prevent successful interbreeding

---

## Enhanced RNN Memory System {#enhanced-rnn-memory-system}

The RNN memory system is a critical component that enables agents to exhibit temporal reasoning and memory-based behaviors. The system operates through recurrent connections that maintain state across time steps.

#### Mathematical Foundation of RNN Memory

The RNN's memory capability stems from its recurrent connections, which create a dynamic system that can maintain information about past states:

$$ \mathbf{h}^{(t)} = f(\mathbf{W}_{ih}\mathbf{x}^{(t)} + \mathbf{W}_{hh}\mathbf{h}^{(t-1)} + \mathbf{b}_h) $$

Where:
- $ \mathbf{h}^{(t)} $ is the hidden state vector at time $ t $
- $ \mathbf{x}^{(t)} $ is the input vector at time $ t $
- $ \mathbf{W}_{ih} $ is the input-to-hidden weight matrix (24×8)
- $ \mathbf{W}_{hh} $ is the hidden-to-hidden (recurrent) weight matrix (8×8)
- $ \mathbf{b}_h $ is the hidden bias vector
- $ f $ is the activation function (tanh)

The recurrent weight matrix $ \mathbf{W}_{hh} $ is what enables memory. Each element $ W_{hh,ij} $ determines how the activation of hidden unit $ j $ at time $ t-1 $ influences the activation of hidden unit $ i $ at time $ t $.

#### Memory Persistence and Decay

The memory in the RNN system exhibits both persistence and decay characteristics:

$$ \lim_{t \to \infty} \mathbf{h}^{(t)} = \lim_{t \to \infty} f\left(\sum_{\tau=0}^{t} \mathbf{W}_{hh}^{t-\tau} \mathbf{W}_{ih}\mathbf{x}^{(\tau)} + \text{bias terms}\right) $$

This equation shows that the current hidden state is influenced by all previous inputs, weighted by powers of the recurrent weight matrix. The eigenvalues of $ \mathbf{W}_{hh} $ determine how quickly information from the past fades.

#### Information Retention Analysis

The information retention in the RNN can be quantified by the spectral radius of the recurrent weight matrix:

$$ \rho(\mathbf{W}_{hh}) = \max_i |\lambda_i| $$

Where $ \lambda_i $ are the eigenvalues of $ \mathbf{W}_{hh} $. When $ \rho(\mathbf{W}_{hh}) < 1 $, the network exhibits exponential forgetting, while when $ \rho(\mathbf{W}_{hh}) > 1 $, it may become unstable. The ideal range for memory retention is when $ \rho(\mathbf{W}_{hh}) \approx 1 $.

The memory capacity can be estimated by the number of time steps over which information remains accessible:

$$ T_{memory} \approx \frac{1}{|\log(\rho(\mathbf{W}_{hh}))|} $$

This represents the approximate number of time steps after which the influence of a past input has decayed to $ 1/e \approx 0.37 $ of its original value.

#### Initialization Strategy for Stable Memory

To ensure stable memory formation, the RNN uses a specific initialization strategy:

$$ W_{hh,ij} = \begin{cases}
\alpha + \mathcal{N}(0, \sigma^2) & \text{if } i = j \\
\mathcal{N}(0, \sigma^2) & \text{if } i \neq j
\end{cases} $$

Where:
- $ \alpha $ is the identity bias (typically 0.1) that promotes stability
- $ \mathcal{N}(0, \sigma^2) $ is Gaussian noise with mean 0 and variance $ \sigma^2 $

This initialization biases the recurrent connections toward identity mapping, which helps preserve information across time steps while allowing for learning of more complex temporal patterns.

#### Memory Gradient Flow

The gradient flow through time in the RNN is governed by the chain rule:

$$ \frac{\partial L}{\partial h_j^{(t-k)}} = \sum_{i=1}^{8} \frac{\partial L}{\partial h_i^{(t-k+1)}} \cdot \frac{\partial h_i^{(t-k+1)}}{\partial h_j^{(t-k)}} $$

Where:
$$ \frac{\partial h_i^{(t-k+1)}}{\partial h_j^{(t-k)}} = W_{ji}^{(hh)} \cdot f'(net_i^{(t-k+1)}) $$

This recursive relationship shows how gradients propagate backward through time, with the magnitude of gradients potentially vanishing or exploding depending on the eigenvalues of $ \mathbf{W}_{hh} $.

#### Optional Stochastic Noise for Exploration

The RNN can include optional stochastic noise to promote exploration:

$$ h_j^{(t)} = \tanh\left(\sum_{i=1}^{24} W_{ij}^{(input-hidden)} \cdot x_i^{(t)} + \sum_{k=1}^{8} W_{kj}^{(hidden-hidden)} \cdot h_k^{(t-1)} + b_j^{(hidden)} + \eta_j^{(t)}\right) $$

Where $ \eta_j^{(t)} \sim \mathcal{N}(0, \sigma_{noise}^2) $ is the noise term added to hidden unit $ j $ at time $ t $.

### N-Step Memory Extension

When enabled, the system stores past hidden states and provides them as additional inputs to the neural network, giving FNN agents pseudo-memory and enhancing RNN temporal reasoning capabilities. The depth is configurable (typically 1-2 steps) and the system maintains a circular buffer of past hidden states. This allows agents to make decisions based on recent history, enabling more sophisticated temporal strategies.

#### Mathematical Representation of N-Step Memory

When N-step memory is enabled, the input vector is augmented with historical hidden states:

$$ \mathbf{x}_{augmented}^{(t)} = [\mathbf{x}^{(t)}, \mathbf{h}^{(t-1)}, \mathbf{h}^{(t-2)}, ..., \mathbf{h}^{(t-n)}] $$

Where:
- $ \mathbf{x}^{(t)} $ is the original 24-dimensional input vector
- $ \mathbf{h}^{(t-i)} $ is the hidden state from $ i $ time steps ago
- $ n $ is the memory depth (typically 1-2)

This augmented input vector has dimension $ 24 + n \times 8 $, which is then processed by the neural network as usual.

#### Memory Buffer Implementation

The memory buffer operates as a circular queue with the following mathematical operations:

$$ \text{buffer}[t \bmod n] = \mathbf{h}^{(t)} $$

Where:
- $ n $ is the memory depth
- $ \mathbf{h}^{(t)} $ is the current hidden state vector
- $ \bmod $ is the modulo operator

The flattened memory vector is constructed as:

$$ \mathbf{m}^{(t)} = [\mathbf{h}^{(t-1)}, \mathbf{h}^{(t-2)}, ..., \mathbf{h}^{(t-n)}] $$

Where each $ \mathbf{h}^{(t-i)} $ is an 8-dimensional vector, resulting in a total of $ 8n $ additional input dimensions.

#### Memory Decay and Forgetting

The effective memory retention in the N-step memory system follows an exponential decay pattern:

$$ R(t) = e^{-\lambda t} $$

Where:
- $ R(t) $ is the retention of information after $ t $ time steps
- $ \lambda $ is the decay constant
- $ t $ is the number of time steps since the information was stored

For the N-step memory system, information beyond $ n $ time steps is completely forgotten, so the effective retention function becomes:

$$ R_{effective}(t) = \begin{cases}
e^{-\lambda t} & \text{if } t \leq n \\
0 & \text{if } t > n
\end{cases} $$

### Stress System

Agents maintain an internal stress level that influences their behavior and neural network inputs:
- **Gain Sources**: Nearby threats, low resources, recent damage
- **Decay**: Natural decay over time with configurable rate
- **Effects**: Influences decision-making, energy consumption, and behavioral thresholds
- **Computation**: Stress increases based on threat level, resource stress, and recent damage, then decays naturally

Mathematical representation of stress dynamics:

$$ \frac{dS}{dt} = G(t) - D \cdot S(t) $$

Where:
- $ S(t) $ is the stress level at time $ t $
- $ G(t) $ is the stress gain function at time $ t $
- $ D $ is the decay rate constant

Discretized version:
$$ S^{(t+1)} = S^{(t)} + (G^{(t)} \cdot \Delta t - D \cdot S^{(t)} \cdot \Delta t) $$

---

## Chapter 4: Genetic System {#genetic-system}

### Genome Structure

The genome consists of 8 pairs of diploid chromosomes with sophisticated organization and realistic inheritance patterns:

**Chromosome Organization**:
- **Chromosomes 0-2**: Physical and behavioral traits (speed, size, aggression, etc.)
- **Chromosome 3**: Additional trait genes and regulatory elements
- **Chromosomes 4-7**: Neural network weights (130 genes for FNN, 166 for RNN)
- **Chromosome 7**: Additional genetic information and regulatory elements

**Brain Genes**: Chromosomes 4-7 encode neural network weights with different organizations for FNN vs RNN architectures:
  - **FNN Mode**: 130 brain genes (96 input-to-hidden weights, 6 hidden biases, 24 hidden-to-output weights, 4 output biases)
  - **RNN Mode**: 166 brain genes (same as FNN plus 36 hidden-to-hidden recurrent weights)

**Trait Genes**: Chromosomes 0-2 encode physical and behavioral traits including speed, size, aggression, vision range, energy efficiency, reproduction urge, camouflage, and max age. Each trait is controlled by multiple genes for polygenic inheritance, creating realistic continuous variation.

**Gene Structure**: Each gene consists of two alleles (one from each parent) that determine trait expression through dominance relationships. The system implements complex dominance effects where one allele may partially or completely mask the expression of the other, creating realistic inheritance patterns.

**Allele Pairing**: Each gene has two alleles that form pairs, with dominance relationships determining how the paired alleles express in the phenotype. Dominance effects can be complete, incomplete, or codominant, creating complex inheritance patterns.

### Reproduction Process

**Mate Selection**: Agents must be mature, have sufficient energy, be hydrated, and be within mating distance. Mate selection is driven by the mate_desire neural network output, which is influenced by the agent's current state and genetic traits.

**Crossover**: During reproduction, chromosomes undergo crossover with configurable probability, mixing parental genetic material. The crossover rate determines how often genetic material is exchanged between parental chromosomes during meiosis.

**Mutation**: Offspring genomes undergo mutation with configurable rates, introducing genetic diversity. Both point mutations and larger mutations are possible, with different effects on fitness and behavior.

**Inheritance**: Offspring inherit mixed parental genomes with proper chromosome segregation and gene expression. The inheritance system maintains genetic diversity while preserving beneficial traits.

### Somatic Mutations

Agents can undergo lifetime mutations at a configurable rate. These mutations occur randomly throughout the agent's life and can affect any aspect of the genome, including neural network weights and physical traits. Somatic mutations can be inherited if the agent reproduces after the mutation occurs, allowing for rapid adaptation within an individual's lifetime that can be passed to offspring.

---

## Chapter 5: Simulation Systems {#simulation-systems}

### Movement System

The movement system is the most complex behavioral system, implementing sophisticated decision-making and physics:

**Sector-Based Input Computation**: Divides the agent's vision into 5 angular sectors of 72° each, computing food, water, and agent signals for each sector. This provides spatial awareness without perfect point-location knowledge, making the agents' decision-making more realistic and challenging.

**Neural Network Forward Pass**: Each frame, the system performs a forward pass through the agent's neural network brain, processing the 24 inputs (or more with memory) and producing 6 outputs that control movement and behavior. The system handles both FNN and RNN architectures appropriately.

**Position Update**: Calculates movement based on neural outputs, applying steering behaviors and physics. The system implements momentum, friction, and realistic movement dynamics.

**Behavioral Drive Application**: Interprets neural outputs as behavioral drives (avoid, approach, attack, mate) and applies them to modify the agent's movement and decision-making. For example, a high avoid drive might cause the agent to flee from threats while a high approach drive might lead it toward resources.

**Collision Handling**: Sophisticated collision detection and resolution prevents agents from passing through obstacles or terrain features. When collisions occur, the system calculates appropriate response vectors to push agents away from obstacles while preserving momentum where possible.

**Steering Behaviors**: Implements various steering behaviors like seeking, fleeing, wandering, and obstacle avoidance to create natural-looking movement patterns that respond intelligently to the environment.

**Velocity Limiting**: Ensures agents don't exceed their maximum speed capabilities based on their genetic traits and current effort level.

**Boundary Handling**: Manages world boundaries and wrapping behavior, allowing agents to move seamlessly across the world edges in torus mode or bounce off walls in bounded mode.

**Region Updates**: Updates the agent's geographic region information based on position and world settings, which affects regional trait modifiers.

### Combat System

The combat system implements sophisticated aggressive interactions with multiple factors:

**Attack Resolution**: When agents are within ATTACK_DISTANCE and have a high attack drive, the system resolves combat encounters. Damage is calculated based on the attacking agent's size, aggression trait, effort level, and other factors, as well as the defending agent's armor and other defensive traits.

**Damage Calculation**: Implements sophisticated damage calculation that considers multiple factors including size differential, aggression levels, effort investment, armor protection, and random variation. Larger, more aggressive agents deal more damage, but armored agents take less.

**Cannibalism Implementation**: Allows successful attackers to gain energy from kills, creating a viable but risky survival strategy. The KILL_ENERGY_GAIN setting determines how much energy is transferred from the killed agent to the killer.

**Attack Intent Processing**: Processes the attack intent from neural outputs and translates it into actual combat behavior, considering factors like target proximity, threat assessment, and energy costs.

**Proximity Detection**: Detects when agents are close enough to engage in combat, using efficient spatial queries to minimize computational overhead.

**Damage Application**: Applies calculated damage to attacked agents, tracking health status and determining when agents die from combat.

**Kill Handling**: Manages the consequences of successful kills, including energy transfer, removal of the killed agent from the simulation, and updating statistics.

**Combat Cooldowns**: Implements cooldown periods after combat to prevent continuous fighting and allow agents to recover.

### Feeding System

The feeding system manages all aspects of food consumption with realistic foraging dynamics:

**Food Consumption**: Allows agents to eat nearby food items when they come within eating distance. The system efficiently detects food in the agent's vicinity using spatial queries and handles consumption priority.

**Energy Restoration**: Restores energy based on the food's energy value and the agent's digestive efficiency. The amount of energy gained may be modified by the agent's traits and current state.

**Proximity Detection**: Detects food items within EATING_DISTANCE of agents, using efficient spatial queries to minimize computational overhead.

**Consumption Priority**: Implements consumption priority systems that determine which food items agents should target when multiple options are available.

**Food Competition**: Handles competition for food resources when multiple agents attempt to consume the same food item simultaneously.

**Foraging Behavior**: Implements sophisticated foraging behaviors that guide agents toward food sources based on their current energy levels and other factors.

### Hydration System

The hydration system manages water consumption and fluid balance with realistic physiological modeling:

**Hydration Drain**: Implements continuous drainage of hydration over time at a rate determined by HYDRATION_DRAIN_RATE. The drainage rate may be modified by agent traits like size and activity level.

**Drinking Behavior**: Allows agents to drink from water sources when they are within drinking range. The system efficiently detects water sources in the agent's vicinity.

**Hydration Restoration**: Restores hydration based on the DRINK_RATE and the agent's drinking efficiency. The rate of hydration gain may be affected by the agent's current state and traits.

**Water Proximity Detection**: Detects water sources within drinking range of agents using efficient spatial queries.

**Thirst Modeling**: Models thirst levels that drive agents to seek water when hydration is low. Thirst may become a priority when hydration falls below critical thresholds.

### Energy System

The energy system implements realistic metabolic processes with multiple factors affecting consumption:

**Metabolic Costs**: Applies metabolic costs based on agent traits like size, speed, and efficiency. Larger agents have higher baseline metabolic costs, while more efficient agents have lower costs.

**Energy Drain**: Implements continuous energy drain based on BASE_ENERGY_DRAIN and various activity multipliers. The drain rate may be affected by agent traits, current activity, and environmental conditions.

**Size-based Costs**: Implements metabolic scaling where larger agents pay proportionally higher energy costs. This creates a trade-off between size advantages and energy demands.

**Speed-based Costs**: Implements energy costs that scale with movement speed, making faster agents consume more energy during locomotion.

**Efficiency Factors**: Applies efficiency factors that can reduce or increase energy costs based on genetic traits and current state.

**Activity-based Costs**: Implements different energy costs for different activities like movement, combat, reproduction, and other behaviors.

### Reproduction System

The reproduction system manages all aspects of genetic inheritance and offspring creation:

**Mating Eligibility**: Determines when agents are eligible to mate based on maturity age, energy levels, hydration, and reproduction cooldown status. Agents must meet multiple criteria before they can reproduce.

**Mate Seeking**: Implements mate-seeking behaviors that guide agents toward potential partners. The system uses spatial queries to locate nearby potential mates.

**Mate Selection**: Implements mate selection criteria that may consider factors like genetic compatibility, trait quality, and availability.

**Reproduction Costs**: Implements energy costs associated with reproduction that agents must pay to successfully reproduce. The cost is determined by REPRODUCTION_COST.

**Maturity Requirements**: Implements maturity requirements that prevent young agents from reproducing until they reach MATURITY_AGE.

**Cooldown Periods**: Implements reproduction cooldowns that prevent agents from reproducing continuously. The cooldown period is determined by REPRODUCTION_COOLDOWN.

**Genetic Inheritance**: Handles the inheritance of genetic material from parents to offspring, including proper chromosome pairing and trait expression.

**Crossover Implementation**: Implements genetic crossover during meiosis that combines parental genetic material to create offspring genomes.

**Mutation Introduction**: Introduces mutations during reproduction with configurable rates, allowing for genetic diversity in offspring.

**Offspring Creation**: Creates new offspring agents with mixed genomes from their parents, properly initializing all attributes and traits.

### Aging System

The aging system implements realistic life-history dynamics with multiple age-related effects:

**Age Increment**: Continuously increments agent age over time based on simulation time passage. The aging rate may be affected by various factors.

**Death from Old Age**: Agents die when their age exceeds their genetically-determined maximum age. This creates natural mortality and population turnover.

**Individual Max Age**: Uses individual genetic max_age values that can vary between agents, creating diversity in lifespan within the population.

**Aging Effects**: Implements various aging effects on agent abilities, including reduced speed, decreased efficiency, and other age-related declines.

**Life Stages**: Implements different life stages (young, prime, old) that affect agent capabilities and behaviors differently.

### Somatic Mutation System

The somatic mutation system implements lifetime genetic changes with inheritance possibilities:

**Lifetime Mutations**: Applies mutations during agent lifetime at the rate determined by SOMATIC_MUTATION_RATE. These mutations occur randomly throughout the agent's life.

**Mutation Tracking**: Tracks accumulated mutations for visualization purposes, with more mutated agents appearing brighter in color.

**Mutation Effects**: Applies various effects of mutations, which can affect any aspect of the agent's genome, including neural network weights, physical traits, and behavioral tendencies.

### Disease Transmission System

The disease system models pathogen spread and effects with realistic epidemiological modeling:

**Transmission Modeling**: Models disease transmission between agents based on proximity and transmission probability. The system considers factors like agent health, immunity, and environmental conditions.

**Transmission Distance**: Implements distance-based transmission where diseases spread between agents within DISEASE_TRANSMISSION_DISTANCE of each other.

**Transmission Probability**: Implements probabilistic transmission that determines the likelihood of disease spread when agents are in proximity.

**Resistance Modeling**: Models genetic resistance to diseases that varies between agents based on their genetic makeup.

**Infection Tracking**: Tracks infection status of agents, monitoring which agents are infected, which diseases they carry, and the progression of infections.

**Recovery Modeling**: Models recovery from diseases with recovery rates that may vary by disease type and agent traits.

**Disease Effects**: Implements various effects of diseases on agent behavior and physiology, including reduced performance, altered behavior, and potential death.

### Events System

The events system manages special population-wide phenomena with complex triggering conditions:

**Special Event Management**: Manages special events like epidemics, resource booms, environmental changes, and other population-wide phenomena.

**Event Triggering**: Triggers events based on various conditions including population density, resource availability, time elapsed, and random probability.

**Event Effects**: Applies effects of events to agents, which may include temporary changes to behavior, physiology, or environmental conditions.

**Epidemic Management**: Manages epidemic events with special rules for disease spread, population impact, and recovery.

**Population Thresholds**: Uses population thresholds for triggering certain events, such as epidemics that require sufficient population density.

---

## Chapter 6: Environment and Entities {#environment-and-entities}

### World Structure

The world implements a sophisticated 2D environment with multiple layers of complexity:

**Spatial Grids**: Implements spatial partitioning grids to efficiently manage collision detection and neighbor queries. Instead of checking every agent against every other agent (O(n²)), the world is divided into grid cells, and agents only check for neighbors within their cell and adjacent cells (O(n)). This dramatically improves performance as the population grows.

**Boundaries**: The world can operate as a torus (wraps around at edges) or as a bounded environment with walls. Torus mode creates a continuous world where agents can travel infinitely in any direction, while bounded mode creates a finite world with defined edges.

**Dynamic Elements**: The world contains multiple dynamic elements: food clusters that drift slowly over time according to seasonal patterns, multiple water sources distributed throughout the world, and configurable terrain obstacles like mountains, rivers, and lakes.

**Environmental Complexity**: The environment includes realistic features like temperature zones, geographic regions with different trait modifiers, and seasonal resource patterns that create complex selective pressures.

### Agent Properties

The agent class implements a comprehensive individual with multiple interacting systems:

**Position and Movement**: Each agent has a Vector2 position in the world and a velocity vector that determines its movement direction and speed. The position is updated each frame based on the neural network's movement outputs and physics calculations. The velocity is subject to steering behaviors, collision responses, and momentum effects.

**Energy System**: The primary resource consumed by existing and moving. Energy drains continuously based on metabolic costs that scale with the agent's size, speed, and activity level. If energy drops to 0, the agent dies. Energy can be replenished by consuming food, with the amount gained determined by the food's energy value and the agent's efficiency traits.

**Hydration System**: The secondary resource that drains at a constant rate. If hydration drops to 0, the agent dies. Hydration can be replenished by drinking from water sources. The rate of hydration gain depends on the agent's drinking efficiency and the proximity to water.

**Age Tracking**: Increases over time and is subject to genetic maximum age limits. When age exceeds the individual's genetically-determined max_age, the agent dies. Age affects various aspects of the agent's behavior and physiology, with younger agents typically being more energetic and older agents potentially having accumulated wisdom or experience.

**Genome Structure**: The agent's complete genetic code consisting of 8 pairs of diploid chromosomes. Each chromosome contains multiple genes, and each gene has two alleles that determine trait expression.

**Phenotype Expression**: The expressed traits derived from the genome through a complex expression system that considers dominance effects, environmental factors, and developmental processes. The phenotype includes all measurable traits like speed, size, aggression, vision range, energy efficiency, reproduction urge, camouflage, and max age.

**Neural Brain**: The `NeuralBrain` instance built from the genome, which can be either a Feed-Forward Neural Network (FNN) or a Recurrent Neural Network (RNN) depending on settings. The brain processes inputs from the environment and internal state to produce behavioral outputs.

**Mutation Tracking**: Tracks accumulated mutations for visualization purposes, with more mutated agents appearing brighter in color. This provides a visual indication of genetic diversity and evolutionary activity in the population.

**Visual Diversity**: Each agent has a unique appearance based on its species and genetic makeup, with different shapes representing different species (circle, square, triangle, parallelogram, diamond, hexagon, pentagon, star). The color indicates traits like aggression (green to red gradient) and energy level (brightness), while the shape represents species membership.

### Environmental Features

The simulation includes sophisticated environmental features that create realistic ecological dynamics:

**Food System**: Spawns in drifting clusters that simulate changing seasons or resource patches. Each food item provides energy when consumed, and the system implements realistic foraging dynamics where agents must locate and compete for resources.

**Water Sources**: Fixed locations where agents can drink to restore hydration. Multiple sources create focal points for agent activity and influence spatial distribution patterns.

**Obstacles**: Terrain features including mountains, rivers, and walls that agents cannot pass through. These create environmental complexity and challenge navigation, forcing agents to develop spatial awareness and pathfinding abilities.

**Terrain Generation**: Sophisticated terrain generator creates realistic features like mountain chains, meandering rivers, and irregular lakes with configurable parameters. The generator uses realistic topographical principles to create natural-looking terrain.

---

## Chapter 7: Advanced Features {#advanced-features}

### Body Size Effects

When enabled, body size creates meaningful trade-offs that affect multiple aspects of agent behavior and physiology:

**Attack Strength**: Scales with size^SIZE_ATTACK_SCALING, making larger agents more effective in combat but creating metabolic costs.

**Speed Penalty**: Larger agents move slower due to increased mass and energy requirements, creating a trade-off between size advantages and mobility.

**Turn Penalty**: Larger agents turn more slowly due to increased moment of inertia, affecting maneuverability in combat and navigation.

**Metabolic Cost**: Scales superlinearly with size^SIZE_METABOLIC_SCALING, making larger agents pay disproportionately higher energy costs.

**Perception Bonus**: Slightly better perception range for larger agents, providing some advantages for size.

### Age-Dependent Modulation

Implements realistic life-history stages with different capabilities and strategies:

**Young Stage (0-20%)**: Lower speed/stamina but potential for rapid learning and adaptation. Young agents may be more exploratory and less risk-averse.

**Prime Stage (20-60%)**: Peak performance in all areas with optimal balance of physical capabilities and accumulated experience.

**Old Stage (60-100%)**: Reduced physical capabilities but potential wisdom benefits from accumulated experience and knowledge.

### Internal State Modulation

Implements soft penalties based on resource levels that create realistic behavioral responses:

**Low Energy**: Reduced attack effectiveness and effort capacity when energy is critically low, forcing agents to prioritize feeding.

**Low Hydration**: Reduced speed and performance when dehydrated, creating urgency for water access.

**High Stress**: Potential short-term effort boost (fight-or-flight) that can provide temporary advantages during crises.

### Action-Specific Cost Asymmetry

Implements differentiated energy costs for different activities that create realistic behavioral economics:

**High Speed**: 1.5x multiplier for maximum speed movement, making sustained high-speed travel costly.

**Sharp Turns**: 1.3x multiplier for sudden direction changes, encouraging smoother movement patterns.

**Sustained Pursuit**: 1.2x multiplier for prolonged chasing, making extended hunting costly.

**Combat**: Higher base costs for attacking, creating risk-reward calculations for aggressive behaviors.

**Reproduction**: Significant energy investment that requires careful resource management.

### Morphological Trade-offs

Introduces agility and armor traits that create sophisticated trade-offs:

**Agility**: Improves turning/acceleration but increases metabolic cost, creating a trade-off between mobility and efficiency.

**Armor**: Reduces damage but penalizes speed and increases energy cost, creating a trade-off between protection and mobility.

### Sensory Imperfection

Adds realistic perception limitations that make decision-making more challenging:

**Sensor Noise**: Gaussian noise on inputs that creates uncertainty in environmental perception.

**Sensor Dropout**: Chance of missing signals that creates occasional perceptual failures.

**Internal State Noise**: Noise on energy/hydration perception that affects decision-making accuracy.

### Context Signals

Provides additional neural network inputs tracking time since key events:

**Time Since Food**: Tracks time since last food consumption, potentially affecting hunger motivation.

**Time Since Damage**: Tracks time since last damage received, potentially affecting caution levels.

**Time Since Mating**: Tracks time since last reproduction, potentially affecting mate-seeking behavior.

### Social Pressure Effects

Models crowding and dominance effects that create realistic social dynamics:

**Crowding Stress**: Increases stress in dense areas, potentially affecting behavior and decision-making.

**Dominance Stress**: Stress from larger/aggressive neighbors, creating realistic social hierarchies.

**Social Dynamics**: Emergent social behaviors based on population density and individual characteristics.

---

## Chapter 8: User Interface and Controls {#user-interface-and-controls}

### Keyboard Controls

The simulation provides comprehensive keyboard controls for interaction and management:

| Key | Function |
|-----|----------|
| SPACE | Pause/Resume simulation - Toggles simulation execution |
| UP/DOWN | Increase/Decrease simulation speed - Adjusts simulation speed multiplier (0.25x to 8x) |
| G | Toggle Genetics Visualization menu - Shows detailed neural network and genetic information |
| S | Toggle Statistics Visualization menu - Shows population and trait evolution charts |
| F11 | Toggle fullscreen mode - Switches between windowed and fullscreen display |
| ESC | Return to settings screen - Exits simulation to main settings interface |
| H | Toggle HUD sidebar - Shows/hides heads-up display with statistics |
| O | Toggle obstacles on/off - Enables/disables terrain obstacles |
| B | Toggle border on/off - Enables/disables border walls |
| M | Add horizontal mountain chain - Creates realistic mountain chain across world |
| N | Add vertical mountain chain - Creates realistic mountain chain up/down world |
| R | Add vertical meandering river - Creates meandering river from top to bottom |
| T | Add horizontal meandering river - Creates meandering river from left to right |
| L | Add lake - Creates irregular lake shape |
| D | Add diagonal mountain range - Creates mountain range from corner to corner |
| C | Clear all obstacles (except borders) - Removes all generated obstacles |

### Settings Interface

The settings interface provides comprehensive configuration with intuitive organization:

**Card-Based Design**: Settings are organized into expandable/collapsible category cards with intuitive grouping by function (Population, Genetics, Neural Network, Energy, etc.). Each card contains related parameters that logically belong together.

**Two-Column Layout**: Efficient use of screen space with two-column layout on wide screens, maximizing the number of visible settings while maintaining readability.

**Interactive Controls**: Toggle switches for boolean settings, numeric inputs with +/- buttons, and editable fields for precise value adjustment. All controls provide immediate visual feedback.

**Conditional Visibility**: Settings only appear when their parent feature is enabled, reducing interface clutter and improving usability. For example, RNN-specific settings only appear when RNN mode is selected.

**Real-Time Updates**: Changes take effect immediately without requiring restart, allowing for experimentation with different parameter combinations.

**Category Organization**: Settings are grouped into logical categories:
- Population: Initial agents, food limits, spawn rates
- Genetics: Mutation rates, crossover rates, somatic mutations
- Neural Network: Architecture type, hidden size, weight initialization
- N-Step Memory: Memory depth and enable/disable
- Sensing: Sector count, vision noise
- Internal State: Stress parameters, health metrics
- Effort System: Effort scaling parameters
- Energy: Energy-related parameters
- Hydration: Hydration-related parameters
- Water: Water source parameters
- Combat: Attack-related parameters
- Food Clusters: Food cluster parameters
- World: World size and display parameters
- Agents: Agent-specific parameters
- Aging: Age-related parameters
- Reproduction: Reproduction parameters
- Other: Miscellaneous parameters
- Temperature Zones: Environmental temperature settings
- Initialization: Startup configuration
- Epidemic: Disease outbreak parameters
- Species: Species-related parameters
- Disease: Disease transmission parameters
- Geographic Variations: Regional trait modifiers
- Obstacles: Terrain obstacle parameters
- Rendering: Display parameters
- Trait Ranges: Valid ranges for genetic traits
- Trait Defaults: Default values for traits
- Advanced Features: Optional complex behaviors

### Visualization Systems

The simulation includes multiple sophisticated visualization systems:

**Genetics Visualization**: Detailed neural network architecture visualization showing connections and weights, species overview with population statistics, and agent detail views with genetic information. The system provides insight into how neural networks and genetics influence behavior.

**Statistics Visualization**: Historical tracking of population over time, trait evolution charts showing how genetic traits change across generations, species distribution breakdown, behavioral statistics tracking, and resource availability trends. The system provides quantitative insights into evolutionary and ecological dynamics.

**HUD Display**: Real-time statistics including population counts, species diversity, resource availability, average trait values (speed, size, aggression), top species with color-coded indicators, simulation time and speed, and keyboard shortcut hints. The HUD provides immediate feedback on simulation state.

---

## Chapter 9: Configuration Parameters {#configuration-parameters}

### Population Settings
- `INITIAL_AGENTS`: Starting number of agents in the simulation (default 150)
- `MAX_FOOD`: Maximum number of food items allowed in the world (default 400)
- `FOOD_SPAWN_RATE`: Rate at which new food items are created per second (default 30)

### Genetics Settings
- `MUTATION_RATE`: Probability of mutation per gene during reproduction (default 0.2)
- `CROSSOVER_RATE`: Probability of crossover per chromosome during meiosis (default 0.3)
- `LARGE_MUTATION_CHANCE`: Within mutations, chance of large effect (default 0.05)
- `DOMINANCE_MUTATION_RATE`: Chance a mutation affects dominance instead of value (default 0.15)
- `POINT_MUTATION_STDDEV`: Standard deviation for point mutations (default 0.3)
- `LARGE_MUTATION_STDDEV`: Standard deviation for large-effect mutations (default 1.5)
- `SOMATIC_MUTATION_RATE`: Rate of lifetime mutations per agent (default 0.2)

### Neural Network Settings
- `NN_TYPE`: Network architecture ('FNN' or 'RNN') (default 'FNN')
- `NN_HIDDEN_SIZE`: Number of hidden neurons (default 8)
- `NN_WEIGHT_INIT_STD`: Standard deviation for initial weight randomization (default 0.3)
- `NN_RECURRENT_IDENTITY_BIAS`: Stability bias for RNN hidden-to-hidden connections (default 0.1)
- `NN_HIDDEN_NOISE_ENABLED`: Add stochastic noise to RNN hidden state (default False)
- `NN_HIDDEN_NOISE_STD`: Noise standard deviation (default 0.02)

### N-Step Memory Settings
- `N_STEP_MEMORY_ENABLED`: Enable memory buffer (default False)
- `N_STEP_MEMORY_DEPTH`: Number of past states to store (default 2)

### Sensing Settings
- `SECTOR_COUNT`: Number of angular vision sectors (default 5)
- `VISION_NOISE_STD`: Noise added to sensor inputs (default 0.05)

### Internal State Settings
- `STRESS_GAIN_RATE`: Stress accumulation rate (default 0.5)
- `STRESS_DECAY_RATE`: Stress natural decay rate (default 0.2)
- `STRESS_THREAT_WEIGHT`: Weight for nearby threat stress (default 1.0)
- `STRESS_RESOURCE_WEIGHT`: Weight for low resource stress (default 0.5)

### Effort System Settings
- `EFFORT_SPEED_SCALE`: How much effort affects speed (default 1.0)
- `EFFORT_DAMAGE_SCALE`: How much effort affects attack damage (default 0.5)
- `EFFORT_ENERGY_SCALE`: How much effort affects energy cost (default 1.5)

### Energy Settings
- `BASE_ENERGY`: Starting energy value (default 150.0)
- `MAX_ENERGY`: Maximum energy capacity (default 300.0)
- `REPRODUCTION_THRESHOLD`: Energy needed to reproduce (default 80.0)
- `REPRODUCTION_COST`: Energy cost of reproduction (default 40.0)
- `FOOD_ENERGY`: Energy gained from food (default 60.0)
- `ENERGY_DRAIN_BASE`: Base energy loss per second (default 0.3)
- `MOVEMENT_ENERGY_FACTOR`: Energy cost of movement (default 0.01)

### Hydration Settings
- `BASE_HYDRATION`: Starting hydration value (default 100.0)
- `MAX_HYDRATION`: Maximum hydration capacity (default 150.0)
- `HYDRATION_DRAIN_RATE`: Hydration loss per second (default 0.4)
- `DRINK_RATE`: Hydration gain per second when drinking (default 30.0)

### Water Settings
- `NUM_WATER_SOURCES`: Number of water sources (default 4)
- `WATER_SOURCE_RADIUS`: Radius of water sources (default 40.0)

### Combat Settings
- `ATTACK_DISTANCE`: Distance threshold for attacks (default 10.0)
- `ATTACK_DAMAGE_BASE`: Base damage per second of attack (default 20.0)
- `ATTACK_ENERGY_COST`: Energy cost per second of attacking (default 2.0)
- `KILL_ENERGY_GAIN`: Energy gained from successful kills (default 30.0)

### Food Cluster Settings
- `NUM_FOOD_CLUSTERS`: Number of food cluster centers (default 5)
- `FOOD_CLUSTER_SPREAD`: Gaussian sigma for food scatter (default 40.0)
- `SEASON_SHIFT_INTERVAL`: Seconds between cluster drift (default 30.0)

### World Settings
- `WORLD_WIDTH`: Width of the simulation world (default 1200)
- `WORLD_HEIGHT`: Height of the simulation world (default 600)
- `GRID_CELL_SIZE`: Size of spatial grid cells for neighbor queries (default 50)
- `HUD_WIDTH`: Width of the heads-up display panel (default 280)
- `WINDOW_WIDTH`: Width of the display window (default 3280)
- `WINDOW_HEIGHT`: Height of the display window (default 1400)

### Agent Settings
- `MAX_SPEED_BASE`: Base maximum speed capability (default 6.0)
- `EATING_DISTANCE`: Distance threshold for food consumption (default 10.0)
- `MATING_DISTANCE`: Distance for reproduction (default 50.0)
- `WANDER_STRENGTH`: Strength of wandering behavior (default 0.5)
- `STEER_STRENGTH`: Strength of steering behavior (default 0.3)

### Aging Settings
- `MATURITY_AGE`: Age when agents become capable of reproduction (default 5.0)
- `MAX_AGE`: Maximum genetic age limit (default 70.0)

### Reproduction Settings
- `REPRODUCTION_COOLDOWN`: Time between reproduction attempts in seconds (default 3.0)
- `MATE_SEARCH_RADIUS`: Search radius for finding mates (default 100.0)
- `MAX_SIMULTANEOUS_OFFSPRING`: Maximum offspring per mating session (default 1)

### Other Settings
- `CANNIBALISM_ENERGY_BONUS`: Additional energy gained from eating another agent (default 20.0)

### Temperature Zone Settings
- `TEMPERATURE_ENABLED`: Enable/disable temperature zones (default False)
- `TEMPERATURE_ZONES_X`: Number of temperature zones horizontally (default 2)
- `TEMPERATURE_ZONES_Y`: Number of temperature zones vertically (default 2)

### Initialization Settings
- `RANDOM_AGE_INITIALIZATION`: Initialize agents with random ages (default True)

### Epidemic Settings
- `EPIDEMIC_ENABLED`: Enable/disable epidemic events (default False)
- `EPIDEMIC_INTERVAL`: Seconds between epidemic checks (default 100.0)
- `EPIDEMIC_MIN_POPULATION_RATIO`: Minimum population ratio to trigger epidemic (default 0.8)
- `EPIDEMIC_AFFECTED_RATIO`: Fraction of population affected by epidemic (default 0.3)
- `EPIDEMIC_BASE_PROBABILITY`: Base probability when conditions met (default 0.001)

### Species Settings
- `INITIAL_SAME_SPECIES_PERCENTAGE`: Percentage from same species initially (default 1.0)
- `SPECIES_GENETIC_SIMILARITY_THRESHOLD`: Similarity threshold for same species (default 0.8)
- `SPECIES_DRIFT_RATE`: Rate of genetic difference accumulation (default 0.4)
- `HYBRID_FERTILITY_RATE`: Fertility for cross-species offspring (default 0.1)
- `NUMBER_OF_INITIAL_SPECIES`: Number of different species initially (default 4)

### Geographic Variation Settings
- `REGIONAL_VARIATIONS_ENABLED`: Enable/disable regional trait modifiers (default False)
- `NUM_REGIONS_X`: Number of regions horizontally (default 2)
- `NUM_REGIONS_Y`: Number of regions vertically (default 2)
- `REGION_SPEED_MODIFIER`: Speed modifiers for each region (TL, TR, BL, BR) (default [1.1, 0.9, 1.0, 1.2])
- `REGION_SIZE_MODIFIER`: Size modifiers for each region (default [0.9, 1.1, 1.0, 0.8])
- `REGION_AGGRESSION_MODIFIER`: Aggression modifiers for each region (default [1.2, 0.8, 1.0, 1.3])
- `REGION_EFFICIENCY_MODIFIER`: Energy efficiency modifiers for each region (default [0.95, 1.05, 1.0, 0.85])

### Disease Settings
- `DISEASE_TRANSMISSION_ENABLED`: Enable/disable disease transmission (default True)
- `DISEASE_TRANSMISSION_DISTANCE`: Distance threshold for transmission (default 15.0)
- `DISEASE_NAMES`: Names for different diseases (default ['Flu', 'Plague', 'Malaria', 'Pox', 'Fever', 'Rot', 'Blight', 'Wilt'])
- `NUM_DISEASE_TYPES`: Number of different disease types (default 4)

### Obstacle Settings
- `OBSTACLES_ENABLED`: Enable/disable obstacles (default False)
- `BORDER_ENABLED`: Enable/disable border walls (default True)
- `BORDER_WIDTH`: Width of border obstacles (default 10)
- `NUM_INTERNAL_OBSTACLES`: Number of internal obstacles (default 5)

### Rendering Settings
- `FPS`: Target frames per second (default 60)

### Trait Range Settings
- `TRAIT_RANGES`: Dictionary defining valid ranges for each trait:
  - `speed`: (1.0, 6.0)
  - `size`: (3.0, 12.0)
  - `vision_range`: (40.0, 200.0)
  - `energy_efficiency`: (0.5, 2.0)
  - `reproduction_urge`: (0.3, 1.5)
  - `camouflage`: (0.0, 1.0)
  - `aggression`: (0.3, 2.0)
  - `max_age`: (10.0, 150.0)
  - `virus_resistance`: (0.0, 1.0)
  - `agility`: (0.0, 1.0)
  - `armor`: (0.0, 1.0)

### Trait Default Settings
- `TRAIT_DEFAULTS`: Dictionary defining default values for each trait:
  - `speed`: 3.0
  - `size`: 6.0
  - `vision_range`: 100.0
  - `energy_efficiency`: 1.0
  - `reproduction_urge`: 0.8
  - `camouflage`: 0.5
  - `aggression`: 1.0
  - `max_age`: 70.0
  - `virus_resistance`: 0.5
  - `agility`: 0.5
  - `armor`: 0.5

### Advanced Feature Flags
- `ADVANCED_SIZE_EFFECTS_ENABLED`: Enable size-based trade-offs (default False)
- `AGE_EFFECTS_ENABLED`: Enable age-based modulation (default False)
- `INTERNAL_STATE_MODULATION_ENABLED`: Enable soft internal state effects (default False)
- `ACTION_COSTS_ENABLED`: Enable differentiated action costs (default False)
- `MORPHOLOGY_TRAITS_ENABLED`: Enable agility and armor traits (default False)
- `SENSORY_NOISE_ENABLED`: Enable sensory noise (default True)
- `CONTEXT_SIGNALS_ENABLED`: Enable time-since-event signals (default False)
- `SOCIAL_PRESSURE_ENABLED`: Enable crowding/social stress (default True)

### Advanced Feature Parameters
#### Body Size Effects Parameters
- `SIZE_ATTACK_SCALING`: Exponent for attack strength scaling (1.5)
- `SIZE_SPEED_PENALTY`: Linear penalty per size unit for speed (0.3)
- `SIZE_TURN_PENALTY`: Penalty for turning (0.4)
- `SIZE_METABOLIC_SCALING`: Exponent for metabolic cost (1.3)
- `SIZE_PERCEPTION_BONUS`: Bonus for perception range (0.1)

#### Size-Scaled Energy Costs Parameters
- `SUPERLINEAR_ENERGY_SCALING`: Use superlinear scaling (True)
- `ENERGY_SIZE_EXPONENT`: Exponent for metabolic cost scaling (1.4)
- `EFFORT_SIZE_INTERACTION`: How effort amplifies size cost (0.5)

#### Age-Dependent Modulation Parameters
- `AGE_PRIME_START`: Age ratio when prime begins (0.2)
- `AGE_PRIME_END`: Age ratio when prime ends (0.6)
- `AGE_SPEED_DECLINE`: Max speed reduction in old age (0.3)
- `AGE_STAMINA_DECLINE`: Max stamina reduction in old age (0.4)
- `AGE_EXPERIENCE_BONUS`: Combat bonus from experience (0.2)
- `AGE_REPRODUCTION_CURVE`: Reproduction effectiveness varies with age (True)

#### Internal State Modulation Parameters
- `LOW_ENERGY_ATTACK_PENALTY`: Attack effectiveness penalty when energy low (0.5)
- `LOW_HYDRATION_SPEED_PENALTY`: Speed penalty when dehydrated (0.3)
- `HIGH_STRESS_EFFORT_BOOST`: Stress boost for short-term effort (0.2)
- `EXHAUSTION_THRESHOLD`: Energy level for penalties (0.2)

#### Action-Specific Cost Asymmetry Parameters
- `COST_HIGH_SPEED_MULTIPLIER`: Extra cost for max speed (1.5)
- `COST_SHARP_TURN_MULTIPLIER`: Extra cost for sharp turns (1.3)
- `COST_PURSUIT_MULTIPLIER`: Extra cost for sustained pursuit (1.2)
- `COST_ATTACK_BASE`: Base energy cost per attack tick (3.0)
- `COST_MATING_BASE`: Energy cost for mating attempt (5.0)

#### Morphological Trade-offs Parameters
- `AGILITY_SPEED_BONUS`: Turning/acceleration bonus (0.4)
- `AGILITY_STAMINA_COST`: Metabolism cost for agility (0.2)
- `ARMOR_DAMAGE_REDUCTION`: Damage reduction from armor (0.4)
- `ARMOR_SPEED_PENALTY`: Speed penalty from armor (0.3)
- `ARMOR_ENERGY_COST`: Maintenance cost for armor (0.15)

#### Sensory Imperfection Parameters
- `SENSOR_DROPOUT_RATE`: Probability of missing sector signals (0.05)
- `INTERNAL_STATE_NOISE`: Noise on internal state perception (0.03)
- `PERCEPTION_LAG`: Delay in perception (0.0 = disabled)

#### Context Signals Parameters
- `TIME_SINCE_FOOD_DECAY`: Seconds for food signal to decay (10.0)
- `TIME_SINCE_DAMAGE_DECAY`: Seconds for damage signal to decay (15.0)
- `TIME_SINCE_MATING_DECAY`: Seconds for mating signal to decay (20.0)

#### Social Pressure Effects Parameters
- `CROWD_STRESS_RADIUS`: Radius for counting nearby agents (50.0)
- `CROWD_STRESS_THRESHOLD`: Number of agents before stress increases (3)
- `CROWD_STRESS_RATE`: Stress increase per extra agent (0.1)
- `DOMINANCE_STRESS_FACTOR`: Stress from larger/aggressive neighbors (0.5)

---

## Chapter 10: Data Structures {#data-structures}

### Agent Class
The Agent class represents individual creatures in the simulation with comprehensive attributes and methods:

**Core Attributes**:
- **ID**: Sequentially assigned unique identifier for the agent
- **Position**: Vector2 position in the world
- **Velocity**: Vector2 movement direction and speed
- **Genome**: The agent's complete genetic code
- **Phenotype**: Expressed traits derived from the genome
- **Brain**: Neural network controller (FNN or RNN based on settings)
- **Energy/Hydration/Age**: Vital statistics
- **Generation**: Genetic generation number of the agent
- **State flags**: Alive status, reproduction cooldown, etc.
- **Total Mutations**: Accumulated mutations for visualization purposes

**Neural Network Attributes**:
- **NN Type**: Neural network architecture type (FNN or RNN)
- **Brain Rebuild Capability**: Ability to rebuild brain from current genome after somatic mutations
- **Brain State Reset**: Ability to reset RNN hidden state on significant events
- **Saved Hidden State Preservation**: Preserves RNN hidden state during brain rebuilds when possible
- **Neural outputs**: Last computed movement and behavioral drives (move_x, move_y, avoid, attack, mate, effort)
- **Attack Drive**: Tendency to engage in combat behavior
- **Mate Desire**: Tendency to seek reproduction opportunities
- **Avoid Drive**: Tendency to flee from threats
- **Behavioral Drives**: Decoupled behavioral tendencies (avoid, attack, mate) that influence movement
- **Effort System**: Global intensity/energy expenditure level that scales all activities
- **Internal state**: Stress level, recent damage, memory buffer
- **Recent Damage**: Tracking of damage recently received for stress calculations
- **Last Velocity**: Previous velocity for calculating sharp turn detection in energy costs
- **Memory Buffer**: N-step memory storage for temporal context (when enabled)
- **Last NN Inputs/Outputs**: Stored for visualization
- **Last Hidden Activations**: Stored for visualization

**Genetic Attributes**:
- **Genetic Similarity Calculation**: Method for comparing genetic makeup between agents
- **Calculate Genetic Similarity Method**: Function for computing genetic similarity with another agent
- **Genetic Distance Calculation**: Method for measuring how genetically different an agent is from population mean
- **Calculate Genetic Distance From Mean Method**: Function for computing genetic difference from population average
- **Species Classification**: Based on genetic similarity
- **Determine Shape Type Method**: Function for determining visual shape based on species ID
- **Same Species Check Method**: Function for determining if another agent belongs to the same species
- **Genetic Similarity Score**: Measure of similarity to original species (0.0-1.0)
- **Genetic Similarity Score Property**: Getter for genetic similarity score
- **Calculate Genetic Distance From Mean Method**: Function for computing genetic difference from population average
- **Genetic Distance Calculation**: Method for measuring how genetically different an agent is from population mean
- **Calculate Genetic Similarity Method**: Function for computing genetic similarity with another agent
- **Genetic Similarity Calculation**: Method for comparing genetic makeup between agents
- **Same Species Check Method**: Function for determining if another agent belongs to the same species
- **Determine Shape Type Method**: Function for determining visual shape based on species ID
- **Species Classification**: Based on genetic similarity

**Behavioral Attributes**:
- **Dietary Classification**: Updated based on behavior ('omnivore', 'carnivore', 'herbivore')
- **Dietary Classification Property**: Getter for current dietary classification
- **Hunting Success Rate**: Tracked based on attack success
- **Hunting Success Rate Property**: Getter for hunting success rate
- **Herding Behavior**: Tendency to stay near food sources
- **Herding Behavior Property**: Getter for herding behavior value
- **Carnivorous Tendency**: Tracked based on behavior
- **Carnivorous Tendency Property**: Getter for carnivorous tendency value
- **Herbivorous Tendency**: Tracked based on behavior
- **Herbivorous Tendency Property**: Getter for herbivorous tendency value
- **Dietary Behavior Tracking**: Continuous monitoring of feeding patterns and classification
- **Dietary Behavior Tracking Property**: Getter for dietary behavior tracking status
- **Dietary Behavior Update Method**: Function for updating dietary classification based on recent actions

**Mutation Attributes**:
- **Mutation History**: Complete record of all mutations over agent's lifetime
- **Mutation History Property**: Getter for complete mutation history
- **Dominant Mutations**: Significant mutations that define the agent's characteristics
- **Dominant Mutations Property**: Getter for dominant mutations list
- **Somatic Mutation Timer**: Countdown for recent lifetime mutations
- **Somatic Mutation Timer Property**: Getter for somatic mutation countdown timer
- **Total Mutations**: Accumulated mutations for visualization purposes
- **Total Mutations Property**: Getter for accumulated mutation count

**Disease Attributes**:
- **Disease Resistances**: Genetic resistances to different diseases
- **Disease Resistances Property**: Getter for genetic disease resistances
- **Disease Recovery Rates**: How quickly agents recover from diseases
- **Disease Recovery Rates Property**: Getter for disease recovery rate values
- **Get Disease Resistance Method**: Function for retrieving resistance to a specific disease
- **Can Catch Disease Method**: Function for checking if agent can contract a specific disease
- **Apply Disease Effects Method**: Function for applying specific effects of a disease to the agent
- **Reverse Disease Effects Method**: Function for reversing disease effects upon recovery
- **Infection Status**: Whether agent is currently infected
- **Infection Status Property**: Getter for current infection status
- **Current Disease**: Name of the disease affecting the agent
- **Current Disease Property**: Getter for current disease name
- **Infection Timer**: Duration remaining for infection effects
- **Infection Timer Property**: Getter for infection duration timer
- **Infection Methods**: Functions for infecting, recovering, and checking disease resistance
- **Infection Status Update Method**: Function for updating infection status and handling recovery

**Physical Attributes**:
- **Radius**: Calculated based on the agent's size trait
- **Radius Property**: Getter for agent's display radius based on size and species
- **Speed Property**: Getter for speed with regional modifiers applied
- **Size Property**: Getter for size with regional modifiers applied
- **Vision Range Property**: Getter for vision range from phenotype
- **Efficiency Property**: Getter for efficiency with regional modifiers applied
- **Aggression Property**: Getter for aggression with regional modifiers applied
- **Max Age Property**: Getter for genetic maximum age
- **Virus Resistance Property**: Getter for genetic virus resistance
- **Agility Property**: Getter for morphological agility trait
- **Armor Property**: Getter for morphological armor trait
- **Sex Property**: Getter for genetic sex determination
- **Shape Type**: Determined based on species ID (circle, square, triangle, parallelogram, diamond, hexagon, pentagon, star)
- **Shape Type Property**: Getter for visual shape based on species ID
- **Facing Angle**: Determined by velocity direction for sector-based sensing
- **Region**: Determined based on position and world settings
- **Region Property**: Getter for current geographic region
- **Determine Region Method**: Function for calculating which geographic region the agent is in
- **Region Update Method**: Function for updating agent's region when it moves to a new area
- **Region Trait Modifiers**: Specific modifiers for speed, size, aggression, efficiency, etc. based on geographic region
- **Get Region Trait Modifiers Method**: Function for retrieving trait modifiers based on current region
- **Modified Traits**: Traits adjusted by regional modifiers
- **Modified Traits Property**: Getter for traits with regional adjustments applied
- **Get Modified Trait Method**: Function for retrieving trait values with regional modifications applied
- **Get Modified Trait Method Property**: Getter for trait modification retrieval method

**Reproduction and Survival Attributes**:
- **Offspring Count**: Number of successful reproductions
- **Offspring Count Property**: Getter for number of successful reproductions
- **Reproduction Success Tracking**: Monitoring of successful reproduction events
- **Can Reproduce Method**: Function for checking if agent meets reproduction requirements
- **Death Handling**: Function for managing agent death and cleanup
- **Reproduction Cooldown Property**: Getter for reproduction cooldown timer
- **Energy Property**: Getter for current energy level
- **Hydration Property**: Getter for current hydration level
- **Age Property**: Getter for current age
- **Generation Property**: Getter for genetic generation number

**Visual and Sensory Attributes**:
- **Base Color**: Fixed color based on genetic makeup (calculated once at initialization)
- **Base Color Property**: Getter for fixed base color
- **Color Calculation**: Method for determining base color from genetic color traits
- **Color Calculation Property**: Getter for color calculation method
- **Get Color Method**: Function for retrieving agent's current color with energy brightness applied
- **Get Color Method Property**: Getter for color retrieval method
- **Current Modifiers**: Dynamic modifiers from advanced features
- **Current Modifiers Property**: Getter for current dynamic modifiers
- **Visual properties**: Base color, shape type, size
- **Visual Properties**: Contains base color, shape type, and size getters
- **Species info**: Species ID and genetic similarity score
- **Species ID Property**: Getter for species identifier
- **Disease tracking**: Infection status and resistances
- **Disease Tracking Properties**: Contains infection status, current disease, and resistance getters

**System Integration Attributes**:
- **Legacy Compatibility**: Attack intent for backward compatibility with older systems
- **Brain Rebuild Capability**: Ability to rebuild brain from current genome after somatic mutations
- **Brain State Reset**: Ability to reset RNN hidden state on significant events
- **Saved Hidden State Preservation**: Preserves RNN hidden state during brain rebuilds when possible
- **Behavioral Drives Property**: Getter for behavioral drive values
- **Effort Property**: Getter for current effort level
- **Stress Property**: Getter for current stress level
- **Recent Damage Property**: Getter for recent damage value
- **Memory Buffer Property**: Getter for memory buffer reference
- **Last NN Inputs Property**: Getter for last neural network inputs
- **Last NN Outputs Property**: Getter for last neural network outputs
- **Last Hidden Activations Property**: Getter for last hidden layer activations
- **Neural Outputs Property**: Getter for last computed neural network outputs
- **Behavioral Drives**: Decoupled behavioral tendencies (avoid, attack, mate) that influence movement
- **Effort System**: Global intensity/energy expenditure level that scales all activities
- **Internal state**: Stress level, recent damage, memory buffer
- **Memory Buffer Property**: Getter for memory buffer reference
- **Recent Damage**: Tracking of damage recently received for stress calculations
- **Last Velocity Property**: Getter for previous velocity value
- **Attack Drive Property**: Getter for attack tendency value
- **Mate Desire Property**: Getter for mate desire value
- **Avoid Drive Property**: Getter for avoid tendency value
- **Effort Property**: Getter for current effort level
- **Stress Property**: Getter for current stress level
- **Recent Damage Property**: Getter for recent damage value
- **Species ID Property**: Getter for species identifier
- **Visual Properties**: Contains base color, shape type, and size getters
- **Disease Tracking Properties**: Contains infection status, current disease, and resistance getters

### World Class
The World class manages the simulation environment with comprehensive entity and system management:

**Entity Lists**:
- **Agent List**: All living agents in the world
- **Food List**: All food items in the world
- **Water List**: All water sources in the world
- **Obstacle List**: All terrain obstacles in the world

**Spatial Grids**:
- **Agent Grid**: Spatial grid for efficient agent neighbor queries
- **Food Grid**: Spatial grid for efficient food neighbor queries
- **Water Grid**: Spatial grid for efficient water neighbor queries
- **Obstacle Grid**: Spatial grid for efficient obstacle neighbor queries

**Environmental Systems**:
- **Food Clusters**: System for managing drifting food cluster spawn points
- **Settings Reference**: Reference to current simulation parameters
- **Temperature Zones**: System for geographic temperature variations
- **World Dimensions**: Width and height of the simulation world
- **Spatial Grid System**: Optimized data structures for neighbor queries

**Management Functions**:
- **Cleanup Method**: Function for removing dead agents and expired items
- **Spawn Food Method**: Function for creating new food items based on settings
- **Food Clusters Update**: Function for drifting food cluster positions over time
- **Get Temperature At Position Method**: Function for calculating temperature at specific locations
- **Rebuild Grids Method**: Function for updating spatial grids each frame
- **Query Nearest Method**: Function for finding nearest entities of specific types
- **Query Radius Method**: Function for finding entities within a radius
- **World Boundary Handling**: Methods for handling agent movement across world boundaries
- **World Wrapping**: Torus implementation (agents wrap around edges)
- **Collision Detection**: Methods for detecting collisions between agents and obstacles
- **Event Manager Reference**: Connection to the event management system
- **Disease Transmission System**: Connection to the disease spread system
- **Statistics Collector**: Connection to the statistical tracking system

### Neural Network Classes

#### NeuralBrain (FNN)
The Feed-Forward Neural Network implementation with 24 inputs → 8 hidden → 6 outputs:

**Architecture**:
- **N_INPUTS**: 24 inputs (sector-based sensing)
- **N_HIDDEN**: 8 hidden neurons with tanh activation
- **N_OUTPUTS**: 6 outputs (movement and behavioral drives)
- **N_WEIGHTS**: 254 total weights (192 input-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)

**Weights and Biases**:
- **Input-to-Hidden Weights**: 192 weights (24 inputs × 8 hidden)
- **Hidden Biases**: 8 bias values for hidden neurons
- **Hidden-to-Output Weights**: 48 weights (8 hidden × 6 outputs)
- **Output Biases**: 6 bias values for output neurons

**Processing**:
- **Forward Method**: Performs forward pass through the network
- **Input Validation**: Ensures proper input length with padding if needed
- **Hidden Activation Storage**: Stores last hidden activations for visualization
- **Output Labels**: Provides labels for the 6 outputs (move_x, move_y, avoid, attack, mate, effort)

#### RecurrentBrain (RNN)
The Recurrent Neural Network implementation with memory and temporal processing:

**Architecture**:
- **N_INPUTS**: 24 inputs (sector-based sensing)
- **N_HIDDEN**: 8 hidden neurons with tanh activation and recurrent connections
- **N_OUTPUTS**: 6 outputs (movement and behavioral drives)
- **N_WEIGHTS**: 318 total weights (192 input-hidden + 64 hidden-hidden + 8 hidden biases + 48 hidden-output + 6 output biases)

**Recurrent Connections**:
- **Input-to-Hidden Weights**: 192 weights (24 inputs × 8 hidden)
- **Hidden-to-Hidden Weights**: 64 recurrent weights (8 hidden × 8 hidden) for memory
- **Hidden Biases**: 8 bias values for hidden neurons
- **Hidden-to-Output Weights**: 48 weights (8 hidden × 6 outputs)
- **Output Biases**: 6 bias values for output neurons

**Memory and State**:
- **Hidden State**: Maintains temporal memory across time steps
- **Initial State**: Initialized with small random values to prevent saturation
- **Identity Bias**: Stability bias for recurrent connections
- **Noise Options**: Optional stochastic noise for exploration
- **State Reset**: Ability to reset hidden state when needed
- **State Retrieval**: Method to get current hidden state for memory systems

#### MemoryBuffer Class
The N-step memory buffer for temporal context:

**Structure**:
- **N Steps**: Number of past states to store
- **Hidden Size**: Size of each hidden state vector
- **Buffer**: Circular buffer storing past hidden states

**Operations**:
- **Push Method**: Adds new hidden state, shifts old ones out
- **Get Flat Method**: Returns flattened buffer for input concatenation
- **Reset Method**: Clears the buffer
- **Memory Depth**: Configurable number of past states to remember

### SpatialGrid Class
The spatial partitioning system for efficient neighbor queries:

**Grid Structure**:
- **Grid Cells**: Divides world into discrete cells for spatial queries
- **Efficient Queries**: Fast neighbor and range queries
- **Dynamic Updates**: Handles moving entities

**Query Methods**:
- **Query Radius Method**: Finds entities within a specified radius
- **Query Nearest Method**: Finds nearest entity of a specific type
- **Insert Method**: Adds entities to the grid
- **Remove Method**: Removes entities from the grid
- **Clear Method**: Empties all grid cells
- **Update Method**: Updates entity positions in the grid

**Performance**:
- **Cell Size**: Configurable size of each grid cell
- **World Partitioning**: Efficient partitioning of world space
- **Neighbor Optimization**: Dramatically improves performance of spatial queries

### ParticleSystem Class
The visual effects system for animations and particles:

**Particle Types**:
- **Heart Particles**: Created during mating events
- **Cloud Particles**: Created for infection effects
- **Other Effects**: Various visual enhancement particles

**Animation**:
- **Update Method**: Updates particle positions and lifecycles
- **Draw Method**: Renders particles to the screen
- **Lifecycle Management**: Birth, movement, and death of particles
- **Performance Optimization**: Efficient handling of large numbers of particles

---

## Chapter 11: Implementation Details {#implementation-details}

### Performance Considerations

The simulation implements several performance optimizations to handle large populations efficiently:

**Spatial Partitioning**: Uses grid-based spatial partitioning to reduce collision detection from O(n²) to O(n) complexity. Instead of checking every agent against every other agent, the world is divided into grid cells, and agents only check for neighbors within their cell and adjacent cells. This dramatically improves performance as the population grows.

**Efficient Queries**: Implements optimized spatial queries that can quickly find nearby entities without iterating through all entities in the world.

**Batch Processing**: Groups similar operations together to reduce function call overhead and improve cache locality.

**Memory Management**: Uses efficient data structures and avoids unnecessary object creation during the simulation loop.

**Selective Updates**: Only updates agents that are alive and active, skipping dead or inactive entities.

**Optimized Neural Networks**: Implements neural network computations efficiently without external dependencies like NumPy, using pure Python with optimized matrix operations.

### Scalability Features

The simulation is designed to scale with population size:

**Grid-Based Spatial Queries**: As mentioned, this reduces computational complexity from quadratic to linear with respect to population size.

**Modular Systems**: Each system operates independently but can be optimized separately for performance.

**Configurable Parameters**: Many parameters can be adjusted to balance between biological realism and computational efficiency.

**Event-Driven Architecture**: Uses event-driven systems that only activate when conditions are met, rather than continuously checking all agents.

### Extensibility

The simulation is designed to be extensible:

**Modular Architecture**: Systems are designed to be independent and can be modified or replaced without affecting other systems.

**Plugin System**: The architecture supports adding new features and behaviors through modular components.

**Configuration-Driven**: Most behaviors can be modified through configuration parameters without code changes.

**Genetic Flexibility**: The genetic system is flexible enough to accommodate new traits and behaviors through evolution.

### Error Handling and Robustness

The simulation includes robust error handling:

**Input Validation**: Validates neural network inputs and ensures proper ranges.

**Bounds Checking**: Prevents agents from exceeding valid trait ranges.

**Exception Handling**: Gracefully handles exceptions without crashing the simulation.

**Recovery Mechanisms**: Implements recovery from various failure states.

### Visualization and Monitoring

The simulation includes comprehensive visualization and monitoring:

**Real-Time Statistics**: Tracks and displays population statistics, trait evolution, and behavioral patterns.

**Genetic Visualization**: Shows neural network architecture and genetic information for selected agents.

**Historical Tracking**: Maintains historical data for long-term analysis.

**Performance Metrics**: Monitors simulation performance and provides feedback.

### Biological Accuracy

The simulation incorporates realistic biological principles:

**Genetic Inheritance**: Implements realistic diploid inheritance with dominance effects.

**Metabolic Scaling**: Uses realistic metabolic scaling laws based on body size.

**Resource Management**: Models realistic energy and hydration management with trade-offs.

**Life History**: Implements realistic aging and life-history strategies.

**Behavioral Ecology**: Models realistic behavioral strategies based on resource availability and competition.

### Evolutionary Dynamics

The simulation captures important evolutionary dynamics:

**Selection Pressure**: Implements selection based on survival and reproduction success.

**Genetic Drift**: Models random genetic drift effects in small populations.

**Mutation-Selection Balance**: Balances mutation introduction with selection pressure.

**Trade-offs**: Implements realistic biological trade-offs that constrain evolution.

**Adaptive Landscapes**: Creates complex adaptive landscapes with multiple possible strategies.

### Emergent Complexity

The simulation demonstrates emergent complexity through:

**Behavioral Strategies**: Complex strategies emerge from simple neural network outputs.

**Social Dynamics**: Social behaviors emerge from agent interactions.

**Ecological Interactions**: Complex ecological relationships emerge from resource competition.

**Evolutionary Arms Races**: Competitive interactions drive evolutionary change.

**Niche Construction**: Agents modify their environment, creating new selection pressures.

This comprehensive documentation covers all major aspects of the population simulation, including its architecture, systems, parameters, and implementation details. The simulation provides a rich platform for studying evolutionary and ecological processes through computational modeling.
