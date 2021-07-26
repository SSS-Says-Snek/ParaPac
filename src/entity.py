import pygame
from typing import Any

from src import tiles


class Direction:
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3
    NONE = 4


class Entity:
    """
    ParaPac Entity class which abstracts a character/enemy in the game world.
    """
    COLLIDE_PRECISION = 100
    PLACEHOLDER_SURFACE = pygame.Surface((16, 16))
    PLACEHOLDER_SURFACE.fill((255, 0, 0))

    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z
        self.killed = False
        self.task = self.wonder
        self.frame = Entity.PLACEHOLDER_SURFACE
        self.direction = Direction.NONE

    def width(self):
        return self.frame.get_width() / tiles.TILE_SIZE

    def height(self):
        return self.frame.get_height() / tiles.TILE_SIZE

    def kill(self, world):
        """
        Kills the entity
        """
        self.killed = True

    def collide(self, x: float, y: float, width: float, height: float) -> bool:
        """
        :param x: X coordinate of the collision box
        :param y: Y coordinate of the collision box
        :param width: Width of the collision box
        :param height: Height of the collision box
        :return: Returns true if it collided with the entity
        """
        self_rect = pygame.Rect((self.x * Entity.COLLIDE_PRECISION, self.y * Entity.COLLIDE_PRECISION),
                                (self.frame.get_width() * Entity.COLLIDE_PRECISION,
                                 self.frame.get_height() * Entity.COLLIDE_PRECISION))
        other_rect = pygame.Rect((x * Entity.COLLIDE_PRECISION, y * Entity.COLLIDE_PRECISION),
                                 (width * Entity.COLLIDE_PRECISION, height * Entity.COLLIDE_PRECISION))
        return bool(self_rect.colliderect(other_rect))

    def nudge(self, world, x: float, y: float, ignore_collision=False) -> bool:
        is_able = not world.collide(self.x + x, self.y + y, self.width(), self.height())
        if is_able or ignore_collision:
            self.x += x
            self.y += y

            if x < 0:
                self.direction = Direction.LEFT
            elif x > 0:
                self.direction = Direction.RIGHT
            elif y < 0:
                self.direction = Direction.UP
            elif y > 0:
                self.direction = Direction.DOWN

        return is_able

    def update(self, world):
        """
        :param world: References the Map object
        """

    def wonder(self, world):
        """
        Wonders what task to do depending on certain circumstances defined by the sub-class.
        """
