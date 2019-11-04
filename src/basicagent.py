import random, time
from hiddengame import *
from game import *
from move import *
from cards import *

def rig_game(game, agent_id):
    '''
        Rig a game for testing stuff
    '''
    game.goal_cards[agent_id] = Card(9, "Spades")
    game.player_hands[agent_id] = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Hearts"), Card(4, "Clubs")]
    return game

class BasicAgent:
    '''
        A simple autonomous agent
    '''
    def __init__(self):
        # path to blindly follow (in reverse order, i.e. pop() each element)
        self.path = []

    def get_child_states(self, hg, allowed_moves, coalesce=True):
        '''
            Given a HiddenGame, get all possible states made by playing
            from the hand or from the discard piles
            Return a list of tuples (move, HiddenGame)
            Where move = (move_type, args)
        '''
        states = []
        legal_moves = hg.get_legal_moves()

        if coalesce:
            legal_moves = list(legal_moves)
            for move_type in allowed_moves:
                if move_type == MOVE_END_TURN:
                    buckets = {}
                    # each bucket contains moves that are different but actually equivalent
                    # bucket key is a tuple of (card_value, discard_pile)
                    discard_piles = hg.discard_piles[hg.current_player]
                    for move in legal_moves[move_type]:
                        card = move.args[0]
                        pile = discard_piles[move.args[1]]
                        # TODO this doesn't work in all cases because king's value != joker's value
                        bucket_key = (card.value, pile)
                        buckets[bucket_key] = move
                        #if bucket_key in buckets:
                        #    buckets[bucket_key].append(move)
                        #else:
                        #    buckets[bucket_key] = [move]

                    legal_moves[move_type] = buckets.values()
                # TODO more coalescing. MOVE_END_TURN is the biggest offender however
                #legal_moves[move_type] = [bucket[0] for bucket in buckets.values()]
                '''
                for key, bucket in buckets.items():
                    print(key)
                    for move in bucket:
                        print(" ",move.repr(hg))
                '''

            legal_moves = tuple(legal_moves)

        for move_type in allowed_moves:
            for move in legal_moves[move_type]:
                new_hg = hg.do_move(move)
                states.append(new_hg)
        
        return states

    def find_path(self, hg, is_goal_state):
        '''
            Search to find if there's a guaranteed path to get to a state defined by the function is_goal_state
            Return path of states in reverse order
        '''
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL]

        queue = [[hg]]
        seen = set([hg])
        goal_path = None

        while len(queue) > 0:

            path = queue.pop()
            if is_goal_state(path[-1]):
                goal_path = path
                break

            for child_state in self.get_child_states(path[-1], allowed_moves=child_moves):
                if child_state in seen:
                    continue
                seen.add(child_state)
                new_path = path[:] + [child_state]
                queue.append(new_path)

        if goal_path is None:
            return None

        # get the moves from the states
        path = [state.last_move for state in goal_path]
        # pop empty move, and reverse for later consumption
        path.pop(0)
        path.reverse()
        return path

    def find_path_to_goal(self, hg):
        goal_func = lambda state: True if state.last_move.type == MOVE_PLAY_GOAL else False
        return self.find_path(hg, goal_func)

    def find_path_to_empty_hand(self, hg):
        goal_func = lambda state: True if len(state.player_hands[state.current_player]) == 0 else False
        return self.find_path(hg, goal_func)

    def score_player_cards(self, hg):
        '''
            Compute a score in the range (0,8] of how valuable a players immediately playable cards are
            Immediately playable cards are cards in the hand and discard pile
            A score of 8 is a run of 8 cards up to the current goal card
            A score close to 0 means most of the cards aren't near the goal card
            Return normalized score between 0 and 1
        '''
        MAX_SCORE = hg.hand_size + NUM_DISCARD_PILES
        goal_card = hg.goal_cards[hg.current_player]
        # treat wild goal card as max score
        # (TODO maybe make this higher? or something... range of 0-12 with this being 12?)
        if goal_card.is_wild():
            return MAX_SCORE
        player_hand = hg.player_hands[hg.current_player]
        top_discard_cards = [pile[-1] for pile in hg.discard_piles[hg.current_player] if len(pile)]

        playable_cards = []
        playable_cards += player_hand
        playable_cards += top_discard_cards
        # remove wildcards and count them up
        num_wild = 0
        for card in playable_cards:
            if card.is_wild():
                playable_cards.remove(card)
                num_wild += 1
        # note that making this a set removes duplicates too
        playable_card_values = set([card.value for card in playable_cards])

        score = 0
        # this is the score that gets added as we count down from the goal card
        curr_max_score = 1
        # this value will decrease
        curr_value = (goal_card.value + MAX_CARDS_PER_PLAY_PILE - 1) % MAX_CARDS_PER_PLAY_PILE
        # count down until all possible card values are encountered
        for _ in range(MAX_CARDS_PER_PLAY_PILE):
            if curr_value in playable_card_values:
                score += curr_max_score
                playable_card_values.remove(curr_value)
            elif num_wild > 0:
                # fill in gaps with wild cards
                score += curr_max_score
                num_wild -= 1
            else:
                # there's a gap in the run, so futher cards can only be half as valuable
                curr_max_score /= 2
            curr_value = (curr_value + MAX_CARDS_PER_PLAY_PILE - 1) % MAX_CARDS_PER_PLAY_PILE
        # normalize
        return score/MAX_SCORE

    def score_state(self, hg, player_id):
        '''
            Determine how valuable a state is for player_id
            This has a lot of room for improvement
            Assumes current player can't empty their hand or play their goal card this turn
            Return a score between 0 and 1
        '''
        # score our cards
        new_hg = hg.copy_mutable()
        new_hg.current_player = player_id
        new_hg.make_immutable()
        hand_score = self.score_player_cards(new_hg)

        # this will contain numbers 0 - 5 representing how close another player is to playing
        # their goal card (0 is they can play it NOW, 5 is they can't play it even if holding 4 wilds)
        MAX_DANGER = 1 # hg.hand_size + 1
        other_players_danger = [0 for _ in range(hg.num_players)]

        #start = time.perf_counter()
        
        # score other player's hands based on what we can see
        for player_id in range(hg.num_players):
            if player_id == hg.current_player:
                continue
            # add up to hand_size wild cards to enemy player's hand
            # determine how dangerous they are based on how many must be added for them to
            # be able to play their goal card
            new_hg = hg.copy_mutable()
            new_hg.current_player = player_id
            for num_wilds in range(MAX_DANGER):
                new_hg.player_hands[player_id] = [Card(14, "")] * num_wilds
                immut_hg = new_hg.copy_mutable()
                immut_hg.make_immutable()
                if self.find_path_to_goal(immut_hg) is not None:
                    other_players_danger[player_id] = num_wilds
                    break

        #print(time.perf_counter() - start)
        
        # normalize the dangers
        other_players_danger = [d/MAX_DANGER for d in other_players_danger]
        # TODO modulate the danger of opposing players by the size of their goal pile
        # higher pile means it's less dangerous (a little) to let them play
        all_scores = other_players_danger
        all_scores[hg.current_player] = hand_score
        return sum([score/len(all_scores) for score in all_scores])

    def do_generic_moves(self, hg):
        '''
            In the likely event we can't play the goal card on this turn, or empty our hand for
            another shot at the goal, we need to strategically cycle cards out of our hand.
        '''
        # Some thoughts
        # 1. predict cards in other players' hands (or what they will be holding/have available)
        # take into account:
        #   cards they'll draw from the draw pile
        #   what they're already holding: e.g.
        #       - holding onto cards means can't play or saving for goal
        #       - close to goal but didn't play goal means don't have X card on path to goal
        #       - in general, holding onto cards means cards further from play piles (likely)
        #   cards they'll uncover in their goal pile
        # 2. assume other players will play their goal if possible
        # 3. run a minimax algorithm to simulate what might happen, and make decisions based off of that
        # But there is a fair bit of hidden information and lots of heuristics involved in predicting what
        # other players may be holding...
        # 
        # More simply just assume players have a 'range' of 1 or 2, i.e. subtract 1 or 2 from their goal card
        # i.e. each player has actually 3 cards: goal, goal-1, goal-2
        # (the agent can compute their own range by counting back from the goal card playable cards...)
        # now assume others use their discard piles and their range to play the goal if possible
        #
        # So we want to make plays that:
        #   don't put others within range of their goals
        #   don't reduce own range (take into account discarding at end of turn)
        # And secondarily:
        #   play as many cards as possible (to free discard space & cycle the draw pile


        # Search for the best path
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL, MOVE_END_TURN]
        # enumerate all paths that terminate in MOVE_END_TURN
        # queue of paths, not just states
        queue = [[hg]]
        seen = set([hg])
        best_path = None
        best_score = 0

        iters = 0

        while len(queue) > 0:

            iters += 1
            if iters % 100 == 0:
                print (iters)

            path = queue.pop()
            if path[-1].last_move.type == MOVE_END_TURN:
                if best_path is None:
                    best_path = path
                else:
                    # score the last state to evaluate which path to keep
                    score = self.score_state(path[-1], hg.current_player)
                    if score > best_score:
                        best_path = path
                        best_score = score
                continue

            for child_state in self.get_child_states(path[-1], child_moves):
                if child_state in seen:
                    continue
                seen.add(child_state)
                new_path = path[:] + [child_state]
                queue.append(new_path)

        path = [state.last_move for state in best_path]
        path.pop(0)
        path.reverse()

        return path

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

        # this always returns a path
        self.path = self.do_generic_moves(hidden_game)
        return self.path.pop()
