from game import *
from utils import copy_nested
from move import *

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

        # store the last move
        self.last_move = Move(None, None)

        self.make_immutable()

    def make_immutable(self):
        for attr, value in self.__dict__.items():
            if attr.startswith('__'):
                continue
            if isinstance(value, list):
                self.__dict__[attr] = copy_nested(value, immutable=True)

    def get_legal_moves(self):
        '''
            Return a tuple of all legal moves for the current player, indexed by move type
            Each entry is a list of moves for a type of move
        '''
        from_goal = []
        from_hand = []
        from_discard = []
        end_turn = []

        for card in self.player_hands[self.current_player]:
            for i in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, i):
                    from_hand.append(Move(MOVE_PLAY_HAND, (card, i)))
            for i in range(NUM_DISCARD_PILES):
                end_turn.append(Move(MOVE_END_TURN, (card, i)))

        for i in range(NUM_DISCARD_PILES):
            if len(self.discard_piles[self.current_player][i]) == 0:
                continue
            card = self.discard_piles[self.current_player][i][-1]
            for j in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, j):
                    from_discard.append(Move(MOVE_PLAY_DISCARD, (i, j)))

        for i in range(NUM_PLAY_PILES):
            if self.is_valid_play(self.goal_cards[self.current_player], i):
                from_goal.append(Move(MOVE_PLAY_GOAL, (i,)))
    
        return (from_goal, from_hand, from_discard, end_turn)

    def fill_hand(self):
        pass

    def do_other_work(self):
        '''
            Do everything that isn't shared with Game
        '''
        # remove full play piles
        for i in range(len(self.play_piles)):
            if len(self.play_piles[i]) == MAX_CARDS_PER_PLAY_PILE:
                self.play_piles[i] = []

    def do_move(self, move):
        game = super().do_move(move)
        game.last_move = move
        game.make_immutable()
        return game
