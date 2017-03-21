import sys
sys.path.append("../")
import game_ending_type_extraction as g_e_t_extraction


class UniqueEndingTypeIdentifier:
    """
    identifies unique ending types and provides the path to an example for further analysis
    (there is no documentation on the Gravon.de site that I could find)
    """

    def __init__(self, target_path):
        self._encountered_ending_types = dict()
        self._main_log_directory = target_path

    def store_paths_to_logs_of_unique_game_endings(self, path_to_log, ending_type):
        """
        store the game ending type and the path to an xml containing an example of this ending (relative to the main
        game log directory) in self._encountered_ending_types
        :param path_to_log: the path to the current game log being processed
        :param ending_type: the numerical type of game ending
        """
        if ending_type not in self._encountered_ending_types:
            cleaned_path_to_log = path_to_log.replace(self._main_log_directory, "")
            self._encountered_ending_types[ending_type] = cleaned_path_to_log

    def display_examples_of_unique_game_endings(self):
        """
        display the results in the console, sorted ascending
        """
        sorted_ending_types = sorted(self._encountered_ending_types.keys())
        for ending_type in sorted_ending_types:
            print(ending_type)
            print(self._encountered_ending_types[ending_type])


if __name__ == "__main__":
    #path = "C:/Users/Jeroen/Desktop/Stratego games-20170320T133045Z-001/Stratego games"
    path = "C:/Users/Jeroen/Desktop/Stratego games-20170320T133045Z-001/Cleaned_Stratego_Games"
    extractor = g_e_t_extraction.GameEndingTypeExtractor(path)
    type_identifier = UniqueEndingTypeIdentifier(path)

    for game_log_subdir_processor in extractor.get_game_endings():
        for ending_type, log_path in game_log_subdir_processor:
            type_identifier.store_paths_to_logs_of_unique_game_endings(log_path, ending_type)

    type_identifier.display_examples_of_unique_game_endings()
