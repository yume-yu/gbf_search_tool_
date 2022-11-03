"""
tweet取得からIDコピまでの処理を行なうThread拡張クラスを定義する
Attributes:
    JST (dt.timezone): "Asia/Tokyo"のタイムゾーンオブジェクト
"""
import datetime as dt
import json
import time
import uuid
from multiprocessing import Process
from threading import Thread

import pyperclip

import tweet as tm
from db import clear_logged_battle_id, log_battle_id
from status_monitor import StatusMonitor
from util import DEFAULT_INTERVAL, JST, TWEET_ID_BUFFER, Error, get_rescue_ID


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

    def __init__(self, search_query, monitor: StatusMonitor = None):
        """
        Args:
            search_query(str): tweet検索に使う文字列
        """
        super().__init__()
        self.daemon = True
        self.running_flag = True
        self.interval = DEFAULT_INTERVAL
        self.search_query = search_query
        self.status_monitor = monitor
        self.since_id = "0"
        clear_logged_battle_id()

    def run(self):
        """run

        run this therad.
        """
        while True:
            self.get_battle_id_from_twitter()
            if self.running_flag:
                time.sleep(10) # 15min
                #time.sleep(900) # 15min
            else:
                break

    def stop(self):
        """stop

        このスレッドを停止する。
        """
        self.running_flag = False

    def update_monitor(self, **status):
        """update_monitor

        ステータス表示を更新する

        Args:
            newid (str): 今回取得した救援ID
            date (dt.datetime): 対象のツイートが投稿された時間
            status_code (int): エラー時のHTTPStatusCode
        """
        refresh_thread = RefreshStatusMonitor(
            status_window=self.status_monitor, **status
        )
        refresh_thread.start()

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
            tweet = tm.Tweet()
            tweet.clear_filter_rule()
            tweet.add_filter_rule(tag=str(uuid.uuid4()), value=f'({self.search_query}) -is:retweet')
            with tweet.open_filtered_stram(params={'tweet.fields':'created_at,text'}) as stream:

                for chunk in stream.iter_lines():
                    try:
                        Thread(target=self.find_new_tweet, args=[chunk]).run()
                    except AttributeError:
                        if 'connection_issue' in chunk.decode('utf-8'):
                            raise tm.RequestFaildError(status_code=429)
                            break
                    except json.decoder.JSONDecodeError:
                        if len(chunk) != 0:
                            pass
                        else:
                            pass
                    if not self.running_flag:
                        break

        except tm.RequestFaildError as faild:
            self.update_monitor(error=faild)

    def find_new_tweet(self, chunk):
        tweet = json.loads(chunk).get('data')
        _, battle_id = get_rescue_ID(tweet.get("text"))
        tweet_date = dt.datetime.fromisoformat(tweet.get("created_at").replace('Z', '+00:00')).astimezone(JST)
        pyperclip.copy(battle_id)
        self.update_monitor(newid=battle_id, date=tweet_date)
        self.update_monitor(interval=self.interval)

class RefreshStatusMonitor(Thread):
    """
    Check_tweetスレッドの状態/情報表示を行なうスレッド
    """

    def __init__(self, status_window: StatusMonitor = None, **status):
        super().__init__()
        self.daemon = True
        self.running_flag = True
        self.api_status = True
        self.monitor = status_window
        self.status = status

    def run(self):
        self.update_monitor()

    def update_monitor(self):
        if self.monitor:
            self.update_status_window()
        else:
            self.print_status()

    def update_status_window(self):
        if self.status.get("error"):
            self.monitor.error_update(self.status.get("error"))
        elif self.status.get("interval"):
            self.monitor.update_request_status(interval=self.status.get("interval"))
        elif self.status.get("newid"):
            self.monitor.update_recent_log(
                battle_id=self.status.get("newid"),
                tweet_date=self.status.get("date"),
                now=dt.datetime.now().astimezone(JST),
            )
        elif self.status.get("limit"):
            self.monitor.update_rate_limit(
                limit=self.status.get("limit"),
                remaining=self.status.get("remaining"),
                reset=dt.datetime.fromtimestamp(
                    int(self.status.get("reset"))
                ).astimezone(JST),
            )

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


class CheckRateLimit(Process):
    """
    TwitterAPIのsearch/tweetのAPI Rate Linitを取得するProcess拡張クラス

    Attributes:
        running_flag(bool): プロセスを維持するかどうかのフラグ
        statuses(multiprocessing.Array): RateLimitの状況を記錄したリスト [Limit, Remaining, ResetAt]
    """

    def __init__(self, statuses):
        super().__init__()
        self.daemon = True
        self.running_flag = True
        self.statuses = statuses

    def stop(self):
        """stop

        このスレッドを停止する。
        """
        self.running_flag = False

    def run(self):
        tweet = tm.Tweet()
        while self.running_flag:
            try:
                limit_info = tweet.get_rate_limits().get("tweets").get("/tweets/search/stream")
                self.update_status(**limit_info)
            except tm.RequestFaildError:
                pass
            time.sleep(5)

    def update_status(self, limit=None, remaining=None, reset=None):
        """update_status

        自身のRateLimit情報を更新する

        Args:
            limit(int): 規定された15分ごとのリクエスト許可回数
            remaining(int): resetの時間までに許可されたリクエストの回数
            reset(int): 次にremaingがリセットされる時間のunixtime
        """
        self.statuses[0] = limit
        self.statuses[1] = remaining
        self.statuses[2] = reset

    def update_monitor(self, **status):
        """update_monitor

        /search/tweets のRateLimit表示を更新する

        Args:
            limit(int): APIの許容リクエスト数
            remaining(int): 一定時間内にリクエスト可能な残り回数
            reset(int): リクエスト可能回数のリセット日時のunixtime
        """
        refresh_thread = RefreshStatusMonitor(
            status_window=self.status_monitor, **status
        )
        refresh_thread.start()


if __name__ == "__main__":
    str_q = '"Lvl 200 Akasha" OR "Lv200 アーカーシャ"'
    # str_q = "わーい"
    print(str_q)
    ct = CheckTweet(str_q)
    ct.start()
    while True:
        time.sleep(1000000)
