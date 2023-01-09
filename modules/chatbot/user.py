# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# user.py - 사용자 관리 및 인증을 담당하는 스크립트입니다.

import datetime
import json
import os

import pytz

from modules.common import security, log

timezone_local = pytz.timezone("Asia/Seoul")

path = "./data/users.json"

# 학급수 불러오기
classes = int(os.environ.get("HDMeal-NumOfClasses"))
# 오류 메세지
errors_conf = {
    "ServerError": [
        "서버 오류가 발생했습니다.",
        500,
    ],
    "InvalidRequest": [
        "올바르지 않은 요청입니다.",
        400,
    ],
    "NoToken": [
        "토큰이 없습니다.",
        401,
    ],
    "ExpiredToken": [
        "만료된 토큰입니다.",
        403,
    ],
    "InvalidToken": [
        "올바르지 않은 토큰입니다.",
        400,
    ],
    "NoRecaptchaToken": [
        "리캡챠 토큰이 없습니다.",
        401,
    ],
    "InvalidRecaptchaToken": [
        "만료된 리캡챠 토큰입니다.",
        403,
    ],
    "RecaptchaTokenValidationError": [
        "올바르지 않은 리캡챠 토큰입니다.",
        400,
    ],
    "TooManyResult": [
        "결과값이 너무 많습니다.",
        400,
    ],
}

# 설정 기본값
preferences_default = {"AllergyInfo": "Number"}
preferences_values = {"AllergyInfo": ["None", "Number", "FullText"]}

# 오류 발생 처리
def hdm_error(code: str):
    return {"message": errors_conf[code][0]}, errors_conf[code][1]


# JSON에서 Datetime 포맷 처리
def json_default(value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    raise TypeError("not JSON serializable")


# 사용자 정보 읽기
def get_user(uid: str, req_id: str, debugging: bool):
    log.info("[#%s] get_user@modules/user.py: Started Fetching User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            data = json.load(data_file)
        if debugging:
            print(data)
        if not uid in data:  # 사용자 정보 없을 때
            return_data = [None, None, {}]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
            return return_data
        if debugging:
            print(data[uid])
        if data[uid]["Grade"] != "" or data[uid]["Class"] != "":  # 사용자 정보 있을 때
            return_data = [
                data[uid]["Grade"],
                data[uid]["Class"],
                data[uid]["Preferences"],
            ]
            log.info("[#%s] get_user@modules/user.py: Succeeded" % req_id)
        else:  # 사용자 정보 없을 때
            return_data = [None, None, {}]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
        return return_data
    except Exception as e:
        return e


# 사용자 생성 및 수정
def manage_user(
    uid: str,
    user_grade: int,
    user_class: int,
    preferences: dict,
    req_id: str,
    debugging: bool,
):
    log.info("[#%s] manage_user@user.py: Started Managing User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            data = json.load(data_file)
        if debugging:
            print(data)
        if uid in data:  # 사용자 정보 있을 때
            current_settings = data[uid]
            if preferences:
                new_settings = {
                    "Grade": user_grade,
                    "Class": user_class,
                    "Preferences": preferences,
                }
            else:
                new_settings = {
                    "Grade": user_grade,
                    "Class": user_class,
                    "Preferences": current_settings.get(
                        "Preferences", preferences_default
                    ),
                }
            if debugging:
                print(current_settings)
            if current_settings == new_settings:  # 사용자 정보 똑같을 때
                log.info("[#%s] manage_user@user.py: Same" % req_id)
                return "Same"
            else:  # 사용자 정보 있고 같지도 않을 때 - 업데이트
                del data[uid]
                data[uid] = new_settings
                if debugging:
                    print("DEL USER")
                log.info("[#%s] manage_user@user.py: Updated" % req_id)
                return_msg = "Updated"
        else:  # 사용자 정보 없을 때 - 생성
            if preferences:
                new_settings = {
                    "Grade": user_grade,
                    "Class": user_class,
                    "Preferences": preferences,
                }
            else:
                new_settings = {
                    "Grade": user_grade,
                    "Class": user_class,
                    "Preferences": preferences_default,
                }
            log.info("[#%s] manage_user@user.py: Registered" % req_id)
            return_msg = "Registered"
            data[uid] = new_settings
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            log.info("[#%s] manage_user@user.py: Succeeded" % req_id)
            return return_msg
    except Exception:
        log.err("[#%s] manage_user@user.py: Failed" % req_id)
        return Exception


# 사용자 삭제
def delete_user(uid: str, req_id: str, debugging: bool):
    log.info("[#%s] delete_user@user.py: Started Deleting User Info" % req_id)
    try:
        with open(path, encoding="utf-8") as data_file:
            data = json.load(data_file)
        if uid in data:  # 사용자 정보 있을 때
            if debugging:
                print("DEL USER")
            del data[uid]
        else:  # 사용자 정보 없을 때
            log.info("[#%s] delete_user@user.py: No User Info" % req_id)
            return "NotExist"
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file, ensure_ascii=False, indent="\t")
            log.info("[#%s] delete_user@user.py: Succeeded" % req_id)
            return "Deleted"
    except Exception:
        log.err("[#%s] delete_user@user.py: Failed" % req_id)
        return Exception


# 관리자 인증
def auth_admin(uid, req_id, debugging):
    data = json.loads(os.environ.get("HDMeal-AdminTokens", "[]"))
    if debugging:
        print(uid)
        print(data)
    if uid in data:
        log.info("[#%s] auth_admin@user.py: Match" % req_id)
        return True
    else:
        log.info("[#%s] auth_admin@user.py: Not Match" % req_id)
        return False


# 요청 데이터 해석
def decode_data(original_fn):
    def wrapper_fn(*args, **kwargs):
        global req_data, req_args
        if args[0].data:
            try:
                req_data = json.loads(args[0].data)
            except Exception:
                return hdm_error("InvalidRequest")
        else:
            req_data = {}
        req_args = args[0].args
        return original_fn(*args, **kwargs)

    return wrapper_fn


# JWT 토큰 검증
def validate_token(original_fn):
    def wrapper_fn(*args, **kwargs):
        global uid, token, scope
        if "token" in req_data:
            token = req_data["token"]
        elif "token" in req_args:
            token = req_args["token"]
        else:
            return hdm_error("NoToken")
        if token:
            validation: tuple = security.validate_token(token, args[1])
            if validation[0]:
                uid = validation[1]
                scope = validation[2]
                return original_fn(*args, **kwargs)
            else:
                return hdm_error(validation[1])
        else:
            return hdm_error("InvalidToken")

    return wrapper_fn


# 리캡챠 토큰 검증
def validate_recaptcha(original_fn):
    def wrapper_fn(*args, **kwargs):
        global token
        if "recaptcha" in req_data:
            recaptcha = req_data["recaptcha"]
        elif "recaptcha" in req_args:
            recaptcha = req_args["recaptcha"]
        else:
            return hdm_error("NoRecaptchaToken")
        if recaptcha:
            validation: tuple = security.validate_recaptcha(recaptcha, args[1])
            if validation[0]:
                return original_fn(*args, **kwargs)
            else:
                return hdm_error(validation[1])
        else:
            log.info("[#%s] validate_recaptcha@user.py: No Recaptcha Token" % args[1])
            return hdm_error("NoRecaptchaToken")

    return wrapper_fn


# 사용자 설정 - GET
@decode_data
@validate_token
def user_settings_rest_get(req, req_id, debugging):
    if uid and "GetUserInfo" in scope:
        try:
            user = get_user(uid, req_id, debugging)
        except Exception as error:
            log.err("[#%s] user_settings_rest_get@user.py: %s" % (req_id, error))
            return hdm_error("ServerError")
        return {
            "classes": list(range(1, classes + 1)),
            "current_grade": user[0],
            "current_class": user[1],
            "preferences": user[2],
        }
    else:
        return hdm_error("InvalidToken")


# 사용자 설정 - POST
@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_post(req, req_id, debugging):
    if not uid or not "ManageUserInfo" in scope:
        return hdm_error("InvalidToken")
    if "user_grade" in req_data and "user_class" in req_data:
        user_grade = int(req_data["user_grade"])
        user_class = int(req_data["user_class"])
        if 0 < user_grade < 4 and 0 < user_class <= classes:
            if all(
                item in preferences_values.keys()
                for item in req_data["preferences"].keys()
            ):
                for i in req_data["preferences"].keys():
                    if not req_data["preferences"][i] in preferences_values[i]:
                        return hdm_error("InvalidRequest")
                try:
                    manage_user(
                        uid,
                        user_grade,
                        user_class,
                        req_data["preferences"],
                        req_id,
                        debugging,
                    )
                except Exception as error:
                    log.err(
                        "[#%s] user_settings_rest_post@user.py: %s" % (req_id, error)
                    )
                    return hdm_error("ServerError")
            return {"message": "저장했습니다."}
    return hdm_error("InvalidRequest")


# 사용자 설정 - DELETE
@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_delete(req, req_id, debugging):
    if not uid or not "ManageUserInfo" in scope:
        return hdm_error("InvalidToken")
    try:
        delete_user(uid, req_id, debugging)
    except Exception as error:
        log.err("[#%s] user_settings_rest_delete@user.py: %s" % (req_id, error))
        return hdm_error("ServerError")
    return {"message": "삭제했습니다."}


# 디버그
if __name__ == "__main__":
    log.init()
    # 0 - GetUser, 1 - ManageUser, 2 - DeleteUser
    flag = 1
    user_id = "uid"
    user_grade = 1
    user_class = 1

    path = "../data/users.json"
    if flag == 0:
        print(get_user(user_id, "****DEBUG****", True))
    elif flag == 1:
        print(manage_user(user_id, user_grade, user_class, "****DEBUG****", True))
    elif flag == 2:
        print(delete_user(user_id, "****DEBUG****", True))
