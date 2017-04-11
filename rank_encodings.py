import string

# ranks and base values
RED_PIECES = {"B": 0, "C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11}
BLUE_PIECES = {"N": 0, "O": 1, "P": 2, "Q": 3, "R": 4, "S": 5, "T": 6, "U": 7, "V": 8, "W": 9, "X": 10, "Y": 11}
ALL_PIECES = {"B": 0, "C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11,
              "N": 0, "O": 1, "P": 2, "Q": 3, "R": 4, "S": 5, "T": 6, "U": 7, "V": 8, "W": 9, "X": 10, "Y": 11}


PLAYER_RED = 0
PLAYER_BLUE = 1

BASE_VALUE = 5
RED_PIECES_LIST = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
BLUE_PIECES_LIST = ["N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"]

RED_MOVABLE_PIECES = ["C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
BLUE_MOVABLE_PIECES = ["O", "P", "Q", "R", "S", "T", "U", "V", "W", "X"]

RED_EXCEPTIONAL_VALUE_MOVABLE_PIECES = ["C", "D", "E", "L"]
BLUE_EXCEPTIONAL_VALUE_MOVABLE_PIECES = ["O", "P", "Q", "X"]

ALL_STATIC_PIECES = ["B", "M", "N", "Y"]

EMPTY_VALUE = 0

# special value indices
BOMB = 0
SPY = 1
SCOUT = 2
MINER = 3
MARSHAL = 10

# board codes
EMPTY_TILE = "A"
WATER = "_"

NO_PIECES = [EMPTY_TILE, WATER]

# RED
R_B = "B"   # bomb
R_1 = "C"   # spy
R_2 = "D"   # scout
R_3 = "E"   # miner
R_4 = "F"   # sergeant
R_5 = "G"   # lieutenant
R_6 = "H"   # captain
R_7 = "I"   # major
R_8 = "J"   # colonel
R_9 = "K"   # general
R_10 = "L"  # field marshal
R_F = "M"   # flag

# BLUE
B_B = "N"   # bomb
B_1 = "O"   # spy
B_2 = "P"   # scout
B_3 = "Q"   # miner
B_4 = "R"   # sergeant
B_5 = "S"   # lieutenant
B_6 = "T"   # captain
B_7 = "U"   # major
B_8 = "V"   # colonel
B_9 = "W"   # general
B_10 = "X"  # field marshal
B_F = "Y"   # flag


HIGHEST_RANK = 12
MOVE_WIN = 0
MOVE_DRAW = 1
MOVE_LOSE = 2
MOVE_EMPTY = 3

REMOVE_EMPTY_AND_WATER = 2


def transform_piece_rank_to_comparable_value(piece_rank: str) -> int:  # comment updated
    """
    Movable piece rank values are given as c:l and o:x. This function transforms them to values of 2:11
    :param piece_rank: Char rank of the piece (see ranks_encodings.py)
    :return: the converted int height of the piece
    """
    rank_height = string.ascii_lowercase.index(piece_rank.lower())
    rank_height -= REMOVE_EMPTY_AND_WATER
    if rank_height > HIGHEST_RANK:
        rank_height -= HIGHEST_RANK
    return rank_height


def compare_source_to_target_rank(source: str, target: str) -> [str, str]:  # comment updated
    """
    determine the outcome of the player's move
    :param source: the moving piece
    :param target: the target piece
    :return: the pieces that occupy the source tile and the target tile after the move and the move result
    """
    source_rank = transform_piece_rank_to_comparable_value(source)
    target_rank = transform_piece_rank_to_comparable_value(target)
    if source_rank > target_rank:
        return EMPTY_TILE, source, MOVE_WIN
    elif source_rank < target_rank:
        return EMPTY_TILE, target, MOVE_LOSE
    return EMPTY_TILE, EMPTY_TILE, MOVE_DRAW


def determine_move_to_result(source: str, target: str) -> [str, str, int]:  # comment updated
    """
    determine the result of the player's move from the source to the target tile
    :param source: the piece rank in the source tile
    :param target: the piece rank in the target tile (if any)
    :return: the updated ranks in the source and target tiles with the result
    """
    if target == EMPTY_TILE:
        return EMPTY_TILE, source, MOVE_EMPTY
    elif target in [B_F, R_F]:
        return EMPTY_TILE, source, MOVE_WIN
    elif source in [B_3, R_3] and target in [B_B, R_B]:
        return EMPTY_TILE, source, MOVE_WIN
    elif target in [B_B, R_B]:
        return EMPTY_TILE, target, MOVE_LOSE
    elif source in [B_1, R_1] and target in [B_10, R_10]:
        return EMPTY_TILE, source, MOVE_WIN
    else:
        return compare_source_to_target_rank(source, target)



