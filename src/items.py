import time

import pygame
from src import common, powerup
from src.ghost import Ghost, GhostState


def add_health():
    common.player.health += 1


def set_speed():
    powerup.add_powerup(powerup.PowerUp.EXTRA_SPEED, 15)


def set_ghost_eatable():
    for dimension, _bg, _file, _unlocked in common.maps:
        for entity in dimension:
            if issubclass(entity.__class__, Ghost):
                if entity.state == GhostState.DEAD:
                    continue

                entity.load_random_path = True
                entity.state = GhostState.VULNERABLE
                entity.timer = time.perf_counter()
                entity.speed = entity.default_speed / 2

    powerup.add_powerup(powerup.PowerUp.EAT_GHOST, 10)


store_items = [
    {
        "name": "Extra Lives",
        "summary": "Heal player by 1 HP",
        "description": "This item gives you an extra life. There is no limit for how many lives you have. Lives can be very useful as "
                       "a backup for if you get eaten by a ghost.",
        "price": 90,
        "image": pygame.image.load(common.PATH / "assets/ghost.png"),
        "on_purchase": add_health
    }, {
        "name": "Speed Potion",
        "summary": "Double the player speed for 15 sec",
        "description": "The speed potion doubles your speed for FIFTEEN seconds. That is very fast! However, be "
                       "careful when using it, as you might run into ghosts quicker, and movement may be a bit harder "
                       "when fast.",
        "price": 50,
        "image": pygame.image.load(common.PATH / "assets/ghost.png"),
        "on_purchase": set_speed
    }, {
        "name": "Ghost-B-Gone",
        "summary": "Allows player to eat ghosts for 15 sec",
        "description": "This power up allows you to eat ghosts for 15 seconds, kind of like the pellet. However, don't get too carried "
                       "away, as the ghosts will start blinking once the powerup is ending, and will return to their original "
                       "state afterwards.",
        "price": 80,
        "image": pygame.image.load(common.PATH / "assets/ghost.png"),
        "on_purchase": set_ghost_eatable
    }
]
