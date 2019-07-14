from flask import Flask
import os
import datetime
from pytz import timezone
import urllib.request
from bs4 import BeautifulSoup
import json
from collections import OrderedDict
from flask_restful import reqparse, Api, Resource

# 디버그용
isDebugging = False
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# Flask 인스턴스 생성
app = Flask(__name__)
api = Api(app)


# 파서
def parse(year, month):
    year = year
    month = month

    try:
        url = urllib.request.urlopen(
            "https://www.heungdeok.ms.kr/segio/meal_v2/meal_month.php?year=" + year + "&month=" + month)
    except Exception as error:
        if isDebugging:
            print(error)
        return error
    data = BeautifulSoup(url, 'html.parser')

    # 메뉴 파싱
    raw_meal = data.find_all("div", {"class": "meal_cont"})
    raw_meal = data.find_all("a")
    if isDebugging:
        print(raw_meal)

    meal = list()
    for i in raw_meal:
        if i.get_text() != "":
            meal.append(i.get_text().strip())
    if isDebugging:
        print(meal)

    # 날짜 파싱
    date = list()
    for i in raw_meal:
        if i.get_text() != "":
            date.append(int(i.get("name").split(",")[2]))
    if isDebugging:
        print(date)

    # JSON 생성
    if len(date) == 0 or len(meal) == 0:
        if isDebugging:
            print("NoData")
        return("NoData")

    json_data = OrderedDict()
    for i in range(len(date)):
        json_data[date[i]] = meal[i]
    if isDebugging:
        print(json_data)

    # 파일 생성
    with open('data/' + year.zfill(4) + '.' + month.zfill(2) + '.json', 'w', encoding="utf-8") as make_file:
        json.dump(json_data, make_file, ensure_ascii=False, indent="\t")
        if isDebugging:
            print("File Created")

    # 파일 체크
    with open('data/' + year.zfill(4) + '.' + month.zfill(2) + '.json', 'r', encoding="utf-8") as file:
        if isDebugging:
            print(file.read())

    return 0


# 데이터 가져오기
def meal_data(year, month, date):
    # 자료형 변환
    year = str(year)
    month = str(month)
    date = str(date)

    if not os.path.isfile('data/' + str(year).zfill(4) + '.' + str(month).zfill(2) + '.json'):
        parse(year, month)

    dict_data = OrderedDict()
    dict_data["year"] = year
    dict_data["month"] = month
    dict_data["date"] = date

    try:
        with open('data/' + year.zfill(4) + '.' + month.zfill(2) + '.json', encoding="utf-8") as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

            if date in data:
                dict_data["menu"] = data[date]
                if isDebugging:
                    print(data[date])
            else:
                dict_data["menu"] = "급식을 실시하지 않습니다."
                if isDebugging:
                    print("KeyNotFound")
    except FileNotFoundError:  # 파일 없을때
        if isDebugging:
            print("FileNotFound")
        dict_data["menu"] = "해당월 데이터가 등록되어있지 않습니다."
    except Exception as error:
        if isDebugging:
            print("Error :" + str(type(error)) + str(error))
            dict_data["menu"] = "Error :" + str(type(error)) + str(error)
        else:
            dict_data["menu"] = "Error"
    return dict_data


# 오늘
class Today(Resource):
    def get(self):
        if isDebugging:
            year = today_year
            month = today_month
            date = today_date
        else:
            year = list(timezone('Asia/Seoul').localize(datetime.datetime.now()).timetuple())[0]
            month = list(timezone('Asia/Seoul').localize(datetime.datetime.now()).timetuple())[1]
            date = list(timezone('Asia/Seoul').localize(datetime.datetime.now()).timetuple())[2]
        return meal_data(year, month, date)


# 특정 날짜
class Date(Resource):
    def get(self, year, month, date):
        return meal_data(year, month, date)


# 캐시 비우기
class PurgeCache(Resource):
    def get(self):
        dict_data = OrderedDict()
        try:
            file_list = [file for file in os.listdir("data") if file.endswith(".json")]
            for file in file_list:
                os.remove("data/" + file)
        except Exception as error:
            if isDebugging:
                dict_data["status"] = error
            else:
                dict_data["status"] = "Error"
        dict_data["status"] = "OK"
        return dict_data


parser = reqparse.RequestParser()
parser.add_argument('task')

# URL Router에 맵핑한다.(Rest URL정의)
api.add_resource(Today, '/today/')
api.add_resource(Date, '/date/<int:year>-<int:month>-<int:date>')
api.add_resource(PurgeCache, '/purge/')

# 서버 실행
if __name__ == '__main__':
    app.run(debug=isDebugging)
