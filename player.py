from entity import *


class Player(Entity):
    """
    ParaPac Player, the player character.
    """

    def __init__(self, x: int, y: int, z: int = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

    def update(self, level):
        pass

    def wonder(self):
        pass

    def forward(self):
        pass

    def teleport(self):
        pass
