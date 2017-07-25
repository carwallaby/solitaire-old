from .stacks import *


class Solitaire:
    """a game of solitaire."""

    COLUMNS = 7

    def __init__(self, draw=1):
        """initializes a game of solitaire.
        param:
            - draw (int): 1 or 3 card draw.
        """
        assert draw == 1 or draw == 3
        self.reset_game(draw)

    def reset_game(self, draw):
        """sets up new game of solitaire."""
        self.draw = draw

        self.deck = Deck()
        self.discard_pile = []
        self.ace_piles = {s: AcePile() for s in Card.SUITS}
        self.columns = [Column() for _ in range(self.COLUMNS)]
        self._initialize_columns()

    def _initialize_columns(self):
        """fills in columns from deck during reset."""
        for i, col in enumerate(self.columns):
            while col.size < i:
                col._push_card(self.deck.take_card())
            col._push_card(self.deck.take_card().flip())
