from os import listdir
import xml.etree.ElementTree
import sys
sys.path.append("../")
import utils


class GameEndingTypeExtractor:
    """
    yields the ending type (int) and path to the log of games
    """

    _CLASSIC_LOG = "classic-"
    _RESULT_NODE = "./game/result"
    _GAME_ENDING_TYPE = "type"
    _PROCESSING = "processing:"

    def __init__(self, target_path):
        self._main_log_directory = target_path

    def get_game_endings(self):
        """
        handle processing of subdirectories in the current main directory
        """
        subdirectories = listdir(self._main_log_directory)
        for subdir in subdirectories:
            self._display_progress(subdir)
            path_to_subdir = utils.extend_path_with(self._main_log_directory, subdir)
            yield self._process_all_game_logs_in_dir(path_to_subdir)

    def _process_all_game_logs_in_dir(self, path_to_dir):
        """
        handle parsing of individual game log files in the current subdirectory
        :param path_to_dir: path to the current subdirectory
        """
        game_logs_in_dir = listdir(path_to_dir)
        for game_log in game_logs_in_dir:
            if game_log.startswith(self._CLASSIC_LOG):
                path_to_game_log = utils.extend_path_with(path_to_dir, game_log)
                yield self._parse_individual_game_log(path_to_game_log), path_to_game_log

    def _parse_individual_game_log(self, path_to_log):
        """
        extract the game ending type from the xml structure
        :param path_to_log: the path to an xml game log
        """
        game_log_root = xml.etree.ElementTree.parse(path_to_log).getroot()
        game_type_node = game_log_root.find(self._RESULT_NODE)
        game_ending_type = int(game_type_node.get(self._GAME_ENDING_TYPE))
        return game_ending_type

    def _display_progress(self, dir_name):
        progress = ' '.join([self._PROCESSING, dir_name])
        print(progress)
