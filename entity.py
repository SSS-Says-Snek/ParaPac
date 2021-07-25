import pygame
from typing import Tuple

import tiles


class Entity:
    """
    ParaPac Entity class which abstracts a character/enemy in the game world.
    """
    COLLIDE_PRECISION = 100

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.z = 0
        self.killed = False

    def kill(self):
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
                                (self.width * Entity.COLLIDE_PRECISION, self.height * Entity.COLLIDE_PRECISION))
        other_rect = pygame.Rect((x * Entity.COLLIDE_PRECISION, y * Entity.COLLIDE_PRECISION),
                                 (width * Entity.COLLIDE_PRECISION, height * Entity.COLLIDE_PRECISION))
        return bool(self_rect.colliderect(other_rect))

    def frame(self) -> Tuple[float, float, pygame.Surface]:
        """
        :return: Entity surface and its position to be rendered at
        """
        return self.x, self.y, pygame.Surface((1, 1))

    def update(self, level):
        """
        :param level: References the Map object
        """
