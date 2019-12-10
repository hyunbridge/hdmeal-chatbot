# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/FB.py - 페이스북 페이지에 급식정보를 발행하는 스크립트입니다.

from datetime import datetime, timedelta
import re
from PIL import Image, ImageDraw, ImageFont
from modules import getData, log
import facebook
import io

def publish(fb_token, req_id, debugging):

    fb = "OK"
    status = 200

    tomorrow = datetime.now() + timedelta(days=1)  # 내일
    meal = getData.meal(str(tomorrow.year), str(tomorrow.month), str(tomorrow.day), req_id, debugging)  # 급식정보 불러오기

    log.info("[#%s] publish@modules/FB.py: Started Publishing" % req_id)

    # 급식데이터가 있는지 확인
    if "message" in meal:
        if meal["message"] == "등록된 데이터가 없습니다.":
            if debugging:
                print("NoData")
            log.info("[#%s] publish@modules/FB.py: No Data" % req_id)
            return {"Parser": "NoData"}, 200
        else:
            if debugging:
                print("NoData")
            log.err("[#%s] publish@modules/FB.py: Failed to Publish" % req_id)
            return {"Parser": "ERROR"}, 500
    else:
        date = meal["date"]  # 날짜 - YYYY-MM-DD(Weekday)
        menu = re.sub(r'\[[^\]]*\]', '', meal["menu"]).split('\n')  # 괄호(알레르기정보) 제거, 행별로 나누기
        kcal = meal["kcal"] + " kcal"  # 열량값에 단위(kcal)붙이기

    # 템플릿
    try:
        tmpl = Image.open('data/FB_Template.png')
        pmap_tmpl = tmpl.load()
    except FileNotFoundError:
        log.err("[#%s] publish@modules/FB.py: Failed" % req_id)
        return {"Parser": "OK", "IMG": "Missing File"}, 500
    except Exception:
        log.err("[#%s] publish@modules/FB.py: Failed" % req_id)
        return {"Parser": "OK", "IMG": "FAIL"}, 500

    # 이미지 생성
    output = Image.new(tmpl.mode, tmpl.size)
    pmap_output = output.load()

    # 템플릿의 Pixel Map을 복제
    for x in range(output.size[0]):
        for y in range(output.size[1]):
            pmap_output[x, y] = pmap_tmpl[x, y]

    # 글꼴과 크기 정의
    font_date = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 72)
    font_menu = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 64)
    font_kcal = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 56)

    # 날짜 그리기
    ImageDraw.Draw(output).text((84, 62), date, (59, 111, 217), font=font_date)

    # 메뉴 그리기
    for i in range(len(menu)):
        # 별이 있는 경우(맛있는 메뉴) 파란색으로 강조하기
        if '⭐' in menu[i]:
            ImageDraw.Draw(output).text((84, 204 + (77 * i)), menu[i].replace('⭐', ''), (59, 111, 217), font=font_menu)
        else:
            ImageDraw.Draw(output).text((84, 204 + (77 * i)), menu[i], (0, 0, 0), font=font_menu)

    # 열량 그리기
    ImageDraw.Draw(output).text((219, 923), kcal, (59, 111, 217), font=font_kcal)

    # RAM에 임시로 파일 저장
    temp = io.BytesIO()
    output.save(temp, format="png")

    # Facebook에 업로드
    if fb_token:
        try:
            graph = facebook.GraphAPI(access_token=fb_token)
            graph.put_photo(image=temp.getvalue(), message=date + " 급식")  # YYYY-MM-DD(Weekday) 급식
        except facebook.GraphAPIError as error:
            if debugging:
                print(error)
            if str(error) == "Invalid OAuth access token.":
                fb = "Invalid Token"
                status = 400
            else:
                fb = "ERR"
                status = 500
        except Exception:
            fb = "ERR"
            status = 500
    else:
        fb = "No Token"

    # OK 반환
    log.info("[#%s] publish@modules/FB.py: Succeeded" % req_id)
    return {"Parser": "OK", "IMG": "OK", "fb": fb}, status

# 디버그
if __name__ == "__main__":
    print(publish('', "****DEBUG****", True))
