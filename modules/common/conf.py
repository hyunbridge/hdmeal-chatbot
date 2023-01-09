# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# conf.py - 설정을 관리하는 스크립트입니다.

delicious = []


def load():
    global delicious
    with open("data/delicious.txt", "r", encoding="utf-8") as delicious_file:
        delicious = list(
            map(lambda x: x.strip(), delicious_file.readlines())
        )  # 개행문자 제거
