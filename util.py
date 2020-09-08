import toml
import re

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
TWEET_LIMIT = 0

GLOBAL_PARAMS = "global"
STANDARD_SEARCH_API_TOKENS = "APIkeys"

configs = toml.load("./config.toml")

ID_EXTRACTION_PATTERN = re.compile(".*(?P<ID>[A-F0-9]{8}) :")


def setup():
    # 一般設定読み込み
    global TWEET_LIMIT

    TWEET_LIMIT = configs.get(GLOBAL_PARAMS)

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
        return(False, None)
    else:
        return (True, found_id)


setup()
