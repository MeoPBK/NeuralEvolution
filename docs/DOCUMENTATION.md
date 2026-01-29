# Population Simulation v2 - Documentation

## Overview

This simulation models a single species of agents in a 2D world. Each agent's behavior is controlled by a genetically encoded neural network. The simulation explores how complex behaviors like herbivory, cannibalism, and social dynamics can emerge through evolutionary processes.

Key features include:
- **Neural Network Brains**: Agents make decisions using either a Feed-Forward Neural Network (FNN) or a Recurrent Neural Network (RNN), selectable in settings.
- **Genetic Inheritance**: All agent traits, including their neural network weights, are determined by a diploid genome and are heritable.
- **Resource Management**: Agents must find and consume food and water to survive.
- **Dynamic Environment**: Food spawns in drifting clusters, simulating changing seasons or resource patches.
- **Emergent Behaviors**: Behaviors like fleeing, fighting (cannibalism), and mating are not hard-coded but emerge from the NN outputs.
- **Somatic Mutations**: Agents can undergo minor genetic mutations during their lifetime.
- **Genetic Lifespan**: Individual agents have genetically determined lifespans that can evolve over generations.
- **Comprehensive UI**: Full-screen settings interface with categorized parameters, scrollable controls, and intuitive value adjustment.

---

## The World

The world is a continuous 2D space that wraps around at the edges (a torus). It contains agents, food pellets, and water sources.

- **Dimensions**: Configurable via settings (default 1000x800 units).
- **Food**: Spawns in clusters. There are a fixed number of cluster centers that drift slowly over time. New food items appear at a steady rate, scattered with a Gaussian distribution around one of the random cluster centers.
- **Water**: The world contains several persistent `WaterSource` entities. These are large circular areas where agents can drink.

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

---

## Genetics

The genetic system is based on diploid chromosomes. Each gene has two alleles, and their combined expression (weighted by a dominance value) determines a trait value.

### Genome
- **8 Chromosomes**: The genome consists of 8 pairs of chromosomes.
- **Brain Genes**: Chromosomes 4 through 7 are dedicated to encoding the weights of the neural network:
  - **FNN Mode**: 130 brain genes (96 input-to-hidden + 6 hidden biases + 24 hidden-to-output + 4 output biases)
  - **RNN Mode**: 166 brain genes (adds 36 hidden-to-hidden recurrent weights)
- **Trait Genes**: Chromosomes 0 through 2 encode the agent's physical and behavioral traits (speed, size, max_age, etc.).

### Reproduction
- Two agents of the opposite sex can reproduce if they are mature, have sufficient energy, and are close to each other.
- Reproduction is driven by the `mate_desire` NN output.
- Offspring are created via crossover and mutation, inheriting a mix of their parents' genomes.

### Mutations
- **Reproductive Mutations**: Occur during reproduction with a relatively high probability. This is the primary driver of evolution.
- **Somatic Mutations**: Occur at a very low rate throughout an agent's life. They directly modify the agent's own genome, causing small changes to its phenotype and brain during its lifetime. These changes can be inherited if the agent reproduces after the mutation occurs.
- **Mutation Tracking**: Accumulated mutations are tracked and visually represented by increased brightness in agent color.

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

### Stress System
Agents have internal stress that increases from threats, low resources, and damage, then decays over time. This influences behavior through the neural network.

### RNN Hidden State (RNN Mode Only)
When using RNN mode, each agent maintains a hidden state vector (8 values):
- **Initialization**: Small random values N(0, 0.1) to prevent saturation
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
