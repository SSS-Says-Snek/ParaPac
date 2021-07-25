import math
import numpy
import pygame
from typing import Optional, List, Tuple

import tiles
from tiles import Tile
from entity import Entity


class Map:
    """
    ParaPac Map class which abstracts the game world.
    """

    def __init__(self, file: str, entities: List[Entity] = ()):
        self.entities = entities
        self.entities: List[Entity] = list(entities)
        self.world: Optional[pygame.Surface] = None
        self.tiles: Optional[numpy.ndarray] = None
        with open(file) as f:
            self.load(f.read())

    def load(self, string: str):
        """
        :param string: Tile map string to be loaded in the Map object
        """
        rows = string.strip("\r").split("\n")

        for row in rows:
            if not row:
                rows.remove(row)

        self.world = pygame.Surface((len(rows[0]) * tiles.TILE_SIZE,
                                     len(rows) * tiles.TILE_SIZE), pygame.SRCALPHA)
        self.tiles = numpy.zeros((len(rows[0]), len(rows)), dtype=numpy.uint8)

        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                self.tiles[x, y] = int(tile)

        self.render_world()

    def save(self) -> str:
        string = ""

        for y in range(self.tiles.shape[1]):
            for x in range(self.tiles.shape[0]):
                string += str(self.tiles[x, y])
            string += "\n"

        return string

    def width(self) -> int:
        """
        :return: Width of the tile map
        """
        return self.tiles.shape[0]

    def height(self) -> int:
        """
        :return: Height of the tile map
        """
        return self.tiles.shape[1]

    def size(self) -> Tuple[int, int]:
        """
        :return: Size of the tile map
        """
        return self.tiles.shape

    def get_at(self, x: int, y: int) -> int:
        """
        :param x: X coordinate in the tile map
        :param y: Y coordinate in the tile map
        :return: Returns the tile ID of that coordinate or Tile.AIR if it's out of bound
        """
        if 0 <= x < self.tiles.shape[0] and 0 <= y < self.tiles.shape[1]:
            return self.tiles[x, y]
        else:
            return Tile.AIR

    def set_at(self, x: int, y: int, tile: int):
        """
        :param x: X coordinate in the tile map
        :param y: Y coordinate in the tile map
        :param tile: Tile ID to be placed of in the coordinate of the tile map
        """
        if 0 <= x < self.tiles.shape[0] and 0 <= y < self.tiles.shape[1]:
            self.tiles[x, y] = tile
            self.render_world(x - 1, y - 1, x + 2, y + 2)

    def collide(self, x: float, y: float, width: float, height: float) -> bool:
        """
        :param x: X coordinate of the collision box
        :param y: Y coordinate of the collision box
        :param width: Width of the collision box
        :param height: Height of the collision box
        :return: Returns true if it collided with the world
        """
        for xx in range(math.floor(x), math.ceil(x + width)):
            for yy in range(math.floor(y), math.ceil(y + height)):
                if self.get_at(xx, yy) != Tile.AIR:
                    return True
        return False

    def render_world(self, *args):
        """
        :param args: Begin X, begin Y, end X, and end Y of the tiles to be rendered,
        leave it empty to render the whole map
        """
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

                if tile == Tile.AIR:
                    pass
                elif tile == Tile.WALL:
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

    def render(self) -> pygame.Surface:
        """
        :return: Rendered surface of the world
        """
        surface = self.world.copy()

        for entity in self.entities:
            frame = entity.frame
            outside_x = entity.x + entity.width() > self.width() - 1
            outside_y = entity.y + entity.height() > self.height() - 1

            if outside_x and outside_y:
                surface.blit(frame, ((entity.x - self.width()) * tiles.TILE_SIZE,
                                     (entity.y - self.height()) * tiles.TILE_SIZE))
            elif outside_x:
                surface.blit(frame, ((entity.x - self.width()) * tiles.TILE_SIZE,
                                     entity.y * tiles.TILE_SIZE))
            elif outside_y:
                surface.blit(frame, (entity.x * tiles.TILE_SIZE,
                                     (entity.y - self.height()) * tiles.TILE_SIZE))

            surface.blit(frame, (entity.x * tiles.TILE_SIZE, entity.y * tiles.TILE_SIZE))

        return surface

    def update(self):
        """
        Calls the Map object's entities' update method with its tasks and remove killed entities
        """
        self.entities = sorted(self.entities, key=lambda en: -en.z)

        for i, entity in enumerate(self.entities):
            if entity.killed:
                del self.entities[i]
                continue
            entity.x %= self.width()
            entity.y %= self.height()
            entity.task(self)
            entity.update(self)
