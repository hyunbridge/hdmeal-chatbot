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
        if ext == '.json':
            if debugging:
                print(filename)
            return_data = "%s\n%s" % (return_data, filename.replace(".json", ""))
    log.info("[#%s] get@modules/cache.py: Succeeded to Fetch Cache List" % req_id)
    return return_data
