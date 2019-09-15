# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# cache.py - 캐시를 관리하는 스크립트입니다.

import os
from collections import OrderedDict


# 캐시 비우기
def purge(debugging):
    dict_data = OrderedDict()
    try:
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)
    except Exception as error:
        if debugging:
            dict_data["status"] = error
        dict_data["status"] = "Error"
        return dict_data
    dict_data["status"] = "OK"
    return dict_data


# 캐시정보 가져오기
def get(debugging):
    filenames = os.listdir('data/cache/')
    return_data = str()
    for filename in filenames:
        ext = os.path.splitext(filename)[-1]
        if ext == '.json':
            if debugging:
                print(filename)
            return_data = "%s\n%s" % (return_data, filename.replace(".json", ""))
    return return_data
