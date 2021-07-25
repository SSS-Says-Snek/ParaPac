import os
import time

from entity import *


SPEED = 0.125  # MUST have a base power of 2, otherwise floating precision errors go brr

EATING = []
for i in range(11):
    path = os.path.join("assets", f"pacman_{str(i).zfill(2)}.png")
    EATING.append(pygame.image.load(path))
ROTATED_EATING = [[pygame.transform.rotate(frame, rotation) for frame in EATING]
                  for rotation in (0, 180, 90, -90)]


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
        self.next_direction = PlayerDirection.NONE

    def update(self, level):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.next_direction = PlayerDirection.UP
        elif keys[pygame.K_a]:
            self.next_direction = PlayerDirection.LEFT
        elif keys[pygame.K_s]:
            self.next_direction = PlayerDirection.DOWN
        elif keys[pygame.K_d]:
            self.next_direction = PlayerDirection.RIGHT

    def wonder(self, level):
        self.task = self.forward

    def forward(self, level):
        moved = False
        if self.direction == PlayerDirection.RIGHT:
            if not level.collide(self.x + SPEED, self.y, 2, 2):
                self.x += SPEED
                moved = True
        elif self.direction == PlayerDirection.LEFT:
            if not level.collide(self.x - SPEED, self.y, 2, 2):
                self.x -= SPEED
                moved = True
        elif self.direction == PlayerDirection.UP:
            if not level.collide(self.x, self.y - SPEED, 2, 2):
                self.y -= SPEED
                moved = True
        elif self.direction == PlayerDirection.DOWN:
            if not level.collide(self.x, self.y + SPEED, 2, 2):
                self.y += SPEED
                moved = True

        if self.next_direction != self.direction:
            if self.next_direction == PlayerDirection.RIGHT:
                if not level.collide(self.x + SPEED, self.y, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == PlayerDirection.LEFT:
                if not level.collide(self.x - SPEED, self.y, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == PlayerDirection.UP:
                if not level.collide(self.x, self.y - SPEED, 2, 2):
                    self.direction = self.next_direction
            elif self.next_direction == PlayerDirection.DOWN:
                if not level.collide(self.x, self.y + SPEED, 2, 2):
                    self.direction = self.next_direction

        if moved:
            self.frame = ROTATED_EATING[self.direction - 1][int(time.perf_counter() * len(EATING) * 4) % len(EATING)]
        else:
            self.frame = ROTATED_EATING[self.direction - 1][-1]

    def teleport(self, level):
        pass
