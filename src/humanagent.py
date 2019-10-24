from hiddengame import HiddenGame, MOVE_TYPES

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
        print("The tops of the play piles are: ")
        for play_pile in hidden_game.play_piles:
            if len(play_pile) == 0:
                print("  None")
            elif play_pile[-1].is_wild():
                print(" ", play_pile[-1], "({})".format(len(play_pile)))
            else:
                print(" ", play_pile[-1])

        chosen_move_type = None
        chosen_move_args = None
        while chosen_move_type is None:

            print("Choose a type of move: ")
            for i, moves in zip(range(len(legal_moves)), legal_moves):
                if len(moves) > 0:
                    print("  {}. {}".format(i, MOVE_TYPES[i]))
                else:
                    print("  {}. << Can't do this right now >>".format(i))

            print("(0-{}): ".format(len(legal_moves)-1), end="")
            move_type = int(input())
            move_list = legal_moves[move_type]
            if move_type not in range(len(legal_moves)) or len(move_list) == 0:
                print("Can't do that!")
                continue

            print("Okay, which move?")
            for i, args in zip(range(len(move_list)), move_list):
                print("  {}. {}".format(i, hidden_game.move_repr(move_type, args)))
            print("  b. Go back")

            print("(0-{},b): ".format(len(move_list)-1), end="")
            choice = input()
            if choice == "b":
                continue

            move_choice = int(choice)
            if move_choice not in range(len(move_list)):
                print("Can't do that!")
                continue
            chosen_move_type = move_type
            chosen_move_args = move_list[move_choice]

        return chosen_move_type, chosen_move_args


