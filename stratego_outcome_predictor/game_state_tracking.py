import numpy as np
import sys
import copy
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
    _FIRST_TURN = 1
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
        self.piece_values_red = np.zeros([board.ROWS, board.COLS])
        self.piece_values_blue = np.zeros([board.ROWS, board.COLS])
        self.red_bombs = list()
        self.blue_bombs = list()
        self.red_flag = list()
        self.blue_flag = list()

    def init_game_board(self, board_state, unmoved_pieces, unrevealed_pieces): #FIXME implementeer hier de initiele setup
                                # FIXME geef hier ook mee wie waar begint!!!!
        # FIXME eventueel hier een rotate functie? waarin je binnenkomende board data verticaal spiegelt indien de spelers andersom zitten en rood boven staat ipv beneden?
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
        self.piece_values_red = np.zeros([board.ROWS, board.COLS])
        self.piece_values_blue = np.zeros([board.ROWS, board.COLS])
        self.red_bombs = list()
        self.blue_bombs = list()
        self.red_flag = list()
        self.blue_flag = list()

        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces
        self.current_turn_number = self._ZERO
        for ind_row, row in enumerate(self.board_state):
            for ind_col, piece_rank in enumerate(row):
                if piece_rank not in ranks.NO_PIECES:
                    piece_init_value_index = ranks.ALL_PIECES[piece_rank]
                    piece_init_value = ranks.INITIAL_VALUES[piece_init_value_index]
                    if val_calc.determine_piece_color(piece_rank) == ranks.PLAYER_RED:
                        self.piece_values_red[ind_row, ind_col] = piece_init_value
                    else:
                        self.piece_values_blue[ind_row, ind_col] = piece_init_value
        print self.piece_values_red
        print self.piece_values_blue
        quit()

    def update_game_state(self, board_state, unmoved_pieces, unrevealed_pieces, source, target):
        parsed_source = utils.parse_location_encoding_to_row_column(source)
        parsed_target = utils.parse_location_encoding_to_row_column(target)

        self.current_turn_number += self._NEW_TURN
        self._determine_captured_pieces_and_values(parsed_source, parsed_target)
        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces

        self._get_static_piece_positions(board_state)
        extracted_feature_container = dfc.DataPointFeatureContainer()

        feature_extractor = feature_extraction.FeatureExtractor(board_state, unmoved_pieces, unrevealed_pieces,
                                                                extracted_feature_container, self.red_bombs,
                                                                self.blue_bombs, self.red_flag, self.blue_flag)
        feature_extractor.extract_features()
        self.piece_values_red = copy.deepcopy(feature_extractor.piece_values_red)
        self.piece_values_blue = copy.deepcopy(feature_extractor.piece_values_blue)
        self._add_long_term_features_to_feature_container(extracted_feature_container)
        return extracted_feature_container

    def _determine_captured_pieces_and_values(self, source, target):
        """
        get the rank, color and value of the involved piece(s). Call a second function to process the result
        :param source: the 2d array location (y, x) of the source tile (moving from)
        :param target: the 2d array location (y, x) of the target tile (moving to)
        """
        source_piece = self.board_state[source[board.Y_POS], source[board.X_POS]]
        target_piece = self.board_state[target[board.Y_POS], target[board.X_POS]]
        current_player = val_calc.determine_piece_color(source_piece)
        opponent = val_calc.get_other_player(current_player)
        result_source, result_target, result = ranks.determine_move_to_result(source_piece, target_piece)
        self._process_move_result(result, current_player, source, target)
        self._interpret_move_towards_opponent(source, target, current_player, opponent)

    def _process_move_result(self, result, player, source, target):
        """
        process the result of a move action regarding player total captures
        :param result: the result of the move (win, draw, lose, empty)
        :param player: the current player
        :param source: [y,x] tile the move originated from
        :param target: [y,x] tile that's the target of the move
        """
        if result == ranks.MOVE_WIN:
            if player == ranks.PLAYER_RED:
                self._number_of_opponent_pieces_captured_red += val_calc.INCREMENT_ONE
                target_value = self.piece_values_blue[target[board.Y_POS], target[board.X_POS]]
                self._value_of_opponent_pieces_captured_red += target_value
            else:
                self._number_of_opponent_pieces_captured_blue += val_calc.INCREMENT_ONE
                target_value = self.piece_values_red[target[board.Y_POS], target[board.X_POS]]
                self._value_of_opponent_pieces_captured_blue += target_value
        elif result == ranks.MOVE_LOSE:
            if player == ranks.PLAYER_RED:
                self._number_of_opponent_pieces_captured_blue += val_calc.INCREMENT_ONE
                source_value = self.piece_values_red[source[board.Y_POS], source[board.X_POS]]
                self._value_of_opponent_pieces_captured_blue += source_value
            else:
                self._number_of_opponent_pieces_captured_red += val_calc.INCREMENT_ONE
                source_value = self.piece_values_blue[source[board.Y_POS], source[board.X_POS]]
                self._value_of_opponent_pieces_captured_red += source_value
        elif result == ranks.MOVE_DRAW:
            if player == ranks.PLAYER_RED:
                self._number_of_opponent_pieces_captured_red += val_calc.INCREMENT_ONE
                target_value = self.piece_values_blue[target[board.Y_POS], target[board.X_POS]]
                self._value_of_opponent_pieces_captured_red += target_value
                self._number_of_opponent_pieces_captured_blue += val_calc.INCREMENT_ONE
                source_value = self.piece_values_red[source[board.Y_POS], source[board.X_POS]]
                self._value_of_opponent_pieces_captured_blue += source_value
            else:
                self._number_of_opponent_pieces_captured_blue += val_calc.INCREMENT_ONE
                target_value = self.piece_values_red[target[board.Y_POS], target[board.X_POS]]
                self._value_of_opponent_pieces_captured_blue += target_value
                self._number_of_opponent_pieces_captured_red += val_calc.INCREMENT_ONE
                source_value = self.piece_values_blue[source[board.Y_POS], source[board.X_POS]]
                self._value_of_opponent_pieces_captured_red += source_value

    def _interpret_move_towards_opponent(self, source, target, player, opponent):
        """
        store the amount of times players move towards each others board edge.
        :param source: the source tile
        :param target: the target tile
        :param player: the current player
        :param opponent: the opponent
        """
        move_direction = int(target[board.Y_POS]) - int(source[board.Y_POS])
        edges = [board.BOTTOM, board.TOP]
        if self.red_start == board.TOP:
            edges = [board.TOP, board.BOTTOM]
        opposing_edge = edges[opponent]
        if move_direction == opposing_edge:
            if player == ranks.PLAYER_RED:
                self._moves_toward_opponent_red += val_calc.INCREMENT_ONE
            else:
                self._moves_toward_opponent_blue += val_calc.INCREMENT_ONE

    def _get_static_piece_positions(self, board_state):
        self.red_bombs = list()
        self.blue_bombs = list()
        for row_ind, row in enumerate(board_state):
            for col_ind, piece in enumerate(row):
                position = [row_ind, col_ind]
                self._store_static_piece_positions(piece, position)

    def _store_static_piece_positions(self, piece, position):
        if piece == ranks.R_B:
            self.red_bombs.append(position)
        elif piece == ranks.B_B:
            self.blue_bombs.append(position)
        if self.current_turn_number == self._FIRST_TURN:
            if piece == ranks.R_F:
                self.red_flag = position
            elif piece == ranks.B_F:
                self.blue_flag = position

    def _add_long_term_features_to_feature_container(self, feats):
        player_turn_number = val_calc.get_player_turn_number(self.current_turn_number)

        feats.extracted_features[feats.CURRENT_TURN_NUMBER] = self.current_turn_number  #

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
