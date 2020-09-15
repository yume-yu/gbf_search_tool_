"""db

sqlite3のデータベースを使う部分の関数をまとめたモジュール
"""
import sqlite3
from contextlib import closing

DBPATH = "gbf_search.sqlite"
GET_BOSS_CATTEGORIRS = "SELECT * FROM boss_categories ORDER BY id ASC"
GET_BOSSLIST_BY_ID = "SELECT * FROM boss_name WHERE category = ?;"


def get_bosscategories():
    """get_bosscategories

    データベースからマルチボスカテゴリをすべて取得する

    Returns:
        list: [{'id': 1, 'category_name': 'name'}, ...]

    Returns:
        sqlite3.OperationalError: SQLに関連するすべてのエラー
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
        sqlite3.OperationalError: SQLに関連するすべてのエラー
    """
    with closing(sqlite3.connect(DBPATH)) as connection:
        connection = sqlite3.connect(DBPATH)
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


if __name__ == "__main__":
    print(get_bosslist_by_id(1))
