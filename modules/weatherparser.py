# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/weatherparser.py - 컴시간 서버에 접속하여 시간표정보를 파싱해오는 스크립트입니다.

import urllib.request
import xml.etree.ElementTree

# 지역코드를 정확히 입력
region = "4146351500"

def parse(debugging):

    try:
        url = urllib.request.urlopen("https://www.kma.go.kr/wid/queryDFSRSS.jsp"
                                     "?zone=%s" % region)
    except Exception as error:
        if debugging:
            print(error)
        return error

    data = xml.etree.ElementTree.fromstring(url.read().decode('utf-8')).findall('.//data')

    weather = dict()
    loc = int()
    for i in range(7):
        if data[i].find('hour').text == '9':  # 9시 찾기
            if not i == 7:  # 다음날 9시가 아닐 경우
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
                loc = i
                break

    if not weather:  # 날씨데이터 없을 경우(다음날 9시로 밀린 경우) 그 다음 데이터를 취함
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

    # 하늘 상태, 강수 형태 대응값
    sky = ['☀ 맑음', '🌤️ 구름 조금', '🌥️ 구름 많음', '☁ 흐림']
    pty = ['❌ 없음', '🌧️ 비', '🌤️ 구름 조금', '🌥️ 구름 많음']

    # 하늘 상태 대응값 적용
    if int(weather['sky']) <= 4:
        weather['sky'] = sky[int(weather['sky'])-1]  # 1부터 시작
    else:
        weather['sky'] = '⚠ 오류'

    # 강수 형태 대응값 적용
    if int(weather['pty']) < 4:
        weather['pty'] = pty[int(weather['pty'])]
    else:
        weather['pty'] = '⚠ 오류'

    return weather

# 디버그
if __name__ == "__main__":
    print(parse(True))
