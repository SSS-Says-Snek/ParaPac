import pygame
import os
import sys
import time

import common
from world import World
from interrupt import *
from player import Player
from tiles import Tile


def setup():
    pygame.display.set_caption("ParaPac - Pygame Community Summer Team Jam")

    common.maps = [
        (World(os.path.join("maps", "map_a.txt")), (0, 32, 64), "map_a.txt"),
        (World(os.path.join("maps", "map_b.txt")), (64, 0, 0), "map_b.txt")
    ]

    common.player = Player(19, 29)
    common.active_map_id = 0
    common.active_map = common.maps[common.active_map_id][0]
    for dimension, _bg, _file in common.maps:
        dimension.entities.append(common.player)


def gameplay_events():
    pygame.display.flip()
    common.clock.tick(60)

    common.delta = time.perf_counter() - common.last_tick
    common.fps = 1 / common.delta
    common.last_tick = time.perf_counter()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameExit
        elif event.type == pygame.KEYDOWN:
            # Toggles debug mode
            if event.key == pygame.K_q:
                common.DEBUG = not common.DEBUG
            # Saves the map (Only in debug mode)
            elif event.key == pygame.K_z and common.DEBUG:
                with open(os.path.join("maps",
                                       common.maps[common.active_map_id][2]), "w") as f:
                    f.write(common.active_map.save())
            # Changes the map dimension
            elif event.key == pygame.K_p:
                common.transitioning_mode = "Fading"
                common.alpha = 255

    if common.DEBUG:
        mx, my = pygame.mouse.get_pos()
        left_click, middle_click, right_click = pygame.mouse.get_pressed(3)
        x, y = common.to_world_space(mx, my)
        if left_click:
            common.active_map.set_at(int(x), int(y), Tile.WALL)
        elif middle_click:
            common.active_map.set_at(int(x), int(y), Tile.POINT)
        elif right_click:
            common.active_map.set_at(int(x), int(y), Tile.AIR)


def gameplay_map():
    common.active_map.update()
    world = common.active_map.render()

    common.window.fill(common.maps[common.active_map_id][1])
    ratio = world.get_width() / world.get_height()
    if common.window.get_width() > ratio * common.window.get_height():
        common.map_area_width = int(ratio * common.window.get_height())
        common.map_area_height = int(common.window.get_height())
        common.map_area_x = (common.window.get_width() - common.map_area_width) // 2
        common.map_area_y = 0
    else:
        common.map_area_width = int(common.window.get_width())
        common.map_area_height = int(common.window.get_width() / ratio)
        common.map_area_x = 0
        common.map_area_y = (common.window.get_height() - common.map_area_height) // 2

    world = pygame.transform.scale(world, (common.map_area_width, common.map_area_height))

    if common.transitioning_mode != "Not Transitioning":
        world.set_alpha(common.alpha)
        if common.transitioning_mode == "Fading":
            common.alpha -= 5
        elif common.transitioning_mode == "Reappearing":
            common.alpha += 5

        if common.alpha < 0:
            common.transitioning_mode = "Reappearing"
            common.active_map_id = (common.active_map_id + 1) % len(common.maps)
            common.active_map = common.maps[common.active_map_id][0]

        if common.alpha == 255:
            common.transitioning_mode = "Not Transitioning"

    common.window.blit(world, (common.map_area_x, common.map_area_y))


def gameplay_loop():
    gameplay_events()
    gameplay_map()

    if common.DEBUG:
        common.window.blit(common.font.render(
            f"FPS: {int(common.fps)}",
            False, (255, 255, 255), (0, 0, 0)
        ), (0, 0))

    score_txt = common.font.render(
        f"Score: {str(common.score).zfill(6)}",
        False, (255, 255, 255)
    )
    score_txt_rect = score_txt.get_rect(right=common.window.get_width() - 30)
    common.window.blit(common.font.render(
        f"Score: {str(common.score).zfill(6)}",
        False, (255, 255, 255)
    ), score_txt_rect)


def main():
    while True:
        try:
            gameplay_loop()
        except GameExit:
            sys.exit(0)
        except GamePaused:
            pass
        except GameRetry:
            pass
        except GameOver:
            pass


if __name__ == "__main__":
    setup()
    main()
