from random import shuffle
from random import randint

from euchre.players import Player
from euchre.players import LivePlayer
from euchre.players import Team
from euchre.players import playernames
from euchre import cards
from euchre.interaction import ConsoleUI


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
        Player0 = LivePlayer("You", 0, ui)
    else:
        Player0 = Player(playernames[0], 0, ui)

    Player1 = Player(playernames[1], 1, ui)
    Player2 = Player(playernames[2], 2, ui)
    Player3 = Player(playernames[3], 3, ui)
    Players = [Player0, Player1, Player2, Player3]

    Team1 = Team(1, Players)
    Team2 = Team(2, Players)

    Team1.setopposingteam(Team2)
    Team2.setopposingteam(Team1)

    Teams = [Team1, Team2]

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
        if have_real_player:
            ui.display("\n\nThe dealer is " + Players[dealer_num].name + ".")
        Team1.trickcount = 0
        Team2.trickcount = 0
        alone = 0
        shuffledcards = cards.card_values[:]
        shuffle(shuffledcards)
        for player in Players:
            player.getcards(shuffledcards)
        topcard = shuffledcards[0]
        # topcardbu = topcard[:]
        trump = topcard[0]
        if have_real_player:
            ui.display("The up-card is " + cards.labelcard(topcard[0], topcard[1]))
        for player in Players:
            if have_real_player and player == 0:
                player.showhand(trump, 0)
        dealers = positions[dealer_num:] + positions[:dealer_num]
        nextdealer_num = Players[dealers[1]].number
        firstbidder_num = Players[dealers[1]].number
        bidders = positions[firstbidder_num:] + positions[:firstbidder_num]
        # Bidding
        # bidding_round = 0
        bid = 0
        for bidder_num in bidders:
            # Second parameter is "player position" in bidding order,
            # currently stored when recording live player data. May have other uses.
            bid = Players[bidder_num].bid(
                0, bidders.index(bidder_num), Teams, topcard, dealer_num, hand
            )
            bid_type = bid[1]
            if bid_type > 0:
                bidmaker = Players[bidder_num]
                Players[dealer_num].hand.append(topcard)
                if isinstance(Players[dealer_num], LivePlayer):
                    # If the LivePlayer needs to discard, the following is skipped.
                    # LP must be prompted to discard below.
                    pass
                else:
                    handbackup = Players[dealer_num].hand[:]
                    discardvalues = []
                    for discard in range(6):
                        Players[dealer_num].hand = handbackup[:]
                        del Players[dealer_num].hand[discard]
                        discardvalues.append(
                            Players[dealer_num].calc_handvalue(
                                trump, 0, dealer_num, topcard, Players
                            )
                        )
                    Players[dealer_num].hand = handbackup
                    # Discards from dealers hand the card that resulted in highest
                    # hand value when discarded:
                    del Players[dealer_num].hand[
                        discardvalues.index(max(discardvalues))
                    ]
            if bid_type == 0:
                if have_real_player:
                    ui.display(Players[bidder_num].name + " passes.")
                continue
            else:
                if bid_type == 2:
                    alone = 1
                action = " orders "
                if bidder_num == dealer_num:
                    action = " picks "
                if have_real_player:
                    ui.display(
                        Players[bidder_num].name
                        + action
                        + "up "
                        + cards.labelcard(topcard[0], topcard[1])
                        + (". Going alone" * alone)
                        + "."
                    )
                if isinstance(Players[dealer_num], LivePlayer):
                    validdiscards = {1, 2, 3, 4, 5, 6}
                    lpdiscard = 999
                    Player0.showhand(trump, 0)
                    lpdiscard = ui.question(
                        "Which card do you want to discard? (1 through 6)",
                        datatype=int,
                        options=validdiscards,
                    )

                    del Player0.hand[lpdiscard - 1]
            break
        if bid_type == 0:
            # round of bidding in other suits, if bid_type is still 0.
            for bidder_num in bidders:
                Players[bidder_num].updatecards_out(topcard)
            for bidder_num in bidders:
                bid = Players[bidder_num].bid(
                    1, bidders.index(bidder_num), Teams, topcard, dealer_num, hand
                )
                trump = bid[0]
                bid_type = bid[1]
                if bid_type > 0:
                    bidmaker = Players[bidder_num]
                if bid_type == 0:
                    if have_real_player:
                        ui.display(Players[bidder_num].name + " passes.")
                    continue
                else:
                    if bid_type == 2:
                        alone = 1
                    if have_real_player:
                        ui.display(
                            Players[bidder_num].name
                            + " bids "
                            + cards.suitlabels[trump]
                            + (" alone" * alone)
                            + "."
                        )
                    break
        if bid_type == 0:
            if have_real_player:
                ui.display("No one bids. Redeal!")
            continue
        else:
            trumplist = [0, 1, 2, 3]
            trumplist = trumplist[trump:] + trumplist[:trump]
            LB = (trumplist[2], 2)
            # Playing
            trickcount = 1
            Team1.trickscore = 0
            Team2.trickscore = 0
            for player in Players:
                player.voids = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            for trick in range(5):
                if have_real_player:
                    ui.display("\nTrick " + str(trickcount) + ": ")
                played_cards = []  # Cards played in trick
                played_cards_values = []  # Values of cards played in trick
                if trickcount == 1:
                    leader_num = firstbidder_num
                else:
                    leader_num = currentwinner_num
                tricksequence = Players[leader_num:] + Players[0:leader_num]
                if bid_type == 2:
                    tricksequence.remove(bidmaker.partner)
                for player in tricksequence:
                    played_card = player.play(
                        leadsuit,
                        trump,
                        tricksequence,
                        bidmaker,
                        Players,
                        currentwinner_num,
                        played_cards,
                        played_cards_values,
                    )
                    if player == tricksequence[0]:
                        leadsuit = played_card[0]
                        if played_card == LB:
                            leadsuit = trump
                    if have_real_player:
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
                        for player2 in Players:
                            player2.voids[player.number][leadsuit] = 1
                    for player2 in Players:
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
                                for player3 in Players:
                                    player3.voids[player2.number][suit] = 1
                    if played_card[0] == leadsuit or played_card == LB:
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
                Players[currentwinner_num].team.trickscore += 1
                trickcount += 1
                if have_real_player:
                    ui.display("\n" + Players[currentwinner_num].name + " wins trick!")
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
            if have_real_player:
                ui.display(roundwinner.name + " wins round!")
                ui.display(
                    "Team 1 score: "
                    + str(Team1.score)
                    + "; Team 2 score: "
                    + str(Team2.score)
                )
                ui.display(
                    "Team 1 trick count:"
                    + str(Team1.trickscore)
                    + "; Team 2 trick count: "
                    + str(Team2.trickscore)
                )
            teamscores = [Team1.score, Team2.score]

            if max(teamscores) > 9:
                if have_real_player:
                    ui.display(
                        "Team "
                        + str(teamscores.index(max(teamscores)) + 1)
                        + " wins game "
                        + str(game)
                        + "!"
                    )
                Teams[teamscores.index(max(teamscores))].gamescore += 1
                Team1.score = 0
                Team2.score = 0
                game += 1
                if have_real_player:
                    ui.display("END OF GAME " + str(game))
                    ui.display(
                        "Team1 game wins="
                        + str(Team1.gamescore)
                        + " Team2 game wins="
                        + str(Team2.gamescore)
                    )

    if have_real_player:
        ui.display(
            "Team1 game wins="
            + str(Team1.gamescore)
            + " Team2 game wins="
            + str(Team2.gamescore)
        )
    return Teams


if __name__ == "__main__":
    games = 0
    realplayer = 0

    # Get input from player.
    ui = ConsoleUI()

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

    run(have_real_player, games, ui)
