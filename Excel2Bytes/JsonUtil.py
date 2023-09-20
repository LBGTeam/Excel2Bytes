import json
import os


def LoadJsonData(filePath):
    jsonData = []
    if os.path.exists(filePath):
        with open(filePath, 'r') as f:
            jsonData = json.load(f)
    return jsonData


def SaveJsonData(filePath, jsonData):
    # 回到工程目录
    with open(filePath, 'w') as f:
        json.dump(jsonData, f)
