import json
import os

from PathUtil import SavePath

ResList = []


def AddResRef(resName):
    if resName not in ResList:
        ResList.append(resName)


def SaveResList():
    with open(os.path.join(SavePath, 'reslist.json'), 'w') as f:
        json.dump(ResList, f, indent=4, ensure_ascii=False)
