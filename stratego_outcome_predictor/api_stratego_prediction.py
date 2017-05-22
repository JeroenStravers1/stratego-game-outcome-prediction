import numpy as np
import json
import os
from StringIO import StringIO
from flask import Flask
from flask import g
from flask import render_template
from flask import request
import flask_sijax
from game_state_tracking import GameStateTracker
from datapoint_feature_containment import DataPointFeatureContainer
from outcome_prediction import StrategoClassifier
from html_output_generation import HTML_Generator


SOURCE = 'source'
TARGET = 'target'
RANKS_POSITIONS = 'piece_positions'
RANKS_UNMOVED = 'unmoved_pieces'
RANKS_UNREVEALED = 'unrevealed_pieces'
INDEX_POSITIONS = 0
INDEX_UNMOVED = 1
INDEX_UNREVEALED = 2
INDEX_SOURCE = 3
INDEX_TARGET = 4

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app = Flask('stratego_outcome_predictor')
app = Flask(__name__.split('.')[0])
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
#app.debug = False
flask_sijax.Sijax(app)

game_state = GameStateTracker()
stratego_classifier = StrategoClassifier()
html_generator = HTML_Generator()

current_dashboard_html = "Just give me a few seconds please"


def init_first_turn(piece_positions, unmoved_pieces, unrevealed_pieces):
    game_state.init_game_board(piece_positions, unmoved_pieces, unrevealed_pieces)
    html_generator.init_game(piece_positions)


def calculate_features(piece_positions, unmoved_pieces, unrevealed_pieces, source, target):
    """
    :param piece_positions: a grid representation of the ranks of all pieces
    :param unmoved_pieces: a grid representation of the ranks of all unmoved pieces
    :param unrevealed_pieces: a grid representation of the ranks of all unrevealed pieces
    :param source: the tile the move action originates from
    :param target: the tile the player tries to move to
    :return: feature container object
    """
    current_turn_extracted_features = game_state.update_game_state(piece_positions, unmoved_pieces, unrevealed_pieces,
                                                                   source, target)
    return current_turn_extracted_features


def get_prediction(piece_positions, unmoved_pieces, unrevealed_pieces, source, target):
    """run a trained logreg classifier to predict the chances of red and blue winning. extract required features beforehand, and standardize them.""" 
    feature_container = calculate_features(piece_positions, unmoved_pieces, unrevealed_pieces, source, target)
    result = stratego_classifier.predict_outcome_from_features(feature_container)
    html_generator.process_update(result, feature_container.extracted_features, piece_positions)
    print result


def check_for_source_and_target_in_raw_payload(raw_payload, parsed_payload):
    """get source and target vals, remove pesky escaped quotes"""
    source = raw_payload[SOURCE].replace('"', '')
    target = raw_payload[TARGET].replace('"', '')
    if source != "":
        parsed_payload.append(source)
        parsed_payload.append(target)
    else:
        print "no source/target in payload"


def parse_json_post(request):
    """parse a json post into ndarrays for board state representations and strings for source and target"""
    print request.headers
    print 00000000000000000000000
    print request.__dict__
    raw_payload = ""
    try:
        raw_payload = request.get_json(force=True)
    except Exception as err_one:
        print 1
        print err_one
    print raw_payload
    print type(raw_payload)
    print "________AAAAAAA______________"
    print raw_payload['unrevealed_pieces']
        
    list_positions = ""
    list_unmoved = ""
    list_unrevealed = ""
    try:
        list_positions = raw_payload[RANKS_POSITIONS]
        list_unmoved = raw_payload[RANKS_UNMOVED]
        list_unrevealed = raw_payload[RANKS_UNREVEALED]
    except Exception as err_two:
        print 2
        print err_two
    ndarray_positions = np.array(list_positions)
    ndarray_unmoved = np.array(list_unmoved)
    ndarray_unrevealed = np.array(list_unrevealed)
    parsed_payload = [ndarray_positions, ndarray_unmoved, ndarray_unrevealed]
    check_for_source_and_target_in_raw_payload(raw_payload, parsed_payload)
    return parsed_payload


@app.route("/new_game", methods=["POST"])
def init_new_game():
    print "hierzo"
    print request.data
    print "einde"
    print type(request.data)
    #print request.data[0]
    parsed_payload = parse_json_post(request)
    print request
    print "_____________________________"
    print parsed_payload
    init_first_turn(parsed_payload[INDEX_POSITIONS], parsed_payload[INDEX_UNMOVED], parsed_payload[INDEX_UNREVEALED])
    return "starting new game"
    #return "new game"


@app.route("/update", methods=["POST"])
def goodbye():
    parsed_payload = parse_json_post(request)
    get_prediction(parsed_payload[INDEX_POSITIONS], parsed_payload[INDEX_UNMOVED], parsed_payload[INDEX_UNREVEALED], parsed_payload[INDEX_SOURCE], parsed_payload[INDEX_TARGET])
    return "update"


NSR = 0


def get_request_number():
    global NSR
    #global game_state
    #return game_state.board_state[0][0]
    NSR += 1
    return NSR


def get_html():
    global html_generator
    #global game_state
    #return game_state.board_state[0][0]
    return html_generator.html_output


def get_view_content(obj_response):
    """handles the response to a Sijax request"""
    response = get_html()
    obj_response.html('#main_div', response) #'<p>HALLOOOOOO</p>' + str(reqs))


@flask_sijax.route(app, "/view")
def display_game():
    # sijax response function was initially defined here
    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.register_callback('get_view_content', get_view_content)
        return g.sijax.process_request()
    # Regular (non-Sijax request) - render the page template
    return render_template('view.html')


@app.route("/")
def pulse():
    return "IT'S ALIIIIIIIIIIVE!!!!"


if __name__ == "__main__":
    app.run()

