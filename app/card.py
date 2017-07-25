class Card:
    """one playing card."""

    SUITS = {
        "clubs": {
            "color": "black",
            "display": "\N{BLACK CLUB SUIT}"
        },
        "diamonds": {
            "color": "red",
            "display": "\N{BLACK DIAMOND SUIT}"
        },
        "hearts": {
            "color": "red",
            "display": "\N{BLACK HEART SUIT}"
        },
        "spades": {
            "color": "black",
            "display": "\N{BLACK SPADE SUIT}"
        }
    }

    __symbols = {
        1: "A",
        11: "J",
        12: "Q",
        13: "K"
    }

    def __init__(self, value, suit):
        """initializes a face-down playing card.
        params:
            - value (int): numerical value of card
                           1 <= value <= 13
            - suit (str): valid card suit
        """
        suit = suit.lower()

        assert value in range(1, 14), "value must be beween 1-13."
        assert suit in self.SUITS, "suit must be a valid card suit."

        self.value = value
        self.suit = suit
        self.face_up = False

    def __repr__(self):
        cls_name = "card" if self.face_up else "----"
        return "<{}: {} of {}>".format(cls_name, self.symbol, self.suit)

    def __eq__(self, card):
        """cards are equal if their values and suits match."""
        return self.value == card.value and self.suit == card.suit

    @property
    def symbol(self):
        """(str) a, j, q, k instead of 1, 11, 12, 13."""
        return self.__symbols.get(self.value, str(self.value))

    @property
    def color(self):
        """(str) color of card's suit."""
        return self.SUITS[self.suit].get("color")

    @property
    def is_red(self):
        """(bool) whether card is a red suit."""
        return self.color == "red"

    @property
    def display(self):
        """(str) symbol of card's suit."""
        return self.SUITS[self.suit].get("display")

    def flip(self):
        """flips over card. returns self."""
        self.face_up = not self.face_up
        return self
