#!/usr/bin/env python3
import random

from game import Game
from humanagent import HumanAgent
from basicagent import BasicAgent, rig_game
from randomagent import RandomAgent
from gamerunner import GameRunner

def main():
    random.seed(None)
    human_agent = HumanAgent()
    basic_agent = BasicAgent()
    random_agent = RandomAgent()
    game = Game(goal_size=8)
    #game = rig_game(game, 0)
    game = GameRunner(game, [basic_agent, random_agent])
    game.play()

if __name__=='__main__':
    main()
