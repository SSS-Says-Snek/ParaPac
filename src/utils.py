from src import common
import pygame

from typing import List, Tuple


def polarity(x: float) -> int:
    if x == 0:
        return 0
    elif x < 0:
        return -1
    else:
        return 1


def to_world_space(x: int, y: int) -> Tuple[float, float]:
    return (x - common.map_area_x) / common.map_area_width * common.active_map.width(), \
           (y - common.map_area_y) / common.map_area_height * common.active_map.height()


def from_world_space(x: int, y: int) -> Tuple[float, float]:
    return common.active_map.width() / common.map_area_width * x + common.map_area_x, \
           common.active_map.height() / common.map_area_height * y + common.map_area_y


def load_sprite_sheet(file_name: str, columns: int, rows: int) -> List[pygame.Surface]:
    sprite_sheet = pygame.image.load(file_name).convert_alpha()
    sprites = []

    width = sprite_sheet.get_width() // columns
    height = sprite_sheet.get_height() // rows

    for y in range(rows):
        for x in range(columns):
            sprites.append(sprite_sheet.subsurface(((x * width, y * height), (width, height))).copy())

    return sprites
