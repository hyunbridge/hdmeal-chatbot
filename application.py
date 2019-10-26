# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

from flask import Flask
from flask_restful import request, Api, Resource
from modules import getdata, skill, fb

# 디버그용
debugging = False
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# Flask 인스턴스 생성
app = Flask(__name__)
api = Api(app)

# 특정 날짜 식단 조회
class Date(Resource):
    def get(self, year, month, date):
        return getdata.meal(year, month, date, debugging)

# Skill 식단 조회
class Meal(Resource):
    @staticmethod
    def post():
        return skill.meal(request.data, debugging)

# Skill 특정날짜(고정값) 식단 조회
class MealSpecificDate(Resource):
    @staticmethod
    def post():
        return skill.meal_specific_date(request.data, debugging)


# Skill 시간표 조회 (등록 사용자용)
class TimetableRegistered(Resource):
    @staticmethod
    def post():
        return skill.tt_registered(request.data, debugging)

# Skill 시간표 조회 (미등록 사용자용)
class Timetable(Resource):
    @staticmethod
    def post():
        return skill.tt(request.data, debugging)


# 캐시 비우기
class PurgeCache(Resource):
    @staticmethod
    def post():
        return skill.purge_cache(request.data, debugging)

# 캐시 목록 보여주기
class ListCache(Resource):
    @staticmethod
    def post():
        return skill.get_cache(request.data, debugging)


# 사용자 관리
class ManageUser(Resource):
    @staticmethod
    def post():
        return skill.manage_user(request.data, debugging)

# 사용자 삭제
class DeleteUser(Resource):
    @staticmethod
    def post():
        return skill.delete_user(request.data, debugging)


# 한강 수온 조회
class WTemp(Resource):
    @staticmethod
    def post():
        return skill.wtemp(debugging)


# 학사일정 조회
class Cal(Resource):
    @staticmethod
    def post():
        return skill.cal(request.data, debugging)


# 페이스북 포스팅
class FB(Resource):
    @staticmethod
    def post():
        if "X-FB-Token" in request.headers:
            return fb.publish(request.headers["X-FB-Token"], debugging)
        else:
            return fb.publish('', debugging)


# 급식봇 브리핑
class Briefing(Resource):
    @staticmethod
    def post():
        return skill.briefing(request.data, debugging)


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(Meal, '/meal/')
api.add_resource(MealSpecificDate, '/meal/specificdate/')
api.add_resource(Timetable, '/tt/')
api.add_resource(TimetableRegistered, '/tt/registered/')
api.add_resource(ListCache, '/cache/list/')
api.add_resource(PurgeCache, '/cache/purge/')
api.add_resource(ManageUser, '/user/manage/')
api.add_resource(DeleteUser, '/user/delete/')
api.add_resource(WTemp, '/wtemp/')
api.add_resource(Cal, '/cal/')
api.add_resource(FB, '/fb/')
api.add_resource(Briefing, '/briefing/')

# 서버 실행
if __name__ == '__main__':
    app.run(debug=debugging)
