from euchre import Euchre15


def test_end_to_end():
    result = Euchre15.run()
    scores = [result[0].gamescore, result[1].gamescore]
    assert scores[0] + scores[1] == 1
