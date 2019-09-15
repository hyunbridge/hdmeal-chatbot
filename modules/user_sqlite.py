# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# user.py - 사용자 관리 및 인증을 담당하는 스크립트입니다.

import json
import hashlib
import sqlite3

path = "data/user/user.db"
admin_path = "data/user/admin.json"


# 사용자 정보 읽기
def get_user(uid):
    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & DB 검색
    conn = sqlite3.connect(path)
    curs = conn.cursor()
    curs.execute("SELECT * FROM User WHERE UID = '%s';" % enc_uid)
    data = curs.fetchone()  # 튜플로 저장됨 - (UID, Grade, Class)
    conn.close()

    # 응답 데이터 작성
    return_data = list()
    if data is None:  # 사용자 정보 없을 경우
        return_data.append(None)
        return_data.append(None)
    else:
        return_data.append(data[1])
        return_data.append(data[2])
    return return_data


# 사용자 생성 및 수정
def manage_user(uid, user_grade, user_class):
    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & 작업 수행
    conn = sqlite3.connect(path)
    curs = conn.cursor()
    curs.execute("SELECT * FROM User WHERE UID = '%s';" % enc_uid)
    data = curs.fetchone()
    if data is None:  # 사용자 정보 없을 때 - 생성
        sql = "INSERT INTO User VALUES ('%s', '%s', '%s');" % (enc_uid, user_grade, user_class)
        return_msg = "Created"
    elif data[1] == user_grade and data[2] == user_class:  # 사용자 정보 똑같을 때 - 아무것도 안 함
        return "Same"
    else:  # 사용자 정보 있고 같지도 않을 때 - 업데이트
        sql = "UPDATE User SET Grade = '%s', Class = '%s'  WHERE UID = '%s';" % (user_grade, user_class, enc_uid)
        return_msg = "Updated"
    curs.execute(sql)
    conn.commit()
    conn.close()
    return return_msg


# 사용자 삭제
def delete_user(uid):
    # UID 암호화
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    enc_uid = enc.hexdigest()

    # DB 연결 수립 & 작업 수행
    conn = sqlite3.connect(path)
    curs = conn.cursor()
    curs.execute("SELECT * FROM User WHERE UID = '%s';" % enc_uid)
    data = curs.fetchone()
    if data is None:  # 사용자 정보 없을 때
        return "NotExist"
    curs.execute("DELETE FROM User WHERE UID = '%s';" % enc_uid)
    conn.commit()
    conn.close()
    return "Deleted"


# 관리자 인증
def auth_admin(uid, debugging):
    with open(admin_path, encoding="utf-8") as data_file:
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        enc_uid = enc.hexdigest()
        data = json.load(data_file)
        if debugging:
            print(enc_uid)
            print(data)
        if enc_uid in data:
            return True
        else:
            return False


# 디버그
if __name__ == "__main__":
    # 0 - GetUser, 1 - ManageUser, 2 - DeleteUser
    flag = 1
    user_id = "uid"
    user_grade = "3"
    user_class = "11"

    path = "../data/user/user.db"
    admin_path = "../data/user/admin.json"
    if flag == 0:
        print(get_user(user_id))
    elif flag == 1:
        print(manage_user(user_id, user_grade, user_class))
    elif flag == 2:
        print(delete_user(user_id))
