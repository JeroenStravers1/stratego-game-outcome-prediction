import numpy as np
import sys
sys.path.append("../")
import rank_encodings as ranks
import game_board_descriptors as board
import value_calculation as val_calc
import utils


class FeatureExtractor:
    """
    extracts all features that do not need information regarding previous turns to calculate. Mainly a value container.
    """

    REVEALED = True
    UNREVEALED = False
    ONE = 1
    _BASE_VALUE = 1
    _BASE_REVEAL_PENALTY = 0.71
    _REVEAL_PENALTY_INCREMENT = 0.02
    _REVEAL_PENALTY_INTERCEPT_VALUE = 0.01
    _REVEAL_PENALTY_DYNAMIC_MAX_VALUE = 0.28
    _REVEAL_PENALTY_MODIFICATION_REQUIRED_MAXIMUM_PIECES = 14

    def __init__(self, board_state, unmoved_pieces, unrevealed_pieces):
        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces

        self.piece_values_red = np.zeros([board.ROWS, board.COLS])
        self.piece_values_blue = np.zeros([board.ROWS, board.COLS])

        self.red_discovery_cost = self._BASE_REVEAL_PENALTY
        self.red_base_value = self._BASE_VALUE

        self.blue_discovery_cost = self._BASE_REVEAL_PENALTY
        self.blue_base_value = self._BASE_VALUE

        self.red_pieces_amount = utils.EMPTY
        self.red_pieces_movable_amount = utils.EMPTY
        self.blue_pieces_amount = utils.EMPTY
        self.blue_pieces_movable_amount = utils.EMPTY

    def extract_features(self):
        red_pieces, blue_pieces = val_calc.get_amount_of_pieces_per_rank(self.board_state)
        red_unmoved_pieces, blue_unmoved_pieces = val_calc.get_amount_of_pieces_per_rank(self.unmoved_pieces)
        red_unrevealed_pieces, blue_unrevealed_pieces = val_calc.get_amount_of_pieces_per_rank(self.unrevealed_pieces)

        self.red_pieces_amount = sum(red_pieces.values())
        self.blue_pieces_amount = sum(blue_pieces.values())

        self.red_pieces_movable_amount = val_calc.determine_player_amount_of_moving_pieces(ranks.PLAYER_RED, red_pieces)
        self.blue_pieces_movable_amount = val_calc.determine_player_amount_of_moving_pieces(ranks.PLAYER_BLUE, blue_pieces)
        self._assign_piece_values(red_pieces, blue_pieces)

    def _assign_piece_values(self, red_pieces: dict, blue_pieces: dict):
        self._determine_reveal_and_base_penalties()
        red_rank_values = val_calc.determine_rank_values(blue_pieces)
        blue_rank_values = val_calc.determine_rank_values(red_pieces)
        for ind_row, row in enumerate(self.board_state):
            for ind_col, column in enumerate(row):
                current_piece_type = self.board_state[row, column]
                current_piece_value_index = ranks.ALL_PIECES[current_piece_type] - utils.START_AT_ZERO_MODIFIER
                current_piece_revealed = val_calc.is_revealed([ind_row, ind_col], self.unrevealed_pieces)
                player = val_calc.determine_piece_color(current_piece_type)
                piece_value_modifier = self._determine_applicable_base_value_modifier(current_piece_revealed, player)
                if player == ranks.PLAYER_RED:
                    piece_value = red_rank_values[current_piece_value_index] * piece_value_modifier #FIXME: hier stop je je marshal/spy/miner/scout/bomb spul
                    self.piece_values_red[ind_row, ind_col] = piece_value
                else:
                    piece_value = blue_rank_values[current_piece_value_index] * piece_value_modifier
                    self.piece_values_red[ind_row, ind_col] = piece_value


    def _determine_applicable_base_value_modifier(self, current_piece_revealed, player):
        if current_piece_revealed:
            return self.red_discovery_cost if player == ranks.PLAYER_RED else self.blue_discovery_cost
        else:
            return self.red_base_value if player == ranks.PLAYER_RED else self.blue_base_value



    def _determine_reveal_and_base_penalties(self):
        """
        account for the fact that the identity of pieces becomes clearer as fewer remain
        """
        red_modifier = self._calculate_reveal_base_penalty_modifier(self.red_pieces_movable_amount)
        blue_modifier = self._calculate_reveal_base_penalty_modifier(self.blue_pieces_movable_amount)
        self.red_base_value = self._BASE_REVEAL_PENALTY + red_modifier
        self.red_discovery_cost = self._BASE_VALUE - red_modifier
        self.blue_base_value = self._BASE_REVEAL_PENALTY + blue_modifier
        self.blue_discovery_cost = self._BASE_VALUE + blue_modifier

    def _calculate_reveal_base_penalty_modifier(self, player_movable_pieces_sum):
        """
        1 + 28 - (pieces_left * 2) -> percentage cost of being revealed when player moving pieces <= 14
        """
        modifier = utils.EMPTY
        if player_movable_pieces_sum <= self._REVEAL_PENALTY_MODIFICATION_REQUIRED_MAXIMUM_PIECES:
            modifier = self._REVEAL_PENALTY_INTERCEPT_VALUE + self._REVEAL_PENALTY_DYNAMIC_MAX_VALUE \
                - (player_movable_pieces_sum * self._REVEAL_PENALTY_INCREMENT)
        return modifier



def calculate_piece_values(board_state: list, unrevealed_pieces: list) -> list:
    """
    :param grid:
    :param revealed_grid:
    :return: grid with values on positions
    """
    red_pieces, blue_pieces = None#get_amount_of_pieces_per_rank(board_state)

    ranks.ALL_PIECES # use to get index of rank of single piece, correct value with - START_AT_ZERO
    # x recalculate rank base values for red and blue
    # x assign base values
    #   x |-correct for revealed pieces -29%
    #   x |-correct for n_movable <= 14
    #   |-triple miner value if opponent has bombs
    #   |-triple scout value if opponent has unrevealed pieces
    #   |-set bomb value to 50% highest opposing piece value
    #   |-if marshal alive: set spy to 50% of its value
    #   |-if spy alive: set marshal to 79% of value



if __name__ == "__main__":
    bob = FeatureExtractor(np.zeros([board.ROWS, board.COLS]), np.zeros([board.ROWS, board.COLS]), np.zeros([board.ROWS, board.COLS]))
    henk = {"1":1, "2":2}
    print(sum(henk.values()))