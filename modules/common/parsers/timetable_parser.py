# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# timetable_parser.py - 컴시간 서버에 접속하여 시간표정보를 파싱해오는 스크립트입니다.

import ast
import base64
import datetime
import json
import os
import re
import urllib.error
import urllib.parse as urlparse
import urllib.request

from modules.common import conf, log

# 컴시간알리미 웹사이트 URL
url = "http://comci.kr/st/"

# 기타 옵션 입력
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
}

school_region = conf.configs['School']['Region']
school_name = conf.configs['School']['Name']


def parse(tt_grade, tt_class, year, month, date, req_id, debugging):
    global sunday, data_1, data_2
    part_code = str()
    tt_date = datetime.date(year, month, date)
    tt_grade = int(tt_grade)
    tt_class = int(tt_class)

    log.info(
        "[#%s] parse@timetable_parser.py: Started Parsing Timetable(%s-%s, %s)" % (req_id, tt_grade, tt_class, tt_date))

    # 데이터 가져오기
    def fetch():
        global part_code, data_1, data_2
        try:
            # BaseURL 알아내기
            baseurl_req = urllib.request.Request(url, data=None, headers=headers)
            baseurl_respns = urllib.request.urlopen(baseurl_req, timeout=2).read().decode('EUC-KR')
            baseurl_pattern = re.compile("src='.*?/st'")
            baseurl_matches = baseurl_pattern.findall(baseurl_respns)
            if baseurl_matches:
                base_url = baseurl_matches[0].split("'")[1][:-2]
            else:
                raise Exception

            # school_ra, sc_data, 자료위치 알아내기
            init_req = urllib.request.Request(base_url + 'st', data=None, headers=headers)
            init_respns = urllib.request.urlopen(init_req, timeout=2).read().decode('EUC-KR')
            # school_ra
            school_ra_pattern = re.compile("url:'.?(.*?)'")
            school_ra_matches = school_ra_pattern.findall(init_respns)
            if school_ra_matches:
                school_ra = school_ra_matches[0][1:]
                school_ra_code = school_ra.split('?')[0]
            else:
                raise Exception
            # sc_data
            sc_data_pattern = re.compile("sc_data\('[0-9].*?\);")
            sc_data_matches = sc_data_pattern.findall(init_respns)
            if sc_data_matches:
                sc_data = sc_data_matches[0].split("'")[1]
            else:
                raise Exception
            # 일일시간표
            daily_timetable_pattern = re.compile("일일자료=자료.*?\[")
            daily_timetable_matches = daily_timetable_pattern.findall(init_respns)
            if daily_timetable_matches:
                daily_timetable = daily_timetable_matches[0].split('자료.')[1][:-1]
            else:
                raise Exception
            # 원본시간표
            original_timetable_pattern = re.compile("원자료=자료.*?\[")
            original_timetable_matches = original_timetable_pattern.findall(init_respns)
            if original_timetable_matches:
                original_timetable = original_timetable_matches[0].split('자료.')[1][:-1]
            else:
                raise Exception
            # 교사명
            teachers_list_pattern = re.compile("성명=자료.*?\[th")
            teachers_list_matches = teachers_list_pattern.findall(init_respns)
            if teachers_list_matches:
                teachers_list = teachers_list_matches[0].split('자료.')[1][:-3]
            else:
                raise Exception
            # 과목명
            subjects_list_pattern = re.compile('"\'>"\+자료.*?\[sb')
            subjects_list_matches = subjects_list_pattern.findall(init_respns)
            if subjects_list_matches:
                subjects_list = subjects_list_matches[0].split('자료.')[1][:-3]
            else:
                raise Exception

            # 학교명으로 검색해 학교코드 알아내기
            search_req = urllib.request.Request(
                base_url + school_ra + urlparse.quote(school_name.encode("EUC-KR")),
                data=None, headers=headers
            )

            search_url = urllib.request.urlopen(search_req, timeout=2)

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
            fetch_req_1 = urllib.request.Request(
                base_url + school_ra_code + '?' + base64.b64encode(
                    bytes(sc_data + str(part_code) + "_0_1", 'utf-8'))
                .decode("utf-8"),
                data=None, headers=headers
            )

            fetch_req_2 = urllib.request.Request(
                base_url + school_ra_code + '?' + base64.b64encode(
                    bytes(sc_data + str(part_code) + "_0_2", 'utf-8'))
                .decode("utf-8"),
                data=None, headers=headers
            )

            # 시간표 디코딩
            url_1 = urllib.request.urlopen(fetch_req_1, timeout=2).read().decode('utf-8').replace('\x00', '')
            url_2 = urllib.request.urlopen(fetch_req_2, timeout=2).read().decode('utf-8').replace('\x00', '')

            # JSON 파싱
            data_1_raw = json.loads(url_1)
            data_2_raw = json.loads(url_2)

            timestamp = int(datetime.datetime.now().timestamp())  # 타임스탬프 생성

            # 캐시 만들기
            json_cache = dict()
            json_cache["1"] = dict()
            json_cache["2"] = dict()
            json_cache["Timestamp"] = timestamp
            # 필요한 자료들만 선별해서 캐싱하기
            json_cache["1"]["dailyTimetable"] = data_1_raw[daily_timetable]
            json_cache["1"]["originalTimetable"] = data_1_raw[original_timetable]
            json_cache["1"]["teachersList"] = data_1_raw[teachers_list]
            json_cache["1"]["subjectsList"] = data_1_raw[subjects_list]
            json_cache["2"]["dailyTimetable"] = data_2_raw[daily_timetable]
            json_cache["2"]["originalTimetable"] = data_2_raw[original_timetable]
            json_cache["2"]["teachersList"] = data_2_raw[teachers_list]
            json_cache["2"]["subjectsList"] = data_2_raw[subjects_list]
            json_cache["2"]["startDate"] = data_2_raw["시작일"]
            with open('data/cache/TT.json', 'w', encoding="utf-8") as make_file:
                json.dump(json_cache, make_file, ensure_ascii=False)
                print("File Created")

            # 이후 파서에서 이용할 수 있도록 data 정의
            data_1 = json_cache["1"]
            data_2 = json_cache["2"]
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            log.err("[#%s] fetch.parse@timetable_parser.py: Failed to Parse Timetable(%s-%s, %s) because %s" % (
                req_id, tt_grade, tt_class, tt_date, e))
            raise ConnectionError

    if os.path.isfile('data/cache/TT.json'):  # 캐시 있으면
        try:
            log.info("[#%s] parse@timetable_parser.py: Read Data in Cache" % req_id)
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
                log.err("[#%s] parse@timetable_parser.py: Failed to Delete Cache" % req_id)
                return error
            fetch()  # 파싱
        # 캐시 유효하면
        if datetime.datetime.now() - datetime.datetime.fromtimestamp(data["Timestamp"]) < datetime.timedelta(hours=3):
            log.info("[#%s] parse@timetable_parser.py: Use Data in Cache" % req_id)
        else:  # 캐시 무효하면
            log.info("[#%s] parse@timetable_parser.py: Cache Expired" % req_id)
            fetch()  # 파싱
    else:  # 캐시 없으면
        log.info("[#%s] parse@timetable_parser.py: No Cache" % req_id)
        fetch()  # 파싱

    # 날짜비교 기준일(2번째 자료의 시작일) 파싱
    data_2_date = data_2["startDate"].split("-")
    data_2_date = datetime.date(int(data_2_date[0]), int(data_2_date[1]), int(data_2_date[2]))

    # 기준일이 조회일보다 미래이고, 날짜차이가 7일 이내일 때, 첫 번째 자료 선택
    if data_2_date >= tt_date and (data_2_date - tt_date).days <= 7:
        data = data_1
    # 조회일이 기준일보다 미래이고, 날짜차이가 6일 이내일 때, 두 번째 자료 선택
    elif data_2_date <= tt_date and (tt_date - data_2_date).days <= 6:
        data = data_2
    else:
        return None

    tt = data["dailyTimetable"][tt_grade][tt_class]  # 일일시간표
    og_tt = data["originalTimetable"][tt_grade][tt_class]  # 원본시간표
    teacher_list = data["teachersList"]  # 교사명단
    subject_list = data["subjectsList"]  # 2글자로 축약한 과목명단

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

    # 리스트에서 0 제거
    tt[comci_weekday] = [i for i in tt[comci_weekday] if i != 0]
    og_tt[comci_weekday] = [i for i in og_tt[comci_weekday] if i != 0]

    # 단축수업, 연장수업, 시간표없음 표시
    if tt[comci_weekday] and og_tt[comci_weekday]:
        # 교시수 구하기
        tt_num = len(tt[comci_weekday])
        og_tt_num = len(og_tt[comci_weekday])

        if tt_num == og_tt_num:
            pass
        elif tt_num < og_tt_num:
            return_data.append("[MSG]⭐단축수업이 있습니다. (%s교시 → %s교시)" % (og_tt_num, tt_num))
        elif tt_num > og_tt_num:
            return_data.append("[MSG]⭐연장수업이 있습니다. (%s교시 → %s교시)" % (og_tt_num, tt_num))

        log.info("[#%s] parse@timetable_parser.py: Succeeded(%s-%s, %s)" % (
            req_id, tt_grade, tt_class, tt_date))
    else:
        return_data.append("[MSG]⭐수업을 실시하지 않습니다. (시간표 없음)")

    return return_data


# 디버그
if __name__ == "__main__":
    print(parse(3, 11, 2019, 10, 25, "****DEBUG****", True))
