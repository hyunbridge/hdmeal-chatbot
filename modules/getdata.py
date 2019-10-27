# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/getdata.py - 급식, 시간표, 캐시정보를 가져오는 스크립트입니다.

import datetime
import json
import os
from collections import OrderedDict
from modules import mealparser, calendarparser, wtemparser, ttparser, weatherparser


# 급식정보 가져오기
def meal(year, month, date, debugging):
    # 자료형 변환
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    if not os.path.isfile('data/cache/' + year + '-' + month + '-' + date + '.json'):
        parser = mealparser.parse(year, month, date, debugging)
        if parser == "NoData" or parser == "":
            return {"message": "등록된 데이터가 없습니다."}

    json_data = OrderedDict()
    try:
        with open('data/cache/' + year + '-' + month + '-' + date + '.json',
                  encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            json_data = data
    except FileNotFoundError:  # 파일 없을때
        if debugging:
            print("FileNotFound")
        json_data["message"] = "등록된 데이터가 없습니다."
    return json_data


# 시간표정보 가져오기
def tt(tt_grade, tt_class, year, month, date, debugging):

    tt_weekday = datetime.date(year, month, date).weekday()

    if tt_weekday >= 5:  # 토요일, 일요일 제외
        return "등록된 데이터가 없습니다."

    data = ttparser.parse(tt_grade, tt_class, year, month, date, debugging)

    if not data:
        return "등록된 데이터가 없습니다."

    def wday(tt_weekday):
        if tt_weekday == 0:
            return "월"
        elif tt_weekday == 1:
            return "화"
        elif tt_weekday == 2:
            return "수"
        elif tt_weekday == 3:
            return "목"
        elif tt_weekday == 4:
            return "금"
        elif tt_weekday == 5:
            return "토"
        elif tt_weekday == 6:
            return "일"
        else:
            return "오류"

    # 헤더 작성. n학년 n반, yyyy-mm-dd(요일): 형식
    header = ("%s학년 %s반,\n%s(%s):\n" % (
        tt_grade, tt_class, datetime.date(year, month, date), wday(tt_weekday)))
    if debugging:
        print(header)

    # 본문 작성
    body = str()
    for i in range(len(data)):
        body = body + "\n%s교시: %s" % (i+1, data[i])

    return header + body


# 학사일정 가져오기
def cal(year, month, date, debugging):
    # 자료형 변환
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    # 파일 없으면 생성
    if not os.path.isfile('data/cache/Cal-%s-%s.json' % (year, month)):
        calendarparser.parse(year, month, debugging)

    try:
        with open('data/cache/Cal-%s-%s.json' % (year, month),
                  encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
    except FileNotFoundError:  # 파일 없을때
        if debugging:
            print("FileNotFound")
        return "일정이 없습니다."

    # 일정 있는지 확인
    if date in data:
        return data[date]
    return "일정이 없습니다."


# 학사일정 가져오기 (다중)
def cal_mass(start, end, debugging):
    between_month = list()
    between_date = list()
    cal = list()

    delta = (end - start).days  # 시작일과 종료일 사이의 일수를 구함

    for i in range(delta + 1):  # 리스트에 시작일과 종료일 사이의 모든 달과 날짜를 담음
        date = start + datetime.timedelta(days=i)
        between_month.append((str(date.year).zfill(4), str(date.month).zfill(2)))
        between_date.append((str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))

    between_month = sorted(list(set(between_month)))  # List의 중복을 제거하고 정렬

    for i in between_month:  # 대상월의 캐시가 있는지 확인, 없으면 만들기
        if not os.path.isfile('data/cache/Cal-%s-%s.json' % (i[0], i[1])):
            calendarparser.parse(i[0], i[1], debugging)

    for i in between_date:
        try:  # 파일 열기, JSON 데이터를 딕셔너리형으로 변환
            with open('data/cache/Cal-%s-%s.json' % (i[0], i[1]),
                      encoding="utf-8") as data_file:
                data = json.load(data_file, object_pairs_hook=OrderedDict)
        except FileNotFoundError:  # 파일 없을때
            if debugging:
                print("FileNotFound")
            body = "일정이 없습니다."
            cal.append((i[0], i[1], i[2], body))  # 년, 월, 일, 일정
            continue  # 이후 구문 실행 않음

        if i[2] in data:  # 일정이 있는지 확인
            body = data[i[2]]
        else:  # 없으면
            body = "일정이 없습니다."

        cal.append((i[0], i[1], i[2], body))  # 년, 월, 일, 일정

    return cal


# 한강 수온 가져오기
def wtemp(debugging):
    try:
        data = wtemparser.get(debugging)
        body = "%s %s 측정자료:\n한강 수온은 %s°C 입니다." % (data[0], data[1], data[2])
    except Exception:
        body = "측정소 또는 서버 오류입니다."
    return body

# 날씨 가져오기
def weather(debugging):
    weather = weatherparser.parse(debugging)

    return_data = ("🌡️ [오늘/내일] 최소/최대 기온: %s℃/%s℃\n\n"
                   "등굣길 예상 날씨: %s\n"
                   "🌡️ 기온: %s℃\n"
                   "🌦️ 강수 형태: %s\n"
                   "❔ 강수 확률: %s%%\n"
                   "💧 습도: %s%%" % (weather['temp_min'], weather['temp_max'], weather['sky'], weather['temp'],
                                    weather['pty'], weather['pop'], weather['reh']))

    return return_data

# 디버그
if __name__ == "__main__":
    # print(cal_mass(datetime.datetime(2019, 12, 1), datetime.datetime(2020, 2, 29), True))
    print(tt(3, 11, 2019, 10, 25, True))
