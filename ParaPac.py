import pygame
import os
import sys
import time

from map import Map
from interrupt import *
from player import Player
from tiles import Tile


DEBUG = "-d" in sys.argv or "--debug" in sys.argv
WINDOW = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
FONT = pygame.font.Font(os.path.join("assets", "VT323.ttf"), 24)
CLOCK = pygame.time.Clock()

fps = 0
delta = 0
last_tick = time.perf_counter()

player = Player(0, 0)
map_a = Map(os.path.join("maps", "map_a.txt"))
# map_b = Map(os.path.join("maps", "map_b.txt"))
active_map = map_a

map_area_x, map_area_y = 0, 0
map_area_width, map_area_height = 0, 0


def gameplay_events():
    global DEBUG, WINDOW, fps, delta, last_tick

    pygame.display.flip()
    CLOCK.tick()

    delta = time.perf_counter() - last_tick
    fps = 1 / delta
    last_tick = time.perf_counter()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                DEBUG = not DEBUG

    if DEBUG:
        mx, my = pygame.mouse.get_pos()
        lmb, mmb, rmb = pygame.mouse.get_pressed(3)
        if lmb:
            gameplay_map_edit(mx, my, Tile.WALL)
        elif rmb:
            gameplay_map_edit(mx, my, Tile.AIR)


def gameplay_map_edit(x: int, y: int, tile):
    x = (x - map_area_x) / map_area_width * active_map.width()
    y = (y - map_area_y) / map_area_height * active_map.height()
    active_map.set_at(int(x), int(y), tile)


def gameplay_map():
    global map_area_x, map_area_y, map_area_width, map_area_height

    active_map.update()
    world = active_map.render()

    WINDOW.fill((0, 32, 64))
    ratio = world.get_width() / world.get_height()
    if WINDOW.get_width() > ratio * WINDOW.get_height():
        map_area_width, map_area_height = int(ratio * WINDOW.get_height()), int(WINDOW.get_height())
        map_area_x, map_area_y = (WINDOW.get_width() - map_area_width) // 2, 0
    else:
        map_area_width, map_area_height = int(WINDOW.get_width()), int(WINDOW.get_width() / ratio)
        map_area_x, map_area_y = 0, (WINDOW.get_height() - map_area_height) // 2

    world = pygame.transform.scale(world, (map_area_width, map_area_height))
    WINDOW.blit(world, (map_area_x, map_area_y))


def gameplay_loop():
    gameplay_events()
    gameplay_map()

    if DEBUG:
        WINDOW.blit(FONT.render(
            f"FPS: {int(fps)}",
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
    main()
