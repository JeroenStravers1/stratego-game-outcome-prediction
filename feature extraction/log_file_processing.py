import os
import sys
import string
import copy
import numpy as np
import collections
import xml.etree.ElementTree as xml_tree
from game_state_tracking import GameStateTracker
import api_stratego_prediction as api
sys.path.append("../")
import utils
import rank_encodings as ranks
import game_board_descriptors as board_desc


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

    _RED = 1
    _BLUE = 2

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
        player_deployment, unmoved_pieces, unrevealed_pieces = self._interpret_starting_position(game_node) # moet een keer voor de beginopstellinge en aparte calc feature call gooien.

        # FIXME
        first_turn_features = api.calculate_features(player_deployment, unmoved_pieces, unrevealed_pieces)

        turn_effect_generator  = self._interpret_turns(game_node, player_deployment, unmoved_pieces, unrevealed_pieces)
        self._store_initial_and_extracted_features_in_csv(dict(), turn_effect_generator, "") #FIXME placeholder args for #0 and #2

    def _interpret_game_log_winner(self, game_node: xml_tree.Element) -> int:  # comment updated
        """
        return the id of the player that won the game from the stratego/game/result node)
        :param game_node: the xml tree node containing all game log information
        :return: (int) winning player (_RED (1) or _BLUE (2))
        """
        result_node = game_node.find(self._RESULT_NODE)
        winning_player = int(result_node.get(self._WINNER))
        return winning_player

    def _interpret_starting_position(self, game_node: xml_tree.Element) -> [np.ndarray, np.ndarray, np.ndarray]:  # comment updated
        """
        convert the inverted (upside-down) single string player deployment to a regular 2d list
        :param game_node: the xml tree node containing all game log information
        :return: three ndarrays to use as the players' deployments. Used to track current piece/rank positions,
        which pieces did not move and to track which pieces have not been revealed to the opponent
        """
        deployment_node = game_node.find(self._START_POSITION_NODE)
        deployment_as_single_string = deployment_node.get(self._DEPLOYMENT)
        deployment = list()
        unmoved_pieces = list()
        revealed_pieces = list()
        for row_index in range(self._ROWS_AMOUNT):
            start_of_row = row_index * self._COLS_AMOUNT
            end_or_row = self._COLS_AMOUNT + row_index * self._COLS_AMOUNT
            current_row = list(deployment_as_single_string[start_of_row:end_or_row])
            deployment.append(current_row)
            unmoved_pieces.append(copy.deepcopy(current_row))
            revealed_pieces.append(copy.deepcopy(current_row))
        return np.array(deployment), np.array(unmoved_pieces), np.array(revealed_pieces)

    def _interpret_turns(self, game_node: xml_tree.Element, board_state, unmoved_pieces, unrevealed_pieces) -> None:  # comment updated
        """
        interpret all individual moves in a log file
        :param game_node: the xml node containing all game information
        :param board_state: the current positions of ranks on the board
        :param unmoved_pieces: the current positions of unmoved pieces on the board (ranks)
        :param unrevealed_pieces: the current positions of unrevealed pieces on the board (ranks)
        """
        turn_nodes = game_node.findall(self._MOVE_NODE)
        for node in turn_nodes:
            source = node.get(self._SOURCE)
            target = node.get(self._TARGET)
            yield self._interpret_move(source, target, board_state, unmoved_pieces, unrevealed_pieces)

    def _interpret_move(self, source: str, target: str, board_state: list, unmoved_pieces: list,  # comment updated
                        unrevealed_pieces: list) -> [np.ndarray, np.ndarray, np.ndarray, int, int]:
        """
        interpret the result of the 'A4' -> 'B4' annotated move and update the three board representations accordingly.
        :param source: location from where the move action was initiated
        :param target: destination of the move action
        :param board_state: representation of the board containing ranks of pieces per location
        :param unmoved_pieces: representation of the board containing only unmoved pieces
        :param unrevealed_pieces: representation of the board containing only unrevealed pieces
        :return: updated board representations and the move (source and target location)
        """
        source_location = utils.parse_location_encoding_to_row_column(source)
        target_location = utils.parse_location_encoding_to_row_column(target)
        source_piece = board_state[source_location[self._ROW]][source_location[self._COLUMN]]
        target_piece = board_state[target_location[self._ROW]][target_location[self._COLUMN]]
        result_source_tile, result_target_tile, move_result = ranks.determine_move_to_result(source_piece, target_piece)
        board_state[source_location[self._ROW]][source_location[self._COLUMN]] = result_source_tile
        board_state[target_location[self._ROW]][target_location[self._COLUMN]] = result_target_tile
        unmoved_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY_TILE
        unmoved_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = ranks.EMPTY_TILE
        self._determine_moved_pieces(source_location, target_location, move_result,
                                     unrevealed_pieces)
        return np.array(board_state), np.array(unmoved_pieces), np.array(unrevealed_pieces), source, target

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
        if not (unrevealed_grid_source == ranks.EMPTY_TILE and unrevealed_grid_target == ranks.EMPTY_TILE): # check of allebei de stukken niet al onthuld zijn
            if move_result == ranks.MOVE_EMPTY:
                unrevealed_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = unrevealed_grid_source
                unrevealed_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY_TILE
            else:
                unrevealed_pieces[target_location[self._ROW]][target_location[self._COLUMN]] = ranks.EMPTY_TILE
                unrevealed_pieces[source_location[self._ROW]][source_location[self._COLUMN]] = ranks.EMPTY_TILE

    def _store_initial_and_extracted_features_in_csv(self, deployment_features: dict,
                                                     turn_effect_generator: collections.Iterable,
                                                     output_file_path: str):
        # with open(output_file_path, "a+") as output_file:
        #     output_file.write()
        for game_state, unmoved_pieces, unrevealed_pieces, source, target in turn_effect_generator:
            current_turn_features = api.calculate_features(game_state, unmoved_pieces, unrevealed_pieces, source,
                                                           target)

    def _convert_features_to_string(self):
        pass


if __name__ == "__main__":
    example_path = ("C:/Users/Jeroen/Desktop/test")
    log_processor_test = LogProcessor(example_path)
    log_processor_test.process_game_logs()
