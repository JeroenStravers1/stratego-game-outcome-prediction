import os


LAST_ITEM_IN_LIST = -1
FORWARD_SLASH = "/"


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