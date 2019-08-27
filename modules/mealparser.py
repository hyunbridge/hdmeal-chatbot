# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# mealparser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import urllib.request
from bs4 import BeautifulSoup
import json
from collections import OrderedDict
import re
import html

def parse(year, month, date, isDebugging):
    year = str(year).zfill(2)
    month = str(month).zfill(2)
    date = str(date).zfill(2)

    try:
        url = urllib.request.urlopen("http://stu.goe.go.kr/sts_sci_md01_001.do?"
                                     "schulCode=J100005775"
                                     "&schulCrseScCode=3"
                                     "&schulKndScCode=03"
                                     "&schMmealScCode=2"
                                     "&schYmd=%s.%s.%s" % (year, month, date))
    except Exception as error:
        if isDebugging:
            print(error)
        return error
    data = BeautifulSoup(url, 'html.parser')
    data = data.find_all("tr")

    # 날싸 파싱
    loc = int()
    raw_date = data[0].find_all("th")
    try:
        for i in range(8):
            if year.zfill(4) + "." + month.zfill(2) + "." + date.zfill(2) in str(raw_date[i]):
                loc = i - 1
                date = raw_date[i].get_text().strip().replace(".", "-")
                if isDebugging:
                    print(loc)
                    print(date)
    except IndexError:
        return "IndexError"
    if not loc:
        return ""

    # 알레르기정보 선언
    allergy_filter = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.",
                      "9.", "10.", "11.", "12.", "13.", "14.", "15.", "16.",
                      "17.", "18."]
    allergy_string = ["[난류]", "[우유]", "[메밀]", "[땅콩]", "[대두]", "[밀]", "[고등어]", "[게]",
                      "[새우]", "[돼지고기]", "[복숭아]", "[토마토]", "[아황산류]", "[호두]", "[닭고기]", "[쇠고기]",
                      "[오징어]", "[조개류]"]
    allergy_filter.reverse()
    allergy_string.reverse()  # 역순으로 정렬 - 오류방지

    # 메뉴 파싱
    menu = data[2].find_all("td")
    try:
        menu = str(menu[loc]).replace('<br/>', '.\n')  # 줄바꿈 처리
    except IndexError:
        return "IndexError"
    menu = html.unescape(re.sub('<.+?>', '', menu).strip())  # 태그 및 HTML 엔티티 처리
    if menu == "":
        return "NoData"
    for i in range(18):
        menu = menu.replace(allergy_filter[i], allergy_string[i])
    if isDebugging:
        print(menu)

    # 칼로리 파싱
    kcal = data[45].find_all("td")
    kcal = kcal[loc].get_text().strip()
    if isDebugging:
        print(kcal)

    # 반환값 생성
    return_data = OrderedDict()
    return_data["date"] = date
    return_data["menu"] = menu
    return_data["kcal"] = kcal
    if isDebugging:
        print(return_data)

    with open('data/cache/' + date[:10] + '.json', 'w',
            encoding="utf-8") as make_file:
        json.dump(return_data, make_file, ensure_ascii=False, indent="\t")
        print("File Created")

    return 0
