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

# 사용자 정보 읽기
def get_user(uid, isDebugging):
    try:
        with open('data/user/user.json', encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
            if isDebugging:
                print(data)
            if not enc_uid in data:
                return Exception
            return_data = list()
            return_data.append(data[enc_uid][0])
            return_data.append(data[enc_uid][1])
            return return_data
    except Exception:
        return Exception

# 사용자 생성 및 수정
def manage_user(uid, user_grade, user_class, isDebugging):
    try:
        with open('data/user/user.json', encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
            if isDebugging:
                print(data)
            if enc_uid in data_file:
                delete_user(uid, isDebugging)
            user_data = list()
            user_data.append(user_grade)
            user_data.append(user_class)
            data[enc_uid] = user_data
        with open('data/user/user.json', "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            return True
    except Exception:
        return Exception

# 사용자 삭제
def delete_user(uid, isDebugging):
    try:
        with open('data/user/user.json', encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
            if enc_uid in data:
                if isDebugging:
                    print("DEL USER")
                del data[enc_uid]
            else:
                return Exception
        with open('data/user/user.json', "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            return True
    except Exception:
        return Exception

# 관리자 인증
def auth_admin(uid, isDebugging):
    with open('data/user/admin.json', encoding="utf-8") as data_file:
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        enc_uid = enc.hexdigest()
        data = json.load(data_file)
        if isDebugging:
            print(enc_uid)
            print(data)
        if enc_uid in data:
            return True
        else:
            return False

# 디버그
if __name__ == "__main__":
    manage_user("uid", "3", "11", True)