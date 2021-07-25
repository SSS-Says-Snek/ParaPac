import numpy
import pygame

import tiles
from tiles import Tile
from typing import List
from entity import Entity


class Map:
    def __init__(self, file: str):
        self.entities: List[Entity] = []
        self.world = None
        self.tiles = None
        with open(file) as f:
            self.load(f.read())

    def load(self, string: str):
        rows = string.split("\n")
        self.world = pygame.Surface((len(rows[0]) * tiles.TILE_SIZE,
                                     len(rows) * tiles.TILE_SIZE), pygame.SRCALPHA)
        self.tiles = numpy.zeros((len(rows[0]), len(rows)), dtype=numpy.uint8)

        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                self.tiles[x, y] = int(tile)

        self.render_world()

    def width(self) -> int:
        return self.tiles.shape[0]

    def height(self) -> int:
        return self.tiles.shape[1]

    def size(self) -> int:
        return self.tiles.shape

    def get_at(self, x: int, y: int) -> int:
        if 0 <= x < self.tiles.shape[0] and 0 <= y < self.tiles.shape[1]:
            return self.tiles[x, y]
        else:
            return Tile.AIR

    def set_at(self, x: int, y: int, tile: int):
        if 0 <= x < self.tiles.shape[0] and 0 <= y < self.tiles.shape[1]:
            self.tiles[x, y] = tile
            self.render_world(x - 1, y - 1, x + 2, y + 2)

    def render_world(self, *args):
        begin_x, begin_y, end_x, end_y = 0, 0, self.width(), self.height()
        if args:
            begin_x, begin_y, end_x, end_y = args

        for x in range(begin_x, end_x):
            for y in range(begin_y, end_y):
                tile = self.get_at(x, y)
                xx, yy = x * tiles.TILE_SIZE, y * tiles.TILE_SIZE

                # Clear tile space
                pygame.draw.rect(self.world, (0, 0, 0, 0),
                                 ((xx, yy), (tiles.TILE_SIZE, tiles.TILE_SIZE)))

                if tile == Tile.AIR:  # Air; Nothing.
                    pass
                elif tile == Tile.WALL:  # Wall
                    right = self.get_at(x + 1, y) != Tile.WALL
                    left = self.get_at(x - 1, y) != Tile.WALL
                    up = self.get_at(x, y - 1) != Tile.WALL
                    down = self.get_at(x, y + 1) != Tile.WALL

                    if right or left or up or down:
                        self.world.blit(tiles.WALLS[(right, left, up, down)], (xx, yy))
                    if not (up or right) and self.get_at(x + 1, y - 1) != Tile.WALL:
                        self.world.blit(tiles.WALL_C_UR, (xx, yy))
                    if not (right or down) and self.get_at(x + 1, y + 1) != Tile.WALL:
                        self.world.blit(tiles.WALL_C_RD, (xx, yy))
                    if not (down or left) and self.get_at(x - 1, y + 1) != Tile.WALL:
                        self.world.blit(tiles.WALL_C_DL, (xx, yy))
                    if not (left or up) and self.get_at(x - 1, y - 1) != Tile.WALL:
                        self.world.blit(tiles.WALL_C_LU, (xx, yy))

    def render(self, x: float, y: float, width: float, height: float) -> pygame.Surface:
        surface = pygame.Surface((int(width * tiles.TILE_SIZE), int(height * tiles.TILE_SIZE)))
        surface.blit(self.world, (int(-x * tiles.TILE_SIZE), int(-y * tiles.TILE_SIZE)))
        return surface

    def update(self):
        pass
