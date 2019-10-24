from hiddengame import *
from game import *
from cards import *

def rig_game(game, agent_id):
    '''
        Rig a game for testing stuff
    '''
    game.goal_cards[agent_id] = Card(3, "Spades")
    game.player_hands[agent_id] = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Hearts"), Card(9, "Clubs")]
    return game

class BasicAgent:
    '''
        A simple autonomous agent
    '''
    def __init__(self):
        # path to blindly follow (in reverse order, i.e. pop() each element)
        self.path = []

    def get_child_states(self, hg):
        '''
            Given a HiddenGame, get all possible states made by playing
            from the hand or from the discard piles
            Return a list of tuples (move, HiddenGame)
            Where move = (move_type, args)
        '''
        states = []
        legal_moves = hg.get_legal_moves()
        #print("hg play piles:",hg.play_piles)
        #print("hg player hand:",hg.player_hand)
        #print("hg legal moves:",len(legal_moves[MOVE_PLAY_HAND]))
        for move_type in [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL]:
            for args in legal_moves[move_type]:
                #print(hg.move_repr(move_type, args))
                new_hg = hg.do_move(move_type, args)
                states.append(((move_type, args), new_hg))
        #print([hg.move_repr(*state[0]) for state in states])
        return states

    def can_play_goal(self, hg):
        '''
            Search to find if there's a guaranteed path to play a goal card
            Store goal path in self.goal_path [(move_type, args), ...]
            Return true or false
        '''
        if len(self.path) > 0:
            return True

        queue = [((None, None), hg)]
        map_back = {queue[0]: None}
        goal_state = None

        while len(queue) > 0:
            state = queue.pop()
            #print([state[1].move_repr(*state[0]) for state in queue])
            # if we can play the goal card, we're done
            if state[0][0] == MOVE_PLAY_GOAL:
                goal_state = state
                break

            for child_state in self.get_child_states(state[1]):
                #print(child_state[1].play_piles)
                if child_state in map_back:
                    continue
                map_back[child_state] = state
                queue.append(child_state)

        if goal_state is None:
            return False
        
        while goal_state is not None:
            self.path.append(goal_state[0])
            goal_state = map_back[goal_state]

        # pop current state (None, None)
        self.path.pop()
        return True
    
    def random_move(self, hg):
        legal_moves = hg.get_legal_moves()
        all_moves = []
        for i, moves in zip(range(len(legal_moves)), legal_moves):
            for args in moves:
                all_moves.append((i, args))
        return all_moves[random.randrange(len(all_moves))]

    def get_move(self, hidden_game):

        # try to play a goal card at all costs
        if self.can_play_goal(hidden_game):
            move = self.path.pop()
            print(move)
            return move

        # if no guaranteed goal path, try to empty hand
        #if can_empty_hand(self, hidden_game):
        #    return self.path.pop()

        # if can block another player, (play cards until they're blocked)
        #if can_block(self, hidden_game):
        #    return self.path.pop(0)

        move = self.random_move(hidden_game)
        print(move)
        return move


