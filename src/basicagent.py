import random
from hiddengame import *
from game import *
from move import *
from cards import *

def rig_game(game, agent_id):
    '''
        Rig a game for testing stuff
    '''
    game.goal_cards[agent_id] = Card(9, "Spades")
    game.player_hands[agent_id] = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Hearts"), Card(4, "Clubs")]
    return game

class BasicAgent:
    '''
        A simple autonomous agent
    '''
    def __init__(self):
        # path to blindly follow (in reverse order, i.e. pop() each element)
        self.path = []

    def get_child_states(self, hg, allowed_moves):
        '''
            Given a HiddenGame, get all possible states made by playing
            from the hand or from the discard piles
            Return a list of tuples (move, HiddenGame)
            Where move = (move_type, args)
        '''
        states = []
        legal_moves = hg.get_legal_moves()
        for move_type in allowed_moves:
            for move in legal_moves[move_type]:
                new_hg = hg.do_move(move)
                states.append(new_hg)
        return states

    def find_path(self, hg, is_goal_state):
        '''
            Search to find if there's a guaranteed path to get to a state defined by the function is_goal_state
            Return path of states in reverse order
        '''
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL]

        queue = [[hg]]
        seen = set([hg])
        goal_path = None

        while len(queue) > 0:

            path = queue.pop()
            if is_goal_state(path[-1]):
                goal_path = path
                break

            for child_state in self.get_child_states(path[-1], allowed_moves=child_moves):
                if child_state in seen:
                    continue
                seen.add(child_state)
                new_path = path[:] + [child_state]
                queue.append(new_path)

        if goal_path is None:
            return None

        # get the moves from the states
        path = [state.last_move for state in goal_path]
        # pop empty move, and reverse for later consumption
        path.pop(0)
        path.reverse()
        return path

    def find_path_to_goal(self, hg):
        goal_func = lambda state: True if state.last_move.type == MOVE_PLAY_GOAL else False
        return self.find_path(hg, goal_func)

    def find_path_to_empty_hand(self, hg):
        goal_func = lambda state: True if len(state.player_hands[state.current_player]) == 0 else False
        return self.find_path(hg, goal_func)

    def score_player_cards(self, hg):
        '''
            Compute a score in the range (0,8] of how valuable a players immediately playable cards are
            Immediately playable cards are cards in the hand and discard pile
            A score of 8 is a run of 8 cards up to the current goal card
            A score close to 0 means most of the cards aren't near the goal card
        '''
        goal_card = hg.goal_cards[hg.current_player]
        if goal_card.is_wild():
            return 8
        player_hand = hg.player_hands[hg.current_player]
        top_discard_cards = [pile[-1] for pile in hg.discard_piles[hg.current_player] if len(pile)]

        playable_cards = []
        playable_cards += player_hand
        playable_cards += top_discard_cards
        # remove wildcards and count them up
        num_wild = 0
        for card in playable_cards:
            if card.is_wild():
                playable_cards.remove(card)
                num_wild += 1
        # note that making this a set removes duplicates too
        playable_card_values = set([card.value for card in playable_cards])

        score = 0
        # this is the score that gets added as we count down from the goal card
        curr_max_score = 1
        # this value will decrease
        curr_value = (goal_card.value + MAX_CARDS_PER_PLAY_PILE - 1) % MAX_CARDS_PER_PLAY_PILE
        # count down until all possible card values are encountered
        for _ in range(MAX_CARDS_PER_PLAY_PILE):
            if curr_value in playable_card_values:
                score += curr_max_score
                playable_card_values.remove(curr_value)
            elif num_wild > 0:
                # fill in gaps with wild cards
                score += curr_max_score
                num_wild -= 1
            else:
                # there's a gap in the run, so futher cards can only be half as valuable
                curr_max_score /= 2
            curr_value = (curr_value + MAX_CARDS_PER_PLAY_PILE - 1) % MAX_CARDS_PER_PLAY_PILE
        return score
    
    def random_move(self, hg):
        legal_moves = hg.get_legal_moves()
        all_moves = []
        for moves in legal_moves:
            for move in moves:
                all_moves.append(move)
        return all_moves[random.randrange(len(all_moves))]

    def get_move(self, hidden_game):

        if len(self.path) > 0:
            return self.path.pop()

        # try to play a goal card at all costs
        self.path = self.find_path_to_goal(hidden_game)
        if self.path is not None:
            return self.path.pop()

        # if no guaranteed goal path, try to empty hand
        self.path = self.find_path_to_empty_hand(hidden_game):
        if self.path is not None:
            return self.path.pop()

        # if can block another player, (play cards until they're blocked)
        #if can_block(self, hidden_game):
        #    return self.path.pop(0)

        move = self.random_move(hidden_game)
        return move


