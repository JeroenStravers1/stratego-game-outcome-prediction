import numpy as np
import hug
from game_state_tracking import GameStateTracker
from datapoint_feature_containment import DataPointFeatureContainer


game_state = GameStateTracker()

# FIXME Needs game over recognition!!!!


def init_first_turn(piece_positions: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray) -> None:
    # FIXME needs player satsarting positions
    RED_START_BOTTOM = 1
    game_state.init_game_board(piece_positions, unmoved_pieces, unrevealed_pieces)


def calculate_features(piece_positions: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray,
                       source: str, target: str) -> DataPointFeatureContainer:
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


def get_prediction(piece_positions: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray, source: str,
                   target: str):
    """ return type is still unclear"""

    calculate_features(piece_positions, unmoved_pieces, unrevealed_pieces, source, target)


def process_outcome_for_display():
    """either change variables being displayed or POST outcome variables to a webservice/site/view"""
    pass


@hug.cli()
@hug.get()
@hug.local()
def predict_outcome_from_input():
    # get_prediction()
    # process_outcome_for_display()
    # FIXME hier zit de interpretatie van JSON naar normaal leesbaar formaat.
    return {game_state}