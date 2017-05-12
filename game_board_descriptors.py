import rank_encodings as ranks
import numpy as np

FIRST_TILE = 0
COLS = 10
ROWS = 10
PLAYERS = 2
STARTING_PIECES_AMOUNT = 40
STARTING_PIECES_TOTAL_VALUE = 1451.53

TOP_LEFT_COORDINATES = 0
CHUNK_WIDTH = 1
CHUNK_HEIGHT = 2
BOTTOM = -1
TOP = 1

Y_POS = 0
X_POS = 1

CHAR_COLON = ":"
COLON_VALUE = 10
DIRECTIONS = 4
LEFT = -1
RIGHT = 1
UP = 1
DOWN = -1

TWO_DEEP = 2
TWO_WIDE = 2
THREE_WIDE = 3
FOUR_WIDE = 4

A_10 = "A_10"
A_8 = "A_8"
A_6 = "A_6"
A_4 = "A_4"
A_2 = "A_2"

D_10 = "D_10"
D_8 = "D_8"
E_6 = "E_6"
D_4 = "D_4"
D_2 = "D_2"

H_10 = "H_10"
H_8 = "H_8"
I_6 = "I_6"
H_4 = "H_4"
H_2 = "H_2"


CHUNKS_TOP_LEFT_DIMENSIONS = {
    A_10: [[9, 0], THREE_WIDE, TWO_DEEP],
    A_8: [[7, 0], THREE_WIDE, TWO_DEEP],
    A_6: [[5, 0], TWO_WIDE, TWO_DEEP],
    A_4: [[3, 0], THREE_WIDE, TWO_DEEP],
    A_2: [[1, 0], THREE_WIDE, TWO_DEEP],

    D_10: [[9, 3], FOUR_WIDE, TWO_DEEP],
    D_8: [[7, 3], FOUR_WIDE, TWO_DEEP],
    E_6: [[5, 4], TWO_WIDE, TWO_DEEP],
    D_4: [[3, 3], FOUR_WIDE, TWO_DEEP],
    D_2: [[1, 3], FOUR_WIDE, TWO_DEEP],

    H_10: [[9, 7], THREE_WIDE, TWO_DEEP],
    H_8: [[7, 7], THREE_WIDE, TWO_DEEP],
    I_6: [[5, 8], TWO_WIDE, TWO_DEEP],
    H_4: [[3, 7], THREE_WIDE, TWO_DEEP],
    H_2: [[1, 7], THREE_WIDE, TWO_DEEP]
}


def generate_chunk_coordinates(coordinate_starting_positions):
    """
    generate the coordinates of all chunks in CHUNKS_TOP_LEFT_DIMENSIONS based on the top left square of the chunk
    (row, col) and its width.
    :return: chunk name : list(location coordinates in that chunk)
    """
    chunk_dimensions = dict()
    for key in coordinate_starting_positions.keys():
        dimensions = coordinate_starting_positions[key]
        start_position = dimensions[TOP_LEFT_COORDINATES]
        chunk_width = dimensions[CHUNK_WIDTH]
        chunk_depth = dimensions[CHUNK_HEIGHT]
        row_index = start_position[Y_POS]
        col_index = start_position[X_POS]
        coordinates = list()
        for horizontal_tile in range(chunk_width):
            for vertical_tile in range(chunk_depth):
                current_row_index = row_index - vertical_tile
                current_col_index = col_index + horizontal_tile
                coordinate = [current_row_index, current_col_index]
                coordinates.append(coordinate)
        chunk_dimensions[key] = coordinates
    return chunk_dimensions


def tile_can_be_moved_to(tile, grid):
    """
    check if a tile is empty (so can be a target for movement)
    :param tile: [y,x]
    :param grid: grid representing the board
    :return: whether the tile is empty
    """
    try:
        if grid[tile[Y_POS], tile[X_POS]] == ranks.EMPTY_TILE:
            return True
        return False
    except IndexError:
        return False
