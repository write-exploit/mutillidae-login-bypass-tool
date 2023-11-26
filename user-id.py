import json
import argparse

parser = argparse.ArgumentParser(description='user id',usage="tool kullanım rehberi")

parser.add_argument("uid")

args = parser.parse_args()

uid = args.uid
with open(r"user-information.json","r") as dosya:
    json_file:dict = json.load(dosya)

for i in json_file:
    try:
        print(i[str(uid)])
    except:
        pass
