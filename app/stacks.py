from .card import Card
from random import shuffle


# ----- stack -----

class Stack:
    """base class for stack of cards."""

    def __init__(self):
        """initializes empty stack."""
        self.cards = []

    def __repr__(self):
        maybe_s = "" if self.size == 1 else "s"
        return "<stack: {} card{}>".format(self.size, maybe_s)

    @property
    def size(self):
        """(int) number of cards in stack."""
        return len(self.cards)

    @property
    def is_empty(self):
        """(bool) whether or not the stack is empty."""
        return self.size == 0

    @property
    def top_card(self):
        """(card) returns top card in stack."""
        assert not self.is_empty, "stack is empty."
        return self.cards[-1]

    def take_card(self):
        """(card) removes and returns top card in stack."""
        assert not self.is_empty, "stack is empty."
        return self.cards.pop()

    def add_cards(self, cards):
        """adds card/list to stack.
        param:
            - cards (card/list): card(s) to add
        """
        try:
            assert isinstance(cards, list)
        except AssertionError:
            assert isinstance(cards, Card)
            cards = [cards]

        self.cards += cards
        return self


# ----- deck -----

class Deck(Stack):
    """deck of cards."""

    def __init__(self):
        """initializes a full, shuffled deck of cards."""
        self.reset_deck().shuffle()

    def __repr__(self):
        maybe_s = "" if self.size == 1 else "s"
        return "<deck: {} card{}>".format(self.size, maybe_s)

    def reset_deck(self):
        """empties and refills cards with new, ordered set."""
        stack = []

        for suit in Card.SUITS:
            for i in range(1, 14):
                stack.append(Card(i, suit))

        self.cards = stack
        return self

    def shuffle(self):
        """shuffles deck in place."""
        shuffle(self.cards)
        return self


# ----- ace pile -----

class AcePile(Stack):
    """ace pile for solitaire."""

    def __repr__(self):
        maybe_s = "" if self.size == 1 else "s"
        return "<ace pile: {} card{}>".format(self.size, maybe_s)

    def add_cards(self, cards):
        """override parent method."""
        raise IllegalMoveError()

    def add_card(self, card):
        """adds a card to the pile, if possible.
        param:
            - card (card): card to attempt to add
        """
        if not self._can_add_card(card):
            raise IllegalMoveError()
        return super().add_cards(card)

    def _can_add_card(self, card):
        """(bool) whether card can be added to pile.
        param:
            - card (card): card to attempt to add
        """
        assert isinstance(card, Card), "only a card can be added to ace pile."

        if card.value == 1:
            # always allow aces
            return True
        elif self.is_empty:
            # don't allow non-aces on empty piles
            return False
        return (card.suit == self.top_card.suit and
                card.value == self.top_card.value + 1)


# ----- column -----

class Column(Stack):
    """column for solitaire."""

    def __repr__(self):
        maybe_s = "" if self.size == 1 else "s"
        return "<column: {} card{}>".format(self.size, maybe_s)

    def add_card(self, card):
        """adds a card to the column if possible.
        param:
            - card (card): card to attempt to add
        """
        assert isinstance(card, Card)
        if not self._can_add_card(card):
            raise IllegalMoveError()
        return super().add_cards(card)

    def add_cards(self, cards):
        """adds card/list to column if possible.
        param:
            - cards (card/list): card(s) to add
        """
        try:
            assert isinstance(cards, list)
        except AssertionError:
            assert isinstance(cards, Card)
            cards = [cards]
        if not self._can_add_card(cards[0]):
            raise IllegalMoveError()
        return super().add_cards(cards)

    def take_card(self):
        """removes and returns top card in deck.
        overrides super and adds check to flip top card."""
        card = super().take_card()
        if not self.is_empty and not self.top_card.face_up:
            self.top_card.flip()
        return card

    def take_cards(self, num_cards):
        """removes and returns num_cards in order.
        param:
            - num_cards (int): number of cards to take
        """
        assert num_cards <= self.size, "not enough cards."

        cards = self.cards[(num_cards * -1):]
        self.cards = self.cards[:(num_cards * -1)]

        if not self.is_empty and not self.top_card.face_up:
            self.top_card.flip()
        return cards

    def _can_add_card(self, card):
        """(bool) whether card can be added to the column.
        param:
            - card (card): card to attempt to add
        """
        if self.is_empty:
            # always allow kings on empty columns
            return card.value == 13

        correct_color = card.color != self.top_card.color
        correct_value = card.value == self.top_card.value - 1
        return correct_color and correct_value

    def _push_card(self, card):
        """allows cards to be added to column that don't fit the rules.
        used for populating the columns."""
        self.cards.append(card)
        return self


# ----- errors -----

class IllegalMoveError(Exception):
    pass
