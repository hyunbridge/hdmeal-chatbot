# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/mealParser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import html
import json
import re
import urllib.request
from collections import OrderedDict
from bs4 import BeautifulSoup
from modules import log, conf


school_code = conf.configs['School']['NEIS']['Code']
school_kind = conf.configs['School']['NEIS']['Kind']
neis_baseurl = conf.configs['School']['NEIS']['BaseURL']

def parse(year, month, day, req_id, debugging):
    global date
    year = str(year).zfill(4)
    month = str(month).zfill(2)
    day = str(day).zfill(2)

    log.info("[#%s] parse@modules/mealParser.py: Started Parsing Menu(%s-%s-%s)" % (req_id, year, month, day))

    try:
        url = urllib.request.urlopen(neis_baseurl+"sts_sci_md01_001.do?"
                                     "schulCode=%s"
                                     "&schulCrseScCode=%d"
                                     "&schulKndScCode=%02d"
                                     "&schMmealScCode=2"
                                     "&schYmd=%s.%s.%s" % (school_code, school_kind, school_kind,
                                                           year, month, day))
    except Exception as error:
        log.err("[#%s] parse@modules/mealParser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        if debugging:
            print(error)
        return error
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
        log.err("[#%s] parse@modules/mealParser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "IndexError"
    if not loc:
        log.err("[#%s] parse@modules/mealParser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
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
        log.err("[#%s] parse@modules/mealParser.py: Failed to Parse Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "IndexError"
    menu = html.unescape(re.sub('<.+?>', '', menu).strip())  # 태그 및 HTML 엔티티 처리
    if menu == "":
        log.info("[#%s] parse@modules/mealParser.py: No Menu(%s-%s-%s)" % (req_id, year, month, day))
        return "NoData"
    for i in range(18):
        menu = menu.replace(allergy_filter[i], allergy_string[i]).replace('.\n', ',\n')  # 알러지 처리 및 콤마 찍기
    if debugging:
        print(menu)

    # 맛있는 메뉴 표시
    delicious = ['까스', '깐풍기', '꼬치', '꿀떡', '꿔바로우', '도넛', '떡갈비', '떡꼬치', '떡볶이', '마요', '마카롱',
                 '맛탕', '망고', '메론', '미트볼', '바나나', '바베큐', '부대찌개', '불고기', '브라우니', '브라운',
                 '브리또', '비엔나', '빵', '샌드위치', '샐러드', '샤브샤브', '소세지', '송편', '스파게티', '스프',
                 '아이스', '와플', '우동', '인절미', '제육', '쥬스', '짜장', '쫄면', '차슈', '초코', '치즈', '치킨',
                 '카레', '케이크', '케익', '쿠키', '쿨피스', '타코야끼', '탕수육', '토스트', '튀김', '파이', '파인애플',
                 '피자', '하이라이스', '함박', '핫도그', '핫바', '햄', '햄버거', '훈제']

    split = menu.split("\n")  # 메뉴 라인별로 나누기
    meal = str()
    global line
    for line in split:  # 라인별로 반복작업
        for keyword in delicious:
            if keyword in line:
                line = "⭐" + line  # 별 덧붙이기
                break
        meal = "%s\n%s" % (meal, line)  # meal에 추가
    meal = meal[1:]  # 맨 처음 줄바꿈 제거

    # 칼로리 파싱
    kcal = data[45].find_all("td")
    kcal = kcal[loc].get_text().strip()
    if debugging:
        print(kcal)

    # 반환값 생성
    return_data = OrderedDict()
    return_data["date"] = date
    return_data["menu"] = meal
    return_data["kcal"] = kcal
    if debugging:
        print(return_data)

    with open('data/cache/' + date[:10] + '.json', 'w',
              encoding="utf-8") as make_file:
        json.dump(return_data, make_file, ensure_ascii=False, indent="\t")
        print("File Created")

    log.info("[#%s] parse@modules/mealParser.py: Succeeded(%s-%s-%s)" % (req_id, year, month, day))

    return 0

# 디버그
if __name__ == "__main__":
    parse(2019, 9, 11, "****DEBUG****", True)
