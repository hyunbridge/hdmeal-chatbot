# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/ttparser.py - 컴시간 서버에 접속하여 시간표정보를 파싱해오는 스크립트입니다.

import urllib.request
import urllib.parse as urlparse
import json
import ast
import datetime
import base64

# 학교가 속한 지역과 학교의 이름을 정확히 입력
# 검색 결과가 1개로 특정되도록 해주세요.
# 검색 결과가 2건 이상일 경우, 첫 번째 학교를 선택합니다.
school_region = "경기"
school_name = "흥덕중학교"

def parse(tt_grade, tt_class, year, month, date, debugging):
    global sunday
    part_code = str()
    tt_date = datetime.datetime(year, month, date).date()
    tt_grade = int(tt_grade)
    tt_class = int(tt_class)

    try:
        search_req = urllib.request.Request(
            'http://comci.kr:4081/98372?92744l%s' % urlparse.quote(school_name.encode("EUC-KR")),
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/78.0.3904.70 Safari/537.36'
            }
        )

        search_url = urllib.request.urlopen(search_req)
    except Exception as error:
        if debugging:
            print(error)
        return error

    # 학교 검색결과 가져오기
    school_list = ast.literal_eval(search_url.read().decode('utf-8').replace('\x00', ''))["학교검색"]
    if debugging:
        print(school_list)

    # 검색결과를 지역으로 구분하고 학교코드 가져오기
    for i in school_list:
        if i[1] == school_region:
            part_code = i[3]
            break

    # 이번 주 일요일의 날짜를 구함
    for i in range(6):
        sunday = datetime.datetime.now() + datetime.timedelta(days=i)
        if sunday.weekday() == 6:
            if debugging:
                print(sunday.date())
            break

    # 조회하고자 하는 주를 덧붙여 코드 완성
    if tt_date > sunday.date():
        code = "34739_%s_0_2" % part_code
    else:
        code = "34739_%s_0_1" % part_code

    try:
        fetch_req = urllib.request.Request(
            'http://comci.kr:4081/98372?' + base64.b64encode(bytes(code, 'utf-8')).decode("utf-8"),
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/78.0.3904.70 Safari/537.36'
            }
        )

        fetch_url = urllib.request.urlopen(fetch_req)
    except Exception as error:
        if debugging:
            print(error)
        return error

    fetch_data = json.loads(fetch_url.read().decode('utf-8').replace('\x00', ''))

    tt = fetch_data["자료14"][tt_grade][tt_class]  # 자료14에 각 반의 일일시간표 정보가 담겨있음
    og_tt = fetch_data["자료81"][tt_grade][tt_class]  # 자료81에 각 반의 원본시간표 정보가 담겨있음
    teacher_list = fetch_data["자료46"]  # 교사명단
    subject_list = fetch_data["자료92"]  # 2글자로 축약한 과목명단 - 전체 명칭은 긴자료92에 담겨있음

    # 파이썬의 weekday는 월요일부터 시작하지만
    # 컴시간의 weekday는 일요일부터 시작한다
    # 파이썬 → 컴시간 형식변환
    if tt_date.weekday() == 6:
        comci_weekday = 0
    else:
        comci_weekday = tt_date.weekday() + 1

    if debugging:
        print(tt[comci_weekday])

    return_data = list()
    for i in range(len(tt[comci_weekday])):
        if tt[comci_weekday][i] != 0:
            subject = subject_list[int(str(tt[comci_weekday][i])[-2:])]  # 뒤의 2자리는 과목명을 나타냄
            teacher = teacher_list[int(str(tt[comci_weekday][i])[:-2])]  # 나머지 숫자는 교사명을 나타냄
            if not tt[comci_weekday][i] == og_tt[comci_weekday][i]:
                return_data.append("⭐%s(%s)" % (subject, teacher))
            else:
                return_data.append("%s(%s)" % (subject, teacher))

    return return_data

# 디버그
if __name__ == "__main__":
    print(parse(3, 11, 2019, 10, 25, True))
