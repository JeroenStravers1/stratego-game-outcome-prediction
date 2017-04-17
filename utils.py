import os
import string
import game_board_descriptors as board


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


def clear_additional_header_lines_from_file(file_location):
    with open(file_location, "r") as input:
        cleaned_file_location = file_location.replace(".txt", "_cleaned.txt")
        with open(cleaned_file_location, "a+") as output:
            iterations = 0
            for line in input:
                if iterations > 0:
                    if "UNREV_BOMBS_R" in line:
                        print("Skipping unwanted header line")
                        continue
                output.write(line)
                iterations += 1


if __name__ == "__main__":
    clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/eval.txt")
    clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/test.txt")
    clear_additional_header_lines_from_file("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/train.txt")
