import hug
from game_state_tracking import GameStateTracker


game_state = GameStateTracker()


@hug.cli()
@hug.get()
@hug.local()
def predict_outcome_from_input():
    # get_prediction()
    # process_outcome_for_display()
    return {game_state}


def get_prediction(piece_positions: list, unmoved_pieces: list, unrevealed_pieces: list):
    """ return type is still unclear"""
    calculate_features(piece_positions, unmoved_pieces, unrevealed_pieces)


def calculate_features(piece_positions: list, unmoved_pieces: list, unrevealed_pieces: list):
    game_state.update_game_state(piece_positions, unmoved_pieces, unrevealed_pieces)
    #game_state.calculate_features()

    print(game_state.current_turn)
    print(unmoved_pieces)

def process_outcome_for_display():
    """either change variables being displayed or POST outcome variables to a webservice/site/view"""
    pass
