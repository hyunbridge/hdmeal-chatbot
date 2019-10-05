# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/fb.py - 페이스북 페이지에 급식정보를 발행하는 스크립트입니다.

from datetime import datetime, timedelta
import re
from PIL import Image, ImageDraw, ImageFont
from modules import getdata
import facebook
import io

def publish(key, debugging):
    tomorrow = datetime.now() + timedelta(days=1)
    meal = getdata.meal(str(tomorrow.year), str(tomorrow.month), str(tomorrow.day), debugging)
    if "message" in meal:
        if debugging:
            print("NoData")
        return {"Status": "NoData"}
    else:
        date = meal["date"]
        menu = re.sub(r'\[[^\]]*\]', '', meal["menu"]).split('\n')
        kcal = meal["kcal"] + " kcal"

    img = Image.open('data/FB_Template.png')
    pmap = img.load()

    output = Image.new(img.mode, img.size)
    pmap_new = output.load()
    for x in range(output.size[0]):
        for y in range(output.size[1]):
            pmap_new[x, y] = pmap[x, y]

    font_date = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 72)
    font_menu = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 64)
    font_kcal = ImageFont.truetype('data/NotoSansCJKkr-Bold.otf', 56)

    print(font_kcal.getsize("열량: ")[0])

    ImageDraw.Draw(output).text((84, 62), date, (59, 111, 217), font=font_date)
    for i in range(len(menu)):
        if '⭐' in menu[i]:
            ImageDraw.Draw(output).text((84, 204 + (77 * i)), menu[i].replace('⭐', ''), (59, 111, 217), font=font_menu)
        else:
            ImageDraw.Draw(output).text((84, 204 + (77 * i)), menu[i], (0, 0, 0), font=font_menu)
        ImageDraw.Draw(output).text((219, 923), kcal, (59, 111, 217), font=font_kcal)

    temp = io.BytesIO()
    output.save(temp, format="png")
    graph = facebook.GraphAPI(access_token=key)
    graph.put_photo(image=temp.getvalue(), message=date + " 급식")
    return {"Status": "OK"}

# 디버그
if __name__ == "__main__":
    publish('', True)
