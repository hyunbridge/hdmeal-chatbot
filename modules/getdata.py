# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# getdata.py - 급식, 시간표, 캐시정보를 가져오는 스크립트입니다.

import os
import urllib.request
import json
from collections import OrderedDict
from modules import mealparser, wtemparser

# 급식정보 가져오기
def meal(year, month, date, isDebugging):
    # 자료형 변환
    year = str(year)
    month = str(month)
    date = str(date)

    if not os.path.isfile('data/cache/' + year.zfill(4) + '-' + month.zfill(2) + '-' + date.zfill(2) + '.json'):
        mealparser.parse(year, month, date, isDebugging)

    json_data = OrderedDict()
    try:
        with open('data/cache/' + year.zfill(4) + '-' + month.zfill(2) + '-' + date.zfill(2) + '.json',
                  encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
            json_data = data
    except FileNotFoundError:  # 파일 없을때
        if isDebugging:
            print("FileNotFound")
        json_data["message"] = "등록된 데이터가 없습니다."
    return json_data


# 시간표정보 가져오기
def tt(tt_grade, tt_class, tt_weekday, isDebugging):
    # Github Juneyoung-Kang님의 KoreanSchoolAPI 사용
    # https://github.com/Juneyoung-Kang/koreanschoolapi

    if tt_weekday >= 5:  # 토요일, 일요일 제외
        return "등록된 데이터가 없습니다."

    try:
        url = urllib.request.urlopen("https://comci.azurewebsites.net/"
                                     "?schoolName=%ED%9D%A5%EB%8D%95%EC%A4%91%ED%95%99%EA%B5%90"
                                     "&gradeNumber=" + tt_grade + "&classNumber=" + tt_class + "&resultType=week")
    except Exception:
        if isDebugging:
            print("오류")
        return ""

    data = url.read().decode('utf-8')

    json_data = json.loads(data)

    data = json_data["data"]["result"][tt_weekday]
    # 헤더 작성. n학년 n반, yyyy-mm-dd(요일): 형식
    header = ("%s학년 %s반,\n%s(%s):\n\n" % (tt_grade, tt_class, data["date"].replace(".", "-"), data["day"].replace("요일", "")))
    if isDebugging:
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

# 한강 수온 가져오기
def wtemp(isDebugging):
    data = wtemparser.get(isDebugging)
    body = "%s %s 측정자료:\n한강 수온은 %s°C 입니다." % (data[0], data[1], data[2])
    return body
