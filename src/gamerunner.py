from hiddengame import HiddenGame
import time

class GameRunner:
    '''
        Class for running and collecting information about a Game
    '''
    def __init__(self, game, agents, verbose=True):
        if game.num_players != len(agents):
            raise RuntimeError("Wrong number of agents!")
        self.game = game
        self.agents = agents
        self.verbose = verbose
        self.agent_move_times = [[] for _ in agents]
    
    def v_print(self, string):
        if self.verbose:
            print(string)

    def get_avg_move_times(self):
        return [sum(times)/len(times) for time in self.agent_move_times]

    def get_longest_move_times(self):
        return [max(times) for times in self.agent_move_times]

    def play(self):
        while True:
            # get the current agent, and ask it what move it wants to do
            agent = self.agents[self.game.current_player]
            hg = HiddenGame(self.game)

            start_time = time.perf_counter()
            # Do the move
            move = agent.get_move(hg)
            # record how long it took
            self.agent_move_times[self.game.current_player].append(time.perf_counter() - start_time)

            self.v_print("Player {} => {}".format(self.game.current_player, move.repr(hg)))
            self.v_print("=========================================================")
            # now actually do the move
            self.game = self.game.do_move(move)
            # stop as soon as there is a winner
            if self.game.winner is not None:
                self.v_print ("Player {} won the game!".format(self.game.current_player))
                return self.game.winner
            #sleep(0.5)