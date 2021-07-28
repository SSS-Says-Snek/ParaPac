import os
import random
import time

from src import common, utils, pathfinding
from src.entity import *
from typing import Any

GHOST_TEMPLATE = utils.load_sprite_sheet(os.path.join("assets", "ghost.png"), 2, 2)
GHOST_VULNERABLE = utils.load_sprite_sheet(os.path.join("assets", "ghost_vulnerable.png"), 2, 2)


class GhostAttributes:
    RED_COLOR = (255, 0, 0)
    PINK_COLOR = (255, 0, 255)
    BLUE_COLOR = (0, 0, 255)
    ORANGE_COLOR = (255, 255, 0)


class GhostState:
    NONE = 0
    CHASING = 1
    VULNERABLE = 2
    TRANSITION = 3
    SCATTER = 4
    DEAD = 5


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
        self.default_speed = speed
        self.speed = speed
        self.state = GhostState.CHASING
        self.timer = 0
        self.vulnerable_period = vulnerable_period
        self.transition_period = transition_period

        self.default_scatter_length = 8
        self.scatter_length = self.default_scatter_length
        self.default_chasing_length = 30
        self.chasing_length = self.default_chasing_length
        self.scatter_timer = time.perf_counter()

        self.path = []
        self.eyes = [frame.copy() for frame in GHOST_TEMPLATE]
        self.frames = [frame.copy() for frame in GHOST_TEMPLATE]
        self.direction = Direction.UP

        self.load_random_path = False
        self.scatter_tile: Any = None

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
            if (self.state == GhostState.CHASING or self.state == GhostState.SCATTER) and not common.player.immune:
                if not common.DEBUG:
                    common.sfx.stop()
                    common.sfx.play(common.pacman_die_sfx)
                    common.player.task = common.player.die
            else:
                self.state = GhostState.DEAD

                if common.player.task != common.player.die and self.task != self.go_home:
                    common.sfx.stop()
                    common.sfx.play(common.pacman_eat_ghost_sfx)

        if self.state == GhostState.CHASING:
            self.task = self.tracking

            # if (time.perf_counter() - self.scatter_timer) % 2 > 1.5:
            #     print(time.perf_counter() - self.scatter_timer)
            if time.perf_counter() - self.scatter_timer > self.chasing_length:
                if self.chasing_length != self.default_chasing_length:
                    self.chasing_length = self.default_chasing_length
                print("TRANSITIONING")
                self.scatter_timer = time.perf_counter()
                self.state = GhostState.SCATTER
        elif self.state == GhostState.VULNERABLE:
            if time.perf_counter() - self.timer > self.vulnerable_period:
                self.state = GhostState.TRANSITION
                self.timer = time.perf_counter()
        elif self.state == GhostState.TRANSITION:
            if time.perf_counter() - self.timer > self.transition_period:
                self.state = GhostState.CHASING
                self.scatter_timer = time.perf_counter()
        elif self.state == GhostState.SCATTER:
            self.task = self.scatter
            if time.perf_counter() - self.scatter_timer > self.scatter_length:
                if self.scatter_length != self.default_scatter_length:
                    self.scatter_length = self.default_scatter_length
                self.scatter_timer = time.perf_counter()
                self.state = GhostState.CHASING
        elif self.state == GhostState.DEAD:
            self.task = self.go_home
            if self.x == self.origin_x and self.y == self.origin_y:
                self.scatter_timer = time.perf_counter()
                self.state = GhostState.CHASING
                self.speed = self.default_speed

        if self.state == GhostState.CHASING or self.state == GhostState.SCATTER:
            self.frame = self.frames[self.direction]
        elif self.state == GhostState.VULNERABLE:
            if self.load_random_path:
                while True:
                    random_pos = (random.randint(0, len(world.tile_map) - 1),
                                  random.randint(0, len(world.tile_map[0]) - 1))
                    if world.tile_map[random_pos[0], random_pos[1]] not in tiles.SOLID_TILES:
                        self.path = world.path_find(self.x, self.y, *random_pos)
                        self.load_random_path = False
                        break

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
                               ignore_collision=self.state != GhostState.CHASING)
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

            if self.path is None:
                # Staks should turn to wander_to_movable_tile, but that's broken rn
                pass

    def scatter(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return

        if self.path:
            self.propagate_path(world)
        elif self.x != self.scatter_tile[0] or self.y != self.scatter_tile[1]:
            self.path = world.path_find(self.x, self.y, *self.scatter_tile)

    def wander_to_movable_tile(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return
        path = world.path_find(self.x, self.y, int(common.player.x), int(common.player.y))
        if path is not None:
            self.task = self.tracking
        else:
            pass

    def wonder(self, world):
        pass


class BlinkyGhost(Ghost):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_tile = (38, 1)


class PinkyGhost(Ghost):
    """Ghost AI for Pinky (The pink ghost)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_tile = (1, 1)

    def tracking(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return

        if self.path:
            self.propagate_path(world)
        elif self.x != int(common.player.x) or self.y != int(common.player.y):
            adjusted_x = common.player.x
            adjusted_y = common.player.y

            if common.player.direction == Direction.RIGHT:
                adjusted_x = min(adjusted_x + 4, len(world.tile_map) - 2)
            elif common.player.direction == Direction.LEFT:
                adjusted_x = max(adjusted_x - 4, 0)
            elif common.player.direction == Direction.UP:
                adjusted_x = max(adjusted_x - 4, 0)
                adjusted_y = max(adjusted_y - 4, 0)
            elif common.player.direction == Direction.DOWN:
                adjusted_y = min(adjusted_y + 4, len(world.tile_map[0]) - 2)

            adjusted_x, adjusted_y = int(adjusted_x), int(adjusted_y)

            while world.get_at(adjusted_x, adjusted_y) in tiles.SOLID_TILES:
                try:
                    adjusted_x, adjusted_y = random.choice(
                        pathfinding.get_neighbors(
                            pathfinding.array_to_class(world.tile_map),
                            (adjusted_x, adjusted_y)
                        )
                    )
                except IndexError:
                    adjusted_x, adjusted_y = int(common.player.x), int(common.player.y)

            self.path = world.path_find(self.x, self.y, adjusted_x, adjusted_y)


class InkyGhost(Ghost):
    """Ghost AI for Inky (The cyan ghost)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_tile = (38, 30)

    def tracking(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return

        if self.path:
            self.propagate_path(world)
        elif self.x != int(common.player.x) or self.y != int(common.player.y):
            current_blinky_distance = float('inf')
            nearest_blinky = None
            for entity in world.entities:
                if isinstance(entity, BlinkyGhost):
                    if pathfinding.euclidean((entity.x, entity.y),
                                             (common.player.x, common.player.y)) < current_blinky_distance:
                        current_blinky_distance = pathfinding.euclidean((entity.x, entity.y),
                                                                        (common.player.x, common.player.y))
                        nearest_blinky = entity
            vec = pygame.Vector2(nearest_blinky.x - self.x, nearest_blinky.y - self.y)
            vec = vec.rotate(180)
            adjusted_x = int(max(min(common.player.x - vec.x, len(world.tile_map) - 2), 1))
            adjusted_y = int(max(min(common.player.y - vec.y, len(world.tile_map[0]) - 2), 1))

            while world.get_at(adjusted_x, adjusted_y) in tiles.SOLID_TILES:
                try:
                    adjusted_x, adjusted_y = random.choice(
                        pathfinding.get_neighbors(
                            pathfinding.array_to_class(world.tile_map),
                            (adjusted_x, adjusted_y)
                        )
                    )
                except IndexError:
                    adjusted_x, adjusted_y = int(common.player.x), int(common.player.y)

            self.path = world.path_find(self.x, self.y, adjusted_x, adjusted_y)


class ClydeGhost(Ghost):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_tile = (1, 30)

    def tracking(self, world):
        if common.player not in world.entities:
            self.task = self.wonder
            return

        if self.path:
            self.propagate_path(world)
        elif self.x != int(common.player.x) or self.y != int(common.player.y):
            if pathfinding.euclidean((self.x, self.y), (common.player.x, common.player.y)) > 16:
                self.path = world.path_find(self.x, self.y, int(common.player.x), int(common.player.y))
            else:
                self.path = world.path_find(self.x, self.y, self.scatter_tile[0], self.scatter_tile[1])
