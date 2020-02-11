# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/chat.py - Skill 응답 데이터를 만드는 스크립트입니다.

import datetime
import hashlib
import json
import re
import time
from itertools import groupby
from threading import Thread
import requests
from modules import getData, user, log, LoL, conf, security


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


def getuserid(uid):
    enc = hashlib.sha256()
    enc.update(uid.encode("utf-8"))
    return 'KT-' + enc.hexdigest()


def router(uid: str, intent: str, params: dict, req_id: str, debugging: bool):
    if 'Briefing' in intent:
        return briefing(uid, req_id, debugging)
    elif 'Meal' in intent:
        return meal(params, req_id, debugging)
    elif 'Timetable' in intent:
        return timetable(uid, params, req_id, debugging)
    elif 'Schedule' in intent:
        return schdl(params, req_id, debugging)
    elif 'WaterTemperature' in intent:
        return [getData.wtemp(req_id, debugging)], None
    elif 'UserSettings' in intent:
        return user_settings(uid, req_id)
    elif 'LoL' in intent:
        return lol(params, req_id, debugging)
    else:
        return ["오류가 발생했습니다.\n요청 ID: " + req_id], None


# 식단조회
def meal(params: dict, req_id: str, debugging: bool):
    if not params['date']:
        return ["언제의 급식을 조회하시겠어요?"], None
    if isinstance(params['date'], datetime.datetime):
        date: datetime = params['date']
        if date.weekday() >= 5:  # 주말
            return ["급식을 실시하지 않습니다. (주말)"], None
        meal = getData.meal(date.year, date.month, date.day, req_id, debugging)
        if not "message" in meal:  # 파서 메시지 있는지 확인, 없으면 만들어서 응답
            return ["%s:\n\n%s\n\n열량: %s kcal" % (meal["date"], meal["menu"], meal["kcal"])], None
        if meal["message"] == "등록된 데이터가 없습니다.":
            cal = getData.schdl(date.year, date.month, date.day, req_id, debugging)
            if not cal == "일정이 없습니다.":
                return ["급식을 실시하지 않습니다. (%s)" % cal], None
        return [meal["message"]], None
    else:
        return ["정확한 날짜를 입력해주세요.\n현재 식단조회에서는 여러날짜 조회를 지원하지 않습니다."], None


# 시간표 조회
def timetable(uid: str, params: dict, req_id: str, debugging: bool):
    log.info("[#%s] tt_registered@modules/chat.py: New Request" % req_id)
    user_data = user.get_user(uid, req_id, debugging)  # 사용자 정보 불러오기
    tt_grade = user_data[0]
    tt_class = user_data[1]
    if not tt_grade or not tt_class:
        return ["내 정보 등록을 해주세요."], None
    if not params['date']:
        return ["언제의 시간표를 조회하시겠어요?"], None
    if isinstance(params['date'], datetime.datetime):
        date: datetime = params['date']
        return [getData.tt(tt_grade, tt_class, date, req_id, debugging)], None
    else:
        return ["정확한 날짜를 입력해주세요.\n현재 시간표조회에서는 여러날짜 조회를 지원하지 않습니다."], None


# 학사일정 조회
def schdl(params: dict, req_id: str, debugging: bool):
    global msg
    log.info("[#%s] cal@modules/chat.py: New Request" % req_id)
    if "date" in params:
        if not params['date']:
            return ["언제의 학사일정을 조회하시겠어요?"], None
        # 특정일자 조회
        if isinstance(params['date'], datetime.datetime):
            try:
                date: datetime = params["date"]
            except Exception:
                log.err("[#%s] cal@modules/chat.py: Error while Parsing Date" % req_id)
                return ["오류가 발생했습니다.\n요청 ID: " + req_id], None

            prsnt_schdl = getData.schdl(date.year, date.month, date.day, req_id, debugging)

            prsnt_schdl = prsnt_schdl
            if prsnt_schdl:
                msg = "%s-%s-%s(%s):\n%s" % (str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2),
                                             wday(date), prsnt_schdl)  # YYYY-MM-DD(Weekday)
            else:
                msg = "일정이 없습니다."
        # 특정일자 조회 끝
        # 기간 조회
        elif isinstance(params['date'], list):  # 기간
            body = str()
            try:
                start: datetime = params['date'][0]  # 시작일 파싱
            except Exception:
                log.err("[#%s] cal@modules/chat.py: Error while Parsing StartDate" % req_id)
                return ["오류가 발생했습니다.\n요청 ID: " + req_id], None
            try:
                end: datetime = params['date'][1]  # 종료일 파싱
            except Exception:
                log.err("[#%s] cal@modules/chat.py: Error while Parsing EndDate" % req_id)
                return ["오류가 발생했습니다.\n요청 ID: " + req_id], None

            if (end - start).days > 90:  # 90일 이상을 조회요청한 경우,
                head = ("서버 성능상의 이유로 최대 90일까지만 조회가 가능합니다."
                        "\n조회기간이 %s부터 %s까지로 제한되었습니다.\n\n" %
                        (start.date(), (start + datetime.timedelta(days=90)).date()))
                end = start + datetime.timedelta(days=90)  # 종료일 앞당김
            else:
                head = "%s부터 %s까지 조회합니다.\n\n" % (start.date(), end.date())

            schdls = getData.schdl_mass(start, end, req_id, debugging)
            # 년, 월, 일, 일정 정보를 담은 튜플이 리스트로 묶여서 반환됨

            # body 쓰기, 연속되는 일정은 묶어 처리함
            for content, group in groupby(schdls, lambda k: k[3]):
                lst = [*group]
                if lst[0] != lst[-1]:
                    start_date = datetime.date(*lst[0][:3])
                    end_date = datetime.date(*lst[-1][:3])
                    body = '%s%s(%s)~%s(%s):\n%s\n' % (
                        body, start_date, wday(start_date), end_date, wday(end_date), content)
                else:
                    date = datetime.date(*lst[0][:3])
                    body = '%s%s(%s):\n%s\n' % (body, date, wday(date), content)

            if not body:
                body = "일정이 없습니다.\n"
            msg = (head + body)[:-1]  # 맨 끝의 줄바꿈을 제거함
            # 기간 조회 끝

    else:  # 아무런 파라미터도 넘겨받지 못한 경우
        log.info("[#%s] cal@modules/chat.py: No Parameter" % req_id)
        return ["언제의 학사일정을 조회하시겠어요?"], None

    return [msg], None


# 급식봇 브리핑
def briefing(uid: str, req_id: str, debugging: bool):
    log.info("[#%s] briefing@modules/chat.py: New Request" % req_id)
    global briefing_header, hd_err, briefing_schdl, briefing_weather, briefing_meal, briefing_meal_ga, briefing_tt
    briefing_header = "일시적인 서버 오류로 헤더를 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."
    briefing_schdl = "일시적인 서버 오류로 학사일정을 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."
    briefing_weather = "일시적인 서버 오류로 날씨를 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."
    briefing_meal = "일시적인 서버 오류로 식단을 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."
    briefing_meal_ga = "일시적인 서버 오류로 식단을 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."
    briefing_tt = "일시적인 서버 오류로 시간표를 불러올 수 없었습니다.\n나중에 다시 시도해 보세요."

    if datetime.datetime.now().time() >= datetime.time(11):  # 11시 이후이면
        # 내일을 기준일로 설정
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        date_ko = "내일"
    else:  # 9시 이전이면
        # 오늘을 기준일로 설정
        date = datetime.datetime.now()
        date_ko = "오늘"

    log.info("[#%s] briefing@modules/chat.py: Date: %s" % (req_id, date))

    def logging_time(original_fn):
        def wrapper_fn(*args, **kwargs):
            result = original_fn(*args, **kwargs)
            if debugging:
                start_time = time.time()
                print("{} 실행.".format(original_fn.__name__))
                end_time = time.time()
                print("{} 종료. 실행시간: {} 초".format(original_fn.__name__, end_time - start_time))
            return result

        return wrapper_fn

    # 첫 번째 말풍선
    # 헤더
    @logging_time
    def f_header():
        global briefing_header, hd_err
        if date.weekday() >= 5:  # 주말이면
            log.info("[#%s] briefing@modules/chat.py: Weekend" % req_id)
            hd_err = "%s은 주말 입니다." % date_ko
        else:
            briefing_header = "%s은 %s(%s) 입니다." % (date_ko, date.date().isoformat(), wday(date))
            hd_err = None

    # 학사일정
    @logging_time
    def f_cal():
        global briefing_schdl
        briefing_schdl = getData.schdl(date.year, date.month, date.day, req_id, debugging)
        if not briefing_schdl:
            log.info("[#%s] briefing@modules/chat.py: No Schedule" % req_id)
            briefing_schdl = "%s은 학사일정이 없습니다." % date_ko
        else:
            briefing_schdl = "%s 학사일정:\n%s" % (date_ko, briefing_schdl)

    # 두 번째 말풍선
    # 날씨
    @logging_time
    def f_weather():
        global briefing_weather
        briefing_weather = getData.weather(date_ko, req_id, debugging)

    # 세 번째 말풍선
    # 급식
    @logging_time
    def f_meal():
        global briefing_meal, briefing_meal_ga
        briefing_meal = meal({'date': date}, req_id, debugging)[0][0]
        if "급식을 실시하지 않습니다." in briefing_meal:
            log.info("[#%s] briefing@modules/chat.py: No Meal" % req_id)
            briefing_meal_ga = date_ko + "은 급식을 실시하지 않습니다."
            briefing_meal = "%s은 %s" % (date_ko, briefing_meal)
        elif "열량" in briefing_meal:
            briefing_meal_ga = "%s 급식은 %s 입니다." % (
                date_ko, re.sub(r'\[[^\]]*\]', '',
                                # 헤더, 줄바꿈 제거하고 반점 뒤 띄어쓰기
                                briefing_meal[16:].replace('\n', '').replace(',', ', ')
                                # 맛있는 메뉴 표시, 마침표 제거하기
                                .replace('⭐', '').split('.')[0]))
            briefing_meal = "%s 급식:\n%s" % (date_ko, briefing_meal[16:].replace('\n\n', '\n'))  # 헤더부분 제거, 줄바꿈 2번 → 1번

    # 시간표
    @logging_time
    def f_tt():
        global briefing_tt
        tt_grade = int()
        tt_class = int()
        try:
            user_data = user.get_user(uid, req_id, debugging)  # 사용자 정보 불러오기
            tt_grade = user_data[0]
            tt_class = user_data[1]
        except Exception:
            log.err("[#%s] briefing@modules/chat.py: Failed to Fetch Timetable" % req_id)
            briefing_tt = "시간표 조회 중 오류가 발생했습니다."
        if tt_grade is not None or tt_class is not None:  # 사용자 정보 있을 때
            tt = getData.tt(tt_grade, tt_class, date, req_id, debugging)
            if tt == "등록된 데이터가 없습니다.":
                briefing_tt = "등록된 시간표가 없습니다."
            else:
                briefing_tt = "%s 시간표:\n%s" % (date_ko, tt.split('):\n\n')[1])  # 헤더부분 제거
        else:
            log.info("[#%s] briefing@modules/chat.py: Non-Registered User" % req_id)
            briefing_tt = "등록된 사용자만 시간표를 볼 수 있습니다."

    # 쓰레드 정의
    th_header = Thread(target=f_header)
    th_cal = Thread(target=f_cal)
    th_weather = Thread(target=f_weather)
    th_meal = Thread(target=f_meal)
    th_tt = Thread(target=f_tt)
    # 쓰레드 실행
    th_header.start()
    th_cal.start()
    th_weather.start()
    th_meal.start()
    th_tt.start()
    # 전 쓰레드 종료 시까지 기다리기
    th_header.join()
    if hd_err:
        return [hd_err], None, '안녕하세요, 흥덕고 급식봇입니다.\n' + hd_err
    th_cal.join()
    th_weather.join()
    th_meal.join()
    th_tt.join()

    # 구글어시스턴트 응답
    ga_respns = '안녕하세요, 흥덕고 급식봇입니다.\n' + briefing_meal_ga

    # 응답 만들기
    return ["%s\n\n%s" % (briefing_header, briefing_schdl), briefing_weather,
            "%s\n\n%s" % (briefing_meal, briefing_tt)], None, ga_respns


def lol(params, req_id, debugging):
    log.info("[#%s] lol@modules/chat.py: New Request" % req_id)
    try:
        summoner_name = params["summonerName"]
    except KeyError:
        return ["소환사명을 입력해주세요."], None
    except Exception:
        log.err("[#%s] lol@modules/chat.py: Error while Parsing Summoner Name" % req_id)
        return ["오류가 발생했습니다.\n요청 ID: " + req_id], None

    # 소환사명 16자 초과하면
    if len(summoner_name) > 16:
        log.info("[#%s] lol@modules/chat.py: Summoner Name is Too Long" % req_id)

        return [{
            "type": "card",
            "title": "소환사명이 너무 김",
            "body": "소환사명이 너무 깁니다.\n"
                    "소환사명은 영문 16자, 한글 8자 이내입니다.\n"
                    "잘못 입력하진 않았는지 확인해주세요.",
        }], None

    try:
        summoner_data = LoL.parse(summoner_name, req_id, debugging)
    except Exception:
        log.err("[#%s] lol@modules/chat.py: Error while Parsing Summoner Data" % req_id)
        return ["오류가 발생했습니다.\n요청 ID: " + req_id], None

    if summoner_data == 'Invalid Token':
        log.err("[#%s] lol@modules/chat.py: Invalid Token" % req_id)
        return ["오류가 발생했습니다.\n요청 ID: " + req_id], None

    if summoner_data:
        # 솔랭 전적 구하기
        if summoner_data["ranked_solo"]:
            solo = ("솔랭 전적:\n"
                    "%s %s (%s LP)\n"
                    "%s승 %s패 (%s%%)\n\n" %
                    (summoner_data["ranked_solo"]["tier"], summoner_data["ranked_solo"]["rank"],
                     summoner_data["ranked_solo"]["leaguePoints"],
                     summoner_data["ranked_solo"]["wins"],
                     summoner_data["ranked_solo"]["losses"],
                     summoner_data["ranked_solo"]["winningRate"]))
        else:
            solo = "솔랭 전적이 없습니다. 분발하세요!\n\n"

        # 자유랭 전적 구하기
        if summoner_data["ranked_flex"]:
            flex = ("자유랭 전적:\n"
                    "%s %s (%s LP)\n"
                    "%s승 %s패 (%s%%)\n\n" %
                    (summoner_data["ranked_flex"]["tier"], summoner_data["ranked_flex"]["rank"],
                     summoner_data["ranked_flex"]["leaguePoints"],
                     summoner_data["ranked_flex"]["wins"],
                     summoner_data["ranked_flex"]["losses"],
                     summoner_data["ranked_flex"]["winningRate"]))
        else:
            flex = "자유랭 전적이 없습니다. 분발하세요!\n\n"

        # 통계 내기
        if summoner_data["games"]:
            if summoner_data["preferredLane"]:
                preferred_lane = "%s(%s%%)" % (summoner_data["preferredLane"][0], summoner_data["preferredLane"][1])
            else:
                preferred_lane = "정보없음"
            if summoner_data["preferredChampion"]:
                preferred_champion = ("%s(%s%%)" %
                                      (summoner_data["preferredChampion"][0], summoner_data["preferredChampion"][1]))
            else:
                preferred_champion = "정보없음"
            preferences = ("최근 %s번의 매치를 바탕으로 분석한 결과입니다:\n"
                           "많이한 라인: %s\n"
                           "많이한 챔피언: %s") % (summoner_data["games"], preferred_lane, preferred_champion)
        else:
            preferences = "통계가 없습니다. 분발하세요!"

        return [{
            "type": "card",
            "title": "%s (레벨 %s)" % (summoner_data["summoner"]["name"], summoner_data["summoner"]["level"]),
            "body": solo + flex + preferences,
            'image': summoner_data["summoner"]["profileIcon"],
            "buttons": [
                {
                    "type": "web",
                    "title": "OP.GG에서 보기",
                    "url": summoner_data["summoner"]["OPGG"]
                },
                {
                    "type": "message",
                    "title": "다른 소환사 검색하기"
                }
            ]
        }], None
    else:
        return [{
            "type": "card",
            "title": "소환사를 찾을 수 없음",
            "body": summoner_name + " 소환사를 찾을 수 없습니다.\n"
                                    "한국 서버에 등록된 소환사가 맞는지, "
                                    "잘못 입력하진 않았는지 확인해주세요.",
            "buttons": [
                {
                    "type": "message",
                    "title": "다시 검색하기"
                }
            ]
        }], None


def user_settings(uid: str, req_id: str):
    url = conf.configs['Misc']['SettingsURL']
    return [{
        "type": "card",
        "title": "내 정보 관리",
        "body": "아래 버튼을 클릭해 관리 페이지로 접속해 주세요.\n"
                "링크는 10분 뒤 만료됩니다.",
        "buttons": [
            {
                "type": "web",
                "title": "내 정보 관리",
                "url": url + "?token=" + security.generate_token('UserSettings', uid, ['GetUserInfo', 'ManageUserInfo', 'GetUsageData', 'DeleteUsageData'], req_id)
            }
        ]
    }], None


def notify(reqdata, req_id, debugging):
    now = datetime.datetime.now()
    try:
        onesignal_app_id = json.loads(reqdata)["OneSignal"]["AppID"]
        onesignal_api_key = json.loads(reqdata)["OneSignal"]["APIKey"]
    except Exception:
        return {"message": "OneSignal AppID 또는 APIKey 없음"}, 401
    try:
        title = json.loads(reqdata)["Title"]
        url = json.loads(reqdata)["URL"]
    except Exception:
        return {"message": "올바른 요청이 아님"}, 400
    if now.weekday() >= 5:
        return {"message": "알림미발송(주말)"}
    meal = getData.meal(now.year, now.month, now.day, req_id, debugging)
    if not "menu" in meal:
        return {"message": "알림미발송(정보없음)"}
    reqbody = {
        "app_id": onesignal_app_id,
        "headings": {
            "en": title
        },
        "contents": {
            "en": meal["date"] + " 급식:\n" + re.sub(r'\[[^\]]*\]', '', meal["menu"]).replace('⭐', '')
        },
        "url": url,
        "included_segments": [
            "All"
        ]
    }
    reqheader = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + onesignal_api_key
    }
    try:
        request = requests.post("https://onesignal.com/api/v1/notifications", data=json.dumps(reqbody),
                                headers=reqheader)
    except Exception as error:
        return error
    return {"message": "성공"}


# 디버그
if __name__ == "__main__":
    log.init()
