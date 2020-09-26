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
from util import (BOTTOM_PART_HEIGHT, JST, MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH,
                  MIDDLE_PART_HEIGHT, TOP_PART_HEIGHT, gbss_addstr)


class StatusMonitor:
    def __init__(self, stdscr, ratelimit_statuses, boss_info: dict):
        self.window = stdscr
        self.ratelimit_statuses = ratelimit_statuses
        self.subwin_width = int(MAIN_WIN_WIDTH / 2)

        #  タイトル部分表示
        self.title_pad = self.window.subpad(TOP_PART_HEIGHT, MAIN_WIN_WIDTH, 0, 0)
        self.title_pad.bkgd(curses.color_pair(4))
        self.title_pad.addstr(1, 1, "< Target >", curses.A_BOLD)
        gbss_addstr(self.title_pad, 2, 1, boss_info.get("boss_name"))
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
        self.api_monitor.addstr(3, 1, "Request interval [s/req]:")
        self.api_monitor.addstr(4, 1, "Last update:")
        self.api_monitor.addstr(6, 1, "< About Rate Limit >", curses.A_BOLD)
        self.api_monitor.addstr(7, 1, "Rate Limit [/15min]:")
        self.api_monitor.addstr(8, 1, "Remaining:")
        self.api_monitor.addstr(9, 1, "Reset at:")
        self.api_monitor.border()
        self.api_monitor.refresh()

        # 操作説明描画
        self.control_explain = stdscr.derwin(
            BOTTOM_PART_HEIGHT, MAIN_WIN_WIDTH, TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT, 0
        )
        self.control_explain.bkgd(curses.color_pair(4))
        self.control_explain.addstr(0, 1, "< How to Control >", curses.A_BOLD)
        self.control_explain.addstr(
            1, 5, "q: quit this / a: slow / s: normal / d: fast / p: return to select"
        )
        self.control_explain.refresh()

    def update_request_status(self, interval: int):
        self.update_rate_limit()
        # API状況更新
        self.api_monitor.addstr(
            2,
            1 + len("API Status:"),
            "".join(
                [" " for index in range(self.subwin_width - 2 - len("API Status:"))]
            ),
        )
        self.api_monitor.addstr(
            2, (self.subwin_width - 1 - len("OK") - 1), "OK", curses.color_pair(1)
        )

        self.api_monitor.addstr(
            3,
            1 + len("Request interval [s/req]:"),
            "".join(
                [
                    " "
                    for index in range(
                        self.subwin_width - 2 - len("Request interval [s/req]:")
                    )
                ]
            ),
        )
        self.api_monitor.addstr(
            3, (self.subwin_width - 1 - len(str(interval)) - 1), str(interval)
        )

        now = dt.datetime.now().strftime("%H:%M:%S")
        self.api_monitor.addstr(4, self.subwin_width - 1 - len(now) - 1, now)
        self.api_monitor.refresh()

    def update_recent_log(
        self, battle_id: str, tweet_date: dt.datetime, now: dt.datetime
    ):

        # 記錄ID追記
        self.recent_pad.scroll()

        # title
        self.recent_pad.addstr(
            1, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.recent_pad.addstr(1, 1, "< Recent >", curses.A_BOLD)

        # header
        self.recent_pad.addstr(
            2, 1, "".join([" " for index in range(self.subwin_width - 2)])
        )
        self.recent_pad.addstr(2, 2, "id       - posttime : delay")

        self.recent_pad.addstr(
            MIDDLE_PART_HEIGHT - 2,
            1,
            "".join([" " for index in range(self.subwin_width - 2)]),
        )
        self.recent_pad.addstr(
            MIDDLE_PART_HEIGHT - 2,
            2,
            "{} - {} : {}".format(
                battle_id, tweet_date.strftime("%H:%M:%S"), now - tweet_date
            ),
        )
        self.recent_pad.border()

        self.recent_pad.refresh()

    def error_update(self, error: RequestFaildError):
        message = str(error.status_code) + " : " + error.sumally

        # API状況更新
        self.api_monitor.addstr(
            2,
            1 + len("API Status:"),
            "".join(
                [" " for index in range(self.subwin_width - 2 - len("API Status:"))]
            ),
        )
        self.api_monitor.addstr(
            2,
            (self.subwin_width - 1 - len("NG :" + message) - 1),
            "NG :" + message,
            curses.color_pair(2),
        )

        now = dt.datetime.now().strftime("%H:%M:%S")
        self.api_monitor.addstr(4, self.subwin_width - 1 - len(now) - 1, now)
        self.recent_pad.refresh()
        self.api_monitor.refresh()

    def update_rate_limit(self):
        self.api_monitor.addstr(
            7,
            1 + len("Rate Limit [/15min]:"),
            "".join(
                [
                    " "
                    for index in range(
                        self.subwin_width - 2 - len("Rate Limit [/15min]:")
                    )
                ]
            ),
        )
        self.api_monitor.addstr(
            7,
            self.subwin_width - 1 - len(str(self.ratelimit_statuses[0])) - 1,
            str(self.ratelimit_statuses[0]),
        )

        self.api_monitor.addstr(
            8,
            1 + len("Remaining:"),
            "".join(
                [" " for index in range(self.subwin_width - 2 - len("Remaining:"))]
            ),
        )
        self.api_monitor.addstr(
            8,
            self.subwin_width - 1 - len(str(self.ratelimit_statuses[1])) - 1,
            str(self.ratelimit_statuses[1]),
        )

        self.api_monitor.addstr(
            9,
            1 + len("Reset at:"),
            "".join([" " for index in range(self.subwin_width - 2 - len("Reset at:"))]),
        )
        reset_time = (
            dt.datetime.fromtimestamp(self.ratelimit_statuses[2])
            .astimezone(JST)
            .strftime("%H:%M:%S")
        )
        self.api_monitor.addstr(
            9, self.subwin_width - 1 - len(reset_time) - 1, str(reset_time)
        )

    def please_wait_view(self):
        height = int(MAIN_WIN_HEIGHT / 2)
        width = int(MAIN_WIN_WIDTH / 2)
        alert_message = "please wait"
        alert = self.window.derwin(height, width, int(height / 2), int(width / 2))
        alert.clear()
        alert.bkgd(" ", curses.color_pair(4))
        alert.addstr(
            int(height / 2),
            int(width / 2) - len(alert_message),
            alert_message,
            curses.A_BOLD,
        )
        alert.border()
        alert.refresh()


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
