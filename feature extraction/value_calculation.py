import string
import sys
import math
import numpy as np
sys.path.append("../")
import rank_encodings as ranks
import game_board_descriptors as board
import utils


ONE = 1
TWO =  2
THREE = 3
FIRST = 0
EMPTY = 0
HIGHEST = 1
RED_HIGHEST_RANK_CODE = 12
RANK_DIFFERENCE_FACTOR = 1.45
LAST_ITEM = -1
INCREMENT_ONE = 1

BOMB_VALUE_MODIFIER = 0.5
SPY_VALUE_MODIFIER = 0.5
SCOUT_VALUE_MODIFIER = 2.43
SCOUT_MODIFIER_THRESHOLD = 1.0
MINER_VALUE_MODIFIER = 3.0
MARSHAL_VALUE_MODIFIER = 0.8
NO_MODIFIER = 1.0

BASE_VALUE = 1.0
BASE_REVEAL_PENALTY = 0.71
REVEAL_PENALTY_INCREMENT = 0.02
REVEAL_PENALTY_INTERCEPT_VALUE = 0.01
REVEAL_PENALTY_DYNAMIC_MAX_VALUE = 0.28
REVEAL_PENALTY_MODIFICATION_REQUIRED_MAXIMUM_PIECES = 14

REVEALED = True
UNREVEALED = False
CHUNK = 'chunk'


def location_exists(location: list) -> bool:  # FIXME test
    if location[board.Y_POS] >= board.ROWS or location[board.Y_POS] < board.FIRST_TILE:
        return False
    elif location[board.X_POS] >= board.ROWS or location[board.X_POS] < board.FIRST_TILE:
        return False
    return True


def get_total_value_of_pieces_in_chunk(chunk_locations: list, grid_own_piece_values: np.ndarray) -> float:
    """
    sums the value of a player's pieces in a chunk
    :param chunk_locations: list of [y,x] tiles in the current chunk
    :param grid_own_piece_values: grid board representation containing the values of own pieces on tiles
    :return:
    """
    sum_chunk_own_piece_values = EMPTY # FIXME test deze
    for location in chunk_locations:
        if location_exists(location):
            sum_chunk_own_piece_values += grid_own_piece_values[location[board.Y_POS], location[board.X_POS]]
    return sum_chunk_own_piece_values


def get_adjacent_tile_locations(target_location: list) -> list: # FIXME test
    """
    get locations left, right, up, down from current tile. Does not take viability into account.
    :param target_location: [y,x]
    :return: adjacent locations
    """
    move_targets = list()
    move_targets.append([target_location[board.Y_POS], target_location[board.X_POS] + board.LEFT])
    move_targets.append([target_location[board.Y_POS], target_location[board.X_POS] + board.RIGHT])
    move_targets.append([target_location[board.Y_POS] + board.UP, target_location[board.X_POS]])
    move_targets.append([target_location[board.Y_POS] + board.DOWN, target_location[board.X_POS]])
    return move_targets


def tile_occupied_by_hostile(location: list, grid_opponent_piece_values: np.ndarray):  # FIXME test
    if grid_opponent_piece_values[location[board.Y_POS], location[board.X_POS]] > ranks.EMPTY_VALUE:
        return True
    return False


def tiles_contain_hostiles(locations: list, grid_opponent_piece_values: np.ndarray) -> bool:  # FIXME test
    """
    returns True if any of the supplied tile locations contain a hostile piece
    :param locations: list of [y,x] locations
    :param grid_opponent_piece_values: grid board representation containing the values of opposing pieces on tiles
    :return: True or False
    """
    for location in locations:
        if location_exists(location):
            if tile_occupied_by_hostile(location, grid_opponent_piece_values):
                return True
    return False


def sum_value_own_pieces_with_adjacent_hostiles(grid_own_piece_values: np.ndarray,  # FIXME test
                                      grid_opponent_piece_values: np.ndarray) -> int:
    """
    get the sum of values of own pieces with adjacent hostile pieces
    :param grid_own_piece_values: grid board representation containing the values of own pieces on tiles
    :param grid_opponent_piece_values: grid board representation containing the values of opposing pieces on tiles
    :return piece_with_adjacent_hostiles_values: sum of own piece values with adjacent opponent pieces
    """
    piece_with_adjacent_hostiles_values = EMPTY
    for ind_row, row in enumerate(grid_own_piece_values):
        for ind_col, tile_value in enumerate(row):
            if tile_value > ranks.EMPTY_VALUE:
                adjacent_tiles = get_adjacent_tile_locations([ind_row, ind_col])
                if tiles_contain_hostiles(adjacent_tiles, grid_opponent_piece_values):
                    piece_with_adjacent_hostiles_values += tile_value
    return piece_with_adjacent_hostiles_values


def sum_pieces_with_adjacent_hostiles(grid_own_piece_values: np.ndarray,  # FIXME test
                                      grid_opponent_piece_values: np.ndarray) -> int:
    """
    :param grid_own_piece_values: grid board representation containing the values of own pieces on tiles
    :param grid_opponent_piece_values: grid board representation containing the values of opposing pieces on tiles
    :return: sum own pieces with adjacent hostiles
    """
    sum_own_pieces_with_adjacent_hostiles = EMPTY
    for ind_row, row in enumerate(grid_own_piece_values):
        for ind_col, tile_value in enumerate(row):
            if tile_value > ranks.EMPTY_VALUE:
                adjacent_tiles = get_adjacent_tile_locations([ind_row, ind_col])
                if tiles_contain_hostiles(adjacent_tiles, grid_opponent_piece_values):
                    sum_own_pieces_with_adjacent_hostiles += INCREMENT_ONE
    return sum_own_pieces_with_adjacent_hostiles


def count_valid_move_targets(raw_move_targets: list, all_pieces: np.ndarray) -> int: # FIXME : test
    """
    determine which locations in a list are valid movement targets
    :param raw_move_targets: list of locations to consider
    :param all_pieces: grid representation of all pieces on the game board
    :return: sum of valid targets in provided targets
    """
    sum_valid_moves = EMPTY
    for target in raw_move_targets:
        if location_exists(target):
            if all_pieces[target[board.Y_POS], target[board.X_POS]] == ranks.EMPTY_TILE:
                sum_valid_moves += INCREMENT_ONE
    return sum_valid_moves


def get_possible_moves_amount_by_comparing_own_pieces_to_all_pieces(grid_own_piece_values: np.ndarray,
                                                                    all_pieces: np.ndarray) -> int:  # FIXME test
    """
    get the total number of possible moves for a player (discounting flags and bombs as they cannot move)
    :param grid_own_piece_values: grid board representation containing only own piece values
    :param all_pieces: grid board representation containing all piece ranks
    :return: sum of possible moves
    """
    sum_possible_moves = EMPTY
    for ind_row, row in enumerate(grid_own_piece_values):
        for ind_col, tile_value in enumerate(row):
            if tile_value > ranks.EMPTY_VALUE and all_pieces[ind_row, ind_col] not in ranks.BOMBS:
                raw_move_targets = get_adjacent_tile_locations([ind_row, ind_col])
                sum_possible_moves += count_valid_move_targets(raw_move_targets, all_pieces)
    return sum_possible_moves


def get_locations_n_tiles_from_centre(n: int, radius_centre: list) -> dict:
    """
    get [y,x] representations of tiles in radius of n tiles from starting point
    :param n: number of tiles in radius (excluding centre)
    :param radius_centre: location [y,x] of the centre of the circle
    :return: dict containing chunkname: list of locations in chunk
    """
    top_left_y = radius_centre[board.Y_POS] + n  # FIXME: TEST DEZE
    top_left_x = radius_centre[board.X_POS] - n
    top_left_location = [top_left_y, top_left_x]
    diameter = n + n + ONE
    chunk = {CHUNK: [top_left_location, diameter, diameter]}
    return board.generate_chunk_coordinates(chunk)


def get_total_values_pieces_in_n_tile_radius_from_location_in_grid(n: int, radius_centre: list,
                                                                   grid_own_piece_values: np.ndarray) -> float:
    """
    :param n: tile radius (excluding the centre tile)
    :param grid_own_piece_values: the grid to find the values in
    :param radius_centre: the location of the centre of the circle
    :return: the sum of all values found in the tiles in the circle
    """
    tiles_in_radius = get_locations_n_tiles_from_centre(n, radius_centre)
    sum_values_pieces_in_radius = EMPTY # FIXME test deze
    for chunk in tiles_in_radius:
        for location in tiles_in_radius[chunk]:
            if location_exists(location):
                sum_values_pieces_in_radius += grid_own_piece_values[location[board.Y_POS], location[board.X_POS]]
    return sum_values_pieces_in_radius


def get_other_player(current_player):
    if current_player == ranks.PLAYER_RED:
        return ranks.PLAYER_BLUE
    return ranks.PLAYER_RED


def determine_piece_color(piece_encoding: str) -> int:
    if piece_encoding not in ranks.NO_PIECES:
        if piece_encoding in ranks.RED_PIECES_LIST:
            return ranks.PLAYER_RED
        return ranks.PLAYER_BLUE
    print("empty tile")
    return None


def tile_is_safe(tile: list, player: int, all_pieces: np.ndarray) -> bool:
    """
    check if a tile is occupied by a friendly piece, is out of bounds or is water
    :param tile: location to check
    :param player: the friendly player color
    :param all_pieces: grid with all pieces
    :return: True or False
    """
    if location_exists(tile):
        tile_piece_color = determine_piece_color(all_pieces[tile[board.Y_POS], tile[board.X_POS]])
        if tile_piece_color == player or tile_piece_color == ranks.WATER:
            return True
        return False
    return True


def determine_flag_protected(flag_position: list, all_pieces: np.ndarray) -> bool:
    """
    determine if a player's flag is surrounded (horizontally and vertically) by friendly pieces or board edges
    :param flag_position: y, x coordinates
    :param all_pieces: grid containing all pieces
    :return: true or false
    """
    flag_y = flag_position[board.Y_POS]
    flag_x = flag_position[board.X_POS]
    player = determine_piece_color(all_pieces[flag_y, flag_x])
    left_safe = tile_is_safe([flag_y, flag_x - ONE], player, all_pieces)
    right_safe = tile_is_safe([flag_y, flag_x + ONE], player, all_pieces)
    top_safe = tile_is_safe([flag_y + ONE, flag_x], player, all_pieces)
    bottom_safe = tile_is_safe([flag_y - ONE, flag_x - ONE], player, all_pieces)
    if left_safe and right_safe and top_safe and bottom_safe:
        return True
    return False


def get_non_zero_values(grid_own_piece_values: np.ndarray) -> list:
    values = list()
    for row in grid_own_piece_values:
        for value in row:
            if value > EMPTY:
                values.append(value)
    return values


def x_relative_to_y(x, y) -> float:
    try:
        return x / y
    except ZeroDivisionError:
        print(''.join(("X: ", str(x), " Y: ", str(y), " ZERODIVISIONERROR")))


def get_relative_value_of_unrevealed_pieces(grid_own_piece_values: np.ndarray, unrevealed_pieces: np.ndarray) -> float:
    """
    get the relative value of the player's unrevealed piece values compared to her total piece values
    :param grid_own_piece_values: array with the player's piece values
    :param unrevealed_pieces: array with all unrevealed pieces ranks; revealed pieces are represented with 'A'
    (EMPTY_TILE) status
    :return: the unrevealed/total value percentage
    """
    sum_all_piece_values = EMPTY
    sum_unrevealed_piece_values = EMPTY
    for ind_row, row in enumerate(grid_own_piece_values):
        for ind_col, piece_value in enumerate(row):
            sum_all_piece_values += piece_value
            if unrevealed_pieces[ind_row, ind_col] != ranks.EMPTY_TILE:
                sum_unrevealed_piece_values += piece_value
    return x_relative_to_y(sum_unrevealed_piece_values, sum_all_piece_values)


def get_value_of_highest_value_revealed_or_unrevealed_piece(grid_own_piece_values: np.ndarray,
                                                            unrevealed_pieces: np.ndarray,
                                                            use_revealed_pieces: bool) -> float:
    """
    get the value of the highest value revealed or unrevealed piece for the player
    :param grid_own_piece_values: array with the player's piece values
    :param unrevealed_pieces: array with all unrevealed pieces ranks; revealed pieces are represented with 'A'
    (EMPTY_TILE) status
    :param use_both_revealed_and_unrevealed_pieces:
    :return: the player's highest value unrevealed piece's value
    """
    highest_value = EMPTY
    for ind_row, row in enumerate(grid_own_piece_values):
        for ind_col, piece_value in enumerate(row):
            if piece_value > highest_value:
                if not use_revealed_pieces:
                    if unrevealed_pieces[ind_row, ind_col] != ranks.EMPTY_TILE:
                        highest_value = piece_value
                else:
                    if unrevealed_pieces[ind_row, ind_col] == ranks.EMPTY_TILE:
                        highest_value = piece_value
    return highest_value


def determine_unrevealed_bombs_amount(player_bomb_locations: list, unrevealed_pieces: np.ndarray) -> int:
    """
    count the number of unrevealed bombs a player has
    :param player_bomb_locations: [y,x] locations of a player's bombs
    :param unrevealed_pieces: all unrevealed pieces a player has
    :return: the amount of unrevealed bombs
    """
    unrevealed_bombas = EMPTY
    for bomb in player_bomb_locations:
        if unrevealed_pieces[bomb[board.Y_POS], bomb[board.X_POS]] != ranks.EMPTY_TILE:  # FIXME mooi moment voor een print: wat vindt ie hier dan?
            unrevealed_bombas += INCREMENT_ONE
    return unrevealed_bombas


def calculate_reveal_base_penalty_modifier(player_movable_pieces_sum: int) -> float:
    """
    1 + 28 - (pieces_left * 2) -> percentage cost of being revealed when player moving pieces <= 14
    """
    modifier = utils.EMPTY
    if player_movable_pieces_sum <= REVEAL_PENALTY_MODIFICATION_REQUIRED_MAXIMUM_PIECES:
        modifier = REVEAL_PENALTY_INTERCEPT_VALUE + REVEAL_PENALTY_DYNAMIC_MAX_VALUE \
                   - (player_movable_pieces_sum * REVEAL_PENALTY_INCREMENT)
    return modifier


def get_player_turn_number(cumulative_turns: int) -> int:
    """"
    :return player_turn_number: returns 1 for the first turn for either player, 2 for the second turn etcetera
    """
    player_turn_number = int((cumulative_turns + utils.START_AT_ONE_MODIFIER) / board.PLAYERS)
    return player_turn_number


# FIXME coverage below this line

def handle_bomb_values(own_bombs: list, opposing_pieces: np.ndarray, grid_own_piece_values: np.ndarray) -> None:  # covered
    """
    set 0.5 * the opponent's highest value piece as bomb value
    :param own_bombs: locations (y,x) of own bombs
    :param opposing_pieces: dict containing number of opponent pieces per rank
    :param grid_own_piece_values: 2d array with the representation in values of own pieces
    """
    if not own_bombs:
        return
    most_valuable_opposing_piece = determine_n_highest_values_in_grid(ONE, opposing_pieces)
    bomb_value = most_valuable_opposing_piece[FIRST] * BOMB_VALUE_MODIFIER
    for bomb in own_bombs:
        grid_own_piece_values[bomb[board.Y_POS], bomb[board.X_POS]] = bomb_value


def handle_scout_values(exceptional_valued_movable_pieces: dict, scout: str, opposing_unrevealed_pieces: dict,
                        grid_own_piece_values: np.ndarray) -> None:  # covered
    """
    multiply the value of scouts by 2.43 if the opponent has more than 1 unrevealed piece left
    :param exceptional_valued_movable_pieces: dict with locations of pieces with special value assignment rules
    :param scout: string representation of the scout rank
    :param opposing_unrevealed_pieces: dict containing number of opponent unrevealed pieces per rank
    :param grid_own_piece_values: 2d array with the representation in values of own pieces
    """
    if scout in exceptional_valued_movable_pieces:
        if sum(opposing_unrevealed_pieces.values()) > SCOUT_MODIFIER_THRESHOLD:
            for scout_location in exceptional_valued_movable_pieces[scout]:
                grid_own_piece_values[scout_location[board.Y_POS], scout_location[board.X_POS]] *= SCOUT_VALUE_MODIFIER


def handle_spy_values(exceptional_valued_movable_pieces: dict, spy: str, opposing_marshal: str,  # covered
                      grid_own_piece_values: np.ndarray, opponent_piece_values: np.ndarray) -> None:
    """
    spies have a value equal to 50% of the opponent's marshal's total value, if it still lives
    :param exceptional_valued_movable_pieces: dict with locations of pieces with special value assignment rules
    :param spy: str representation of current player's spy rank
    :param opposing_marshal: str representation of opposing marshal rank
    :param grid_own_piece_values: 2d array with the representation in values of own pieces
    :param opponent_piece_values: 2d array with the representation in values of opponent pieces
    :return:
    """
    if spy in exceptional_valued_movable_pieces:
        if opposing_marshal in exceptional_valued_movable_pieces:
            spy_location_list = exceptional_valued_movable_pieces[spy]
            spy_location = spy_location_list[FIRST]
            opposing_marshal_locations = exceptional_valued_movable_pieces[opposing_marshal]
            marshal_location = opposing_marshal_locations[FIRST]
            opposing_marshal_value = opponent_piece_values[marshal_location[board.Y_POS],
                                                           marshal_location[board.X_POS]]
            spy_value = opposing_marshal_value * SPY_VALUE_MODIFIER
            grid_own_piece_values[spy_location[board.Y_POS], spy_location[board.X_POS]] = spy_value


def get_exceptional_piece_type_value_modifier(piece_type: str, opposing_pieces: dict) -> float:  # covered
    if piece_type == ranks.R_10:
        if opposing_pieces[ranks.B_1] > EMPTY:
            return MARSHAL_VALUE_MODIFIER
    elif piece_type == ranks.B_10:
        if opposing_pieces[ranks.R_1] > EMPTY:
            return MARSHAL_VALUE_MODIFIER
    elif piece_type == ranks.R_3:
        if opposing_pieces[ranks.B_B] > EMPTY:
            return MINER_VALUE_MODIFIER
    elif piece_type == ranks.B_3:
        if opposing_pieces[ranks.R_B] > EMPTY:
            return MINER_VALUE_MODIFIER
    return NO_MODIFIER


def determine_n_highest_values_in_grid(n: int, values_grid: np.ndarray) -> list:  # covered
    n_highest_values = [EMPTY] * n
    for row in values_grid:
        row_n_highest_value_indices = np.argpartition(row, -n)[-n:]
        for index in row_n_highest_value_indices:
            if row[index] > n_highest_values[LAST_ITEM]:
                n_highest_values[LAST_ITEM] = row[index]
                n_highest_values.sort(reverse=True)
    return n_highest_values


def is_revealed(position: list, unrevealed_pieces: np.ndarray) -> bool:
    if unrevealed_pieces[position[board.Y_POS], position[board.X_POS]] == ranks.EMPTY_TILE:
        return True
    return False


def determine_player_amount_of_moving_pieces(player: int, player_pieces: dict) -> int:  # covered
    static_pieces = [ranks.R_B, ranks.R_F] if player == ranks.PLAYER_RED else [ranks.B_B, ranks.B_F]
    sum_moving_pieces = EMPTY
    for key in player_pieces:
        if key not in static_pieces:
            sum_moving_pieces += player_pieces[key]
    return sum_moving_pieces


def assign_piece_to_red_or_blue_player_dict(piece_encoding: str, red_player_pieces: dict, blue_player_pieces: dict) \
        -> None:
    if determine_piece_color(piece_encoding) == ranks.PLAYER_RED:
        red_player_pieces[piece_encoding] += ONE
    else:
        blue_player_pieces[piece_encoding] += ONE


def initialize_player_pieces_dict(piece_ranks: list) -> dict:
    player_pieces = dict()
    for possible_rank in piece_ranks:
        player_pieces[possible_rank] = ranks.EMPTY_VALUE
    return player_pieces


def get_amount_of_pieces_per_rank(board_state: list) -> [dict, dict]:  # covered
    red_player_pieces = initialize_player_pieces_dict(ranks.RED_PIECES_LIST)
    blue_player_pieces = initialize_player_pieces_dict(ranks.BLUE_PIECES_LIST)
    for row in board_state:
        for column_value in row:
            if column_value not in [ranks.EMPTY_TILE, ranks.WATER]:
                assign_piece_to_red_or_blue_player_dict(column_value, red_player_pieces, blue_player_pieces)
    return red_player_pieces, blue_player_pieces


def get_player_movable_pieces_codes(piece_code: str) -> list:
    if determine_piece_color(piece_code) == ranks.PLAYER_RED:
        return ranks.RED_MOVABLE_PIECES
    return ranks.BLUE_MOVABLE_PIECES


def determine_rank_values(own_pieces_per_rank: dict, opposing_pieces_per_rank: dict) -> list:  # covered
    """
    uses De Boer's algorithm (2007) to increase the value of a piece's rank only if it can capture opposing pieces that
    a friendly piece of one rank lower could not capture. *www.kbs.twi.tudelft.nl/docs/MSc/2007/deBoer/thesis.pdf
    :param own_pieces_per_rank: the amount of pieces of each movable rank the current player has
    :param opposing_pieces_per_rank: the amount of pieces of each movable rank the current player's opponent has
    :return: a recalculated, relative value for each rank
    """
    determined_rank_values = list()
    ranks_in_opponent_dict = list(opposing_pieces_per_rank)
    ranks_in_current_player_dict = list(own_pieces_per_rank)

    sorted_opponent_movable_rank_codes = get_player_movable_pieces_codes(ranks_in_opponent_dict[FIRST])
    sorted_current_player_movable_rank_codes = get_player_movable_pieces_codes(ranks_in_current_player_dict[FIRST])
    current_rank_value = ranks.BASE_VALUE
    for index, rank_code in enumerate(sorted_opponent_movable_rank_codes):
        if index != FIRST:
            current_player_rank_code = sorted_current_player_movable_rank_codes[index]
            if own_pieces_per_rank[current_player_rank_code] > EMPTY: # if player has pieces of current rank
                one_rank_lower = index - 1
                opponent_one_rank_lower_code = sorted_opponent_movable_rank_codes[one_rank_lower]
                opponent_current_rank_code = sorted_opponent_movable_rank_codes[index]
                weaker_or_equal_opposing_pieces = opposing_pieces_per_rank[opponent_one_rank_lower_code] \
                                                  + opposing_pieces_per_rank[opponent_current_rank_code]
                if weaker_or_equal_opposing_pieces > EMPTY: # if opponent has pieces of equal or one lower rank
                    current_rank_value = ranks.BASE_VALUE * math.pow(RANK_DIFFERENCE_FACTOR, index)
        determined_rank_values.append(current_rank_value)
    return determined_rank_values
