import math
import numpy
import pygame
import time
from typing import Optional, List, Tuple, Union

from src import common, pathfinding, tiles
from src.tiles import Tile
from src.entity import Entity
from src.ghost import BlinkyGhost, PinkyGhost, InkyGhost, ClydeGhost, GhostAttributes


class World:
    """
    ParaPac Map class which abstracts the game world.
    """

    def __init__(self, file: str, entities: List[Entity] = ()):
        self.creation = time.perf_counter()
        self.entities: List[Entity] = list(entities)
        self.surface: Optional[pygame.Surface] = None
        self.overlay: Optional[pygame.Surface] = None
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
        self.overlay = self.surface.copy()
        self.tile_map = numpy.zeros((len(rows[0]), len(rows)), dtype=numpy.uint8)

        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                tile = int(tile, 36)
                self.tile_map[x, y] = tile

                if tile == Tile.RED_GHOST:
                    self.entities.append(BlinkyGhost(x, y, GhostAttributes.RED_COLOR))
                elif tile == Tile.PINK_GHOST:
                    self.entities.append(PinkyGhost(x, y, GhostAttributes.PINK_COLOR))
                elif tile == Tile.BLUE_GHOST:
                    self.entities.append(InkyGhost(x, y, GhostAttributes.BLUE_COLOR))
                elif tile == Tile.ORANGE_GHOST:
                    self.entities.append(ClydeGhost(x, y, GhostAttributes.ORANGE_COLOR))
        self.render_world()

    def save(self) -> str:
        string = ""

        for y in range(self.tile_map.shape[1]):
            for x in range(self.tile_map.shape[0]):
                string += hex(self.tile_map[x, y])[2:]
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

    def collide(self, x: float, y: float, width: float, height: float, is_player=False) -> bool:
        """
        :param x: X coordinate of the collision box
        :param y: Y coordinate of the collision box
        :param width: Width of the collision box
        :param height: Height of the collision box
        :param is_player: If the "collidee" is a player
        :return: Returns true if it collided with the world
        """
        for xx in range(math.floor(x), math.ceil(x + width)):
            for yy in range(math.floor(y), math.ceil(y + height)):
                tile = self.get_at(xx, yy)
                if is_player and tile in tiles.ANTI_PLAYER_TILES:
                    return True
                elif tile in tiles.SOLID_TILES:
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
        path = pathfinding.algorithm(numpy.transpose(self.tile_map),
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

        for x in range(max(begin_x, 0), min(end_x, self.width())):
            for y in range(max(begin_y, min(end_y, self.height()))):
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
                elif tile == Tile.COIN:
                    pygame.draw.circle(self.surface, (255, 255, 0), (xx + 7, yy + 7), 4)
                elif tile == Tile.PELLET:
                    pygame.draw.circle(self.surface, (255, 255, 0), (xx + 7, yy + 7), 7)
                elif tile == Tile.SHOP:
                    pygame.draw.rect(self.surface, (255, 255, 0), (xx, yy, tiles.TILE_SIZE, tiles.TILE_SIZE))
                elif tile == Tile.END:
                    pygame.draw.rect(self.surface, (0, 255, 0), (xx, yy, tiles.TILE_SIZE, tiles.TILE_SIZE))
                elif common.DEBUG:
                    def draw(color):
                        pygame.draw.rect(self.surface, color, ((xx + 4, yy + 4),
                                                               (tiles.TILE_SIZE // 2, tiles.TILE_SIZE // 2)))

                    if tile == Tile.RED_GHOST:
                        draw(GhostAttributes.RED_COLOR)
                    elif tile == Tile.PINK_GHOST:
                        draw(GhostAttributes.PINK_COLOR)
                    elif tile == Tile.BLUE_GHOST:
                        draw(GhostAttributes.BLUE_COLOR)
                    elif tile == Tile.ORANGE_GHOST:
                        draw(GhostAttributes.ORANGE_COLOR)

                    elif tile == Tile.BARRIER:
                        pygame.draw.rect(self.surface, (255, 0, 0), ((xx, yy), (tiles.TILE_SIZE, tiles.TILE_SIZE)))

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

        surface.blit(self.overlay, (0, 0))
        return surface

    def update(self):
        """
        Calls the World object's entities' update method with its tasks and remove killed entities
        """
        self.entities = sorted(self.entities, key=lambda en: en.z)
        self.overlay.fill((0, 0, 0, 0))

        for i, entity in enumerate(self.entities):
            if entity.killed:
                del self.entities[i]
                continue
            entity.x %= self.width()
            entity.y %= self.height()

            if not common.DEBUG_FREEZE:
                entity.task(self)
                entity.update(self)

            if common.DEBUG:
                entity.debug(self)

    def has_coins(self) -> bool:
        for x in range(self.width()):
            for y in range(self.height()):
                if self.tile_map[x, y] == Tile.COIN:
                    return True

        return False
