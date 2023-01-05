# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# security.py - 보안 관련 기능들을 담당하는 스크립트입니다.

import datetime
import random
import authlib.jose.errors as JWTErrors
import pymongo
import requests
from authlib.jose import JsonWebToken, JWTClaims
from modules.common import base58, conf, log

# DB정보 불러오기
connection = pymongo.MongoClient(conf.configs["DataBase"]["ConnectString"])
db = connection.hdmeal
utterances_collection = db.utterances
# 토큰 불러오기
tokens: dict = conf.configs["Tokens"]["HDM"]
# 사용할 JWT 알고리즘
jwt = JsonWebToken(["HS256"])
# JWT 토큰 검증
claim_options = {
    "iss": {"essential": True, "values": ["HDMeal-UserSettings"]},
    "uid": {"essential": True},
    "scope": {"essential": True},
    "reqId": {"essential": True},
    "nbf": {"essential": True, "validate": JWTClaims.validate_nbf},
    "exp": {
        "essential": True,
        "validate": JWTClaims.validate_exp,
    },
}


# DB에 요청 기록
def log_req(
    uid: str, utterance: str, intent: str, params: dict, req_id: str, platform: str
):
    utterances_collection.insert_one(
        {
            "Platform": platform,
            "Date": datetime.datetime.utcnow(),
            "Request ID": req_id,
            "User ID": uid,
            "Utterance": utterance,
            "Intent": intent,
            "Parameters": params,
        }
    )


# JWT 토큰 생성
def generate_token(issuer: str, uid: str, scope: list, req_id: str):
    log.info("[#%s] generate_token@security.py: Token Generated" % req_id)
    now = datetime.datetime.utcnow()
    return jwt.encode(
        {"alg": "HS256", "typ": "JWT"},
        {
            "iss": "HDMeal-" + issuer,
            "uid": uid,
            "scope": scope,
            "reqId": req_id,
            "nbf": now,
            "exp": now + datetime.timedelta(seconds=600),
        },
        conf.configs["Misc"]["Settings"]["Secret"],
    ).decode("UTF-8")


# JWT 토큰 검증
def validate_token(token: str, req_id: str):
    try:
        decoded = jwt.decode(
            token,
            conf.configs["Misc"]["Settings"]["Secret"],
            claims_options=claim_options,
        )
        decoded.validate()
    except JWTErrors.ExpiredTokenError:
        log.info("[#%s] validate_token@security.py: Expired Token" % req_id)
        return False, "ExpiredToken"
    except JWTErrors.JoseError:
        log.info("[#%s] validate_token@security.py: Invalid Token" % req_id)
        return False, "InvalidToken"
    log.info(
        "[#%s] validate_token@security.py: Valid Token (ISS %s)"
        % (req_id, decoded["iss"])
    )
    return True, decoded["uid"], decoded["scope"]


# 리캡챠 토큰 검증
def validate_recaptcha(token: str, req_id: str):
    try:
        req = requests.post(
            "https://www.google.com/recaptcha/api/siteverify?secret=%s&response=%s"
            % (conf.configs["Tokens"]["reCAPTCHA"], token),
            data=None,
        )
        rspns = req.json()
    except Exception:
        log.err(
            "[#%s] validate_recaptcha@security.py: Recaptcha Validation Error" % req_id
        )
        return False, "RecaptchaTokenValidationError"
    if rspns["success"]:
        log.info("[#%s] validate_recaptcha@security.py: Valid Recaptcha Token" % req_id)
        return (True,)
    else:
        log.info(
            "[#%s] validate_recaptcha@security.py: Invalid Recaptcha Token" % req_id
        )
        return False, "InvalidRecaptchaToken"


# 요청 ID 생성
def generate_req_id():
    # 요청 ID는 {난수+유닉스 타임스탬프*100}(17자리)+타임스탬프 위치(1자리)+체크섬(3자리)로, 총 21자리로 이루어져 있음
    # 체크섬은 체크섬을 제외한 요청ID(총 18자리)를 997로 나눈 나머지가 됨
    # 사용자 편의를 위해, 58진법으로 변환되어 보여짐
    tmstm = str(int(datetime.datetime.utcnow().timestamp() * 100))  # 타임스탬프 생성(0.01초 단위)
    rand = str(random.randint(1, 9))  # 첫자리가 0이 되지 않도록 첫자리는 미리 만들어줌
    for i in range(16 - len(tmstm)):  # 랜덤문자열과 타임스탬프를 이어붙여 17자리가 되도록 길이조정
        rand = rand + str(random.randint(0, 9))
    tmstm_loc = str(len(rand))  # 타임스탬프만 추출해낼 수 있도록 타임스탬프 위치 기록
    chksum = str(int(rand + tmstm + tmstm_loc) % 997).zfill(3)  # 3자리 체크섬 만들기
    req_id = int(rand + tmstm + tmstm_loc + chksum)  # 모두 이어붙여 요청 ID 만들기
    return base58.encode(req_id).zfill(12)  # Base58 변환, 12자리 채우기


# 토큰 인증
def auth(token: str, req_id: str):
    if token in tokens:
        log.info('[#%s] Authorized with Token "%s"' % (req_id, tokens[token]))
        return True
    else:
        log.info("[#%s] Failed to Authorize(Token Not Match)" % req_id)
        return False
