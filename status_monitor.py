"""
tweetの取得状況を表示/更新するクラス
Attributes:
    window (curses.window): 呼び出し元から受け取ったメインウィンドウ
    title_pad (curses.window): 検索対象のボス名を表示するサブウィンドウ
    recent_pad (curses.window): 記錄した救援IDの履歴を表示するサブウィンドウ
    api_monitor (curses.window): 直前のAPIへのリクエストステータスを表示するサブウィンドウ
"""
import curses
import datetime as dt

from tweet import RequestFaildError
from util import (BOTTOM_PART_HEIGHT, MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH,
                  MIDDLE_PART_HEIGHT, TOP_PART_HEIGHT)


class StatusMonitor:
    def __init__(self, stdscr: curses.window, boss_info: dict):
        self.window = stdscr
        self.subwin_width = int(MAIN_WIN_WIDTH / 2)

        #  タイトル部分表示
        self.title_pad = self.window.subpad(TOP_PART_HEIGHT, MAIN_WIN_WIDTH, 0, 0)
        self.title_pad.bkgd(curses.color_pair(4))
        self.title_pad.addstr(1, 1, "< Target >", curses.A_BOLD)
        self.title_pad.addstr(2, 1, boss_info.get("boss_name"))
        self.title_pad.border()
        self.title_pad.refresh()

        # 履歴部分基礎描画
        self.recent_pad = stdscr.derwin(
            MIDDLE_PART_HEIGHT, self.subwin_width, TOP_PART_HEIGHT, 0
        )
        self.recent_pad.bkgd(curses.color_pair(4))
        self.recent_pad.scrollok(True)
        self.recent_pad.idlok(True)
        self.recent_pad.addstr(1, 1, "< Recent >", curses.A_BOLD)
        self.recent_pad.border()
        self.recent_pad.refresh()

        # API情報基礎描画
        self.api_monitor = stdscr.derwin(
            MIDDLE_PART_HEIGHT, self.subwin_width, TOP_PART_HEIGHT, self.subwin_width
        )
        self.api_monitor.bkgd(curses.color_pair(4))
        self.api_monitor.addstr(1, 1, "< About Request >", curses.A_BOLD)
        self.api_monitor.addstr(2, 1, "API Status:")
        self.api_monitor.addstr(5, 1, "Request interval [s/req]:")
        self.api_monitor.addstr(8, 1, "last update:")
        self.api_monitor.border()
        self.api_monitor.refresh()

        # 操作説明描画
        self.control_explain = stdscr.derwin(
            BOTTOM_PART_HEIGHT, MAIN_WIN_WIDTH, TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT, 0
        )
        self.control_explain.bkgd(curses.color_pair(4))
        self.control_explain.addstr(0, 1, "< How to Control >", curses.A_BOLD)
        self.control_explain.addstr(
            1, 5, "q: quit this / a: slow / s: normal / d: fast"
        )
        self.control_explain.refresh()

    def update_request_status(self, interval: int):
        # API状況更新
        self.api_monitor.addstr(
            3, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.api_monitor.addstr(
            4, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.api_monitor.addstr(
            3, (self.subwin_width - 1 - len("OK") - 1), "OK", curses.color_pair(1)
        )

        self.api_monitor.addstr(
            6, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.api_monitor.addstr(
            6, (self.subwin_width - 1 - len(str(interval)) - 1), str(interval)
        )

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.api_monitor.addstr(9, self.subwin_width - 1 - len(now) - 1, now)
        self.api_monitor.refresh()

    def update_recent_log(self, battle_id: str, tweet_date: dt.datetime):

        # 記錄ID追記
        self.recent_pad.scroll()
        self.recent_pad.addstr(1, 1, "< Recent >", curses.A_BOLD)
        self.recent_pad.addstr(
            MIDDLE_PART_HEIGHT - 2,
            1,
            "".join([" " for index in range(self.subwin_width - 2)]),
        )
        self.recent_pad.addstr(
            MIDDLE_PART_HEIGHT - 2,
            2,
            "{} - {}".format(battle_id, tweet_date.strftime("%H:%M:%S")),
        )
        self.recent_pad.border()

        self.recent_pad.refresh()

    def error_update(self, error: RequestFaildError):
        message = str(error.status_code) + " : " + error.sumally

        # API状況更新
        self.api_monitor.addstr(
            3, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.api_monitor.addstr(
            4, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.api_monitor.addstr(
            3, (self.subwin_width - 1 - len("NG") - 1), "NG", curses.color_pair(2)
        )
        self.api_monitor.addstr(
            3, (self.subwin_width - 1 - len(message) - 1), message, curses.color_pair(2)
        )

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.api_monitor.addstr(9, self.subwin_width - 1 - len(now) - 1, now)
        self.recent_pad.refresh()
        self.api_monitor.refresh()


if __name__ == "__main__":

    def main(stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.curs_set(False)
        curses.resize_term(MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH)
        t = StatusMonitor(stdscr)
        curses.curs_set(True)

    print(curses.wrapper(main))
