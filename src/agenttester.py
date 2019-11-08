#!/usr/bin/env python3
import random, argparse

from game import Game
from humanagent import HumanAgent
from basicagent import BasicAgent, rig_game
from randomagent import RandomAgent
from gamerunner import GameRunner

def main():

    random.seed(None)
    
    parser = argparse.ArgumentParser(description="Run batches of games to test agents")
    parser.add_argument('-n', '--num-games', type=int, default=1, dest='num_games', help='number of games')
    args = parser.parse_args()
    agent_scores = [0, 0]
    agent_types = [BasicAgent, RandomAgent]

    for _ in range(args.num_games):
        agents = [agent() for agent in agent_types]
        game = Game(goal_size=10)
        #game = rig_game(game, 0)
        game = GameRunner(game, agents, verbose=False)
        winner = game.play()
        agent_scores[winner] += 1
    
    print('Scores:')
    for i, agent_type, agent_score in zip(range(len(agent_types)), agent_types, agent_scores):
        agent = agent_type()
        print('  {} - {}: {}'.format(i, agent.name, agent_score))

if __name__=='__main__':
    main()
