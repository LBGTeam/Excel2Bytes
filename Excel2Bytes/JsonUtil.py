import json
import os

import pandas as pd

from GlobalUtil import TablePath, SupportExcelFormats, TableSheetInfo, TableConfigJsonPath, GetScriptsName


def LoadJsonData(filePath):
    jsonData = {}
    if os.path.exists(filePath):
        with open(filePath, 'r') as f:
            jsonData = json.load(f)
    return jsonData


def SaveJsonData(filePath, jsonData):
    # 回到工程目录
    with open(filePath, 'w') as f:
        json.dump(jsonData, f, indent=4, ensure_ascii=False)


def InitTableJsonData():
    TableConfig = LoadJsonData(TableConfigJsonPath)
    fileLists = os.listdir(TablePath)
    newTableConfig = {}
    for fileName in fileLists:
        if any([fileName.endswith(ext) for ext in SupportExcelFormats]):
            if fileName not in TableConfig:
                TableConfig[fileName] = {}
            newTableConfig[fileName] = {}
            filePath = os.path.join(TablePath, fileName)
            workbook = pd.ExcelFile(filePath)
            for sheetName in workbook.sheet_names:
                if sheetName not in TableConfig[fileName]:
                    TableConfig[fileName][sheetName] = {}
                newTableConfig[fileName][sheetName] = {}
                for info in TableSheetInfo.keys():
                    if info not in TableConfig[fileName][sheetName]:
                        TableConfig[fileName][sheetName][info] = TableSheetInfo[info]
                    newTableConfig[fileName][sheetName][info] = TableConfig[fileName][sheetName][info]
                scriptName = TableConfig[fileName][sheetName]['ScriptsName']
                if scriptName.isspace() or len(scriptName) == 0 or scriptName is None:
                    TableConfig[fileName][sheetName]['ScriptsName'] = GetScriptsName(filePath, sheetName)
                newTableConfig[fileName][sheetName]['ScriptsName'] = TableConfig[fileName][sheetName]['ScriptsName']
    SaveTableJsonData(newTableConfig)


def LoadTableJsonData():
    return LoadJsonData(TableConfigJsonPath)


def SaveTableJsonData(TableConfig):
    SaveJsonData(TableConfigJsonPath, TableConfig)
