#from sklearn.linear_model import SGDClassifier


FEATURES_AMOUNT = 78
CLASS_LABEL_INDEX = 78
ORIGIN_LOG_NAME_INDEX = 79


def parse_file_to_features_and_classes_lists(path_to_file: str, header: bool) -> [list, list]:
    labels = list()
    features = list()
    with open(path_to_file, "r") as data_file:
        for line in data_file:
            line_features = list()
            if header:
                header = False
                continue
            current_line_elements = line.split(",")
            for feature in range(FEATURES_AMOUNT):
                line_features.append(current_line_elements[feature])
            features.append(line_features)
            labels.append(current_line_elements[CLASS_LABEL_INDEX])
