from game import Game
from hiddengame import HiddenGame
from humanagent import HumanAgent
from time import sleep

class GameRunner:
    def __init__(self, game, agents):
        if game.num_players != len(agents):
            raise RuntimeError("Wrong number of agents!")
        self.game = game
        self.agents = agents

    def play(self):
        while True:
            # get the current agent, and ask it what move it wants to do
            agent = self.agents[self.game.current_player]
            hg = HiddenGame(self.game)
            move = agent.get_move(hg)
            print("Player {} => {}".format(self.game.current_player, hg.move_repr(move)))
            print("=========================================================")
            # now actually do the move
            self.game = self.game.do_move(move)
            # stop as soon as there is a winner
            if self.game.winner is not None:
                return self.game.winner
            sleep(1)

def main():
    human_agent = HumanAgent()
    game = GameRunner(Game(), [human_agent, human_agent])
    game.play()

if __name__=='__main__':
    main()
