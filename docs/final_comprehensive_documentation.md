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
10. [Implementation Details](#implementation-details)

## Project Overview

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

## Core Architecture

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

## Neural Network System

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

### Input System - Sector-Based Sensing

The neural network receives 24 inputs organized in 5 angular sectors of 72° each:

**Sector-Based Food Signals (0-4)**: Each sector provides a food presence signal calculated as the sum of 1/(1 + distance²) for all food items in that sector, normalized to [0,1]. This provides spatial awareness of food distribution without perfect location knowledge. The formula creates a realistic falloff where closer food items have stronger signals than distant ones.

**Sector-Based Water Signals (5-9)**: Each sector provides a water proximity signal based on the maximum water signal in that sector, calculated from distance to water source edges, normalized to [0,1]. The signal strength decreases with distance from water sources, encouraging agents to move toward water when thirsty.

**Sector-Based Agent Signals (10-14)**: Each sector provides an agent presence signal that indicates the relative size and threat level of agents in that sector. Positive values indicate smaller/weaker agents (potential prey), negative values indicate larger/stronger agents (potential threats), with magnitude reflecting proximity and relative size. This creates a sophisticated threat assessment system.

**Internal State Signals (15-19)**:
- **Energy (15)**: Current energy normalized by maximum energy [0,1], providing awareness of energy reserves
- **Hydration (16)**: Current hydration normalized by maximum hydration [0,1], providing awareness of water needs
- **Age Ratio (17)**: Current age divided by genetic maximum age [0,1], providing awareness of remaining lifespan
- **Stress (18)**: Internal arousal/stress level [0,1], reflecting accumulated stress from various sources
- **Health (19)**: Combined vitality metric [0,1], integrating multiple health indicators

**Egocentric Velocity (20-21)**:
- **Forward Velocity (20)**: Velocity component in facing direction [-1,1], providing awareness of movement relative to facing direction
- **Lateral Velocity (21)**: Velocity component perpendicular to facing direction [-1,1], providing awareness of sideways movement

**Self Traits (22-23)**:
- **Own Size Normalized (22)**: Agent's size normalized to trait range [0,1], providing self-awareness of physical capabilities
- **Own Speed Normalized (23)**: Agent's speed capability normalized to trait range [0,1], providing self-awareness of movement capabilities

### Output System - Decoupled Behavioral Drives

The neural network produces 6 outputs that control different aspects of behavior, allowing for complex multi-objective decision making:

**Movement Controls (0-1)**:
- **Move X (0)**: Desired X movement direction [-1,1], controlling horizontal movement
- **Move Y (1)**: Desired Y movement direction [-1,1], controlling vertical movement

**Behavioral Drives (2-4)**:
- **Avoid Drive (2)**: Flee/avoidance tendency [0,1], controlling escape behaviors from threats
- **Attack Drive (3)**: Attack tendency [0,1], controlling aggressive behaviors toward other agents
- **Mate Desire (4)**: Reproduction seeking tendency [0,1], controlling mate-seeking behaviors

**Global Control (5)**:
- **Effort (5)**: Global intensity/energy expenditure level [0,1], controlling the intensity of all activities

### N-Step Memory Extension

When enabled, the system stores past hidden states and provides them as additional inputs to the neural network, giving FNN agents pseudo-memory and enhancing RNN temporal reasoning capabilities. The depth is configurable (typically 1-2 steps) and the system maintains a circular buffer of past hidden states. This allows agents to make decisions based on recent history, enabling more sophisticated temporal strategies.

### Stress System

Agents maintain an internal stress level that influences their behavior and neural network inputs:
- **Gain Sources**: Nearby threats, low resources, recent damage
- **Decay**: Natural decay over time with configurable rate
- **Effects**: Influences decision-making, energy consumption, and behavioral thresholds
- **Computation**: Stress increases based on threat level, resource stress, and recent damage, then decays naturally

## Genetic System

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

## Simulation Systems

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

**Death from Age**: Handles death from old age when agents exceed their genetically determined max_age. The max_age trait is subject to evolutionary pressure.

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

## Environment and Entities

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

## Advanced Features

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

## User Interface and Controls

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

## Configuration Parameters

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
- `MATING_DISTANCE`: Distance threshold for reproduction (default 50.0)
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

## Data Structures

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
- **World Wrapping**: Toroidal world implementation (agents wrap around edges)
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

## Implementation Details

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

**Genetic Flexibility**: The genetic system is flexible enough to accommodate new traits and behaviors.

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