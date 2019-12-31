# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# exec/migrator.py - json 파일에 저장된 사용자 정보를 SQLite DB로 옮겨 주는 스크립트입니다.

import json
'''
import os
import pyodbc


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s'
                      % (os.getenv("DB_SERVER"), os.getenv("DB_NAME"), os.getenv("DB_UID"), os.getenv("DB_PWD")))
curs = conn.cursor()
with open('../data/user/user.json', encoding="utf-8") as json_users:
    with open('../data/user/admin.json', encoding="utf-8") as json_admins:
        users = json.load(json_users)
        admins = json.load(json_admins)
        for i in users.keys():
            if i == "Encrypted UID":
                continue
            if i in admins:
                isadmin = 1
            else:
                isadmin = 0
            curs.execute("INSERT INTO Users VALUES ('%s', '%s', '%s', '%s');" % (i, int(users[i][0]), int(users[i][1]), isadmin))
conn.commit()
conn.close()
'''

with open('db.json', encoding="utf-8") as json_db:
    db = json.load(json_db)
    users = dict()
    admins = list()
    for item in db:
        users[item["UID"]] = [item["Grade"], item["Class"]]
        if item["Admin"] == "1":
            admins.append(item["UID"])
    with open('../data/user/user.json', "w", encoding="utf-8") as json_users:
        json.dump(users, json_users, ensure_ascii=False, indent="\t")
    with open('../data/user/admin.json', "w", encoding="utf-8") as json_admins:
        json.dump(admins, json_admins, ensure_ascii=False, indent="\t")
