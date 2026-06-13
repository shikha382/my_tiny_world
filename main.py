# /// script
# dependencies = [
#   "pygame-ce",
#   "numpy",
# ]
# ///
import pygame
import math
import csv
import asyncio
import numpy

from creature import (
    spawn_creature,
    spawn_food,
    create_next_generation,
    update_creatures,
    apply_energy_and_collect_dead,
    handle_creature_eating,
    best_creatures,
    NUM_CREATURES,
    CREATURE_RADIUS,
    INITIAL_ENERGY,
    ENERGY_LOSS_PER_SECOND,
    MAX_ENERGY,
    TOP_BRAINS,
)

from predator import (
    create_predator,
    next_generation_predator,
    update_predator,
    apply_energy_and_collect_dead_predator,
    handle_predator_eating,
    best_predators,
    PREDATOR_COUNT ,
    PREDATOR_RADIUS ,
    PREDATOR_INITIAL_ENERGY ,
    PREDATOR_ENERGY_LOSS_PER_SECOND,
    PREDATOR_MAX_ENERGY,
    PREDATOR_TOP_BRAINS
)

NEON_BG = (9, 12, 26)
CYAN = (80, 255, 230)
PINK = (255, 70, 160)
LIME = (175, 255, 80)
GOLD = (255, 215, 85)
RED = (255, 65, 75)

pygame.init()

WIDTH, HEIGHT = 1280, 700
NUM_FOOD = 20
GENERATION_TIME = 30
TARGET_FPS = 45
SHOW_VISION_CONES = False
SHOW_ENERGY_LABELS = False
HUD_REFRESH_SECONDS = 0.25

def mix_color(a, b, amount):
    return tuple(int(a[i] + (b[i] - a[i]) * amount) for i in range(3))


def creature_color(creature):
    energy_ratio = max(0, min(1, creature["energy"] / MAX_ENERGY))
    return mix_color(PINK, CYAN, energy_ratio)

# def draw_creatures(screen, creatures):
#     color=creature_color(creatures)
#     x = int(creatures["x"])
#     y = int(creatures["y"])
#     pygame.draw.circle(screen, color, (x, y), CREATURE_RADIUS)

def draw_background(surface):
    surface.fill(NEON_BG)
    for y in range(0, HEIGHT, 40):
        shade = 22 + (y // 40) % 2 * 8
        pygame.draw.line(surface, (shade, 26, 58), (0, y), (WIDTH, y), 1)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, (18, 46, 66), (x, 0), (x, HEIGHT), 1)

def draw_food(surface, food):
    x, y = food
    pygame.draw.circle(surface, mix_color(LIME, NEON_BG, 0.65), (x, y), 10)
    pygame.draw.circle(surface, LIME, (x, y), 5)


def draw_vision_cone(surface, creature):
    vision_range = 100
    half_angle = math.radians(32)
    angle = creature["angle"]
    origin = (int(creature["x"]), int(creature["y"]))
    left = (
        int(creature["x"] + math.cos(angle - half_angle) * vision_range),
        int(creature["y"] + math.sin(angle - half_angle) * vision_range),
    )
    right = (
        int(creature["x"] + math.cos(angle + half_angle) * vision_range),
        int(creature["y"] + math.sin(angle + half_angle) * vision_range),
    )

    cone_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(cone_layer, (90, 255, 230, 24), [origin, left, right])
    surface.blit(cone_layer, (0, 0))


async def main():
    global TOP_BRAINS, PREDATOR_TOP_BRAINS
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Creature Evolution")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    background = pygame.Surface((WIDTH, HEIGHT)).convert()
    draw_background(background)
    hud_surfaces = []
    hud_timer = HUD_REFRESH_SECONDS
    generation_timer = 0
    generation = 1

    creatures = [spawn_creature(WIDTH, HEIGHT, INITIAL_ENERGY) for _ in range(NUM_CREATURES)]
    dead_creatures = []
    food_list = [spawn_food(WIDTH,HEIGHT) for _ in range(NUM_FOOD)]
    ################# predator ####################
    predators = [create_predator(WIDTH,HEIGHT,PREDATOR_INITIAL_ENERGY) for _ in range(PREDATOR_COUNT)]
    dead_predators =[]

    # Initialize CSV for recording performances
    try:
        with open('creature_performances.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Generation", "Average_Performance"])
    except OSError:
        pass

    try:
        with open('predator_performances.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Generation", "Average_Performance"])
    except OSError:
        pass

    running = True
    while running:
        dt = min(clock.tick(TARGET_FPS) / 1000, 0.05)
        generation_timer += dt

        if len(creatures) == 0 or generation_timer >= GENERATION_TIME:
            generation += 1
            generation_timer = 0
            old_creatures = creatures + dead_creatures
            for creature in old_creatures:
                creature['performance'] += creature['survival_time']*0.16 - creature['fear']
            
            TOP_BRAINS = best_creatures(old_creatures,TOP_BRAINS)
            
            # Calculate and write the average performance of creatures for this generation
            avg_creature_perf = sum(c['performance'] for c in old_creatures) / len(old_creatures) if old_creatures else 0
            try:
                with open('creature_performances.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([generation - 1, avg_creature_perf])
            except OSError:
                pass

            creatures = create_next_generation(
                TOP_BRAINS, NUM_CREATURES, WIDTH, HEIGHT, INITIAL_ENERGY
            )
            dead_creatures = []
            #################### predator ################################
            for pred in predators:
                pred['performance'] +=pred['catch']
            old_predators = predators + dead_predators
            
            PREDATOR_TOP_BRAINS = best_predators(old_predators,PREDATOR_TOP_BRAINS)
            
            # Calculate and write the average performance of predators for this generation
            avg_predator_perf = sum(p['performance'] for p in old_predators) / len(old_predators) if old_predators else 0
            try:
                with open('predator_performances.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([generation - 1, avg_predator_perf])
            except OSError:
                pass
                    
            predators = next_generation_predator(PREDATOR_TOP_BRAINS,PREDATOR_COUNT,WIDTH, HEIGHT,
                                                  PREDATOR_INITIAL_ENERGY )
            dead_predators=[]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_creatures(creatures, food_list,predators ,WIDTH, HEIGHT, CREATURE_RADIUS,dt)
        apply_energy_and_collect_dead(creatures, dead_creatures, ENERGY_LOSS_PER_SECOND, dt)
        handle_creature_eating(
            creatures, food_list, CREATURE_RADIUS, spawn_food, max_energy=MAX_ENERGY
        )
        ######################### predator ##############################

        update_predator(predators, creatures, WIDTH, HEIGHT, PREDATOR_RADIUS,dt)
        apply_energy_and_collect_dead_predator(predators, dead_predators, PREDATOR_ENERGY_LOSS_PER_SECOND, dt)
        handle_predator_eating(
            predators, creatures,dead_creatures, PREDATOR_RADIUS,  max_energy=PREDATOR_MAX_ENERGY)

        screen.blit(background, (0, 0))

        for food in food_list:
            draw_food(screen, food)

        for creature in creatures:
            if SHOW_VISION_CONES:
                draw_vision_cone(screen, creature)
            pygame.draw.circle(
                screen,
                creature_color(creature),
                (int(creature["x"]), int(creature["y"])),
                CREATURE_RADIUS,
            )

            if SHOW_ENERGY_LABELS:
                energy_text = font.render(str(int(creature["energy"])), True, (255, 255, 255))
                screen.blit(energy_text, (creature["x"], creature["y"] - 20))
        ##################### predator #######################
        for predator in predators:
            pygame.draw.circle(screen,(255, 0, 0),
                (int(predator["x"]), int(predator["y"])),
                PREDATOR_RADIUS,
            )
           

        hud_timer += dt
        if hud_timer >= HUD_REFRESH_SECONDS:
            total_score = sum(c["score"] for c in creatures)
            best_score = max((c["score"] for c in creatures), default=0)
            hud_surfaces = [
                (font.render(f"Total Food Eaten: {total_score}", True, (255, 255, 255)), (10, 10)),
                (font.render(f"Best Score: {best_score}", True, (255, 255, 0)), (10, 40)),
                (font.render(f"Creatures Alive: {len(creatures)}", True, (200, 200, 255)), (10, 70)),
                (font.render(f"Generation: {generation}", True, (180, 255, 180)), (10, 100)),
            ]
            hud_timer = 0

        for hud_surface, hud_pos in hud_surfaces:
            screen.blit(hud_surface, hud_pos)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
