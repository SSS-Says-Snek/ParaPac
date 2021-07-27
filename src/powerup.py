import time


class PowerUp:
    DEBUG_POWER = -1
    I_AM_SPEED = 0
    PASS_THROUGH_WALLS = 1
    SEE_STUFF = 2


# Power : [start_time, duration, image, name]
powerups = {
    PowerUp.DEBUG_POWER: [0, 15, "", "DEBUG"],
    PowerUp.I_AM_SPEED: [0, 13, "", "Speed"],
    PowerUp.PASS_THROUGH_WALLS: [0, 20, "", "Wall Hax"],
    PowerUp.SEE_STUFF: [0, 10, "", "See Stuff"]
}


def is_powerup_on(powerup):
    return not (powerups[powerup][0] == 0 and powerups[powerup][1] == 0)


def add_powerup(powerup, duration):
    if is_powerup_on(powerup):
        powerups[powerup][1] += duration
    else:
        powerups[powerup][0] = time.perf_time()
        powerups[powerup][1] = duration
