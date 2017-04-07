import string
import sys
import math
import numpy as np
sys.path.append("../")
import rank_encodings as ranks
import game_board_descriptors as board
import utils


ONE = 1
FIRST = 0
EMPTY = 0
RED_HIGHEST_RANK_CODE = 12
RANK_DIFFERENCE_FACTOR = 1.45
LAST_ITEM = -1

BOMB_VALUE_MODIFIER = 0.5
SPY_VALUE_MODIFIER = 0.5
SCOUT_VALUE_MODIFIER = 2.43
SCOUT_MODIFIER_THRESHOLD = 1.0
MINER_VALUE_MODIFIER = 3.0
MARSHAL_VALUE_MODIFIER = 0.8
NO_MODIFIER = 1.0


def interpret_move(source: str, target: str): #FIXME; handle move result interpretation here! duplicate from log_file_processing but modified to return what happens to the involved pieces and if it was towards the opponent
    pass


def handle_bomb_values(own_bombs: list, opposing_pieces: np.ndarray, own_piece_values: np.ndarray) -> None:
    """
    set 0.5 * the opponent's highest value piece as bomb value
    :param own_bombs: locations (y,x) of own bombs
    :param opposing_pieces: dict containing number of opponent pieces per rank
    :param own_piece_values: 2d array with the representation in values of own pieces
    """
    if not own_bombs:
        return
    most_valuable_opposing_piece = determine_n_highest_values_in_grid(ONE, opposing_pieces)
    bomb_value = most_valuable_opposing_piece[FIRST] * BOMB_VALUE_MODIFIER
    for bomb in own_bombs:
        own_piece_values[bomb[board.Y_POS], bomb[board.X_POS]] = bomb_value


def handle_scout_values(exceptional_valued_movable_pieces: dict, scout: str, opposing_unrevealed_pieces: dict,
                        own_piece_values: np.ndarray) -> None:  # covered
    """
    multiply the value of scouts by 2.43 if the opponent has more than 1 unrevealed piece left
    :param exceptional_valued_movable_pieces: dict with locations of pieces with special value assignment rules
    :param scout: string representation of the scout rank
    :param opposing_unrevealed_pieces: dict containing number of opponent unrevealed pieces per rank
    :param own_piece_values: 2d array with the representation in values of own pieces
    """
    if scout in exceptional_valued_movable_pieces:
        if sum(opposing_unrevealed_pieces.values()) > SCOUT_MODIFIER_THRESHOLD:
            for scout_location in exceptional_valued_movable_pieces[scout]:
                own_piece_values[scout_location[board.Y_POS], scout_location[board.X_POS]] *= SCOUT_VALUE_MODIFIER


def handle_spy_values(exceptional_valued_movable_pieces: dict, spy: str, opposing_marshal: str,  # covered
                      own_piece_values: np.ndarray, opponent_piece_values: np.ndarray) -> None:
    """
    spies have a value equal to 50% of the opponent's marshal's total value, if it still lives
    :param exceptional_valued_movable_pieces: dict with locations of pieces with special value assignment rules
    :param spy: str representation of current player's spy rank
    :param opposing_marshal: str representation of opposing marshal rank
    :param own_piece_values: 2d array with the representation in values of own pieces
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
            own_piece_values[spy_location[board.Y_POS], spy_location[board.X_POS]] = spy_value


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


def determine_piece_color(piece_encoding: str) -> int:
    if piece_encoding in ranks.RED_PIECES_LIST:
        return ranks.PLAYER_RED
    return ranks.PLAYER_BLUE


def is_revealed(position: list, unrevealed_pieces: np.ndarray) -> bool:
    if unrevealed_pieces[position[board.Y_POS], position[board.X_POS]] == ranks.EMPTY:
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
            if column_value not in [ranks.EMPTY, ranks.WATER]:
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
