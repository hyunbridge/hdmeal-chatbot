# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019, Hyungyo Seo
# test.py - 유닛 테스트용 스크립트입니다.

import atexit
import datetime
import json
import os
import platform
import random
import shutil
import signal
import subprocess
import unittest
import requests


class Tests(unittest.TestCase):

    # 서버 종료
    # atexit에 등록하여 태스터 프로세스 종료시 함께 종료시킴
    @staticmethod
    @atexit.register
    def kill_server():
        # 서버 프로세스와 그 자식 프로세스까지 모두 종료시켜야 합니다.
        # Microsoft Windows가 아닌 OS에서는 프로세스 그룹을 구해서 종료시키고,
        # Microsoft Windows에서는 Taskill에 /T 옵션을 주어 종료시킵니다.
        if "server" in globals() and not server.poll():  # 서버가 실행된 상태일때만 종료구문 실행
            if platform.system() is not 'Windows':
                pgid = os.getpgid(server.pid)
                os.killpg(pgid, signal.SIGKILL)
            else:
                subprocess.check_output("Taskkill /PID %d /T /F" % server.pid)

    # 테스터 실행 시 한 번만 실행되는 구문
    # 테스트 ID, 인터프리터 위치 정의
    @classmethod
    def setUpClass(self):
        global server, base_url, start_time

        while True:
            print("테스트를 실행하면 캐시가 모두 삭제되고, 임의의 사용자가 생성된 뒤 삭제됩니다.")
            print("이는 테스트 과정상 발생하는 것으로, 확인해 주시지 않으면 테스트를 진행할 수 없습니다.")
            confirm = input("위의 내용을 확인하셨습니까? [Y/n]: ")
            confirm = confirm.strip()
            if confirm == "Y" or confirm == "y":
                break
            elif confirm == "N" or confirm == "n":
                exit(0)
            elif not confirm:
                break
            else:
                print("테스트를 진행하시려면 Y를 입력해 주시고, 종료하시려면 N을 입력해 주세요.")

        start_time = datetime.datetime.now()
        while True:
            # Test ID 생성
            global test_id
            now = datetime.datetime.now()
            date = "%s%s%s" % (str(now.year)[2:].zfill(2), str(now.month).zfill(2), str(now.day).zfill(2))
            rand = str(random.randint(1, 9999)).zfill(4)
            test_id = "T-%s-%s" % (date, rand)
            # 백업 폴더에 중복파일 있는지 확인
            if not os.path.isfile("bak/data[%s].zip" % test_id[2:]):
                break
            time_delta = datetime.datetime.now() - start_time
            # Timeout 되면
            if time_delta.total_seconds() >= 5:
                print("테스트 ID를 만들 수 없었습니다.")
                print("bak 폴더에 백업 파일이 너무 많으면 그럴 수 있으니 bak 폴더를 확인해 주세요.")
                exit(1)

        print('테스트 ID는 "%s" 입니다.' % test_id)

        while True:
            print("data 폴더를 백업하실 수 있습니다.")
            print("백업 파일은 bak/data[%s].zip 에 압축되어 저장됩니다." % test_id[2:])
            backup = input("data 폴더를 백업 하시겠습니까? [y/N]: ")
            backup = backup.strip()
            if backup == "Y" or backup == "y":
                if not os.path.exists("bak"):  # 폴더 없으면 만들기
                    os.mkdir("bak")
                if os.path.isfile("bak/data[%s].zip" % test_id[2:]):  # 파일명 중복체크
                    print("해당 파일명이 이미 존재합니다. 백업 디렉토리를 확인해 주세요.")
                    exit(1)
                shutil.make_archive("bak/data[%s]" % test_id[2:], 'zip', "data")  # data 폴더 압축
                break
            elif backup == "N" or backup == "n":
                break
            elif not backup:
                break
            else:
                print("백업하시려면 Y를 입력해 주시고, 그렇지 않다면 N을 입력해 주세요.")

        while True:
            interpreter = input("파이썬3 인터프리터 위치를 입력해주세요. [python]: ")
            interpreter = interpreter.strip()
            if not interpreter:
                interpreter = "python"
            try:  # 인터프리터 버전 체크
                if not subprocess.check_output([interpreter, "--version"]).decode("UTF-8")[:8] == "Python 3":
                    print("올바른 파이썬 3 인터프리터가 아닌 것 같습니다.")
                    exit(1)
            except Exception:
                print("올바른 파이썬 3 인터프리터가 아닌 것 같습니다.")
                exit(1)
            break

        # 서브프로세스로 서버 실행, 인자로 테스트 ID 넘김
        server = subprocess.Popen(interpreter + " application.py --test-id " + test_id, shell=True)
        base_url = "http://127.0.0.1:5000/"

        start_time = datetime.datetime.now()
        while True:
            # Timeout 되면
            time_delta = datetime.datetime.now() - start_time
            if time_delta.total_seconds() >= 5:
                print("서버를 실행할 수 없었습니다.")
                exit(1)
            try:
                status_code = requests.get(base_url).status_code
            except Exception:
                continue
            if status_code == 404:  # Base URL로 요청 보내면 원래 404오류 남
                break

    # 테스트 실행 전 실행되는 구문
    # 캐시의 영향을 없애기 위해, 캐시를 비움
    def setUp(self):
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)

    # 모든 테스트가 끝난 이후 실행되는 구문
    # 테스트용 사용자를 삭제하고, 캐시를 비움
    @classmethod
    def tearDownClass(self):
        request_data = (
            {
                "userRequest": {
                    "user": {
                        "id": test_id
                    }
                }
            }
        )
        requests.post(base_url + "user/delete/", data=json.dumps(request_data))  # 사용자 삭제 요청 보내기

        # 캐시 삭제
        file_list = [file for file in os.listdir("data/cache/") if file.endswith(".json")]
        for file in file_list:
            os.remove("data/cache/" + file)

    # 브리핑
    def test_briefing(self):
        request_data = (
            {
                "userRequest": {
                    "user": {
                        "id": test_id
                    }
                }
            }
        )
        request = requests.post(base_url + "briefing/", data=json.dumps(request_data))
        data = request.json()["template"]["outputs"]

        def block(loc):
            return data[loc]["simpleText"]["text"]

        self.assertEqual(request.status_code, 200, "비 정상 응답")
        self.assertEqual("오류" in block(0), False, "1번 블록에 오류 있음\n\n" + block(0))
        self.assertEqual("오류" in block(1), False, "2번 블록에 오류 있음\n\n" + block(1))
        self.assertEqual("오류" in block(2), False, "3번 블록에 오류 있음\n\n" + block(2))

    # 사용자
    def test_user(self):
        request_data = (
            {
                "userRequest": {
                    "user": {
                        "id": test_id
                    }
                },
                "action": {
                    "params": {
                        "Grade": "1",
                        "Class": "1"
                    }
                }
            }
        )
        request_manage = requests.post(base_url + "user/manage/", data=json.dumps(request_data))
        response_data_manage = request_manage.json()["data"]["msg"]
        request_delete = requests.post(base_url + "user/delete/", data=json.dumps(request_data))
        response_data_delete = request_delete.json()["data"]["msg"]

        self.assertEqual(request_manage.status_code, 200, "비 정상 응답 (Manage)")
        self.assertEqual("오류" in response_data_manage, False, "서버 오류 발생 (Manage)")
        self.assertEqual(request_delete.status_code, 200, "비 정상 응답 (Delete)")
        self.assertEqual("오류" in response_data_delete, False, "서버 오류 발생 (Delete)")

        requests.post(base_url + "user/manage/", data=json.dumps(request_data))

    # 식단 조회
    def test_meal(self):
        request_data = (
            {
                "action": {
                    "params": {
                        "sys_date":
                            "{\"dateTag\": \"tomorrow\", \"dateHeadword\": null, \"month\": null, \"year\": null,"
                            " \"date\": \"%s\", \"day\": null}" % start_time.date(),
                        "date": str(start_time.date())
                    }
                }
            }
        )
        request_general = requests.post(base_url + "meal/", data=json.dumps(request_data))
        response_data_general = request_general.json()["data"]["msg"]
        request_specificdate = requests.post(base_url + "meal/specificdate/", data=json.dumps(request_data))
        response_data_specificdate = request_specificdate.json()["data"]["msg"]

        self.assertEqual(request_general.status_code, 200, "비 정상 응답 (General)")
        self.assertEqual("오류" in response_data_general, False, "서버 오류 발생 (General)")
        self.assertEqual(request_specificdate.status_code, 200, "비 정상 응답 (SpecificDate)")
        self.assertEqual("오류" in response_data_specificdate, False, "서버 오류 발생 (SpecificDate)")

    # 시간표 조회
    def test_timetable(self):
        request_data = (
            {
                "userRequest": {
                    "user": {
                        "id": test_id
                    }
                },
                "action": {
                    "params": {
                        "Grade": "1",
                        "Class": "1",
                        "sys_date":
                            "{\"dateTag\": \"tomorrow\", \"dateHeadword\": null, \"month\": null, \"year\": null,"
                            " \"date\": \"%s\", \"day\": null}" % start_time.date()
                    }
                }
            }
        )
        request_non_registered = requests.post(base_url + "tt/", data=json.dumps(request_data))
        response_data_non_registered = request_non_registered.json()["data"]["msg"]
        request_registered = requests.post(base_url + "tt/registered/", data=json.dumps(request_data))
        response_data_registered = request_registered.json()["data"]["msg"]

        self.assertEqual(request_non_registered.status_code, 200, "비 정상 응답 (General)")
        self.assertEqual("오류" in response_data_non_registered, False, "서버 오류 발생 (General)")
        self.assertEqual(request_registered.status_code, 200, "비 정상 응답 (SpecificDate)")
        self.assertEqual("오류" in response_data_registered, False, "서버 오류 발생 (SpecificDate)")

    # 학사일정 조회
    def test_schedule(self):
        request_data_single = (
            {
                "action": {
                    "params": {
                        "sys_date":
                            "{\"dateTag\": \"tomorrow\", \"dateHeadword\": null, \"month\": null, \"year\": null,"
                            " \"date\": \"%s\", \"day\": null}" % start_time.date()
                    }
                }
            }
        )
        request_data_mass = (
            {
                "action": {
                    "params": {
                        "sys_date_period":
                            "{\"to\": {\"dateTag\": null, \"dateHeadword\": null, \"month\": null, \"year\": null,"
                            " \"date\": \"%s\", \"day\": null}, \"from\": {\"dateTag\": null,"
                            " \"dateHeadword\": null, \"month\": null, \"year\": null, \"date\": \"%s\","
                            " \"day\": null}}" % ((start_time + datetime.timedelta(days=7)).date(),
                                                  (start_time - datetime.timedelta(days=7)).date())
                    }
                }
            }
        )
        request_single = requests.post(base_url + "cal/", data=json.dumps(request_data_single))
        response_data_single = request_single.json()["data"]["msg"]
        request_mass = requests.post(base_url + "cal/", data=json.dumps(request_data_mass))
        response_data_mass = request_mass.json()["data"]["msg"]

        self.assertEqual(request_single.status_code, 200, "비 정상 응답 (Single)")
        self.assertEqual("오류" in response_data_single, False, "서버 오류 발생 (Single)")
        self.assertEqual(request_mass.status_code, 200, "비 정상 응답 (Mass)")
        self.assertEqual("오류" in response_data_mass, False, "서버 오류 발생 (Mass)")

    # 한강 수온 조회
    def test_wtemp(self):
        request = requests.post(base_url + "wtemp/")
        response_data = request.json()["data"]["msg"]

        self.assertEqual(request.status_code, 200, "비 정상 응답")
        self.assertEqual("오류" in response_data, False, "서버 오류 발생")

    # 페이스북 포스팅
    def test_facebook(self):
        request = requests.post(base_url + "fb/")
        response_data = request.json()

        self.assertEqual(request.status_code, 200, "비 정상 응답")
        self.assertEqual("OK" == response_data["Parser"], True, "파서 오류 발생")
        self.assertEqual("OK" == response_data["IMG"], True, "이미지 생성 중 오류 발생")

    # 커밋 기록 조회
    def test_commits(self):
        request = requests.post(base_url + "commits/")
        response_data = request.json()["data"]["msg"]

        self.assertEqual(request.status_code, 200, "비 정상 응답")

    # 롤 전적 조회
    def test_lol(self):
        request_data = (
            {
                "action": {
                    "params": {
                        "summonerName": "미국거주희선아빠"
                    }
                }
            }
        )
        request = requests.post(base_url + "lol/", data=json.dumps(request_data))
        response_data = request.json()["template"]["outputs"][0]

        self.assertEqual(request.status_code, 200, "비 정상 응답")
        self.assertEqual("basicCard" in response_data, True, "서버 오류 발생")


if __name__ == '__main__':
    unittest.main()
