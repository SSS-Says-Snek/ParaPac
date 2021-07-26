import numpy as np
from src import common, utils
from src.tiles import SOLID_TILES
from src.entity import Direction


def distance(pos1, pos2):
    """
    Calculates (x2-x1)^2 + (y2-y1)^2 (square rooting doesn't matter in this case,
    it'll just slow things down)
    """
    return (pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2


def get_neighbors(world, ghost_dir, tile_pos):
    """
    Returns a PASSABLE dict above, below, right, and left of the given tile
    """
    tile_x = tile_pos[0]
    tile_y = tile_pos[1]
    tiles_obj = {
        Direction.LEFT: world.tile_map[tile_x - 1, tile_y],
        Direction.RIGHT: world.tile_map[tile_x + 1, tile_y],
        Direction.DOWN: world.tile_map[tile_x, tile_y + 1],
        Direction.UP: world.tile_map[tile_x, tile_y - 1]
    }
    tiles_pos = {
        Direction.LEFT: (tile_x - 1, tile_y),
        Direction.RIGHT: (tile_x + 1, tile_y),
        Direction.DOWN: (tile_x, tile_y + 1),
        Direction.UP: (tile_x, tile_y - 1)
    }
    # Remove the tile for opposite direction
    del tiles_obj[list(tiles_obj.keys()).index(ghost_dir)]
    passable_tiles = {}
    for direction, tile in tiles_obj.items():
        if tile not in SOLID_TILES:
            passable_tiles[direction] = tiles_pos[direction]
    return passable_tiles


def get_neighbors_2(world, ghost_dir, tile_pos):
    """
    Returns a PASSABLE dict above, below, right, and left of the given tile
    """
    tile_x = tile_pos[0]
    tile_y = tile_pos[1]
    tiles_obj = {
        Direction.LEFT: [world.tile_map[tile_x - 1, tile_y], world.tile_map[tile_x - 1, tile_y + 1]],
        Direction.RIGHT: [world.tile_map[tile_x + 2, tile_y], world.tile_map[tile_x + 2, tile_y + 1]],
        Direction.DOWN: [world.tile_map[tile_x, tile_y + 2], world.tile_map[tile_x + 1, tile_y + 2]],
        Direction.UP: [world.tile_map[tile_x, tile_y - 1], world.tile_map[tile_x + 1, tile_y - 1]]
    }
    tiles_pos = {
        Direction.LEFT: [(tile_x - 1, tile_y), (tile_x - 1, tile_y + 1)],
        Direction.RIGHT: [(tile_x + 2, tile_y), (tile_x + 2, tile_y + 1)],
        Direction.DOWN: [(tile_x, tile_y + 2), (tile_x + 1, tile_y + 2)],
        Direction.UP: [(tile_x, tile_y - 1), (tile_x + 1, tile_y - 1)]
    }
    # Remove the tile for opposite direction
    del tiles_obj[list(tiles_obj.keys()).index(ghost_dir)]
    passable_tiles = {}
    for direction, tiles in tiles_obj.items():
        for tile in tiles:
            if tile not in SOLID_TILES:
                passable_tiles[direction] = tiles_pos[direction]
    return passable_tiles


def blinky_ai(tile_neighbors, pacman_pos):
    """
    Given all passable tile neighbors, and the pacman position,
    return the direction of the move, and the next tile of the move
    """
    neighbor_dict = {}
    rev_neighbor_dict = {}
    for direction, neighbor in tile_neighbors.items():
        neighbor_distance = distance(pacman_pos, neighbor)
        neighbor_dict[direction] = [neighbor_distance, neighbor]
        rev_neighbor_dict[neighbor_distance] = [direction, neighbor]
    distances = [value[0] for value in neighbor_dict.values()]
    min_distance = min(distances)
    min_distance_neighbor = rev_neighbor_dict[min_distance][1]
    min_distance_direction = rev_neighbor_dict[min_distance][0]

    return min_distance_neighbor, min_distance_direction


def blinky_ai_2(tile_neighbors, pacman_pos):
    """
    Given all passable tile neighbors, and the pacman position,
    return the direction of the move, and the next tile of the move
    """
    neighbor_dict = {}
    rev_neighbor_dict = {}
    for direction, neighbors in tile_neighbors.items():
        neighbor = ((neighbors[0][0] + neighbors[1][0])/2, (neighbors[0][1] + neighbors[1][1])/2)
        neighbor_distance = distance(utils.from_world_space(*pacman_pos), neighbor)
        neighbor_dict[direction] = [neighbor_distance, neighbor]
        rev_neighbor_dict[neighbor_distance] = [direction, neighbor]
    distances = [value[0] for value in neighbor_dict.values()]
    try:
        min_distance = min(distances)
        min_distance_neighbor = rev_neighbor_dict[min_distance][1]
        min_distance_direction = rev_neighbor_dict[min_distance][0]
    except ValueError:
        min_distance_neighbor = None
        min_distance_direction = None

    return min_distance_neighbor, min_distance_direction
