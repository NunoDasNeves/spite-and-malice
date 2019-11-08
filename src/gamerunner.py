from hiddengame import HiddenGame

class GameRunner:
    def __init__(self, game, agents, verbose=True):
        if game.num_players != len(agents):
            raise RuntimeError("Wrong number of agents!")
        self.game = game
        self.agents = agents
        self.verbose = verbose
    
    def v_print(self, string):
        if self.verbose:
            print(string)

    def play(self):
        while True:
            # get the current agent, and ask it what move it wants to do
            agent = self.agents[self.game.current_player]
            hg = HiddenGame(self.game)
            move = agent.get_move(hg)
            self.v_print("Player {} => {}".format(self.game.current_player, move.repr(hg)))
            self.v_print("=========================================================")
            # now actually do the move
            self.game = self.game.do_move(move)
            # stop as soon as there is a winner
            if self.game.winner is not None:
                self.v_print ("Player {} won the game!".format(self.game.current_player))
                return self.game.winner
            #sleep(0.5)