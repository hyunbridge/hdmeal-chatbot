# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# modules/user.py - 사용자 관리 및 인증을 담당하는 스크립트입니다.

import base64
import datetime
import json
import zipfile
from io import BytesIO
import pymongo
import pytz
from modules import log, conf, security

timezone_local = pytz.timezone('Asia/Seoul')

# DB정보 불러오기
connection = pymongo.MongoClient(conf.configs['DataBase']['ConnectString'])
db = connection.hdmeal
users_collection = db.users
utterances_collection = db.utterances
# 학급수 불러오기
classes = int(conf.configs['School']['Classes'])
# 오류 메세지
errors_conf = conf.configs['Misc']['Errors']


# 오류 발생 처리
def hdm_error(code: str):
    return {'message': errors_conf[code][0]}, int(errors_conf[code][1])


# JSON에서 Datetime 포맷 처리
def json_default(value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    raise TypeError('not JSON serializable')


# 사용자 정보 읽기
def get_user(uid: str, req_id: str, debugging: bool):
    log.info("[#%s] get_user@modules/user.py: Started Fetching User Info" % req_id)
    try:
        data = users_collection.find_one({'UID': uid})
        if debugging:
            print(data)
        if not data:  # 사용자 정보 없을 때
            return_data = [None, None]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
            return return_data
        if data['Grade'] and data['Class']:  # 사용자 정보 있을 때
            return_data = [data['Grade'], data['Class']]
            log.info("[#%s] get_user@modules/user.py: Succeeded" % req_id)
        else:  # 사용자 정보 없을 때
            return_data = [None, None]
            log.info("[#%s] get_user@modules/user.py: No User Info" % req_id)
        return return_data
    except Exception:
        return Exception


# 사용자 생성 및 수정
def manage_user(uid: str, user_grade: int, user_class: int, req_id: str, debugging: bool):
    log.info("[#%s] manage_user@modules/user.py: Started Managing User Info" % req_id)
    try:
        data = users_collection.find_one({'UID': uid})
        if debugging:
            print(data)
        if data:  # 사용자 정보 있을 때
            if data['Grade'] == user_grade and data['Class'] == user_class:  # 사용자 정보 똑같을 때
                log.info("[#%s] manage_user@modules/user.py: Same" % req_id)
                return "Same"
            else:  # 사용자 정보 있고 같지도 않을 때 - 업데이트
                data = users_collection.update({'UID': uid}, {'$set': {'Grade': user_grade, 'Class': user_class}})
                log.info("[#%s] manage_user@modules/user.py: Updated" % req_id)
                return "Updated"
        else:  # 사용자 정보 없을 때 - 생성
            users_collection.insert_one({"UID": uid, "Grade": user_grade, "Class": user_class})
            log.info("[#%s] manage_user@modules/user.py: Registered" % req_id)
            return "Registered"
    except Exception:
        log.err("[#%s] manage_user@modules/user.py: Failed" % req_id)
        return Exception


# 사용자 삭제
def delete_user(uid: str, req_id: str, debugging: bool):
    log.info("[#%s] delete_user@modules/user.py: Started Deleting User Info" % req_id)
    try:
        data = users_collection.find_one({'UID': uid})
        if data:  # 사용자 정보 있을 때
            if debugging:
                print("DEL USER")
            users_collection.remove({'UID': uid})
        else:  # 사용자 정보 없을 때
            log.info("[#%s] delete_user@modules/user.py: No User Info" % req_id)
            return "NotExist"
    except Exception:
        log.err("[#%s] delete_user@modules/user.py: Failed" % req_id)
        return Exception


# 관리자 인증
def auth_admin(uid, req_id, debugging):
    data = conf.configs['Admins']
    if debugging:
        print(uid)
        print(data)
    if uid in data:
        log.info("[#%s] auth_admin@modules/user.py: Match" % req_id)
        return True
    else:
        log.info("[#%s] auth_admin@modules/user.py: Not Match" % req_id)
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
        if 'token' in req_data:
            token = req_data['token']
        elif 'token' in req_args:
            token = req_args['token']
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
        if 'recaptcha' in req_data:
            recaptcha = req_data['recaptcha']
        elif 'recaptcha' in req_args:
            recaptcha = req_args['recaptcha']
        else:
            return hdm_error("NoRecaptchaToken")
        if recaptcha:
            validation: tuple = security.validate_recaptcha(recaptcha, args[1])
            if validation[0]:
                return original_fn(*args, **kwargs)
            else:
                return hdm_error(validation[1])
        else:
            log.info("[#%s] validate_recaptcha@modules/user.py: No Recaptcha Token" % args[1])
            return hdm_error("NoRecaptchaToken")

    return wrapper_fn


# 사용자 설정 - GET
@decode_data
@validate_token
def user_settings_rest_get(req, req_id, debugging):
    if uid and 'GetUserInfo' in scope:
        try:
            user = get_user(uid, req_id, debugging)
        except Exception as error:
            log.err("[#%s] user_settings_rest_get@modules/user.py: %s" % (req_id, error))
            return hdm_error("ServerError")
        return {'token': token, 'classes': list(range(1, classes + 1)), 'uid': uid,
                'current_grade': user[0], 'current_class': user[1]}
    else:
        return hdm_error("InvalidToken")

# 사용자 설정 - POST
@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_post(req, req_id, debugging):
    if not uid or not 'ManageUserInfo' in scope:
        return hdm_error("InvalidToken")
    if "user_grade" in req_data and "user_class" in req_data:
        user_grade = int(req_data["user_grade"])
        user_class = int(req_data["user_class"])
        if 0 < user_grade < 4 and 0 < user_class <= classes:
            try:
                manage_user(uid, user_grade, user_class, req_id, debugging)
            except Exception as error:
                log.err("[#%s] user_settings_rest_post@modules/user.py: %s" % (req_id, error))
                return hdm_error("ServerError")
            return {'message': "저장했습니다."}
        else:
            return hdm_error("InvalidRequest")
    else:
        return hdm_error("InvalidRequest")

# 사용자 설정 - DELETE
@decode_data
@validate_recaptcha
@validate_token
def user_settings_rest_delete(req, req_id, debugging):
    if not uid or not 'ManageUserInfo' in scope:
        return hdm_error("InvalidToken")
    try:
        delete_user(uid, req_id, debugging)
    except Exception as error:
        log.err("[#%s] user_settings_rest_delete@modules/user.py: %s" % (req_id, error))
        return hdm_error("ServerError")
    return {'message': "삭제했습니다."}


# 사용 데이터 관리 - GET
@decode_data
@validate_recaptcha
@validate_token
def get_usage_data(req, req_id, debugging):
    if uid and 'GetUsageData' in scope:
        # 데이터가 1만건이 넘을경우 오류 발생시키기
        db_find_usage_data = list(utterances_collection.find({"User ID": uid}, {"_id": 0}).limit(10001))
        if len(db_find_usage_data) > 10000:
            return hdm_error("TooManyResult")
        print(db_find_usage_data)
        return_list = []
        for i in db_find_usage_data:
            # UTC -> KST로 변환
            utc_moment = pytz.utc.localize(i['Date'])
            local_moment = utc_moment.astimezone(timezone_local)
            i['Date'] = local_moment.isoformat()
            return_list.append(i)
        if not return_list:
            return {'message': "데이터가 없습니다."}
        print(return_list)
        # json 덤프 만들기
        return_json = json.dumps(return_list, indent=4, ensure_ascii=False, default=json_default)
        # 압축파일 RAM에 생성하기
        in_memory = BytesIO()
        return_zip = zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED)
        return_zip.comment = uid.encode()  # ZIP 설명에 UTD 입력
        return_zip.writestr("UsageData.json", return_json)
        return_zip.close()
        # DATA URL로 변환
        return {'file': 'data:application/zip;base64,'+base64.b64encode(in_memory.getvalue()).decode('unicode-escape')}
    else:
        return hdm_error("InvalidToken")

# 사용 데이터 관리 - DELETE
@decode_data
@validate_recaptcha
@validate_token
def delete_usage_data(req, req_id, debugging):
    if uid and 'DeleteUsageData' in scope:
        utterances_collection.remove({"User ID": uid})
        return {'message': "삭제했습니다."}
    else:
        return hdm_error("InvalidToken")

# 디버그
if __name__ == "__main__":
    log.init()
    # 0 - GetUser, 1 - ManageUser, 2 - DeleteUser
    flag = 2
    user_id = "uid"
    user_grade = 1
    user_class = 1

    path = "../data/user/user.json"
    admin_path = "../data/user/admin.json"
    if flag == 0:
        print(get_user(user_id, "****DEBUG****", True))
    elif flag == 1:
        print(manage_user(user_id, user_grade, user_class, "****DEBUG****", True))
    elif flag == 2:
        print(delete_user(user_id, "****DEBUG****", True))
