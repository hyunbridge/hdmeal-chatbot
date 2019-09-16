# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# delicious.py - delicious.txt에서 키워드를 읽어와 list형으로 변환해주는 스크립트입니다.

file = open("../data/delicious.txt", 'r', encoding="utf-8")
menu = list()
while True:
    line = file.readline()
    if not line:
        break
    menu.append(line.replace("\n", ""))
file.close()
print(menu)
