# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

from flask import Flask
from flask_restful import request, Api, Resource
from modules import getdata, skill, user

# 디버그용
isDebugging = False
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
        return getdata.meal(year, month, date, isDebugging)

# Skill 식단 조회
class Skill(Resource):
    @staticmethod
    def post():
        return skill.meal(request.data, isDebugging)

# Skill 특정날짜(고정값) 식단 조회
class SkillSpecificDate(Resource):
    @staticmethod
    def post():
        return skill.meal_specific_date(request.data, isDebugging)

# Skill 시간표 조회 (등록 사용자용)
class TimetableRegistered(Resource):
    @staticmethod
    def post():
        return skill.tt_registered(request.data, isDebugging)

# Skill 시간표 조회 (미등록 사용자용)
class Timetable(Resource):
    @staticmethod
    def post():
        return skill.tt(request.data, isDebugging)


# 캐시 비우기
class PurgeCache(Resource):
    @staticmethod
    def post():
        return skill.purge_cache(request.data, isDebugging)

# 캐시 목록 보여주기
class ListCache(Resource):
    @staticmethod
    def post():
        return skill.get_cache(request.data, isDebugging)

# 사용자 관리
class ManageUser(Resource):
    @staticmethod
    def post():
        return skill.manage_user(request.data, isDebugging)

# 사용자 삭제
class DeleteUser(Resource):
    @staticmethod
    def post():
        return skill.delete_user(request.data, isDebugging)


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(Skill, '/skill-gateway/')
api.add_resource(SkillSpecificDate, '/skill-gateway/specificdate/')
api.add_resource(TimetableRegistered, '/skill-gateway/tt/registered/')
api.add_resource(Timetable, '/skill-gateway/tt/')
api.add_resource(PurgeCache, '/cache/purge/')
api.add_resource(ListCache, '/cache/list/')
api.add_resource(ManageUser, '/user/manage/')
api.add_resource(DeleteUser, '/user/delete/')

# 서버 실행
if __name__ == '__main__':
    app.run(debug=isDebugging)
