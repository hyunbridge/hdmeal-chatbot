# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/skill.py - Skill 응답 데이터를 만드는 스크립트입니다.

import datetime
import json
from collections import OrderedDict
from modules import getdata, cache, user


# Skill 응답용 JSON 생성
def skill(msg):
    return_simple_text = OrderedDict()
    return_outputs = OrderedDict()
    return_list = list()
    return_template = OrderedDict()
    return_data = OrderedDict()
    return_simple_text["text"] = msg
    return_outputs["simpleText"] = return_simple_text
    if not return_outputs in return_list:
        return_list.append(return_outputs)
    return_template["outputs"] = return_list
    return_data["version"] = "2.0"
    return_data["template"] = return_template
    return return_data


# 식단조회 코어
def meal_core(year, month, date, wday, debugging):
    if wday >= 5:  # 주말
        return skill("급식을 실시하지 않습니다. (주말)")
    meal = getdata.meal(year, month, date, debugging)
    if not "message" in meal:  # 파서 메시지 있는지 확인, 없으면 만들어서 응답
        return skill("%s:\n\n%s\n\n열량: %s kcal" % (meal["date"], meal["menu"], meal["kcal"]))
    if meal["message"] == "등록된 데이터가 없습니다.":
        cal = getdata.cal(year, month, date, debugging)
        if not cal == "일정이 없습니다.":
            return skill("급식을 실시하지 않습니다. (%s)" % cal)
    return skill(meal["message"])

# Skill 식단 조회
def meal(reqdata, debugging):
    try:
        sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 가져오기
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        # 년월일 파싱
        year = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[0]
        month = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[1]
        date = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[2]
        wday = datetime.datetime.strptime(sys_date, "%Y-%m-%d").timetuple()[6]
    except ValueError:  # 파싱중 값오류 발생시
        return skill("오류가 발생했습니다.")
    if debugging:
        print(sys_date)
        print(year)
        print(month)
        print(date)
        print(wday)
    return meal_core(year, month, date, wday, debugging)

# Skill 특정날짜(고정값) 식단 조회
def meal_specific_date(reqdata, debugging):
    try:
        specific_date = json.loads(reqdata)["action"]["params"]["date"]
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        # 년월일 파싱
        year = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[0]
        month = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[1]
        date = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[2]
        wday = datetime.datetime.strptime(specific_date, "%Y-%m-%d").timetuple()[6]
    except ValueError:  # 값오류 발생시
        return skill("오류가 발생했습니다.")
    if debugging:
        print(specific_date)
        print(year)
        print(month)
        print(date)
        print(wday)
    return meal_core(year, month, date, wday, debugging)


# Skill 시간표 조회 (등록 사용자용)
def tt_registered(reqdata, debugging):
    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]
        user_data = user.get_user(uid, debugging)  # 사용자 정보 불러오기
        tt_grade = user_data[0]
        tt_class = user_data[1]
    except Exception:
        return skill("오류가 발생했습니다.")
    if tt_grade is not None or tt_class is not None:  # 사용자 정보 있을 때
        try:
            sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 파싱
        except Exception:
            return skill("오류가 발생했습니다.")
        try:
            tt_weekday = datetime.datetime.strptime(sys_date, "%Y-%m-%d").weekday()  # 요일 파싱
        except ValueError:  # 값오류 발생시
            return skill("오류가 발생했습니다.")
        if debugging:
            print(tt_grade)
            print(tt_class)
            print(tt_weekday)
        msg = getdata.tt(tt_grade, tt_class, tt_weekday, debugging)
    else:
        msg = "미등록 사용자입니다.\n먼저 사용자 등록을 해 주시기 바랍니다."
    return skill(msg)

# Skill 시간표 조회 (미등록 사용자용)
def tt(reqdata, debugging):
    try:
        tt_grade = json.loads(reqdata)["action"]["params"]["Grade"]  # 학년 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        tt_class = json.loads(reqdata)["action"]["params"]["Class"]  # 반 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        sys_date = json.loads(json.loads(reqdata)["action"]["params"]["sys_date"])["date"]  # 날짜 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        tt_weekday = datetime.datetime.strptime(sys_date, "%Y-%m-%d").weekday()  # 요일 파싱
    except ValueError:  # 값오류 발생시
        return skill("오류가 발생했습니다.")
    if debugging:
        print(tt_grade)
        print(tt_class)
        print(tt_weekday)
    msg = getdata.tt(tt_grade, tt_class, tt_weekday, debugging)
    return skill(msg)


# 캐시 가져오기
def get_cache(reqdata, debugging):

    # 사용자 ID 가져오고 검증
    uid = json.loads(reqdata)["userRequest"]["user"]["id"]
    if user.auth_admin(uid, debugging):
        cache_list = cache.get(debugging)
        if cache_list == "":
            cache_list = "\n캐시가 없습니다."
        msg = "캐시 목록:" + cache_list
    else:
        msg = "사용자 인증에 실패하였습니다.\n당신의 UID는 %s 입니다." % uid
    return skill(msg)

# 캐시 비우기
def purge_cache(reqdata, debugging):
    # 사용자 ID 가져오고 검증
    uid = json.loads(reqdata)["userRequest"]["user"]["id"]
    if user.auth_admin(uid, debugging):
        if cache.purge(debugging)["status"] == "OK":  # 삭제 실행, 결과 검증
            msg = "캐시를 비웠습니다."
        else:
            msg = "삭제에 실패하였습니다. 오류가 발생했습니다."
    else:
        msg = "사용자 인증에 실패하였습니다.\n당신의 UID는 %s 입니다." % uid
    return skill(msg)


# 사용자 관리
def manage_user(reqdata, debugging):
    try:
        user_grade = json.loads(reqdata)["action"]["params"]["Grade"]  # 학년 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        user_class = json.loads(reqdata)["action"]["params"]["Class"]  # 반 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]  # UID 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    if debugging:
        print(user_grade)
        print(user_class)
        print(uid)
    req = user.manage_user(uid, user_grade, user_class, debugging)
    if req == "Created":
        msg = "등록에 성공했습니다."
    elif req == "Same":
        msg = "저장된 정보와 수정할 정보가 같아 수정하지 않았습니다."
    elif req == "Updated":
        msg = "수정되었습니다."
    else:
        return skill("오류가 발생했습니다.")
    return skill(msg)

# 사용자 삭제
def delete_user(reqdata, debugging):
    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]  # UID 파싱
    except Exception:
        return skill("오류가 발생했습니다.")
    if debugging:
        print(uid)
    req = user.delete_user(uid, debugging)
    if req == "NotExist":
        msg = "존재하지 않는 사용자입니다."
    elif req == "Deleted":
        msg = "삭제에 성공했습니다."
    else:
        return skill("오류가 발생했습니다.")
    return skill(msg)


# 한강 수온 조회
def wtemp(debugging):
    return skill(getdata.wtemp(debugging))