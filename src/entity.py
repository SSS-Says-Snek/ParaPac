import pygame

from src import tiles


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

    def width(self):
        return self.frame.get_width() / tiles.TILE_SIZE

    def height(self):
        return self.frame.get_height() / tiles.TILE_SIZE

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
                                (self.frame.get_width() * Entity.COLLIDE_PRECISION,
                                 self.frame.get_height() * Entity.COLLIDE_PRECISION))
        other_rect = pygame.Rect((x * Entity.COLLIDE_PRECISION, y * Entity.COLLIDE_PRECISION),
                                 (width * Entity.COLLIDE_PRECISION, height * Entity.COLLIDE_PRECISION))
        return bool(self_rect.colliderect(other_rect))

    def update(self, world):
        """
        :param world: References the Map object
        """

    def wonder(self, world):
        """
        Wonders what task to do depending on certain circumstances defined by the sub-class.
        """
