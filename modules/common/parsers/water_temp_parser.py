# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# water_temp_parser.py - 실시간수질정보시스템 서버에 접속하여 수온정보를 파싱해오는 스크립트입니다.

import datetime
import os
import urllib.error
import urllib.request

from modules.common import log

api_key = os.environ.get("HDMeal-SeoulData-Token")


def get(req_id, debugging):
    log.info(
        "[#%s] get@water_temp_parser.py: Started Parsing Water Temperature" % req_id
    )
    try:
        url = urllib.request.urlopen(
            f"http://openapi.seoul.go.kr:8088/{api_key}/json/WPOSInformationTime/1/5/",
            timeout=2,
        )
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err(
            "[#%s] get@water_temp_parser.py: Failed to Parse Water Temperature because %s"
            % (req_id, e)
        )
        raise ConnectionError
    import json

    res = json.load(url)
    data = res["WPOSInformationTime"]["row"]

    # 측정일시 파싱
    measurement_date = datetime.datetime.strptime(
        f'{data[0]["MSR_DATE"]} {data[0]["MSR_TIME"]}', "%Y%m%d %H:%M"
    )
    # 수온 파싱
    measurements = []
    for i in data:
        temp = i["W_TEMP"]
        try:
            measurements.append(float(temp))
        except ValueError:
            pass
    log.info("[#%s] get@water_temp_parser.py: Succeeded" % req_id)
    return measurement_date, str(sum(measurements) / len(measurements))
