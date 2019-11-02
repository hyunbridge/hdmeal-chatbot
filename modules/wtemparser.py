# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/wtemparser.py - 실시간수질정보시스템 서버에 접속하여 수온정보를 파싱해오는 스크립트입니다.

import urllib.request
from bs4 import BeautifulSoup
from modules import log

def get(req_id, debugging):
    log.info("[#%s] get@modules/wtemparser.py: 수온 파싱 시작" % req_id)
    try:
        url = urllib.request.urlopen("http://koreawqi.go.kr/wQSCHomeLayout_D.wq?action_type=T")
    except Exception as error:
        if debugging:
            print(error)
        log.err("[#%s] get@modules/wtemparser.py: 수온 파싱 실패" % req_id)
        return error
    data = BeautifulSoup(url, 'html.parser')
    # 측정일시 파싱
    date = data.find('span', class_='data').get_text().split('"')[1]
    time = int(data.find('span', class_='data').get_text().split('"')[3])
    date = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
    # 24시간제 -> 12시간제 변환
    if time == 0 or time == 24:  # 자정
        time = "오전 12시"
    elif time < 12:  # 오전
        time = "오전 %s시" % (time)
    elif time == 12:  # 정오
        time = "오후 12시"
    else:  # 오후
        time = "오후 %s시" % (time - 12)
    # 수온 파싱
    wtemp = data.find('tr', class_='site_S01004').get_text()  # 구리측정소 사용
    wtemp = wtemp.replace("구리", "").strip()
    # List 만들기
    return_data = list()
    return_data.append(date)
    return_data.append(time)
    return_data.append(wtemp)
    log.info("[#%s] get@modules/wtemparser.py: 수온 파싱 성공" % req_id)
    return return_data
