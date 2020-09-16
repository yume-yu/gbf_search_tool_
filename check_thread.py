"""
tweet取得からIDコピまでの処理を行なうThread拡張クラスを定義する
"""
import time
from threading import Thread

import pyperclip

import tweet as tm
from db import clear_logged_battle_id, log_battle_id
from util import DEFAULT_INTERVAL, get_rescue_ID


class Check_tweet(Thread):
    """
    tweet取得からIDコピーまでの処理を停止されるまで行なうThread拡張クラス

    Attributes:
        running_flag (bool): threadの無限ループを維持するかのflag.Falseになるとループが止まりThreadが止まる
        interval (int): 救援IDの取得完了から次のtweet取得開始までのインターバル
        tweet (tweet.Tweet): Twitterのツイート取得オブジェクト
        search_query (str): tweet検索に使う文字列
        since_id (str): Tweet検索の際に基準にするTweetのid
    """

    def __init__(self, search_query):
        """
        Args:
            search_query(str): tweet検索に使う文字列
        """
        super().__init__()
        self.running_flag = True
        self.interval = DEFAULT_INTERVAL
        self.tweet = tm.Tweet()
        self.search_query = search_query
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
        self.running_flag = False

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
        tweets = self.tweet.search_tweet(self.search_query, self.since_id)
        battle_id = None
        for tweet in tweets:
            _, battle_id = get_rescue_ID(tweet.get("text"))
            tweet_date = tweet.get("created_at")
            if log_battle_id(battle_id, tweet_date):
                self.since_id = tweet.get("id")
                pyperclip.copy(battle_id)
                break


if __name__ == "__main__":
    str_q = '"Lvl 200 Akasha" OR "Lv200 アーカーシャ"'
    # str_q = "わーい"
    print(str_q)
    ct = Check_tweet(str_q)
    ct.start()
    while True:
        print("yes")
        time.sleep(2)
