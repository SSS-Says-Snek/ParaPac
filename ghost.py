from entity import *


class Ghost(Entity):
    """
    ParaPac Ghost. Do I have to explain this?
    """

    def __init__(self, x: int, y: int, z: int = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

    def wonder(self):
        pass
