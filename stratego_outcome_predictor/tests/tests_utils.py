import unittest
import sys
sys.path.append("../../")
import utils

class TestUtilsMethods(unittest.TestCase):

    def test_parse_location_encoding_to_row_column(self):
        parsed_location = utils.parse_location_encoding_to_row_column("A4")
        self.assertEqual(parsed_location, [3, 0])
