from euchre import cards

playernames = ["Sam", "Kim", "Sue", "Tim"]


class Player:
    def __init__(self, name, number, ui):
        self.name = name
        self.number = number
        self.voids = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.handvalue = 0
        self.handbu = []
        self.ui = ui

    def getcards(self, deck):
        self.hand = []
        for card in range(5):
            self.hand.append(deck.pop())
            self.cards_out = cards.card_values[:]
        for card in self.hand:
            del self.cards_out[self.cards_out.index(card)]
        self.handbu = self.hand[:]
        self.cards_outbu = self.cards_out[:]

    def getsuit(self, suit, cards, trump):
        self.cardlist = []
        trumplist = [0, 1, 2, 3]
        trumplist = trumplist[trump:] + trumplist[:trump]
        LB_local = (trumplist[2], 2)
        for card in cards:
            if card == LB_local:
                if suit == trump:
                    self.cardlist.append(card)
            else:
                if card[0] == suit:
                    self.cardlist.append(card)
        return self.cardlist

    def setpartner(self, partner):
        self.partner = partner

    def setteam(self, team):
        self.team = team

    def setopposingteam(self, team):
        self.opposingteam = team

    def updatecards_out(self, card):
        del self.cards_out[self.cards_out.index(card)]

    def getcardvalues(self, trump):
        self.cardvalues = []
        for card in self.hand:
            value = cards.calc_card_point_value(trump, card)
            self.cardvalues.append(value)
        return self.cardvalues

    def calc_handvalue(self, trump, bidding_round, dealer_num, topcard, players):
        "Totals up hand value based on particular assumption of trump."
        self.handvalue = 0
        trial_hand = self.hand[:]
        if bidding_round == 0 and self.number == dealer_num:
            trial_hand.append(topcard)
        trumplist = [0, 1, 2, 3]
        trumplist = trumplist[trump:] + trumplist[:trump]
        LB_local = (trumplist[2], 2)
        suitcounts = [0, 0, 0, 0]

        for card in trial_hand:
            if card == LB_local:
                suitcounts[trump] += 1
            else:
                suitcounts[card[0]] += 1
        # Calculate temporary card values.
        discardvalues = [9] * len(trial_hand)
        count = 0
        for card in trial_hand:
            if not (card[0] == trump) and not card == LB_local:
                # formula computes value of all non-trump card values by
                # subtracting 4.5 from positional value,
                # then dividing by the cube of all cards in that suit.
                discardvalues[count] = (card[1] - 4.5) / pow(suitcounts[card[0]], 3)
            count += 1
        if len(trial_hand) == 6:
            del trial_hand[discardvalues.index(min(discardvalues))]
        for card in trial_hand:
            self.handvalue += cards.calc_card_point_value(trump, card)
            if card[1] < 5 and card[1] > 0:
                # reduces value of 10 through King for bidding purposes
                self.handvalue -= 1
        trumpvoid = 1
        if suitcounts[trump] > 0:
            trumpvoid = 0
        if not (trumpvoid):
            for suit in range(0, 4):
                if suitcounts[suit] == 0 and not (suit == trump):
                    self.handvalue += 6

        if bidding_round == 0:
            if self.partner.number == dealer_num:
                # Extra points for adding up-card to hand or to partner's hand.
                self.handvalue += cards.calc_card_point_value(trump, topcard) + 3
            if self.opposingteam == players[dealer_num].opposingteam:
                # Negative points for adding up-card to opposing team's hand,
                # plus extra penalty (3) for possibility they'll create a void.
                self.handvalue -= cards.calc_card_point_value(trump, topcard) + 3
        return self.handvalue

    def showhand(self, trump, bidding_round):
        if isinstance(self, LivePlayer):
            print("\nYour hand:")
        else:
            print("\n" + self.name + "'s hand:")
        self.hand.sort(key=lambda card: card[1])  # sort by position
        self.hand.sort(key=lambda card: card[0])  # sort by suit
        LB_local = (999, 999)
        if bidding_round == 0 and trump > -1:
            # NOTE: Bidding round is 0 in first round of bidding
            # and after a bid is made
            trumpcards = []
            trumplist = [0, 1, 2, 3]
            trumplist = trumplist[trump:] + trumplist[:trump]
            LB_local = (trumplist[2], 2)  # left bauer
            for card in self.hand:
                if card[0] == trump or card == LB_local:
                    trumpcards.append(card)
            selfhandmatch = self.hand[:]
            for card in selfhandmatch:
                if card in trumpcards:
                    # removes trump cards from self.hand:
                    del self.hand[self.hand.index(card)]
            trumpcardvalues = []
            trumpcards2 = trumpcards[:]
            for card in trumpcards:
                trumpcardvalues.append(
                    cards.calc_card_point_value(trump, card)
                )  # calculates values for trump cards

            def findkey(tup):
                # function returns value of trump card by matching position
                # of the card tuple (suit, position) in an unchanging master
                # list of trump cards
                return trumpcardvalues[trumpcards2.index(tup)]

            trumpcards.sort(key=findkey)  # sorts trump cards according to their value
            for card in self.hand:
                # re-attaches cards from rest of hand to trump cards
                trumpcards.append(card)
            # assigns new values to self.hand from foregoing
            self.hand = trumpcards[:]
        if self.hand[0] == LB_local:
            currentsuit = trump  # XXX Was "trump"  Don't think it needed to be. -Jesse
        else:
            currentsuit = self.hand[0][0]
        print(cards.suitlabels[currentsuit] + ":"),
        for card in self.hand:
            if card == LB_local:
                if not card == self.hand[0]:
                    print(","),  # ,end=''
                print(
                    "Jack of " + cards.suitlabels[card[0]] + " [left bauer]"
                ),  # ,end=""
            elif card[0] == currentsuit:
                if not card == self.hand[0]:
                    print(","),  # ,end=''
                print(
                    cards.positionlabels[card[1]]
                    + (
                        (" of " + cards.suitlabels[card[0]] + " [left bauer]")
                        * (card == LB_local)
                    )
                ),  # ,end=''
            else:
                currentsuit = card[0]
                print(
                    "\n"
                    + cards.suitlabels[card[0]]
                    + ": "
                    + cards.positionlabels[card[1]]
                ),  # ,end=''
        print("\n")

    def bid(self, bidding_round, player_position, teams, topcard, dealer_num, hand):
        self.handval = 0
        players = [
            teams[0].playerA,
            teams[1].playerA,
            teams[0].playerB,
            teams[1].playerB,
        ]
        if self.team == teams[0]:
            lowcutR0 = 36
            lowcutR1 = 33
            highcutR0 = 49
            highcutR1 = 46
        else:
            lowcutR0 = 36
            lowcutR1 = 33
            highcutR0 = 49
            highcutR1 = 46
        if bidding_round == 0:
            trump = topcard[0]
            self.handval = self.calc_handvalue(trump, 0, dealer_num, topcard, players)
            if self.handval > lowcutR0:
                if self.handval > highcutR0:
                    bid_type = 2
                else:
                    bid_type = 1
            else:
                bid_type = 0
        else:
            x = [0, 1, 2, 3]
            del x[topcard[0]]
            y = [0, 0, 0]
            count = 0
            for trump in x:
                y[count] = self.calc_handvalue(trump, 1, dealer_num, topcard, players)
                count += 1
            if max(y) > lowcutR1:
                if max(y) > highcutR1:
                    bid_type = 2
                else:
                    bid_type = 1
                trump = x[y.index(max(y))]
            else:
                bid_type = 0
        self.team.bid = bid_type
        return trump, bid_type

    def lead(self, trump, bidmaker):
        # picks a card for leading a trick
        lead_card_values = [0] * len(self.hand)
        count = 0
        trumplist = [0, 1, 2, 3]
        trumplist = trumplist[trump:] + trumplist[:trump]
        LB_local = (trumplist[2], 2)
        for card in self.hand:
            # This section to determine value of leading with trump cards.
            if card[0] == trump or card == LB_local:
                if self.partner == bidmaker or self == bidmaker:
                    lead_card_values[count] += 6
                else:
                    lead_card_values[count] -= 4
                higher = 0
                trumps_out = self.getsuit(trump, self.cards_out, trump)
                for card2 in trumps_out:
                    if cards.calc_card_point_value(
                        trump, card
                    ) < cards.calc_card_point_value(trump, card2):
                        higher += 1
                if higher == 0:
                    # card is higher than trump cards still out in other
                    # players hand (or discard pile)
                    lead_card_values[count] += 2
                lead_card_values[count] -= higher
                # trump card value as lead increased by other trump in hand:
                lead_card_values[count] += (
                    len(self.getsuit(trump, self.hand, trump)) - 1
                )
                # trump card value as lead descreased by voids in hand
                # (missed opportunity to trump opponents' high off-suit cards)
                lead_card_values[count] -= 2 * (sum(self.voids[self.number]))
                count += 1
            # This section to determine value of leading with non-trump cards.
            else:
                lower = 0
                higher = 0
                for card2 in self.getsuit(card[0], self.cards_out, trump):
                    if cards.calc_card_point_value(
                        trump, card
                    ) < cards.calc_card_point_value(trump, card2):
                        higher += 1
                    else:
                        lower += 1
                if higher == 0:
                    lead_card_values[count] += 2  # Card is high in suit.
                if (lower - higher) > 1:
                    # Of cards in same suit that are still out there,
                    # lower cards outnumber higher by more than 1.
                    lead_card_values[count] += 1
                if higher > lower:
                    # Of cards in same suit that are still out there,
                    # more are higher than lower.
                    lead_card_values[count] -= 1
                if (
                    sum(self.voids[self.partner.number]) > 0
                    and self.voids[self.partner.number][trump] == 0
                ):
                    lead_card_values[count] += 2  # My partner could trump in.
                if self.voids[self.opposingteam.playerA.number][card[0]] == 1:
                    if self.voids[self.opposingteam.playerA.number][trump] == 1:
                        # player in opposing team cannot beat, cannot trump
                        lead_card_values[count] += 1
                    else:
                        # player in opposing team has void, could possibly trump
                        lead_card_values[count] -= 1
                if self.voids[self.opposingteam.playerB.number][card[0]] == 1:
                    if self.voids[self.opposingteam.playerB.number][trump] == 1:
                        # player in opposing team cannot beat, cannot trump
                        lead_card_values[count] += 1
                    else:
                        # player in opposing team has void, could possibly trump
                        lead_card_values[count] -= 1
                if (
                    len(self.getsuit(card[0], self.hand, trump)) == 1
                    and len(self.getsuit(trump, self.hand, trump)) > 0
                ):
                    # could create a void in own hand, then trump
                    lead_card_values[count] += 1
                count += 1
        leadcard = self.hand[lead_card_values.index(max(lead_card_values))]
        # NOTE-If highest value is found in more than one card, the first
        # card in hand will be chosen.
        return leadcard

    def follow(
        self,
        leadsuit,
        trump,
        tricksequence,
        players,
        currentwinner_num,
        played_cards,
        played_cards_values,
    ):
        follow_card_values = []
        validcards = self.getsuit(leadsuit, self.hand, trump)
        trumpcards = self.getsuit(trump, self.hand, trump)
        validcardvalues = []
        trumpcardvalues = []
        for validcard in validcards:
            validcardvalues.append(cards.calc_card_point_value(trump, validcard))
        for trumpcard in trumpcards:
            trumpcardvalues.append(cards.calc_card_point_value(trump, trumpcard))
        if validcards:
            lowcard = validcards[validcardvalues.index(min(validcardvalues))]
            highcard = validcards[validcardvalues.index(max(validcardvalues))]
        if trumpcards:
            lowtrump = trumpcards[trumpcardvalues.index(min(trumpcardvalues))]
            hightrump = trumpcards[trumpcardvalues.index(max(trumpcardvalues))]
        if validcards:
            if (
                players[currentwinner_num] == self.partner
            ):  # If your partner is winning....
                partnercard = played_cards[tricksequence.index(self.partner)]
                for card in self.getsuit(leadsuit, self.cards_out, trump):
                    if cards.calc_card_point_value(
                        trump, card
                    ) > cards.calc_card_point_value(trump, partnercard):
                        # And there's a within-suit card still out that's higher
                        # than partner's.
                        # This will sometimes lead to playing a higher card
                        # than necessary--if in last position,
                        # will play highest card even when a lower might be sure to
                        # win; and if partner is just one step below.
                        if cards.calc_card_point_value(
                            trump, highcard
                        ) > cards.calc_card_point_value(trump, partnercard):
                            # ... and could lose to other in-suit card, then play
                            # my high card, if it beats partner's.
                            return highcard
                else:
                    return lowcard
            else:
                # If partner not winning....
                # NOTE: This will sometimes lead to playing a higher
                # card than necessary.
                if cards.calc_card_point_value(trump, highcard) > max(
                    played_cards_values
                ):
                    return highcard
                else:
                    return lowcard
        elif trumpcards:
            if players[currentwinner_num] == self.partner:
                # If your partner is winning....
                partnercard = played_cards[tricksequence.index(self.partner)]
                for card in self.getsuit(leadsuit, self.cards_out, trump):
                    if cards.calc_card_point_value(
                        trump, card
                    ) > cards.calc_card_point_value(trump, partnercard):
                        if cards.calc_card_point_value(
                            trump, lowtrump
                        ) > cards.calc_card_point_value(trump, partnercard):
                            # ... and could lose to other in-suit card,
                            # then play my lowest trump card, if it beats partner's.
                            return lowtrump
                        elif cards.calc_card_point_value(
                            trump, hightrump
                        ) > cards.calc_card_point_value(trump, partnercard):
                            return hightrump
            else:
                if cards.calc_card_point_value(trump, lowtrump) > max(
                    played_cards_values
                ):
                    return lowtrump
                else:
                    if cards.calc_card_point_value(trump, hightrump) > max(
                        played_cards_values
                    ):
                        return hightrump

        # If this point reached, cannot win trick. Play lowest card.
        for card in self.hand:
            follow_card_values.append(cards.calc_card_point_value(trump, card))
            if self.getsuit(card[0], self.hand, trump) == 1:
                follow_card_values[len(follow_card_values)] -= 4
        followcard = self.hand[follow_card_values.index(min(follow_card_values))]
        return followcard

    def play(
        self,
        leadsuit,
        trump,
        tricksequence,
        bidmaker,
        players,
        currentwinner_num,
        played_cards,
        played_cards_values,
    ):
        if tricksequence.index(self) == 0:
            play_card = self.lead(trump, bidmaker)
        else:
            play_card = self.follow(
                leadsuit,
                trump,
                tricksequence,
                players,
                currentwinner_num,
                played_cards,
                played_cards_values,
            )
        del self.hand[self.hand.index(play_card)]
        return play_card


class LivePlayer(Player):
    def __init__(self, name, number, ui):
        self.name = name
        self.number = number
        self.voids = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.bidding_data = []
        self.ui = ui

    def bid(
        self, bidding_round, player_position, teams, topcard, dealer_num, hand
    ):  # Does this override bid for Player class?
        players = [
            teams[0].playerA,
            teams[1].playerA,
            teams[0].playerB,
            teams[1].playerB,
        ]
        if bidding_round == 0:
            trump = topcard[0]
            handval = self.calc_handvalue(trump, 0, dealer_num, topcard, players)
            validbids = {0, 1, 2, 88}
            bid_type = 999
            bid_type = self.ui.question(
                "Do you want to bid? (0=no; 1=yes; 2=go alone)",
                datatype=int,
                options=validbids,
            )
            if bid_type == 88:  # WTF?
                teams[0].score += 10
                bid_type = 1
            roundinfo = [
                bid_type,
                hand,
                bidding_round,
                player_position,
                handval,
                trump,
                topcard,
                self.hand,
            ]
            self.bidding_data.append(roundinfo)
            self.team.bid = bid_type
            return trump, bid_type
        else:
            self.showhand(-1, 1)
            validbids = {0, 1, 2}
            bid_type = 999
            bid_type = self.ui.question(
                "Do you want to bid? (0=no; 1=yes; 2=go alone)",
                datatype=int,
                options=validbids,
            )
            if bid_type > 0:
                validtrump = {0, 1, 2, 3}
                trump = 999
                validtrump.remove(topcard[0])
                trump = self.ui.question(
                    "Which suit? (hearts=0, spades=1, diamonds=2, clubs=3)",
                    datatype=int,
                    options=validtrump,
                )
                handval = self.calc_handvalue(trump, 1, dealer_num, topcard, players)
            else:
                x = [0, 1, 2, 3]
                del x[topcard[0]]
                y = [0, 0, 0]
                count = 0
                for trump in x:
                    y[count] = self.calc_handvalue(
                        trump, 1, dealer_num, topcard, players
                    )
                    count += 1
                handval = max(y)
                trump = x[y.index(max(y))]
                bid_type = 0
            roundinfo = [
                bid_type,
                hand,
                bidding_round,
                player_position,
                handval,
                trump,
                topcard,
                self.hand,
            ]
            self.bidding_data.append(roundinfo)
            self.team.bid = bid_type
            return trump, bid_type

    def play(
        self,
        leadsuit,
        trump,
        tricksequence,
        bidmaker,
        players,
        currentwinner_num,
        played_cards,
        played_cards_values,
    ):
        self.showhand(trump, 0)
        legit = {x + 1 for x in range(len(self.hand))}
        pc = 999
        trumplist = [0, 1, 2, 3]
        trumplist = trumplist[trump:] + trumplist[:trump]
        LB_local = (trumplist[2], 2)
        while pc not in legit:
            pc = self.ui.question(
                "Which card? (1 through " + str(len(self.hand)) + "): ",
                datatype=int,
                options=legit,
            )
            if pc in legit:
                if tricksequence.index(self) > 0:
                    if len(self.getsuit(leadsuit, self.hand, trump)) > 0:
                        if self.hand[pc - 1] == LB_local and leadsuit == trump:
                            pass
                        elif self.hand[pc - 1][0] != leadsuit and (pc in legit):
                            self.ui.display("Must follow lead suit.")
                            pc = 99
        play_card = self.hand[pc - 1]
        del self.hand[pc - 1]
        return play_card


class Team:
    def __init__(self, number, players):
        self.name = "Team " + str(number)
        self.number = number
        self.score = 0
        self.trickscore = 0
        self.gamescore = 0
        self.bid = 0
        # Bind players as attributes in team to players that exist outside the team.
        # Otherwise, having players bid and play in order seemed too complicated.
        self.playerA = players[number - 1]
        self.playerB = players[number + 1]
        self.playerA.setpartner(self.playerB)
        self.playerB.setpartner(self.playerA)
        self.playerA.setteam(self)
        self.playerB.setteam(self)

    def setopposingteam(self, team):
        self.playerA.setopposingteam(team)
        self.playerB.setopposingteam(team)
