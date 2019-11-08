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
    agent_types = [BasicAgent, RandomAgent]
    gamerunners = []

    for _ in range(args.num_games):
        agents = [agent() for agent in agent_types]
        game = Game(goal_size=10)
        #game = rig_game(game, 0)
        game = GameRunner(game, agents, verbose=True)
        winner = game.play()
        gamerunners.append(game)
    
    agent_scores = [0, 0]
    agent_move_times = [[], []]
    agent_longest_move_time = [0, 0]
    for game in gamerunners:
        agent_scores[game.game.winner] += 1
        longest = game.get_longest_move_times()
        for agent_id in range(len(agent_types)):
            agent_move_times[agent_id] += game.agent_move_times[agent_id]
            if longest[agent_id] > agent_longest_move_time[agent_id]:
                agent_longest_move_time[agent_id] = longest[agent_id]

    print('Scores:')
    for i, agent_type, agent_score in zip(range(len(agent_types)), agent_types, agent_scores):
        agent = agent_type()
        print('  {} - {}: {}'.format(i, agent.name, agent_score))
        print('    avg move time: {}'.format(sum(agent_move_times[i])/len(agent_move_times[i])))
        print('    longest move time: {}'.format(agent_longest_move_time[i]))

if __name__=='__main__':
    main()
