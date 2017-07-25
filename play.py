#!/usr/bin/env python3
import curses
from app import *


class CSolitaire(Solitaire):
    """solitaire with curses!"""

    # ----- gui constants -----

    CARD_WIDTH = 8
    CARD_HEIGHT = 5

    TL_CORNER = "\N{BOX DRAWINGS LIGHT DOWN AND RIGHT}"
    TR_CORNER = "\N{BOX DRAWINGS LIGHT DOWN AND LEFT}"
    H_LINE = "\N{BOX DRAWINGS LIGHT HORIZONTAL}"
    V_LINE = "\N{BOX DRAWINGS LIGHT VERTICAL}"
    BL_CORNER = "\N{BOX DRAWINGS LIGHT UP AND RIGHT}"
    BR_CORNER = "\N{BOX DRAWINGS LIGHT UP AND LEFT}"

    CARD_TOP = TL_CORNER + (H_LINE * (CARD_WIDTH - 2)) + TR_CORNER
    CARD_BOTTOM = BL_CORNER + (H_LINE * (CARD_WIDTH - 2)) + BR_CORNER

    EMPTY_TOP = TL_CORNER + (" " * (CARD_WIDTH - 2)) + TR_CORNER
    EMPTY_BOTTOM = BL_CORNER + (" " * (CARD_WIDTH - 2)) + BR_CORNER
    EMPTY_MIDDLE = V_LINE + (" " * (CARD_WIDTH - 2)) + V_LINE

    DECK_DESIGN = "\N{CLOUD}"

    MAX_FACE_DOWN_CARDS = Solitaire.COLUMNS - 1  # 1 line each
    MAX_FACE_UP_COVERED_CARDS = 13  # 2 lines each
    MAX_COL_HEIGHT = (MAX_FACE_DOWN_CARDS +
                      (2 * MAX_FACE_UP_COVERED_CARDS) +
                      CARD_HEIGHT)

    # ----- main functions -----

    def __init__(self, screen, draw=1):
        """initializes curses solitaire game.
        params:
            - screen (stdscr): curses screen
            - draw (int): 1 or 3 card draw
        """
        self.screen = screen
        super().__init__(draw)

        start_curses(self.screen)
        self.RED = curses.color_pair(1)
        self.BLUE = curses.color_pair(2)
        self.set_key_mappings()
        self.calibrate_screen_size()

        self.running = True
        self.play()

    def play(self):
        """main function for game."""
        while self.running:
            move = self.screen.getch()
            if move in self.KEY_MAPPING:
                self.KEY_MAPPING[move]()
        stop_curses(self.screen)

    def confirm_quit(self):
        """displays confirmation text and waits for action."""
        self.set_message("are you sure you want to quit? (y / n)", self.RED)
        answer = self.screen.getch()
        if answer == ord("y"):
            self.running = False
        else:
            self.clear_message_box()

    # ----- setup -----

    def calibrate_screen_size(self):
        """sets new screen dimensions after resize and redraws screen."""
        self.height, self.width = self.screen.getmaxyx()
        self.draw_screen()

    def set_key_mappings(self):
        """initializes key mappings."""
        self.KEY_MAPPING = {
            curses.KEY_RESIZE: self.calibrate_screen_size,
            ord("q"): self.confirm_quit
        }

    def draw_screen(self):
        """clears and redraws entire screen."""
        try:
            self._draw_message_box()
            self._draw_ace_piles()
            self._draw_discard_pile()
        except curses.error:
            self.screen.clear()
            self._draw_message_box()
            self.set_message("please make your screen larger. :)", self.RED)

    def _draw_message_box(self):
        """message subwindow that is easily cleared."""
        try:
            self.message_box.clear()
        except AttributeError:
            pass

        self.message_box = self.screen.subwin(self.height - 1, 0)
        self.screen.refresh()
        self.message_box.refresh()

    def _draw_ace_piles(self):
        """initializes ace pile windows."""
        self.ace_pile_windows = {}

        for i, suit in enumerate(Card.SUITS):
            x = (i * self.CARD_WIDTH) + (i + 1)
            self.ace_pile_windows[suit] = self._draw_ace_pile(1, x)
            self._populate_ace_pile(suit)

    def _draw_discard_pile(self):
        """draws the discard pile window."""
        x = (self.CARD_WIDTH * (self.COLUMNS - 1)) + self.COLUMNS
        self.discard_pile_window = self.screen.subwin(self.CARD_HEIGHT + 1,
                                                      self.CARD_WIDTH + 1,
                                                      0,
                                                      x)
        self._populate_discard_pile()

    # ----- messages -----

    def set_message(self, msg, attr=0):
        """sets message in message box.
        param:
            - msg (str): message to display
            - attr (int / curses attr): attribute
        """
        self.message_box.clear()
        self.message_box.addstr(msg, attr)
        self.screen.refresh()
        self.message_box.refresh()

    def clear_message_box(self):
        """clears message box."""
        self.message_box.clear()
        self.screen.refresh()
        self.message_box.refresh()

    # ----- gui components -----

    def _draw_ace_pile(self, start_y, start_x):
        """draws and returns bordered subwindow for ace pile.
        params:
            - start_y (int): y-coordinate of top-left
            - start_x (int): x-coordinate of top-left
        """
        win = self.screen.subwin(self.CARD_HEIGHT,
                                 self.CARD_WIDTH,
                                 start_y,
                                 start_x)
        win.box()
        self.screen.refresh()
        win.refresh()
        return win

    def _populate_ace_pile(self, suit):
        """fill in ace pile strings if card in ace pile."""
        pile = self.ace_piles[suit]

        if not pile.is_empty:
            win = self.ace_pile_windows[suit]
            attr = self.RED if pile.top_card.is_red else 0
            win.addstr(1, 1, self._card_top_str(pile.top_card), attr)
            win.addstr(self.CARD_HEIGHT - 2,
                       1,
                       self._card_bottom_str(pile.top_card),
                       attr)
            self.screen.refresh()
            win.refresh()

    def _populate_discard_pile(self):
        """fill in discard pile appropriately."""
        # TODO: break up into reusable things. same w/ ace card constuction
        # TODO: set this up so it displays top 3 cards if there are 3+
        if len(self.discard_pile) == 0:
            self.discard_pile_window.clear()
            self.discard_pile_window.addstr(1, 0, self.EMPTY_TOP)
            self.discard_pile_window.addstr(self.CARD_HEIGHT,
                                            0,
                                            self.EMPTY_BOTTOM)
        else:
            self.discard_pile_window.clear()
            card = self.discard_pile[-1]
            attr = self.RED if card.is_red else 0
            # draw top of card
            self.discard_pile_window.addstr(1, 0, self.CARD_TOP)
            # draw first line with text
            self.discard_pile_window.addstr(2, 0, self.V_LINE)
            self.discard_pile_window.addstr(2,
                                            1,
                                            self._card_top_str(card),
                                            attr)
            self.discard_pile_window.addstr(2,
                                            self.CARD_WIDTH - 1,
                                            self.V_LINE)
            # draw middle lines
            for i in range(3, self.CARD_HEIGHT - 1):
                self.discard_pile_window.addstr(i, 0, self.EMPTY_MIDDLE)
            # draw bottom line with text
            self.discard_pile_window.addstr(self.CARD_HEIGHT - 1,
                                            0,
                                            self.V_LINE)
            self.discard_pile_window.addstr(self.CARD_HEIGHT - 1,
                                            1,
                                            self._card_bottom_str(card),
                                            attr)
            self.discard_pile_window.addstr(self.CARD_HEIGHT - 1,
                                            self.CARD_WIDTH - 1,
                                            self.V_LINE)
            # draw bottom of card
            self.discard_pile_window.addstr(self.CARD_HEIGHT,
                                            0,
                                            self.CARD_BOTTOM)
        self.screen.refresh()
        self.discard_pile_window.refresh()

    # ----- gui builders -----

    def _card_top_str(self, card):
        """string for top half of card."""
        space_chars = self.CARD_WIDTH - 5 - len(card.symbol)
        return " " + card.symbol + (" " * space_chars) + card.display + " "

    def _card_bottom_str(self, card):
        """string for bottom half of card."""
        space_chars = self.CARD_WIDTH - 5 - len(card.symbol)
        return " " + card.display + (" " * space_chars) + card.symbol + " "


# ----- curses utilities -----

def start_curses(screen):
    screen.keypad(True)
    curses.cbreak()
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.curs_set(0)


def stop_curses(screen):
    screen.clear()
    screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    screen = curses.initscr()
    try:
        game = CSolitaire(screen)
    except:
        import traceback
        stop_curses(screen)
        traceback.print_exc()
