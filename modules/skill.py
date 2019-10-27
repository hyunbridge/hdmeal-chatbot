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
from modules import getdata, cache, user


# Skill 응답용 JSON 생성
def skill(msg):
    return {'version': '2.0',
            'data': {
                'msg': msg
            }
            }


def skill_simpletext(msg):
    return {'version': '2.0',
            'template': {
                'outputs': [
                    {
                        'simpleText': {
                            'text': msg
                        }
                    }
                ]
            }
            }


# 식단조회 코어
def meal_core(year, month, date, wday, debugging):
    if wday >= 5:  # 주말
        return "급식을 실시하지 않습니다. (주말)"
    meal = getdata.meal(year, month, date, debugging)
    if not "message" in meal:  # 파서 메시지 있는지 확인, 없으면 만들어서 응답
        return "%s:\n\n%s\n\n열량: %s kcal" % (meal["date"], meal["menu"], meal["kcal"])
    if meal["message"] == "등록된 데이터가 없습니다.":
        cal = getdata.cal(year, month, date, debugging)
        if not cal == "일정이 없습니다.":
            return "급식을 실시하지 않습니다. (%s)" % cal
    return meal["message"]


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
    return skill(meal_core(year, month, date, wday, debugging))


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
    return skill(meal_core(year, month, date, wday, debugging))


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
            date = datetime.datetime.strptime(sys_date, "%Y-%m-%d")
        except ValueError:  # 값오류 발생시
            return skill("오류가 발생했습니다.")
        if debugging:
            print(tt_grade)
            print(tt_class)
        msg = getdata.tt(tt_grade, tt_class, date.year, date.month, date.day, debugging)
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
        date = datetime.datetime.strptime(sys_date, "%Y-%m-%d")
    except ValueError:  # 값오류 발생시
        return skill("오류가 발생했습니다.")
    if debugging:
        print(tt_grade)
        print(tt_class)
    msg = getdata.tt(tt_grade, tt_class, date.year, date.month, date.day, debugging)
    return skill(msg)


# 일정 후처리(잡정보들 삭제)
def pstpr(cal):
    return cal.replace("일정이 없습니다.", "").replace("토요휴업일", "").replace("여름방학", "") \
        .replace("겨울방학", "").strip()


# 요일 처리
def wday(date):
    if date.weekday() == 0:
        return "월"
    elif date.weekday() == 1:
        return "화"
    elif date.weekday() == 2:
        return "수"
    elif date.weekday() == 3:
        return "목"
    elif date.weekday() == 4:
        return "금"
    elif date.weekday() == 5:
        return "토"
    else:
        return "일"


# Skill 학사일정 조회
def cal(reqdata, debugging):
    global msg

    try:
        data = json.loads(reqdata)["action"]["params"]
    except Exception:
        return skill("오류가 발생했습니다.")

    # 특정일자 조회
    if "sys_date" in data:
        try:
            date = datetime.datetime.strptime(json.loads(data["sys_date"])["date"], "%Y-%m-%d")  # 날짜 파싱
        except Exception:
            return skill("오류가 발생했습니다.")

        cal = getdata.cal(date.year, date.month, date.day, debugging)

        cal = pstpr(cal)
        if cal:
            msg = "%s-%s-%s(%s):\n%s" % (date.year, date.month, date.day, wday(date), cal)  # YYYY-MM-DD(Weekday)
        else:
            msg = "일정이 없습니다."
    # 특정일자 조회 끝

    # 기간 조회
    elif "sys_date_period" in data:  # 기간

        body = str()

        try:
            start = json.loads(data["sys_date_period"])["from"]["date"]  # 시작일 파싱
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
        except Exception:
            return skill("오류가 발생했습니다.")
        try:
            end = json.loads(data["sys_date_period"])["to"]["date"]  # 종료일 파싱
            end = datetime.datetime.strptime(end, "%Y-%m-%d")
        except Exception:
            return skill("오류가 발생했습니다.")

        if (end - start).days > 90:  # 90일 이상을 조회요청한 경우,
            head = ("서버 성능상의 이유로 최대 90일까지만 조회가 가능합니다."
                    "\n조회기간이 %s부터 %s까지로 제한되었습니다.\n\n" %
                    (start.date(), (start + datetime.timedelta(days=90)).date()))
            end = start + datetime.timedelta(days=90)  # 종료일 앞당김
        else:
            head = "%s부터 %s까지 조회합니다.\n\n" % (start.date(), end.date())

        cal = getdata.cal_mass(start, end, debugging)
        # 년, 월, 일, 일정 정보를 담은 튜플이 리스트로 묶여서 반환됨

        for i in cal:
            date = datetime.date(int(i[0]), int(i[1]), int(i[2]))  # 년, 월, 일
            cal = i[3]  # 일정

            cal = pstpr(cal)
            if cal:
                body = "%s%s-%s-%s(%s):\n%s\n" % (body, i[0], i[1], i[2], wday(date), cal)  # YYYY-MM-DD(Weekday)

        if not body:
            body = "일정이 없습니다.\n"
        msg = (head + body)[:-1]  # 맨 끝의 줄바꿈을 제거함
        # 기간 조회 끝

    else:  # 아무런 파라미터도 넘겨받지 못한 경우
        return skill("오늘, 이번 달 등의 날짜 또는 기간을 입력해 주세요.")

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


# 급식봇 브리핑
def briefing(reqdata, debugging):
    if datetime.datetime.now().time() >= datetime.time(9):  # 9시 이후이면
        # 내일을 기준일로 설정
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        date_ko = "내일"
    else:  # 9시 이전이면
        # 오늘을 기준일로 설정
        date = datetime.datetime.now()
        date_ko = "오늘"

    # 첫 번째 말풍선
    # 헤더
    if date.weekday() >= 5:  # 주말이면
        return skill_simpletext("%s은 주말 입니다." % date_ko)
    else:
        header = "%s은 %s(%s) 입니다." % (date_ko, date.date().isoformat(), wday(date))
    # 학사일정
    cal = pstpr(getdata.cal(date.year, date.month, date.day, debugging))
    if not cal:
        cal = "%s은 학사일정이 없습니다." % date_ko
    else:
        cal = "%s 학사일정:\n\n%s" % (date_ko, cal)

    # 두 번째 말풍선
    # 날씨
    weather = getdata.weather(debugging).replace('[오늘/내일]', date_ko)

    # 세 번째 말풍선
    # 급식
    meal = meal_core(date.year, date.month, date.day, date.weekday(), debugging)
    if "급식을 실시하지 않습니다." in meal:
        meal = "%s은 %s" % (date_ko, meal)
    elif "열량" in meal:
        meal = "%s 급식:\n%s" % (date_ko, meal[16:].replace('\n\n', '\n'))  # 헤더부분 제거, 줄바꿈 2번 → 1번
    # 시간표
    try:
        uid = json.loads(reqdata)["userRequest"]["user"]["id"]
        user_data = user.get_user(uid, debugging)  # 사용자 정보 불러오기
        tt_grade = user_data[0]
        tt_class = user_data[1]
    except Exception:
        return skill_simpletext("오류가 발생했습니다.")
    if tt_grade is not None or tt_class is not None:  # 사용자 정보 있을 때
        tt = "%s 시간표:\n%s" % (date_ko,
                              getdata.tt(tt_grade, tt_class, date.year, date.month, date.day, debugging)
                              .split('):\n\n')[1])  # 헤더부분 제거
    else:
        tt = "등록된 사용자만 시간표를 볼 수 있습니다."

    # 응답 만들기
    return {'version': '2.0',
            'template': {
                'outputs': [
                    {
                        'simpleText': {
                            'text': "%s\n\n%s" % (header, cal)
                        }
                    },
                    {
                        'simpleText': {
                            'text': weather
                        }
                    },
                    {
                        'simpleText': {
                            'text': "%s\n\n%s" % (meal, tt)
                        }
                    }
                ]
            }
            }


# 디버그
if __name__ == "__main__":
    print(skill("msg"))
