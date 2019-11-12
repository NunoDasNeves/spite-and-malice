import random, time
from hiddengame import *
from game import *
from move import *
from cards import *

def rig_game(game, agent_id):
    '''
        Rig a game for testing stuff
    '''
    game.goal_cards[agent_id] = Card(5, "Spades")
    game.player_hands[agent_id] = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Hearts"), Card(4, "Clubs")]
    return game

class BasicAgent:
    '''
        A simple autonomous agent
    '''
    def __init__(self):
        # path to blindly follow (in reverse order, i.e. pop() each element)
        self.path = []
        self.name = 'BasicAgent'

    def get_child_states(self, hg, allowed_moves, coalesce=True):
        '''
            Given a HiddenGame, get all possible states made by playing the allowed_moves types
            Return a tuple of HiddenGames
        '''
        states = []
        legal_moves = hg.get_legal_moves()

        if coalesce:
            legal_moves = list(legal_moves)
            for move_type in allowed_moves:
                # each bucket contains moves that are different but actually equivalent
                # bucket key is a tuple of:
                #   (MOVE_PLAY_GOAL, card_value, len(play_pile))
                #   (MOVE_PLAY_HAND, card_value, len(play_pile))
                #   (MOVE_PLAY_DISCARD, discard_pile, len(play_pile))
                #   (MOVE_END_TURN, card_value, discard_pile)
                buckets = {}
                for move in legal_moves[move_type]:

                    bucket_key = None

                    if move_type == MOVE_PLAY_GOAL:
                        card = hg.goal_cards[hg.current_player]
                        play_pile = hg.play_piles[move.args[0]]
                        bucket_key = (MOVE_PLAY_GOAL, card.value, len(play_pile))

                    elif move_type == MOVE_PLAY_HAND:
                        play_pile = hg.play_piles[move.args[1]]
                        bucket_key = (MOVE_PLAY_HAND, move.args[0].value, len(play_pile))

                    elif move_type == MOVE_PLAY_DISCARD:
                        discard_pile = hg.discard_piles[hg.current_player][move.args[0]]
                        play_pile = hg.play_piles[move.args[1]]
                        bucket_key = (MOVE_PLAY_DISCARD, discard_pile, len(play_pile))

                    elif move_type == MOVE_END_TURN:
                        discard_piles = hg.discard_piles[hg.current_player]
                        card = move.args[0]
                        pile = discard_piles[move.args[1]]
                        # TODO this doesn't work in all cases because king's value != joker's value
                        bucket_key = (MOVE_END_TURN, card.value, pile)

                    else:
                        raise RuntimeError("Invalid move type!")

                    buckets[bucket_key] = move

                legal_moves[move_type] = buckets.values()

            legal_moves = tuple(legal_moves)

        for move_type in allowed_moves:
            for move in legal_moves[move_type]:
                new_hg = hg.do_move(move)
                states.append(new_hg)
        
        return states

    def path_cost(self, path):
        '''
            Used in find_path
            'Cost' of a path is simple for now; 1 per move
            TODO: Slightly disincentivises playing wildcards, saving them for later plays
        '''
        total = 0
        # first state is always the current hg with last_move=None, don't include it
        #for state in path[1:]:
        #    if state.last_move.type == MOVE_PLAY_HAND and state.last_move.args[0].is_wild():
        #        total += 1
        #    else:
        #        total += 1
        return len(path) - 1
        return total

    def find_path(self, hg, is_goal_state, heuristic):
        '''
            A* search to find if there's a guaranteed path to get to a state defined by the function is_goal_state
            is_goal_state(state) returns true if state is a goal state
            heuristic(state) returns an estimate of the minimum distance to the goal
            Return path of states in reverse order
        '''
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL]

        queue = [[hg]]
        seen = set([hg])
        goal_path = None
        # function for sorting paths in the queue
        f = lambda path: self.path_cost(path) + heuristic(path[-1])

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

            # we pop from the end, so must reverse the queue
            queue.sort(key=f, reverse=True)

        if goal_path is None:
            return None

        # get the moves from the states
        path = [state.last_move for state in goal_path]
        # pop empty move, and reverse for later consumption
        path.pop(0)
        path.reverse()
        return path

    def min_dist_to_play_pile(self, hg, card):
        '''
            Return minimum distance in moves from the top of a play pile in hg to a given card
            Include the move of putting the card on the pile
            e.g. a play pile of length 2 and a card of value 4 are a distance 2 moves away
        '''
        if card.is_wild():
            return 1
        pile_diffs = [(card.value - 1 - len(pile) + MAX_CARDS_PER_PLAY_PILE) % MAX_CARDS_PER_PLAY_PILE for pile in hg.play_piles]
        return min(pile_diffs)

    def find_path_to_goal(self, hg):
        '''
            Find and return a path to the goal card, or None if it's not possible
            TODO:
            IDEA: Using a simple A* runs into problems with a massive search space in cases where
            it's not possible to play the goal card but there are many possible plays
            So, we determine the sequence of cards directly prior to the goal which must be in the
            discard pile/player's hand.
            E.g. if goal is 5, then 4 (or a wild card) must be in the playable cards (or be on top of a play pile)
            E.g. if 4 or a wild card exists, then 3 must exist in playable cards (or be on top of a play pile)
                etc, until we have a list of cards that must go ontop of a given play pile for the goal to be possible 
            We can use this as a better metric to determine if find_path will succeed
            IDEA: Extending this idea, we can search for the lowest card in that sequence, then search for the next etc
            until the goal is achieved.
            This should be much more efficient than a blind A* search in cases where there IS a path
            IDEA: the play pile closest to the goal card will always be the one the goal card is played on (check this)
        '''

        goal_card = hg.goal_cards[hg.current_player]

        if goal_card.is_wild():
            # TODO: maximize options after playing wild goal card instead of just being dumb here
            return [Move(MOVE_PLAY_GOAL, (0,))]

        # TODO make this find the path also; for now it just improves find_path

        # get playable card values
        playable_cards = list(hg.player_hands[hg.current_player])
        playable_cards += [card for pile in hg.discard_piles[hg.current_player] for card in pile]
        playable_card_values = [card.value for card in playable_cards]

        min_dist = self.min_dist_to_play_pile(hg, goal_card)

        # if min_dist == 2 then we want to only check 1 previous card, so -1 here: 
        for i in range(1, min_dist - 1):
            curr_value = (goal_card.value - i + MAX_CARDS_PER_PLAY_PILE) % MAX_CARDS_PER_PLAY_PILE
            # is the previous card (potentially) playable this turn?
            if curr_value in playable_card_values:
                # Remove from the list
                playable_card_values.remove(curr_value)
                continue

            # check if there's a wildcard that may be of service instead
            wild_val = None
            for val in playable_card_values:
                if val in WILD_VALUES:
                    wild_val = val
                    break
            if wild_val is None:
                return None
            else:
                playable_card_values.remove(wild_val)

        # Now we know at least that all the cards exist to make it to the goal card

        # Normal search
        goal_func = lambda state: True if state.last_move is not None and state.last_move.type == MOVE_PLAY_GOAL else False
        # heuristic is simply min distance between play piles and goal card
        def h(state):
            goal_card = state.goal_cards[state.current_player]
            # TODO figure out what correct check is here
            if goal_func(state) or state.goal_cards[state.current_player] is None:
                return 0
            return self.min_dist_to_play_pile(state, goal_card)
        
        return self.find_path(hg, goal_func, h)

    def find_path_to_empty_hand(self, hg):
        goal_func = lambda state: True if len(state.player_hands[state.current_player]) == 0 else False
        h = lambda state: len(state.player_hands[state.current_player])
        return self.find_path(hg, goal_func, h)

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
        '''
            How to score a state:
            - Look at immediately playable cards; what is the reach?
            - Look at opponents; how close are they to playing their goal?
            - Look at discard piles; are they flexible/not blocking potential plays?
            - Look at hand; do we have wildcards?
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

        # normalize the dangers
        other_players_danger = [d/MAX_DANGER for d in other_players_danger]
        # TODO modulate the danger of opposing players by the size of their goal pile
        # higher pile means it's less dangerous (a little) to let them play
        all_scores = other_players_danger
        all_scores[hg.current_player] = hand_score
        return sum([score/len(all_scores) for score in all_scores])

    def do_good_moves(self, hg):
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

        # TODO: play as many cards as possible; this isn't happening rn, throwing away good paths

        # Search for the best path
        child_moves = [MOVE_PLAY_HAND, MOVE_PLAY_DISCARD, MOVE_PLAY_GOAL, MOVE_END_TURN]
        # enumerate all paths that terminate in MOVE_END_TURN
        # queue of paths, not just states
        queue = [[hg]]
        seen = set([hg])
        best_path = None
        best_score = 0
        num_paths_found = 0
        MAX_PATHS_FOUND = 100

        # TODO order the queue and cap the search depth/time

        start = time.perf_counter()

        while len(queue) > 0:

            path = queue.pop()
            if path[-1].last_move is not None and path[-1].last_move.type == MOVE_END_TURN:

                if best_path is None:
                    best_path = path
                else:
                    # score the last state to evaluate which path to keep
                    score = self.score_state(path[-1], hg.current_player)
                    if score > best_score:
                        best_path = path
                        best_score = score

                # TODO: maybe don't have to do this?
                num_paths_found += 1
                if num_paths_found > MAX_PATHS_FOUND:
                    break

                continue

            for child_state in self.get_child_states(path[-1], child_moves):
                if child_state in seen:
                    continue
                seen.add(child_state)
                new_path = path[:] + [child_state]
                queue.append(new_path)

        #print(time.perf_counter() - start)

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
        self.path = self.do_good_moves(hidden_game)
        return self.path.pop()
