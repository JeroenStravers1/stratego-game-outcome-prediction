from datapoint_feature_containment import DataPointFeatureContainer
import value_calculation as val_calc
import numpy as np
import sys
sys.path.append("../")
import rank_encodings as ranks
import game_board_descriptors as board
import utils


class FeatureExtractor:
    """
    extracts all features that do not need information regarding previous turns to calculate. Mainly a value container.
    """

    def __init__(self, board_state: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray,
                 feature_container: DataPointFeatureContainer, red_bombs: list, blue_bombs: list, red_flag: list,
                 blue_flag: list) -> None:

        self.feats = feature_container

        self.board_state = board_state
        self.unmoved_pieces = unmoved_pieces
        self.unrevealed_pieces = unrevealed_pieces

        self.red_bombs = red_bombs
        self.blue_bombs = blue_bombs
        self.red_flag = red_flag
        self.blue_flag = blue_flag

        self.piece_values_red = np.zeros([board.ROWS, board.COLS])
        self.piece_values_blue = np.zeros([board.ROWS, board.COLS])

        self.red_discovery_cost = val_calc.BASE_REVEAL_PENALTY
        self.red_base_value = val_calc.BASE_VALUE

        self.blue_discovery_cost = val_calc.BASE_REVEAL_PENALTY
        self.blue_base_value = val_calc.BASE_VALUE

        self.red_pieces_amount = utils.EMPTY
        self.red_pieces_movable_amount = utils.EMPTY
        self.blue_pieces_amount = utils.EMPTY
        self.blue_pieces_movable_amount = utils.EMPTY

    def extract_features(self) -> None:
        """
        coordinate the extraction of all non-long term features, stores them in the DataPointFeatureContainer
        """
        red_pieces, blue_pieces = val_calc.get_amount_of_pieces_per_rank(self.board_state)
        red_unmoved_pieces, blue_unmoved_pieces = val_calc.get_amount_of_pieces_per_rank(self.unmoved_pieces)
        red_unrevealed_pieces, blue_unrevealed_pieces = val_calc.get_amount_of_pieces_per_rank(self.unrevealed_pieces)

        self.red_pieces_amount = sum(red_pieces.values())
        self.blue_pieces_amount = sum(blue_pieces.values())

        self.red_pieces_movable_amount = val_calc.determine_player_amount_of_moving_pieces(ranks.PLAYER_RED, red_pieces)
        self.blue_pieces_movable_amount = val_calc.determine_player_amount_of_moving_pieces(ranks.PLAYER_BLUE,
                                                                                            blue_pieces)
        self._assign_piece_values(red_pieces, blue_pieces, red_unrevealed_pieces, blue_unrevealed_pieces)
        self._store_features_in_container(red_unmoved_pieces, blue_unmoved_pieces, red_unrevealed_pieces,
                                          blue_unrevealed_pieces)

    def _assign_piece_values(self, red_pieces: dict, blue_pieces: dict, red_unrevealed_pieces: dict,
                             blue_unrevealed_pieces: dict) -> None:
        """
        assign values for each piece. First assign base value and revealed penalty, then handle pieces with specific
        value rules
        :param red_pieces: the number of pieces for each rank
        :param blue_pieces: the number of pieces for each rank
        :param red_unrevealed_pieces: the number of unrevealed pieces for each rank
        :param blue_unrevealed_pieces: the number of unrevealed pieces for each rank
        """
        self._determine_reveal_and_base_penalties()
        red_rank_values = val_calc.determine_rank_values(blue_pieces, red_pieces)
        blue_rank_values = val_calc.determine_rank_values(red_pieces, blue_pieces)
        exceptional_valued_movable_pieces = dict()
        for ind_row, row in enumerate(self.board_state):
            for ind_col, column in enumerate(row):
                current_piece_type = self.board_state[ind_row, ind_col]
                if current_piece_type not in ranks.NO_PIECES:
                    current_piece_value_index = ranks.ALL_PIECES[current_piece_type] - utils.START_AT_ZERO_MODIFIER
                    current_piece_revealed = val_calc.is_revealed([ind_row, ind_col], self.unrevealed_pieces)
                    player = val_calc.determine_piece_color(current_piece_type)
                    piece_value_modifier = self._determine_applicable_base_value_modifier(current_piece_revealed, player)
                    self._store_piece_exceptional_value_locations(current_piece_type, [ind_row, ind_col],
                                                                  exceptional_valued_movable_pieces)
                    if current_piece_type not in ranks.ALL_STATIC_PIECES:
                        if player == ranks.PLAYER_RED:
                            piece_value = red_rank_values[current_piece_value_index] * piece_value_modifier
                            self.piece_values_red[ind_row, ind_col] = piece_value
                        else:
                            piece_value = blue_rank_values[current_piece_value_index] * piece_value_modifier
                            self.piece_values_red[ind_row, ind_col] = piece_value
        self._apply_exceptional_values(exceptional_valued_movable_pieces, red_pieces, blue_pieces,
                                       red_unrevealed_pieces, blue_unrevealed_pieces)

    def _determine_applicable_base_value_modifier(self, current_piece_revealed: bool, player: int) -> float:
        """
        determine the correct modifier for the piece based on whether it has been revealed or nog
        :param current_piece_revealed:
        :param player: the current player
        :return: the base modifier for the piece's value (piece value * modifier, so modifier 1 signifies unrevealed)
        """
        if current_piece_revealed:
            return self.red_discovery_cost if player == ranks.PLAYER_RED else self.blue_discovery_cost
        else:
            return self.red_base_value if player == ranks.PLAYER_RED else self.blue_base_value

    def _determine_reveal_and_base_penalties(self) -> None:
        """
        account for the fact that the identity of pieces becomes clearer as fewer remain, by reducing both the base
        value of pieces and the discovery penalty. This means that being discovered will become less punishing, while
        the 'bonus' of being unrevealed becomes worth less.
        """
        red_modifier = val_calc.calculate_reveal_base_penalty_modifier(self.red_pieces_movable_amount)
        blue_modifier = val_calc.calculate_reveal_base_penalty_modifier(self.blue_pieces_movable_amount)
        self.red_base_value = val_calc.BASE_REVEAL_PENALTY + red_modifier
        self.red_discovery_cost = val_calc.BASE_VALUE - red_modifier
        self.blue_base_value = val_calc.BASE_REVEAL_PENALTY + blue_modifier
        self.blue_discovery_cost = val_calc.BASE_VALUE + blue_modifier

    def _store_piece_exceptional_value_locations(self, piece_type: str, piece_location: list,
                                                 exceptional_valued_movable_pieces: dict) -> None:
        """
        store the locations of movable pieces with exceptional values (spy, scout, miner, marshal)
        :param piece_type: the type of the piece
        :param piece_location: [row, column] (ints)
        :param exceptional_valued_movable_pieces: the dict containing the locations of these pieces
        """
        if piece_type in ranks.RED_EXCEPTIONAL_VALUE_MOVABLE_PIECES \
                or piece_type in ranks.BLUE_EXCEPTIONAL_VALUE_MOVABLE_PIECES:
            if piece_type not in exceptional_valued_movable_pieces:
                exceptional_valued_movable_pieces[piece_type] = [piece_location]
            else:
                exceptional_valued_movable_pieces[piece_type].append(piece_location)

    def _apply_exceptional_values(self, exceptional_valued_movable_pieces: dict, red_pieces: dict, blue_pieces: dict,
                                  red_unrevealed_pieces: dict, blue_unrevealed_pieces: dict) -> None:
        """
        assign all exceptional values (bombs, spies, scouts, miners and marshals)
        :param exceptional_valued_movable_pieces: dict with locations of pieces with special value assignment rules
        :param red_pieces: number of red pieces per rank
        :param blue_pieces: number of red pieces per rank
        :param red_unrevealed_pieces: number of red unrevealed pieces per rank
        :param blue_unrevealed_pieces: number of blue unrevealed pieces per rank
        """
        for piece_type in exceptional_valued_movable_pieces:
            current_player = val_calc.determine_piece_color(piece_type)
            current_piece_type_locations = exceptional_valued_movable_pieces[piece_type]
            relevant_player_piece_values = self.piece_values_blue
            opposing_pieces_amounts = red_pieces
            if current_player == ranks.PLAYER_RED:
                relevant_player_piece_values = self.piece_values_red
                opposing_pieces_amounts = blue_pieces
            if piece_type not in [ranks.R_1, ranks.B_1]:
                for location in current_piece_type_locations:
                    modifier = val_calc.get_exceptional_piece_type_value_modifier(piece_type, opposing_pieces_amounts)
                    relevant_player_piece_values[location[board.Y_POS], location[board.X_POS]] *= modifier
        val_calc.handle_spy_values(exceptional_valued_movable_pieces, ranks.R_1, ranks.B_10,
                                   self.piece_values_red, self.piece_values_blue)
        val_calc.handle_spy_values(exceptional_valued_movable_pieces, ranks.B_1, ranks.R_10,
                                   self.piece_values_blue, self.piece_values_red)
        val_calc.handle_scout_values(exceptional_valued_movable_pieces, ranks.R_2, blue_unrevealed_pieces,
                                     self.piece_values_red)
        val_calc.handle_scout_values(exceptional_valued_movable_pieces, ranks.B_2, red_unrevealed_pieces,
                                     self.piece_values_blue)
        val_calc.handle_bomb_values(self.red_bombs, self.piece_values_blue, self.piece_values_red)
        val_calc.handle_bomb_values(self.blue_bombs, self.piece_values_red, self.piece_values_blue)

    def _store_features_in_container(self, red_unmoved_pieces: dict, blue_unmoved_pieces: dict,
                                     red_unrevealed_pieces: dict, blue_unrevealed_pieces: dict) -> None:
        self._store_information_features(red_unmoved_pieces, blue_unmoved_pieces,
                                         red_unrevealed_pieces, blue_unrevealed_pieces)
        self.feats.extracted_features[self.feats.SUM_PIECES_RED] = self.red_pieces_amount
        self.feats.extracted_features[self.feats.SUM_PIECES_BLUE] = self.blue_pieces_amount
        self.feats.extracted_features[self.feats.SUM_PIECES_RED_MOVABLE] = self.red_pieces_movable_amount
        self.feats.extracted_features[self.feats.SUM_PIECES_BLUE_MOVABLE] = self.blue_pieces_movable_amount
        self._store_relative_strength_features()
        self._store_board_position_features()
        self._store_board_chunk_features()  # runs, but test values!


    def _store_information_features(self, red_unmoved_pieces: dict, blue_unmoved_pieces: dict,
                                    red_unrevealed_pieces: dict, blue_unrevealed_pieces: dict) -> None:
        """
        Store all non-long term features that fall under the INFORMATION header
        :param red_unmoved_pieces:
        :param blue_unmoved_pieces:
        :param red_unrevealed_pieces:
        :param blue_unrevealed_pieces:
        """
        self.feats.extracted_features[self.feats.UNREVEALED_BOMBS_RED] = val_calc.determine_unrevealed_bombs_amount(
            self.red_bombs, self.unrevealed_pieces)
        self.feats.extracted_features[self.feats.UNREVEALED_BOMBS_BLUE] = val_calc.determine_unrevealed_bombs_amount(
            self.blue_bombs, self.unrevealed_pieces)

        self.feats.extracted_features[self.feats.PERCENTAGE_UNREVEALED_RED] = \
            val_calc.x_relative_to_y(sum(red_unrevealed_pieces.values()), board.STARTING_PIECES_AMOUNT)
        self.feats.extracted_features[self.feats.PERCENTAGE_UNREVEALED_BLUE] = \
            val_calc.x_relative_to_y(sum(blue_unrevealed_pieces.values()), board.STARTING_PIECES_AMOUNT)

        self.feats.extracted_features[self.feats.PERCENTAGE_UNMOVED_RED] = \
            val_calc.x_relative_to_y(sum(red_unmoved_pieces.values()), board.STARTING_PIECES_AMOUNT)
        self.feats.extracted_features[self.feats.PERCENTAGE_UNMOVED_BLUE] = \
            val_calc.x_relative_to_y(sum(blue_unmoved_pieces.values()), board.STARTING_PIECES_AMOUNT)

        self.feats.extracted_features[self.feats.MOST_VALUABLE_REVEALED_PIECE_RED] = \
            val_calc.get_value_of_highest_value_revealed_or_unrevealed_piece(self.piece_values_red,
                                                                             self.unrevealed_pieces,
                                                                             val_calc.REVEALED)
        self.feats.extracted_features[self.feats.MOST_VALUABLE_REVEALED_PIECE_BLUE] = \
            val_calc.get_value_of_highest_value_revealed_or_unrevealed_piece(self.piece_values_blue,
                                                                             self.unrevealed_pieces,
                                                                             val_calc.REVEALED)

        self.feats.extracted_features[self.feats.MOST_VALUABLE_UNREVEALED_PIECE_RED] = \
            val_calc.get_value_of_highest_value_revealed_or_unrevealed_piece(self.piece_values_red,
                                                                             self.unrevealed_pieces,
                                                                             val_calc.UNREVEALED)
        self.feats.extracted_features[self.feats.MOST_VALUABLE_UNREVEALED_PIECE_BLUE] = \
            val_calc.get_value_of_highest_value_revealed_or_unrevealed_piece(self.piece_values_blue,
                                                                             self.unrevealed_pieces,
                                                                             val_calc.UNREVEALED)

        self.feats.extracted_features[self.feats.PERCENTAGE_VALUE_UNREVEALED_PIECES_RED] = \
            val_calc.get_relative_value_of_unrevealed_pieces(self.piece_values_red, self.unrevealed_pieces)

        self.feats.extracted_features[self.feats.PERCENTAGE_VALUE_UNREVEALED_PIECES_BLUE] = \
            val_calc.get_relative_value_of_unrevealed_pieces(self.piece_values_blue, self.unrevealed_pieces)

    def _store_relative_strength_features(self) -> None:
        """
        Store all non-long term features that fall under the RELATIVE STRENGTH header
        """
        red_mvp = sum(val_calc.determine_n_highest_values_in_grid(val_calc.HIGHEST, self.piece_values_red))
        blue_mvp = sum(val_calc.determine_n_highest_values_in_grid(val_calc.HIGHEST, self.piece_values_blue))
        relative_strength_red_mvp_versus_blue_mvp = val_calc.x_relative_to_y(red_mvp, blue_mvp)
        self.feats.extracted_features[self.feats.PERCENTAGE_RED_VALUE_STRONGEST_PIECE_VS_BLUE_VALUE_STRONGEST_PIECE] = \
            relative_strength_red_mvp_versus_blue_mvp

        self.feats.extracted_features[self.feats.PERCENTAGE_SUM_RED_VALUE_SUM_BLUE_VALUE] = \
            val_calc.x_relative_to_y(self.piece_values_red.sum(), self.piece_values_blue.sum())

        red_pieces_values = val_calc.get_non_zero_values(self.piece_values_red)
        self.feats.extracted_features[self.feats.STDEV_RED_VALUE_PIECES] = np.std(red_pieces_values)
        blue_pieces_values = val_calc.get_non_zero_values(self.piece_values_blue)
        self.feats.extracted_features[self.feats.STDEV_BLUE_VALUE_PIECES] = np.std(blue_pieces_values)

        self.feats.extracted_features[self.feats.MEAN_RED_VALUE_PIECES] = np.mean(red_pieces_values)
        self.feats.extracted_features[self.feats.MEAN_BLUE_VALUE_PIECES] = np.mean(blue_pieces_values)

        sum_red_current_value = sum(red_pieces_values)
        self.feats.extracted_features[self.feats.STARTING_VALUE_PERCENTAGE_RED] = \
            val_calc.x_relative_to_y(sum_red_current_value, board.STARTING_PIECES_TOTAL_VALUE)
        sum_blue_current_value = sum(blue_pieces_values)
        self.feats.extracted_features[self.feats.STARTING_VALUE_PERCENTAGE_BLUE] = \
            val_calc.x_relative_to_y(sum_blue_current_value, board.STARTING_PIECES_TOTAL_VALUE)

        self.feats.extracted_features[self.feats.STARTING_NUMBER_PERCENTAGE_RED] = \
            val_calc.x_relative_to_y(len(red_pieces_values), board.STARTING_PIECES_AMOUNT)
        self.feats.extracted_features[self.feats.STARTING_NUMBER_PERCENTAGE_BLUE] = \
            val_calc.x_relative_to_y(len(blue_pieces_values), board.STARTING_PIECES_AMOUNT)

        red_three_highest_values = val_calc.determine_n_highest_values_in_grid(val_calc.THREE, self.piece_values_red)
        self.feats.extracted_features[self.feats.SUM_THREE_MOST_VALUABLE_RED] = red_three_highest_values
        blue_three_highest_values = val_calc.determine_n_highest_values_in_grid(val_calc.THREE, self.piece_values_blue)
        self.feats.extracted_features[self.feats.SUM_THREE_MOST_VALUABLE_BLUE] = blue_three_highest_values

        self.feats.extracted_features[self.feats.RED_THREE_MOST_VALUABLE_PERCENTAGE_BLUE_THREE_MOST_VALUABLE] = \
            val_calc.x_relative_to_y(sum(red_three_highest_values), sum(blue_three_highest_values))

    def _store_board_position_features(self) -> None:
        """
        Store all non-long term features that fall under the BOARD POSITION header
        """
        self.feats.extracted_features[self.feats.OWN_FLAG_SAFE_RED] = \
            val_calc.determine_flag_protected(self.red_flag, self.board_state)
        self.feats.extracted_features[self.feats.OWN_FLAG_SAFE_BLUE] = \
            val_calc.determine_flag_protected(self.blue_flag, self.board_state)

        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_ONE_TILE_RADIUS_OWN_FLAG_RED] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.ONE, self.red_flag,
                                                                                    self.piece_values_red)
        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_ONE_TILE_RADIUS_OWN_FLAG_BLUE] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.ONE, self.blue_flag,
                                                                                    self.piece_values_blue)

        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_TWO_TILE_RADIUS_OWN_FLAG_RED] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.TWO, self.red_flag,
                                                                                    self.piece_values_red)
        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_TWO_TILE_RADIUS_OWN_FLAG_BLUE] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.TWO, self.blue_flag,
                                                                                    self.piece_values_blue)

        self.feats.extracted_features[self.feats.SUM_VALUE_HOSTILES_ONE_TILE_RADIUS_OWN_FLAG_RED] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.ONE, self.red_flag,
                                                                                    self.piece_values_blue)
        self.feats.extracted_features[self.feats.SUM_VALUE_HOSTILES_ONE_TILE_RADIUS_OWN_FLAG_BLUE] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.ONE, self.blue_flag,
                                                                                    self.piece_values_red)

        self.feats.extracted_features[self.feats.SUM_VALUE_HOSTILES_TWO_TILE_RADIUS_OWN_FLAG_RED] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.TWO, self.red_flag,
                                                                                    self.piece_values_blue)
        self.feats.extracted_features[self.feats.SUM_VALUE_HOSTILES_TWO_TILE_RADIUS_OWN_FLAG_BLUE] = \
            val_calc.get_total_values_pieces_in_n_tile_radius_from_location_in_grid(val_calc.TWO, self.blue_flag,
                                                                                    self.piece_values_red)

        self.feats.extracted_features[self.feats.SUM_POSSIBLE_MOVES_RED] = \
            val_calc.get_possible_moves_amount_by_comparing_own_pieces_to_all_pieces(
                self.piece_values_red, self.board_state)
        self.feats.extracted_features[self.feats.SUM_POSSIBLE_MOVES_BLUE] = \
            val_calc.get_possible_moves_amount_by_comparing_own_pieces_to_all_pieces(
                self.piece_values_blue, self.board_state)

        self.feats.extracted_features[self.feats.SUM_FRIENDLIES_WITH_HOSTILES_ADJACENT_TILE_RED] = \
            val_calc.sum_pieces_with_adjacent_hostiles(self.piece_values_red, self.piece_values_blue)
        self.feats.extracted_features[self.feats.SUM_FRIENDLIES_WITH_HOSTILES_ADJACENT_TILE_BLUE] = \
            val_calc.sum_pieces_with_adjacent_hostiles(self.piece_values_blue, self.piece_values_red)

        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_WITH_ADJACENT_HOSTILES_RED] = \
            val_calc.sum_value_own_pieces_with_adjacent_hostiles(self.piece_values_red, self.piece_values_blue)
        self.feats.extracted_features[self.feats.SUM_VALUE_FRIENDLIES_WITH_ADJACENT_HOSTILES_BLUE] = \
            val_calc.sum_value_own_pieces_with_adjacent_hostiles(self.piece_values_blue, self.piece_values_red)

    def _store_board_chunk_features(self) -> None:
        """
        Store all non-long term features that fall under the BOARD CHUNK header; sum piece values per chunk per player
        """
        chunks = board.generate_chunk_coordinates(board.CHUNKS_TOP_LEFT_DIMENSIONS)
        self.feats.extracted_features[self.feats.R_A10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_10], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_A10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_10], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_A8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_8], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_A8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_8], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_A6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_6], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_A6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_6], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_A4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_4], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_A4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_4], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_A2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_2], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_A2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.A_2], self.piece_values_blue)

        self.feats.extracted_features[self.feats.R_D10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_10], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_D10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_10], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_D8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_8], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_D8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_8], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_E6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.E_6], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_E6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.E_6], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_D4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_4], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_D4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_4], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_D2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_2], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_D2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.D_2], self.piece_values_blue)

        self.feats.extracted_features[self.feats.R_H10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_10], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_H10] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_10], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_H8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_8], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_H8] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_8], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_I6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.I_6], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_I6] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.I_6], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_H4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_4], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_H4] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_4], self.piece_values_blue)
        self.feats.extracted_features[self.feats.R_H2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_2], self.piece_values_red)
        self.feats.extracted_features[self.feats.B_H2] = val_calc.get_total_value_of_pieces_in_chunk(
            chunks[board.H_2], self.piece_values_blue)


if __name__ == "__main__":
    y = np.array([[1,2], [3,4]])
    b = [3,4,6,4,3,6,7,8,4,4]
    # print(np.mean(b))
    # print(y.sum())
    # print(1/0)
    a = False
    b = True
    c = False
