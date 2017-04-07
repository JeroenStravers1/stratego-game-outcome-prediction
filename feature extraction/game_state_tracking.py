import numpy as np
import sys
import feature_extraction
import datapoint_feature_containment as dfc
sys.path.append("../")
import game_board_descriptors as board
import rank_encodings as ranks
import utils


class GameStateTracker:
    """
    is called each turn
    """

    _ZERO = 0
    _NEW_TURN = 1
    _FIRST_TURN = 0

    def __init__(self):
        self._moves_toward_opponent_red = self._ZERO
        self._moves_toward_opponent_blue = self._ZERO
        self._number_of_opponent_pieces_captured_red = self._ZERO
        self._number_of_opponent_pieces_captured_blue = self._ZERO
        self._value_of_opponent_pieces_captured_red = self._ZERO
        self._value_of_opponent_pieces_captured_blue = self._ZERO
        self.current_turn_number = self._ZERO
        self.board_state = None
        self.unmoved_pieces = None
        self.unrevealed_pieces = None
        self.piece_values = np.zeros([board.ROWS, board.COLS])
        self.board_chunks = board.generate_chunk_coordinates()
        self.red_bombs = list()
        self.blue_bombs = list()
        self.red_flag = list()
        self.blue_flag = list()

        #FIXME keep list of removed pieces?
        # keep list of values? should only be determined afterwards or something?

    def update_game_state(self, board_state: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray): #FIXME needs MOVE as arg to interpret turn result
        self._get_static_piece_positions(board_state)
        extracted_feature_container = dfc.DataPointFeatureContainer()
        self.current_turn_number += self._NEW_TURN
        feature_extractor = feature_extraction.FeatureExtractor(board_state, unmoved_pieces, unrevealed_pieces)
        #FIXME hier vergelijk je previous board state om verloren stukken te berekenen?
        # self.board_state = board_state
        # self.unmoved_pieces = unmoved_pieces
        # self.unrevealed_pieces = unrevealed_pieces
        # FIXME hier moet een check zitten. Je kijkt eerst wat er gebeurd is door features te calcen, dan ga je dat met de vorige situatie vergelijken om de beurt te interpreteren. Dan pas sla je de nieuwe board versies op over de oudes.

        # FIXME: PROCESS MOVE RESULT HERE, THEN:
        feature_extractor.extract_features(extracted_feature_container)
        return extracted_feature_container

    def calculate_features(self, initial_deployment: np.ndarray, unmoved_pieces: np.ndarray,
                           unrevealed_pieces: np.ndarray, piece_values: np.ndarray,
                           extracted_feature_container: dfc.DataPointFeatureContainer):
        pass

    def _generate_feature_dict(self):
        pass

    def _get_static_piece_positions(self, board_state: np.ndarray):
        self.red_bombs = list()
        self.blue_bombs = list()
        for row_ind, row in enumerate(board_state):
            for col_ind, piece in enumerate(row):
                position = [row_ind, col_ind]
                self._store_static_piece_positions(piece, position)

    def _store_static_piece_positions(self, piece: str, position: list):
        if piece == ranks.R_B:
            self.red_bombs.append(position)
        elif piece == ranks.B_B:
            self.blue_bombs.append(position)
        if self.current_turn_number == self._FIRST_TURN:
            if piece == ranks.R_F:
                self.red_flag.append(position)
            elif piece == ranks.B_F:
                self.blue_flag.append(position)
