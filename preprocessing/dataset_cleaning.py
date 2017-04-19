from shutil import copy
import sys
sys.path.append("../")
import game_ending_type_extraction as g_e_t_extraction
sys.path.append("../")
import utils


class CleanedDatasetProvider:
    """
    copies all game logs that are Classic games with an outcome type of 0-4 to a 'cleaned_data' directory
    uses an instance of GameEndingTypeExtractor to get the game endings and file paths
    """

    _CLEANED_DATA_DIR = "../Cleaned_Stratego_Games/strados_clean"
    _CONNECTION_ISSUE_ENDING_TYPES = [10, 11, 12, 13, 14]
    _DRAW_ENDING_TYPES = [2, 4]

    def __init__(self, target_path):
        self._main_log_directory = target_path
        self._clean_dataset_dir_path = utils.extend_path_with(self._main_log_directory, self._CLEANED_DATA_DIR)
        utils.ensure_cleaned_dir_exists(self._clean_dataset_dir_path)

    def copy_clean_dataset_to_cleaned_dir(self, ending_type_and_path_generator):
        """
        organises further processing of the output of the GameEndingTypeExtractor
        :param ending_type_and_path_generator: a generator yielding the game type ending and the path to the game log
        """
        for game_log_subdir_processor in ending_type_and_path_generator:
            for ending_type, log_path in game_log_subdir_processor:
                self._process_individual_log(ending_type, log_path)

    def _process_individual_log(self, ending_type, log_path):
        """
        move the current log to the cleaned directory if the game did not terminate due to connection issues
        :param ending_type: int representing how the game ended
        :param log_path: path to the current log file
        """
        if ending_type not in self._CONNECTION_ISSUE_ENDING_TYPES:
            if ending_type not in self._DRAW_ENDING_TYPES:
                try:
                    copy(log_path, self._clean_dataset_dir_path)
                except IOError as ioerror:
                    print(ioerror)


if __name__ == "__main__":
    red_count = 0
    blue_count = 0
    path = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/Cleaned_Stratego_Games"
    # path = "C:/Users/Jeroen/Desktop/Stratego games-20170320T133045Z-001/Stratego games"
    extractor = g_e_t_extraction.GameEndingTypeExtractor(path)
    game_ending_types_with_paths = extractor.get_game_endings()
    for ending_gen in game_ending_types_with_paths:
        for end, location in ending_gen:
            if int(end) == 1:
                red_count += 1
            else:
                blue_count += 1
    print(red_count)
    print(blue_count)
    # dataset_cleaner = CleanedDatasetProvider(path)
    # dataset_cleaner.copy_clean_dataset_to_cleaned_dir(game_ending_types_with_paths)
