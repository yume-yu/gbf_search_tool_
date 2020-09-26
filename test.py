# -*- coding: utf-8 -*-

import json
import re
import time
from pprint import pprint

import pyperclip
from requests_oauthlib import OAuth1Session
# import config
from util import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY,
                  CONSUMER_SECRET, TWEET_LIMIT, get_rescue_ID)

# Twitter Endpoint(検索結果を取得する)
SEARCH_API_URL = "https://api.twitter.com/1.1/search/tweets.json"

session = None


def init_sesstion():
    twitter = OAuth1Session(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    return twitter


def search_tweet(session: OAuth1Session, keyword: str):

    params = {"count": TWEET_LIMIT, "q": keyword}  # 取得するtweet数  # 検索キーワード

    req = session.get(SEARCH_API_URL, params=params)

    if req.status_code == 200:
        res = json.loads(req.text)
        return res["statuses"]
    else:
        print("Failed: %d" % req.status_code)


if __name__ == "__main__":
    # Enedpointへ渡すパラメーター
    keyword = "'LV150 Tiamat Malice' OR 'Lv150 ティアマト・マリス'"
    session = init_sesstion()

    while True:
        if not session.authorized or session is None:
            session = init_sesstion()

        tweets = search_tweet(session, keyword)

        search = re.compile(".*(?P<ID>[A-F0-9]{8}) :")
        for tweet in tweets:
            try:
                fount_flag, id = get_rescue_ID(tweet["text"])
                if fount_flag:
                    print(tweet["text"])
                    print("ID -> " + id)
            except AttributeError:
                # 該当Tweetが救援じゃなかったときの対応
                pass
            print("-------------------------------------------")

        time.sleep(1)
