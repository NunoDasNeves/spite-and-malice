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
        self.goal_cards = tuple(game.goal_cards[:])
        self.goal_pile_sizes = tuple([len(pile) for pile in game.goal_piles])
        self.discard_piles = copy_nested(game.discard_piles, immutable=True)
        self.play_piles = copy_nested(game.play_piles,immutable=True)
        # mask other player hands
        self.player_hands = copy_nested(game.player_hands)
        self.player_hands = tuple(
            [tuple(hand) if i == self.current_player else None \
                for i, hand in zip(range(len(self.player_hands)), self.player_hands)]
            )
        self.player_hand = self.player_hands[self.current_player]

        # The player whose perspective this hidden game is from
        self.this_player = game.current_player

        # not sure if needed/useful
        self.draw_pile_size = len(game.draw_pile)

    def copy(self):
        '''
            Clone the hidden game object, deep copying everything except the cards themselves
        '''
        clone = shallow_copy(self)
        clone.goal_cards = tuple(self.goal_cards[:])
        clone.goal_pile_sizes = tuple(self.goal_pile_sizes[:])
        # these can be modified by arguments
        clone.discard_piles = copy_nested(self.discard_piles, immutable=True)
        clone.play_piles = copy_nested(self.play_piles, immutable=True)
        clone.player_hands = copy_nested(self.player_hands, immutable=True)
        clone.player_hand = tuple(self.player_hand[:])
        return clone

    def __hash__(self):
        return hash((
            self.num_players,
            self.num_decks,
            self.hand_size,
            self.goal_size,
            self.current_player,
            self.winner,
            self.goal_cards,
            self.goal_pile_sizes,
            self.discard_piles,
            self.play_piles,
            self.player_hand
        ))

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

        for card in self.player_hand:
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

    def play_from_hand(self, card, play_pile_index):
        '''
            Play a card from the current player's hand onto a play pile
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")
        # validate the play
        if card not in self.player_hand:
            raise RuntimeError("Can't play that card - it's not in your hand!")
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # make the play
        new_hand = copy_nested(self.player_hand)
        new_piles = copy_nested(self.play_piles)
        new_hand.remove(card)
        new_piles[play_pile_index].append(card)
        # check the pile to see if it's done, and empty it if so
        if len(new_piles[play_pile_index]) >= MAX_CARDS_PER_PLAY_PILE:
            new_piles[play_pile_index] = []
        # if player's hand is empty, draw another hand of cards
        # <not done in hiddengame>
        new_game = self.copy()
        new_game.player_hand = copy_nested(new_hand, immutable=True)
        new_game.play_piles = copy_nested(new_piles, immutable=True)
        return new_game

    def play_from_discard(self, discard_pile_index, play_pile_index):
        '''
            Play a card from one of the current player's discard piles
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")
        # validate the play
        if len(self.discard_piles[self.current_player][discard_pile_index]) == 0:
            raise RuntimeError("Can't play from an empty discard pile!")
        card = self.discard_piles[self.current_player][discard_pile_index][-1]
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # make the play
        new_discard = discard_piles[self.current_player][discard_pile_index].pop()
        new_piles = play_piles[play_pile_index].append(card)
        # check the pile to see if it's done
        if len(new_piles[play_pile_index]) >= MAX_CARDS_PER_PLAY_PILE:
            new_piles[play_pile_index] = []
        
        new_game = self.copy()
        new_game.discard_piles = copy_nested(new_discard, immutable=True)
        new_game.play_piles = copy_nested(new_piles, immutable=True)
        return new_game

    def play_from_goal(self, play_pile_index):
        '''
            Play the current player's goal card
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")
        # validate the play
        card = self.goal_cards[self.current_player]
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # make the play
        new_piles = copy_nested(self.play_piles)
        new_goal_cards = copy_nested(self.goal_cards)
        new_goal_sizes = copy_nested(self.goal_pile_sizes)
        new_game = self.copy()

        new_piles[play_pile_index].append(card)
        new_goal_cards[self.current_player] = None
        new_goal_sizes[self.current_player] -= 1
        if new_goal_sizes[self.current_player] > 0:
            # check the pile to see if it's done
            if len(new_piles[play_pile_index]) >= MAX_CARDS_PER_PLAY_PILE:
                new_piles[play_pile_index] = []
        else:
            # if the goal pile is empty, the current player won!
            new_game.winner = self.current_player
        
        new_game.play_piles = copy_nested(new_piles, immutable=True)
        new_game.goal_cards = tuple(new_goal_cards)
        new_game.goal_pile_sizes = tuple(new_goal_sizes)

        return new_game

    def end_turn(self, card, discard_pile_index):
        '''
            Since HiddenGame doesn't reveal much about other players, this won't be useful...
        '''
        raise RuntimeError("HiddenGame doesn't support end_turn!")

    def do_move(self, move, args):
        '''
            'Do' a move (hidden information remains hidden) supplied as a tuple (move_id, args)
            return the newly created HiddenGame
        '''
        move_list = (self.play_from_goal, self.play_from_hand, self.play_from_discard, self.end_turn)
        return move_list[move](*args)

