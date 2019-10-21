'''
    Card class and utility functions
'''
import random

# include jokers
NUM_CARDS_PER_DECK=54
NUM_JOKERS_PER_DECK=2
NUM_SUITES=4
SUITES=["Diamonds", "Hearts", "Clubs", "Spades"]
VALUE_TO_CARD_NAME={
        1: "Ace",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Joker"
        }
WILD_VALUES=[13,14]

class Card:
    '''
        A card in the game spite and malice
    '''
    def __init__(self, value, suite):
        self.value = value
        self.suite = suite

    def is_wild(self):
        return self.value in WILD_VALUES

    def __repr__(self):
        if self.value == 14:
            return "Joker"
        return "{} of {}".format(VALUE_TO_CARD_NAME[self.value], self.suite)

DECK=[Card(value, suite) for value in list(VALUE_TO_CARD_NAME.keys())[:13] for suite in SUITES] + \
        [Card(14, None), Card(14, None)]

def make_decks(N):
    '''
        Create a list containing N full decks of Cards
    '''
    ret = []
    for _ in range(N):
        ret += DECK[:]
    return ret

def draw(pile):
    '''
        Draw a card randomly from a pile
        A pile is just a list of Cards
    '''
    if len(pile) == 0:
        return None
    index = random.randrange(0, len(pile))
    return pile.pop(index)

def draw_N(pile, N):
    if N > len(pile):
        raise RuntimeError("Can't draw that many cards!")
    return [draw(pile) for _ in range(N)]
