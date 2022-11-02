import json
from http import HTTPStatus

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth1Session, OAuth2Session

from util import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY,
                  CONSUMER_SECRET, TWEET_LIMIT, USE_USER_OAUTH, Error)


class Tweet:
    """
        Twitter Standard Search APIへリクエストを行うためのクラス

    Attributes:
        SEARCH_API_URL: Twitter Standard Search API のリクエストUrl
    """

    # Twitter Endpoint
    TOKEN_OAUTH_URL = "https://api.twitter.com/oauth2/token"
    FILTER_RULE_URL = 'https://api.twitter.com/2/tweets/search/stream/rules'
    FILTERED_STREAM_URL = 'https://api.twitter.com/2/tweets/search/stream'
    SEARCH_API_URL = "https://api.twitter.com/1.1/search/tweets.json"
    RATE_LIMIT_URL = "https://api.twitter.com/1.1/application/rate_limit_status.json"

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
        if USE_USER_OAUTH:
            twitter = OAuth1Session(
                CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
            )
            return twitter
        else:
            # 初回のトークン取得
            client = BackendApplicationClient(client_id=CONSUMER_KEY)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(
                token_url=self.TOKEN_OAUTH_URL,
                client_id=CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
            )
            twitter = OAuth2Session(
                client=client,
                token=token,
                auto_refresh_url=self.TOKEN_OAUTH_URL,
                auto_refresh_kwargs={
                    "client_id": CONSUMER_KEY,
                    "client_secret": CONSUMER_SECRET,
                },
            )
            return twitter

    def get_filter_rule(self):
        """get_filter_rule

        現在登録されているFilter ruleを取得する
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream-rules

        Returns:
            dict: APIから返されたレスポンス

        Examples:
            ```python
            tw = Tweet()
            response = tw.get_filter_rule()
            pprint(response)
            > {'data': [{'id': '1587836298793914369',
            >            'tag': 'tuyo',
            >            'value': '("Lvl 150 Proto Bahamut") '
            >                     '-is:retweet'}],
            >  'meta': {'result_count': 1, 'sent': '2022-11-02T15:57:29.101Z'}}
            ```

        """
        filters = []
        with self.session.get(url=self.FILTER_RULE_URL) as res:
            filters = json.loads(res.text)

        return filters

    def add_filter_rule(self, **kargs):
        """add_filter_rule

        指定したルールを追加する。filtersでlistが渡されているときはその内容を追加する。
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules

        Args:
            filters(list<dict>): {name: '[filter name]', find_value: '[find me]'} のリスト
            tag(str): 追加するフィルターの名前
            value(str): 検索文字列

        Returns:
            dict: APIから返されたレスポンス

        Examples:
            ```python
            tw = Tweet()
            response = tw.get_filter_rule()
            pprint(response)
            > {'data': [{'id': '1587836298793914369',
            >            'tag': 'tuyo',
            >            'value': '("Lvl 150 Proto Bahamut") '
            >                     '-is:retweet'}],
            >  'meta': {'result_count': 1, 'sent': '2022-11-02T15:57:29.101Z'}}
            ```

        """
        add = []
        if kargs.get('filters'):
            add = kargs.get('filters')
        else:
            add.append({
                'value': kargs.get('value'),
                'tag': kargs.get('tag')
            })
        data = {
            'add': add
        }
        with self.session.post(url=self.FILTER_RULE_URL, json=data) as res:
            return res

    def delete_filter_rule(self, ids: list):
        """delete_filter_rule

        引数で指定されたidを持つFilterRuleを削除する
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules

        Args:
            ids(list<str>): 削除するルールのidを持ったリスト

        Returns:
            dict: APIから返されたレスポンス

        Examples:
            ```python
            tw = Tweet()
            target_ids = ['1587836298793914369']
            response = tw.delete_filter_rule(target_ids)
            pprint(filter)
            > {'meta': {'sent': '2022-11-02T16:14:43.430Z',
            >          'summary': {'deleted': 1, 'not_deleted': 0}}}
            ```

        """
        data = {
            'delete':{
                'ids': ids
            }
        }
        with self.session.post(url=self.FILTER_RULE_URL, json=data) as res:
            return res

    def clear_filter_rule(self):
        """clear_filter_rule

        現在のFilterRuleをすべて削除する

        Returns:
            dict: APIから返されたレスポンス

        Examples:
            ```python
            tw = Tweet()
            target_ids = ['1587836298793914369']
            response = tw.delete_filter_rule(target_ids)
            pprint(filter)
            > {'meta': {'sent': '2022-11-02T16:14:43.430Z',
            >          'summary': {'deleted': 1, 'not_deleted': 0}}}
            ```
        """
        filters = self.get_filter_rule()
        if filters.get('data'):
            ids = [filter.get('id') for filter in filters.get('data')]
            self.delete_filter_rule(ids)

    def open_filtered_stram(self, params: dict = None):
        """open_filtered_stram

        FilteredStreamを開く。
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream
        Args:
            params(dict): APIを利用する際のパラメータ。取得するTweetの情報などが指定できる

        Returns:
            requests.models.Response: Getリクエストが維持されているHttpStream
        """
        return self.session.get(url=self.FILTERED_STREAM_URL, stream=True, params=params)

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

        params = {
            "count": TWEET_LIMIT,
            "q": keyword,
            "since_id": since_id,
            "result_type": "recent",
        }

        req = self.session.get(self.SEARCH_API_URL, params=params)

        if req.status_code == 200:
            res = json.loads(req.text)
            return res["statuses"]
        else:
            raise RequestFaildError(req.status_code)

    def get_rate_limits(self):
        """get_rate_limits

        Twitter APIからRate Limitの情報を取得する

        Returns:
            dict: API Rate limitの情報

        Raises:
            RequestFaildError: 何らかの理由でリクエストに失敗したとき

        """

        req = self.session.get(self.RATE_LIMIT_URL)

        if req.status_code == 200:
            res = json.loads(req.text)
            return res.get("resources")
        else:
            raise RequestFaildError(req.status_code, req.text)
        pass


class RequestFaildError(Error):
    """
    Twitterへのリクエストが失敗したとき発生するエラー

    Attributes:
        status_code: エラーのhttpステータスコード
        sumally: エラーの概要
        description: エラーの詳細
    """

    def __init__(self, status_code: int, message=None):
        self.status_code = status_code
        self.sumally, self.description = self.convert_status_code(status_code)
        if message:
            self.description = message

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

    from pprint import pprint
    from datetime import datetime as dt

    tw = Tweet()
    url = 'https://api.twitter.com/2/tweets/search/stream'
    tw.clear_filter_rule()
    pprint(tw.add_filter_rule(tag='hoge', value='("Lvl 150 Proto Bahamut" OR "Lv150 プロトバハムート") -is:retweet').text)
    # pprint(tw.get_filter_rule())
    res = tw.open_filtered_stram()
    print(type(res))
    for chunk in res.iter_lines():
        if len(chunk) != 0:
            pprint(json.loads(chunk))
            print(json.loads(chunk).get('data').get('text'))

    pprint(tw.get_rate_limits().get("application"))
    pprint(tw.get_rate_limits().get("search"))
    unixtime = tw.get_rate_limits().get("search").get("/search/tweets").get("reset")
    print(dt.fromtimestamp(unixtime))
    try:
        raise RequestFaildError(406)
    except RequestFaildError as rf:
        print(rf.description)

