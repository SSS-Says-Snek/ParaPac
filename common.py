import pygame
import os
import sys
import time
from typing import Any, Tuple


pygame.init()

DEBUG = "-d" in sys.argv or "--debug" in sys.argv
window = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.Font(os.path.join("assets", "VT323.ttf"), 24)
maps = []

fps = 0
delta = 0
last_tick = time.perf_counter()
map_area_x, map_area_y = 0, 0
map_area_width, map_area_height = 1, 1

player: Any = None
active_map_id = 0
active_map: Any = None


def to_world_space(x: int, y: int) -> Tuple[float, float]:
    return (x - map_area_x) / map_area_width * active_map.width(), \
           (y - map_area_y) / map_area_height * active_map.height()


def from_world_space(x: int, y: int) -> Tuple[float, float]:
    return active_map.width() / map_area_width * x + map_area_x, \
           active_map.height() / map_area_height * y + map_area_y
