# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# menu_parser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import html
import json
import re
import urllib.error
import urllib.request
from collections import OrderedDict
from bs4 import BeautifulSoup
from modules.common import conf, log

school_code = conf.configs['School']['NEIS']['Code']
school_kind = conf.configs['School']['NEIS']['Kind']
neis_baseurl = conf.configs['School']['NEIS']['BaseURL']
delicious = conf.delicious


def parse(year, month, day, req_id, debugging):
    global date
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    day = str(day).zfill(2)

    log.info("[#%s] parse@menu_parser.py: Started Parsing Menu(%s-%s-%s)" % (req_id, year, month, day))

    try:
        url = urllib.request.urlopen(neis_baseurl + "sts_sci_md01_001.do?"
                                                    "schulCode=%s"
                                                    "&schulCrseScCode=%d"
                                                    "&schulKndScCode=%02d"
                                                    "&schMmealScCode=2"
                                                    "&schYmd=%s.%s.%s" % (school_code, school_kind, school_kind,
                                                                          year, month, day), timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s) because %s" % (
            req_id, year, month, day, e))
        raise ConnectionError
    data = BeautifulSoup(url, 'html.parser')
    data = data.find_all("tr")

    # 날짜 파싱
    loc = int()
    raw_date = data[0].find_all("th")
    try:
        for i in range(8):
            if year + "." + month + "." + day in str(raw_date[i]):
                loc = i - 1
                date = raw_date[i].get_text().strip().replace(".", "-")
                if debugging:
                    print(loc)
                    print(date)
    except IndexError:
        log.err("[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "IndexError"
    if not loc:
        log.err("[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        return ""

    # 메뉴 파싱
    menus = data[2].find_all("td")
    manu_final = []
    try:
        menus = str(menus[loc]).replace('<br/>', '.\n')  # 줄바꿈 처리
    except IndexError:
        log.err("[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "IndexError"
    menus = html.unescape(re.sub('<.+?>', '', menus).strip())  # 태그 및 HTML 엔티티 처리
    if menus == "":
        log.info("[#%s] parse@menu_parser.py: No Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "NoData"
    for menu in menus.split('\n'):
        allergy_re = re.findall(r'[0-9]+\.', menu)
        allergy_info = [int(x[:-1]) for x in allergy_re]
        menu = menu[:-1].replace(''.join(allergy_re), '')
        # 맛있는 메뉴 강조표시
        for keyword in delicious:
            if keyword in menu:
                menu = "⭐" + menu  # 별 덧붙이기
                break
        manu_final.append([menu, allergy_info])
    if debugging:
        print(menus)
        print(manu_final)

    # 칼로리 파싱
    kcal = data[51].find_all("td")
    kcal = kcal[loc].get_text().strip()
    if debugging:
        print(kcal)

    # 반환값 생성
    return_data = OrderedDict()
    return_data["date"] = date
    return_data["menu"] = manu_final
    return_data["kcal"] = kcal
    if debugging:
        print(return_data)

    with open('data/cache/' + date[:10] + '.json', 'w',
              encoding="utf-8") as make_file:
        json.dump(return_data, make_file, ensure_ascii=False)
        print("File Created")

    log.info("[#%s] parse@menu_parser.py: Succeeded(%s-%s-%s)" % (req_id, year, month, day))

    return 0


# 디버그
if __name__ == "__main__":
    parse(2020, 11, 20, "****DEBUG****", True)
