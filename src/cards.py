'''
    Card class and utility functions
'''
import random

# include jokers
NUM_CARDS_PER_DECK=54
NUM_JOKERS_PER_DECK=2
NUM_SUITES=4
SUITES=["Diamonds", "Hearts", "Clubs", "Spades"]
# card types
CARD_ACE = 1
CARD_2 = 2
CARD_3 = 3
CARD_4 = 4
CARD_5 = 5
CARD_6 = 6
CARD_7 = 7
CARD_8 = 8
CARD_9 = 9
CARD_10 = 10
CARD_JACK = 11
CARD_QUEEN = 12
CARD_KING = 13
CARD_JOKER = 14

CARD_TYPE_TO_NAME={
        CARD_ACE: "Ace",
        CARD_2: "2",
        CARD_3: "3",
        CARD_4: "4",
        CARD_5: "5",
        CARD_6: "6",
        CARD_7: "7",
        CARD_8: "8",
        CARD_9: "9",
        CARD_10: "10",
        CARD_JACK: "Jack",
        CARD_QUEEN: "Queen",
        CARD_KING: "King",
        CARD_JOKER: "Joker"
        }
WILD_TYPES=[13,14]
WILD_VALUE=99
CARD_TYPE_TO_VALUE={
    key:(key if key not in WILD_TYPES else WILD_VALUE) \
        for key in CARD_TYPE_TO_NAME.keys()
    }

class Card:
    '''
        A card in the game spite and malice
    '''
    def __init__(self, ctype, suite):
        self.ctype = ctype
        self.suite = suite
        self.value = CARD_TYPE_TO_VALUE[self.ctype]

    def is_wild(self):
        return self.value == WILD_VALUE

    def __hash__(self):
        return self.value

    def __repr__(self):
        if self.ctype == CARD_JOKER:
            return CARD_TYPE_TO_NAME[self.ctype]
        return "{} of {}".format(CARD_TYPE_TO_NAME[self.ctype], self.suite)

DECK = [Card(ctype, suite) \
    for ctype in [t for t in CARD_TYPE_TO_NAME.keys() if t != CARD_JOKER] \
        for suite in SUITES]
DECK += [Card(CARD_JOKER, None)]*2

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
