import random
from basicagent import BasicAgent

class RandomAgent(BasicAgent):
    '''
        A simple autonomous agent
    '''

    def random_move(self, hg):
        '''
            Not used anymore but good as a baseline heh
        '''
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
        self.path = self.find_path_to_empty_hand(hidden_game)
        if self.path is not None:
            return self.path.pop()

        self.path = [self.random_move(hidden_game)]
        return self.path.pop()

