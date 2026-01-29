# Neural Architecture V2 - Design Specification

## Overview

This document specifies a redesigned neural network architecture for the evolutionary simulation, focusing on:
- **Sector-based spatial sensing** instead of single-point nearest-entity detection
- **Decoupled behavioral drives** for nuanced action selection
- **Enhanced RNN mechanics** with proper initialization and optional memory extensions
- **Embodied realism** through egocentric sensing and internal state modeling

---

## 1. Input Vector Specification (24 inputs)

### 1.1 Sector-Based Spatial Sensing (15 inputs)

The agent's vision is divided into **5 angular sectors** of 72° each, centered on the agent's facing direction:

```
Sector Layout (top-down view, agent facing up):

         [2]          Sector 0: Front      (-36° to +36°)
       /     \        Sector 1: Front-Left (+36° to +108°)
     [1]     [3]      Sector 2: Left       (+108° to +180°)
      |   A   |       Sector 3: Front-Right(-108° to -36°)
     [4]     [0]      Sector 4: Right      (-180° to -108°)
       \     /
         [4]
```

**Note**: Sectors wrap around; rear coverage is split between sectors 2 and 4.

For each sector, three signals are computed:

| Input | Name | Description | Range | Computation |
|-------|------|-------------|-------|-------------|
| 0-4 | `sector_food[0-4]` | Food presence in sector | 0 to 1 | Sum of (1 / (1 + dist²)) for all food in sector, clamped |
| 5-9 | `sector_water[0-4]` | Water proximity in sector | 0 to 1 | Max water signal in sector based on distance to edge |
| 10-14 | `sector_agent[0-4]` | Agent presence in sector | -1 to 1 | Weighted sum; sign indicates size comparison |

**Sector Agent Signal Details**:
- Positive values indicate smaller/weaker agents (potential prey)
- Negative values indicate larger/stronger agents (potential threats)
- Magnitude reflects proximity and count

### 1.2 Internal State (5 inputs)

| Input | Name | Description | Range |
|-------|------|-------------|-------|
| 15 | `energy` | Current energy / MAX_ENERGY | 0 to 1 |
| 16 | `hydration` | Current hydration / MAX_HYDRATION | 0 to 1 |
| 17 | `age_ratio` | Current age / genetic max_age | 0 to 1 |
| 18 | `stress` | Internal arousal/stress level | 0 to 1 |
| 19 | `health` | Combined vitality metric | 0 to 1 |

**Stress Computation**:
```python
stress += stress_gain_rate * dt * (
    nearby_agent_threat +      # Larger agents nearby
    (1 - energy) * 0.5 +       # Low energy
    (1 - hydration) * 0.3 +    # Low hydration
    recent_damage * 2.0        # Recent attacks received
)
stress -= stress_decay_rate * dt  # Natural decay
stress = clamp(stress, 0, 1)
```

### 1.3 Egocentric Velocity (2 inputs)

| Input | Name | Description | Range |
|-------|------|-------------|-------|
| 20 | `vel_forward` | Velocity in facing direction / max_speed | -1 to 1 |
| 21 | `vel_lateral` | Velocity perpendicular to facing / max_speed | -1 to 1 |

### 1.4 Self Traits (2 inputs)

| Input | Name | Description | Range |
|-------|------|-------------|-------|
| 22 | `own_size_norm` | Own size normalized to trait range | 0 to 1 |
| 23 | `own_speed_norm` | Own speed capability normalized | 0 to 1 |

### 1.5 Optional: N-Step Memory Extension

When `N_STEP_MEMORY_ENABLED` is true, concatenate previous hidden states:

| Inputs | Name | Description | Range |
|--------|------|-------------|-------|
| 24-29 | `h_t1[0-5]` | Hidden state from t-1 | -1 to 1 |
| 30-35 | `h_t2[0-5]` | Hidden state from t-2 (if n=2) | -1 to 1 |

**Total with n-step memory**: 24 + (n × hidden_size)
- n=1: 30 inputs
- n=2: 36 inputs

---

## 2. Output Vector Specification (6 outputs)

All outputs use tanh activation, producing values in [-1, 1] or scaled to [0, 1].

| Output | Name | Raw Range | Interpretation |
|--------|------|-----------|----------------|
| 0 | `move_x` | -1 to 1 | Desired movement direction X (world-relative) |
| 1 | `move_y` | -1 to 1 | Desired movement direction Y (world-relative) |
| 2 | `avoid_drive` | 0 to 1 | Flee/avoidance tendency (scaled from tanh) |
| 3 | `attack_drive` | 0 to 1 | Attack tendency when in range |
| 4 | `mate_desire` | 0 to 1 | Reproduction seeking tendency |
| 5 | `effort` | 0 to 1 | Global intensity/energy expenditure |

### Output Scaling

```python
# Raw tanh outputs
raw = brain.forward(inputs)

# Movement (keep as-is)
move_x, move_y = raw[0], raw[1]

# Drives scaled to [0, 1]
avoid_drive = (raw[2] + 1) / 2
attack_drive = (raw[3] + 1) / 2
mate_desire = (raw[4] + 1) / 2
effort = (raw[5] + 1) / 2
```

### Behavioral Interpretation

**Movement Resolution**:
```python
# Base movement from NN
movement = Vector2(move_x, move_y).normalized()

# Modify based on drives
if avoid_drive > 0.5 and nearest_threat:
    # Blend movement away from threat
    flee_dir = (self.pos - threat.pos).normalized()
    movement = lerp(movement, flee_dir, avoid_drive - 0.5)

# Scale by effort
actual_speed = max_speed * effort
movement *= actual_speed
```

**Combat Resolution**:
```python
# Attack only if:
# 1. attack_drive > threshold (0.5)
# 2. Target in range
# 3. avoid_drive < attack_drive (not fleeing)
can_attack = (
    attack_drive > 0.5 and
    target_in_range and
    attack_drive > avoid_drive
)

# Damage scales with effort
damage = base_damage * aggression * effort
```

**Energy Cost**:
```python
# All actions scale with effort
energy_cost = (
    base_drain +
    movement_cost * speed * effort +
    attack_cost * is_attacking * effort
)
```

---

## 3. Neural Network Architecture

### 3.1 FNN Architecture

```
Inputs (24) → Hidden (8, tanh) → Outputs (6, tanh)

Weights:
- Input→Hidden: 24 × 8 = 192
- Hidden biases: 8
- Hidden→Output: 8 × 6 = 48
- Output biases: 6

Total: 254 weights
```

### 3.2 RNN Architecture

```
Inputs (24) → Hidden (8, tanh, recurrent) → Outputs (6, tanh)

Weights:
- Input→Hidden: 24 × 8 = 192
- Hidden→Hidden (recurrent): 8 × 8 = 64
- Hidden biases: 8
- Hidden→Output: 8 × 6 = 48
- Output biases: 6

Total: 318 weights
```

### 3.3 Hidden State Dynamics (RNN)

```python
def forward(self, inputs):
    # Compute new hidden state
    ih_sum = matmul(self.w_ih, inputs)      # Input contribution
    hh_sum = matmul(self.w_hh, self.hidden) # Recurrent contribution

    # Optional stochastic noise for exploration
    if self.use_noise:
        noise = [random.gauss(0, 0.02) for _ in range(N_HIDDEN)]
        hh_sum = [h + n for h, n in zip(hh_sum, noise)]

    # Update hidden state
    self.hidden = [tanh(ih + hh + b)
                   for ih, hh, b in zip(ih_sum, hh_sum, self.b_h)]

    # Compute outputs
    output = [tanh(sum(h * w for h, w in zip(self.hidden, self.w_ho[o])) + self.b_o[o])
              for o in range(N_OUTPUTS)]

    return output
```

### 3.4 Initialization Strategy

**Weight Initialization**:
```python
# Standard weights: small random
w_ih = [[random.gauss(0, 0.3) for _ in range(N_INPUTS)]
        for _ in range(N_HIDDEN)]

# Recurrent weights: slight identity bias for stability
w_hh = [[random.gauss(0.1 if i == j else 0, 0.2)
         for j in range(N_HIDDEN)]
        for i in range(N_HIDDEN)]

# Biases: near zero
b_h = [random.gauss(0, 0.1) for _ in range(N_HIDDEN)]
b_o = [random.gauss(0, 0.1) for _ in range(N_OUTPUTS)]
```

**Hidden State Initialization**:
```python
# Small random values prevent immediate saturation
hidden = [random.gauss(0, 0.1) for _ in range(N_HIDDEN)]
```

---

## 4. N-Step Memory System

### 4.1 Overview

When enabled, the agent stores the last `n` hidden states and provides them as additional inputs. This gives FNN agents pseudo-memory and enhances RNN temporal reasoning.

### 4.2 Implementation

```python
class MemoryBuffer:
    def __init__(self, n_steps, hidden_size):
        self.n_steps = n_steps
        self.hidden_size = hidden_size
        self.buffer = [[0.0] * hidden_size for _ in range(n_steps)]

    def push(self, hidden_state):
        """Add new hidden state, shift old ones"""
        self.buffer.pop(0)
        self.buffer.append(list(hidden_state))

    def get_flat(self):
        """Return flattened buffer for input concatenation"""
        return [v for state in self.buffer for v in state]
```

### 4.3 Integration

```python
def compute_nn_inputs(agent, world):
    # Compute base 24 inputs
    base_inputs = compute_base_inputs(agent, world)

    if settings.N_STEP_MEMORY_ENABLED:
        # Append historical hidden states
        memory_inputs = agent.memory_buffer.get_flat()
        return base_inputs + memory_inputs

    return base_inputs
```

---

## 5. Expected Emergent Behaviors

### 5.1 From Sector-Based Sensing

| Behavior | Mechanism |
|----------|-----------|
| **Gradient following** | Agents learn to move toward sectors with higher food/water signals |
| **Flanking** | Attack from sectors where target has blind spots |
| **Threat awareness** | Negative agent signals in rear sectors trigger avoidance |
| **Herding** | Group movements emerge from consistent sector responses |

### 5.2 From Decoupled Drives

| Behavior | Mechanism |
|----------|-----------|
| **Stalking** | High approach, low attack until close range |
| **Bluffing** | High attack drive without actual engagement |
| **Panic flight** | Maximum avoid_drive overrides all else |
| **Opportunistic predation** | Attack only when avoid_drive is low |
| **Cautious approach** | Moderate avoid + moderate approach = careful investigation |

### 5.3 From Effort Scaling

| Behavior | Mechanism |
|----------|-----------|
| **Energy conservation** | Low effort when resources abundant |
| **Burst activity** | High effort for critical actions (escape, kill) |
| **Sustainable hunting** | Moderate effort for extended pursuits |
| **Desperation** | Maximum effort when near death |

### 5.4 From Stress/Arousal

| Behavior | Mechanism |
|----------|-----------|
| **Vigilance** | High stress increases reactivity |
| **Calm foraging** | Low stress allows focused resource gathering |
| **Panic cascades** | Stressed agents stress nearby agents |
| **Recovery periods** | Agents seek safety to reduce stress |

### 5.5 From RNN Memory

| Behavior | Mechanism |
|----------|-----------|
| **Pursuit persistence** | Continue chasing after target leaves vision |
| **Threat memory** | Avoid areas where damage was received |
| **Path integration** | Return to known resource locations |
| **Social recognition** | Different responses to familiar vs novel agents |

---

## 6. Configuration Parameters

### 6.1 New Settings

```python
# Neural Architecture
'NN_TYPE': 'FNN',                    # 'FNN' or 'RNN'
'NN_HIDDEN_SIZE': 8,                 # Hidden layer neurons
'NN_WEIGHT_INIT_STD': 0.3,           # Weight initialization std
'NN_RECURRENT_IDENTITY_BIAS': 0.1,   # Identity bias for RNN stability

# N-Step Memory
'N_STEP_MEMORY_ENABLED': False,      # Enable memory buffer
'N_STEP_MEMORY_DEPTH': 2,            # Number of past states to store

# Sensing
'SECTOR_COUNT': 5,                   # Number of angular sectors
'VISION_NOISE_STD': 0.05,            # Noise added to sensor inputs

# Internal State
'STRESS_GAIN_RATE': 0.5,             # Stress accumulation rate
'STRESS_DECAY_RATE': 0.2,            # Stress natural decay rate
'STRESS_THREAT_WEIGHT': 1.0,         # Weight for nearby threats
'STRESS_RESOURCE_WEIGHT': 0.5,       # Weight for low resources

# Effort System
'EFFORT_SPEED_SCALE': 1.0,           # How much effort affects speed
'EFFORT_DAMAGE_SCALE': 0.5,          # How much effort affects damage
'EFFORT_ENERGY_SCALE': 1.5,          # How much effort affects energy cost
```

### 6.2 Genome Updates

```python
# Chromosome allocation for 318 RNN weights:
BRAIN_GENES = [
    # Chromosome 4: Input→Hidden weights 0-79
    [f'brain_w{i}' for i in range(0, 80)],
    # Chromosome 5: Input→Hidden weights 80-159
    [f'brain_w{i}' for i in range(80, 160)],
    # Chromosome 6: Input→Hidden 160-191 + Recurrent 0-47
    [f'brain_w{i}' for i in range(160, 208)],
    # Chromosome 7: Recurrent 48-63 + Biases + Output weights
    [f'brain_w{i}' for i in range(208, 318)],
]
```

---

## 7. Trade-offs and Considerations

### 7.1 Computational Cost

| Feature | Impact | Mitigation |
|---------|--------|------------|
| Sector sensing | O(entities × sectors) per agent | Spatial grid acceleration |
| N-step memory | +n×hidden_size inputs | Limit to n≤2 |
| Larger hidden layer | More weights to evolve | Start with 8, can reduce |

### 7.2 Evolutionary Pressure

| Feature | Pressure | Expected Outcome |
|---------|----------|------------------|
| Effort system | Penalizes constant high effort | Energy-efficient behaviors |
| Stress decay | Rewards safe behaviors | Territory/shelter emergence |
| Sector sensing | Rewards spatial awareness | Predator/prey strategies |

### 7.3 Backward Compatibility

The new architecture is **not** backward compatible with saved genomes from the old system. A migration script or fresh start is required.

---

## 8. Implementation Checklist

- [ ] Update `src/nn/brain.py` - New FNN architecture (24→8→6)
- [ ] Update `src/nn/rnn_brain.py` - New RNN architecture with improvements
- [ ] Update `src/nn/brain_phenotype.py` - New weight extraction
- [ ] Update `src/genetics/genome.py` - New gene layout
- [ ] Create `src/systems/sensing.py` - Sector-based input computation
- [ ] Update `src/entities/agent.py` - Add stress, velocity, memory buffer
- [ ] Update `src/systems/movement.py` - Use new inputs/outputs
- [ ] Update `src/systems/combat.py` - Use decoupled drives
- [ ] Update `src/systems/energy.py` - Effort-scaled costs
- [x] Update `config.py` and `settings.py` - New parameters
- [ ] Update `src/rendering/menu_G/` - Visualize new architecture
- [ ] Update `docs/DOCUMENTATION.md` - Document changes

---

## 9. Advanced Features (Optional)

All advanced features are disabled by default and can be enabled individually through settings. They provide more realistic embodied behaviors while keeping complexity manageable.

### 9.1 Body Size Effects

**Setting**: `ADVANCED_SIZE_EFFECTS_ENABLED`

Makes body size a first-class trait with meaningful trade-offs:

| Effect | Formula | Range |
|--------|---------|-------|
| Attack strength | 0.5 + 1.5 × (size_norm ^ SIZE_ATTACK_SCALING) | 0.5 to 2.0 |
| Speed penalty | 1.0 - size_norm × SIZE_SPEED_PENALTY | 0.7 to 1.0 |
| Turn rate penalty | 1.0 - size_norm × SIZE_TURN_PENALTY | 0.6 to 1.0 |
| Metabolic cost | 0.7 + 0.6 × (size_norm ^ SIZE_METABOLIC_SCALING) | 0.7 to 1.3 |
| Perception range | 1.0 + size_norm × SIZE_PERCEPTION_BONUS | 1.0 to 1.1 |

**Parameters**:
- `SIZE_ATTACK_SCALING`: 1.5 (exponent for attack strength)
- `SIZE_SPEED_PENALTY`: 0.3 (max speed reduction for largest agents)
- `SIZE_TURN_PENALTY`: 0.4 (max turn rate reduction)
- `SIZE_METABOLIC_SCALING`: 1.3 (exponent for metabolic cost)
- `SIZE_PERCEPTION_BONUS`: 0.1 (perception range increase)

### 9.2 Superlinear Energy Scaling

**Setting**: `SUPERLINEAR_ENERGY_SCALING` (default: True)

Larger agents pay superlinear energy costs:

```python
size_factor = (size / 6.0) ** ENERGY_SIZE_EXPONENT
base_cost *= size_factor

# Effort amplifies size cost
base_cost *= (1.0 + effort * EFFORT_SIZE_INTERACTION * (size / 6.0 - 1.0))
```

**Parameters**:
- `ENERGY_SIZE_EXPONENT`: 1.4
- `EFFORT_SIZE_INTERACTION`: 0.5

### 9.3 Age-Dependent Modulation

**Setting**: `AGE_EFFECTS_ENABLED`

Implements life-history stages:

| Stage | Age Ratio | Speed | Stamina | Experience | Reproduction |
|-------|-----------|-------|---------|------------|--------------|
| Young | 0.0 - 0.2 | 70-100% | 70-100% | 80-100% | 50-100% |
| Prime | 0.2 - 0.6 | 100% | 100% | 100-120% | 100% |
| Old | 0.6 - 1.0 | 70-100% | 60-100% | 116% | 40-100% |

**Parameters**:
- `AGE_PRIME_START`: 0.2 (when prime begins)
- `AGE_PRIME_END`: 0.6 (when prime ends)
- `AGE_SPEED_DECLINE`: 0.3 (max speed reduction in old age)
- `AGE_STAMINA_DECLINE`: 0.4 (max stamina reduction in old age)
- `AGE_EXPERIENCE_BONUS`: 0.2 (combat bonus from experience)
- `AGE_REPRODUCTION_CURVE`: True (fertility varies with age)

### 9.4 Internal State Modulation

**Setting**: `INTERNAL_STATE_MODULATION_ENABLED`

Soft penalties based on resource levels:

| Condition | Effect |
|-----------|--------|
| Energy < 20% | Attack effectiveness reduced to 50-100% |
| Hydration < 30% | Speed reduced by up to 30% |
| Energy < 20% | Effort capacity reduced to 50-100% |
| High stress | Short-term effort boost (fight-or-flight) |

**Parameters**:
- `LOW_ENERGY_ATTACK_PENALTY`: 0.5
- `LOW_HYDRATION_SPEED_PENALTY`: 0.3
- `HIGH_STRESS_EFFORT_BOOST`: 0.2
- `EXHAUSTION_THRESHOLD`: 0.2

### 9.5 Action-Specific Cost Asymmetry

**Setting**: `ACTION_COSTS_ENABLED`

Different actions have different energy costs:

| Action | Multiplier | Description |
|--------|------------|-------------|
| High speed | 1.5 | Moving at >80% max speed |
| Sharp turn | 1.3 | Sudden direction changes |
| Pursuit | 1.2 | Sustained chasing |
| Attack | 3.0 | Combat actions |
| Mating | 5.0 | Reproduction attempts |
| Idle | 0.7 | Stationary/slow movement |

**Parameters**:
- `COST_HIGH_SPEED_MULTIPLIER`: 1.5
- `COST_SHARP_TURN_MULTIPLIER`: 1.3
- `COST_PURSUIT_MULTIPLIER`: 1.2
- `COST_ATTACK_BASE`: 3.0
- `COST_MATING_BASE`: 5.0

### 9.6 Morphological Trade-offs

**Setting**: `MORPHOLOGY_TRAITS_ENABLED`

Two new evolvable traits:

**Agility** (0-1):
- Turn rate: +40% at max agility
- Acceleration: +20% at max agility
- Metabolic cost: +20% at max agility

**Armor** (0-1):
- Damage reduction: up to 40% at max armor
- Speed penalty: up to 30% at max armor
- Metabolic cost: +15% at max armor

**Parameters**:
- `AGILITY_SPEED_BONUS`: 0.4
- `AGILITY_STAMINA_COST`: 0.2
- `ARMOR_DAMAGE_REDUCTION`: 0.4
- `ARMOR_SPEED_PENALTY`: 0.3
- `ARMOR_ENERGY_COST`: 0.15

### 9.7 Sensory Imperfection

**Setting**: `SENSORY_NOISE_ENABLED` (default: True)

Adds realistic perception limitations:

| Effect | Description |
|--------|-------------|
| Gaussian noise | VISION_NOISE_STD added to sector signals |
| Sensor dropout | SENSOR_DROPOUT_RATE chance of missing detections |
| Internal noise | INTERNAL_STATE_NOISE on energy/hydration perception |

**Parameters**:
- `VISION_NOISE_STD`: 0.05
- `SENSOR_DROPOUT_RATE`: 0.05
- `INTERNAL_STATE_NOISE`: 0.03
- `PERCEPTION_LAG`: 0.0 (optional delay)

### 9.8 Context Signals

**Setting**: `CONTEXT_SIGNALS_ENABLED`

Adds 3 additional NN inputs (bringing total to 27):

| Input | Name | Description |
|-------|------|-------------|
| 24 | `hunger_signal` | Time since last food / decay time |
| 25 | `safety_signal` | Time since last damage / decay time |
| 26 | `mating_signal` | Time since last mating / decay time |

These signals decay over time and reset when the relevant event occurs.

**Parameters**:
- `TIME_SINCE_FOOD_DECAY`: 10.0 seconds
- `TIME_SINCE_DAMAGE_DECAY`: 15.0 seconds
- `TIME_SINCE_MATING_DECAY`: 20.0 seconds

### 9.9 Social Pressure Effects

**Setting**: `SOCIAL_PRESSURE_ENABLED` (default: True)

Crowding and dominance affect stress:

```python
# Crowding stress
if nearby_count > CROWD_STRESS_THRESHOLD:
    stress += (nearby_count - threshold) * CROWD_STRESS_RATE

# Dominance stress
for neighbor in nearby:
    if neighbor.threat_level > own_threat * 1.2:
        stress += (threat_ratio - 1.0) * DOMINANCE_STRESS_FACTOR
```

**Parameters**:
- `CROWD_STRESS_RADIUS`: 50.0
- `CROWD_STRESS_THRESHOLD`: 3
- `CROWD_STRESS_RATE`: 0.1
- `DOMINANCE_STRESS_FACTOR`: 0.5

---

## 10. Modifier Combination

All modifiers are combined multiplicatively in `compute_combined_modifiers()`:

```python
effective_speed = (
    size_modifier.speed *
    age_modifier.speed *
    state_modifier.speed *
    morphology_modifier.speed
)

effective_attack = (
    size_modifier.attack *
    age_modifier.experience *
    state_modifier.attack
)

effective_metabolism = (
    size_modifier.metabolic *
    morphology_modifier.metabolic
)

effective_effort_capacity = (
    state_modifier.effort_capacity *
    age_modifier.stamina
)
```

These modifiers are stored on `agent.current_modifiers` and used by movement, combat, and energy systems.
