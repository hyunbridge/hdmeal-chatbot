# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# migrator.py - json 파일에 저장된 사용자 정보를 SQLite DB로 옮겨 주는 스크립트입니다.

import json
import sqlite3

conn = sqlite3.connect('../data/user/user.db')
curs = conn.cursor()
with open('../data/user/user.json', encoding="utf-8") as data_file:
    data = json.load(data_file)
    for i in data.keys():
        curs.execute("INSERT INTO User VALUES ('%s', '%s', '%s');" % (i, data[i][0], data[i][1]))
curs.execute("DELETE FROM User WHERE UID = 'Encrypted UID';")
conn.commit()
conn.close()