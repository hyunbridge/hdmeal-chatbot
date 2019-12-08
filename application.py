# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

from flask import Flask
from flask_restful import request, Api, Resource
from modules import getData, skill, FB, log, cache
import datetime
import random

# 디버그용
debugging = False
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# 요청코드 생성
def request_id(original_fn):
    def wrapper_fn(*args, **kwargs):
        global req_id
        rand = str(random.randint(1, 99999)).zfill(5)  # 5자리 난수 생성
        tmstm = str(int(datetime.datetime.now().timestamp()))  # 타임스탬프 생성
        req_id = str(hex(int(rand + tmstm)))[2:].zfill(13)  # 난수 + 타임스탬프 합치고 HEX 변환, 13자리 채우기
        return original_fn(*args, **kwargs)
    return wrapper_fn

# 로거 초기화
log.init()

# Flask 인스턴스 생성
app = Flask(__name__)
api = Api(app)

log.info("Server Started")

# 특정 날짜 식단 조회
class Date(Resource):
    @request_id
    def get(self, year, month, date):
        return getData.meal(year, month, date, req_id, debugging)

# Skill 식단 조회
class Meal(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.meal(request.data, req_id, debugging)

# Skill 특정날짜(고정값) 식단 조회
class MealSpecificDate(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.meal_specific_date(request.data, req_id, debugging)


# Skill 시간표 조회 (등록 사용자용)
class TimetableRegistered(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.tt_registered(request.data, req_id, debugging)

# Skill 시간표 조회 (미등록 사용자용)
class Timetable(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.tt(request.data, req_id, debugging)


# 캐시 비우기
class PurgeCache(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.purge_cache(request.data, req_id, debugging)

# 캐시 목록 보여주기
class ListCache(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.get_cache(request.data, req_id, debugging)

# 캐시 상태확인
class CacheHealthCheck(Resource):
    @staticmethod
    @request_id
    def get():
        return cache.health_check(req_id, debugging)

# 캐시 상태확인(Skill)
class CacheHealthCheck_Skill(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.check_cache(request.data, req_id, debugging)

# 사용자 관리
class ManageUser(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.manage_user(request.data, req_id, debugging)

# 사용자 삭제
class DeleteUser(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.delete_user(request.data, req_id, debugging)


# 한강 수온 조회
class WTemp(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.wtemp(req_id, debugging)


# 학사일정 조회
class Cal(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.schdl(request.data, req_id, debugging)


# 페이스북 포스팅
class Facebook(Resource):
    @staticmethod
    @request_id
    def post():
        if "X-FB-Token" in request.headers:
            return FB.publish(request.headers["X-FB-Token"], req_id, debugging)
        else:
            return FB.publish('', req_id, debugging)


# 급식봇 브리핑
class Briefing(Resource):
    @staticmethod
    @request_id
    def post():
        return skill.briefing(request.data, req_id, debugging)


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(Meal, '/meal/')
api.add_resource(MealSpecificDate, '/meal/specificdate/')
api.add_resource(Timetable, '/tt/')
api.add_resource(TimetableRegistered, '/tt/registered/')
api.add_resource(ListCache, '/cache/list/')
api.add_resource(PurgeCache, '/cache/purge/')
api.add_resource(CacheHealthCheck, '/cache/healthcheck/')
api.add_resource(CacheHealthCheck_Skill, '/cache/healthcheck/skill/')
api.add_resource(ManageUser, '/user/manage/')
api.add_resource(DeleteUser, '/user/delete/')
api.add_resource(WTemp, '/wtemp/')
api.add_resource(Cal, '/cal/')
api.add_resource(Facebook, '/fb/')
api.add_resource(Briefing, '/briefing/')

# 서버 실행
if __name__ == '__main__':
    debugging = True
    app.run(debug=debugging)
