# Technical Requirements Document (TRD): Creature Lab

## 1. System Architecture
Creature Lab relies on a standard Game Loop architecture powered by `pygame`, layered over a custom-built Neural Network / Genetic Algorithm pipeline handled primarily via `numpy` for efficiency.

**High-Level Flow:**
1. **Initialization:** Pygame setup, generation of initial agents (Creatures, Predators) and Food.
2. **Input Processing:** Handle window events (quit, pause).
3. **Simulation Computation:**
   - Update sensors for all agents.
   - Run forward pass on all agent Brains (`numpy` matrix multiplication).
   - Update physical positions.
   - Calculate collisions (eating food, getting eaten).
   - Apply metabolic decay.
4. **Genetic Pipeline (Triggered per Generation):**
   - Evaluate fitness.
   - Sort and slice the top performing brains.
   - Replicate and mutate weights.
   - Reset simulation plane.
5. **Rendering:** Draw background, entities, UI overlays, and `pygame.display.flip()`.

## 2. Technology Stack
- **Core Language:** Python 3.x
- **Rendering & Inputs:** `pygame` (2D rendering engine)
- **Math & Neural Networks:** `numpy` (Handling weights, biases, and forward-pass calculations)
- **Data Persistence:** Built-in `csv` module (Logging performance data)

## 3. Data Models / Entities

### 3.1. Creature/Predator Structure
Entities are represented as Python dictionaries containing their physical state, coupled with a `Brain` object.
```python
{
    "x": float,
    "y": float,
    "angle": float,
    "speed": float,
    "score": int,
    "performance": float,
    "survival_time": float,
    "energy": float,
    "brain": Brain()
}
```

### 3.2. Biological Brain Model (Neural Network)
The `Brain` class manages the neural structures. 
- **Initialization:** Matrices for Weights and Biases initialized randomly via a normal distribution.
- **Forward Pass:** Input Vector -> **Dense Layer** -> **Activation** (e.g., Tanh/Sigmoid) -> **Output Layer** -> **Actions** (Accelerate/Decelerate, Turn Left/Right).
- **Mutation Logic:** Iterates over numpy weight arrays and adds Gaussian noise (`np.random.normal`) scaled by mutation strength and rate to a subset of weights.

## 4. Subsystem Details

### 4.1. Collision & Sensing (Environment Physics)
- Uses continuous 2D Euclidean distance calculations ($math.dist(p1, p2)$).
- **Vision:** Implemented via raycasting/angle checking relative to the agent's facing angle and field-of-view radius. 
- Screen wrapping vs Bounding Box: Handled in the positional update step to ensure agents do not exit the bounds.

### 4.2. Fitness Function & Selection Algorithm
At the generation tick (triggered by total population death or time limit $t > GENERATION\_TIME$):
1. **Creature Fitness:** $F_c = \Sigma(C\_{score}) + (C\_{survival\_time} * 0.16) - C\_{fear}$
2. **Predator Fitness:** $F_p = \Sigma(P\_{catch})$
3. **Elitism/Selection:** The simulation aggregates the entire generation (including dead agents), sorts by fitness, and extracts `TOP_BRAINS`.
4. **Reproduction:** New agents are spawned. One agent directly inherits the exact top brain (Elitism), while the rest receive a deep copy (`copy.deepcopy` equivalent) of a randomly chosen top brain, followed by `brain.mutate()`.

## 5. Performance and Constraints
- **Algorithmic Complexity:** The $O(N \times (F + P))$ complexity in the `update_creatures` loops means performance scales linearly per agent but exponentially as agent interactions (Creature -> Food, Creature -> Predator) increase. 
- **Optimization Strategy:** 
  - Numpy handles the heavy lifting of the neural logic.
  - Using Pygame's basic drawing primitives for circles and alpha layers (for vision cones) instead of heavy texture loading.
- **Memory Footprint:** Very low. Brains consist of minimal matrices (typically < 100 parameters each).

## 6. Directory Structure
```text
creature_lab/
 ├── main.py                  # Entry point, game loop, rendering pipelines
 ├── creature.py              # Creature logic, fitness evaluation, bounding box
 ├── creature_brain.py        # Feed-forward Neural Network structure
 ├── predator.py              # Predator entity logic
 ├── predator_brain.py        # Deep NN logic for predator decision making
 ├── README.md                # General info
 ├── PRD.md                   # Product specs
 ├── TRD.md                   # Technical architectures
 └── *_performances.csv       # Telemetry files (auto-generated)
```