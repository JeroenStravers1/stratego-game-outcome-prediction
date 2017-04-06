import string
import sys
import math
sys.path.append("../")
import rank_encodings as ranks
import game_board_descriptors as board
import utils


ONE = 1
FIRST = 0
EMPTY = 0
RED_HIGHEST_RANK_CODE = 12
RANK_DIFFERENCE_FACTOR = 1.45


def interpret_move_result(move): #FIXME; handle move result interpretation here! duplicate from log_file_processing but modified to return what happens to the involved pieces
    pass


def determine_piece_color(piece_encoding: str) -> int:
    if piece_encoding in ranks.RED_PIECES_LIST:
        return ranks.PLAYER_RED
    return ranks.PLAYER_BLUE


def is_revealed(position, unrevealed_pieces):
    if unrevealed_pieces[position[board.Y_POS], position[board.X_POS]] == ranks.EMPTY:
        return False
    return True


def determine_player_amount_of_moving_pieces(player, player_pieces):
    static_pieces = [ranks.R_B, ranks.R_F] if player == ranks.PLAYER_RED else [ranks.B_B, ranks.B_F]
    sum_moving_pieces = EMPTY
    for key in player_pieces:
        if key not in static_pieces:
            sum_moving_pieces += player_pieces[key]
    return sum_moving_pieces


def assign_piece_to_red_or_blue_player_dict(piece_encoding: str, red_player_pieces: dict, blue_player_pieces: dict):
    if determine_piece_color(piece_encoding) == ranks.PLAYER_RED:
        red_player_pieces[piece_encoding] += ONE
    else:
        blue_player_pieces[piece_encoding] += ONE


def initialize_player_pieces_dict(piece_ranks: list) -> dict:
    player_pieces = dict()
    for possible_rank in piece_ranks:
        player_pieces[possible_rank] = ranks.EMPTY_VALUE
    return player_pieces


def get_amount_of_pieces_per_rank(board_state: list) -> [dict, dict]:
    red_player_pieces = initialize_player_pieces_dict(ranks.RED_PIECES_LIST)
    blue_player_pieces = initialize_player_pieces_dict(ranks.BLUE_PIECES_LIST)
    for row in board_state:
        for column_value in row:
            if column_value not in [ranks.EMPTY, ranks.WATER]:
                assign_piece_to_red_or_blue_player_dict(column_value, red_player_pieces, blue_player_pieces)
    return red_player_pieces, blue_player_pieces


def get_player_movable_pieces_codes(piece_code):
    if determine_piece_color(piece_code) == ranks.PLAYER_RED:
        return ranks.RED_MOVABLE_PIECES
    return ranks.BLUE_MOVABLE_PIECES


#je bent de waarden van stukken aan eht berekenen obv welke ranks de tegenstander heeft
def determine_rank_values(own_pieces_per_rank: dict, opposing_pieces_per_rank: dict) -> list:
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


if __name__ == "__main__":
    a = {"B": 0, "C": 1, "D": 1, "E": 0, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11}
    b = {"N": 0, "O": 1, "P": 1, "Q": 3, "R": 0, "S": 0, "T": 6, "U": 7, "V": 8, "W": 9, "X": 10, "Y": 11}
    print(determine_rank_values(a, b))
