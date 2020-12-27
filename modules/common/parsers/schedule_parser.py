# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# schedule_parser.py - NEIS 서버에 접속하여 학사일정을 파싱해오는 스크립트입니다.

import datetime
import json
import urllib.error
import urllib.request
from itertools import groupby
from modules.common import conf, log

# 설정 불러오기
NEIS_OPENAPI_TOKEN = conf.configs['Tokens']['NEIS']  # NEUS 오픈API 인증 토큰
ATPT_OFCDC_SC_CODE = conf.configs['School']['NEIS']['ATPT_OFCDC_SC_CODE']  # 시도교육청코드
SD_SCHUL_CODE = conf.configs['School']['NEIS']['SD_SCHUL_CODE']  # 표준학교코드


def parse(year, month, req_id, debugging):
    year, month = int(year), int(month)
    schdls = {}

    log.info("[#%s] parse@schedule_parser.py: Started Parsing Schedule(%s-%s)" % (req_id, year, month))

    date_from = datetime.date(year, month, 1)
    date_to = (date_from + datetime.timedelta(days=40)).replace(day=1) - datetime.timedelta(days=1)
    # 다음달 첫날의 날짜를 구하고 -1일 => 이번달 말일

    try:
        req = urllib.request.urlopen("https://open.neis.go.kr/hub/SchoolSchedule?KEY=%s&Type=json&ATPT_OFCDC_SC_CODE"
                                     "=%s&SD_SCHUL_CODE=%s&AA_FROM_YMD=%s&AA_TO_YMD=%s"
                                     % (NEIS_OPENAPI_TOKEN, ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE,
                                        date_from.strftime("%Y%m%d"), date_to.strftime("%Y%m%d")), timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] parse@schedule_parser.py: Failed to Parse Schedule(%s-%s) because %s" % (
            req_id, year, month, e))
        raise ConnectionError

    data = json.loads(req.read())

    schedules = []
    for i in data["SchoolSchedule"][1]["row"]:
        if i["EVENT_NM"] == "토요휴업일":
            continue

        date = datetime.datetime.strptime(i["AA_YMD"], "%Y%m%d").date()

        related_grade = []
        if i["ONE_GRADE_EVENT_YN"] == "Y": related_grade.append(1)
        if i["TW_GRADE_EVENT_YN"] == "Y": related_grade.append(2)
        if i["THREE_GRADE_EVENT_YN"] == "Y": related_grade.append(3)
        if i["FR_GRADE_EVENT_YN"] == "Y": related_grade.append(4)
        if i["FIV_GRADE_EVENT_YN"] == "Y": related_grade.append(5)
        if i["SIX_GRADE_EVENT_YN"] == "Y": related_grade.append(6)

        schedules.append([date, i["EVENT_NM"], related_grade])

        for k, v in groupby(schedules, lambda k: k[0]):
            schedule_text = ""
            for item in v:
                schedule_text = "%s%s(%s)\n" % (schedule_text, item[1], ", ".join("%s학년" % i for i in item[2]))
            schedule_text = schedule_text[:-1].replace("()", "")
            schdls[str(k.day)] = schedule_text

    if schdls:
        with open('data/cache/Cal-%s-%s.json' % (year, month), 'w',
                  encoding="utf-8") as make_file:
            json.dump(schdls, make_file, ensure_ascii=False)
            print("File Created")

    log.info("[#%s] parse@schedule_parser.py: Succeeded(%s-%s)" % (req_id, year, month))

    return 0


# 디버그
if __name__ == "__main__":
    log.init()
    parse(2019, 8, "****DEBUG****", True)
