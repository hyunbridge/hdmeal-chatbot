# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# exec/dbinit.py - DB를 생성하는 스크립트입니다.

import os
import pyodbc


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s'
                      % (os.getenv("DB_SERVER"), os.getenv("DB_NAME"), os.getenv("DB_UID"), os.getenv("DB_PWD")))
curs = conn.cursor()
curs.execute(
    'create table Users (UID nchar(64) NOT NULL, Grade tinyint NOT NULL, Class tinyint NOT NULL, Admin bit NOT NULL)')
conn.commit()
conn.close()
