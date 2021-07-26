import os

import pygame.key

from src import common, utils
from src.entity import *


SPEED = 0.125  # MUST have a base power of 2


GHOST = utils.load_sprite_sheet(os.path.join("assets", "ghost.png"), 2, 2)


class GhostDirection:
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3


class Ghost(Entity):
    """
    ParaPac Ghost. Do I have to explain this?
    """

    def __init__(self, x: int, y: int, z: int = 0, color=(0, 0, 0)):
        super().__init__()
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self.z = z

        self.frames = [frame.copy() for frame in GHOST]
        self.direction = GhostDirection.RIGHT
        self.path = []

        # Color keys the ghost
        for frame in self.frames:
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):
                    if frame.get_at((x, y)) == (0, 255, 0, 255):
                        frame.set_at((x, y), color)

    def update(self, world):
        self.frame = self.frames[self.direction]

    def follow(self, world):
        pass

    def wonder(self, world):
        pass
