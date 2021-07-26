import math
import numpy
import pygame
from typing import Optional, List, Tuple, Union

from src import common, pathfinding, tiles
from src.tiles import Tile
from src.entity import Entity
from src.ghost import Ghost


class World:
    """
    ParaPac Map class which abstracts the game world.
    """

    def __init__(self, file: str, entities: List[Entity] = ()):
        self.entities: List[Entity] = list(entities)
        self.surface: Optional[pygame.Surface] = None
        self.tile_map: Optional[numpy.ndarray] = None
        with open(file) as f:
            self.load(f.read())

    def load(self, string: str):
        """
        :param string: Tile map string to be loaded in the World object
        """
        rows = string.strip("\r").split("\n")

        for row in rows:
            if not row:
                rows.remove(row)

        self.surface = pygame.Surface((len(rows[0]) * tiles.TILE_SIZE,
                                       len(rows) * tiles.TILE_SIZE), pygame.SRCALPHA)
        self.tile_map = numpy.zeros((len(rows[0]), len(rows)), dtype=numpy.uint8)

        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                self.tile_map[x, y] = int(tile)

                if int(tile) == Tile.GHOST:
                    self.entities.append(Ghost(x, y))

        self.render_world()

    def save(self) -> str:
        string = ""

        for y in range(self.tile_map.shape[1]):
            for x in range(self.tile_map.shape[0]):
                string += str(self.tile_map[x, y])
            string += "\n"

        return string

    def width(self) -> int:
        """
        :return: Width of the world
        """
        return self.tile_map.shape[0]

    def height(self) -> int:
        """
        :return: Height of the world
        """
        return self.tile_map.shape[1]

    def size(self) -> Tuple[int, int]:
        """
        :return: Size of the world
        """
        return self.tile_map.shape

    def get_at(self, x: int, y: int) -> int:
        """
        :param x: X coordinate in the tile map
        :param y: Y coordinate in the tile map
        :return: Returns the tile ID of that coordinate
        """
        return self.tile_map[x % self.tile_map.shape[0], y % self.tile_map.shape[1]]

    def set_at(self, x: int, y: int, tile: int):
        """
        :param x: X coordinate in the tile map
        :param y: Y coordinate in the tile map
        :param tile: Tile ID to be placed of in the coordinate of the tile map
        """
        self.tile_map[x % self.tile_map.shape[0], y % self.tile_map.shape[1]] = tile
        self.render_world(x, y)

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
                if self.get_at(xx, yy) in tiles.SOLID_TILES:
                    return True
        return False

    def collide_tile(self, x: float, y: float, width: float, height: float) -> int:
        """
        :param x: X coordinate of the collision box
        :param y: Y coordinate of the collision box
        :param width: Width of the collision box
        :param height: Height of the collision box
        :return: Kind of like `collide`, except it returns what tile it collided with (air is excluded)
        """
        for xx in range(math.floor(x), math.ceil(x + width)):
            for yy in range(math.floor(y), math.ceil(y + height)):
                if self.get_at(xx, yy) != Tile.AIR:
                    return self.get_at(xx, yy)

    def path_find(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Union[List, None]:
        path = pathfinding.algorithm(numpy.rot90(self.tile_map, k=1, axes=(0, 1)),
                                     (int(start_y), int(start_x)), (int(end_y), int(end_x)))
        if path:
            path[0] = path[0][1], path[0][0]
            path = path[1:]

        return path

    def render_world(self, *args):
        """
        :param args: Begin X, begin Y, end X (Optional), and end Y (Optional) of the tiles to be rendered,
        leave it empty to render the whole map
        """
        begin_x, begin_y, end_x, end_y = 0, 0, self.width(), self.height()

        if len(args) == 2:
            begin_x, begin_y = args
            end_x, end_y = begin_x + 1, begin_y + 1
        elif len(args) == 4:
            begin_x, begin_y, end_x, end_y = args

        self._render_world(begin_x - 1, begin_y - 1, end_x + 2, end_y + 2)

    def _render_world(self, begin_x, begin_y, end_x, end_y):
        width, height = self.surface.get_size()

        for x in range(begin_x, end_x):
            for y in range(begin_y, end_y):
                tile = self.get_at(x, y)
                xx, yy = x * tiles.TILE_SIZE, y * tiles.TILE_SIZE

                # Clear tile space
                pygame.draw.rect(self.surface, (0, 0, 0, 0),
                                 ((xx % width, yy % height), (tiles.TILE_SIZE, tiles.TILE_SIZE)))

                if tile == Tile.AIR:
                    pass
                elif tile == Tile.WALL:
                    def blit_wall(wall):
                        self.surface.blit(wall, (xx % width, yy % height))

                    right = self.get_at(x + 1, y) in tiles.PASSABLE_TILES
                    left = self.get_at(x - 1, y) in tiles.PASSABLE_TILES
                    up = self.get_at(x, y - 1) in tiles.PASSABLE_TILES
                    down = self.get_at(x, y + 1) in tiles.PASSABLE_TILES

                    if right or left or up or down:
                        blit_wall(tiles.WALLS[(right, left, up, down)])
                    if not (up or right) and self.get_at(x + 1, y - 1) in tiles.PASSABLE_TILES:
                        blit_wall(tiles.WALL_C_UR)
                    if not (right or down) and self.get_at(x + 1, y + 1) in tiles.PASSABLE_TILES:
                        blit_wall(tiles.WALL_C_RD)
                    if not (down or left) and self.get_at(x - 1, y + 1) in tiles.PASSABLE_TILES:
                        blit_wall(tiles.WALL_C_DL)
                    if not (left or up) and self.get_at(x - 1, y - 1) in tiles.PASSABLE_TILES:
                        blit_wall(tiles.WALL_C_LU)
                elif tile == Tile.POINT:
                    pygame.draw.circle(self.surface, (255, 255, 0), (xx + 8, yy + 8), 5)
                elif tile == Tile.GHOST and common.DEBUG:
                    pygame.draw.circle(self.surface, (255, 0, 0), (xx + 8, yy + 8), 5)

    def render(self) -> pygame.Surface:
        """
        :return: Rendered surface of the world
        """
        surface = self.surface.copy()

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
        Calls the World object's entities' update method with its tasks and remove killed entities
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
