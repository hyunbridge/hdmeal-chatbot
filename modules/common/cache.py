# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# cache.py - 캐시를 관리하는 스크립트입니다.

import datetime
import json
import os
from collections import OrderedDict
from threading import Thread
from modules.chatbot import get_data
from modules.common import log
from modules.common.parsers import timetable_parser


# 캐시 비우기
def purge(req_id, debugging):
    dict_data = OrderedDict()
    try:
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)
    except Exception as error:
        log.err("[#%s] purge@cache.py: Failed" % req_id)
        if debugging:
            dict_data["status"] = error
        dict_data["status"] = "Error"
        return dict_data
    dict_data["status"] = "OK"
    log.info("[#%s] purge@cache.py: Succeeded" % req_id)
    return dict_data


# 캐시정보 가져오기
def get(req_id, debugging):
    filenames = os.listdir('data/cache/')
    return_data = str()
    for filename in filenames:
        ext = os.path.splitext(filename)[-1]
        # 시간표와 수온, 날씨 캐시 파일 숨김
        if ext == '.json' and filename != "TT.json" and filename != "wtemp.json" and filename != "weather.json":
            if debugging:
                print(filename)
            return_data = "%s\n%s" % (return_data, filename.replace(".json", ""))
    # 시간표 캐시 만료기한 조회
    if "TT.json" in filenames:
        with open('data/cache/TT.json', encoding="utf-8") as data:  # 캐시 읽기
            timestamp = datetime.datetime.fromtimestamp(json.load(data)["Timestamp"])
            if (datetime.datetime.now() - timestamp) < datetime.timedelta(hours=3):  # 캐시 만료됐는지 확인
                time_left = int((datetime.timedelta(hours=3) - (datetime.datetime.now() - timestamp)).seconds / 60)
                return_data = "%s\n시간표 캐시 만료까지 %s분 남음" % (return_data, time_left)
            else:
                return_data = "%s\n시간표 캐시 만료됨" % return_data
    # 한강 수온 캐시 만료기한 조회
    if "wtemp.json" in filenames:
        with open('data/cache/wtemp.json', encoding="utf-8") as data:  # 캐시 읽기
            timestamp = datetime.datetime.fromtimestamp(json.load(data)["timestamp"])
            if (datetime.datetime.now() - timestamp) < datetime.timedelta(minutes=76):  # 캐시 만료됐는지 확인
                time_left = int((datetime.timedelta(minutes=76) - (datetime.datetime.now() - timestamp)).seconds / 60)
                return_data = "%s\n한강 수온 캐시 만료까지 %s분 남음" % (return_data, time_left)
            else:
                return_data = "%s\n한강 수온 캐시 만료됨" % return_data
    # 날씨 캐시 만료기한 조회
    if "weather.json" in filenames:
        with open('data/cache/weather.json', encoding="utf-8") as data:  # 캐시 읽기
            timestamp = datetime.datetime.fromtimestamp(json.load(data)["Timestamp"])
            if (datetime.datetime.now() - timestamp) < datetime.timedelta(hours=1):  # 캐시 만료됐는지 확인
                time_left = int((datetime.timedelta(hours=1) - (datetime.datetime.now() - timestamp)).seconds / 60)
                return_data = "%s\n날씨 캐시 만료까지 %s분 남음" % (return_data, time_left)
            else:
                return_data = "%s\n날씨 캐시 만료됨" % return_data
    log.info("[#%s] get@cache.py: Succeeded" % req_id)
    return return_data


def health_check(req_id, debugging):
    global status_tt, status_wtemp, status_weather
    filenames = os.listdir('data/cache/')
    now = datetime.datetime.now()

    # 시간표 캐시 만료기한 조회
    def check_tt():
        global status_tt
        if "TT.json" in filenames:
            with open('data/cache/TT.json', encoding="utf-8") as data:  # 캐시 읽기
                timestamp = datetime.datetime.fromtimestamp(json.load(data)["Timestamp"])
                if (datetime.datetime.now() - timestamp) < datetime.timedelta(hours=3):  # 캐시 만료됐는지 확인
                    time_left = int((datetime.timedelta(hours=3) - (datetime.datetime.now() - timestamp)).seconds / 60)
                    status_tt = "Vaild (Up to %s Min(s))" % time_left
                else:
                    try:
                        timetable_parser.parse(1, 1, now.year, now.month, now.day, req_id, debugging)
                        status_tt = "Expired (Regenerated)"
                    except Exception as e:
                        log.err(
                            "[#%s] health_check@cache.py: Failed to Regenerate Cache(Timetable) because %s" %
                            (req_id, e))
                        status_tt = "Expired (Failed)"
        else:
            try:
                timetable_parser.parse(1, 1, now.year, now.month, now.day, req_id, debugging)
                status_tt = "NotFound (Regenerated)"
            except Exception as e:
                log.err("[#%s] health_check@cache.py: Failed to Regenerate Cache(Timetable) because %s" %
                        (req_id, e))
                status_tt = "NotFound (Failed)"

    # 한강 수온 캐시 만료기한 조회
    def check_wtemp():
        global status_wtemp
        if "wtemp.json" in filenames:
            with open('data/cache/wtemp.json', encoding="utf-8") as data:  # 캐시 읽기
                timestamp = datetime.datetime.fromtimestamp(json.load(data)["timestamp"])
                if (datetime.datetime.now() - timestamp) < datetime.timedelta(minutes=76):  # 캐시 만료됐는지 확인
                    time_left = int(
                        (datetime.timedelta(minutes=76) - (datetime.datetime.now() - timestamp)).seconds / 60)
                    status_wtemp = "Vaild (Up to %s Min(s))" % time_left
                else:
                    try:
                        get_data.wtemp(req_id, debugging)
                        status_wtemp = "Expired (Regenerated)"
                    except Exception as e:
                        log.err(
                            "[#%s] health_check@cache.py: Failed to Regenerate Cache(WTemp) because %s" %
                            (req_id, e))
                        status_wtemp = "Expired (Failed)"
        else:
            try:
                get_data.wtemp(req_id, debugging)
                status_wtemp = "NotFound (Regenerated)"
            except Exception as e:
                log.err(
                    "[#%s] health_check@cache.py: Failed to Regenerate Cache(WTemp) because %s" %
                    (req_id, e))
                status_wtemp = "NotFound (Failed)"

    # 날씨 캐시 만료기한 조회
    def check_weather():
        global status_weather
        if "weather.json" in filenames:
            with open('data/cache/weather.json', encoding="utf-8") as data:  # 캐시 읽기
                timestamp = datetime.datetime.fromtimestamp(json.load(data)["Timestamp"])
                if (datetime.datetime.now() - timestamp) < datetime.timedelta(hours=1):  # 캐시 만료됐는지 확인
                    time_left = int((datetime.timedelta(hours=1) - (datetime.datetime.now() - timestamp)).seconds / 60)
                    status_weather = "Vaild (Up to %s Min(s))" % time_left
                else:
                    try:
                        get_data.weather(None, req_id, debugging)
                        status_weather = "Expired (Regenerated)"
                    except Exception as e:
                        log.err(
                            "[#%s] health_check@cache.py: Failed to Regenerate Cache(Weather) because %s" %
                            (req_id, e))
                        status_weather = "Expired (Failed)"
        else:
            try:
                get_data.weather(None, req_id, debugging)
                status_weather = "NotFound (Regenerated)"
            except Exception as e:
                log.err(
                    "[#%s] health_check@cache.py: Failed to Regenerate Cache(Weather) because %s" %
                    (req_id, e))
                status_weather = "NotFound (Failed)"

    # 쓰레드 정의
    th_tt = Thread(target=check_tt)
    th_wtemp = Thread(target=check_wtemp)
    th_weather = Thread(target=check_weather)
    # 쓰레드 실행
    th_tt.start()
    th_wtemp.start()
    th_weather.start()
    # 전 쓰레드 종료 시까지 기다리기
    th_tt.join()
    th_wtemp.join()
    th_weather.join()

    return {"Timetable": status_tt, "HanRiverTemperature": status_wtemp, "Weather": status_weather}
