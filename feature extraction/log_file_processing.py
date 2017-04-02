import os
import sys
import string
import numpy as np
import xml.etree.ElementTree
sys.path.append("../")
from feature_extraction import FeatureExtractor
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

    def __init__(self, cleaned_logs_path):
        self._cleaned_logs_path = cleaned_logs_path
        self._feature_extractor = FeatureExtractor()

    def process_game_logs(self):
        try:
            all_log_names = os.listdir(self._cleaned_logs_path)
            for log_name in all_log_names:
                current_log_path = utils.extend_path_with(self._cleaned_logs_path, log_name)
                self._process_individual_log(current_log_path)
        except FileNotFoundError as fnfe:
            print(fnfe)

    def _process_individual_log(self, log_file_path):
        log_xml_root = xml.etree.ElementTree.parse(log_file_path).getroot()
        game_node = log_xml_root.find(self._GAME_NODE)

        winner = self._interpret_game_log_winner(game_node)
        print(winner)
        player_deployment = self._interpret_starting_position(game_node)
        print(player_deployment)
        self._interpret_turns(game_node, player_deployment)

    def _interpret_game_log_winner(self, game_node):
        """
        return the id of the player that won the game from the stratego/game/result node
        :param game_node: xml tree node containing all game information
        :return: (int) player id. _RED (1) or _BLUE (2)
        """
        result_node = game_node.find(self._RESULT_NODE)
        winning_player = int(result_node.get(self._WINNER))
        return winning_player

    def _interpret_starting_position(self, game_node):
        """
        convert the inverted (upside-down) single string player deployment to a regular 2d list
        :param game_node: the xml tree node containing all game log information
        :return: (list(list(str))) the players' deployments (row list containing column lists)
        """
        deployment_node = game_node.find(self._START_POSITION_NODE)
        deployment_as_single_string = deployment_node.get(self._DEPLOYMENT)
        deployment = list()
        for row_index in range(self._ROWS_AMOUNT):
            reverse_index = self._COLS_AMOUNT - row_index - self._START_AT_ZERO_MODIFIER
            start_of_row = reverse_index * self._COLS_AMOUNT
            end_or_row = self._COLS_AMOUNT + (reverse_index * self._COLS_AMOUNT)
            current_row = list(deployment_as_single_string[start_of_row:end_or_row])
            deployment.append(current_row)
        return deployment

    def _interpret_turns(self, game_node, deployment):
        game_state = deployment
        turn_nodes = game_node.findall(self._MOVE_NODE)
        self._feature_extractor.extract_features(deployment)
        for node in turn_nodes:
            source = node.get(self._SOURCE)
            target = node.get(self._TARGET)
            self._interpret_move(source, target, game_state)
            print(node.get(self._ID))

    def _interpret_move(self, source, target, game_state):
        source_location = self._parse_location_encoding__to_row_column(source)
        target_location = self._parse_location_encoding__to_row_column(target)
        source_piece = game_state[source_location[self._ROW]][source_location[self._COLUMN]]
        target_piece = game_state[target_location[self._ROW]][target_location[self._COLUMN]]
        move_result = self._determine_move_to_result(source_piece, target_piece) #FIXME update gamestate?
        print(source_location)
        print(target_location)
        print(move_result)
        return game_state

    def _parse_location_encoding__to_row_column(self, location):
        """
        parse 'A4' annotated position data to index values usable in a 2D array representation of the game board
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

    # FIXME move interpretations are not required in the final result,
    # FIXME but I will need to deduce what happened in between turns
    def _determine_move_to_result(self, source, target):
        """
        determine the result of the player's move from the source to the target tile
        :param source: the piece in the source tile
        :param target: the piece in the target tile (if any)
        :return: source, target
        """
        if target == ranks.EMPTY:
            return ranks.EMPTY, source#FIXME keep track of revealed/moved pieces here! (do this by keeping copies of the game board array. The "hasmoved: array can work with deletion on move.
        elif target in [ranks.B_F, ranks.R_F]: # TODO do the above by adding 2 positional args here. BTW, the source piece ALWAYS moves here. Identification is another matter though.
            return ranks.EMPTY, source
        elif source in [ranks.B_3, ranks.R_3] and target in [ranks.B_B, ranks.R_B]:
            return ranks.EMPTY, source
        elif target in [ranks.B_B, ranks.R_B]:
            return ranks.EMPTY, target
        elif source in [ranks.B_1, ranks.R_1] and target in [ranks.B_10, ranks.R_10]:
            return ranks.EMPTY, source
        else:
            return self._compare_source_to_target_rank(source, target)

    def _compare_source_to_target_rank(self, source, target):
        """
        determines the outcome of the player's move
        :param source: the moving piece
        :param target: the target piece
        :return: the pieces that occupy the source tile and the target tile after the move
        """
        source_rank = self._transform_piece_rank_to_comparable_value(source)
        target_rank = self._transform_piece_rank_to_comparable_value(target)
        if source_rank > target_rank:
            return ranks.EMPTY, source
        elif source_rank < target_rank:
            return ranks.EMPTY, target
        return source, target

    def _transform_piece_rank_to_comparable_value(self, piece_rank):
        """
        Movable piece rank values are given as c:l and o:x. This function transforms them to values of 2:11
        :param piece_rank: Char rank of the piece (see ranks_encodings.py)
        :return: the converted int height of the piece
        """
        rank_height = string.ascii_lowercase.index(piece_rank.lower())
        if rank_height > self._HIGHEST_RANK:
            rank_height -= self._HIGHEST_RANK
        return rank_height


if __name__ == "__main__":
    example_path = ("C:/Users/Jeroen/Desktop/test")
    log_processor_test = LogProcessor(example_path)
    log_processor_test.process_game_logs()
