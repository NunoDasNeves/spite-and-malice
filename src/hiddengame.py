from game import *

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

        self.current_player = game.current_player
        self.winner = game.winner
        self.goal_cards = game.goal_cards[:]
        self.goal_pile_sizes = [len(pile) for pile in game.goal_piles]
        self.discard_piles = [[pile[:] for pile in piles] for piles in game.discard_piles]
        self.play_piles = [pile[:] for pile in game.play_piles]
        self.player_hand = game.player_hands[self.current_player][:]

        # The player whose perspective this hidden game is from
        self.this_player = game.current_player

        # functions from game
        self.is_valid_play = game.is_valid_play
        self.check_play_pile = game.check_play_pile
        self.get_play_pile_values = game.get_play_pile_values

        # not sure if needed/useful
        self.draw_pile_size = len(game.draw_pile)

        self.make_immutable()

    def mutable_copy(self):
        '''
            Clone the hidden game object, deep copying everything except the cards themselves
        '''
        clone = shallow_copy(self)
        clone.goal_cards = list(self.goal_cards[:])
        clone.goal_pile_sizes = list(self.goal_pile_sizes[:])
        clone.discard_piles = [[list(pile[:]) for pile in piles] for piles in self.discard_piles]
        clone.play_piles = [list(pile[:]) for pile in self.play_piles]
        clone.player_hand = list(self.player_hand[:])
        return clone
    
    def make_immutable(self):
        self.goal_cards = tuple(self.goal_cards)
        self.goal_pile_sizes = tuple(self.goal_pile_sizes)
        self.discard_piles = tuple([tuple([tuple(pile) for pile in piles]) for piles in self.discard_piles])
        self.play_piles = tuple([tuple(pile) for pile in self.play_piles])
        self.player_hand = tuple(self.player_hand)

    def __hash__(self):
        return hash((
            self.num_players,
            self.num_decks,
            self.hand_size,
            self.goal_size,
            self.current_player,
            self.winner,
            self.goal_cards,
            self.discard_piles,
            self.play_piles,
            self.player_hand,
            self.this_player
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
                if self.is_valid_play(card, i):
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
        if self.current_player != self.this_player:
            raise RuntimeError("You don't know that they have that card!")
        if card not in self.player_hand:
            raise RuntimeError("Can't play that card - it's not in your hand!")
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # copy the game
        game = self.mutable_copy()
        # make the play
        game.player_hand.remove(card)
        game.play_piles[play_pile_index].append(card)
        # check the pile to see if it's done
        game.check_play_pile(play_pile_index)
        # if player's hand is empty, draw another hand of cards
        # <not done in hiddengame>
        game.make_immutable()
        return game

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

        # copy the game
        game = self.mutable_copy()
        # make the play
        game.discard_piles[self.current_player][discard_pile_index].pop()
        game.play_piles[play_pile_index].append(card)
        # check the pile to see if it's done
        game.check_play_pile(play_pile_index)
        game.make_immutable()
        return game

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

        # copy the game
        game = self.mutable_copy()
        # make the play
        game.play_piles[play_pile_index].append(card)
        if game.goal_pile_sizes[game.current_player] > 0:
            game.goal_cards[game.current_player] = None
            # check the pile to see if it's done
            game.check_play_pile(play_pile_index)
        else:
            # if the goal pile is empty, the current player won!
            game.winner = game.current_player
        game.make_immutable()
        return game

    def end_turn(self, card, discard_pile_index):
        '''
            End the current player's turn, discarding one card from their hand
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")

        if self.current_player != self.this_player:
            raise RuntimeError("You don't know that they have that card!")
        # check the card is in their hand
        if card not in self.player_hand:
            raise RuntimeError("Can't discard that card - it's not in your hand!")

        # copy the game
        game = self.mutable_copy()
        # discard the card
        game.player_hand.remove(card)
        game.discard_piles[game.current_player][discard_pile_index].append(card)
        # Advance to the next player
        game.current_player = (game.current_player + 1) % game.num_players
        # Have them draw until their hand is full
        # < can't do it here >
        game.make_immutable()
        return game

    def do_move(self, move, args):
        '''
            'Do' a move (hidden information remains hidden) supplied as a tuple (move_id, args)
            return the newly created HiddenGame
        '''
        move_list = (self.play_from_goal, self.play_from_hand, self.play_from_discard, self.end_turn)
        return move_list[move](*args)

