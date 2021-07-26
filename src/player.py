import os
import time

from src import common, utils
from src.entity import *


SPEED = 0.125  # MUST have a base power of 2, otherwise floating precision errors go brr

_PACMAN = utils.load_sprite_sheet(os.path.join("assets", "pacman.png"), 3, 4)[:11]
PACMAN = [[pygame.transform.rotate(frame, rotation) for frame in _PACMAN]
          for rotation in (0, 180, 90, -90)]


class Player(Entity):
    """
    ParaPac Player, the player character.
    """

    def __init__(self, x: int, y: int, z: int = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

        self.direction = Direction.UP
        self.next_direction = Direction.NONE

    def update(self, world):
        if common.DEBUG:
            print(f"Player X: {self.x} Y: {self.y}")

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.next_direction = Direction.UP
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.next_direction = Direction.LEFT
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.next_direction = Direction.DOWN
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.next_direction = Direction.RIGHT

        if world.collide_tile(int(self.x), int(self.y), 2, 2) == tiles.Tile.POINT:
            # print("score point :eyes:")
            for x in range(int(self.x), int(self.x) + 2):
                for y in range(int(self.y), int(self.y) + 2):
                    if world.get_at(x, y) == tiles.Tile.POINT:
                        world.set_at(x, y, tiles.Tile.AIR)
                        common.score += 10

    def wonder(self, world):
        self.task = self.forward

    def forward(self, world):
        moved = False
        if self.direction == Direction.RIGHT:
            moved = moved or self.nudge(world, SPEED, 0)
        elif self.direction == Direction.LEFT:
            moved = moved or self.nudge(world, -SPEED, 0)
        elif self.direction == Direction.UP:
            moved = moved or self.nudge(world, 0, -SPEED)
        elif self.direction == Direction.DOWN:
            moved = moved or self.nudge(world, 0, SPEED)

        if self.next_direction != self.direction:
            if self.next_direction == Direction.RIGHT:
                if not world.collide(self.x + SPEED, self.y, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.LEFT:
                if not world.collide(self.x - SPEED, self.y, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.UP:
                if not world.collide(self.x, self.y - SPEED, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.DOWN:
                if not world.collide(self.x, self.y + SPEED, 2, 2):
                    self.direction = self.next_direction

        if moved:
            self.frame = PACMAN[self.direction][int(time.perf_counter() * len(_PACMAN) * 4) % len(_PACMAN)]
        else:
            self.frame = PACMAN[self.direction][-1]

    def teleport(self, world):
        pass
