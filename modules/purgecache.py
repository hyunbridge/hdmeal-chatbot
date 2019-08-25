# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# purgecache.py - 캐시를 비우는 스크립트입니다.

import os
from collections import OrderedDict

def purge(isDebugging):
    dict_data = OrderedDict()
    try:
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)
    except Exception as error:
        if isDebugging:
            dict_data["status"] = error
        dict_data["status"] = "Error"
        return dict_data
    dict_data["status"] = "OK"
    return dict_data
