# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/cache.py - 캐시를 관리하는 스크립트입니다.

import os
from collections import OrderedDict
from modules import log
import datetime
import json

# 캐시 비우기
def purge(req_id, debugging):
    dict_data = OrderedDict()
    try:
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)
    except Exception as error:
        log.err("[#%s] purge@modules/cache.py: Failed to Purge Cache" % req_id)
        if debugging:
            dict_data["status"] = error
        dict_data["status"] = "Error"
        return dict_data
    dict_data["status"] = "OK"
    log.info("[#%s] purge@modules/cache.py: Succeeded to Purge Cache" % req_id)
    return dict_data


# 캐시정보 가져오기
def get(req_id, debugging):
    filenames = os.listdir('data/cache/')
    return_data = str()
    for filename in filenames:
        ext = os.path.splitext(filename)[-1]
        if ext == '.json' and filename != "TT.json" and filename != "wtemp.json":  # 시간표와 수온 캐시 파일 숨김
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
    log.info("[#%s] get@modules/cache.py: Succeeded to Fetch Cache List" % req_id)
    return return_data
