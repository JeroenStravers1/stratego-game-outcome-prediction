import numpy as np
import sys
import feature_extraction
sys.path.append("../")
import game_board_descriptors as board
import utils


class GameStateTracker:
    """
    is called each turn
    """

    _ZERO = 0
    _NEW_TURN = 1

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

        #FIXME keep list of removed pieces?
        # keep list of values? should only be determined afterwards or something?

    def update_game_state(self, board_state: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray): #FIXME needs MOVE as arg to interpret turn result
        self.current_turn_number += self._NEW_TURN
        feature_extractor = feature_extraction.FeatureExtractor(board_state, unmoved_pieces, unrevealed_pieces)
        #FIXME hier vergelijk je previous board state om verloren stukken te berekenen?
        # self.board_state = board_state
        # self.unmoved_pieces = unmoved_pieces
        # self.unrevealed_pieces = unrevealed_pieces
        # FIXME hier moet een check zitten. Je kijkt eerst wat er gebeurd is door features te calcen, dan ga je dat met de vorige situatie vergelijken om de beurt te interpreteren. Dan pas sla je de nieuwe board versies op over de oudes.

        # FIXME: PROCESS MOVE RESULT HERE, THEN:
        self.calculate_features(board_state, unmoved_pieces, unrevealed_pieces, self.piece_values)
        return self._generate_feature_dict()

    def calculate_features(self, initial_deployment: np.ndarray, unmoved_pieces: np.ndarray,
                           unrevealed_pieces: np.ndarray, piece_values: np.ndarray):
        pass

    def _generate_feature_dict(self):
        pass


class DataPointFeatureContainer:
    """
    a container class used to deliver the output of all datapoint features in a single, easily accessible object
    """
    # INFORMATION
    REVEALED_BOMBS_RED = 0
    REVEALED_BOMBS_BLUE = 1
    PERCENTAGE_UNREVEALED_RED = 2
    PERCENTAGE_UNREVEALED_BLUE = 3
    PERCENTAGE_UNMOVED_RED = 4
    PERCENTAGE_UNMOVED_BLUE = 5
    MOST_VALUABLE_REVEALED_PIECE_RED = 6
    MOST_VALUABLE_REVEALED_PIECE_BLUE = 7
    MOST_VALUABLE_UNREVEALED_PIECE_RED = 8
    MOST_VALUABLE_UNREVEALED_PIECE_BLUE = 9
    PERCENTAGE_VALUE_REVEALED_PIECES_RED = 10
    PERCENTAGE_VALUE_REVEALED_PIECES_BLUE = 11

    # RELATIVE STRENGTH
    PERCENTAGE_SUM_RED_VALUE_STRONGEST_PIECE_VS_BLUE_VALUE_STRONGEST_PIECE = 12
    PERCENTAGE_SUM_RED_VALUE_SUM_BLUE_VALUE = 13
    STDEV_RED_VALUE_PIECES = 14
    STDEV_BLUE_VALUE_PIECES = 15
    MEAN_RED_VALUE_PIECES = 16
    MEAN_BLUE_VALUE_PIECES = 17
    SUM_PIECES_RED = 18
    SUM_PIECES_BLUE = 19
    STARTING_VALUE_PERCENTAGE_RED = 20
    STARTING_VALUE_PERCENTAGE_BLUE = 21
    STARTING_NUMBER_PERCENTAGE_RED = 22
    STARTING_NUMBER_PERCENTAGE_BLUE = 23
    SUM_THREE_MOST_VALUABLE_RED = 24
    SUM_THREE_MOST_VALUABLE_BLUE = 25
    RED_THREE_MOST_VALUABLE_PERCENTAGE_BLUE_THREE_MOST_VALUABLE = 26
    MEAN_AMOUNT_CAPTURES_PER_TURN_RED = 27
    MEAN_AMOUNT_CAPTURES_PER_TURN_BLUE = 28
    MEAN_VALUE_CAPTURES_PER_TURN_RED = 29
    MEAN_VALUE_CAPTURES_PER_TURN_BLUE = 30
    CURRENT_TURN_NUMBER = 31

    # BOARD POSITION
    OWN_FLAG_SAFE_RED = 32
    OWN_FLAG_SAFE_BLUE = 33
    SUM_VALUE_FRIENDLIES_ONE_TILE_RADIUS_OWN_FLAG_RED = 34
    SUM_VALUE_FRIENDLIES_ONE_TILE_RADIUS_OWN_FLAG_BLUE = 35
    SUM_VALUE_FRIENDLIES_TWO_TILE_RADIUS_OWN_FLAG_RED = 36
    SUM_VALUE_FRIENDLIES_TWO_TILE_RADIUS_OWN_FLAG_BLUE = 37
    SUM_VALUE_HOSTILES_ONE_TILE_RADIUS_OWN_FLAG_RED = 38
    SUM_VALUE_HOSTILES_ONE_TILE_RADIUS_OWN_FLAG_BLUE = 39
    SUM_VALUE_HOSTILES_TWO_TILE_RADIUS_OWN_FLAG_RED = 40
    SUM_VALUE_HOSTILES_TWO_TILE_RADIUS_OWN_FLAG_BLUE = 41
    SUM_MOVES_TOWARD_OPPONENT_BOARD_EDGE_RED = 42
    SUM_MOVES_TOWARD_OPPONENT_BOARD_EDGE_BLUE = 43
    SUM_POSSIBLE_MOVES_RED = 44
    SUM_POSSIBLE_MOVES_BLUE = 45
    SUM_SAFE_MOVES_RED = 46
    SUM_SAFE_MOVES_BLUE = 47
    SUM_FRIENDLIES_WITH_HOSTILES_ADJACENT_TILE_RED = 48
    SUM_FRIENDLIES_WITH_HOSTILES_ADJACENT_TILE_BLUE = 49
    SUM_HOSTILES_ADJACENT_TO_FRIENDLIES_RED = 50
    SUM_HOSTILES_ADJACENT_TO_FRIENDLIES_BLUE = 51
    SUM_ADJACENT_CAPTURABLES_RED = 52
    SUM_ADJACENT_CAPTURABLES_BLUE = 53
    SUM_ADJACENT_REVEALED_CAPTURABLES_RED = 54
    SUM_ADJACENT_REVEALED_CAPTURABLES_BLUE = 55
    SUM_VALUE_FRIENDLIES_WITH_ADJACENT_HOSTILES_RED = 56
    SUM_VALUE_FRIENDLIES_WITH_ADJACENT_HOSTILES_BLUE = 57
    SUM_VALUE_HOSTILES_WITH_ADJACENT_FRIENDLIES_RED = 58
    SUM_VALUE_HOSTILES_WITH_ADJACENT_FRIENDLIES_BLUE = 59

    # BOARD CHUNKS
    R_A10 = 60
    B_A10 = 61
    R_A8 = 62
    B_A8 = 63
    R_A6 = 64
    B_A6 = 65
    R_A4 = 66
    B_A4 = 67
    R_A2 = 68
    B_A2 = 69
    R_D10 = 70
    B_D10 = 71
    R_D8 = 72
    B_D8 = 73
    R_E6 = 74
    B_E6 = 75
    R_D4 = 76
    B_D4 = 77
    R_D2 = 78
    B_D2 = 79
    R_H10 = 80
    B_H10 = 81
    R_H8 = 82
    B_H8 = 83
    R_I6 = 84
    B_I6 = 85
    R_H4 = 86
    B_H4 = 87
    R_H2 = 88
    B_H2 = 89

    def __init__(self):
        self.extracted_features = dict()
