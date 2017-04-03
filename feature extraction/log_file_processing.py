import os
import sys
import string
import copy
import numpy as np
import xml.etree.ElementTree as xml_tree
sys.path.append("../")
from game_state_tracking import GameStateTracker
sys.path.append("../")
import utils
import rank_encodings as ranks


class LogProcessor:
    """
    handles cleaned xml log files turn by turn
    """
    _GAME_ENDING_TYPE = "type"
    _GAME_NODE = "./game"
    _START_POSITION_NODE = "./field"
    _RESULT_NODE = "./result"
    _MOVE_NODE = "./move"
    _WINNER = "winner"
    _DEPLOYMENT = "content"
    _ID = "id"
    _SOURCE = "source"
    _TARGET = "target"

    _ROWS_AMOUNT = 10
    _COLS_AMOUNT = 10
    _X_AXIS = 0
    _Y_AXIS = 1
    _ROW = 0
    _COLUMN = 1
    _CHAR_COLON = ":"
    _COLON_VALUE = "10"
    _START_AT_ZERO_MODIFIER = 1

    _RED = 1
    _BLUE = 2

    _HIGHEST_RANK = 11
    _MOVE_WIN = 0
    _MOVE_DRAW = 1
    _MOVE_LOSE = 2
    _MOVE_EMPTY = 3

    _TURN

    def __init__(self, cleaned_logs_path: str) -> None:
        """
        :param cleaned_logs_path: path to the dir containing all game logs
        """
        self._cleaned_logs_path = cleaned_logs_path

    def process_game_logs(self) -> None:
        """
        calculate features for all game turns in all game logs. The features are stored in a csv file.
        """
        try:
            all_log_names = os.listdir(self._cleaned_logs_path)
            for log_name in all_log_names:
                current_log_path = utils.extend_path_with(self._cleaned_logs_path, log_name)
                self._process_individual_log(current_log_path)
        except FileNotFoundError as fnfe:
            print(fnfe)

    def _process_individual_log(self, log_file_path: str) -> None:
        """
        extract all features from an individual log. Each game turn is treated as a data point.
        :param log_file_path: path to the current game log file
        """
        log_xml_root = xml_tree.parse(log_file_path).getroot()
        game_node = log_xml_root.find(self._GAME_NODE)
        winner = self._interpret_game_log_winner(game_node) #FIXME use winner to annotate class!
        player_deployment, moved_pieces, revealed_pieces = self._interpret_starting_position(game_node)
        game_state_tracker = GameStateTracker(player_deployment, moved_pieces, revealed_pieces)
        self._interpret_turns(game_node, winner, game_state_tracker)

    def _interpret_game_log_winner(self, game_node: xml_tree.Element) -> int:
        """
        return the id of the player that won the game from the stratego/game/result node)
        :param game_node: the xml tree node containing all game log information
        :return: (int) winning player (_RED (1) or _BLUE (2))
        """
        result_node = game_node.find(self._RESULT_NODE)
        winning_player = int(result_node.get(self._WINNER))
        return winning_player

    def _interpret_starting_position(self, game_node: xml_tree.Element) -> [list, list, list]:
        """
        convert the inverted (upside-down) single string player deployment to a regular 2d list
        :param game_node: the xml tree node containing all game log information
        :return: (list(list(str))) three times, to use as the players' deployments, to track which pieces moved
        at least once and to track which pieces have been revealed to the opponent
        """
        deployment_node = game_node.find(self._START_POSITION_NODE)
        deployment_as_single_string = deployment_node.get(self._DEPLOYMENT)
        deployment = list()
        unmoved_pieces = list()
        revealed_pieces = list()
        for row_index in range(self._ROWS_AMOUNT):
            reverse_index = self._COLS_AMOUNT - row_index - self._START_AT_ZERO_MODIFIER
            start_of_row = reverse_index * self._COLS_AMOUNT
            end_or_row = self._COLS_AMOUNT + (reverse_index * self._COLS_AMOUNT)
            current_row = list(deployment_as_single_string[start_of_row:end_or_row])
            deployment.append(current_row)
            unmoved_pieces.append(current_row)
            revealed_pieces.append(current_row)
        return deployment, unmoved_pieces, revealed_pieces

    def _interpret_turns(self, game_node: xml_tree.Element, winner: int, game_state_tracker: GameStateTracker) -> None:
        """
        process each player turn in a log
        :param game_node: the xml tree node containing all game log information
        :param winner: the winning player
        :param game_state_tracker: object containing 2d list representations of game piece positions on the board
        """
        turn_nodes = game_node.findall(self._MOVE_NODE)
        #self._feature_extractor.extract_features(game_state_tracker) #FIXME
        for node in turn_nodes:
            source = node.get(self._SOURCE)
            target = node.get(self._TARGET)
            self._interpret_move(source, target, game_state_tracker)

    def _interpret_move(self, source: str, target: str, game_state_tracker: GameStateTracker) -> None:
        """
        determine the board state after a player's move
        :param source: the moving piece
        :param target: the target tile
        :param game_state_tracker: object containing 2d list representations of game piece positions on the board
        """
        source_location = self._parse_location_encoding_to_row_column(source)# get [y,x]
        target_location = self._parse_location_encoding_to_row_column(target)
        source_piece = game_state_tracker.board_state[source_location[self._ROW]][source_location[self._COLUMN]] # get piece at location
        target_piece = game_state_tracker.board_state[target_location[self._ROW]][target_location[self._COLUMN]]
        result_source_tile, result_target_tile, move_result = self._determine_move_to_result(source_piece, target_piece)
        game_state_tracker.board_state[source_location[self._ROW]][source_location[self._COLUMN]] = result_source_tile
        game_state_tracker.board_state[target_location[self._ROW]][target_location[self._COLUMN]] = result_target_tile
        game_state_tracker.unmoved_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY
        game_state_tracker.unmoved_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = ranks.EMPTY
        self._determine_moved_pieces(source_location, target_location, move_result,
                                     game_state_tracker.unrevealed_pieces)
        game_state_tracker.turns += self._TURN

    def _parse_location_encoding_to_row_column(self, location: str) -> [int, int]:
        """
        parse annotated position data (i.e. 'A4') to index values usable in a 2D array representation of the game board
        :param location: <char + int> annotated location data. In the location values int value 10 is represented
        by ':', char 'J' is replaced by char 'K'.
        :return: (list(int, int)) the row and column values
        """
        raw_row = location[self._Y_AXIS]
        if raw_row == self._CHAR_COLON:
            raw_row = self._COLON_VALUE
        row = int(raw_row) - self._START_AT_ZERO_MODIFIER

        raw_column = location[self._X_AXIS].lower()
        column = string.ascii_lowercase.index(raw_column)
        if column >= self._COLS_AMOUNT:
            column = self._COLS_AMOUNT - self._START_AT_ZERO_MODIFIER

        return [row, column]

    def _determine_move_to_result(self, source: str, target: str) -> [str, str, int]:
        """
        determine the result of the player's move from the source to the target tile
        :param source: the piece rank in the source tile
        :param target: the piece rank in the target tile (if any)
        :return: the updated ranks in the source and target tiles with the result
        """
        if target == ranks.EMPTY:
            return ranks.EMPTY, source, self._MOVE_EMPTY#FIXME keep track of revealed/moved pieces here! (do this by keeping copies of the game board array. The "hasmoved: array can work with deletion on move.
        elif target in [ranks.B_F, ranks.R_F]: # TODO do the above by adding 2 positional args here. BTW, the source piece ALWAYS moves here. Identification is another matter though.
            return ranks.EMPTY, source, self._MOVE_WIN  # FIXME track progress variables (turns, moves_toward_opponent) as external variables, pass by reference to feature_extractor
        elif source in [ranks.B_3, ranks.R_3] and target in [ranks.B_B, ranks.R_B]:
            return ranks.EMPTY, source, self._MOVE_WIN
        elif target in [ranks.B_B, ranks.R_B]:
            return ranks.EMPTY, target, self._MOVE_LOSE
        elif source in [ranks.B_1, ranks.R_1] and target in [ranks.B_10, ranks.R_10]:
            return ranks.EMPTY, source, self._MOVE_WIN
        else:
            return self._compare_source_to_target_rank(source, target)

    def _compare_source_to_target_rank(self, source: str, target: str) -> [str, str]:
        """
        determine the outcome of the player's move
        :param source: the moving piece
        :param target: the target piece
        :return: the pieces that occupy the source tile and the target tile after the move and the move result
        """
        source_rank = self._transform_piece_rank_to_comparable_value(source)
        target_rank = self._transform_piece_rank_to_comparable_value(target)
        if source_rank > target_rank:
            return ranks.EMPTY, source, self._MOVE_WIN
        elif source_rank < target_rank:
            return ranks.EMPTY, target, self._MOVE_LOSE
        return source, target, self._MOVE_DRAW

    def _transform_piece_rank_to_comparable_value(self, piece_rank: str) -> int:
        """
        Movable piece rank values are given as c:l and o:x. This function transforms them to values of 2:11
        :param piece_rank: Char rank of the piece (see ranks_encodings.py)
        :return: the converted int height of the piece
        """
        rank_height = string.ascii_lowercase.index(piece_rank.lower())
        if rank_height > self._HIGHEST_RANK:
            rank_height -= self._HIGHEST_RANK
        return rank_height

    def _determine_moved_pieces(self, source_location: list, target_location: list, move_result: int,
                                unrevealed_pieces: list):
        """
        track a second layer of the board that only contains unrevealed pieces
        :param source_location: the coordinates of the moving piece
        :param target_location: the coordinates of the moving piece's destination
        :param move_result: the result of the move action
        :param unrevealed_pieces: 2D list containing only the ranks of unrevealed pieces, all others are ranks.EMPTY
        """
        unrevealed_grid_source = unrevealed_pieces[source_location[self._ROW]][source_location[self._COLUMN]]
        unrevealed_grid_target =  unrevealed_pieces[target_location[self._ROW]][target_location[self._COLUMN]]
        if not (unrevealed_grid_source == ranks.EMPTY and unrevealed_grid_target == ranks.EMPTY): # check of allebei de stukken niet al onthuld zijn
            if move_result == self._MOVE_EMPTY:
                unrevealed_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = unrevealed_grid_source
                unrevealed_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY
            else:
                unrevealed_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = ranks.EMPTY
                unrevealed_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY


if __name__ == "__main__":
    example_path = ("C:/Users/Jeroen/Desktop/test")
    log_processor_test = LogProcessor(example_path)
    log_processor_test.process_game_logs()
