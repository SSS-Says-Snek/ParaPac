import os
import time

from src import common, interrupt, utils, powerup
from src.tiles import Tile
from src.ghost import Ghost, GhostState
from src.entity import *
from src.states import *

SPEED = 0.125  # MUST have a base power of 2, otherwise floating precision errors go brr

_PACMAN_EAT = utils.load_sprite_sheet(os.path.join("assets", "pacman_eat.png"), 4, 2)
PACMAN_EAT = [[pygame.transform.rotate(frame, rotation) for frame in _PACMAN_EAT]
              for rotation in (0, 180, 90, -90)]

_PACMAN_DIE = utils.load_sprite_sheet(os.path.join("assets", "pacman_die.png"), 4, 5)
PACMAN_DIE = [[pygame.transform.rotate(frame, rotation) for frame in _PACMAN_DIE]
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
        self.dead = -1  # Also acts as an animation frame counter
        self.health = 3

        self.immunity_duration = 4
        self.immune = False
        self.immunity_timer = time.perf_counter()

        self.moved_after_shop_exit = None
        self.moved_after_shop_exit_timer = 0

        self.debug_tile = Tile.WALL

    def update(self, world):
        if self.dead >= 0:
            return
        if self.moved_after_shop_exit and time.perf_counter() - self.moved_after_shop_exit_timer > 1:
            self.moved_after_shop_exit = None

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.next_direction = Direction.UP
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.next_direction = Direction.LEFT
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.next_direction = Direction.DOWN
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.next_direction = Direction.RIGHT

        if not common.DEBUG:
            tile = world.get_at(int(self.x), int(self.y))
            if tile == Tile.COIN:
                world.set_at(int(self.x), int(self.y), Tile.AIR)
                common.score += 10
                common.coins += 1
                if not common.sfx.get_busy():
                    common.sfx.play(common.pacman_eat_sfx)
            elif tile == Tile.PELLET:
                world.set_at(int(self.x), int(self.y), Tile.AIR)
                common.score += 100

                common.sfx.stop()
                common.sfx.play(common.pacman_pellet_sfx)
                for entity in world.entities:
                    if issubclass(entity.__class__, Ghost):
                        entity.load_random_path = True
                        entity.state = GhostState.VULNERABLE
                        entity.timer = time.perf_counter()
                        entity.speed = entity.default_speed / 2
            elif tile == Tile.SHOP and (self.moved_after_shop_exit is None):
                self.x, self.y = int(self.x), int(self.y)
                common.game_loop.state.change_state(ShopState)

    def debug(self, world):
        mx, my = pygame.mouse.get_pos()
        left_click, middle_click, right_click = pygame.mouse.get_pressed(3)
        x, y = utils.to_world_space(mx, my)

        rect = pygame.Surface((tiles.TILE_SIZE, tiles.TILE_SIZE), pygame.SRCALPHA)
        rect.fill((255, 255, 0, 128))
        world.overlay.blit(rect, (int(x) * tiles.TILE_SIZE, int(y) * tiles.TILE_SIZE))

        if left_click:
            world.set_at(int(x), int(y), self.debug_tile)
        elif middle_click:
            world.set_at(int(x), int(y), Tile.COIN)
        elif right_click:
            world.set_at(int(x), int(y), Tile.AIR)

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
            self.frame = PACMAN_EAT[self.direction][int(time.perf_counter() *
                                                        len(_PACMAN_EAT) * 4) % len(_PACMAN_EAT)]

            if self.moved_after_shop_exit is False:
                self.moved_after_shop_exit = True
                self.moved_after_shop_exit_timer = time.perf_counter()
        else:
            self.frame = PACMAN_EAT[self.direction][-1]

        if self.immune and time.perf_counter() - self.immunity_timer > self.immunity_duration:
            self.immune = False

    def die(self, world):
        if self.dead < 0:
            if self.health > 0:
                self.health -= 1
                self.immune = True
                self.immunity_timer = time.perf_counter()

                powerup.add_powerup(powerup.PowerUp.IMMUNITY, 4)

                for entity in common.active_map.entities:
                    if issubclass(entity.__class__, Ghost):
                        entity.task = entity.scatter
                        entity.scatter_timer = time.perf_counter()
                        entity.scatter_length = 4
                        entity.path = world.path_find(entity.x, entity.y, *entity.scatter_tile)
                print(self.health)
            self.dead = 0
        elif self.dead >= len(_PACMAN_DIE) and self.health == 0:
            raise interrupt.GameOver

        try:
            self.frame = PACMAN_DIE[self.direction][int(self.dead)]
        except IndexError:
            common.player.task = common.player.forward
            self.dead = -1

        self.dead += 0.25

    def teleport(self, world):
        pass
