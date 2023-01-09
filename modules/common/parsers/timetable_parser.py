# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# timetable_parser.py - 컴시간 서버에 접속하여 시간표정보를 파싱해오는 스크립트입니다.

import datetime
import json
import os
import urllib.error
import urllib.request
from itertools import groupby

from modules.common import log

# 설정 불러오기
NEIS_OPENAPI_TOKEN = os.environ.get("HDMeal-NEIS-Token")  # NEUS 오픈API 인증 토큰
ATPT_OFCDC_SC_CODE = os.environ.get("HDMeal-NEIS-ATPT_OFCDC_SC_CODE")  # 시도교육청코드
SD_SCHUL_CODE = os.environ.get("HDMeal-NEIS-SD_SCHUL_CODE")  # 표준학교코드

timetable = {}


def parse(tt_grade, tt_class, year, month, date, req_id, debugging):
    global timetable
    timetable_raw_data = []
    tt_date = datetime.date(year, month, date)
    tt_grade = str(tt_grade)
    tt_class = str(tt_class)
    date_string = tt_date.strftime("%Y-%m-%d")
    filename = "data/cache/TT-%s.json" % date_string

    log.info(
        "[#%s] parse@timetable_parser.py: Started Parsing Timetable(%s-%s, %s)"
        % (req_id, tt_grade, tt_class, tt_date)
    )

    if tt_date.weekday() > 4:
        return None

    # 데이터 가져오기
    def fetch():
        global timetable
        req = urllib.request.urlopen(
            "https://open.neis.go.kr/hub/hisTimetable?KEY=%s&Type=json&pSize=1000"
            "&ATPT_OFCDC_SC_CODE=%s&SD_SCHUL_CODE=%s&ALL_TI_YMD=%s"
            % (
                NEIS_OPENAPI_TOKEN,
                ATPT_OFCDC_SC_CODE,
                SD_SCHUL_CODE,
                tt_date.strftime("%Y%m%d"),
            ),
            timeout=2,
        )
        data = json.loads(req.read())
        print(data)

        try:
            for i in data["hisTimetable"][1]["row"]:

                timetable_raw_data.append([i["GRADE"], i["CLASS_NM"], i["ITRT_CNTNT"]])
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            log.err(
                "[#%s] fetch.parse@timetable_parser.py: Failed to Parse Timetable(%s-%s, %s) because %s"
                % (req_id, tt_grade, tt_class, tt_date, e)
            )
            raise ConnectionError

        print(timetable_raw_data)

        for grade, x in groupby(timetable_raw_data, lambda i: i[0]):
            timetable[grade] = {}
            for class_, y in groupby(x, lambda i: i[1]):
                timetable[grade][class_] = [i[2] for i in y if i[2] != "토요휴업일"]

        if timetable:
            with open(filename, "w", encoding="utf-8") as make_file:
                json.dump(timetable, make_file, ensure_ascii=False)
                print("File Created")

    if os.path.isfile(filename):  # 캐시 있으면
        try:
            log.info("[#%s] parse@timetable_parser.py: Read Data in Cache" % req_id)
            with open(filename, encoding="utf-8") as data_file:  # 캐시 읽기
                timetable = json.load(data_file)
        except Exception:  # 캐시 읽을 수 없으면
            try:
                # 캐시 삭제
                os.remove("data/cache/TT.json")
            except Exception as error:
                log.err(
                    "[#%s] parse@timetable_parser.py: Failed to Delete Cache" % req_id
                )
                return error
            fetch()  # 파싱
    else:  # 캐시 없으면
        log.info("[#%s] parse@timetable_parser.py: No Cache" % req_id)
        fetch()  # 파싱

    log.info(
        "[#%s] parse@timetable_parser.py: Succeeded(%s-%s, %s)"
        % (req_id, tt_grade, tt_class, tt_date)
    )

    return timetable[tt_grade][tt_class]


# 디버그
if __name__ == "__main__":
    print(parse(3, 11, 2019, 10, 25, "****DEBUG****", True))
