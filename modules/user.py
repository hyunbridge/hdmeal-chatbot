# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/user.py - 사용자 관리 및 인증을 담당하는 스크립트입니다.

import hashlib
import os
import pyodbc
from modules import log

dbconf = ('DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s'
          % (os.getenv("DB_SERVER"), os.getenv("DB_NAME"), os.getenv("DB_UID"), os.getenv("DB_PWD")))


# 사용자 정보 읽기
def get_user(uid, req_id):
    log.info("[#%s] get_user@modules/user.py: Started Fetching User Info" % req_id)

    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & DB 검색
    with pyodbc.connect(dbconf) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM Users WHERE UID = '%s';" % enc_uid)
        data = curs.fetchone()  # 튜플로 저장됨 - (UID, Grade, Class)

    # 응답 데이터 작성
    return_data = list()
    if data is None:  # 사용자 정보 없을 경우
        return_data.append(None)
        return_data.append(None)
        log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
    else:
        return_data.append(data[1])
        return_data.append(data[2])
        log.info("[#%s] get_user@modules/user.py: Succeeded" % req_id)
    return return_data


# 사용자 생성 및 수정
def manage_user(uid, user_grade, user_class, req_id):
    user_grade = int(user_grade)
    user_class = int(user_class)

    log.info("[#%s] manage_user@modules/user.py: Started Managing User Info" % req_id)

    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & 작업 수행
    with pyodbc.connect(dbconf) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM Users WHERE UID = '%s';" % enc_uid)
        data = curs.fetchone()
        if data is None:  # 사용자 정보 없을 때 - 생성
            sql = "INSERT INTO Users VALUES ('%s', '%s', '%s', 0);" % (enc_uid, user_grade, user_class)
            log.info("[#%s] manage_user@modules/user.py: Registered" % req_id)
            return_msg = "Registered"
        elif data[1] == user_grade and data[2] == user_class:  # 사용자 정보 똑같을 때 - 아무것도 안 함
            log.info("[#%s] manage_user@modules/user.py: Same" % req_id)
            return "Same"
        else:  # 사용자 정보 있고 같지도 않을 때 - 업데이트
            sql = "UPDATE Users SET Grade = '%s', Class = '%s'  WHERE UID = '%s';" % (user_grade, user_class, enc_uid)
            log.info("[#%s] manage_user@modules/user.py: Updated" % req_id)
            return_msg = "Updated"
        curs.execute(sql)
        conn.commit()
    return return_msg


# 사용자 삭제
def delete_user(uid, req_id):
    log.info("[#%s] delete_user@modules/user.py: Started Deleting User Info" % req_id)

    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & 작업 수행
    with pyodbc.connect(dbconf) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM Users WHERE UID = '%s';" % enc_uid)
        data = curs.fetchone()
        if data is None:  # 사용자 정보 없을 때
            log.info("[#%s] delete_user@modules/user.py: No User Info" % req_id)
            return "NotExist"
        curs.execute("DELETE FROM Users WHERE UID = '%s';" % enc_uid)
        conn.commit()
    log.info("[#%s] delete_user@modules/user.py: Failed" % req_id)
    return "Deleted"


# 관리자 인증
def auth_admin(uid, req_id):
    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & DB 검색
    with pyodbc.connect(dbconf) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM Users WHERE UID = '%s';" % enc_uid)
        data = curs.fetchone()  # 튜플로 저장됨 - (UID, Grade, Class)

    # 응답 데이터 작성
    if data[3] == 1:
        log.info("[#%s] auth_admin@modules/user.py: Match" % req_id)
        return True
    else:
        log.info("[#%s] auth_admin@modules/user.py: Not Match" % req_id)
        return False


# 디버그
if __name__ == "__main__":
    log.init()
    # 0 - GetUser, 1 - ManageUser, 2 - DeleteUser
    flag = 2
    user_id = "uid"
    user_grade = 3
    user_class = 11

    if flag == 0:
        print(get_user(user_id, "****DEBUG****"))
    elif flag == 1:
        print(manage_user(user_id, user_grade, user_class, "****DEBUG****"))
    elif flag == 2:
        print(delete_user(user_id, "****DEBUG****"))
    elif flag == 3:
        print(auth_admin(user_id, "****DEBUG****"))
