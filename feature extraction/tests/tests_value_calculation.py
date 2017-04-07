import unittest
import numpy as np
import sys
sys.path.append("../")
import value_calculation as val_calc
sys.path.append("../")
import rank_encodings as ranks


class TestValueCalculationMethods(unittest.TestCase):

    def test_determine_rank_values(self):
        """
        check if the value increase is handled as specified in
        https://docs.google.com/document/d/1y5r3RjrUmZHCWHUhiDFR3ucPpkvWhM-OtXFFv2_0psI/edit?usp=sharing
        """
        correct_output = [5, 7.25, 7.25, 15.243125, 15.243125, 15.243125, 46.47057195312499, 67.38232933203123,
                          97.70437753144529, 97.70437753144529]
        red_rank_amounts = {"B": 0, "C": 1, "D": 1, "E": 0, "F": 4, "G": 5, "H": 6, "I": 7, "J": 2, "K": 1, "L": 1, "M": 1}
        blue_rank_amounts = {"N": 0, "O": 1, "P": 1, "Q": 3, "R": 0, "S": 0, "T": 0, "U": 1, "V": 4, "W": 0, "X": 0, "Y": 1}
        assigned_base_values = val_calc.determine_rank_values(red_rank_amounts, blue_rank_amounts)
        self.assertEqual(assigned_base_values, correct_output)

    def test_get_amount_of_pieces_per_rank(self):
        """
        test if the function correctly splits pieces on the board between players by providing a sample board with a
        single empty space
        """
        sample_board_state = [["F", "C", "F"],
                              ["O", "A", "X"]]
        red_pieces, blue_pieces = val_calc.get_amount_of_pieces_per_rank(sample_board_state)
        self.assertTrue(sum(red_pieces.values()) == 3.0)
        self.assertTrue(sum(blue_pieces.values()) == 2.0)
        self.assertTrue(red_pieces["F"] == 2.0)

    def test_determine_player_amount_of_moving_pieces(self):
        """
        test if the amount of movable pieces is correctly determined by providing a sample of red pieces;
        5 bombs, 2 spies, 1 flag and 0 sergeants
        """
        red_player = 0
        player_pieces = {"B": 5, "C": 2, "M": 1, "F": 0}
        moving_pieces = val_calc.determine_player_amount_of_moving_pieces(red_player, player_pieces)
        self.assertEqual(moving_pieces, 2)

    def test_determine_n_highest_values_in_grid(self):
        """
        test if the method correctly returns the n highest values from an ndarray
        """
        grid = np.array([[5.0, 1.0, 0.0],
                         [0.0, 9.0, 2.0],
                         [3.0, 7.0, 2.0]])
        n = 3
        found_values = val_calc.determine_n_highest_values_in_grid(n, grid)
        self.assertEqual(found_values, [9.0, 7.0, 5.0])

    def test_get_exceptional_piece_type_value_modifier(self):
        """
        test if the function returns the correct modifier by providing one case (the other 3 cases are identical)
        """
        check_marshal_modifier_rank = ranks.R_10
        check_marshal_modifier_opposing_pieces = {ranks.B_1: 1}
        check_marshal_modifier_result = val_calc.get_exceptional_piece_type_value_modifier(check_marshal_modifier_rank,
                                                           check_marshal_modifier_opposing_pieces)
        self.assertEqual(check_marshal_modifier_result, 0.8)

        check_no_modifier_rank = ranks.R_10
        check_no_modifier_opposing_pieces = {ranks.B_1: 0}
        check_no_modifier_result = val_calc.get_exceptional_piece_type_value_modifier(check_no_modifier_rank,
                                                            check_no_modifier_opposing_pieces)
        self.assertEqual(check_no_modifier_result, 1.0)

    def test_handle_spy_values(self):
        """
        check if spy values are assigned correctly. Blue's spy should be valued at 50% of red's marshal (70), red's spy
        should retain its base value of 5. Only 1 spy and 1 marshal per side, so no testing for multiples.
        """
        exceptional_valued_movable_pieces = {
            ranks.B_1: [[0, 0]],
            ranks.R_10: [[0, 2]],
            ranks.R_1: [[1, 0]]
        }
        red_spy = ranks.R_1
        blue_spy = ranks.B_1
        red_marshal = ranks.R_10
        blue_marshal = ranks.B_10

        red_piece_values = np.array([[0.0, 0.0, 140.0],
                                     [5.0, 0.0, 0.0]])
        blue_piece_values = np.array([[5.0, 0.0, 0.0],
                                      [0.0, 0.0, 0.0]])
        val_calc.handle_spy_values(exceptional_valued_movable_pieces, red_spy, blue_marshal, red_piece_values,
                                   blue_piece_values)
        self.assertTrue(red_piece_values[1, 0] == 5) # red's spy is still values at 5
        val_calc.handle_spy_values(exceptional_valued_movable_pieces, blue_spy, red_marshal, blue_piece_values,
                                   red_piece_values)
        self.assertTrue(blue_piece_values[0, 0] == 70) # blue's spy is valued at 70

    def test_handle_scout_values(self):
        """
        check if scout value is multiplied by 2.43 if the opponent has more than 1 moving unrevealed piece
        """
        exceptional_valued_movable_pieces = { # locations of exceptional movable pieces (scouts)
            ranks.B_2: [[0, 0]], # blue scout
            ranks.R_2: [[1, 0], [1, 2]], # red scouts
            ranks.R_1: [[1, 1]]
        }
        red_scout = ranks.R_2
        blue_unrevealed_pieces = {"P": 1, "Q": 2, "X": 1}   # amount unrevealed of each type
        red_piece_values = np.array([[0.0, 0.0, 0.0],             # board representation with value per tile for red
                                    [7.3, 15, 7.3]])        # 7.3 is the base value of a scout
        val_calc.handle_scout_values(exceptional_valued_movable_pieces, red_scout, blue_unrevealed_pieces,
                                     red_piece_values)

        desired_red_scout_value = 17.739
        self.assertEqual(red_piece_values[1, 0], desired_red_scout_value)
        self.assertEqual(red_piece_values[1, 2], desired_red_scout_value)

    def test_handle_bomb_values(self):
        """
        check if bomb values are correctly set to 50% of the highest opposing piece's value
        """
        red_bombs = [[0, 0],
                     [1, 0]]
        red_piece_values = np.array([[0],
                                     [0]])
        blue_piece_values = np.array([[5],
                                      [20]])
        val_calc.handle_bomb_values(red_bombs, blue_piece_values, red_piece_values)

        self.assertTrue(red_piece_values[0, 0] == 10)
        self.assertTrue(red_piece_values[1, 0] == 10)
