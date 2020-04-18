from euchre import Euchre15
from euchre import ui


def test_end_to_end():
    num_games = 2
    ui_ = ui.ConsoleUI()
    result = Euchre15.run(have_real_player=False, games=num_games, ui=ui_)
    scores = [result[0].gamescore, result[1].gamescore]
    assert scores[0] + scores[1] == num_games


def test_end_to_end_with_fake_real_player():
    num_games = 20
    ui_ = ui.FakeUI()
    result = Euchre15.run(have_real_player=True, games=num_games, ui=ui_)
    scores = [result[0].gamescore, result[1].gamescore]
    assert scores[0] + scores[1] == num_games
