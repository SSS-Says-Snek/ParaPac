import os

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

    def __init__(self, x: int, y: int, z: int = 0):
        super().__init__()
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self.z = z
        self.direction = GhostDirection.RIGHT
        self.path = []

    def update(self, world):
        self.frame = GHOST[self.direction]

    def follow(self, world):
        if self.path:
            if self.path[0] == (self.x, self.y):
                del self.path[0]
            if self.path:
                self.x += utils.polarity(self.path[0][0] - self.x) * SPEED
                self.y += utils.polarity(self.path[0][1] - self.y) * SPEED
        else:
            self.path = world.path_find(int(self.x), int(self.y),
                                        int(common.player.x), int(common.player.y))

    def wonder(self, world):
        self.task = self.follow
