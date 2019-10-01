# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/mealparser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import urllib.request
from bs4 import BeautifulSoup
import json
from collections import OrderedDict
import re
import html


def parse(year, month, date, debugging):
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
            if year.zfill(4) + "." + month.zfill(2) + "." + date.zfill(2) in str(raw_date[i]):
                loc = i - 1
                date = raw_date[i].get_text().strip().replace(".", "-")
                if debugging:
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
    if debugging:
        print(menu)

    # 맛있는 메뉴 표시
    delicious = ['까스', '꿔바로우', '도넛', '떡갈비', '떡꼬치', '떡볶이', '마요', '마카롱', '맛탕', '망고', '메론',
                 '미트볼', '바나나', '바베큐', '불고기', '브라우니', '브라운', '브리또', '비엔나', '빵', '샌드위치',
                 '샐러드', '소세지', '송편', '스파게티', '스프', '아이스', '와플', '우동', '쥬스', '짜장', '치즈',
                 '치킨', '카레', '케이크', '케익', '타코야끼', '탕수육', '튀김', '파이', '파인애플', '피자',
                 '하이라이스', '함박', '핫도그', '핫바', '햄', '햄버거', '훈제']
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

    return 0

# 디버그
if __name__ == "__main__":
    parse(2019, 9, 11, True)
