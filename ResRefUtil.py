import json

from ConfigData import Config

ResList = []


def AddResRef(resName):
    if resName not in ResList:
        ResList.append(resName)


def SaveResList():
    with open(Config.ResRefFileListPath(), 'w') as f:
        json.dump(ResList, f, indent=4, ensure_ascii=False)
