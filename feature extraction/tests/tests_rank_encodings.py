import unittest
import sys
sys.path.append("../../")
import rank_encodings as ranks


class TestRankEncodingMethods(unittest.TestCase):

    def test_transform_piece_rank_to_comparable_value(self):
        marshal_red  = ranks.transform_piece_rank_to_comparable_value("L")
        marshal_blue = ranks.transform_piece_rank_to_comparable_value("X")
        self.assertEqual(marshal_red, marshal_blue)

    def test_compare_source_to_target_rank(self):
        source, target, result = ranks.compare_source_to_target_rank("L", "X")
        self.assertEqual(source, ranks.EMPTY_TILE)
        self.assertEqual(target, ranks.EMPTY_TILE)
        self.assertEqual(result, ranks.MOVE_DRAW)
        source, target, result = ranks.compare_source_to_target_rank("D", "X")
        self.assertEqual(source, ranks.EMPTY_TILE)
        self.assertEqual(target, "X")
        self.assertEqual(result, ranks.MOVE_LOSE)