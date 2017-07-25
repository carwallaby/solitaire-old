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

    DECK_DESIGN = "\N{CLOUD}"

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
        self.draw_message_box()

    def draw_message_box(self):
        """message subwindow that is easily cleared."""
        self.message_box = self.screen.subwin(self.height - 1, 0)
        self.screen.refresh()

    # ----- messages -----

    def set_message(self, msg, attr=0):
        """sets message in message box.
        param:
            - msg (str): message to display
        """
        self.message_box.clear()
        self.message_box.addstr(msg, attr)
        self.message_box.refresh()
        self.screen.refresh()

    def clear_message_box(self):
        """clears message box."""
        self.message_box.clear()
        self.message_box.refresh()
        self.screen.refresh()


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
