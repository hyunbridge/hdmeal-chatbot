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
from bs4 import BeautifulSoup
from modules.common import conf, log

school_code = conf.configs['School']['NEIS']['Code']
school_kind = conf.configs['School']['NEIS']['Kind']
neis_baseurl = conf.configs['School']['NEIS']['BaseURL']
delicious = conf.delicious


def parse(year: int, month: int, day: int, req_id: str, debugging: bool):
    dates, menus, calories = [], [], []
    year, month, day = int(year), int(month), int(day)

    log.info("[#%s] parse@menu_parser.py: Started Parsing Menu(%s-%s-%s)" % (req_id, year, month, day))

    try:
        url = urllib.request.urlopen(neis_baseurl + "sts_sci_md01_001.do?"
                                                    "schulCode=%s"
                                                    "&schulCrseScCode=%d"
                                                    "&schulKndScCode=%02d"
                                                    "&schMmealScCode=2"
                                                    "&schYmd=%04d.%02d.%02d" % (school_code, school_kind, school_kind,
                                                                                year, month, day), timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s) because %s" % (
            req_id, year, month, day, e))
        raise ConnectionError
    data = BeautifulSoup(url, 'html.parser')
    data = data.find_all("tr")

    # 날짜 파싱
    dates_text_raw = data[0].find_all("th")
    for date_text_raw in dates_text_raw:
        date_text = date_text_raw.get_text().strip().replace(".", "-")
        if not date_text:
            continue
        dates.append(date_text)

    # 메뉴 파싱
    menus_raw = data[2].find_all("td")
    for menu_raw in menus_raw:
        meal = []
        menu = str(menu_raw).replace('<br/>', '.\n')  # 줄바꿈 처리
        menu = html.unescape(re.sub('<.+?>', '', menu).strip())  # 태그 및 HTML 엔티티 처리
        for i in menu.split('\n'):
            if i:
                allergy_re = re.findall(r'[0-9]+\.', i)
                allergy_info = [int(x[:-1]) for x in allergy_re]
                i = i[:-1].replace(''.join(allergy_re), '')
                # 맛있는 메뉴 강조표시
                for keyword in delicious:
                    if keyword in i:
                        i = "⭐" + i  # 별 덧붙이기
                        break
                meal.append([i, allergy_info])
        menus.append(meal)

    # 칼로리 파싱
    calories_raw = data[51].find_all("td")
    for calorie_raw in calories_raw:
        calorie = calorie_raw.get_text().strip()
        try:
            calorie = float(calorie)
        except ValueError:
            calorie = None
        calories.append(calorie)

    # 파일 생성
    for loc in range(len(dates)):
        try:
            if menus[loc]:
                return_data = {
                    "date": dates[loc],
                    "menu": menus[loc],
                    "kcal": calories[loc]
                }
                if debugging:
                    print(return_data)

                with open('data/cache/' + dates[loc][:10] + '.json', 'w',
                          encoding="utf-8") as make_file:
                    json.dump(return_data, make_file, ensure_ascii=False)
                    print("File Created")

                log.info("[#%s] parse@menu_parser.py: Succeeded(%s-%s-%s)" % (req_id, year, month, day))
        except IndexError:
            pass


# 디버그
if __name__ == "__main__":
    parse(2020, 11, 20, "****DEBUG****", True)
