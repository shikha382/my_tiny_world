# Product Requirements Document (PRD): Creature Lab

## 1. Product Overview
**Creature Lab** is an interactive, multi-agent artificial life simulation developed in Python. It provides a visual environment where simple software agents (Creatures and Predators) learn to survive and thrive over multiple generations using evolutionary algorithms and neural networks. Through the process of natural selection, these randomly acting entities gradually acquire complex, emergent behaviors such as foraging for food, fleeing from threats, and actively hunting prey.

## 2. Goals & Objectives
### Primary Goals
- **Simulate Evolution:** Provide a robust simulation demonstrating natural selection, mutation, and inheritance in artificial agents.
- **Emergent Behavior:** Allow agents to develop complex survival strategies entirely from scratch without hard-coded state machines.

### Secondary Goals
- **Data Visualization:** Include real-time metrics tracking total food eaten, generation count, and current population.
- **Extensibility:** Serve as a foundation for further machine learning experiments.

## 3. Target Audience
- **Educators and Students:** Seeking visual and interactive examples of Genetic Algorithms (GAs) and Neural Networks.
- **AI Enthusiasts & Researchers:** Interested in multi-agent reinforcement learning or evolutionary simulations.
- **Hobbyists:** Enjoying "zero-player games" and artificial life sandboxes.

## 4. Product Features

### 4.1. The Environment
- A continuous 2D plane with configurable screen dimensions (default 1280x700).
- Implements a stylized "Neon" aesthetic with vision cone overlays for the creatures.
- Continuous spawning of a set amount of food particles.

### 4.2. Creatures (Prey)
- **Objective:** Survive as long as possible and consume food.
- **Sensory Inputs:** Can "see" food locations, predator locations, and their own energy levels.
- **Metabolism:** Starts with an initial energy pool that depletes continuously over time. Eating food replenishes energy.
- **Death:** Occurs when energy drops below 0 or when intercepted by a Predator.
- **Neural Brain:** Driven by a multi-layer neural network evaluating sensory inputs to produce turn/movement outputs.

### 4.3. Predators
- **Objective:** Track and consume Creatures.
- **Sensory Inputs:** Can "see" nearby Creatures.
- **Metabolism:** Has a separate energy decay timer and requires eating Creatures to maintain energy.
- **Evolution:** Operates on an independent evolutionary track from the Creatures (co-evolution system).

### 4.4. The Evolutionary Cycle
- **Generations:** A generation ends after a fixed time limit or when all Creatures have died.
- **Fitness Evaluation:** Agents are scored based on survival time, food consumption, and successful predator evasion (-fear factor).
- **Reproduction:** The top-performing agents ("Top Brains") are selected; their neural weights are cloned and randomly mutated to form the next generation.

### 4.5. Analytics & Export
- Logs average performance metrics for both Creatures and Predators per generation.
- Automatically exports to `.csv` files (`creature_performances.csv` and `predator_performances.csv`) for post-simulation analysis.

## 5. Non-Functional Requirements
- **Performance:** Maintain a steady 60 FPS under a standard load of ~20 Creatures, 20 Food entities, and a set number of Predators.
- **Language Stack:** Python 3.x using `pygame` for rendering/game loop and `numpy` for efficient neural network matrix multiplication.
- **Cross-Platform:** Usable on Windows, macOS, and Linux without native system dependencies beyond Python.

## 6. Future Enhancements (Roadmap)
- Interactive UI to tweak mutation rate, population size, and simulation speed on the fly.
- Saving and loading of specific "Brain" profiles (models) to resume evolved states.
- Implementation of flocking mechanics or communication between agents.
