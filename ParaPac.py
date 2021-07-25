import pygame
import os
import sys
import time

import common
from map import Map
from interrupt import *
from player import Player
from tiles import Tile


def setup():
    pygame.display.set_caption("ParaPac - Pygame Community Summer Team Jam")

    common.maps = [
        (Map(os.path.join("maps", "map_a.txt")), (0, 32, 64), "map_a.txt"),
        (Map(os.path.join("maps", "map_b.txt")), (64, 0, 0), "map_b.txt")
    ]

    common.player = Player(1, 1)
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
                common.active_map_id = (common.active_map_id + 1) % len(common.maps)
                common.active_map = common.maps[common.active_map_id][0]

    if common.DEBUG:
        mx, my = pygame.mouse.get_pos()
        lmb, mmb, rmb = pygame.mouse.get_pressed(3)
        x, y = common.to_world_space(mx, my)
        if lmb:
            common.active_map.set_at(int(x), int(y), Tile.WALL)
        elif rmb:
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
    common.window.blit(world, (common.map_area_x, common.map_area_y))


def gameplay_loop():
    gameplay_events()
    gameplay_map()

    if common.DEBUG:
        common.window.blit(common.font.render(
            f"FPS: {int(common.fps)}",
            False, (255, 255, 255), (0, 0, 0)
        ), (0, 0))


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
