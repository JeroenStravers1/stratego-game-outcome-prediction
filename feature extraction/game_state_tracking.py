import numpy as np
import sys
import feature_extraction
import datapoint_feature_containment as dfc
import value_calculation as val_calc
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
    _PREVIOUS_TURN = 1

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
        self.red_start = None
        self.piece_values = np.zeros([board.ROWS, board.COLS])
        self.board_chunks = board.generate_chunk_coordinates(board.CHUNKS_TOP_LEFT_DIMENSIONS)
        self.red_bombs = list()
        self.blue_bombs = list()
        self.red_flag = list()
        self.blue_flag = list()

    def init_game_board(self, board_state: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray): #FIXME implementeer hier de initiele setup!
        # FIXME geef hier ook mee wie waar begint!!!!
        # FIXME eventueel hier een rotate functie? waarin je binnenkomende board data verticaal spiegelt indien de spelers andersom zitten en rood boven staat ipv beneden?
        self.red_start = self._START_BOTTOM
        pass

    def update_game_state(self, board_state: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray,
                          source: str, target: str) -> dfc.DataPointFeatureContainer:
        self.current_turn_number += self._NEW_TURN
        self._determine_captured_pieces_and_values(source, target)

        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces

        self._get_static_piece_positions(board_state)
        extracted_feature_container = dfc.DataPointFeatureContainer()
        feature_extractor = feature_extraction.FeatureExtractor(board_state, unmoved_pieces, unrevealed_pieces,
                                                                extracted_feature_container, self.red_bombs,
                                                                self.blue_bombs, self.red_flag, self.blue_flag)
        feature_extractor.extract_features()
        self._add_long_term_features_to_feature_container(extracted_feature_container)
        return extracted_feature_container


    def _determine_captured_pieces_and_values(self, source: str, target: str) -> None:
        """
        get the rank, color and value of the involved piece(s). Call a second function to process the result
        :param source: the 2d array location (y, x) of the source tile (moving from)
        :param target: the 2d array location (y, x) of the target tile (moving to)
        """
        source_piece = self.board_state[source[board.Y_POS], source[board.X_POS]]
        target_piece = self.board_state[source[board.Y_POS], source[board.X_POS]]
        source_value = self.piece_values[source[board.Y_POS], source[board.X_POS]]
        target_value = self.piece_values[target[board.Y_POS], target[board.X_POS]]
        result_source, result_target, result = ranks.determine_move_to_result(source, target)
        current_player = val_calc.determine_piece_color(source_piece)
        opponent = val_calc.determine_piece_color(target_piece)
        players_number_captured_pieces = [self._number_of_opponent_pieces_captured_red,
                                          self._number_of_opponent_pieces_captured_blue]
        players_value_captured_pieces = [self._value_of_opponent_pieces_captured_red,
                                         self._value_of_opponent_pieces_captured_blue]
        current_player_amount_captured = players_number_captured_pieces[current_player]
        opponent_amount_captured = players_number_captured_pieces[opponent]
        current_player_value_captured = players_value_captured_pieces[current_player]
        opponent_value_captured = players_value_captured_pieces[opponent]
        self._process_move_result(result, source_value, target_value, current_player_amount_captured,
                                  opponent_amount_captured, current_player_value_captured, opponent_value_captured)
        self._interpret_move_towards_opponent(source, target, player, opponent)

    def _process_move_result(self, result: int, source_value: float, target_value: float,
                             current_player_amount_captured: int, opponent_amount_captured: float,
                             current_player_value_captured: int, opponent_value_captured: float) -> None:
        """
        process the result of a move action regarding player total captures
        :param result: the result of the move (win, draw, lose, empty)
        :param source_value: the float value of the moving piece
        :param target_value: the float value of the targetted piece (0 if empty)
        :param current_player_amount_captured:
        :param opponent_amount_captured:
        :param current_player_value_captured:
        :param opponent_value_captured:
        """
        if result == ranks.MOVE_WIN:
            current_player_amount_captured += val_calc.INCREMENT_ONE
            current_player_value_captured += target_value
        elif result == ranks.MOVE_LOSE:
            opponent_amount_captured += val_calc.INCREMENT_ONE
            opponent_value_captured += source_value
        elif result == ranks.MOVE_DRAW:
            current_player_amount_captured += val_calc.INCREMENT_ONE
            current_player_value_captured += target_value
            opponent_amount_captured += val_calc.INCREMENT_ONE
            opponent_value_captured += source_value

    def _interpret_move_towards_opponent(self, source: str, target: str, player: int, opponent: int) -> None:
        """
        store the amount of times players move towards each other.
        :param source: the source tile
        :param target: the target tile
        :param player: the current player
        :param opponent: the opponent
        """
        players_moves_towards_opponents = [self._moves_toward_opponent_red, self._moves_toward_opponent_blue]
        move_direction = int(target[board.Y_POS]) - int(source[board.Y_POS])
        edges = [board.BOTTOM, board.TOP]
        if self.red_start == board.TOP:
            edges = [board.TOP, board.BOTTOM]
        opposing_edge = edges[opponent]
        if move_direction == opposing_edge:
            players_moves_towards_opponents[player] += val_calc.INCREMENT_ONE

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

    def _add_long_term_features_to_feature_container(self, feats: dfc.DataPointFeatureContainer):
        player_turn_number = val_calc.get_player_turn_number(self.current_turn_number)

        feats.extracted_features[feats.CURRENT_TURN_NUMBER] = self.current_turn_number

        feats.extracted_features[feats.MEAN_AMOUNT_CAPTURES_PER_TURN_RED] = \
            self._number_of_opponent_pieces_captured_red / player_turn_number
        feats.extracted_features[feats.MEAN_AMOUNT_CAPTURES_PER_TURN_BLUE] = \
            self._number_of_opponent_pieces_captured_blue / player_turn_number

        feats.extracted_features[feats.MEAN_VALUE_CAPTURES_PER_TURN_RED] = \
            self._value_of_opponent_pieces_captured_red / player_turn_number
        feats.extracted_features[feats.MEAN_VALUE_CAPTURES_PER_TURN_BLUE] = \
            self._value_of_opponent_pieces_captured_blue / player_turn_number

        feats.extracted_features[feats.SUM_MOVES_TOWARD_OPPONENT_BOARD_EDGE_RED] = self._moves_toward_opponent_red
        feats.extracted_features[feats.SUM_MOVES_TOWARD_OPPONENT_BOARD_EDGE_BLUE] = self._moves_toward_opponent_blue




