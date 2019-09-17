# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# delicious.py - delicious.txt에서 키워드를 읽어와 list형으로 변환해주는 스크립트입니다.

keyword = list()
with open("../data/delicious.txt", 'r', encoding="utf-8") as file:
    while True:
        line = file.readline()
        if not line:  # 내용이 없을 경우 반복문 탈출
            break
        keyword.append(line.replace("\n", ""))

sort = sorted(list(set(keyword)))  # set 자료형으로 변환하여 중복제거 후 정렬

text = str()
for i in sort:
    text = "%s\n%s" % (text, i)  # text 파일에 저장할 값 만들기
text = text[1:]  # 맨 처음 줄바꿈 제거
with open("../data/delicious.txt", 'w', encoding="utf-8") as file:
    file.write(text)  # 파일에 쓰기

print(sort)  # 코드에 반영할 수 있도록 리스트 출력
