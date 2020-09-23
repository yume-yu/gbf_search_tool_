import curses
import time

from check_thread import CheckTweet
from select_boss import boss_select_menu
from status_monitor import StatusMonitor
from util import INTERVAL_PATTERN, MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH


def do_action(key: str, thread: CheckTweet) -> bool:
    if key == "q":
        return False
    elif key == "d":
        thread.update_interval(INTERVAL_PATTERN[0])
    elif key == "s":
        thread.update_interval(INTERVAL_PATTERN[1])
    elif key == "a":
        thread.update_interval(INTERVAL_PATTERN[2])
    return True


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.resize_term(MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH)
    select = boss_select_menu(stdscr)
    stdscr.clear()
    monitor = StatusMonitor(stdscr, select)
    thread = CheckTweet(search_query=select.get("search_query"), monitor=monitor)
    thread.start()
    while True:
        try:
            key = stdscr.getkey()
            if do_action(key, thread):
                pass
            else:
                return
        except:
            pass


curses.wrapper(main)
