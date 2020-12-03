from random import shuffle
from random import randint

from euchre.players import Player
from euchre.players import LivePlayer
from euchre.players import Team
from euchre.players import playernames
from euchre import cards
from euchre import interaction


def run(have_real_player, games, ui):

    # realplayer = 0
    # name = ""
    # hands = 0
    currentwinner_num = None
    hand = 0
    game = 0
    leadsuit = -1
    # NOTE: With respect to the function showhand, bidding_round just serves
    # to distinguish between when trump is known (0) and when it isn't (1).
    # bidding_round = 0
    topcard = []

    # Set players
    if have_real_player:
        player0 = LivePlayer("You", 0, ui)
    else:
        player0 = Player(playernames[0], 0, ui)

    players = [
        player0,
        Player(playernames[1], 1, ui),
        Player(playernames[2], 2, ui),
        Player(playernames[3], 3, ui),
    ]

    team1 = Team(1, players)
    team2 = Team(2, players)

    team1.setopposingteam(team2)
    team2.setopposingteam(team1)

    Teams = [team1, team2]

    # Start game.

    if have_real_player:
        ui.display("Your partner is Sue.")

    positions = [0, 1, 2, 3]
    nextdealer_num = randint(0, 3)

    team1score = 0
    team2score = 0
    teamscores = [team1score, team2score]

    while game < games:
        # Dealing
        dealer_num = nextdealer_num
        ui.display("\n\nThe dealer is " + players[dealer_num].name + ".")
        team1.trickcount = 0
        team2.trickcount = 0
        alone = 0
        shuffledcards = cards.card_values[:]
        shuffle(shuffledcards)
        for player in players:
            player.getcards(shuffledcards)
        topcard = shuffledcards[0]
        # topcardbu = topcard[:]
        trump = topcard[0]
        ui.display("The up-card is " + cards.labelcard(topcard[0], topcard[1]))
        for player in players:
            if have_real_player and player == 0:
                player.showhand(trump, 0)
        dealers = positions[dealer_num:] + positions[:dealer_num]
        nextdealer_num = players[dealers[1]].number
        firstbidder_num = players[dealers[1]].number
        bidders = positions[firstbidder_num:] + positions[:firstbidder_num]
        # Bidding
        # bidding_round = 0
        bid = 0
        for bidder_num in bidders:
            # Second parameter is "player position" in bidding order,
            # currently stored when recording live player data. May have other uses.
            bid = players[bidder_num].bid(
                0, bidders.index(bidder_num), Teams, topcard, dealer_num, hand
            )
            bid_type = bid[1]
            if bid_type > 0:
                bidmaker = players[bidder_num]
                players[dealer_num].hand.append(topcard)
                if isinstance(players[dealer_num], LivePlayer):
                    # If the LivePlayer needs to discard, the following is skipped.
                    # LP must be prompted to discard below.
                    pass
                else:
                    handbackup = players[dealer_num].hand[:]
                    discardvalues = []
                    for discard in range(6):
                        players[dealer_num].hand = handbackup[:]
                        del players[dealer_num].hand[discard]
                        discardvalues.append(
                            players[dealer_num].calc_handvalue(
                                trump, 0, dealer_num, topcard, players
                            )
                        )
                    players[dealer_num].hand = handbackup
                    # Discards from dealers hand the card that resulted in highest
                    # hand value when discarded:
                    del players[dealer_num].hand[
                        discardvalues.index(max(discardvalues))
                    ]
            if bid_type == 0:
                ui.display(players[bidder_num].name + " passes.")
                continue
            else:
                if bid_type == 2:
                    alone = 1
                action = " orders "
                if bidder_num == dealer_num:
                    action = " picks "
                ui.display(
                    players[bidder_num].name
                    + action
                    + "up "
                    + cards.labelcard(topcard[0], topcard[1])
                    + (". Going alone" * alone)
                    + "."
                )
                if isinstance(players[dealer_num], LivePlayer):
                    validdiscards = {1, 2, 3, 4, 5, 6}
                    lpdiscard = 999
                    player0.showhand(trump, 0)
                    lpdiscard = ui.question(
                        "Which card do you want to discard? (1 through 6)",
                        datatype=int,
                        options=validdiscards,
                    )

                    del player0.hand[lpdiscard - 1]
            break
        if bid_type == 0:
            # round of bidding in other suits, if bid_type is still 0.
            for bidder_num in bidders:
                players[bidder_num].updatecards_out(topcard)
            for bidder_num in bidders:
                bid = players[bidder_num].bid(
                    1, bidders.index(bidder_num), Teams, topcard, dealer_num, hand
                )
                trump = bid[0]
                bid_type = bid[1]
                if bid_type > 0:
                    bidmaker = players[bidder_num]
                if bid_type == 0:
                    ui.display(players[bidder_num].name + " passes.")
                    continue
                else:
                    if bid_type == 2:
                        alone = 1
                    ui.display(
                        players[bidder_num].name
                        + " bids "
                        + cards.suitlabels[trump]
                        + (" alone" * alone)
                        + "."
                    )
                    break
        if bid_type == 0:
            ui.display("No one bids. Redeal!")
            continue
        else:
            trumplist = [0, 1, 2, 3]
            trumplist = trumplist[trump:] + trumplist[:trump]
            left_bauer = (trumplist[2], 2)
            # Playing
            trickcount = 1
            team1.trickscore = 0
            team2.trickscore = 0
            for player in players:
                player.voids = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            for trick in range(5):
                ui.display("\nTrick " + str(trickcount) + ": ")
                played_cards = []  # Cards played in trick
                played_cards_values = []  # Values of cards played in trick
                if trickcount == 1:
                    leader_num = firstbidder_num
                else:
                    leader_num = currentwinner_num
                tricksequence = players[leader_num:] + players[0:leader_num]
                if bid_type == 2:
                    tricksequence.remove(bidmaker.partner)
                for player in tricksequence:
                    played_card = player.play(
                        leadsuit,
                        trump,
                        tricksequence,
                        bidmaker,
                        players,
                        currentwinner_num,
                        played_cards,
                        played_cards_values,
                    )
                    if player == tricksequence[0]:
                        leadsuit = played_card[0]
                        if played_card == left_bauer:
                            leadsuit = trump
                    ui.display(
                        player.name
                        + " plays "
                        + cards.labelcard(played_card[0], played_card[1])
                        + "."
                    )
                    played_cards.append(played_card)
                    if not (played_card[0]) == leadsuit:
                        # All players update their known voids if the see current
                        # player not following suit.
                        # NOTE: This would be better if it could somehow be assessed at
                        # the end of the trick.
                        # Otherwise, players are playing as if people who have already
                        # played in trick could trump in.
                        for player2 in players:
                            player2.voids[player.number][leadsuit] = 1
                    for player2 in players:
                        if not (player2 == player):
                            # All players update the cards they know are out.
                            player2.updatecards_out(played_card)
                        for suit in range(4):
                            if (
                                len(player2.getsuit(suit, player2.cards_out, trump))
                                == 0
                            ):
                                # If player knows, based on played cards and own hand,
                                # there's a void in a suit, this is registered as a
                                # void for all players, only known to player.
                                for player3 in players:
                                    player3.voids[player2.number][suit] = 1
                    if played_card[0] == leadsuit or played_card == left_bauer:
                        played_cards_values.append(
                            cards.calc_card_point_value(trump, played_card)
                        )
                    elif played_card[0] == trump:
                        played_cards_values.append(
                            cards.calc_card_point_value(trump, played_card)
                        )
                    else:
                        played_cards_values.append(-1)
                    # the current winner number is the number of the player in the
                    # tricksequence whose card value is currently highest among all
                    # played cards:
                    currentwinner_num = tricksequence[
                        played_cards_values.index(max(played_cards_values))
                    ].number
                players[currentwinner_num].team.trickscore += 1
                trickcount += 1
                ui.display("\n" + players[currentwinner_num].name + " wins trick!")
            for team in Teams:
                if team.bid == 0:
                    if team.trickscore > 2:
                        team.score += 2
                        roundwinner = team
                if team.bid == 1:
                    if team.trickscore > 2:
                        team.score += 1
                        roundwinner = team
                    if team.trickscore > 4:
                        team.score += 1
                if team.bid == 2:
                    if team.trickscore > 2:
                        team.score += 1
                        roundwinner = team
                    if team.trickscore > 4:
                        team.score += 3
            # End of round
            ui.display(roundwinner.name + " wins round!")
            ui.display(
                "Team 1 score: "
                + str(team1.score)
                + "; Team 2 score: "
                + str(team2.score)
            )
            ui.display(
                "Team 1 trick count:"
                + str(team1.trickscore)
                + "; Team 2 trick count: "
                + str(team2.trickscore)
            )
            teamscores = [team1.score, team2.score]

            if max(teamscores) > 9:
                ui.display(
                    "Team "
                    + str(teamscores.index(max(teamscores)) + 1)
                    + " wins game "
                    + str(game)
                    + "!"
                )
                Teams[teamscores.index(max(teamscores))].gamescore += 1
                team1.score = 0
                team2.score = 0
                game += 1
                ui.display("END OF GAME " + str(game))
                ui.display(
                    "team1 game wins="
                    + str(team1.gamescore)
                    + " team2 game wins="
                    + str(team2.gamescore)
                )

    ui.display(
        "team1 game wins="
        + str(team1.gamescore)
        + " team2 game wins="
        + str(team2.gamescore)
    )
    return Teams


if __name__ == "__main__":
    games = 0
    realplayer = 0

    # Get input from player.
    ui = interaction.ConsoleUI()

    realplayer = ui.question(
        "Do you want to be a player? (y)es or (n)o: ", options={"y", "n"}
    )
    have_real_player = realplayer == "y"

    while not games:
        games = ui.question(
            "How many games do you want to play?", datatype=int, options=set(range(200))
        )
        if games > 200 and have_real_player:
            games = 0
            ui.display("Too many!")
        if games < 0:
            games = 0

    if not have_real_player:
        ui = interaction.NullUI()
    run(have_real_player, games, ui)
