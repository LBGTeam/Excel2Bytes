import json
import os

from GlobalUtil import TableConfigJsonPath, ConfigJsonPath, GenerateScriptType


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


def LoadConfigJsonData():
    if not os.path.exists(ConfigJsonPath):
        config = {
            "IsUpdateAllLNG": True,
            "CNLanguage": "cn",
            "TableLanguageCSName": "Languages",
            "BytesExportPath": "",
            "ScriptsExportPath": "",
            "CoreExportPath": "",
            "TableRootNamespace": "LBRuntime",
            "TableResLoadAssembly": "LBUnity",
            "LanguageKey": ["tw", "en"],
            "SupportExcelFormats": [".xlsx", ".xls"],
            "TableSheetInfo": {'ScriptsName': '', 'ImportType': GenerateScriptType.NoneType.name, 'ExtraNamespace': ''},
        }
    else:
        config = LoadJsonData(ConfigJsonPath)
    SaveJsonData(ConfigJsonPath, config)
    return config


def LoadTableJsonData():
    return LoadJsonData(TableConfigJsonPath)


def SaveTableJsonData(TableConfig):
    SaveJsonData(TableConfigJsonPath, TableConfig)

