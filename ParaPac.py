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


def gameplay_events():
    global WINDOW, fps, delta, last_tick

    pygame.display.flip()
    CLOCK.tick()

    delta = time.perf_counter() - last_tick
    fps = 1 / delta
    last_tick = time.perf_counter()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameExit
        elif event.type == pygame.VIDEORESIZE:
            WINDOW = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            active_map.set_at(int(event.pos[0] / WINDOW.get_width() * active_map.width()),
                              int(event.pos[1] / WINDOW.get_height() * active_map.height()),
                              Tile.WALL if event.button == 1 else Tile.AIR)


def gameplay_loop():
    gameplay_events()

    WINDOW.fill((0, 32, 64))
    active_map.update()
    WINDOW.blit(pygame.transform.scale(active_map.render(), WINDOW.get_size()), (0, 0))

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
