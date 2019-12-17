# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/WTempParser.py - 실시간수질정보시스템 서버에 접속하여 수온정보를 파싱해오는 스크립트입니다.

import datetime
import urllib.request
from bs4 import BeautifulSoup
from modules import log


def get(req_id, debugging):
    log.info("[#%s] get@modules/WTempParser.py: Started Parsing Water Temperature" % req_id)
    try:
        url = urllib.request.urlopen("http://koreawqi.go.kr/wQSCHomeLayout_D.wq?action_type=T")
    except Exception as error:
        if debugging:
            print(error)
        log.err("[#%s] get@modules/WTempParser.py: Failed" % req_id)
        return error
    data = BeautifulSoup(url, 'html.parser')
    # 측정일시 파싱
    date = data.find('span', class_='data').get_text().split('"')[1]
    date = int(date[0:4]), int(date[4:6]), int(date[6:8])
    time = int(data.find('span', class_='data').get_text().split('"')[3])
    measurement_date = datetime.datetime(date[0], date[1], date[2], time)
    # 수온 파싱
    wtemp = data.find('tr', class_='site_S01004').get_text()  # 구리측정소 사용
    wtemp = wtemp.replace("구리", "").strip()
    log.info("[#%s] get@modules/WTempParser.py: Succeeded" % req_id)
    return measurement_date, wtemp
