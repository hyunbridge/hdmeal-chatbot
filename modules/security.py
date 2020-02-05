# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# modules/security.py - 보안 관련 기능들을 담당하는 스크립트입니다.

import datetime
import random
import authlib.jose.errors as JWTErrors
import pymongo
import requests
from authlib.jose import JsonWebToken, JWTClaims
from numpy import base_repr
from modules import conf, log

# DB정보 불러오기
username = conf.configs['DataBase']['Username']
password = conf.configs['DataBase']['Password']
server = conf.configs['DataBase']['Server']
connection = pymongo.MongoClient("mongodb://%s:%s@%s" % (username, password, server))
db = connection.hdmeal
utterances_collection = db.utterances
# 토큰 불러오기
tokens: dict = conf.configs['Tokens']['HDM']
# 사용할 JWT 알고리즘
jwt = JsonWebToken(['ES512'])
# JWT 토큰 검증
claim_options = {
            "iss": {
                "essential": True
            },
            "iat": {
                "essential": True,
                "validate": JWTClaims.validate_iat
            },
            "nbf": {
                "essential": True,
                "validate": JWTClaims.validate_nbf
            },
            "exp": {
                "essential": True,
                "validate": JWTClaims.validate_exp,
            },
            "uid": {
                "essential": True
            }
        }


# DB에 요청 기록
def log_req(uid: str, utterance: str, intent: str, params: dict, req_id: str, platform: str):
    utterances_collection.insert_one({
        "Platform": platform,
        "Date": datetime.datetime.utcnow(),
        "Request ID": req_id,
        "User ID": uid,
        "Utterance": utterance,
        "Intent": intent,
        "Parameters": params
    })

# JWT 토큰 생성
def generate_token(uid: str, req_id: str):
    log.info("[#%s] generate_token@modules/security.py: Token Generated" % req_id)
    now = datetime.datetime.utcnow()
    return jwt.encode(
        {
            'alg': 'ES512',
            'typ': 'JWT'
        },
        {
            'iss': 'HDMeal (Req #%s)' % req_id,
            'iat': now,
            'nbf': now,
            'exp': now + datetime.timedelta(seconds=600),
            'uid': uid
        },
        conf.privkey).decode("UTF-8")

# JWT 토큰 검증
def validate_token(token: str, req_id: str):
    try:
        decoded = jwt.decode(token, conf.pubkey.encode('UTF-8'), claims_options=claim_options)
        decoded.validate()
    except JWTErrors.ExpiredTokenError:
        log.info("[#%s] validate_token@modules/security.py: Expired Token" % req_id)
        return False, "ExpiredToken"
    except JWTErrors.JoseError:
        log.info("[#%s] validate_token@modules/security.py: Invalid Token" % req_id)
        return False, "InvalidToken"
    log.info("[#%s] validate_token@modules/security.py: Valid Token (ISS %s)" % (req_id, decoded['iss']))
    return True, decoded['uid']

# 리캡챠 토큰 검증
def validate_recaptcha(token: str, req_id: str):
    try:
        req = requests.post(
            'https://www.google.com/recaptcha/api/siteverify?secret=%s&response=%s'
            % (conf.configs['Tokens']['reCAPTCHA'], token), data=None
        )
        rspns = req.json()
    except Exception:
        log.err("[#%s] validate_recaptcha@modules/security.py: Recaptcha Validation Error" % req_id)
        return False, "RecaptchaTokenValidationError"
    if rspns['success']:
        log.info("[#%s] validate_recaptcha@modules/security.py: Valid Recaptcha Token" % req_id)
        return True,
    else:
        log.info("[#%s] validate_recaptcha@modules/security.py: Invalid Recaptcha Token" % req_id)
        return False, "InvalidRecaptchaToken"

# 요청 ID 생성
def generate_req_id():
    rand = str(random.randint(1, 99999)).zfill(5)  # 5자리 난수 생성
    tmstm = str(int(datetime.datetime.utcnow().timestamp()))  # 타임스탬프 생성
    return base_repr(int(rand + tmstm), base=36).zfill(10)  # 난수 + 타임스탬프 합치고 Base36 변환, 10자리 채우기

# 토큰 인증
def auth(token: str, req_id: str):
    if token in tokens:
        log.info('[#%s] Authorized with Token "%s"' % (req_id, tokens[token]))
        return True
    else:
        log.info('[#%s] Failed to Authorize(Token Not Match)' % req_id)
        return False
