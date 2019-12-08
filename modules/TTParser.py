# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/TTParser.py - 컴시간 서버에 접속하여 시간표정보를 파싱해오는 스크립트입니다.

import urllib.request
import urllib.parse as urlparse
import json
import ast
import datetime
import base64
from modules import log
import os

# 학교가 속한 지역과 학교의 이름을 정확히 입력
# 검색 결과가 1개로 특정되도록 해주세요.
# 검색 결과가 2건 이상일 경우, 첫 번째 학교를 선택합니다.
school_region = "경기"
school_name = "흥덕중학교"


def parse(tt_grade, tt_class, year, month, date, req_id, debugging):
    global sunday, data_1, data_2
    part_code = str()
    tt_date = datetime.date(year, month, date)
    tt_grade = int(tt_grade)
    tt_class = int(tt_class)

    log.info(
        "[#%s] parse@modules/TTParser.py: Started Parsing Timetable(%s-%s, %s)" % (req_id, tt_grade, tt_class, tt_date))

    # 데이터 가져오기
    def fetch():
        global part_code, data_1, data_2

        # 학교명으로 검색해 학교코드 알아내기
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
            log.err("[#%s] fetch.parse@modules/TTParser.py: Failed to Parse Timetable(%s-%s, %s)" % (
                req_id, tt_grade, tt_class, tt_date))
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

        # 이번 주 시간표와 다음 주 시간표 가져오기
        try:
            fetch_req_1 = urllib.request.Request(
                'http://comci.kr:4081/98372?' + base64.b64encode(bytes("34739_%s_0_1" % part_code, 'utf-8')).decode(
                    "utf-8"),
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/78.0.3904.70 Safari/537.36'
                }
            )

            fetch_req_2 = urllib.request.Request(
                'http://comci.kr:4081/98372?' + base64.b64encode(bytes("34739_%s_0_2" % part_code, 'utf-8')).decode(
                    "utf-8"),
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/78.0.3904.70 Safari/537.36'
                }
            )

            # 시간표 디코딩
            url_1 = urllib.request.urlopen(fetch_req_1).read().decode('utf-8').replace('\x00', '')
            url_2 = urllib.request.urlopen(fetch_req_2).read().decode('utf-8').replace('\x00', '')
        except Exception as error:
            if debugging:
                print(error)
            log.err("[#%s] fetch.parse@modules/TTParser.py: Failed to Parse Timetable(%s-%s, %s)" %
                    (req_id, tt_grade, tt_class, tt_date))
            return error

        # JSON 파싱
        data_1 = json.loads(url_1)
        data_2 = json.loads(url_2)

        timestamp = int(datetime.datetime.now().timestamp())  # 타임스탬프 생성

        # 캐시 만들기
        with open('data/cache/TT.json', 'w', encoding="utf-8") as make_file:
            json_cache = dict()
            json_cache["1"] = dict()
            json_cache["2"] = dict()
            json_cache["Timestamp"] = timestamp
            # 필요한 자료들만 선별에서 캐싱하기
            json_cache["1"]["자료14"] = data_1["자료14"]
            json_cache["1"]["자료81"] = data_1["자료81"]
            json_cache["1"]["자료46"] = data_1["자료46"]
            json_cache["1"]["자료92"] = data_1["자료92"]
            json_cache["2"]["자료14"] = data_2["자료14"]
            json_cache["2"]["자료81"] = data_2["자료81"]
            json_cache["2"]["자료46"] = data_2["자료46"]
            json_cache["2"]["자료92"] = data_2["자료92"]
            json_cache["2"]["시작일"] = data_2["시작일"]
            json.dump(json_cache, make_file, ensure_ascii=False, indent="\t")
            print("File Created")

    if os.path.isfile('data/cache/TT.json'):  # 캐시 있으면
        try:
            log.info("[#%s] parse@modules/TTParser.py: Read Data in Cache" % req_id)
            with open('data/cache/TT.json', encoding="utf-8") as data_file:  # 캐시 읽기
                global data_1, data_2
                data = json.load(data_file)
                data_1 = data["1"]
                data_2 = data["2"]
        except Exception:  # 캐시 읽을 수 없으면
            try:
                # 캐시 삭제
                os.remove('data/cache/TT.json')
            except Exception as error:
                log.err("[#%s] parse@modules/TTParser.py: Failed to Delete Cache" % req_id)
                return error
            fetch()  # 파싱
        # 캐시 유효하면
        if datetime.datetime.now() - datetime.datetime.fromtimestamp(data["Timestamp"]) < datetime.timedelta(hours=3):
            log.info("[#%s] parse@modules/TTParser.py: Use Data in Cache" % req_id)
        else:  # 캐시 무효하면
            log.info("[#%s] parse@modules/TTParser.py: Cache Expired" % req_id)
            fetch()  # 파싱
    else:  # 캐시 없으면
        log.info("[#%s] parse@modules/TTParser.py: No Cache" % req_id)
        fetch()  # 파싱

    # 날짜비교 기준일(2번째 자료의 시작일) 파싱
    data_2_date = data_2["시작일"].split("-")
    data_2_date = datetime.date(int(data_2_date[0]), int(data_2_date[1]), int(data_2_date[2]))

    # 기준일이 조회일보다 미래이고, 날짜차이가 7일 이내일 때, 첫 번째 자료 선택
    if data_2_date >= tt_date and (data_2_date - tt_date).days <= 7:
        data = data_1
    # 조회일이 기준일보다 미래이고, 날짜차이가 6일 이내일 때, 두 번째 자료 선택
    elif data_2_date <= tt_date and (tt_date - data_2_date).days <= 6:
        data = data_2
    else:
        return None

    tt = data["자료14"][tt_grade][tt_class]  # 자료14에 각 반의 일일시간표 정보가 담겨있음
    og_tt = data["자료81"][tt_grade][tt_class]  # 자료81에 각 반의 원본시간표 정보가 담겨있음
    teacher_list = data["자료46"]  # 교사명단
    subject_list = data["자료92"]  # 2글자로 축약한 과목명단 - 전체 명칭은 긴자료92에 담겨있음

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
                return_data.append("⭐%s(%s)" % (subject, teacher))  # 시간표 변경사항 표시
            else:
                return_data.append("%s(%s)" % (subject, teacher))

    # 단축수업, 연장수업 표시
    tt_num, og_tt_num = 0, 0
    for i in range(1, 9):  # 교시수 구하기
        if not tt[comci_weekday][i] and not tt_num:
            tt_num = i - 1
        if not og_tt[comci_weekday][i] and not og_tt_num:
            og_tt_num = i - 1
    if tt_num == og_tt_num:
        pass
    elif tt_num < og_tt_num:
        return_data.append("[MSG]⭐단축수업이 있습니다. (%s교시 → %s교시)" % (og_tt_num, tt_num))
    elif tt_num > og_tt_num:
        return_data.append("[MSG]⭐연장수업이 있습니다. (%s교시 → %s교시)" % (og_tt_num, tt_num))

    log.info("[#%s] parse@modules/TTParser.py: Succeeded to Parse Timetable(%s-%s, %s)" % (
    req_id, tt_grade, tt_class, tt_date))

    return return_data


# 디버그
if __name__ == "__main__":
    print(parse(3, 11, 2019, 10, 25, "****DEBUG****", True))
