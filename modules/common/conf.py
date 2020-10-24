# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# conf.py - 설정을 관리하는 스크립트입니다.

import yaml

configs = None
delicious = []


def load():
    global configs, delicious
    with open('data/conf.yaml', 'r', encoding="utf-8") as config_file:
        configs = yaml.load(config_file, Loader=yaml.SafeLoader)
    with open('data/delicious.txt', 'r', encoding="utf-8") as delicious_file:
        delicious = list(map(lambda x: x.strip(), delicious_file.readlines()))  # 개행문자 제거
