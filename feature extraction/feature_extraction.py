import sys
sys.path.append("../")
import rank_encodings as ranks
import value_calculation


REVEALED = True
UNREVEALED = False
ONE = 1


class FeatureExtractor:

    def __init__(self, board_state, unmoved_pieces, unrevealed_pieces):
        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces

    def calculate_piece_values(self):
        red_pieces, blue_pieces = value_calculation.get_amount_of_pieces_per_rank(self.board_state)
        red_rank_values = value_calculation.determine_rank_values(blue_pieces)
        blue_rank_values = value_calculation.determine_rank_values(red_pieces)


def calculate_piece_values(board_state: list, unrevealed_pieces: list) -> list:
    """
    :param grid:
    :param revealed_grid:
    :return: grid with values on positions
    """
    red_pieces, blue_pieces = get_amount_of_pieces_per_rank(board_state)
    # recalculate rank base values for red and blue
    # assign base values
    # correct for revealed pieces -29%
    # triple miner value if opponent has bombs
    # set bomb value to 50% highest piece value
    # if marshal alive: set spy to 50% of its value
    # if spy alive: set marshal to 79% of value


def extract_features(board_state: list, unmoved_pieces: list, unrevealed_pieces: list) -> dict:
    piece_values = calculate_piece_values(board_state, unrevealed_pieces)

