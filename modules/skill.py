# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# skill.py - Skill 응답 데이터를 만드는 스크립트입니다.

import datetime
import json
from collections import OrderedDict
from modules import getdata, cache, user

# Skill 식단 조회
def meal(reqdata, isDebugging):
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
        sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 가져오기
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

# Skill 특정날짜(고정값) 식단 조회
def meal_specific_date(reqdata, isDebugging):
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
        specific_date = json.loads(reqdata)["action"]["params"]["date"]
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

# Skill 시간표 조회 (등록 사용자용)
def tt_registered(reqdata, isDebugging):
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
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]
        user_data = user.get_user(uid, isDebugging) # 사용자 정보 불러오기
        tt_grade = user_data[0]
        tt_class = user_data[1]
    except Exception:
        return_error()

    if tt_grade != "" or tt_class != "":
        try:
            sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 파싱
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

        msg = getdata.tt(tt_grade, tt_class, tt_weekday, isDebugging)
    else:
        msg = "미등록 사용자입니다.\n먼저 사용자 등록을 해 주시기 바랍니다."

    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data

# Skill 시간표 조회 (미등록 사용자용)
def tt(reqdata, isDebugging):
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
        tt_grade = json.loads(reqdata)["action"]["params"]["Grade"]  # 학년 파싱
    except Exception:
        return_error()
    try:
        tt_class = json.loads(reqdata)["action"]["params"]["Class"]  # 반 파싱
    except Exception:
        return_error()
    try:
        sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 파싱
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
    msg = getdata.tt(tt_grade, tt_class, tt_weekday, isDebugging)
    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data


# 캐시 가져오기
def get_cache(reqdata, isDebugging):
    return_simple_text = OrderedDict()
    return_outputs = OrderedDict()
    return_list = list()
    return_template = OrderedDict()
    return_data = OrderedDict()

    # 사용자 ID 가져오고 검증
    uid = json.loads(reqdata)["userRequest"]["user"]["id"]
    if user.auth_admin(uid, isDebugging):
        cache_list = cache.get(isDebugging)
        if cache_list == "":
            cache_list = "\n캐시가 없습니다."
        msg = "캐시 목록:" + cache_list
    else:
        msg = "사용자 인증에 실패하였습니다.\n당신의 UID는 %s 입니다." % uid

    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data

# 캐시 비우기
def purge_cache(reqdata, isDebugging):
    return_simple_text = OrderedDict()
    return_outputs = OrderedDict()
    return_list = list()
    return_template = OrderedDict()
    return_data = OrderedDict()
    # 사용자 ID 가져오고 검증
    uid = json.loads(reqdata)["userRequest"]["user"]["id"]
    if user.auth_admin(uid, isDebugging):
        if cache.purge(isDebugging)["status"] == "OK":  # 삭제 실행, 결과 검증
            msg = "캐시를 비웠습니다."
        else:
            msg = "삭제에 실패하였습니다. 오류가 발생했습니다."
    else:
        msg = "사용자 인증에 실패하였습니다.\n당신의 UID는 %s 입니다." % uid
    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data


# 사용자 관리
def manage_user(reqdata, isDebugging):
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

    user_grade = str()
    user_class = str()
    uid = str()
    msg = str()
    try:
        user_grade = json.loads(reqdata)["action"]["params"]["Grade"]  # 학년 파싱
    except Exception:
        return_error()
    try:
        user_class = json.loads(reqdata)["action"]["params"]["Class"]  # 반 파싱
    except Exception:
        return_error()
    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]  # UID 파싱
    except Exception:
        return_error()

    if isDebugging:
        print(user_grade)
        print(user_class)
        print(uid)

    if user.manage_user(uid, user_grade, user_class, isDebugging):
        msg = "등록에 성공했습니다."
    else:
        return_error()

    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data

# 사용자 삭제
def delete_user(reqdata, isDebugging):
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

    uid = str()
    msg = str()

    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]  # UID 파싱
    except Exception:
        return_error()

    if isDebugging:
        print(uid)

    if user.delete_user(uid, isDebugging):
        msg = "삭제에 성공했습니다."
    else:
        return_error()

    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data


# 한강 수온 조회
def wtemp(isDebugging):
    return_simple_text = OrderedDict()
    return_outputs = OrderedDict()
    return_list = list()
    return_template = OrderedDict()
    return_data = OrderedDict()

    # 스킬 응답용 JSON 생성
    return_simple_text["text"] = getdata.wtemp(isDebugging)
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data
