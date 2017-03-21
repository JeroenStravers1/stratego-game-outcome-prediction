import sys
sys.path.append("../")
import game_ending_type_extraction as g_e_t_extraction
import utils


class UniqueEndingTypeIdentifier:
    """
    identifies unique ending types and provides the path to an example for further analysis
    (there is no documentation on the Gravon.de site that I could find)
    """

    def __init__(self, target_path):
        self._encountered_ending_types = dict()
        self._main_log_directory = target_path

    def display_examples_of_unique_game_endings(self, game_endings_with_paths):
        """
        display the results in the console, sorted ascending
        """
        self._store_paths_to_logs_of_unique_game_endings(game_endings_with_paths)
        sorted_ending_types = sorted(self._encountered_ending_types.keys())
        for ending_type in sorted_ending_types:
            print(ending_type)
            print(self._encountered_ending_types[ending_type])

    def _store_paths_to_logs_of_unique_game_endings(self, game_endings_with_paths):
        """
        store the game ending type and the path to an xml containing an example of this ending (relative to the main
        game log directory) in self._encountered_ending_types
        :param path_to_log: the path to the current game log being processed
        :param ending_type: the numerical type of game ending
        """
        for game_log_subdir_processor in game_endings_with_paths:
            for ending_type, log_path in game_log_subdir_processor:
                if ending_type not in self._encountered_ending_types:
                    log_name = utils.get_item_by_index_from_string_split_on(
                        utils.LAST_ITEM_IN_LIST,
                        log_path,
                        utils.FORWARD_SLASH)
                    self._encountered_ending_types[ending_type] = log_name


if __name__ == "__main__":
    #path = "C:/Users/Jeroen/Desktop/Stratego games-20170320T133045Z-001/Stratego games"
    path = "C:/Users/Jeroen/Desktop/Stratego games-20170320T133045Z-001/Cleaned_Stratego_Games"
    extractor = g_e_t_extraction.GameEndingTypeExtractor(path)
    game_endings_with_paths = extractor.get_game_endings()

    type_identifier = UniqueEndingTypeIdentifier(path)
    type_identifier.display_examples_of_unique_game_endings(game_endings_with_paths)
