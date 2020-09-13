import json
from http import HTTPStatus

from requests_oauthlib import OAuth1Session

from util import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY,
                  CONSUMER_SECRET, TWEET_LIMIT, Error)


class Tweet:
    """
        Twitter Standard Search APIへリクエストを行うためのクラス

    Attributes:
        SEARCH_API_URL: Twitter Standard Search API のリクエストUrl
    """

    # Twitter Endpoint(検索結果を取得する)
    SEARCH_API_URL = "https://api.twitter.com/1.1/search/tweets.json"

    def __init__(self):
        self.session = self.init_sesstion()

    def init_sesstion(self):
        """init_sesstion

        OAuthクライアントの初期化を行う

        Returns:
            設定から読み混んだキーを使ってクライアントを作成する

        Raise:
            AttributeError: 設定ファイルに適切なキーが存在しなかったとき
        """
        twitter = OAuth1Session(
            CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        return twitter

    def search_tweet(self, keyword: str, since_id: str = "0"):
        """search_tweet

            APIを利用してTwitter検索を行う

        Args:
            keyword (str): 検索ワード
            since_id (str): 検索の基準にするtweetのid.このidより新しいidのtweetを取得する.デフォルト値は0で全てのツイートを取得する。

        Returns:
            tweets: 取得したtweet群を含むdict

        Raises:
            RequestFaildError: 何らかの理由でリクエストに失敗したとき

        Examples:

        """

        params = {"count": TWEET_LIMIT, "q": keyword, "since_id": since_id}

        req = self.session.get(self.SEARCH_API_URL, params=params)

        if req.status_code == 200:
            res = json.loads(req.text)
            return res["statuses"]
        else:
            raise RequestFaildError(req.status_code)


class RequestFaildError(Error):
    """
    Twitterへのリクエストが失敗したとき発生するエラー

    Attributes:
        status_code: エラーのhttpステータスコード
        sumally: エラーの概要
        description: エラーの詳細
    """

    def __init__(self, status_code: int):
        self.status_code = status_code
        self.sumally, self.description = self.convert_status_code(status_code)

    def convert_status_code(self, status_code):
        """convert_status_code

        httpステータスコードをエラー内容に変換して返す

        Args:
            status_code: httpステータスコード

        Returns:
            tuple: エラー概要と詳細
        """
        status = HTTPStatus(status_code)
        return (status.phrase, status.description)


if __name__ == "__main__":
    try:
        raise RequestFaildError(406)
    except RequestFaildError as rf:
        print(rf.description)
