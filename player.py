from entity import *


class PlayerDirection:
    NONE = 0
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class Player(Entity):
    """
    ParaPac Player, the player character.
    """

    def __init__(self, x: int, y: int, z: int = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.direction = PlayerDirection.RIGHT
        self.planned_direction = PlayerDirection.NONE

    def update(self, level):
        pass

    def wonder(self):
        self.task = self.forward

    def forward(self):
        pass

    def teleport(self):
        pass
