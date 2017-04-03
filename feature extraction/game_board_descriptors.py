
COLS = 10
ROWS = 10

TOP_LEFT_COORDINATES = 0
CHUNK_WIDTH = 1
CHUNK_HEIGHT = 2

Y_POS = 0
X_POS = 1

TWO_DEEP = 2
TWO_WIDE = 2
THREE_WIDE = 3
FOUR_WIDE = 4

CHUNKS_TOP_LEFT_DIMENSIONS = {
    'A_10': [[9, 0], THREE_WIDE, TWO_DEEP],
    'A_8': [[7, 0], THREE_WIDE, TWO_DEEP],
    'A_6': [[5, 0], TWO_WIDE, TWO_DEEP],
    'A_4': [[3, 0], THREE_WIDE, TWO_DEEP],
    'A_2': [[1, 0], THREE_WIDE, TWO_DEEP],

    'D_10': [[9, 3], FOUR_WIDE, TWO_DEEP],
    'D_8': [[7, 3], FOUR_WIDE, TWO_DEEP],
    'E_6': [[5, 4], TWO_WIDE, TWO_DEEP],
    'D_4': [[3, 3], FOUR_WIDE, TWO_DEEP],
    'D_2': [[1, 3], FOUR_WIDE, TWO_DEEP],

    'H_10': [[9, 7], THREE_WIDE, TWO_DEEP],
    'H_8': [[7, 7], THREE_WIDE, TWO_DEEP],
    'H_6': [[5, 8], TWO_WIDE, TWO_DEEP],
    'H_4': [[3, 7], THREE_WIDE, TWO_DEEP],
    'H_2': [[1, 7], THREE_WIDE, TWO_DEEP]
}


def generate_chunk_coordinates() -> dict:
    """
    generate the coordinates of all chunks in CHUNKS_TOP_LEFT_DIMENSIONS based on the top left square of the chunk
    (row, col) and its width.
    :return: chunk name : list(location coordinates in that chunk)
    """
    chunk_dimensions = dict()
    for key, dimensions in CHUNKS_TOP_LEFT_DIMENSIONS:
        start_position = dimensions[TOP_LEFT_COORDINATES]
        chunk_width = dimensions[CHUNK_WIDTH]
        chunk_depth = dimensions[CHUNK_HEIGHT]
        row_index = start_position[Y_POS]
        col_index = start_position[X_POS]
        coordinates = list()
        for horizontal_tile in range(chunk_width):
            for vertical_tile in range(chunk_depth):# start-x + horizontaltile,  start-y - verticaltile
                current_row_index = row_index - vertical_tile
                current_col_index = col_index + horizontal_tile
                coordinate = [current_row_index, current_col_index]
                coordinates.append(coordinate)
        chunk_dimensions[key] = coordinates
    return chunk_dimensions
