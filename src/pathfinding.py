from src.tiles import SOLID_TILES
from src import common

import numpy as np

from math import inf
from queue import PriorityQueue
from typing import List, Tuple, Union


class Node:
    def __init__(self, value, pos):
        """Class representing a node, with value and node position"""
        self.value = value
        self.pos = pos


def move_segment(segment_to_move, axis, increment):
    reconstructed_segment = []
    for segment_point in segment_to_move:
        segment_point[axis] += increment
        reconstructed_segment.append(segment_point)
    return reconstructed_segment


def h(pos1: Tuple, pos2: Tuple[int, int]) -> float:
    """Calculates h-score, via manhattan  (best-case for this usage)"""
    return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])


def get_neighbors(array: np.array, pos: Tuple[int, int]) -> List:
    """Gets all PASSABLE neighbors of a given point"""
    neighbors = []
    left = [pos[0] - 1, pos[1]]
    down = [pos[0], pos[1] + 1]
    right = [pos[0] + 1, pos[1]]
    up = [pos[0], pos[1] - 1]
    if left[0] >= 0 and array[left[0], left[1]].value not in SOLID_TILES:
        neighbors.append(left)
    if right[0] < len(array[0]) and array[right[0], right[1]].value not in SOLID_TILES:
        neighbors.append(right)
    if up[1] >= 0 and array[up[0], up[1]].value not in SOLID_TILES:
        neighbors.append(up)
    if down[1] < len(array[1]) and array[down[0], down[1]].value not in SOLID_TILES:
        neighbors.append(down)
    return neighbors


def array_to_class(array: np.array) -> np.array:
    """Converts all elements of a numpy array into a Node instance"""
    return np.array(
        [[Node(value, (x, y)) for y, value in enumerate(row)]
         for x, row in enumerate(array)])


def tuple_to_list(list_to_cvrt):
    reconstructed_list = []
    for tup in list_to_cvrt:
        reconstructed_list.append(list(tup))
    return reconstructed_list


def list_to_tuple(tup_to_cvrt):
    reconstructed_tuple = []
    for lst in tup_to_cvrt:
        reconstructed_tuple.append(tuple(lst))
    return reconstructed_tuple


def reconstruct_path(path_outputted: dict, start: Tuple[int, int], end: Tuple[int, int], humanify: bool = False) -> List:
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
        if humanify:
            result.append(end)
        else:
            result.append((end[1], end[0]))
        end = reconstructed_dict[end]

    if humanify:
        result.append(start)
    else:
        result.append((start[1], start[0]))
    result.reverse()
    return result


def algorithm(array: np.array, start: Tuple[int, int], end: Tuple[int, int], humanify: bool = False) -> Union[List, None]:
    """
    Returns a list of all points, for the path between `start` and `end`

    :param array: a np array of Node instances
    :param start: a tuple (or list) of points corresponding to where to start on array
    :param end: like start, but for the end
    :param humanify: Humanifies the outputs to (x, y) instead of (y, x)

    Example:
    >>> test = np.array(
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
    f_score[actual_start] = h(start, end)
    open_set_hash = {actual_start}
    while not open_set.empty():
        current = open_set.get()[2]
        current_pos = current.pos
        open_set_hash.remove(current)
        if current == actual_end:
            return reconstruct_path(came_from, start, end, humanify)
        for neighbor in get_neighbors(array, current_pos):
            neighbor_instance = array[neighbor[0], neighbor[1]]
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor_instance]:
                came_from[neighbor_instance] = current
                g_score[neighbor_instance] = temp_g_score
                f_score[neighbor_instance] = temp_g_score + h(neighbor, end)
                if neighbor_instance not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor_instance], count, neighbor_instance))
                    open_set_hash.add(neighbor_instance)
    return None


if __name__ == '__main__':
    # Test code; will not be run
    with open(common.PATH / "maps/map_a.txt") as r:
        rows = r.read().split('\n')

        for row in rows:
            if not row:
                rows.remove(row)

        data = np.zeros((len(rows[0]), len(rows)), dtype=np.uint8)
        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                data[x, y] = int(tile)

    e = algorithm(data, (14, 11), (19, 29), True)
    segments = []
    segments_extra = []
    prev_point = None
    prev_direction = None
    j = 0
    for i, point in enumerate(e):
        try:
            if point[0] - prev_point[0] > 0 and point[1] - prev_point[1] == 0:
                direction = "right"
            elif point[0] - prev_point[0] < 0 and point[1] - prev_point[1] == 0:
                direction = "left"
            elif point[0] - prev_point[0] == 0 and point[1] - prev_point[1] < 0:
                direction = "up"
            elif point[0] - prev_point[0] == 0 and point[1] - prev_point[1] > 0:
                direction = "down"
            else:
                direction = None
            if direction is not None and direction != prev_direction:
                segments.append(e[j:i])
                segments_extra.append([e[j:i], prev_direction])
                j = i
            prev_direction = direction
        except Exception as f:
            print(f)
        prev_point = point

    start_segment = segments[0][0]
    del segments[0]
    segments[0].insert(0, start_segment)

    start_segment = segments_extra[0][0][0]
    del segments_extra[0]
    segments_extra[0][0].insert(0, start_segment)
    print(segments_extra)

    offsetted_path = []
    prev_segment_idx = None

    reconstructed_segments = []
    for i, segment in enumerate(segments_extra):
        if i - 1 >= 0:
            prev_segment = segments_extra[i - 1]
        else:
            prev_segment = [None, None]

        prev_segment, prev_direction = prev_segment
        actual_segment, direction = segment
        reconstructed_segment = []
        if prev_direction is not None:
            if prev_direction == "right" and direction == "up":
                segments_extra[i - 1][0].append((prev_segment[-1][0] + 1, prev_segment[-1]))
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 0, 1)
                print(i, reconstructed_segment)
            elif prev_direction == "up" and direction == "left":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 1, -1)
                print(i, reconstructed_segment)
            elif prev_direction == "left" and direction == "down":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 0, -1)
                print(i, reconstructed_segment)
            elif prev_direction == "down" and direction == "right":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 1, -1)
                print(i, reconstructed_segment)
            elif prev_direction == "right" and direction == "down":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 0, 1)
                print(i, reconstructed_segment)
            elif prev_direction == 'down' and direction == "left":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 1, 1)
                print(i, reconstructed_segment)

        else:
            if direction == "right":
                reconstructed_segment = move_segment(tuple_to_list(actual_segment), 1, 1)
                print(i, reconstructed_segment)
            elif direction == "down":
                pass
        reconstructed_segments.append(reconstructed_segment)
    print(reconstructed_segments)
