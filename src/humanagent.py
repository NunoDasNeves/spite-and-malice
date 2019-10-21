from hiddengame import HiddenGame

class HumanAgent:
    '''
        An agent controllable with the keyboard
    '''
    def __init__(self):
        pass

    def get_move(self, hidden_game):

        legal_moves = hidden_game.get_legal_moves()
        player = hidden_game.current_player

        print("You are Player {}".format(player))
        print("Your topmost goal card is: {}".format(hidden_game.goal_cards[player]))
        print("You are holding: \n{}".format(hidden_game.player_hand))
        print("Your discard piles: \n{}".format(hidden_game.discard_piles[player]))
        for other_player in range(hidden_game.num_players):
            if other_player == player:
                continue
            print("Player {}'s goal card is: {}".format(other_player,
                hidden_game.goal_cards[other_player]))
            print("Player {}'s discard piles are: \n{}".format(other_player,
                hidden_game.discard_piles[other_player]))
        print("Which move do you want to do?")
        for i, move in zip(range(len(legal_moves)), legal_moves):
            print("  {}. {}".format(i, hidden_game.move_repr(move)))

        choice = int(input())
        return legal_moves[choice]


