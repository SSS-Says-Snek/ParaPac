from pygame.transform import rotate

from src import common, utils

TILE_SIZE = 16


class Tile:
    """
    Enum of ParaPac tile IDs
    """
    AIR = 0
    WALL = 1
    BARRIER = 2
    COIN = 3
    PELLET = 4

    RED_GHOST = 5
    PINK_GHOST = 6
    BLUE_GHOST = 7
    ORANGE_GHOST = 8

    SHOP = 9


TILE_DICT = {
    Tile.AIR: "air",
    Tile.WALL: "wall",
    Tile.BARRIER: "barrier",
    Tile.COIN: "coin",
    Tile.PELLET: "pellet",

    Tile.RED_GHOST: "red ghost",
    Tile.PINK_GHOST: "pink ghost",
    Tile.BLUE_GHOST: "blue ghost",
    Tile.ORANGE_GHOST: "orange ghost",

    Tile.SHOP: "shop"
}


PASSABLE_TILES = {
    Tile.AIR,
    Tile.BARRIER,
    Tile.COIN,
    Tile.PELLET,

    Tile.RED_GHOST,
    Tile.PINK_GHOST,
    Tile.BLUE_GHOST,
    Tile.ORANGE_GHOST,

    Tile.SHOP,
}

SOLID_TILES = {
    Tile.WALL
}

ANTI_PLAYER_TILES = {
    Tile.BARRIER,
    Tile.RED_GHOST,
    Tile.PINK_GHOST,
    Tile.BLUE_GHOST,
    Tile.ORANGE_GHOST
}

WALL_I, WALL_H, WALL_L, WALL_U, WALL_O, WALL_C = utils.load_sprite_sheet(
    common.PATH / "assets/wall.png", 3, 2
)

# WALL_I = load(join("assets", "wall_0.png")).convert_alpha()  # Faces right
# WALL_H = load(join("assets", "wall_1.png")).convert_alpha()  # Straight up
# WALL_L = load(join("assets", "wall_2.png")).convert_alpha()  # Edge points up-right
# WALL_U = load(join("assets", "wall_3.png")).convert_alpha()  # Just like U
# WALL_O = load(join("assets", "wall_4.png")).convert_alpha()  # Literally all sides

# C corner piece
WALL_C_UR = WALL_C
WALL_C_RD = rotate(WALL_C, -90)
WALL_C_DL = rotate(WALL_C, 180)
WALL_C_LU = rotate(WALL_C, 90)

WALLS = {
    # Checks if there are any air gaps with:
    # right, left, up, down
    (False, False, False, False): None,
    (True, True, True, True): WALL_O,

    # I parts
    (True, False, False, False): WALL_I,
    (False, False, False, True): rotate(WALL_I, -90),
    (False, True, False, False): rotate(WALL_I, 180),
    (False, False, True, False): rotate(WALL_I, 90),

    # H parts
    (True, True, False, False): WALL_H,
    (False, False, True, True): rotate(WALL_H, 90),

    # L parts
    (True, False, True, False): WALL_L,
    (True, False, False, True): rotate(WALL_L, -90),
    (False, True, False, True): rotate(WALL_L, 180),
    (False, True, True, False): rotate(WALL_L, 90),

    # U parts
    (True, True, False, True): WALL_U,
    (False, True, True, True): rotate(WALL_U, -90),
    (True, True, True, False): rotate(WALL_U, 180),
    (True, False, True, True): rotate(WALL_U, 90)
}
