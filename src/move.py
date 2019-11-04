MOVE_PLAY_GOAL=0
MOVE_PLAY_HAND=1
MOVE_PLAY_DISCARD=2
MOVE_END_TURN=3

MOVE_TYPES={
        MOVE_PLAY_GOAL: "Play your goal card",
        MOVE_PLAY_HAND: "Play from your hand",
        MOVE_PLAY_DISCARD: "Play from a discard pile",
        MOVE_END_TURN: "End your turn (discard)"
        }

class Move:
    def __init__(self, mtype, args):
        if mtype not in MOVE_TYPES:
            raise RuntimeError("Move type {} not in valid moves".format(mtype))
        self.type = mtype
        self.args = args

    def repr(self, hg):
        '''
            Pretty print a move current player can make
        '''
        card = None
        from_str = None
        on_card = None
        pile_index = None

        if self.type == MOVE_END_TURN:
            pile = hg.discard_piles[hg.current_player][self.args[1]]
            top_card = pile[-1] if len(pile) > 0 else "nothing"
            return "End turn by discarding {} onto {} on discard pile {}".format(self.args[0], top_card, self.args[1])

        elif self.type == MOVE_PLAY_HAND:
            from_str = "from hand"
            card, pile_index = self.args[0], self.args[1]

        elif self.type == MOVE_PLAY_DISCARD:
            disc_index = self.args[0]
            from_str = "from discard pile {}".format(disc_index)
            pile = hg.discard_piles[hg.current_player][disc_index]
            card, pile_index = pile[-1], self.args[1]

        elif self.type == MOVE_PLAY_GOAL:
            from_str = ": topmost goal card"
            card, pile_index = hg.goal_cards[hg.current_player], self.args[0]

        else:
            raise RuntimeError("Invalid move type: {}".format(self.type))

        if len(hg.play_piles[pile_index]) > 0:
            on_card = "the {} on pile {}".format(hg.play_piles[pile_index][-1], pile_index)
        else:
            on_card = "an empty space"

        return "Play {} {} onto {}".format(card, from_str, on_card)