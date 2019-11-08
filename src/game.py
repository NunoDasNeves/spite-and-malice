import random
from copy import copy as shallow_copy
from cards import Card, draw, draw_N, make_decks, NUM_CARDS_PER_DECK
from utils import copy_nested

NUM_DISCARD_PILES=4
NUM_PLAY_PILES=4
MAX_CARDS_PER_PLAY_PILE=12

class Game:
    '''
        A simulated game of spite and malice
        Functions that progress the game return a new Game
    '''
    def __init__(self, num_players=2, num_decks=2, goal_size=13, hand_size=4):
        '''
            Create a new game, ready to play with the specified parameters
        '''
        if num_players < 2:
            raise RuntimeError("Too few players")
        # TODO explore how many cards are needed to ensure a game finishes - this is a rough guess
        min_cards_needed = num_players * (goal_size + hand_size) + (MAX_CARDS_PER_PLAY_PILE + 1) * NUM_PLAY_PILES
        if num_decks * NUM_CARDS_PER_DECK < min_cards_needed:
            raise RuntimeError("Too few cards")

        # constants
        self.num_players = num_players
        self.num_decks = num_decks
        self.hand_size = hand_size
        self.goal_size = goal_size
        self.winner = None

        # Make a deck
        decks = make_decks(num_decks)

        #Deal!
        # list of lists of Cards
        self.goal_piles = [draw_N(decks, goal_size) for _ in range(num_players)]
        # list of lists of Cards
        self.player_hands = [draw_N(decks, hand_size) for _ in range(num_players)]
        # list of Cards
        self.goal_cards = [draw(pile) for pile in self.goal_piles]
        # list of lists of lists of Cards - top card is self.discard_piles[player_index][pile_index][-1]
        self.discard_piles = [[[] for _ in range(NUM_DISCARD_PILES)] for _ in range(num_players)]
        # list of lists of Cards
        self.play_piles = [[] for _ in range(NUM_PLAY_PILES)]
        # list of Cards
        self.draw_pile = decks
        self.current_player = 0

    def copy_mutable(self):
        '''
            Clone the game object, deep copying everything except the cards themselves
        '''
        clone = shallow_copy(self)

        # deep copy as mutable
        for attr, value in self.__dict__.items():
            if attr.startswith('__'):
                continue
            if isinstance(value, tuple):
                clone.__dict__[attr] = copy_nested(value)

        return clone

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

    def fill_hand(self):
        num_to_draw = self.hand_size - len(self.player_hands[self.current_player])
        self.player_hands[self.current_player] += draw_N(self.draw_pile, num_to_draw)

    def do_other_work(self):
        '''
            Do everything that isn't shared between Game and subclasses
        '''
        # shuffle full play piles back into deck
        for i in range(len(self.play_piles)):
            if len(self.play_piles[i]) == MAX_CARDS_PER_PLAY_PILE:
                self.draw_pile += self.play_piles[i]
                self.play_piles[i] = []

        # restock current player's hand
        if len(self.player_hands[self.current_player]) == 0:
            self.fill_hand()

        # check for winner, flip next goal card
        if self.goal_cards[self.current_player] is None \
                and len(self.goal_piles[self.current_player]) > 0:
            self.goal_cards[self.current_player] = draw(self.goal_piles[self.current_player])

        if len(self.goal_piles[self.current_player]) == 0:
            self.winner = self.current_player
    
    def _play_from_hand(self, card, play_pile_index):
        '''
            Play a card from the current player's hand onto a play pile
            Returns a new game state
        '''
        # validate the play
        if card not in self.player_hands[self.current_player]:
            raise RuntimeError("Can't play that card - it's not in your hand!")
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # Copy game
        new_game = self.copy_mutable()

        # Make the play
        new_game.play_piles[play_pile_index].append(card)
        new_game.player_hands[new_game.current_player].remove(card)

        # Update play piles, repopulate player's hand
        new_game.do_other_work()

        return new_game

    def _play_from_discard(self, discard_pile_index, play_pile_index):
        '''
            Play a card from one of the current player's discard piles
            Returns a new game state
        '''
        # validate the play
        if len(self.discard_piles[self.current_player][discard_pile_index]) == 0:
            raise RuntimeError("Can't play from an empty discard pile!")
        card = self.discard_piles[self.current_player][discard_pile_index][-1]
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # Copy game
        new_game = self.copy_mutable()

        # Make the play
        new_game.play_piles[play_pile_index].append(card)
        new_game.discard_piles[new_game.current_player][discard_pile_index].pop()

        # Update play piles
        new_game.do_other_work()

        return new_game

    def _play_from_goal(self, play_pile_index):
        '''
            Play the current player's goal card
            Returns a new game state
        '''
        # validate the play
        card = self.goal_cards[self.current_player]
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # Copy game
        new_game = self.copy_mutable()

        # Make the play
        new_game.play_piles[play_pile_index].append(card)
        new_game.goal_cards[new_game.current_player] = None
        
        # Check play piles, flip next goal card
        new_game.do_other_work()

        return new_game

    def _end_turn(self, card, discard_pile_index):
        '''
            End the current player's turn, discarding one card from their hand
            Returns a new game state
        '''
        # check the card is in their hand
        if card not in self.player_hands[self.current_player]:
            raise RuntimeError("Can't discard that card - it's not in your hand!")

        # Copy the game
        new_game = self.copy_mutable()
        
        # discard the card
        new_game.discard_piles[new_game.current_player][discard_pile_index].append(card)
        new_game.player_hands[new_game.current_player].remove(card)
        
        # Advance to the next player
        new_game.current_player = (new_game.current_player + 1) % new_game.num_players

        # Next player draws until their hand is full
        new_game.fill_hand()

        return new_game

    def do_move(self, move):
        '''
            Do a move supplied as a tuple (move_id, args)
            return the newly created Game
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")

        move_list = (self._play_from_goal, self._play_from_hand, self._play_from_discard, self._end_turn)
        return move_list[move.type](*move.args)
