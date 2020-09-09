import sqlite3

# データベースファイルのパス
dbpath = 'gbf_search.sqlite'
connection = sqlite3.connect(dbpath)
cursor = connection.cursor()

def get_bosscategories():
    cursor.execute('SELECT * FROM boss_categories ORDER BY id ASC')
# 全件取得は cursor.fetchall()
    res = cursor.fetchall()
    data = res
    categories = []
    for category in data :
        categories.append({'id':category[0],'category_name':category[1]})
    return categories

def get_bosslist_by_id(id: int):
    ids = (id,)
    cursor.execute('SELECT boss_name.id,boss_name.name,boss_name.search_query FROM boss_name LEFT OUTER JOIN boss_categories ON boss_name.category = boss_categories.id WHERE boss_categories.id = ?;',ids)
    res = cursor.fetchall()
    data = res
    bossdata_list = []
    for boss_list in data :
        bossdata_list.append({'id':boss_list[0],'boss_name':boss_list[1],'search_query':boss_list[2]})
    return bossdata_list
