import os
import string
import game_board_descriptors as board
import xml.etree.ElementTree as xml_tree


LAST_ITEM_IN_LIST = -1
FORWARD_SLASH = "/"
START_AT_ZERO_MODIFIER = 1
START_AT_ONE_MODIFIER = 1
EMPTY = 0


def ensure_cleaned_dir_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except Exception as e:
            print(e)


def extend_path_with(existing_path, dir_name):
    return existing_path + "/" + dir_name


def get_item_by_index_from_string_split_on(target_value_index, string_to_process, split_value):
    split_string = string_to_process.split(split_value)
    return split_string[target_value_index]


def parse_location_encoding_to_row_column(location: str) -> [int, int]:
    """
    parse annotated position data (i.e. 'A4') to index values usable in a 2D array representation of the game board
    :param location: <char + int> annotated location data. In the location values int value 10 is represented
    by ':', char 'J' is replaced by char 'K'.
    :return: (list(int, int)) the row and column values
    """
    raw_row = location[board.X_POS]
    if raw_row == board.CHAR_COLON:
        raw_row = board.COLON_VALUE
    row = int(raw_row) - START_AT_ZERO_MODIFIER
    raw_column = location[board.Y_POS].lower()
    column = string.ascii_lowercase.index(raw_column)
    if column >= board.COLS:
        column = board.COLS - START_AT_ZERO_MODIFIER
    return [row, column]


def clear_additional_header_lines_from_file(file_location) -> None:
    """
    clears additional header lines from files that were mistakenly added upon resuming interrupted log file processing
    the bug causing this behavior has been fixed
    :param file_location: path to file
    """
    with open(file_location, "r") as input:
        nancount = 0
        infcount = 0
        cleaned_file_location = file_location.replace(".txt", "_cleaned.txt")
        with open(cleaned_file_location, "a+") as output:
            iterations = 0
            for line in input:
                if iterations > 0:
                    if "UNREV_BOMBS_R" in line:
                        print("Skipping unwanted header line")
                        continue
                    elif "nan" in line:
                        nancount += 1
                        continue
                    elif "inf" in line: # some unexpected divide by zero errors slipped through
                        infcount += 1   # I no longer have time to regenerate the dataset (takes 20hrs+)
                        continue        # this is a stop-gap solution.
                                        # Eval: 1 header line, 26 nan lines, 0 inf lines
                                        # Test: 1 header line, 43 nan lines, 0 inf lines
                                        # Train: 1 header line, 125 nan lines, 0 inf lines
                output.write(line)
                iterations += 1
        print(nancount)
        print(infcount)


def count_word_occurences_in_file(word: str, file_location: str) -> int:
    """
    counts how often a word occurs in a file. Used to determine if class weights are needed in train_cleaned.txt
    :param word: word to count
    :param file_location: path to file
    :return: number of word occurrences
    """
    word_occurences = EMPTY
    with open(file_location, "r") as target_file:
        for line in target_file:
            if word in line:
                word_occurences += 1
    return word_occurences


def count_original_number_of_game_turns_total(folder_location: str) -> int:
    """
    sum the turns in all raw StraDos logs. Requires a main_dir/sub_dir/log.xml structure.
    :param file_location: path to directory with directories containing xml logs
    :return: total number of turns
    """
    total_turns = 0
    for subdir in os.listdir(folder_location):
        subdir_path = extend_path_with(folder_location, subdir)
        for log_name in os.listdir(subdir_path):
            log_path = extend_path_with(subdir_path, log_name)
            log_xml_root = xml_tree.parse(log_path).getroot()
            game_node = log_xml_root.find("./game")
            turn_nodes = game_node.findall("./move")
            for node in turn_nodes:
                total_turns += 1
    return total_turns


if __name__ == '__main__':
    if __name__ == "__main__":
        # path = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/Cleaned_Stratego_Games"
        # sum_turns = count_original_number_of_game_turns_total(path)
        # print("total turns: " + str(sum_turns))

        # winner_red = "red"
        # ml_file_path = "D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/test_cleaned.txt"
        # print(str(count_word_occurences_in_file("red", ml_file_path)), " ", ml_file_path)
        # print(str(count_word_occurences_in_file("blue", ml_file_path)), " ", ml_file_path)

        clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/eval.txt")
        clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/test.txt")
        clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/train.txt")

