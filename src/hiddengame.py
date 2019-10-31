from game import *
from utils import copy_nested

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


class HiddenGame(Game):
    '''
        A class representing a Game from one player's perspective
        Information that player shouldn't be able to see isn't present
    '''
    def __init__(self, game):

        self.num_players = game.num_players
        self.num_decks = game.num_decks
        self.hand_size = game.hand_size
        self.goal_size = game.goal_size

        self.current_player = game.current_player
        self.winner = game.winner
        self.goal_cards = game.goal_cards[:]
        self.discard_piles = copy_nested(game.discard_piles)
        self.play_piles = copy_nested(game.play_piles)
        # mask other player hands
        self.player_hands = copy_nested(game.player_hands)
        self.player_hands = [
            hand if i == self.current_player else None \
                for i, hand in zip(range(len(self.player_hands)), self.player_hands)
            ]

        self.make_immutable()

    def make_immutable(self):
        for attr, value in self.__dict__.items():
            if attr.startswith('__'):
                continue
            if isinstance(value, list):
                self.__dict__[attr] = copy_nested(value, immutable=True)

    def get_legal_moves(self):
        '''
            Return a tuple of all legal moves for the current player
            Each entry is a list of moves for a type of move corresponding to the index in the tuple
            Each entry in each list is the args for the move
            e.g. ([args, args, args], [args], [], [args, args])
        '''
        from_goal = []
        from_hand = []
        from_discard = []
        end_turn = []

        for card in self.player_hands[self.current_player]:
            for i in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, i):
                    from_hand.append((card, i))
            for i in range(NUM_DISCARD_PILES):
                end_turn.append((card, i))

        for i in range(NUM_DISCARD_PILES):
            if len(self.discard_piles[self.current_player][i]) == 0:
                continue
            card = self.discard_piles[self.current_player][i][-1]
            for j in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, j):
                    from_discard.append((i, j))

        for i in range(NUM_PLAY_PILES):
            if self.is_valid_play(self.goal_cards[self.current_player], i):
                from_goal.append((i,))

        return (from_goal, from_hand, from_discard, end_turn)

    def move_repr(self, move_type, args):
        '''
            Pretty print a move current player can make
        '''
        card = None
        from_str = None
        on_card = None
        pile_index = None

        if move_type == MOVE_END_TURN:
            return "End turn by discarding {} onto discard pile {}".format(args[0], args[1])

        elif move_type == MOVE_PLAY_HAND:
            from_str = "from hand"
            card, pile_index = args[0], args[1]

        elif move_type == MOVE_PLAY_DISCARD:
            disc_index = args[0]
            from_str = "from discard pile {}".format(disc_index)
            card, pile_index = self.discard_piles[self.current_player][disc_index][-1], args[1]

        elif move_type == MOVE_PLAY_GOAL:
            from_str = ": topmost goal card"
            card, pile_index = self.goal_cards[self.current_player], args[0]

        if len(self.play_piles[pile_index]) > 0:
            on_card = "the {} on pile {}".format(self.play_piles[pile_index][-1], pile_index)
        else:
            on_card = "an empty space"

        return "Play {} {} onto {}".format(card, from_str, on_card)

    def fill_hand(self, player_id):
        pass

    def do_other_work(self):
        '''
            Do everything that isn't shared with Game
        '''
        # remove full play piles
        for i in range(len(self.play_piles)):
            if len(self.play_piles[i]) == MAX_CARDS_PER_PLAY_PILE:
                self.play_piles[i] = []

    def do_move(self, move, args):
        game = super().do_move(move, args)
        # make lists into tuples
        game.make_immutable()
        return game
