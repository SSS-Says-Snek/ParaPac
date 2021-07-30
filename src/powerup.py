import time
from src import common


class PowerUp:
    DEBUG_POWER = -1
    EXTRA_SPEED = 0
    PASS_THROUGH_WALLS = 1
    SEE_STUFF = 2
    IMMUNITY = 3


# Power : [start_time, duration, image, font_surface]
powerups = {
    PowerUp.DEBUG_POWER: [0, 0, "", common.font.render("Powerup!", False, (255, 255, 255))],
    PowerUp.EXTRA_SPEED: [0, 0, "", common.font.render("Speed", False, (255, 255, 255))],
    PowerUp.PASS_THROUGH_WALLS: [0, 0, "", common.font.render("Wall Hax", False, (255, 255, 255))],
    PowerUp.SEE_STUFF: [0, 0, "", common.font.render("See Stuff", False, (255, 255, 255))],
    PowerUp.IMMUNITY: [0, 0, "", common.font.render("Immunity", False, (255, 255, 255))]
}


def is_powerup_on(powerup):
    return not (powerups[powerup][0] == 0 and powerups[powerup][1] == 0)


def add_powerup(powerup, duration):
    if is_powerup_on(powerup):
        powerups[powerup][1] += duration
    else:
        powerups[powerup][0] = time.perf_counter()
        powerups[powerup][1] = duration


def pause():
    for powerup, data in powerups.items():
        if is_powerup_on(powerup):
            powerups[powerup][1] = (data[0] + data[1]) - time.perf_counter()


def unpause():
    for powerup, data in powerups.items():
        if is_powerup_on(powerup):
            powerups[powerup][0] = time.perf_counter()
