card_values = [(x, y) for x in range(4) for y in range(6)]
# Having same-color suits two apart enables actions recognizing their
# complementary relationship in Euchre.
suitlabels = [
    "Hearts",
    "Spades",
    "Diamonds",
    "Clubs",
]
positionlabels = ["9", "10", "Jack", "Queen", "King", "Ace"]


def labelcard(suit, position):
    "Labels cards in a way comprehensible to user."
    return str("the " + positionlabels[position] + " of " + suitlabels[suit])


def calc_card_point_value(trump_local, card_local):
    value = card_local[1]
    if card_local[0] == trump_local:
        if card_local[1] == 2:
            value += 16
        else:
            value += 6
    if abs(card_local[0] - trump_local) == 2 and card_local[1] == 2:
        value += 13  # Sets value of left bauer.
    return value
