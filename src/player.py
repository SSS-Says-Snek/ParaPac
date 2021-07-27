import os
import time

import pygame

from src import common, utils, tiles
from src.tiles import Tile
from src.entity import *


SPEED = 0.125  # MUST have a base power of 2, otherwise floating precision errors go brr

_PACMAN = utils.load_sprite_sheet(os.path.join("assets", "pacman_eat.png"), 4, 2)
PACMAN = [[pygame.transform.rotate(frame, rotation) for frame in _PACMAN]
          for rotation in (0, 180, 90, -90)]


class Player(Entity):
    """
    ParaPac Player, the player character.
    """

    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y
        self.z = 1

        self.direction = Direction.UP
        self.next_direction = Direction.NONE

    def update(self, world):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.next_direction = Direction.UP
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.next_direction = Direction.LEFT
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.next_direction = Direction.DOWN
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.next_direction = Direction.RIGHT

        if common.DEBUG:
            mx, my = pygame.mouse.get_pos()
            left_click, middle_click, right_click = pygame.mouse.get_pressed(3)
            x, y = utils.to_world_space(mx, my)

            rect = pygame.Surface((tiles.TILE_SIZE, tiles.TILE_SIZE), pygame.SRCALPHA)
            rect.fill((255, 255, 0, 128))
            world.overlay.blit(rect, (int(x) * tiles.TILE_SIZE, int(y) * tiles.TILE_SIZE))

            if left_click:
                world.set_at(int(x), int(y), Tile.WALL)
            elif middle_click:
                world.set_at(int(x), int(y), Tile.GHOST)
            elif right_click:
                world.set_at(int(x), int(y), Tile.AIR)
        else:
            if world.collide_tile(int(self.x), int(self.y), 1, 1) == tiles.Tile.POINT:
                for x in range(int(self.x), int(self.x) + 1):
                    for y in range(int(self.y), int(self.y) + 1):
                        if world.get_at(x, y) == tiles.Tile.POINT:
                            world.set_at(x, y, tiles.Tile.AIR)
                            common.score += 10
                            common.coins += 1

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
                if not world.collide(self.x + SPEED, self.y, 1, 1):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.LEFT:
                if not world.collide(self.x - SPEED, self.y, 1, 1):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.UP:
                if not world.collide(self.x, self.y - SPEED, 1, 1):
                    self.direction = self.next_direction
            elif self.next_direction == Direction.DOWN:
                if not world.collide(self.x, self.y + SPEED, 1, 1):
                    self.direction = self.next_direction

        if moved:
            self.frame = PACMAN[self.direction][int(time.perf_counter() * len(_PACMAN) * 4) % len(_PACMAN)]
        else:
            self.frame = PACMAN[self.direction][-1]

    def teleport(self, world):
        pass
