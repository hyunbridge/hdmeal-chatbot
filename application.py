# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

import argparse
import ast
import datetime
import os
import random
from flask import Flask
from flask_restful import request, Api, Resource
from modules import getData, skill, FB, log, cache, user

# 디버그용
debugging = False
test_id = None
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# 환경변수 있는지 확인
# DEPRECATED #
# if (not os.getenv("DB_SERVER") or not os.getenv("DB_NAME") or not os.getenv("DB_UID") or not os.getenv("DB_PWD")
#        or not os.getenv("HDMEAL_TOKENS") or not os.getenv("RIOT_TOKEN")):
#    print("환경변수 설정이 바르게 되어있지 않습니다.")
#    exit(1)
if (not os.getenv("HDMEAL_TOKENS") or not os.getenv("RIOT_TOKEN") or not os.getenv("SERVER_SECRET")
        or not os.getenv("RECAPTCHA_SECRET") or not os.getenv("SETTINGS_URL")):
    print("환경변수 설정이 바르게 되어있지 않습니다.")
    exit(1)
tokens = ast.literal_eval(os.getenv("HDMEAL_TOKENS"))
if not isinstance(tokens, dict):
    print("환경변수 설정이 바르게 되어있지 않습니다.")
    exit(1)

# 로거 초기화
log.init()


# 요청코드 생성
def request_id(original_fn):
    def wrapper_fn(*args, **kwargs):
        global req_id
        # Test ID 있으면 Test ID 사용
        if test_id:
            req_id = test_id
        else:
            rand = str(random.randint(1, 99999)).zfill(5)  # 5자리 난수 생성
            tmstm = str(int(datetime.datetime.now().timestamp()))  # 타임스탬프 생성
            req_id = str(hex(int(rand + tmstm)))[2:].zfill(13)  # 난수 + 타임스탬프 합치고 HEX 변환, 13자리 채우기
        return original_fn(*args, **kwargs)

    return wrapper_fn


# 토큰 인증
# 인증 데코레이터는 반드시 요청코드 데코레이터 밑에 작성
def auth(original_fn):
    def wrapper_fn(*args, **kwargs):
        if test_id:
            log.info("[#%s] Bypassing Authorization")
            return original_fn(*args, **kwargs)
        else:
            if "HDMeal-Token" in request.headers:
                if request.headers["HDMeal-Token"] in tokens:
                    log.info('[#%s] Authorized with Token "%s"' % (req_id, tokens[request.headers["HDMeal-Token"]]))
                    return original_fn(*args, **kwargs)
                else:
                    log.info('[#%s] Failed to Authorize(Token Not Match)' % req_id)
                    return {'version': '2.0', 'data': {'msg': "미승인 토큰"}}, 403
            else:
                log.info('[#%s] Failed to Authorize(No Token)' % req_id)
                return {'version': '2.0', 'data': {'msg': "인증 토큰 없음"}}, 401

    return wrapper_fn


# Flask 인스턴스 생성
app = Flask(__name__, static_folder='./data/static')
api = Api(app)
app.secret_key = os.getenv("SERVER_SECRET")
jwt_secret = os.getenv("SERVER_SECRET")
log.info("Server Started")


# 특정 날짜 식단 조회
class Date(Resource):
    @request_id
    @auth
    def get(self, year, month, date):
        return getData.meal(year, month, date, req_id, debugging)


# Skill 식단 조회
class Meal(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.meal(request.data, req_id, debugging)


# Skill 특정날짜(고정값) 식단 조회
class MealSpecificDate(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.meal_specific_date(request.data, req_id, debugging)


# Skill 시간표 조회 (등록 사용자용)
class TimetableRegistered(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.tt_registered(request.data, req_id, debugging)


# Skill 시간표 조회 (미등록 사용자용)
class Timetable(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.tt(request.data, req_id, debugging)


# 캐시 비우기
class PurgeCache(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.purge_cache(request.data, req_id, debugging)


# 캐시 목록 보여주기
class ListCache(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.get_cache(request.data, req_id, debugging)


# 캐시 상태확인
class CacheHealthCheck(Resource):
    @staticmethod
    @request_id
    @auth
    def get():
        return cache.health_check(req_id, debugging)


# 캐시 상태확인(Skill)
class CacheHealthCheckSkill(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.check_cache(request.data, req_id, debugging)


# 사용자 관리
class ManageUser(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.manage_user(request.data, req_id, debugging)


# 사용자 삭제
class DeleteUser(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.delete_user(request.data, req_id, debugging)


# 한강 수온 조회
class WTemp(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.wtemp(req_id, debugging)


# 학사일정 조회
class Cal(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.schdl(request.data, req_id, debugging)


# 페이스북 포스팅
class Facebook(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        if "X-FB-Token" in request.headers:
            return FB.publish(request.headers["X-FB-Token"], req_id, debugging)
        else:
            return FB.publish(None, req_id, debugging)


# 급식봇 브리핑
class Briefing(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.briefing(request.data, req_id, debugging)


# Repo 커밋 조회
class Commits(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.commits(req_id, debugging)


# 롤 전적조회
class LoL(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.lol(request.data, req_id, debugging)

# 내 정보 관리(토큰 생성)
class UserSettings(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return skill.user_settings_web(request.data, jwt_secret, req_id, debugging)
# 내 정보 관리(API)
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "application/json,Content-Type,Content-Length,Access-Control-Allow-Origin,Access-Control-Allow-Headers,Server,Date",
    "Access-Control-Allow-Methods": "GET, POST, DELETE"
}
class UserSettingsREST(Resource):
    @staticmethod
    @request_id
    def get():
        response = user.user_settings_rest_get(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)
    @staticmethod
    @request_id
    def post():
        response = user.user_settings_rest_post(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)
    @staticmethod
    @request_id
    def delete():
        response = user.user_settings_rest_delete(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)
    @staticmethod
    def options():
        return None, 200, cors_headers


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(Meal, '/meal/')
api.add_resource(MealSpecificDate, '/meal/specificdate/')
api.add_resource(Timetable, '/tt/')
api.add_resource(TimetableRegistered, '/tt/registered/')
api.add_resource(ListCache, '/cache/list/')
api.add_resource(PurgeCache, '/cache/purge/')
api.add_resource(CacheHealthCheck, '/cache/healthcheck/')
api.add_resource(CacheHealthCheckSkill, '/cache/healthcheck/skill/')
api.add_resource(ManageUser, '/user/manage/')
api.add_resource(DeleteUser, '/user/delete/')
api.add_resource(UserSettings, '/user/settings/get-token/')
api.add_resource(UserSettingsREST, '/user/settings/api-gateway/')
api.add_resource(WTemp, '/wtemp/')
api.add_resource(Cal, '/cal/')
api.add_resource(Facebook, '/fb/')
api.add_resource(Briefing, '/briefing/')
api.add_resource(Commits, '/commits/')
api.add_resource(LoL, '/lol/')

# 서버 실행
if __name__ == '__main__':
    debugging = True
    # 커맨드라인 인자값(Test ID) 받기
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-id", help="Test ID")
    args = parser.parse_args()
    if "test_id" in args:
        test_id = args.test_id
    app.run(debug=debugging)
