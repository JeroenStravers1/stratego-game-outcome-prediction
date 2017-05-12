import os
import sys
import string
import copy
import numpy as np
import collections
import random
from datetime import datetime
import xml.etree.ElementTree as xml_tree
from game_state_tracking import GameStateTracker
import datapoint_feature_containment as dfc
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
    _RED_LABEL = "red"
    _BLUE_LABEL = "blue"

    _PROCESSED_LOGS = "processed.txt"
    _TRAIN_FILE_NAME = "train.txt"
    _EVAL_FILE_NAME = "eval.txt"
    _TEST_FILE_NAME = "test.txt"
    _TRAIN_CHANCE = 7
    _EVAL_CHANCE = 8
    _TEST_CHANCE = 10

    def __init__(self, cleaned_logs_path, output_file_path):
        """
        :param cleaned_logs_path: path to the dir containing all game logs
        """
        self._cleaned_logs_path = cleaned_logs_path
        self._output_file_path = output_file_path

    def process_game_logs(self, resuming_interrupted_run):
        """
        calculate features for all game turns in all game logs. The features are stored in a csv file.
        """
        try:
            all_log_names = os.listdir(self._cleaned_logs_path)
            start_time = datetime.now()
            iteration = 0
            if not resuming_interrupted_run:
                self._write_headers()
            for log_name in all_log_names:
                iteration += 1
                current_log_path = utils.extend_path_with(self._cleaned_logs_path, log_name)
                self._process_individual_log(current_log_path, log_name)
                self.display_progress(iteration, all_log_names, log_name, start_time)
                with open(self._output_file_path + self._PROCESSED_LOGS, "a+") as processed_logs:
                    processed_logs.write(log_name)
                    processed_logs.write("\n")
        except IOError as ioerror:
            print(ioerror)

    def display_progress(self, iteration, all_items, current_item, start_time):
        total_iterations_required = len(all_items)
        percentage_text = "Percentage complete: "
        current_progress_percentage = int((iteration / total_iterations_required) * 100)
        current_time = datetime.now()
        elapsed_time_delta =  current_time - start_time
        elapsed_time_seconds = elapsed_time_delta.seconds
        seconds_per_item = elapsed_time_seconds / iteration
        items_to_process = total_iterations_required - iteration
        eta = int(seconds_per_item * items_to_process)
        progress_output = percentage_text + str(current_progress_percentage) + " (" + str(iteration) + " / " \
                          + str(total_iterations_required) + ") done. ETA in seconds: " + str(eta) + " " + current_item
        print(progress_output)

    def _process_individual_log(self, log_file_path, log_name):
        """
        extract all features from an individual log. Each game turn is treated as a data point.
        :param log_file_path: path to the current game log file
        """
        log_xml_root = xml_tree.parse(log_file_path).getroot()
        game_node = log_xml_root.find(self._GAME_NODE)
        winner = self._interpret_game_log_winner(game_node)
        player_deployment, unmoved_pieces, unrevealed_pieces = self._interpret_starting_position(game_node)
        init_deployment = copy.deepcopy(player_deployment)
        init_unmoved = copy.deepcopy(unmoved_pieces)
        init_unrevealed = copy.deepcopy(unrevealed_pieces)
        api.init_first_turn(init_deployment, init_unmoved, init_unrevealed)
        turn_effect_generator  = self._interpret_turns(game_node, player_deployment, unmoved_pieces, unrevealed_pieces)
        self._store_initial_and_extracted_features_in_csv(dict(), turn_effect_generator, log_name, winner)
        # TODO placeholder arg for #0; implement deployment features

    def _interpret_game_log_winner(self, game_node):
        """
        return the id of the player that won the game from the stratego/game/result node)
        :param game_node: the xml tree node containing all game log information
        :return: (int) winning player (_RED (1) or _BLUE (2))
        """
        result_node = game_node.find(self._RESULT_NODE)
        winning_player = int(result_node.get(self._WINNER))
        return winning_player

    def _interpret_starting_position(self, game_node):  # comment updated
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

    def _interpret_turns(self, game_node, board_state, unmoved_pieces, unrevealed_pieces):
        """
        interpret all individual moves in a log file
        :param game_node: the xml node containing all game information
        :param board_state: the current positions of ranks on the board
        :param unmoved_pieces: the current positions of unmoved pieces on the board (ranks)
        :param unrevealed_pieces: the current positions of unrevealed pieces on the board (ranks)
        """
        turn_nodes = game_node.findall(self._MOVE_NODE)
        for node in turn_nodes:
            # print("-----TURN: " + node.get("id"))
            source = node.get(self._SOURCE)
            target = node.get(self._TARGET)
            yield self._interpret_move(source, target, board_state, unmoved_pieces, unrevealed_pieces)

    def _interpret_move(self, source, target, board_state, unmoved_pieces, unrevealed_pieces):
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

    def _determine_moved_pieces(self, source_location, target_location, move_result, unrevealed_pieces):
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

    def _store_initial_and_extracted_features_in_csv(self, deployment_features, turn_effect_generator, log_name,
                                                     winner):
        """
        process each turn and store its features in train, eval or test files.
        :param deployment_features: not used, deployment is not a separate feature (yet!)
        :param turn_effect_generator: generator containing all turns in a log
        :param log_name: name of the log file
        :param winner: winner of the game
        :return:
        """
        for game_state, unmoved_pieces, unrevealed_pieces, source, target in turn_effect_generator:
            current_turn_feature_object = api.calculate_features(game_state, unmoved_pieces, unrevealed_pieces,
                                                                 source, target)
            relevant_output_file = self._determine_train_eval_or_test()
            features = self._get_feature_values_as_string(current_turn_feature_object, winner, log_name)
            with open(relevant_output_file, "a+") as output_file:
                output_file.write(features)
                output_file.write("\n")

    def _get_feature_values_as_string(self, current_turn_feature_object, winner, log_name):
        """
        get all feature values in the object's dict as string in set order (n-1 == class, n == origin log)
        :param current_turn_feature_object:
        :param winner:
        :param log_name:
        :return:
        """
        features = ""
        for feature in range(current_turn_feature_object.FEATURE_TOTAL):
            if features == "":
                features = str(current_turn_feature_object.extracted_features[feature])
            else:
                features = features + "," + str(current_turn_feature_object.extracted_features[feature])
        winner_label = self._RED_LABEL if winner == self._RED else self._BLUE_LABEL
        features = features + "," + winner_label
        features = features + "," + log_name
        return features

    def _write_headers(self):
        """
        add the header line with column names to all three relevant text files
        :return:
        """
        header = ""
        for feat_name in dfc.FEATURE_NAMES:
            if header == "":
                header = feat_name
            else:
                header = header + "," + feat_name
        header += "\n"
        with open(self._output_file_path + self._TRAIN_FILE_NAME, "a+") as output_file:
            output_file.write(header)
        with open(self._output_file_path + self._EVAL_FILE_NAME, "a+") as output_file:
            output_file.write(header)
        with open(self._output_file_path + self._TEST_FILE_NAME, "a+") as output_file:
            output_file.write(header)

    def _determine_train_eval_or_test(self):
        """
        randomly determine which file the current data point will be written to
        :return:
        """
        relevant_output_file = ""
        assignment_train_eval_test = random.randint(0, 9)
        if assignment_train_eval_test < self._TRAIN_CHANCE:
            relevant_output_file = self._output_file_path + self._TRAIN_FILE_NAME
        elif assignment_train_eval_test < self._EVAL_CHANCE:
            relevant_output_file = self._output_file_path + self._EVAL_FILE_NAME
        elif assignment_train_eval_test < self._TEST_CHANCE:
            relevant_output_file = self._output_file_path + self._TEST_FILE_NAME
        return relevant_output_file

if __name__ == "__main__":
    resuming_interrupted_log_file_processing = False
    #files_to_process = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/test2/test"
    files_to_process = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/Cleaned_Stratego_Games/strados_clean"
    output_file_path = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/"
    #output_file_path = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/testoutput/"

    log_processor_test = LogProcessor(files_to_process, output_file_path)
    log_processor_test.process_game_logs(resuming_interrupted_log_file_processing)
