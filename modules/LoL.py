# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# modules/LoL.py - Riot Games API를 통해 롤 전적을 조회하는 스크립트입니다.

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

from modules import log, conf

# 디버깅용
summoner_name_for_debug = "Hide on Bush"

api_baseurl = conf.configs['Misc']['LoL']['APIBaseURL']
api_key = conf.configs['Tokens']['Riot']
ddragon_version = conf.configs['Misc']['LoL']['DataDragonVersion']


# Riot Games API 사용
def parse(summoner_name, req_id, debugging):
    global api_key
    log.info("[#%s] parse@modules/LoL.py: Started" % req_id)

    if debugging:
        if not summoner_name:
            summoner_name = summoner_name_for_debug

    header = {
        'X-Riot-Token': api_key
    }

    # 소환사 정보 가져오기
    try:
        summoner_req = urllib.request.Request(
            api_baseurl + 'lol/summoner/v4/summoners/by-name/' + urllib.parse.quote(summoner_name),
            data=None, headers=header
        )

        summoner_data = json.load(urllib.request.urlopen(summoner_req))
        summoner_id = summoner_data["id"]
        account_id = summoner_data["accountId"]
    except Exception as error:
        if "404" in str(error):
            return None
        if "401" in str(error) or "403" in str(error):
            return "Invalid Token"
        if debugging:
            print(error)
        log.err("[#%s] parse@modules/LoL.py: Failed to Parse Summoner Data" % req_id)
        return error

    # 소환사의 리그정보 가져오기
    try:
        league_req = urllib.request.Request(
            api_baseurl + 'lol/league/v4/entries/by-summoner/' + summoner_id,
            data=None, headers=header
        )

        league_data = json.load(urllib.request.urlopen(league_req))
    except Exception as error:
        if debugging:
            print(error)
        log.err("[#%s] parse@modules/LoL.py: Failed to Parse League Data" % req_id)
        return error

    # 소환사의 경기전적 가져오기
    try:
        match_req = urllib.request.Request(
            api_baseurl + 'lol/match/v4/matchlists/by-account/' + account_id + '?endIndex=20',
            data=None, headers=header
        )

        match_data = json.load(urllib.request.urlopen(match_req))
    except Exception as error:
        if "404" in str(error):
            match_data = None
        else:
            if debugging:
                print(error)
            log.err("[#%s] parse@modules/LoL.py: Failed to Parse Match Data" % req_id)
            return error

    # 소환사 정보 딕셔너리로 만들기
    data = dict()
    data["summoner"] = {
        "name": summoner_data["name"],  # 소환사명
        "level": summoner_data["summonerLevel"],  # 소환사 레벨
        "profileIcon": ("https://ddragon.leagueoflegends.com/cdn/%s/img/profileicon/%s.png"
                        % (ddragon_version, summoner_data["profileIconId"])),  # 프로필 아이콘
        "OPGG": "https://www.op.gg/summoner/userName=" + urllib.parse.quote(summoner_name)  # OP.GG 링크
    }

    # 승률 계산
    def calculate_winning_rate(wins, losses):
        wins = int(wins)
        losses = int(losses)
        return int(wins / (wins + losses) * 100)

    data["ranked_solo"] = None
    data["ranked_flex"] = None
    for league in league_data:
        # 솔랭 전적
        if league["queueType"] == "RANKED_SOLO_5x5":
            data["ranked_solo"] = {
                "wins": league["wins"],
                "losses": league["losses"],
                "winningRate": calculate_winning_rate(league["wins"], league["losses"]),
                "rank": league["rank"],
                "tier": league["tier"],
                "leaguePoints": league["leaguePoints"]
            }
        # 자유랭 전적
        elif league["queueType"] == "RANKED_FLEX_SR":
            data["ranked_flex"] = {
                "wins": league["wins"],
                "losses": league["losses"],
                "winningRate": calculate_winning_rate(league["wins"], league["losses"]),
                "rank": league["rank"],
                "tier": league["tier"],
                "leaguePoints": league["leaguePoints"]
            }
        else:
            continue

    if match_data:
        data["games"] = match_data["endIndex"]  # 선호도 계산에 사용된 게임 판수(최대 20판)
        lane = list()
        champion = list()
        # 레인과 챔피언으로 List 만들기
        for i in match_data["matches"]:
            if not i["lane"] == "NONE":
                lane.append(i["lane"])
            champion.append(i["champion"])

        # 챔피언 정보 가져오고 ID와 한국어 이름으로 딕셔너리 만들기
        champion_names = dict()
        try:
            if os.path.isfile('data/champion.json'):
                with open('data/champion.json', encoding="utf-8") as data_file:  # 캐시 읽기
                    champion_data = json.load(data_file)["data"]
            else:  # 캐시 없으면
                if os.path.isfile('../data/champion.json'):
                    with open('../data/champion.json', encoding="utf-8") as data_file:  # 캐시 읽기
                        champion_data = json.load(data_file)["data"]
        except Exception as error:
            if debugging:
                print(error)
            log.err("[#%s] parse@modules/LoL.py: Failed to Parse Champion Data" % req_id)
            return error
        for i in champion_data:
            champion_names[int(champion_data[i]["key"])] = champion_data[i]["name"]

        # 선호레인과 챔피언 구하고 플레이 비율 구하기
        data["preferredLane"] = Counter(lane).most_common(1)[0][0], int(
            Counter(lane).most_common(1)[0][1] / data["games"] * 100)
        preferred_champion = Counter(champion).most_common(1)[0]
        data["preferredChampion"] = champion_names[preferred_champion[0]], int(
            preferred_champion[1] / data["games"] * 100)
    else:
        data["games"] = 0
        data["preferredLane"] = None
        data["preferredChampion"] = None

    log.info("[#%s] parse@modules/LoL.py: Succeeded" % req_id)

    return data


if __name__ == "__main__":
    log.init()
    print(parse(None, "****DEBUG****", True))
