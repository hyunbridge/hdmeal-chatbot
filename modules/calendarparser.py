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
from collections import OrderedDict
import re
import html


def parse(year, month, debugging):
    year = str(year).zfill(4)
    month = str(month).zfill(2)

    try:
        url = ("http://stu.goe.go.kr/sts_sci_sf01_001.do?"
               "schulCode=J100005775"
               "&schulCrseScCode=3"
               "&schulKndScCode=03"
               "&ay=%s&mm=%s" % (year, month))
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

    return 0

# 디버그
if __name__ == "__main__":
    parse(2019, 8, True)
