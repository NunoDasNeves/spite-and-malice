from game import *

MOVE_PLAY_FROM_HAND=0
MOVE_PLAY_FROM_DISCARD=1
MOVE_PLAY_FROM_GOAL=2
MOVE_END_TURN=3

class HiddenGame:
    '''
        A class representing a Game from one player's perspective
        Information that player shouldn't be able to see isn't present
    '''
    def __init__(self, game):

        self.num_players = game.num_players
        self.num_decks = game.num_decks
        self.hand_size = game.hand_size
        self.goal_size = game.goal_size
        self.winner = game.winner
        self.goal_cards = game.goal_cards[:]
        self.discard_piles = [[pile[:] for pile in piles] for piles in game.discard_piles]
        self.play_piles = [pile[:] for pile in game.play_piles]
        self.current_player = game.current_player
        self.player_hand = game.player_hands[self.current_player][:]

        # functions for generically doing moves
        self.move_list = [game.play_from_hand, game.play_from_discard, game.play_from_goal, game.end_turn]

        # not sure if needed/useful
        self.draw_pile_size = len(game.draw_pile)

    def is_valid_play(self, card, play_pile_index):
        '''
            Check if a card can be played onto a given play pile
            Assume that the play pile has less than MAX_CARDS_PER_PLAY_PILE
        '''
        # wild cards can be played on any pile
        if card.is_wild():
            return True
        play_pile_length = len(self.play_piles[play_pile_index])
        # empty piles can only have aces played on them
        if play_pile_length == 0 and card.value == 1:
            return True
        # nonempty piles
        if play_pile_length + 1 == card.value:
            return True
        return False

    def get_legal_moves(self):
        '''
            Return a list of all legal moves for the current player
            Each move is a tuple of (move_type, (args))

        '''
        legal_moves = []

        for card in self.player_hand:
            for i in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, i):
                    legal_moves.append((MOVE_PLAY_FROM_HAND, (card, i)))
            for i in range(NUM_DISCARD_PILES):
                legal_moves.append((MOVE_END_TURN, (card, i)))

        for i in range(NUM_DISCARD_PILES):
            if len(self.discard_piles[self.current_player][i]) == 0:
                continue
            card = self.discard_piles[self.current_player][i][-1]
            for j in range(NUM_PLAY_PILES):
                if self.is_valid_play(card, i):
                    legal_moves.append((MOVE_PLAY_FROM_DISCARD, (i, j)))

        for i in range(NUM_PLAY_PILES):
            if self.is_valid_play(self.goal_cards[self.current_player], i):
                legal_moves.append((MOVE_PLAY_FROM_GOAL, (i,)))

        return legal_moves

    def move_repr(self, move):
        '''
            Pretty print a move current player can make
        '''
        card = None
        from_str = None
        on_card = None
        pile_index = None

        if move[0] == MOVE_END_TURN:
            return "Ends their turn by discarding {} onto discard pile {}".format(move[1][0], move[1][1])

        elif move[0] == MOVE_PLAY_FROM_HAND:
            from_str = "from their hand"
            card, pile_index = move[1][0], move[1][1]

        elif move[0] == MOVE_PLAY_FROM_DISCARD:
            disc_index = move[1][0]
            from_str = "from discard pile {}".format(disc_index)
            card, pile_index = self.discard_piles[self.current_player][disc_index][-1], move[1][1]

        elif move[0] == MOVE_PLAY_FROM_GOAL:
            from_str = ": their topmost goal card"
            card, pile_index = self.goal_cards[self.current_player], move[1][0]

        if len(self.play_piles[pile_index]) > 0:
            on_card = "the {} on pile {}".format(self.play_piles[pile_index][-1], pile_index)
        else:
            on_card = "an empty space"

        return "Plays {} {} onto {}".format(card, from_str, on_card)

    def do_move(self, move):
        '''
            Do a move supplied as a tuple (move_id, args)
            return the newly created game
        '''
        return self.move_list[move[0]](*move[1])


