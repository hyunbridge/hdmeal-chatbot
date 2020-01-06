# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/user.py - 사용자 관리 및 인증을 담당하는 스크립트입니다.

import hashlib
import json
import os
import jwt
import requests
from modules import log

path = "data/user/user.json"
admin_path = "data/user/admin.json"
jwt_secret = os.getenv("SERVER_SECRET")
recaptcha_secret = os.getenv("RECAPTCHA_SECRET")

# 사용자 정보 읽기
def get_user(uid, req_id, debugging):
    log.info("[#%s] get_user@modules/user.py: Started Fetching User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
        if debugging:
            print(data)
        if not enc_uid in data:  # 사용자 정보 없을 때
            return_data = [None, None]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
            return return_data
        if debugging:
            print(data[enc_uid])
        if data[enc_uid][0] != "" or data[enc_uid][1] != "":  # 사용자 정보 있을 때
            return_data = [data[enc_uid][0], data[enc_uid][1]]
            log.info("[#%s] get_user@modules/user.py: Succeeded" % req_id)
        else:  # 사용자 정보 없을 때
            return_data = [None, None]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
        return return_data
    except Exception:
        return Exception


# 사용자 생성 및 수정
def manage_user(uid, user_grade, user_class, req_id, debugging):
    log.info("[#%s] manage_user@modules/user.py: Started Managing User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
        if debugging:
            print(data)
        if enc_uid in data:  # 사용자 정보 있을 때
            if data[enc_uid][0] == user_grade and data[enc_uid][1] == user_class:  # 사용자 정보 똑같을 때
                log.info("[#%s] manage_user@modules/user.py: Same" % req_id)
                return "Same"
            else:  # 사용자 정보 있고 같지도 않을 때 - 업데이트 (삭제 후 재생성)
                del data[enc_uid]
                if debugging:
                    print("DEL USER")
                log.info("[#%s] manage_user@modules/user.py: Updated" % req_id)
                return_msg = "Updated"
        else:  # 사용자 정보 없을 때 - 생성
            log.info("[#%s] manage_user@modules/user.py: Registered" % req_id)
            return_msg = "Registered"
        user_data = [int(user_grade), int(user_class)]
        data[enc_uid] = user_data
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            log.info("[#%s] manage_user@modules/user.py: Succeeded" % req_id)
            return return_msg
    except Exception:
        log.err("[#%s] manage_user@modules/user.py: Failed" % req_id)
        return Exception


# 사용자 삭제
def delete_user(uid, req_id, debugging):
    log.info("[#%s] delete_user@modules/user.py: Started Deleting User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            enc_uid = enc.hexdigest()
            data = json.load(data_file)
        if enc_uid in data:  # 사용자 정보 있을 때
            if debugging:
                print("DEL USER")
            del data[enc_uid]
        else:  # 사용자 정보 없을 때
            log.info("[#%s] delete_user@modules/user.py: No User Info" % req_id)
            return "NotExist"
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            log.info("[#%s] delete_user@modules/user.py: Succeeded" % req_id)
            return "Deleted"
    except Exception:
        log.err("[#%s] delete_user@modules/user.py: Failed" % req_id)
        return Exception


# 관리자 인증
def auth_admin(uid, req_id, debugging):
    with open(admin_path, encoding="utf-8") as data_file:
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        enc_uid = enc.hexdigest()
        data = json.load(data_file)
    if debugging:
        print(enc_uid)
        print(data)
    if enc_uid in data:
        log.info("[#%s] auth_admin@modules/user.py: Match" % req_id)
        return True
    else:
        log.info("[#%s] auth_admin@modules/user.py: Not Match" % req_id)
        return False

errors = {
    "ServerError": ({"message": "서버 오류가 발생했습니다."}, 500),
    "InvalidRequest": ({"message": "올바르지 않은 요청입니다."}, 403),
    "NoToken": ({"message": "토큰이 없습니다."}, 401),
    "ExpiredToken": ({"message": "만료된 토큰입니다."}, 403),
    "InvalidToken": ({"message": "올바르지 않은 토큰입니다."}, 403),
    "NoRecaptchaToken": ({"message": "리캡챠 토큰이 없습니다."}, 401),
    "InvalidRecaptchaToken": ({"message": "만료된 리캡챠 토큰입니다."}, 403),
    "RecaptchaTokenValidationError": ({"message": "올바르지 않은 리캡챠 토큰입니다."}, 500)
}
classes = 12
def decode_data(original_fn):
    def wrapper_fn(*args, **kwargs):
        global req_data
        req_data = json.loads(args[0].data)
        return original_fn(*args, **kwargs)
    return wrapper_fn

def validate_token(original_fn):
    def wrapper_fn(*args, **kwargs):
        global token, decoded
        if 'token' in req_data:
            token = req_data['token']
            try:
                decoded = jwt.decode(token.encode("UTF-8"), jwt_secret, algorithms='HS384')
            except jwt.ExpiredSignatureError:
                return errors["ExpiredToken"]
            except jwt.InvalidTokenError:
                return errors["InvalidToken"]
            return original_fn(*args, **kwargs)
        else:
            return errors["NoToken"]
    return wrapper_fn

def validate_recaptcha(original_fn):
    def wrapper_fn(*args, **kwargs):
        global token, decoded
        if 'recaptcha' in req_data:
            try:
                req = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify?secret=%s&response=%s'
                    % (recaptcha_secret, req_data['recaptcha']), data=None
                )
                rspns = req.json()
            except Exception as error:
                return errors["RecaptchaTokenValidationError"]
            if rspns['success']:
                return original_fn(*args, **kwargs)
            else:
                return errors["InvalidRecaptchaToken"]
        else:
            return errors["NoRecaptchaToken"]
    return wrapper_fn


def user_settings_rest_get(req, req_id, debugging):
    global req_data
    req_data = dict()
    req_data["token"] = req.args.get('token', None)
    @validate_token
    def inner(req, req_id, debugging):
        if "uid" in decoded:
            try:
                user = get_user(decoded['uid'], req_id, debugging)
            except Exception as error:
                log.err("[#%s] user_settings_rest_get@modules/user.py: %s" % (req_id, error))
                return errors["ServerError"]
            return {'token': token, 'classes': list(range(1, classes + 1)), 'uid': decoded["uid"],
                    'current_grade': user[0], 'current_class': user[1]}
        else:
            return errors["InvalidToken"]
    return inner(req, req_id, debugging)

@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_post(req, req_id, debugging):
    if "user_grade" in req_data and "user_class" in req_data:
        user_grade = int(req_data["user_grade"])
        user_class = int(req_data["user_class"])
        if 0 < user_grade < 4 and 0 < user_class <= classes:
            try:
                manage_user(decoded['uid'], user_grade, user_class, req_id, debugging)
            except Exception as error:
                log.err("[#%s] user_settings_rest_post@modules/user.py: %s" % (req_id, error))
                return errors["ServerError"]
            return {'message': "저장했습니다."}
        else:
            return errors["InvalidRequest"]
    else:
        return errors["InvalidRequest"]

@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_delete(req, req_id, debugging):
    try:
        delete_user(decoded['uid'], req_id, debugging)
    except Exception as error:
        log.err("[#%s] user_settings_rest_delete@modules/user.py: %s" % (req_id, error))
        return errors["ServerError"]
    return {'message': "삭제했습니다."}

# 디버그
if __name__ == "__main__":
    # 0 - GetUser, 1 - ManageUser, 2 - DeleteUser
    flag = 1
    user_id = "uid"
    user_grade = "3"
    user_class = "11"

    path = "../data/user/user.json"
    admin_path = "../data/user/admin.json"
    if flag == 0:
        print(get_user(user_id, "****DEBUG****", True))
    elif flag == 1:
        print(manage_user(user_id, user_grade, user_class, "****DEBUG****", True))
    elif flag == 2:
        print(delete_user(user_id, "****DEBUG****", True))
