import curses
import locale

import db
from util import gbss_addstr

locale.setlocale(locale.LC_ALL, "")

MAIN_WIN_WIDTH = 80
TOP_PART_HEIGHT = 4
MIDDLE_PART_HEIGHT = 11
BOTTOM_PART_HEIGHT = 4
MAIN_WIN_HEIGHT = TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT + BOTTOM_PART_HEIGHT

CANCEL = -1
TITLE = "Select Search Target"
CATEGORY = "< CATEGORY >"
NAME = "< NAME >"
HOWTOCONTROL_TEXT = "↑↓:up&down →:ENTER ←:CANCEL"


def boss_select_menu(stdscr: curses.window):
    """boss_select_menu

    検索する救援の対象のボスの選択をcursesを使ってユーザーに求める

    Args:
        stdscr: curses.Windowクラスのオブジェクト
    Returns:
        dict: 選択したbossの情報 {'id': 0, 'boss_name': 'name', 'search_query': 'keyword'}
    Examples:
        user_selected_boss = curse.wrapper(boss_select_menu)
    """
    # 必要だから書く
    curses.start_color()
    # 色の設定
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    # バックグラウンド設定
    stdscr.bkgd(" ", curses.color_pair(1) | curses.A_BOLD)
    # 画面のマックスサイズをタプルで取得
    y, x = stdscr.getmaxyx()
    # windowの生成
    window = stdscr.derwin(
        MIDDLE_PART_HEIGHT, int(MAIN_WIN_WIDTH / 2), TOP_PART_HEIGHT, 0
    )
    # window2の生成
    window2 = stdscr.derwin(
        MIDDLE_PART_HEIGHT,
        int(MAIN_WIN_WIDTH / 2),
        TOP_PART_HEIGHT,
        int(MAIN_WIN_WIDTH / 2),
    )
    # window2の背景の設定
    window.bkgd(" ", curses.color_pair(2))
    # window1の背景の設定
    window2.bkgd(" ", curses.color_pair(3))
    # 枠線の設定
    window.border()
    window2.border()

    categories = db.get_bosscategories()
    stdscr.addstr(1, int((MAIN_WIN_WIDTH - len(TITLE)) / 2), TITLE, curses.A_BOLD)
    stdscr.addstr(TOP_PART_HEIGHT - 1, 1, CATEGORY, curses.A_BOLD)
    stdscr.addstr(TOP_PART_HEIGHT - 1, int(MAIN_WIN_WIDTH / 2) + 1, NAME, curses.A_BOLD)
    stdscr.addstr(MAIN_WIN_HEIGHT - 2, 1, HOWTOCONTROL_TEXT, curses.A_REVERSE)
    stdscr.refresh()
    while True:
        selected = scrolled_menu(window, categories, "category_name")
        if selected == CANCEL:
            continue
        bosslists = db.get_bosslist_by_id(selected + 1)
        selected = scrolled_menu(window2, bosslists, "boss_name")
        if selected == CANCEL:
            continue
        return bosslists[selected]


def menu(window: curses.window, datas: list, tag: str):
    """menu

    cursesを使って引数のリストを表示してユーザーに選択を促す。

    Args:
        window: リストを表示/操作するcurses.Windowクラス
        datas: 列挙する内容1つづつをdictとして保持したリスト
        tag: datasのデータ1つの中で、表示する内容のkey
    Returns:
        int: ユーザーがリストの何番目を選択したのか値
    """
    window.keypad(True)
    selected = 0
    maxnum = len(datas) - 1
    while True:
        window.erase()
        for number, data in enumerate(datas):
            if selected == number:
                gbss_addstr(window, (number * 2) + 1, 1, data[tag], curses.A_REVERSE)
            else:
                gbss_addstr(window, (number * 2) + 1, 1, data[tag])
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


def scrolled_menu(window: curses.window, datas: list, tag: str):
    """menu

    cursesを使って引数のリストを表示してユーザーに選択を促す。

    Args:
        window: リストを表示/操作するcurses.Windowクラス
        datas: 列挙する内容1つづつをdictとして保持したリスト
        tag: datasのデータ1つの中で、表示する内容のkey
    Returns:
        int: ユーザーがリストの何番目を選択したのか値
    """
    window.erase()
    window.border()

    # スクロール準備
    height, width = window.getmaxyx()
    window.scrollok(True)
    window.idlok(True)
    # window.setscrreg(1, height - 1)
    top = 0
    bottom = height - 2
    label_offset = 4

    window.keypad(True)
    selected = 0
    maxnum = len(datas) - 1

    # 初期出力

    for index, data in enumerate(datas):
        if top <= index <= bottom - 1:
            if selected == index:
                window.addstr(
                    index + 1,
                    label_offset,
                    "".join([" " for index in range(width - 2 - label_offset)]),
                    curses.A_REVERSE,
                )
                gbss_addstr(
                    window, index + 1, label_offset - 1, data[tag], curses.A_REVERSE
                )
            else:
                gbss_addstr(window, index + 1, label_offset, data[tag])

    if bottom < len(datas):
        gbss_addstr(window, bottom - top, 1, "↓")
    if top > 0:
        gbss_addstr(window, top + 1, 1, "↑")

    while True:
        inputkey = window.getch()
        if inputkey == curses.KEY_UP:
            if selected > 0:
                window.addstr(
                    selected - top + 1, 1, "".join([" " for index in range(width - 2)])
                )
                gbss_addstr(
                    window, selected - top + 1, label_offset, datas[selected].get(tag)
                )
                selected = selected - 1
                if top > selected:
                    top = top - 1
                    bottom = bottom - 1
                    window.scroll(-1)
                    window.border()
                window.addstr(
                    selected - top + 1, 1, "".join([" " for index in range(width - 2)])
                )
                window.addstr(
                    selected - top + 1,
                    label_offset,
                    "".join([" " for index in range(width - 2 - label_offset)]),
                    curses.A_REVERSE,
                )
                gbss_addstr(
                    window,
                    selected - top + 1,
                    label_offset - 1,
                    datas[selected].get(tag),
                    curses.A_REVERSE,
                )
                if bottom < maxnum + 1:
                    gbss_addstr(window, bottom - top, 1, "↓")
                if top > 0:
                    gbss_addstr(window, 1, 1, "↑")
                window.refresh()
        elif inputkey == curses.KEY_DOWN:
            if selected < maxnum:
                window.addstr(
                    selected - top + 1, 1, "".join([" " for index in range(width - 2)])
                )
                gbss_addstr(
                    window, selected - top + 1, label_offset, datas[selected].get(tag)
                )
                selected = selected + 1
                if bottom <= selected:
                    top = top + 1
                    bottom = bottom + 1
                    window.scroll(1)
                    window.border()
                window.addstr(
                    selected - top + 1, 1, "".join([" " for index in range(width - 2)])
                )
                window.addstr(
                    selected - top + 1,
                    label_offset,
                    "".join([" " for index in range(width - 2 - label_offset)]),
                    curses.A_REVERSE,
                )
                gbss_addstr(
                    window,
                    selected - top + 1,
                    label_offset - 1,
                    datas[selected].get(tag),
                    curses.A_REVERSE,
                )
                if bottom < maxnum + 1:
                    gbss_addstr(window, bottom - top, 1, "↓")
                if top > 0:
                    gbss_addstr(window, 1, 1, "↑")
                window.refresh()
        elif inputkey == curses.KEY_RIGHT:
            return selected
        elif inputkey == curses.KEY_LEFT:
            window.erase()
            window.border()
            window.refresh()
            return CANCEL


if __name__ == "__main__":
    main_height = TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT + BOTTOM_PART_HEIGHT

    def main(stdscr):
        curses.curs_set(False)
        curses.resize_term(main_height, MAIN_WIN_WIDTH)
        select = boss_select_menu(stdscr)
        curses.curs_set(True)

        return select

    print(curses.wrapper(main))
