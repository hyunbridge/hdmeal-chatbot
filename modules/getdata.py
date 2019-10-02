# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/getdata.py - 급식, 시간표, 캐시정보를 가져오는 스크립트입니다.

import os
import urllib.request
import json
from collections import OrderedDict
from modules import mealparser, calendarparser, wtemparser

# 급식정보 가져오기
def meal(year, month, date, debugging):
    # 자료형 변환
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    if not os.path.isfile('data/cache/' + year + '-' + month + '-' + date + '.json'):
        mealparser.parse(year, month, date, debugging)

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
def tt(tt_grade, tt_class, tt_weekday, debugging):
    # Github Juneyoung-Kang님의 KoreanSchoolAPI 사용
    # https://github.com/Juneyoung-Kang/koreanschoolapi

    if tt_weekday >= 5:  # 토요일, 일요일 제외
        return "등록된 데이터가 없습니다."

    try:
        url = urllib.request.urlopen("https://comci.azurewebsites.net/"
                                     "?schoolName=%ED%9D%A5%EB%8D%95%EC%A4%91%ED%95%99%EA%B5%90"
                                     "&gradeNumber=" + tt_grade + "&classNumber=" + tt_class + "&resultType=week")
    except Exception:
        if debugging:
            print("오류")
        return ""

    data = url.read().decode('utf-8')

    json_data = json.loads(data)

    data = json_data["data"]["result"][tt_weekday]
    # 헤더 작성. n학년 n반, yyyy-mm-dd(요일): 형식
    header = ("%s학년 %s반,\n%s(%s):\n\n" % (tt_grade, tt_class, data["date"].replace(".", "-"), data["day"].replace("요일", "")))
    if debugging:
        print(header)
    # 본문 작성
    if tt_weekday == 1 or tt_weekday == 3:  # 화, 목
        body = ("1교시: %s\n2교시: %s\n3교시: %s\n4교시: %s\n5교시: %s\n6교시: %s\n7교시: %s"
                % (data["class01"], data["class02"], data["class03"], data["class04"],
                   data["class05"], data["class06"], data["class07"]))
    else:  # 월, 수, 금
        body = ("1교시: %s\n2교시: %s\n3교시: %s\n4교시: %s\n5교시: %s\n6교시: %s"
                % (data["class01"], data["class02"], data["class03"],
                   data["class04"], data["class05"], data["class06"]))
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
            json_data = data
    except FileNotFoundError:  # 파일 없을때
        if debugging:
            print("FileNotFound")
        return "일정이 없습니다."

    # 일정 있는지 확인
    if date in json_data:
        return json_data[date]
    return "일정이 없습니다."


# 한강 수온 가져오기
def wtemp(debugging):
    try:
        data = wtemparser.get(debugging)
        body = "%s %s 측정자료:\n한강 수온은 %s°C 입니다." % (data[0], data[1], data[2])
    except Exception:
        body = "측정소 또는 서버 오류입니다."
    return body


# 디버그
if __name__ == "__main__":
    print(cal(2019, 9, 30, True))