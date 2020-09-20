import re

import toml

# tweet取得系定数
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
TWEET_LIMIT = 0
DEFAULT_INTERVAL = 9999999
SUPPORT_MULTIBYTE = None
TWEET_ID_BUFFER = 0
GLOBAL_PARAMS = "global"
STANDARD_SEARCH_API_TOKENS = "APIkeys"
ID_EXTRACTION_PATTERN = re.compile(".*(?P<ID>[A-F0-9]{8}) :")

# 表示系定数
MAIN_WIN_WIDTH = 80
TOP_PART_HEIGHT = 4
MIDDLE_PART_HEIGHT = 11
BOTTOM_PART_HEIGHT = 4
MAIN_WIN_HEIGHT = TOP_PART_HEIGHT + MIDDLE_PART_HEIGHT + BOTTOM_PART_HEIGHT

configs = toml.load("./config.toml")


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


def setup():
    # 一般設定読み込み
    global TWEET_LIMIT, SUPPORT_MULTIBYTE, DEFAULT_INTERVAL, TWEET_ID_BUFFER

    TWEET_LIMIT = configs.get(GLOBAL_PARAMS).get("Tweet_limit")
    SUPPORT_MULTIBYTE = configs.get(GLOBAL_PARAMS).get("Support_Muiltibyte")
    DEFAULT_INTERVAL = configs.get(GLOBAL_PARAMS).get("Default_interval")
    TWEET_ID_BUFFER = configs.get(GLOBAL_PARAMS).get("Tweet_id_buffer")

    # APIキーの設定読み込み
    global CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

    standardAPI_token = configs.get(STANDARD_SEARCH_API_TOKENS)

    CONSUMER_KEY = standardAPI_token.get("API_Key")
    CONSUMER_SECRET = standardAPI_token.get("API_Key_Secret")
    ACCESS_TOKEN = standardAPI_token.get("Accsess_Token")
    ACCESS_TOKEN_SECRET = standardAPI_token.get("Accsess_Token_Secret")


def get_rescue_ID(tweet_text: str):
    try:
        found_id = re.match(ID_EXTRACTION_PATTERN, tweet_text).group("ID")
    except AttributeError:
        return (False, None)
    else:
        return (True, found_id)


def format_string_for_addstr(string4print: str):
    if SUPPORT_MULTIBYTE:
        return string4print
    else:
        return " ".join(list(string4print)) + " "


def gbss_addstr(window, y, x, string, attr=0):
    window.addstr(y, x, format_string_for_addstr(string), attr)


setup()

if __name__ == "__main__":
    print(CONSUMER_KEY)
    print(CONSUMER_SECRET)
    print(ACCESS_TOKEN)
    print(ACCESS_TOKEN_SECRET)
    print(TWEET_LIMIT)
    print(SUPPORT_MULTIBYTE)
    print(DEFAULT_INTERVAL)
