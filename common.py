import pygame
import os
import sys
import time
from typing import Any, List, Tuple


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

# Uses Any to make PyCharm shut up
player: Any = None
active_map_id: int = 0
active_map: Any = None
transitioning_mode: str = "Not Transitioning"
alpha: int = 255

score: int = 0


def to_world_space(x: int, y: int) -> Tuple[float, float]:
    try:
        return (x - map_area_x) / map_area_width * active_map.width(), \
               (y - map_area_y) / map_area_height * active_map.height()
    except ZeroDivisionError:
        return 0, 0


def from_world_space(x: int, y: int) -> Tuple[float, float]:
    try:
        return active_map.width() / map_area_width * x + map_area_x, \
               active_map.height() / map_area_height * y + map_area_y
    except ZeroDivisionError:
        return 0, 0


def load_sprite_sheet(file_name: str, columns: int, rows: int) -> List[pygame.Surface]:
    sprite_sheet = pygame.image.load(file_name).convert_alpha()
    sprites = []

    width = sprite_sheet.get_width() // columns
    height = sprite_sheet.get_height() // rows

    for y in range(rows):
        for x in range(columns):
            sprites.append(sprite_sheet.subsurface(((x * width, y * height), (width, height))).copy())

    return sprites
