import os

import pygame.key

from src import common, utils
from src.entity import *


GHOST = utils.load_sprite_sheet(os.path.join("assets", "ghost.png"), 2, 2)


class Ghost(Entity):
    """
    ParaPac Ghost. Do I have to explain this?
    """

    def __init__(self, x: int, y: int, color=(0, 0, 0), speed=0.125):
        super().__init__()
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self.z = 1

        self.speed = speed

        self.path = []
        self.frames = [frame.copy() for frame in GHOST]
        self.direction = Direction.UP

        # Color keys the ghost
        for frame in self.frames:
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):
                    if frame.get_at((x, y)) == (0, 255, 0, 255):
                        frame.set_at((x, y), color)

    def update(self, world):
        self.frame = self.frames[self.direction]

        if common.DEBUG:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.kill(world)

            if self.path:
                for x, y in self.path:
                    pygame.draw.rect(world.overlay, (255, 0, 0),
                                     ((x * tiles.TILE_SIZE + tiles.TILE_SIZE // 4,
                                       y * tiles.TILE_SIZE + tiles.TILE_SIZE // 4),
                                      (tiles.TILE_SIZE // 2, tiles.TILE_SIZE // 2)))

    def kill(self, world):
        self.path = world.path_find(self.x, self.y, self.origin_x, self.origin_y)
        self.task = self.go_home

    def propagate_path(self, world):
        if self.path[0] == (self.x, self.y):
            del self.path[0]
        if self.path:
            moved = self.nudge(world, self.speed * utils.polarity(self.path[0][0] - self.x),
                               self.speed * utils.polarity(self.path[0][1] - self.y), ignore_collision=False)
            if not moved:
                self.path = []

    def go_home(self, world):
        if self.path:
            self.propagate_path(world)
        else:
            self.task = self.wonder

    def tracking(self, world):
        if self.path:
            self.propagate_path(world)
        else:
            self.path = world.path_find(self.x, self.y, common.player.x, common.player.y)

    def wonder(self, world):
        self.task = self.tracking
