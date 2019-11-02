# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/calendarparser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import urllib.request
from bs4 import BeautifulSoup
import json
from modules import log

# 학교코드와 학교종류를 정확히 입력
school_code = "J100005775"
school_kind = 3  # 1 유치원, 2 초등학교, 3 중학교, 4 고등학교

def parse(year, month, req_id, debugging):
    year = str(year).zfill(4)
    month = str(month).zfill(2)

    log.info("[#%s] parse@modules/calendarparser.py: 학사일정 파싱 시작(%s-%s)" % (req_id, year, month))

    try:
        url = ("http://stu.goe.go.kr/sts_sci_sf01_001.do?"
               "schulCode=%s"
               "&schulCrseScCode=%s"
               "&schulKndScCode=%s"
               "&ay=%s&mm=%s" % (school_code, school_kind, str(school_kind).zfill(2), year, month))
        req = urllib.request.urlopen(url)

    except Exception as error:
        if debugging:
            print(error)
        return error

    if debugging:
        print(url)

    data = BeautifulSoup(req, 'html.parser')
    data = data.find_all('div', class_='textL')

    calendar = dict()

    for i in range(len(data)):
        string = data[i].get_text().strip()
        if string[2:].replace('\n', ''):
            calendar[string[:2]] = string[2:].strip().replace('\n\n\n', '\n')

    if debugging:
        print(calendar)

    if calendar:
        with open('data/cache/Cal-%s-%s.json' % (year, month), 'w',
                  encoding="utf-8") as make_file:
            json.dump(calendar, make_file, ensure_ascii=False, indent="\t")
            print("File Created")

    log.info("[#%s] parse@modules/calendarparser.py: 학사일정 파싱 성공(%s-%s)" % (req_id, year, month))

    return 0

# 디버그
if __name__ == "__main__":
    parse(2019, 8, "****DEBUG****", True)
