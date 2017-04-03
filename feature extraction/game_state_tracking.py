import numpy as np
import sys
sys.path.append("../")
import feature_extraction


class GameStateTracker:
    """
    is called each turn
    """

    def __init__(self, initial_deployment, unmoved_pieces, unrevealed_pieces):
        self.turns = 0 # including current turn
        self._moves_toward_opponent_red = 0
        self._moves_toward_opponent_blue = 0
        self._number_of_opponent_pieces_captured_red = 0
        self._number_of_opponent_pieces_captured_blue = 0
        self._value_of_opponent_pieces_captured_red = 0
        self._value_of_opponent_pieces_captured_blue = 0

        #FIXME keep list of removed pieces?
        # keep list of values? should only be determined afterwards or something?

        self.board_state = initial_deployment
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces
        self.piece_values = np.empty([self._ROWS_AMOUNT, self._COLS_AMOUNT])


if __name__ == "__main__":
    tester = GameStateTracker()
