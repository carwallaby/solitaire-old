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

    # ----- discard / deck moves -----

    def draw_from_pile(self):
        """draws from the pile into the discard pile."""
        if self.deck.is_empty:
            # fill deck and empty discard if out of cards
            self.deck.add_cards([c.flip() for c in self.discard_pile])
            self.deck.cards.reverse()
            self.discard_pile = []
        else:
            drawn = []
            for _ in range(self.draw):
                try:
                    drawn.append(self.deck.take_card().flip())
                except AssertionError:
                    # stop if deck is empty
                    break
            self.discard_pile += drawn
        return self

    def discard_to_column(self, col_idx):
        """attempt to move top card on discard to given column index.
        param:
            - col_idx (int): index of column to move to
        """
        card = self.discard_pile.pop()
        try:
            self.columns[col_idx].add_card(card)
        except IllegalMoveError as e:
            # make sure illegal card doesn't disappear into limbo
            self.discard_pile.append(card)
            raise e
        return self

    def discard_to_ace_pile(self):
        """attempt to move top card on discard to an ace pile."""
        card = self.discard_pile.pop()
        try:
            self.ace_piles[card.suit].add_card(card)
        except IllegalMoveError as e:
            # make sure illegal card doesn't disappear into limbo
            self.discard_pile.append(card)
            raise e
        return self
