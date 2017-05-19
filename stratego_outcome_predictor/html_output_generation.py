import value_calculation as val_calc
import rank_encodings as ranks
import numpy as np


class HTML_Generator:

    COLOR_RED = "#FD3C26"
    COLOR_BLUE = "#1EC7F7"
    COLOR_BOTH = "#8E828F"
    COLOR_EMPTY = "#FEFCE0"
    COLOR_WATER = "#033A49"
    COLOR_BORDER_TILES = "#FEC481"
    COLOR_INVISIBLE = "#FFFFFF"

    BOARD_TILES_TOTAL = 100
    BOARD_ROWS = 10
    BOARD_COLUMNS = 10
    MAX_ROW_INDEX = 9

    PREDICTIONS = 0
    P_BLUE = 0
    P_RED = 1

    FEATURE_TURN = 33
    FEATURE_UNREVEALED_BOMBS_RED = 0
    FEATURE_UNREVEALED_BOMBS_BLUE = 1
    FEATURE_PIECES_RED = 18
    FEATURE_PIECES_BLUE = 19

    # sterkste stuk
    FEATURE_STRONGEST_PIECE = 12 # check ff de waarde berekening, 1 is gelijk verdeeld. >1 is rood is sterker.
    # 3 besten
    FEATURE_THREE_BEST = 28 # zie hierboven

    #sterkste leger
    FEATURE_ARMY_RED = 22  #
    FEATURE_ARMY_BLUE = 23  #
 
    #agressor
    FEATURE_AGGRESSION_RED = 40   #
    FEATURE_AGGRESSION_BLUE = 41  #

    #keurtroepen = 22/18 vs 23/19

    vertical_indices = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    horizontal_indices = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", ""]

    def __init__(self):
        self.board_html = ""
        self.left_data_column = ""
        self.right_data_column = ""
        self.html_output = ""

    def process_update(self, predictor_output, feature_dict, board_state):
        self.draw_board_representation(board_state)
        left_results_column_html = "<div class='left'>"
        right_results_column_html = "<div class='left'>"
        left_results_column_html, right_results_column_html = self.draw_prediction(predictor_output, left_results_column_html, right_results_column_html)
        left_results_column_html, right_results_column_html = self.draw_game_features(feature_dict, left_results_column_html, right_results_column_html)
        #print left_results_column_html
        #quit()
        left_results_column_html += "</div>"
        right_results_column_html += "</div>"
        self.left_data_column = left_results_column_html
        self.right_data_column = right_results_column_html

    def draw_board_representation(self, board_state):
        new_board_html = "<div class='left'><table bgcolor='#FEFCE0'>"
        for row_index in range(0, self.BOARD_ROWS):
            top_row_index = self.invert_index(row_index, self.MAX_ROW_INDEX)
            top_row = board_state[top_row_index]
            new_board_html += self.convert_board_row_tile_values_to_html_color_cells(top_row, row_index)
        new_board_html += self.draw_horizontal_indices()
        new_board_html += "</table></div>"
        self.board_html = new_board_html
                      
    def invert_index(self, index_value, index_upper_limit):
        """reverse an index. [0-9] with value 4: 9 - 4 = 5"""
        return index_upper_limit - index_value

    def convert_board_row_tile_values_to_html_color_cells(self, row, row_number):
        row_html = "<tr>"
        for tile_value in row:
            cell_html = "<td bgcolor='"
            cell_color = self.convert_tile_to_color(tile_value)
            cell_html += cell_color
            cell_html += "'></td>"
            row_html += cell_html
        border_cell_html = "<td bgcolor='"
        border_cell_html += self.COLOR_BORDER_TILES
        border_cell_html += "'>" + str(self.vertical_indices[row_number]) + "</td>"
        row_html += border_cell_html
        row_html += "</tr>"
        return row_html

    def convert_tile_to_color(self, tile_value):
        cell_color = ""
        piece_color = val_calc.determine_piece_color(tile_value)
        if piece_color != None:
            if piece_color == ranks.PLAYER_RED:
                cell_color = self.COLOR_RED 
            else:
                cell_color = self.COLOR_BLUE
        else:
            if tile_value == ranks.EMPTY_TILE:
                cell_color = self.COLOR_EMPTY
            else:
                cell_color = self.COLOR_WATER
        return cell_color

    def draw_horizontal_indices(self):
        """draw the bottom index line 'a', 'b', 'c' etc"""
        row_html = "<tr>"
        for item in self.horizontal_indices:
            border_cell_html = "<td bgcolor='"
            border_cell_html += self.COLOR_BORDER_TILES
            border_cell_html += "'>" + item + "</td>"
            row_html += border_cell_html
        row_html += "</tr>"
        return row_html

    def draw_prediction(self, predictor_output, left_results_column_html, right_results_column_html):
        winner_chance, loser_chance, winner_color, loser_color = self.get_winner_and_loser_p_and_color(predictor_output)
        left_results_column_html += "<div style='width:160px;height:160px;margin-left:80px;background-color:" + winner_color + ";border:1px solid #000;'>" + winner_chance + "</div>"
        right_results_column_html += "<div style='width:80px;height:80px;margin-left:80px;margin-top:80px;background-color:" + loser_color + ";border:1px solid #000;'>" + loser_chance + "</div>"
        return left_results_column_html, right_results_column_html
        
    def get_winner_and_loser_p_and_color(self, predictor_output):
        predictions = predictor_output[self.PREDICTIONS]
        p_blue = predictions[self.P_BLUE]
        p_red = predictions[self.P_RED]
        winner_chance = p_blue
        loser_chance = p_red
        winner_color = self.COLOR_BLUE
        loser_color = self.COLOR_RED
        if p_red > p_blue:
            winner_chance = p_red
            loser_chance = p_blue
            winner_color = self.COLOR_RED
            loser_color = self.COLOR_BLUE
        winner_chance = format(winner_chance, '.2f')
        loser_chance = format(loser_chance, '.2f')
        return winner_chance, loser_chance, winner_color, loser_color
        
    def draw_game_features(self, feature_dict, left_results_column_html, right_results_column_html):
        left_col_feature_divs = self.get_left_column_feature_divs(feature_dict)
        right_col_feature_divs = self.get_right_column_feature_divs(feature_dict)
        left_results_column_html += left_col_feature_divs
        right_results_column_html += right_col_feature_divs
        return left_results_column_html, right_results_column_html

    def get_left_column_feature_divs(self, feature_dict):
        #"<div style='width:160px;height:160px;margin-left:80px;background-color:" + winner_color + ";border:1px solid #000;'>" + str(winner_chance) + "</div>"
        current_turn = feature_dict[self.FEATURE_TURN]
        unrevealed_bombs_red = feature_dict[self.FEATURE_UNREVEALED_BOMBS_RED]
        unrevealed_bombs_blue = feature_dict[self.FEATURE_UNREVEALED_BOMBS_BLUE]
        pieces_red = feature_dict[self.FEATURE_PIECES_RED]
        pieces_blue = feature_dict[self.FEATURE_PIECES_BLUE]
        features_left_divs = self.convert_to_left_column_div("Beurt: ", current_turn)
        features_left_divs += self.convert_to_left_column_div("Ononthulde bommen rood: ", unrevealed_bombs_red)
        features_left_divs += self.convert_to_left_column_div("Ononthulde bommen blauw:  ", unrevealed_bombs_blue)
        features_left_divs += self.convert_to_left_column_div("Stukken rood:  ", pieces_red)
        features_left_divs += self.convert_to_left_column_div("Stukken blauw:  ", pieces_blue)
        return features_left_divs

    #def convert_to_left_column_div(self, feature, value):
    #    element = "<div style='margin-top:20px;height:40px;'>"
    #    element += feature + str(value)
    #    element += "</div>"
    #    return element

    def convert_to_left_column_div(self, feature, value):
        element = "<div style='margin-top:20px'><p style='float:right;'>" + feature + str(value) + "</p>"
        element += "<div style='float:left;width:30px;height:30px;background-color:" + self.COLOR_INVISIBLE + "'></div></div>"
        return element

    def get_right_column_feature_divs(self, feature_dict):
        highest_value_piece, three_strongest, strongest_army, agressor, elite = self.get_right_column_feature_winners(feature_dict)
        #right_divs = self.convert_to_right_column_div("", value)
        features_right_divs = self.convert_to_right_column_div("Sterkste stuk: ", highest_value_piece)
        features_right_divs += self.convert_to_right_column_div("Drie sterksten: ", three_strongest)
        features_right_divs += self.convert_to_right_column_div("Sterkste leger: ", strongest_army)                
        features_right_divs += self.convert_to_right_column_div("Agressor: ", agressor)
        features_right_divs += self.convert_to_right_column_div("Keurtroepen: ", elite)
        return features_right_divs

    def get_right_column_feature_winners(self, feature_dict):
        """get the color of the player holding each of these categories"""
        highest_value_piece = self.COLOR_BOTH
        if feature_dict[self.FEATURE_STRONGEST_PIECE] > 1:
            highest_value_piece = self.COLOR_RED
        if feature_dict[self.FEATURE_STRONGEST_PIECE] < 1:
            highest_value_piece = self.COLOR_BLUE

        three_strongest = self.COLOR_BOTH
        if feature_dict[self.FEATURE_THREE_BEST] > 1:
            three_strongest = self.COLOR_RED
        if feature_dict[self.FEATURE_THREE_BEST] < 1:
            three_strongest = self.COLOR_BLUE

        strongest_army = self.COLOR_BOTH
        if feature_dict[self.FEATURE_ARMY_RED] > feature_dict[self.FEATURE_ARMY_BLUE]: 
            strongest_army = self.COLOR_RED
        if feature_dict[self.FEATURE_ARMY_RED] < feature_dict[self.FEATURE_ARMY_BLUE]: 
            strongest_army = self.COLOR_BLUE

        agressor = self.COLOR_BOTH
        if feature_dict[self.FEATURE_AGGRESSION_RED] > feature_dict[self.FEATURE_AGGRESSION_BLUE]:
            agressor = self.COLOR_RED
        if feature_dict[self.FEATURE_AGGRESSION_RED] < feature_dict[self.FEATURE_AGGRESSION_BLUE]:
            agressor = self.COLOR_BLUE

        elites_red = feature_dict[self.FEATURE_ARMY_RED] / feature_dict[self.FEATURE_PIECES_RED]
        elites_blue = feature_dict[self.FEATURE_ARMY_BLUE] / feature_dict[self.FEATURE_PIECES_BLUE]
        elite = self.COLOR_BOTH 
        if elites_red > elites_blue:
            elite = self.COLOR_RED
        if elites_red < elites_blue:
            elite = self.COLOR_BLUE
        return highest_value_piece, three_strongest, strongest_army, agressor, elite

    def convert_to_right_column_div(self, feature, color):
        element = "<div style='margin-top:20px'><p style='float:left;'>" + feature + "</p>"
        element += "<div style='float:right;width:30px;height:30px;background-color:" + color + "'></div>"
        return element



if __name__ == "__main__":
    test = HTML_Generator()
    predictor_output = [[0.54, 0.46]]
    feature_dict = {33:15, 0:6, 1:5, 18:40, 19:40, 12:1, 28:1.2, 22:1, 23:0.8, 40:15, 41:16}
    board_state = np.array([["E","E","B","M","B","E","F","B","D","E"],["B","G","I","B","H","G","B","I","D","E"],["G","J","D","F","D","H","C","D","J","G"],["A","H","D","L","I","F","K","F","D","H"],["D","A","_","_","A","A","_","_","A","A"],["A","A","_","_","P","A","_","_","A","A"],["R","N","T","O","A","T","W","N","P","S"],["P","N","V","P","V","P","S","P","U","X"],["N","Q","T","Q","Q","P","Y","R","N","N"],["R","Q","U","P","T","S","Q","S","U","R"]])
    test.process_update(predictor_output, feature_dict, board_state)
    print test.board_html
    print test.left_data_column
    print test.right_data_column



    FEATURE_TURN = 33
    FEATURE_UNREVEALED_BOMBS_RED = 0
    FEATURE_UNREVEALED_BOMBS_BLUE = 1
    FEATURE_PIECES_RED = 18
    FEATURE_PIECES_BLUE = 19

    # sterkste stuk
    FEATURE_STRONGEST_PIECE = 12 # check ff de waarde berekening, 1 is gelijk verdeeld. >1 is rood is sterker.
    # 3 besten
    FEATURE_THREE_BEST = 28 # zie hierboven

    #sterkste leger
    FEATURE_ARMY_RED = 22  #
    FEATURE_ARMY_BLUE = 23  #
 
    #agressor
    FEATURE_AGGRESSION_RED = 40   #
    FEATURE_AGGRESSION_BLUE = 41  #


        
