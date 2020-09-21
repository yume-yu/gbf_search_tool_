"""
tweet取得からIDコピまでの処理を行なうThread拡張クラスを定義する
Attributes:
    JST (dt.timezone): "Asia/Tokyo"のタイムゾーンオブジェクト
"""
import curses
import datetime as dt
import time
from threading import Thread

import pyperclip

import tweet as tm
from db import clear_logged_battle_id, log_battle_id
from util import DEFAULT_INTERVAL, TWEET_ID_BUFFER, get_rescue_ID

JST = dt.timezone(dt.timedelta(hours=9))


class CheckTweet(Thread):
    """
    tweet取得からIDコピーまでの処理を停止されるまで行なうThread拡張クラス

    Attributes:
        TWEET_DATETIME_FORMAT (str): Tweet情報に含まれる投稿時間をdatetimeにパースするためのフォーマット
        running_flag (bool): threadの無限ループを維持するかのflag.Falseになるとループが止まりThreadが止まる
        interval (int): 救援IDの取得完了から次のtweet取得開始までのインターバル
        tweet (tweet.Tweet): Twitterのツイート取得オブジェクト
        search_query (str): tweet検索に使う文字列
        since_id (str): Tweet検索の際に基準にするTweetのid
    """

    TWEET_DATETIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"

    def __init__(self, search_query, monitor: curses.window = None):
        """
        Args:
            search_query(str): tweet検索に使う文字列
        """
        super().__init__()
        self.daemon = True
        self.running_flag = True
        self.interval = DEFAULT_INTERVAL
        self.tweet = tm.Tweet()
        self.search_query = search_query
        self.status_monitor = monitor
        self.since_id = "0"
        clear_logged_battle_id()

    def run(self):
        """run

        run this therad.
        """
        while self.running_flag:
            self.get_battle_id_from_twitter()
            time.sleep(self.interval)

    def stop(self):
        """stop

        このスレッドを停止する。
        """
        self.status_monitor.stop()
        self.running_flag = False

    def update_monitor(self, **status):
        """update_monitor

        ステータス表示を更新する

        Args:
            newid (str): 今回取得した救援ID
            date (dt.datetime): 対象のツイートが投稿された時間
            status_code (int): エラー時のHTTPStatusCode
        """
        status_monitor = Check_tweet_status_monitor(
            status_window=self.status_monitor, **status
        )
        status_monitor.start()

    def update_interval(self, seconds: float):
        """update_interval

        Tweetの取得間隔を引数の値[s]に更新する

        Args:
            seconds(float): 新しく設定するTweetの取得間隔の秒数

        Raises:
            ValueError: 0以下の値が与えられたとき
        """
        if seconds > 0:
            self.interval = seconds
        else:
            raise ValueError("{} is invalid interval.".format(seconds))

    def get_battle_id_from_twitter(self):
        """get_battle_id_from_twitter

        ツイートを検索して、重複のないツイートが見つかったらクリップボードへ挿入する
        """
        try:
            tweets = self.tweet.search_tweet(self.search_query, self.since_id)
            battle_id = None
            for tweet in tweets:
                _, battle_id = get_rescue_ID(tweet.get("text"))
                tweet_date = dt.datetime.strptime(
                    tweet.get("created_at"), self.TWEET_DATETIME_FORMAT
                ).astimezone(JST)
                if log_battle_id(battle_id, tweet_date.isoformat()):
                    # IDのみの指定だと取得漏れが発生しやすくなるので取得開始位置にバッファをもたせる
                    self.since_id = str(tweet.get("id") - TWEET_ID_BUFFER)
                    pyperclip.copy(battle_id)
                    self.update_monitor(newid=battle_id, date=tweet_date)
                    break
        except tm.RequestFaildError as faild:
            self.update_monitor(status_code=faild.status_code)


class Check_tweet_status_monitor(Thread):
    """
    Check_tweetスレッドの状態/情報表示を行なうスレッド
    """

    def __init__(self, status_window: curses.window = None, **status):
        super().__init__()
        self.daemon = True
        self.running_flag = True
        self.api_status = True
        self.monitor = status_window
        self.status = status
        self.status_updated_flag = True

    def run(self):
        self.update_monitor()

    def update_monitor(self):
        if self.monitor:
            pass
        else:
            self.print_status()

    def update_status_window(self):
        pass

    def print_status(self):
        if self.status.get("error"):
            print("API status: NG ({})".format((self.status.get("error").status_code)))
        elif self.status.get("newid"):
            print("API status: OK")
            print("ID: {}".format(self.status.get("newid")))
            print(
                "delay: {}".format(
                    dt.datetime.now().astimezone(JST) - self.status.get("date")
                )
            )
        print("last update: {}".format(dt.datetime.now().astimezone(JST)))
        print("------------------------------------------")


if __name__ == "__main__":
    str_q = '"Lvl 200 Akasha" OR "Lv200 アーカーシャ"'
    # str_q = "わーい"
    print(str_q)
    ct = CheckTweet(str_q)
    ct.start()
    while True:
        time.sleep(1000000)
