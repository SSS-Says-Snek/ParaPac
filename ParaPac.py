import pygame
import os
import sys
import time

from map import Map
from player import Player
from tiles import Tile


DEBUG = "-d" in sys.argv or "--debug" in sys.argv
WINDOW = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
FONT = pygame.font.Font(os.path.join("assets", "VT323.ttf"), 24)
CLOCK = pygame.time.Clock()
fps = 0
delta = 0
last_tick = time.perf_counter()

player = Player()
map_a = Map(os.path.join("maps", "map_a.txt"))
# map_b = Map(os.path.join("maps", "map_b.txt"))


def main():
    global WINDOW, fps, delta, last_tick

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                WINDOW = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                map_a.set_at(int(event.pos[0] / WINDOW.get_width() * map_a.width()),
                             int(event.pos[1] / WINDOW.get_height() * map_a.height()),
                             Tile.WALL if event.button == 1 else Tile.AIR)

        WINDOW.fill((0, 32, 64))
        WINDOW.blit(pygame.transform.scale(map_a.render(0, 0, map_a.width(), map_a.height()),
                                           WINDOW.get_size()), (0, 0))

        if DEBUG:
            WINDOW.blit(FONT.render(
                f"FPS: {int(fps)}",
                False, (255, 255, 255), (0, 0, 0)
            ), (0, 0))

        pygame.display.flip()
        CLOCK.tick()

        delta = time.perf_counter() - last_tick
        fps = 1 / delta
        last_tick = time.perf_counter()


if __name__ == "__main__":
    main()
