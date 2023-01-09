# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# menu_parser.py - NEIS 서버에 접속하여 급식정보를 파싱해오는 스크립트입니다.

import datetime
import json
import os
import re
import urllib.error
import urllib.request

from modules.common import conf, log

NEIS_OPENAPI_TOKEN = os.environ.get("HDMeal-NEIS-Token")  # NEUS 오픈API 인증 토큰
ATPT_OFCDC_SC_CODE = os.environ.get("HDMeal-NEIS-ATPT_OFCDC_SC_CODE")  # 시도교육청코드
SD_SCHUL_CODE = os.environ.get("HDMeal-NEIS-SD_SCHUL_CODE")  # 표준학교코드
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
DELICIOUS = conf.delicious


def parse(year: int, month: int, day: int, req_id: str, debugging: bool):
    year, month, day = int(year), int(month), int(day)

    log.info(
        "[#%s] parse@menu_parser.py: Started Parsing Menu(%s-%s-%s)"
        % (req_id, year, month, day)
    )

    try:
        req = urllib.request.urlopen(
            "https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=%s&Type=json&ATPT_OFCDC_SC_CODE"
            "=%s&SD_SCHUL_CODE=%s&MMEAL_SC_CODE=2&MLSV_YMD=%02d%02d%02d"
            % (NEIS_OPENAPI_TOKEN, ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE, year, month, day),
            timeout=2,
        )
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err(
            "[#%s] parse@menu_parser.py: Failed to Parse Menu(%s-%s-%s) because %s"
            % (req_id, year, month, day, e)
        )
        raise ConnectionError

    data = json.loads(req.read())

    try:
        for item in data["mealServiceDietInfo"][1]["row"]:
            meal = []
            date = datetime.datetime.strptime(item["MLSV_YMD"], "%Y%m%d").date()

            # 메뉴 파싱
            menu = item["DDISH_NM"].replace("<br/>", ".\n")  # 줄바꿈 처리
            menu = menu.split("\n")  # 한 줄씩 자르기
            for i in menu:
                allergy_info = [int(x[:-1]) for x in re.findall(r"[0-9]+\.", i)]
                i = i.replace(f'{".".join(str(x) for x in allergy_info)}.', "").replace(
                    "()", ""
                )
                i = re.sub(r"[ #&*-.=@_]+$", "", i)
                # 맛있는 메뉴 강조표시
                for keyword in DELICIOUS:
                    if keyword in i:
                        i = "⭐" + i  # 별 덧붙이기
                        break
                meal.append([i, allergy_info])

            # 파일 쓰기
            return_data = {
                "date": "%s(%s)"
                % (date.strftime("%Y-%m-%d"), WEEKDAYS[date.weekday()]),
                "menu": meal,
                "kcal": float(item["CAL_INFO"].replace(" Kcal", "")),
            }
            if debugging:
                print(return_data)

            with open(
                "data/cache/" + date.strftime("%Y-%m-%d") + ".json",
                "w",
                encoding="utf-8",
            ) as make_file:
                json.dump(return_data, make_file, ensure_ascii=False)
                print("File Created")

            log.info(
                "[#%s] parse@menu_parser.py: Succeeded(%s)"
                % (req_id, date.strftime("%Y-%m-%d"))
            )
    except KeyError:
        pass


# 디버그
if __name__ == "__main__":
    parse(2020, 11, 20, "****DEBUG****", True)
