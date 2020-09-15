import sqlite3

# データベースファイルのパス
DBPATH = "gbf_search.sqlite"
GET_BOSS_CATTEGORIRS = "SELECT * FROM boss_categories ORDER BY id ASC"
GET_BOSSLIST_BY_ID = "SELECT boss_name.id,boss_name.name,boss_name.search_query FROM boss_name LEFT OUTER JOIN boss_categories ON boss_name.category = boss_categories.id WHERE boss_categories.id = ?;"


def get_bosscategories():
    connection = sqlite3.connect(DBPATH)
    cursor = connection.cursor()
    cursor.execute(GET_BOSS_CATTEGORIRS)
    # 全件取得は cursor.fetchall()
    data = cursor.fetchall()
    categories = []
    for category in data:
        categories.append({"id": category[0], "category_name": category[1]})
    return categories


def get_bosslist_by_id(id: int):
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
