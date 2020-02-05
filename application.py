# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo

import argparse
import datetime
import hashlib
import json
import re
import requests
from flask import Flask
from flask_restful import request, Api, Resource
from modules import conf

conf.load()
from modules import getData, log, cache, user, chat, security, FB

# 디버그용
debugging = False
test_id = None
# today에서 사용됨
today_year = 2019
today_month = 7
today_date = 14

# 초기화
log.init()


# 요청코드 생성
def request_id(original_fn):
    def wrapper_fn(*args, **kwargs):
        global req_id
        # Test ID 있으면 Test ID 사용
        if test_id:
            req_id = test_id
        else:
            req_id = security.generate_req_id()
        return original_fn(*args, **kwargs)

    return wrapper_fn


# 토큰 인증
# 인증 데코레이터는 반드시 요청코드 데코레이터 밑에 작성
def auth(original_fn):
    def wrapper_fn(*args, **kwargs):
        if test_id:
            log.info("[#%s] Bypassing Authorization")
            return original_fn(*args, **kwargs)
        else:
            if "X-HDMeal-Token" in request.headers:
                if security.auth(request.headers["X-HDMeal-Token"], req_id):
                    return original_fn(*args, **kwargs)
                else:
                    return {'version': '2.0', 'data': {'msg': "미승인 토큰"}}, 403
            else:
                log.info('[#%s] Failed to Authorize(No Token)' % req_id)
                return {'version': '2.0', 'data': {'msg': "인증 토큰 없음"}}, 401

    return wrapper_fn


# Flask 인스턴스 생성
app = Flask(__name__, static_folder='./data/static')
api = Api(app)
log.info("Server Started")


# 캐시 상태확인
class CacheHealthCheck(Resource):
    @staticmethod
    @request_id
    @auth
    def get():
        return cache.health_check(req_id, debugging)


# 내 정보 관리(API)
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "application/json,Content-Type,Content-Length,Access-Control-Allow-Origin,Access-Control-Allow-Headers,Server,Date",
    "Access-Control-Allow-Methods": "GET, POST, DELETE"
}


class UserSettingsREST(Resource):
    @staticmethod
    @request_id
    def get():
        response = user.user_settings_rest_get(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)

    @staticmethod
    @request_id
    def post():
        response = user.user_settings_rest_post(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)

    @staticmethod
    @request_id
    def delete():
        response = user.user_settings_rest_delete(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return (response, 200, cors_headers)

    @staticmethod
    def options():
        return None, 200, cors_headers


# 푸시 알림 보내기
class Notify(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        now = datetime.datetime.now()
        onesignal_app_id = conf.configs['Tokens']['OneSignal']['AppID']
        onesignal_api_key = conf.configs['Tokens']['OneSignal']["APIKey"]
        try:
            title = json.loads(request.data)["Title"]
            url = json.loads(request.data)["URL"]
        except Exception:
            return {"message": "올바른 요청이 아님"}, 400
        if now.weekday() >= 5:
            return {"message": "알림미발송(주말)"}
        meal = getData.meal(now.year, now.month, now.day, req_id, debugging)
        if not "menu" in meal:
            return {"message": "알림미발송(정보없음)"}
        reqbody = {
            "app_id": onesignal_app_id,
            "headings": {
                "en": title
            },
            "contents": {
                "en": meal["date"] + " 급식:\n" + re.sub(r'\[[^\]]*\]', '', meal["menu"]).replace('⭐', '')
            },
            "url": url,
            "included_segments": [
                "All"
            ]
        }
        reqheader = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + onesignal_api_key
        }
        try:
            requests.post("https://onesignal.com/api/v1/notifications", data=json.dumps(reqbody), headers=reqheader)
        except Exception as error:
            return error
        return {"message": "성공"}


# Fulfillment API
class Fulfillment(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        try:  # 요청 파싱
            req_data: dict = json.loads(request.data)
            uid: str = req_data['originalDetectIntentRequest']['payload']['data']['sender']['id']
            intent: str = req_data["queryResult"]["intent"]["displayName"]
            params: dict = req_data['queryResult']['parameters']
            utterance: str = req_data["queryResult"]["queryText"]
        except Exception:
            return {"message": "Bad Request"}, 400
        try:
            if 'date' in params:
                if isinstance(params['date'], str):
                    params['date'] = datetime.datetime.strptime(req_data['queryResult']['parameters']['date'][:10],
                                                                "%Y-%m-%d")
                elif isinstance(params['date'], dict):  # 여러날짜는 리스트로 담음
                    params['date'] = [datetime.datetime.strptime(req_data['queryResult']['parameters']['date']
                                                                 ['startDate'][:10], "%Y-%m-%d"),
                                      datetime.datetime.strptime(req_data['queryResult']['parameters']['date']
                                                                 ['endDate'][:10], "%Y-%m-%d")]
        except ValueError:
            params['date'] = None
        # 사용자 ID 변환(해싱+Prefix 붙이기)
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        uid: str = 'FB-' + enc.hexdigest()
        # 로그 남기기
        security.log_req(uid, utterance, intent, params, req_id, "Dialogflow")
        # 요청 수행하기
        respns: tuple = chat.router(uid, intent, params, req_id, debugging)
        # Fulfillment API 형식으로 변환
        outputs = []
        for item in respns[0]:
            if isinstance(item, str):
                outputs.append({"text": {"text": [item]}})
            elif isinstance(item, dict):
                if item['type'] == 'card':
                    card = {"card": {
                        "title": item['title'],
                        "subtitle": item['body']
                    }}
                    if 'image' in item:
                        card["card"]["thumbnail"] = {"imageUrl": item['image']}
                    if 'buttons' in item:
                        card["card"]["buttons"] = []
                        for button in item['buttons']:
                            if button['type'] == 'web':
                                card["card"]["buttons"].append({
                                    "text": button['title'],
                                    "postback": button['url']})
                            elif button['type'] == 'message':
                                card["card"]["buttons"].append({
                                    "label": button['title'],
                                    "postback": button['title']})
                    outputs.append(card)
        return {"fulfillmentMessages": outputs}


# Skill
class Skill(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        try:  # 요청 파싱
            req_data: dict = json.loads(request.data)
            uid: str = req_data["userRequest"]["user"]["id"]
            intent: str = req_data["intent"]["name"]
            params: dict = req_data["action"]["params"]
            utterance: str = req_data["userRequest"]["utterance"]
            if 'date' in params:
                params['date'] = datetime.datetime.strptime(
                    json.loads(req_data["action"]["params"]["date"])["date"],
                    "%Y-%m-%d"
                )
            if 'date_period' in params:  # 여러날짜는 리스트로 담음
                params['date'] = [datetime.datetime.strptime(
                    json.loads(req_data["action"]["params"]["date_period"])["from"]["date"],
                    "%Y-%m-%d"
                ), datetime.datetime.strptime(
                    json.loads(req_data["action"]["params"]["date_period"])["to"]["date"],
                    "%Y-%m-%d"
                )]
                del params['date_period']
        except Exception:
            return {"message": "Bad Request"}, 400
        # 사용자 ID 변환(해싱+Prefix 붙이기)
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        uid: str = 'KT-' + enc.hexdigest()
        # 로그 남기기
        security.log_req(uid, utterance, intent, params, req_id, "Kakao i")
        # 요청 수행하기
        respns: tuple = chat.router(uid, intent, params, req_id, debugging)
        # Kakao i API 형식으로 변환
        outputs = []
        for item in respns[0]:
            if isinstance(item, str):
                outputs.append({'simpleText': {'text': item}})
            elif isinstance(item, dict):
                if item['type'] == 'card':
                    card = {"basicCard": {
                        "title": item['title'],
                        "description": item['body']
                    }}
                    if 'image' in item:
                        card["basicCard"]["thumbnail"] = {"imageUrl": item['image']}
                    if 'buttons' in item:
                        card["basicCard"]["buttons"] = []
                        for button in item['buttons']:
                            if button['type'] == 'web':
                                card["basicCard"]["buttons"].append({"action": "webLink",
                                                                     "label": button['title'],
                                                                     "webLinkUrl": button['url']})
                            elif button['type'] == 'message':
                                card["basicCard"]["buttons"].append({"action": "message",
                                                                     "label": button['title'],
                                                                     "messageText": button['title']})
                    outputs.append(card)
        return {'version': '2.0', 'template': {'outputs': outputs}}


# 페이스북 페이지 업로드
class FBPage(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        return FB.publish(conf.configs['Tokens']['FBPage']['Page-Access-Token'], req_id, debugging)


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(CacheHealthCheck, '/cache/healthcheck/')
api.add_resource(UserSettingsREST, '/user/settings/')
api.add_resource(Fulfillment, '/fulfillment/')
api.add_resource(Skill, '/skill/')
api.add_resource(Notify, '/notify/')
api.add_resource(FBPage, '/facebook/page/')

# 서버 실행
if __name__ == '__main__':
    debugging = True
    # 커맨드라인 인자값(Test ID) 받기
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-id", help="Test ID")
    args = parser.parse_args()
    if "test_id" in args:
        test_id = args.test_id
    app.run(debug=debugging)
