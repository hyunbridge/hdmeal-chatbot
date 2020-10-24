# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# weather_parser.py - 날씨정보를 파싱해오는 스크립트입니다.

import urllib.error
import urllib.request
import xml.etree.ElementTree
from modules.common import conf, log

region = conf.configs['School']['KMAZone']


def parse(req_id, debugging):

    log.info("[#%s] parse@weather_parser.py: Started Parsing Weather" % req_id)

    try:
        url = urllib.request.urlopen("https://www.kma.go.kr/wid/queryDFSRSS.jsp"
                                     "?zone=%s" % region, timeout=2)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        log.err("[#%s] parse@weather_parser.py: Failed to Parse Weather because %s" % (req_id, e))
        raise ConnectionError
    except Exception as error:
        if debugging:
            print(error)
        log.err("[#%s] parse@weather_parser.py: Failed" % req_id)
        return error

    data = xml.etree.ElementTree.fromstring(url.read().decode('utf-8')).findall('.//data')

    weather = dict()
    for i in range(6):
        if data[i].find('hour').text == '9':  # 9시 찾기
            # 위치
            weather['loc'] = i
            # 시간
            weather['hour'] = data[i].find('hour').text
            # 기온/최대 기온/최소 기온
            weather['temp'] = data[i].find('temp').text
            weather['temp_max'] = data[i].find('tmx').text
            weather['temp_min'] = data[i].find('tmn').text
            # 하늘 상태 -  1: 맑음 2: 구름조금 3: 구름많음 4: 흐림
            weather['sky'] = data[i].find('sky').text
            # 강수 형태 - 0: 없음 1: 비 2: 비&눈 3: 눈
            weather['pty'] = data[i].find('pty').text
            # 강수 확률
            weather['pop'] = data[i].find('pop').text
            # 습도
            weather['reh'] = data[i].find('reh').text
            break

    if not weather:  # 날씨데이터 없을 경우(다음날 9시로 밀린 경우) 그 다음 데이터를 취함
        # 위치
        weather['loc'] = 0
        # 시간
        weather['hour'] = data[0].find('hour').text
        # 기온/최대 기온/최소 기온
        weather['temp'] = data[0].find('temp').text
        weather['temp_max'] = data[0].find('tmx').text
        weather['temp_min'] = data[0].find('tmn').text
        # 하늘 상태 -  1: 맑음 2: 구름조금 3: 구름많음 4: 흐림
        weather['sky'] = data[0].find('sky').text
        # 강수 형태 - 0: 없음 1: 비 2: 비&눈 3: 눈
        weather['pty'] = data[0].find('pty').text
        # 강수 확률
        weather['pop'] = data[0].find('pop').text
        # 습도
        weather['reh'] = data[0].find('reh').text

    weather['1st_hour'] = data[0].find('hour').text

    if weather['1st_hour'] == "24":
        weather['1st_hour'] = "0"

    # 하늘 상태, 강수 형태 대응값
    sky = ['☀ 맑음', '🌤️ 구름 조금', '🌥️ 구름 많음', '☁ 흐림']
    pty = ['❌ 없음', '🌧️ 비', '🌤️ 구름 조금', '🌥️ 구름 많음']

    # 하늘 상태 대응값 적용
    if int(weather['sky']) <= 4:
        weather['sky'] = sky[int(weather['sky'])-1]  # 1부터 시작
    else:
        weather['sky'] = '⚠ 오류'
        log.err("[#%s] parse@weather_parser.py: Failed to Parse Sky" % req_id)

    # 강수 형태 대응값 적용
    if int(weather['pty']) < 4:
        weather['pty'] = pty[int(weather['pty'])]
    else:
        weather['pty'] = '⚠ 오류'
        log.err("[#%s] parse@weather_parser.py: Failed to Parse Precipitation Type" % req_id)
    log.info("[#%s] parse@weather_parser.py: Succeeded" % req_id)
    return weather

# 디버그
if __name__ == "__main__":
    print(parse("****DEBUG****", True))
