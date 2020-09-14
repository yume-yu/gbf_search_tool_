import curses
import locale
from util import gbss_addstr
import db

locale.setlocale(locale.LC_ALL, "")

SUPPORT_MULTIBYTE = False

def main(stdscr):
    select = 0
    select_mode = 1
    # 必要だから書く
    curses.start_color()
    stdscr.keypad(True)
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
    # 背景の設計
    # 文字の配置
    #
    # キーが入力されたら終わる
    while True:
        stdscr.addstr(1, int(x / 2) - 3, "title", curses.A_REVERSE)
        stdscr.refresh()
        if select_mode == 1:
            window.erase()
            for i, category in enumerate(categories):
                maxnum = i
                if i == select:
                    gbss_addstr(
                        window,
                        (i * 2) + 1,
                        1,
                        category["category_name"],
                        curses.A_REVERSE,
                    )
                else:
                    gbss_addstr(window, (i * 2) + 1, 1, category["category_name"])
            inputkey = window.getkey()
            if inputkey == curses.KEY_UP:
                if select > 0:
                    select = select - 1
                    window.refresh()
            elif inputkey == curses.KEY_DOWN:
                if select < maxnum:
                    select = select + 1
                    window.refresh()
            elif inputkey == curses.KEY_RIGHT:
                select_mode = 2
                select_boss = 0
                window.refresh()
        if select_mode == 2:
            window2.erase()
            bosslists = db.get_bosslist_by_id((select + 1))
            for i, bosslist in enumerate(bosslists):
                maxnum = i
                if i == select_boss:
                    gbss_addstr(
                        window2, (i * 2) + 1, 1, bosslist["boss_name"], curses.A_REVERSE
                    )
                    window2.refresh()
                else:
                    gbss_addstr(window2, (i * 2) + 1, 1, bosslist["boss_name"])
                    window2.refresh()
            inputkey = window.getkey()
            if inputkey == curses.KEY_UP:
                if select_boss > 0:
                    select_boss = select_boss - 1
                    window2.refresh()
            elif inputkey == curses.KEY_DOWN:
                if select_boss < maxnum:
                    select_boss = select_boss + 1
                    window2.refresh()
            elif inputkey == curses.KEY_LEFT:
                select_mode = 1
                window2.erase()
                window2.refresh()
            elif inputkey == curses.KEY_RIGHT:
                return bosslists[select_boss]
                break


if __name__ == "__main__":
    x = curses.wrapper(main)
    print(x)
