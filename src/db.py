"""db

sqlite3のデータベースを使う部分の関数をまとめたモジュール
"""
import sqlite3
from contextlib import closing

DBPATH = "gbf_search.sqlite"
GET_BOSS_CATTEGORIRS = "SELECT * FROM boss_categories ORDER BY id ASC"
GET_BOSSLIST_BY_ID = "SELECT * FROM boss_name WHERE category = ?;"
LOG_BATTLEID_QUERY = "insert into temp_logged values (?,?)"
CLEAR_LOG_QUERY = "delete from temp_logged"


def get_bosscategories():
    """get_bosscategories

    データベースからマルチボスカテゴリをすべて取得する

    Returns:
        list: [{'id': 1, 'category_name': 'name'}, ...]

    Returns:
        sqlite3.OperationalError: SQLファイルが見つからないとき
    """
    with closing(sqlite3.connect(DBPATH)) as connection:
        cursor = connection.cursor()
        cursor.execute(GET_BOSS_CATTEGORIRS)
        data = cursor.fetchall()
    categories = []
    for category in data:
        categories.append({"id": category[0], "category_name": category[1]})
    return categories


def get_bosslist_by_id(id: int):
    """get_bosslist_by_id

    データベースから指定されたカテゴリのマルチボスをすべて取得する

    Args:
        id(int): 取得するボスのカテゴリーid
    Returns:
        list: [{'id': 0, 'boss_name': 'name', 'search_query': 'query'}, ...]

    Returns:
        sqlite3.OperationalError: SQLファイルが見つからないとき
    """
    with closing(sqlite3.connect(DBPATH)) as connection:
        cursor = connection.cursor()
        params = (id,)
        cursor.execute(GET_BOSSLIST_BY_ID, params)
        data = cursor.fetchall()
    bossdata_list = []
    for boss_list in data:
        bossdata_list.append(
            {
                "id": boss_list[0],
                "boss_name": boss_list[1],
                "search_query": boss_list[2],
            }
        )
    return bossdata_list


def clear_logged_battle_id():
    """clear_logged_battle_id

    一時記憶テーブルに記錄された救援IDをすべて削除する

    Returns:
        sqlite3.OperationalError: SQLファイルが見つからないとき
    """
    with closing(sqlite3.connect(DBPATH)) as connection:
        cursor = connection.cursor()
        cursor.execute(CLEAR_LOG_QUERY)
        connection.commit()


def log_battle_id(battle_id: str, tweet_date: str):
    """log_battle_id

    使用する救援IDをDBに記錄する。

    Args:
        battle_id(str): 記錄する救援ID
        tweet_date(str): 対象のIDが記錄されていたtweetが投稿されていた時間
    Return:
        bool: 重複せず記錄できたか
    """
    with closing(sqlite3.connect(DBPATH)) as connection:
        cursor = connection.cursor()
        try:
            params = (battle_id, tweet_date)
            cursor.execute(LOG_BATTLEID_QUERY, params)
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False


if __name__ == "__main__":
    print(get_bosslist_by_id(1))
