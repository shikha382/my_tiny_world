import math
import random
import numpy as np

from creature_brain import Brain

WIDTH, HEIGHT = 1280, 700
NUM_CREATURES = 20
CREATURE_RADIUS = 10
INITIAL_ENERGY = 30
ENERGY_LOSS_PER_SECOND = 1
MAX_ENERGY = 150
FOOD_ENERGY=10
TOP_BRAINS =[]


def spawn_creature(width, height, initial_energy=INITIAL_ENERGY):
    return {
        "x": random.randint(50, width - 50),
        "y": random.randint(50, height - 50),
        "angle": random.uniform(0, 2 * math.pi),
        "speed": 2.7,
        "score": 0,
        "performance":0,
        "survival_time":0,
        "energy": initial_energy,
        "fear":0,
        "brain": Brain(),
    }


def create_next_generation(
    top_brains,  
    num_creatures=NUM_CREATURES,
    width=1280,
    height=700,
    initial_energy=INITIAL_ENERGY,
):
    

    if not top_brains:
        return [spawn_creature(width, height, initial_energy) for _ in range(num_creatures)]

    new_creatures = []
    for _ in range(num_creatures-1):
        parent = random.choice(top_brains)
        child = spawn_creature(width, height, initial_energy)
        child["brain"] = parent["brain"].copy()
        child["brain"].mutate(rate=0.5, strength=0.1)
        new_creatures.append(child)
    best_parent = top_brains[0]
    elite = spawn_creature(width, height, initial_energy)
    elite["brain"] = best_parent["brain"].copy()
    new_creatures.append(elite)
    
    return new_creatures


def update_creatures(creatures, food_list,predators, width, height, creature_radius,dt):
    max_dist = math.sqrt(width * width + height * height)
    for creature in creatures:
        nearest_dist_sq = float("inf")
        food_dx, food_dy = 0, 0

        for food in food_list:
            dx = food[0] - creature["x"]
            dy = food[1] - creature["y"]
            dist_sq = dx * dx + dy * dy
            if dist_sq < nearest_dist_sq:
                nearest_dist_sq = dist_sq
                food_dx = dx
                food_dy = dy

        nearest_dist = math.sqrt(nearest_dist_sq)
        target_angle = math.atan2(food_dy, food_dx)
        angle_diff = (target_angle - creature["angle"] + math.pi) % (2 * math.pi) - math.pi
        dist_norm = nearest_dist / max_dist
        x_center = (creature["x"] - width / 2) / (width / 2)
        y_center = (creature["y"] - height / 2) / (height / 2)

        predator_dx=predator_dy=0
        predator_dist_sq = width * width + height * height
        for predator in predators:
            dx = predator['x'] - creature["x"]
            dy = predator['y'] - creature["y"]
            dist_sq = dx * dx + dy * dy
            if dist_sq < predator_dist_sq:
                predator_dist_sq = dist_sq
                predator_dx = dx
                predator_dy = dy

        predator_dist = math.sqrt(predator_dist_sq)
        predator_angle = math.atan2(predator_dy, predator_dx)
        predator_angle_diff = (predator_angle - creature["angle"] + math.pi) % (2 * math.pi) - math.pi
        predator_dist_norm = predator_dist / max_dist
        
        # Increase fear radius and penalty for high energy creatures
        if predator_dist < 200:
            danger = (200 - predator_dist) / 200
            health_ratio = (creature["energy"] / INITIAL_ENERGY) * 2
            creature["fear"] += danger * health_ratio * dt * 3.0
            

        inputs = np.array(
               [math.cos(predator_angle_diff),
                math.sin(predator_angle_diff),
                predator_dist_norm,

                math.cos(angle_diff),
                math.sin(angle_diff),
                dist_norm,
                creature["energy"] / MAX_ENERGY,
                x_center,
                y_center,
            ]
        )

        outputs = creature["brain"].think(inputs)
        turn = outputs[0]
        move = 0.3 +0.7*(outputs[1] + 1) / 2

        creature["angle"] += turn * 0.12
        speed_mult = 1.8 if (predator_dist < 200 or nearest_dist < 150) else 1.0
        creature["x"] += math.cos(creature["angle"]) * move * creature["speed"] * speed_mult
        creature["y"] += math.sin(creature["angle"]) * move * creature["speed"] * speed_mult

        if creature["x"] < creature_radius:
            creature["x"] = creature_radius
            creature["angle"] = math.pi - creature["angle"] + random.uniform(-0.25, 0.25)
        elif creature["x"] > width - creature_radius:
            creature["x"] = width - creature_radius
            creature["angle"] = math.pi - creature["angle"] + random.uniform(-0.25, 0.25)

        if creature["y"] < creature_radius:
            creature["y"] = creature_radius
            creature["angle"] = -creature["angle"] + random.uniform(-0.25, 0.25)
        elif creature["y"] > height - creature_radius:
            creature["y"] = height - creature_radius
            creature["angle"] = -creature["angle"] + random.uniform(-0.25, 0.25)

        creature["x"] = max(creature_radius, min(width - creature_radius, creature["x"]))
        creature["y"] = max(creature_radius, min(height - creature_radius, creature["y"]))


def apply_energy_and_collect_dead(creatures, dead_creatures, energy_loss_per_second, dt):
    for creature in creatures[:]:
        creature["energy"] -= energy_loss_per_second * dt
        creature['survival_time'] +=dt  
        if creature["energy"] <= 0:
            dead_creatures.append(creature)
            creatures.remove(creature)


def handle_creature_eating(creatures, food_list, creature_radius, spawn_food, max_energy=None):
    eat_distance_sq = (creature_radius + 10) ** 2
    for creature in creatures:
        for food in food_list[:]:
            dx = creature["x"] - food[0]
            dy = creature["y"] - food[1]
            if dx * dx + dy * dy < eat_distance_sq:
                creature["energy"] += FOOD_ENERGY
                if max_energy is not None:
                    creature["energy"] = min(max_energy, creature["energy"])
                creature["score"] += 2
                creature['performance'] +=2
                food_list.remove(food)
                food_list.append(spawn_food(WIDTH,HEIGHT))

def spawn_food(WIDTH,HEIGHT):
    return [random.randint(20, WIDTH - 20), random.randint(20, HEIGHT - 20)]

def best_creatures(old_creatures,top_brain):
    total_creatures = old_creatures + top_brain
    total_creatures.sort(key=lambda c: c["performance"], reverse=True)
    return total_creatures[:5]
