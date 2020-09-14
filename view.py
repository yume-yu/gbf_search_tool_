import curses
import locale
from util import gbss_addstr
import db

locale.setlocale(locale.LC_ALL, "")
TITLE = "title"
CANCEL = -1
HOWTO ="↑↓:up&down →:ENTER ←:CANCEL"


def main(stdscr):
    # 必要だから書く
    curses.start_color()
    # 色の設定
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLUE)
    # バックグラウンド設定
    stdscr.bkgd(" ", curses.color_pair(1) | curses.A_BOLD)
    # 画面のマックスサイズをタプルで取得
    y, x = stdscr.getmaxyx()
    # windowの生成
    window = stdscr.derwin(int(y) - 4, int(x / 2), 3, 0)
    # window2の生成
    window2 = stdscr.derwin(int(y) - 4, int(x / 2), 3, int(x - (x / 2)))
    # window2の背景の設定
    window.bkgd(" ", curses.color_pair(2))
    # window1の背景の設定
    window2.bkgd(" ", curses.color_pair(3))
    # 枠線の設定
    window.border()
    window2.border()

    categories = db.get_bosscategories()
    stdscr.addstr(1, int(x / 2) - 3, TITLE, curses.A_REVERSE)
    stdscr.addstr(int(y-1), int(x / 2) - 10, HOWTO, curses.A_REVERSE)
    stdscr.refresh()
    while True:
        selected = menu(window, categories, "category_name")
        if(selected == CANCEL):
            continue
        bosslists = db.get_bosslist_by_id(selected)
        selected = menu(window2, bosslists, "boss_name")
        if(selected == CANCEL):
            continue
        return(bosslists[selected])


def menu(window, datas, tag):
    window.keypad(True)
    selected = 0
    maxnum = len(datas) - 1
    while True:
        window.erase()
        for number, data in enumerate(datas):
            if selected == number:
                gbss_addstr(
                    window,
                    (number * 2) + 1,
                    1,
                    data[tag],
                    curses.A_REVERSE,
                )
            else:
                gbss_addstr(
                    window,
                    (number * 2) + 1,
                    1,
                    data[tag]
                )
        window.refresh()
        inputkey = window.getch()
        if inputkey == curses.KEY_UP:
            if selected > 0:
                selected = selected - 1
        elif inputkey == curses.KEY_DOWN:
            if selected < maxnum:
                selected = selected + 1
        elif inputkey == curses.KEY_RIGHT:
            return selected
        elif inputkey == curses.KEY_LEFT:
            window.erase()
            window.refresh()
            return CANCEL


if __name__ == "__main__":
    curses.wrapper(main)
