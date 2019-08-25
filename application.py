# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

from flask import Flask
import datetime
import json
from collections import OrderedDict
from flask_restful import request, Api, Resource
from modules import getdata, purgecache, auth

# 디버그용
isDebugging = False
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# Flask 인스턴스 생성
app = Flask(__name__)
api = Api(app)

# 특정 날짜
class Date(Resource):
    def get(self, year, month, date):
        return getdata.meal(year, month, date, isDebugging)


# Skill (Kakao i Open Builder) - 챗봇용
class Skill(Resource):
    @staticmethod
    def post():
        return_simple_text = OrderedDict()
        return_outputs = OrderedDict()
        return_list = list()
        return_template = OrderedDict()
        return_data = OrderedDict()

        def return_error():  # 오류 발생시 호출됨
            # 스킬 응답용 JSON 생성
            return_simple_text["text"] = "오류가 발생했습니다."
            return_outputs["simpleText"] = return_simple_text
            if not return_outputs in return_list:
                return_list.append(return_outputs)
            return_template["outputs"] = return_list
            return_data["version"] = "2.0"
            return_data["template"] = return_template
            return return_data

        sys_date = str()
        year = int()
        month = int()
        date = int()
        try:
            sys_date = json.loads(json.loads(request.data)["action"]["params"]["sys_date"])["date"]  # 날짜 가져오기
        except Exception:
            return_error()
        try:
            # 년월일 파싱
            year = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[0]
            month = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[1]
            date = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[2]
        except ValueError:  # 파싱중 값오류 발생시
            return_error()
        meal = getdata.meal(year, month, date, isDebugging)
        if not "message" in meal:  # 파서 메시지 있는지 확인, 없으면 만듦
            meal["message"] = "%s:\n\n%s\n\n열량: %s kcal" % (meal["date"], meal["menu"], meal["kcal"])
        # 스킬 응답용 JSON 생성
        return_simple_text["text"] = meal["message"]
        return_outputs["simpleText"] = return_simple_text
        if not return_outputs in return_list:
            return_list.append(return_outputs)
        return_template["outputs"] = return_list
        return_data["version"] = "2.0"
        return_data["template"] = return_template
        return return_data


# Skill 특정날짜(고정값) 조회
class SkillSpecificDate(Resource):
    @staticmethod
    def post():
        return_simple_text = OrderedDict()
        return_outputs = OrderedDict()
        return_list = list()
        return_template = OrderedDict()
        return_data = OrderedDict()

        def return_error():  # 오류 발생시 호출됨
            # 스킬 응답용 JSON 생성
            return_simple_text["text"] = "오류가 발생했습니다."
            return_outputs["simpleText"] = return_simple_text
            if not return_outputs in return_list:
                return_list.append(return_outputs)
            return_template["outputs"] = return_list
            return_data["version"] = "2.0"
            return_data["template"] = return_template
            return return_data

        specific_date = str()
        year = int()
        month = int()
        date = int()
        try:
            specific_date = json.loads(request.data)["action"]["params"]["date"]
        except Exception:
            return_error()
        try:
            # 년월일 파싱
            year = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[0]
            month = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[1]
            date = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[2]
        except ValueError:  # 값오류 발생시
            return_error()
        if isDebugging:
            print(specific_date)
            print(year)
            print(month)
            print(date)
        meal = getdata.meal(year, month, date, isDebugging)
        if not "message" in meal:  # 파서 메시지 있는지 확인, 없으면 만듦
            meal["message"] = "%s:\n\n%s\n\n열량: %s kcal" % (meal["date"], meal["menu"], meal["kcal"])
        # 스킬 응답용 JSON 생성
        return_simple_text["text"] = meal["message"]
        return_outputs["simpleText"] = return_simple_text
        if not return_outputs in return_list:
            return_list.append(return_outputs)
        return_template["outputs"] = return_list
        return_data["version"] = "2.0"
        return_data["template"] = return_template
        return return_data


# Skill 시간표 조회
class Timetable(Resource):
    @staticmethod
    def post():
        return_simple_text = OrderedDict()
        return_outputs = OrderedDict()
        return_list = list()
        return_template = OrderedDict()
        return_data = OrderedDict()

        def return_error():  # 오류 발생시 호출됨
            # 스킬 응답용 JSON 생성
            return_simple_text["text"] = "오류가 발생했습니다."
            return_outputs["simpleText"] = return_simple_text
            if not return_outputs in return_list:
                return_list.append(return_outputs)
            return_template["outputs"] = return_list
            return_data["version"] = "2.0"
            return_data["template"] = return_template
            return return_data

        tt_grade = str()
        tt_class = str()
        sys_date = str()
        tt_weekday = int()
        try:
            tt_grade = json.loads(request.data)["action"]["params"]["Grade"]  # 학년 파싱
        except Exception:
            return_error()
        try:
            tt_class = json.loads(request.data)["action"]["params"]["Class"]  # 반 파싱
        except Exception:
            return_error()
        try:
            sys_date = json.loads(json.loads(request.data)["action"]["params"]["sys_date"])["date"]  # 날짜 파싱
        except Exception:
            return_error()
        try:
            tt_weekday = datetime.datetime.strptime(sys_date, "%Y-%m-%d").weekday()  # 요일 파싱
        except ValueError:  # 값오류 발생시
            return_error()
        if isDebugging:
            print(tt_grade)
            print(tt_class)
            print(tt_weekday)
        tt = getdata.tt(tt_grade, tt_class, tt_weekday, isDebugging)
        # 스킬 응답용 JSON 생성
        return_simple_text["text"] = tt
        return_outputs["simpleText"] = return_simple_text
        if not return_outputs in return_list:
            return_list.append(return_outputs)
        return_template["outputs"] = return_list
        return_data["version"] = "2.0"
        return_data["template"] = return_template
        return return_data


# 캐시 비우기
class PurgeCache(Resource):
    @staticmethod
    def get():
        return purgecache.purge(isDebugging)

    @staticmethod
    def post():
        return_simple_text = OrderedDict()
        return_outputs = OrderedDict()
        return_list = list()
        return_template = OrderedDict()
        return_data = OrderedDict()

        # 사용자 ID 가져오고 검증
        uid = json.loads(request.data)["userRequest"]["user"]["id"]
        if auth.check(uid):
            if purgecache.purge(isDebugging)["status"] == "OK":  # 삭제 실행, 결과 검증
                msg = "정상적으로 삭제되었습니다."
            else:
                msg = "삭제에 실패하였습니다. 오류가 발생했습니다."
        else:
            msg = "사용자 인증에 실패하였습니다."

        # 스킬 응답용 JSON 생성
        return_simple_text["text"] = msg
        return_outputs["simpleText"] = return_simple_text
        if not return_outputs in return_list:
            return_list.append(return_outputs)
        return_template["outputs"] = return_list
        return_data["version"] = "2.0"
        return_data["template"] = return_template
        return return_data

# 캐시 목록 보여주기
class ListCache(Resource):
    @staticmethod
    def post():
        return_simple_text = OrderedDict()
        return_outputs = OrderedDict()
        return_list = list()
        return_template = OrderedDict()
        return_data = OrderedDict()

        # 사용자 ID 가져오고 검증
        uid = json.loads(request.data)["userRequest"]["user"]["id"]
        if auth.check(uid):
            cache = getdata.cache(isDebugging)
            if cache == "":
                cache = "\n캐시가 없습니다."
            msg = "캐시 목록:" + cache
        else:
            msg = "사용자 인증에 실패하였습니다."

        # 스킬 응답용 JSON 생성
        return_simple_text["text"] = msg
        return_outputs["simpleText"] = return_simple_text
        if not return_outputs in return_list:
            return_list.append(return_outputs)
        return_template["outputs"] = return_list
        return_data["version"] = "2.0"
        return_data["template"] = return_template
        return return_data



# URL Router에 맵핑.(Rest URL정의)
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(Skill, '/skill-gateway/')
api.add_resource(SkillSpecificDate, '/skill-gateway/specificdate/')
api.add_resource(Timetable, '/skill-gateway/tt/')
api.add_resource(PurgeCache, '/cache/purge/')
api.add_resource(ListCache, '/cache/list/')

# 서버 실행
if __name__ == '__main__':
    app.run(debug=isDebugging)
