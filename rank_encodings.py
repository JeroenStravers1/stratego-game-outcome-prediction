# ranks and base values
RED_PIECES = {"B": 0, "C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11}
BLUE_PIECES = {"N": 0, "O": 1, "P": 2, "Q": 3, "R": 4, "S": 5, "T": 6, "U": 7, "V": 8, "W": 9, "X": 10, "Y": 11}
ALL_PIECES = {"B": 0, "C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11,
              "N": 0, "O": 1, "P": 2, "Q": 3, "R": 4, "S": 5, "T": 6, "U": 7, "V": 8, "W": 9, "X": 10, "Y": 11}


PLAYER_RED = 0
PLAYER_BLUE = 1

BASE_VALUE = 5
RED_PIECES_LIST = ("B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M")
BLUE_PIECES_LIST = ("N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y")

RED_MOVABLE_PIECES = ("C", "D", "E", "F", "G", "H", "I", "J", "K", "L")
BLUE_MOVABLE_PIECES = ("O", "P", "Q", "R", "S", "T", "U", "V", "W", "X")

EMPTY_VALUE = 0

# special value indices
BOMB = 0
SPY = 1
SCOUT = 2
MINER = 3
MARSHAL = 10

# board codes
EMPTY = "A"
WATER = "_"

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
