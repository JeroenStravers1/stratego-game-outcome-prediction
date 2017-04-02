import os
import sys
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

    _ROWS = 10
    _COLS = 10
    _START_AT_ZERO_MODIFIER = 1

    _RED = 1
    _BLUE = 2

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

        winner = self._interpret_winner(game_node)
        print(winner)
        player_deployment = self._interpret_starting_position(game_node)
        print(player_deployment)
        self._interpret_turns(game_node)


    def _interpret_winner(self, game_node):
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
        :return: (list(list(str))) the players' deployments
        """
        deployment_node = game_node.find(self._START_POSITION_NODE)
        deployment_as_single_string = deployment_node.get(self._DEPLOYMENT)
        deployment = list()
        for row_index in range(self._ROWS):
            reverse_index = self._COLS - row_index - self._START_AT_ZERO_MODIFIER
            start_of_row = reverse_index * self._COLS
            end_or_row = self._COLS + (reverse_index * self._COLS)
            current_row = list(deployment_as_single_string[start_of_row:end_or_row])
            deployment.append(current_row)
        return deployment

    def _interpret_turns(self, game_node, deployment):
        turn_nodes = game_node.findall(self._MOVE_NODE)
        self._feature_extractor.extract_features(deployment)
        for node in turn_nodes:
            print(node.get(self._ID))


if __name__ == "__main__":
    example_path = ("C:/Users/Jeroen/Desktop/test")
    log_processor_test = LogProcessor(example_path)
    log_processor_test.process_game_logs()
