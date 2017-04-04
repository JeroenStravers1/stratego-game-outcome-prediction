import numpy as np
import sys
sys.path.append("../")
import feature_extraction
sys.path.append("../")
import game_board_descriptors as board


class GameStateTracker:
    """
    is called each turn
    """

    _NEW_TURN = 1

    def __init__(self):
        self.current_turn = 0 # including current turn
        self._moves_toward_opponent_red = 0
        self._moves_toward_opponent_blue = 0
        self._number_of_opponent_pieces_captured_red = 0
        self._number_of_opponent_pieces_captured_blue = 0
        self._value_of_opponent_pieces_captured_red = 0
        self._value_of_opponent_pieces_captured_blue = 0
        self.board_state = None
        self.unmoved_pieces = None
        self.unrevealed_pieces = None
        self.piece_values = None
        self.board_chunks = board.generate_chunk_coordinates()

        #FIXME keep list of removed pieces?
        # keep list of values? should only be determined afterwards or something?

    def update_game_state(self, initial_deployment: list, unmoved_pieces: list, unrevealed_pieces: list):
        #FIXME hier vergelijk je previous board state om verloren stukken te berekenen?.
        self.board_state = initial_deployment
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces
        self.piece_values = np.empty([board.ROWS, board.COLS])
        self.current_turn += self._NEW_TURN
        self.calculate_features(initial_deployment, unmoved_pieces, unrevealed_pieces)
        return self._generate_feature_dict()

    def calculate_features(self, initial_deployment: list, unmoved_pieces: list, unrevealed_pieces: list):
        pass

    def _generate_feature_dict(self):
        pass


if __name__ == "__main__":
    #tester = GameStateTracker()
    import string
    print(string.ascii_lowercase.index("m"))
