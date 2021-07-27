import os
import time

from src import common, utils
from src.entity import *


GHOST_TEMPLATE = utils.load_sprite_sheet(os.path.join("assets", "ghost.png"), 2, 2)
GHOST_VULNERABLE = utils.load_sprite_sheet(os.path.join("assets", "ghost_vulnerable.png"), 2, 2)


class GhostAttributes:
    RED_COLOR = (255, 0, 0)
    PINK_COLOR = (255, 0, 255)
    BLUE_COLOR = (0, 0, 255)
    ORANGE_COLOR = (255, 255, 0)


class GhostState:
    NONE = 0
    LIVING = 1
    VULNERABLE = 2
    TRANSITION = 3
    DEAD = 4


class Ghost(Entity):
    """
    ParaPac Ghost. Do I have to explain this?
    """

    def __init__(self, x: int, y: int, color=(0, 0, 0), speed=0.125,
                 vulnerable_period=5, transition_period=5):
        super().__init__()
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y

        self.color = color
        self.speed = speed
        self.state = GhostState.LIVING
        self.timer = 0
        self.vulnerable_period = vulnerable_period
        self.transition_period = transition_period

        self.path = []
        self.eyes = [frame.copy() for frame in GHOST_TEMPLATE]
        self.frames = [frame.copy() for frame in GHOST_TEMPLATE]
        self.direction = Direction.UP

        # Color keys the ghost
        for i, frame in enumerate(GHOST_TEMPLATE):
            for x in range(frame.get_width()):
                for y in range(frame.get_height()):
                    pixel = frame.get_at((x, y))

                    if pixel == (0, 255, 0, 255):
                        self.eyes[i].set_at((x, y), (0, 0, 0, 0))
                        self.frames[i].set_at((x, y), color)
                    elif pixel == (0, 0, 255, 255):
                        self.eyes[i].set_at((x, y), color)
                        self.frames[i].set_at((x, y), color)

    def update(self, world):
        if common.player in world.entities and common.player.collide(self.x, self.y, 1, 1):
            if self.state == GhostState.LIVING:
                pass  # make game over stuff here
            else:
                self.state = GhostState.DEAD

        if self.state == GhostState.LIVING:
            self.task = self.tracking
        elif self.state == GhostState.VULNERABLE or self.state == GhostState.TRANSITION:
            self.task = self.wonder

            if time.perf_counter() - self.timer > self.vulnerable_period:
                self.state = GhostState.TRANSITION
            elif time.perf_counter() - self.timer > self.vulnerable_period + self.transition_period:
                self.state = GhostState.LIVING
        elif self.state == GhostState.DEAD:
            self.task = self.go_home
            if self.x == self.origin_x and self.y == self.origin_y:
                self.state = GhostState.LIVING

        if self.state == GhostState.LIVING:
            self.frame = self.frames[self.direction]
        elif self.state == GhostState.VULNERABLE:
            self.frame = GHOST_VULNERABLE[int(time.perf_counter() * 8) % 4]
        elif self.state == GhostState.TRANSITION:
            if int(time.perf_counter() * 8) % 2:
                self.frame = self.frames[self.direction]
            else:
                self.frame = GHOST_VULNERABLE[int(time.perf_counter() * 8) % 4]
        elif self.state == GhostState.DEAD:
            self.frame = self.eyes[self.direction]

    def debug(self, world):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.task = self.go_home

        pygame.draw.rect(world.overlay, self.color, ((self.origin_x * tiles.TILE_SIZE + tiles.TILE_SIZE // 4,
                                                      self.origin_y * tiles.TILE_SIZE + tiles.TILE_SIZE // 4),
                                                     (tiles.TILE_SIZE // 2, tiles.TILE_SIZE // 2)))

        if self.path:
            rect = pygame.Surface((tiles.TILE_SIZE // 2, tiles.TILE_SIZE // 2), pygame.SRCALPHA)
            rect.fill((self.color[0], self.color[1], self.color[2], 128))

            for x, y in self.path:
                world.overlay.blit(rect, (x * tiles.TILE_SIZE + tiles.TILE_SIZE // 4,
                                          y * tiles.TILE_SIZE + tiles.TILE_SIZE // 4))

    def propagate_path(self, world):
        if self.path[0] == (self.x, self.y):
            del self.path[0]
        if self.path:
            moved = self.nudge(world, self.speed * utils.polarity(self.path[0][0] - self.x),
                               self.speed * utils.polarity(self.path[0][1] - self.y),
                               ignore_collision=self.state != GhostState.LIVING)
            if not moved:
                self.path = []

    def go_home(self, world):
        if self.path and self.path[-1] == (self.origin_x, self.origin_y):
            self.propagate_path(world)
        elif self.x != self.origin_x or self.y != self.origin_y:
            self.path = world.path_find(self.x, self.y, self.origin_x, self.origin_y)

    def tracking(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return

        if self.path:
            self.propagate_path(world)
        elif self.x != int(common.player.x) or self.y != int(common.player.y):
            self.path = world.path_find(self.x, self.y, int(common.player.x), int(common.player.y))

    def wonder(self, world):
        pass
