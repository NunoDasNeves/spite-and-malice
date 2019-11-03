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
            Search to find if there's a guaranteed path to play a goal card
            Store goal path in self.goal_path [(move_type, args), ...]
            Return true or false
        '''
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL]

        queue = [hg]
        map_back = {queue[0]: None}
        goal_state = None

        while len(queue) > 0:
            state = queue.pop()
            # if we can play the goal card, we're done
            if is_goal_state(state):
                goal_state = state
                break

            for child_state in self.get_child_states(state, allowed_moves=child_moves):
                if child_state in map_back:
                    continue
                map_back[child_state] = state
                queue.append(child_state)

        if goal_state is None:
            return None

        path = []
        
        while goal_state is not None:
            path.append(goal_state.last_move)
            goal_state = map_back[goal_state]

        # pop current move (None, None)
        path.pop()
        return path

    def find_path_to_goal(self, hg):
        goal_func = lambda state: True if state.last_move.type == MOVE_PLAY_GOAL else False
        return self.find_path(hg, goal_func)

    def find_path_to_empty_hand(self, hg):
        goal_func = lambda state: True if len(state.player_hands[state.current_player]) == 0 else False
        return self.find_path(hg, goal_func)
    
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


