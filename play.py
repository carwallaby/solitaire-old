#!/usr/bin/env python3
import curses
from app import *
from functools import partial


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
    MAX_FACE_UP_COVERED_CARDS = 11  # 2 lines each
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

        self.ace_pile_windows = {}
        self.column_windows = []

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
                self.clear_message_box()
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
            ord("q"): self.confirm_quit,
            ord(" "): self.draw_from_pile,
            ord("1"): partial(self.select_col, 0),
            ord("2"): partial(self.select_col, 1),
            ord("3"): partial(self.select_col, 2),
            ord("4"): partial(self.select_col, 3),
            ord("5"): partial(self.select_col, 4),
            ord("6"): partial(self.select_col, 5),
            ord("7"): partial(self.select_col, 6),
            ord("d"): self.select_discard,
            ord("N"): self.new_game
        }

    def draw_screen(self):
        """clears and redraws entire screen."""
        try:
            self._draw_message_box()
            self._draw_ace_piles()
            self._draw_discard_pile()
            self._draw_deck()
            self._draw_columns()
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
        for i, suit in enumerate(Card.SUITS):
            if not self.ace_pile_windows.get(suit):
                x = (i * self.CARD_WIDTH) + (i + 1)
                self.ace_pile_windows[suit] = self._draw_ace_pile(1, x)
            self._populate_ace_pile(suit)

    def _draw_discard_pile(self):
        """draws the discard pile window."""
        try:
            self.discard_pile_window.clear()
        except AttributeError:
            x = (self.CARD_WIDTH * (self.COLUMNS - 2)) + self.COLUMNS
            self.discard_pile_window = self.screen.subwin(self.CARD_HEIGHT + 1,
                                                          self.CARD_WIDTH + 1,
                                                          0,
                                                          x)
        self._populate_discard_pile()

    def _draw_deck(self):
        """draws the deck."""
        try:
            self.deck_window.clear()
        except AttributeError:
            x = (self.CARD_WIDTH * (self.COLUMNS - 1)) + self.COLUMNS + 2
            self.deck_window = self.screen.subwin(self.CARD_HEIGHT + 1,
                                                  self.CARD_WIDTH + 1,
                                                  0,
                                                  x)

        self._populate_deck()

    def _draw_columns(self):
        """draws the columns."""
        if not self.column_windows:
            for i in range(0, self.COLUMNS):
                y = self.CARD_HEIGHT + 5
                x = (i * self.CARD_WIDTH) + (i + 1)
                self.screen.addstr(y - 1,
                                   (x + ((self.CARD_WIDTH - 1) // 2)),
                                   str(i + 1))
                self.column_windows.append(self._draw_column(y, x))

        for i in range(0, self.COLUMNS):
            self._populate_column(i)

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

    # ----- overrides and moves -----

    def new_game(self):
        self.screen.clear()
        self.ace_pile_windows = {}
        self.column_windows = []
        super().reset_game(1)
        self.draw_screen()

    def draw_from_pile(self):
        super().draw_from_pile()
        self._draw_deck()
        self._draw_discard_pile()

    def discard_to_column(self, col_idx):
        try:
            super().discard_to_column(col_idx)
            self.draw_screen()
        except IllegalMoveError:
            self.draw_screen()
            self.set_message("illegal move! :(", self.RED)

    def discard_to_ace_pile(self):
        try:
            super().discard_to_ace_pile()
            self.draw_screen()
        except IllegalMoveError:
            self.draw_screen()
            self.set_message("illegal move! :(", self.RED)

    def column_to_column(self, src_idx, dest_idx, num_cards):
        try:
            super().column_to_column(src_idx, dest_idx, num_cards)
            self.draw_screen()
        except IllegalMoveError:
            self.draw_screen()
            self.set_message("illegal move! :(", self.RED)

    def column_to_ace_pile(self, col_idx):
        try:
            super().column_to_ace_pile(col_idx)
            self.draw_screen()
        except IllegalMoveError:
            self.draw_screen()
            self.set_message("illegal move! :(", self.RED)

    def select_col(self, col_idx):
        num_to_select = 1

        selected_key_map = {
            ord("a"): partial(self.column_to_ace_pile, col_idx)
        }

        cols = [i for i in range(0, self.COLUMNS) if i != col_idx]

        while True:
            move = self.screen.getch()
            if move in selected_key_map:
                selected_key_map[move]()
                break
            elif move == curses.KEY_DOWN:
                if num_to_select > 1:
                    num_to_select -= 1
            elif move == curses.KEY_UP:
                idx = num_to_select + 1
                if self.columns[col_idx].cards[(idx * -1)].face_up:
                    num_to_select += 1
            elif (int(chr(move)) - 1) in cols:
                self.column_to_column(col_idx,
                                      int(chr(move)) - 1,
                                      num_to_select)
                break
            else:
                break

    def select_discard(self):
        selected_key_map = {
            ord("a"): self.discard_to_ace_pile,
            ord("1"): partial(self.discard_to_column, 0),
            ord("2"): partial(self.discard_to_column, 1),
            ord("3"): partial(self.discard_to_column, 2),
            ord("4"): partial(self.discard_to_column, 3),
            ord("5"): partial(self.discard_to_column, 4),
            ord("6"): partial(self.discard_to_column, 5),
            ord("7"): partial(self.discard_to_column, 6)
        }

        move = self.screen.getch()
        if move in selected_key_map:
            selected_key_map[move]()
        else:
            pass

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

    def _draw_column(self, start_y, start_x):
        """draws and returns column window."""
        win = self.screen.subwin(self.MAX_COL_HEIGHT,
                                 self.CARD_WIDTH + 1,
                                 start_y,
                                 start_x)
        self.screen.refresh()
        win.refresh()
        return win

    def _populate_ace_pile(self, suit):
        """fill in ace pile strings if card in ace pile."""
        pile = self.ace_piles[suit]
        win = self.ace_pile_windows[suit]
        win.clear()
        win.box()

        if not pile.is_empty:
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
        self.discard_pile_window.clear()

        if len(self.discard_pile) == 0:
            self.discard_pile_window.addstr(1, 0, self.EMPTY_TOP)
            self.discard_pile_window.addstr(self.CARD_HEIGHT,
                                            0,
                                            self.EMPTY_BOTTOM)
        else:
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

    def _populate_deck(self):
        self.deck_window.clear()

        if self.deck.is_empty:
            self.deck_window.addstr(1, 0, self.EMPTY_TOP)
            self.deck_window.addstr(self.CARD_HEIGHT, 0, self.EMPTY_BOTTOM)
        else:
            self.deck_window.addstr(1, 0, self.CARD_TOP)
            for i in range(2, 5):
                self.deck_window.addstr(i, 0, self._face_down_str())
            self.deck_window.addstr(self.CARD_HEIGHT, 0, self.CARD_BOTTOM)

        self.screen.refresh()
        self.deck_window.refresh()

    def _populate_column(self, idx):
        win = self.column_windows[idx]
        col = self.columns[idx]
        win.clear()

        if col.is_empty:
            win.addstr(1, 0, self.EMPTY_TOP)
            win.addstr(self.CARD_HEIGHT, 0, self.EMPTY_BOTTOM)
        else:
            y = 1
            for card in col.cards:
                if card == col.top_card:
                    self._draw_full_card(win, card, y)
                elif card.face_up:
                    self._draw_face_up_covered_card(win, card, y)
                    y += 2
                else:
                    self._draw_face_down_covered_card(win, y)
                    y += 1

        self.screen.refresh()
        win.refresh()

    # ----- gui builders -----

    def _card_top_str(self, card):
        """string for top half of card."""
        space_chars = self.CARD_WIDTH - 5 - len(card.symbol)
        return " " + card.symbol + (" " * space_chars) + card.display + " "

    def _card_bottom_str(self, card):
        """string for bottom half of card."""
        space_chars = self.CARD_WIDTH - 5 - len(card.symbol)
        return " " + card.display + (" " * space_chars) + card.symbol + " "

    def _face_down_str(self):
        """string for one alternate for deck design."""
        return (self.V_LINE + " " + self.DECK_DESIGN + "  " +
                self.DECK_DESIGN + " " + self.V_LINE)

    def _draw_full_card(self, win, card, start_y):
        attr = self.RED if card.is_red else 0
        # draw top of card
        win.addstr(start_y, 0, self.CARD_TOP)
        # draw first line with text
        win.addstr(start_y + 1, 0, self.V_LINE)
        win.addstr(start_y + 1, 1, self._card_top_str(card), attr)
        win.addstr(start_y + 1, self.CARD_WIDTH - 1, self.V_LINE)
        # draw middle lines
        for i in range(2, self.CARD_HEIGHT - 2):
            win.addstr(start_y + i, 0, self.EMPTY_MIDDLE)
        # draw bottom line with text
        win.addstr(start_y + (self.CARD_HEIGHT - 2), 0, self.V_LINE)
        win.addstr(start_y + (self.CARD_HEIGHT - 2),
                   1,
                   self._card_bottom_str(card),
                   attr)
        win.addstr(start_y + (self.CARD_HEIGHT - 2),
                   self.CARD_WIDTH - 1,
                   self.V_LINE)
        # draw bottom of card
        win.addstr(start_y + (self.CARD_HEIGHT - 1), 0, self.CARD_BOTTOM)

    def _draw_face_down_covered_card(self, win, start_y):
        win.addstr(start_y, 0, self.CARD_TOP)

    def _draw_face_up_covered_card(self, win, card, start_y):
        attr = self.RED if card.is_red else 0
        win.addstr(start_y, 0, self.CARD_TOP)
        win.addstr(start_y + 1, 0, self.V_LINE)
        win.addstr(start_y + 1, 1, self._card_top_str(card), attr)
        win.addstr(start_y + 1, self.CARD_WIDTH - 1, self.V_LINE)


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
