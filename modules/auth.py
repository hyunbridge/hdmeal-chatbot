import json
import hashlib

def check(uid):
    with open('data/uid.json', encoding="utf-8") as data_file:
        enc = hashlib.sha256()
        enc.update(uid.encode("utf-8"))
        encText = enc.hexdigest()
        data = json.load(data_file)
        if encText in data:
            return True
        else:
            return False
