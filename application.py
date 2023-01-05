# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo

import argparse
import datetime
import hashlib
import json
from flask import Flask
from flask_restful import request, Api, Resource

from modules.common import conf, log

conf.load()

from modules.chatbot import chat, user
from modules.common import security, cache

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
            # 요청 헤더 또는 쿼리 파라미터에서 토큰 가져오기
            if "X-HDMeal-Token" in request.headers:
                token = request.headers["X-HDMeal-Token"]
            elif request.args.get("token"):
                token = request.args.get("token")
            else:
                log.info("[#%s] Failed to Authorize(No Token)" % req_id)
                return {"version": "2.0", "data": {"msg": "인증 토큰 없음"}}, 401
            # 토큰 일치여부 확인
            if security.auth(token, req_id):
                return original_fn(*args, **kwargs)
            else:
                return {"version": "2.0", "data": {"msg": "미승인 토큰"}}, 403

    return wrapper_fn


# Flask 인스턴스 생성
app = Flask(__name__)
api = Api(app)

api.app.config["RESTFUL_JSON"] = {"ensure_ascii": False}

log.info("Server Started")


# 캐시 상태확인
class CacheHealthCheck(Resource):
    @staticmethod
    @request_id
    @auth
    def get():
        response = cache.health_check(req_id, debugging)
        if isinstance(response, tuple):
            return response + ({"X-HDMeal-Req-ID": req_id},)
        else:
            return response, 200, {"X-HDMeal-Req-ID": req_id}


# 내 정보 관리(API)
cors_headers = {
    "Access-Control-Allow-Origin": conf.configs["Misc"]["Settings"][
        "Access-Control-Allow-Origin"
    ],
    "Access-Control-Allow-Headers": "Content-Type,Access-Control-Allow-Origin,Access-Control-Allow-Headers",
    "Access-Control-Allow-Methods": "GET, POST, DELETE",
}


class UserSettingsREST(Resource):
    @staticmethod
    @request_id
    def get():
        cors_headers["X-HDMeal-Req-ID"] = req_id
        response = user.user_settings_rest_get(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return response, 200, cors_headers

    @staticmethod
    @request_id
    def post():
        cors_headers["X-HDMeal-Req-ID"] = req_id
        response = user.user_settings_rest_post(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return response, 200, cors_headers

    @staticmethod
    @request_id
    def delete():
        cors_headers["X-HDMeal-Req-ID"] = req_id
        response = user.user_settings_rest_delete(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return response, 200, cors_headers

    @staticmethod
    def options():
        return None, 200, cors_headers


# 사용 데이터 관리
class ManageUsageData(Resource):
    @staticmethod
    @request_id
    def get():
        cors_headers["X-HDMeal-Req-ID"] = req_id
        response = user.get_usage_data(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return response, 200, cors_headers

    @staticmethod
    @request_id
    def delete():
        cors_headers["X-HDMeal-Req-ID"] = req_id
        response = user.delete_usage_data(request, req_id, debugging)
        if isinstance(response, tuple):
            return response + (cors_headers,)
        else:
            return response, 200, cors_headers

    @staticmethod
    def options():
        return None, 200, cors_headers


# Fulfillment API
class Fulfillment(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        try:  # 요청 파싱
            req_data: dict = request.json
            intent: str = req_data["queryResult"]["intent"]["displayName"]
            params: dict = req_data["queryResult"]["parameters"]
            utterance: str = req_data["queryResult"]["queryText"]
        except KeyError as key:
            return (
                {"message": "Missing Value: %s Required" % key},
                400,
                {"X-HDMeal-Req-ID": req_id},
            )
        except TypeError:
            return (
                {"message": "Request Body is Not JSON Format"},
                400,
                {"X-HDMeal-Req-ID": req_id},
            )
        except Exception as e:
            if "Failed to decode JSON object" in str(e):
                return (
                    {"message": "Malformed JSON in request body"},
                    400,
                    {"X-HDMeal-Req-ID": req_id},
                )
            else:
                return {"message": "Bad Request"}, 400, {"X-HDMeal-Req-ID": req_id}
        # 사용자 ID 파싱
        uid: str = ""
        prefix: str = ""
        try:  # 페이스북 메신저
            uid = req_data["originalDetectIntentRequest"]["payload"]["data"]["sender"][
                "id"
            ]
            prefix = "FB"
        except KeyError:
            pass
        try:  # 텔레그램
            uid = str(
                req_data["originalDetectIntentRequest"]["payload"]["data"]["from"]["id"]
            )
            prefix = "TG"
        except KeyError:
            pass
        try:  # 라인
            uid = req_data["originalDetectIntentRequest"]["payload"]["data"]["source"][
                "userId"
            ]
            prefix = "LN"
        except KeyError:
            pass
        if uid:  # 사용자 ID 변환(해싱+Prefix 붙이기)
            enc = hashlib.sha256()
            enc.update(uid.encode("utf-8"))
            uid = prefix + "-" + enc.hexdigest()
        else:  # 사용자 ID 없을경우 익명처리
            uid = "ANON-" + req_id
        try:
            if "date" in params:
                if isinstance(params["date"], str):
                    params["date"] = datetime.datetime.strptime(
                        req_data["queryResult"]["parameters"]["date"][:10], "%Y-%m-%d"
                    )
                elif isinstance(params["date"], dict):  # 여러날짜는 리스트로 담음
                    params["date"] = [
                        datetime.datetime.strptime(
                            req_data["queryResult"]["parameters"]["date"]["startDate"][
                                :10
                            ],
                            "%Y-%m-%d",
                        ),
                        datetime.datetime.strptime(
                            req_data["queryResult"]["parameters"]["date"]["endDate"][
                                :10
                            ],
                            "%Y-%m-%d",
                        ),
                    ]
        except ValueError:
            params["date"] = None
        # 로그 남기기
        security.log_req(uid, utterance, intent, params, req_id, "Dialogflow")
        # 요청 수행하기
        respns: tuple = chat.router(prefix, uid, intent, params, req_id, debugging)
        # Fulfillment API 형식으로 변환
        outputs = []
        for item in respns[0]:
            if isinstance(item, str):
                outputs.append({"text": {"text": [item]}})
            elif isinstance(item, dict):
                if item["type"] == "card":
                    card = {"card": {"title": item["title"], "subtitle": item["body"]}}
                    if "image" in item:
                        card["card"]["thumbnail"] = {"imageUrl": item["image"]}
                    if "buttons" in item:
                        card["card"]["buttons"] = []
                        for button in item["buttons"]:
                            if button["type"] == "web":
                                card["card"]["buttons"].append(
                                    {"text": button["title"], "postback": button["url"]}
                                )
                            elif button["type"] == "message":
                                if "postback" in button:
                                    card["card"]["buttons"].append(
                                        {
                                            "label": button["title"],
                                            "postback": button["postback"],
                                        }
                                    )
                                else:
                                    card["card"]["buttons"].append(
                                        {
                                            "label": button["title"],
                                            "postback": button["title"],
                                        }
                                    )
                    outputs.append(card)
        try:
            ga_respns = respns[2]
            outputs.append(
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "simpleResponses": {
                        "simpleResponses": [{"textToSpeech": ga_respns}]
                    },
                }
            )
        except IndexError:
            pass
        return {"fulfillmentMessages": outputs}, 200, {"X-HDMeal-Req-ID": req_id}


# Skill
class Skill(Resource):
    @staticmethod
    @request_id
    @auth
    def post():
        try:  # 요청 파싱
            req_data: dict = request.json
            uid: str = req_data["userRequest"]["user"]["id"]
            intent: str = req_data["intent"]["name"]
            params: dict = req_data["action"]["params"]
            utterance: str = req_data["userRequest"]["utterance"]
            if "date" in params:
                params["date"] = datetime.datetime.strptime(
                    json.loads(req_data["action"]["params"]["date"])["date"], "%Y-%m-%d"
                )
            if "date_period" in params:  # 여러날짜는 리스트로 담음
                params["date"] = [
                    datetime.datetime.strptime(
                        json.loads(req_data["action"]["params"]["date_period"])["from"][
                            "date"
                        ],
                        "%Y-%m-%d",
                    ),
                    datetime.datetime.strptime(
                        json.loads(req_data["action"]["params"]["date_period"])["to"][
                            "date"
                        ],
                        "%Y-%m-%d",
                    ),
                ]
                del params["date_period"]
        except KeyError as key:
            return (
                {"message": "Missing Value: %s Required" % key},
                400,
                {"X-HDMeal-Req-ID": req_id},
            )
        except TypeError:
            return (
                {"message": "Request Body is Not JSON Format"},
                400,
                {"X-HDMeal-Req-ID": req_id},
            )
        except Exception as e:
            if "Failed to decode JSON object" in str(e):
                return (
                    {"message": "Malformed JSON in request body"},
                    400,
                    {"X-HDMeal-Req-ID": req_id},
                )
            else:
                return {"message": "Bad Request"}, 400, {"X-HDMeal-Req-ID": req_id}
        # 사용자 ID 변환(해싱+Prefix 붙이기)
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        uid: str = "KT-" + enc.hexdigest()
        # 로그 남기기
        security.log_req(uid, utterance, intent, params, req_id, "Kakao i")
        # 요청 수행하기
        respns: tuple = chat.router("KT", uid, intent, params, req_id, debugging)
        # Kakao i API 형식으로 변환
        outputs = []
        for item in respns[0]:
            if isinstance(item, str):
                outputs.append({"simpleText": {"text": item}})
            elif isinstance(item, dict):
                if item["type"] == "card":
                    card = {
                        "basicCard": {
                            "title": item["title"],
                            "description": item["body"],
                        }
                    }
                    if "image" in item:
                        card["basicCard"]["thumbnail"] = {"imageUrl": item["image"]}
                    if "buttons" in item:
                        card["basicCard"]["buttons"] = []
                        for button in item["buttons"]:
                            if button["type"] == "web":
                                card["basicCard"]["buttons"].append(
                                    {
                                        "action": "webLink",
                                        "label": button["title"],
                                        "webLinkUrl": button["url"],
                                    }
                                )
                            elif button["type"] == "message":
                                if "postback" in button:
                                    card["basicCard"]["buttons"].append(
                                        {
                                            "action": "message",
                                            "label": button["title"],
                                            "messageText": button["postback"],
                                        }
                                    )
                                else:
                                    card["basicCard"]["buttons"].append(
                                        {
                                            "action": "message",
                                            "label": button["title"],
                                            "messageText": button["title"],
                                        }
                                    )
                    outputs.append(card)
        return (
            {"version": "2.0", "template": {"outputs": outputs}},
            200,
            {"X-HDMeal-Req-ID": req_id},
        )


# URL Router에 맵핑.(Rest URL정의)
api.add_resource(CacheHealthCheck, "/cache/healthcheck/")
api.add_resource(UserSettingsREST, "/user/settings/")
api.add_resource(ManageUsageData, "/user/usage-data/")
api.add_resource(Fulfillment, "/fulfillment/")
api.add_resource(Skill, "/skill/")

# 서버 실행
if __name__ == "__main__":
    debugging = True
    # 커맨드라인 인자값(Test ID) 받기
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-id", help="Test ID")
    args = parser.parse_args()
    if "test_id" in args:
        test_id = args.test_id
    app.run(debug=debugging, threaded=True)
