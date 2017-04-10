import numpy as np
import hug
from game_state_tracking import GameStateTracker


game_state = GameStateTracker()



def calculate_features(piece_positions: np.ndarray, unmoved_pieces: np.ndarray, unrevealed_pieces: np.ndarray, \
                       source: str, target: str):
    game_state.update_game_state(piece_positions, unmoved_pieces, unrevealed_pieces, source, target)
    #game_state.calculate_features()

    print(game_state.current_turn)
    print(unmoved_pieces)


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