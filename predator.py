import math
import random
import numpy as np

from predator_brain import Brain

PREDATOR_COUNT = 4
PREDATOR_RADIUS = 15
PREDATOR_INITIAL_ENERGY = 25
PREDATOR_ENERGY_LOSS_PER_SECOND = 1
PREDATOR_MAX_ENERGY = 80
PREDATOR_SPEED = 3
PREDATOR_EAT_GAIN = 4
PREDATOR_TOP_BRAINS = []


def create_predator(width, height, initial_energy=PREDATOR_INITIAL_ENERGY):
    return {
        "x": random.randint(10, width - 10),
        "y": random.randint(10, height - 10),
        "angle": random.uniform(0, 2 * math.pi),
        "speed": PREDATOR_SPEED,
        "performance": 0,
        "energy": initial_energy,
        "catch":0,
        "brain": Brain(),
    }


def next_generation_predator(
    old_predators,
    num_predators=PREDATOR_COUNT,
    width=1280,
    height=700,
    initial_energy=PREDATOR_INITIAL_ENERGY,
):
    old_predators = list(old_predators)
    old_predators.sort(key=lambda p: p["performance"], reverse=True)
    parents = old_predators[:3]

    if not parents:
        return [create_predator(width, height, initial_energy) for _ in range(num_predators)]

    new_predators = []
    for _ in range(num_predators):
        parent = random.choice(parents)
        child = create_predator(width, height, initial_energy)
        child["brain"] = parent["brain"].copy()
        child["brain"].mutate(rate=0.5, strength=0.1)
        new_predators.append(child)
    return new_predators


def update_predator(predators, prey_creatures, width, height, predator_radius,dt):
    for predator in predators:
        if not prey_creatures:
            predator["angle"] += random.uniform(-0.1, 0.1)
            predator["x"] += math.cos(predator["angle"]) * predator["speed"] * 0.4
            predator["y"] += math.sin(predator["angle"]) * predator["speed"] * 0.4
        else:
            nearest_dist = float("inf")
            target_dx, target_dy = 0, 0

            for prey in prey_creatures:
                dx = prey["x"] - predator["x"]
                dy = prey["y"] - predator["y"]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < nearest_dist:
                    nearest_dist = dist
                    target_dx = dx
                    target_dy = dy

            target_angle = math.atan2(target_dy, target_dx)
            angle_diff = (target_angle - predator["angle"] + math.pi) % (2 * math.pi) - math.pi
            dist_norm = nearest_dist / math.sqrt(width * width + height * height)
            if nearest_dist <180:
                catch= (180 - nearest_dist) / 180
                health_ratio = min(2, PREDATOR_INITIAL_ENERGY / max(1, predator["energy"]))
                predator["catch"] += catch * health_ratio * dt * 0.8

            x_center = (predator["x"] - width / 2) / (width / 2)
            y_center = (predator["y"] - height / 2) / (height / 2)

            inputs = np.array(
                [
                    math.cos(angle_diff),
                    math.sin(angle_diff),
                    dist_norm,
                    predator["energy"] / PREDATOR_INITIAL_ENERGY,
                    x_center,
                    y_center,
                ]
            )

            outputs = predator["brain"].think(inputs)
            turn = outputs[0]
            move =0.3+ 0.7*(outputs[1] + 1) / 2

            predator["angle"] += turn * 0.1
            speed_mult = 1.8 if nearest_dist < 180 else 1.0
            predator["x"] += math.cos(predator["angle"]) * move * predator["speed"] * speed_mult
            predator["y"] += math.sin(predator["angle"]) * move * predator["speed"] * speed_mult

        if predator["x"] < predator_radius:
            predator["x"] = predator_radius
            predator["angle"] = math.pi - predator["angle"] + random.uniform(-0.25, 0.25)
        elif predator["x"] > width - predator_radius:
            predator["x"] = width - predator_radius
            predator["angle"] = math.pi - predator["angle"] + random.uniform(-0.25, 0.25)

        if predator["y"] < predator_radius:
            predator["y"] = predator_radius
            predator["angle"] = -predator["angle"] + random.uniform(-0.25, 0.25)
        elif predator["y"] > height - predator_radius:
            predator["y"] = height - predator_radius
            predator["angle"] = -predator["angle"] + random.uniform(-0.25, 0.25)

        predator["x"] = max(predator_radius, min(width - predator_radius, predator["x"]))
        predator["y"] = max(predator_radius, min(height - predator_radius, predator["y"]))


def apply_energy_and_collect_dead_predator(predators, dead_predators, energy_loss_per_second, dt):
    for predator in predators[:]:
        predator["energy"] -= energy_loss_per_second * dt
        if predator["energy"] <= 0:
            predator['performance'] += predator['catch']
            dead_predators.append(predator)
            predators.remove(predator)


def handle_predator_eating(predators, prey_creatures,dead_creature, predator_radius, max_energy=None):
    for predator in predators:
        for prey in prey_creatures[:]:
            distance = math.sqrt((predator["x"] - prey["x"]) ** 2 + (predator["y"] - prey["y"]) ** 2)
            if distance < predator_radius + 10:
                predator["energy"] += PREDATOR_EAT_GAIN
                if max_energy is not None:
                    predator["energy"] = min(max_energy, predator["energy"])
                predator["performance"] += 1
                prey['performance'] -= prey['performance'] * 0.3  # Moderate penalty for getting eaten
                dead_creature.append(prey)
                prey_creatures.remove(prey)

def best_predators(old_predators,top_brain):
    total_predators = old_predators + top_brain
    total_predators.sort(key=lambda c: c["performance"], reverse=True)
    return total_predators[:3]