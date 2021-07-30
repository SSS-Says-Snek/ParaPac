import pygame
from src import common, powerup


def add_health():
    common.player.health += 1


def set_speed():
    powerup.add_powerup(powerup.PowerUp.EXTRA_SPEED, 15)


store_items = [
    {
        "name": "Medkit",
        "summary": "Heal player by 1 HP",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin risus in "
                       "nisi gravida tincidunt in eu nisi. Vivamus in ligula ac massa congue blandit facilisis "
                       "vel urna. Donec efficitur augue justo, in sollicitudin tortor auctor non. Phasellus id "
                       "turpis auctor, lacinia orci ac, auctor justo.",
        "price": 25,
        "image": pygame.image.load(common.PATH / "assets/ghost.png"),
        "on_purchase": add_health
    }
    for _ in range(7)
]

store_items.append(
    {
        "name": "Speed Potion",
        "summary": "Double the player speed for 15 sec",
        "description": "The speed potion doubles your speed for FIFTEEN seconds. That is very fast! However, be "
                       "careful when using it, as you might run into ghosts quicker, and movement may be a bit harder "
                       "when fast.",
        "price": 20,
        "image": pygame.image.load(common.PATH / "assets/ghost.png"),
        "on_purchase": set_speed
    }
)
