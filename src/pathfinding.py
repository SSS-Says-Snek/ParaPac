from src.tiles import SOLID_TILES
from src.entity import Direction

import numpy

from math import inf
from queue import PriorityQueue
from typing import List, Tuple, Union, Callable


class Node:
    def __init__(self, value, pos):
        """Class representing a node, with value and node position"""
        self.value = value
        self.pos = pos


def manhattan(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculates h-score, via manhattan  (best-case for this usage)"""
    return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])


def euclidean(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculates h-score, via euclidean distance"""
    return ((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2) ** 0.5


def get_neighbors(array: numpy.array, pos: Tuple[int, int], omitted_direction: int = None,
                  omitted_neighbors=()) -> List:
    """Gets all PASSABLE neighbors of a given point"""
    neighbors = []
    left = [pos[0] - 1, pos[1]]
    down = [pos[0], pos[1] + 1]
    right = [pos[0] + 1, pos[1]]
    up = [pos[0], pos[1] - 1]
    if left[0] >= 0 and array[left[0], left[1]].value not in SOLID_TILES and omitted_direction != Direction.LEFT:
        neighbors.append(left)
    if right[0] < len(array[0]) and array[right[0], right[1]].value not in SOLID_TILES and \
            omitted_direction != Direction.RIGHT:
        neighbors.append(right)
    if up[1] >= 0 and array[up[0], up[1]].value not in SOLID_TILES and omitted_direction != Direction.UP:
        neighbors.append(up)
    if down[1] < len(array[1]) and array[down[0], down[1]].value not in SOLID_TILES and \
            omitted_direction != Direction.DOWN:
        neighbors.append(down)

    for omitted_neighbor in omitted_neighbors:
        try:
            neighbors.remove(omitted_neighbor)
        except ValueError:
            pass
    return neighbors


def get_all_movable_tiles(array: numpy.array, pos: Tuple[int, int]) -> List:
    # TODO: AAAAAAAAAAAA HELP I DON'T KNOW RECURSION THAT WELLLLLLLLLLLLLLLLLLLLL - SSS-Says-Snek
    all_neighbors = []

    def recursion_func(arr, p):
        nonlocal all_neighbors
        for neighbor in get_neighbors(arr, p):
            if neighbor not in all_neighbors:
                all_neighbors.append(neighbor)
            for neighbor_of_neighbor in get_neighbors(arr, neighbor, omitted_neighbors=all_neighbors):
                print(all_neighbors)
                if get_neighbors(arr, neighbor_of_neighbor) and neighbor_of_neighbor not in all_neighbors:
                    get_all_movable_tiles(arr, neighbor_of_neighbor)

    recursion_func(array, pos)
    return all_neighbors


def array_to_class(array: numpy.array) -> numpy.array:
    """Converts all elements of a numpy array into a Node instance"""
    return numpy.array(
        [[Node(value, (x, y)) for y, value in enumerate(row)]
         for x, row in enumerate(array)])


def reconstruct_path(path_outputted: dict, start: Tuple[int, int], end: Tuple[int, int]) -> List:
    """
    As `algorithm` outputs a dict of last tracebacks, this function
    converts the Node instances back into positions, then link the positions
    back to a list
    """
    reconstructed_dict = {}
    for key, value in path_outputted.items():
        reconstructed_dict[key.pos] = value.pos
    result = []
    while end in reconstructed_dict:
        result.append((end[1], end[0]))
        end = reconstructed_dict[end]
    result.append(start)
    result.reverse()
    return result


def algorithm(array: numpy.array, start: Tuple[int, int], end: Tuple[int, int],
              heuristic: Callable = manhattan) -> Union[List, None]:
    """
    Returns a list of all points, for the path between `start` and `end`
    :param array: a numpy array of Node instances
    :param start: a tuple (or list) of points corresponding to where to start on array
    :param end: like start, but for the end
    :param heuristic: a function that represents the heuristic (default: manhattan heuristic)
    Example:
    >>> test = numpy.array(
        [[0, 0, 0, 0, 0, 1],
         [0, 1, 1, 1, 0, 1],
         [0, 1, 0, 0, 0, 1],
         [0, 1, 0, 1, 1, 1],
         [0, 0, 0, 0, 1, 0],
         [1, 1, 1, 0, 0, 0]]
        )
    >>> print(algorithm(test, (0, 0), (5, 5)))
    """
    array = array_to_class(array)

    actual_start = array[start[0], start[1]]
    actual_end = array[end[0], end[1]]
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, actual_start))
    came_from = {}
    g_score = {node: inf for row in array for node in row}
    f_score = {node: inf for row in array for node in row}
    g_score[actual_start] = 0
    f_score[actual_start] = heuristic(start, end)
    open_set_hash = {actual_start}
    while not open_set.empty():
        current = open_set.get()[2]
        current_pos = current.pos
        open_set_hash.remove(current)
        if current == actual_end:
            return reconstruct_path(came_from, start, end)
        for neighbor in get_neighbors(array, current_pos):
            neighbor_instance = array[neighbor[0], neighbor[1]]
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor_instance]:
                came_from[neighbor_instance] = current
                g_score[neighbor_instance] = temp_g_score
                f_score[neighbor_instance] = temp_g_score + heuristic(neighbor, end)
                if neighbor_instance not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor_instance], count, neighbor_instance))
                    open_set_hash.add(neighbor_instance)
    return None


if __name__ == "__main__":
    # Test stuff for snek (maybe someone else can help me with the recursive func?)
    from src import common, utils
    import types
    import sys

    sys.setrecursionlimit(4000)

    data = utils.load_map_data(common.PATH / "maps/map_a.txt")
    result = get_all_movable_tiles(array_to_class(data), (12, 15))
    print(result)
