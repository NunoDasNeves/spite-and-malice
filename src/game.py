import random
from copy import copy as shallow_copy
from cards import Card, draw, draw_N, make_decks, NUM_CARDS_PER_DECK

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

        # functions for generically doing moves
        self.move_list = (self.play_from_goal, self.play_from_hand, self.play_from_discard, self.end_turn)

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

    def copy(self):
        '''
            Clone the game object, deep copying everything except the cards themselves
        '''
        clone = shallow_copy(self)
        clone.goal_piles = [pile[:] for pile in self.goal_piles]
        clone.player_hands = [hand[:] for hand in self.player_hands]
        clone.goal_cards = self.goal_cards[:]
        clone.discard_piles = [[pile[:] for pile in piles] for piles in self.discard_piles]
        clone.play_piles = [pile[:] for pile in self.play_piles]
        clone.draw_pile = self.draw_pile[:]
        clone.move_list = (clone.play_from_goal, clone.play_from_hand, clone.play_from_discard, clone.end_turn)
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

    def check_play_pile(self, play_pile_index):
        if len(self.play_piles[play_pile_index]) == MAX_CARDS_PER_PLAY_PILE:
            self.draw_pile += self.play_piles[play_pile_index]
            self.play_piles[play_pile_index] = []

    def get_play_pile_values(self):
        return [len(pile) for pile in self.play_piles]

    def play_from_hand(self, card, play_pile_index):
        '''
            Play a card from the current player's hand onto a play pile
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")
        # validate the play
        if card not in self.player_hands[self.current_player]:
            raise RuntimeError("Can't play that card - it's not in your hand!")
        if not self.is_valid_play(card, play_pile_index):
            raise RuntimeError("Invalid play! {} on top of {}".format(card, self.play_piles[play_pile_index]))

        # copy the game
        game = self.copy()
        # make the play
        game.player_hands[game.current_player].remove(card)
        game.play_piles[play_pile_index].append(card)
        # check the pile to see if it's done
        game.check_play_pile(play_pile_index)
        # if player's hand is empty, draw another hand of cards
        if len(game.player_hands[game.current_player]) == 0:
            game.player_hands[game.current_player] = draw_N(game.draw_pile, game.hand_size)
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
        game = self.copy()
        # make the play
        game.discard_piles[self.current_player][discard_pile_index].pop()
        game.play_piles[play_pile_index].append(card)
        # check the pile to see if it's done
        game.check_play_pile(play_pile_index)
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
        game = self.copy()
        # make the play
        game.play_piles[play_pile_index].append(card)
        if len(game.goal_piles[game.current_player]) > 0:
            game.goal_cards[game.current_player] = draw(game.goal_piles[game.current_player])
            # check the pile to see if it's done
            game.check_play_pile(play_pile_index)
        else:
            # if the goal pile is empty, the current player won!
            game.winner = game.current_player
        return game

    def end_turn(self, card, discard_pile_index):
        '''
            End the current player's turn, discarding one card from their hand
            Returns a new game state
        '''
        if self.winner is not None:
            raise RuntimeError("Game is over!")
        # check the card is in their hand
        if card not in self.player_hands[self.current_player]:
            raise RuntimeError("Can't discard that card - it's not in your hand!")

        # copy the game
        game = self.copy()
        # discard the card
        game.player_hands[game.current_player].remove(card)
        game.discard_piles[game.current_player][discard_pile_index].append(card)
        # Advance to the next player
        game.current_player = (game.current_player + 1) % game.num_players
        # Have them draw until their hand is full
        num_to_draw = game.hand_size - len(game.player_hands[game.current_player])
        game.player_hands[game.current_player] += draw_N(game.draw_pile, num_to_draw)
        return game

    def do_move(self, move, args):
        '''
            Do a move supplied as a tuple (move_id, args)
            return the newly created Game
        '''
        return self.move_list[move](*args)
