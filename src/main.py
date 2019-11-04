#!/usr/bin/env python3
from game import Game
from hiddengame import HiddenGame
from humanagent import HumanAgent
from basicagent import BasicAgent, rig_game
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
            print("Player {} => {}".format(self.game.current_player, move.repr(hg)))
            print("=========================================================")
            # now actually do the move
            self.game = self.game.do_move(move)
            # stop as soon as there is a winner
            if self.game.winner is not None:
                print ("Player {} won the game!".format(self.game.current_player))
                return self.game.winner
            #sleep(0.5)

def main():
    human_agent = HumanAgent()
    basic_agent = BasicAgent()
    game = Game(goal_size=8)
    #game = rig_game(game, 0)
    game = GameRunner(game, [basic_agent, basic_agent])
    game.play()

if __name__=='__main__':
    main()
