import json
import os

from LogUtil import ShowLog
from GlobalUtil import TableConfigJsonPath, ConfigJsonPath, GenerateScriptType, SavePath, InitFileDir


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
            "TablePath": os.path.join(SavePath, 'Table'),
            "BytesPath": os.path.join(SavePath, 'Bytes'),
            "ScriptsPath": os.path.join(SavePath, 'Scripts'),
            "CorePath": os.path.join(SavePath, 'Core'),
            "LNGBytesPath": os.path.join(SavePath, 'Bytes'),
            "ResRefFileListPath": os.path.join(SavePath, 'reslist.json'),
            "LanguageXlsxPath": os.path.join(SavePath, 'Table', 'Languages.xlsx'),
            "CNLanguage": "cn",
            "TableLanguageCSName": "Languages",
            "BytesExportPath": "",
            "ScriptsExportPath": "",
            "CoreExportPath": "",
            "TableRootNamespace": "LBRuntime",
            "TableResLoadAssembly": "LBUnity",
            "ResLoadScripts": "ResManager.OpenFile({0})",
            "LanguageKey": ["tw", "en"],
            "SupportExcelFormats": [".xlsx", ".xls"],
            "TableSheetInfo": {'ScriptsName': '', 'ImportType': GenerateScriptType.NoneType.name, 'ExtraNamespace': ''},
        }
    else:
        config = LoadJsonData(ConfigJsonPath)

    InitFileDir()
    if not os.path.exists(config['TablePath']):
        os.mkdir(config['TablePath'])
        ShowLog('创建文件夹: Table')
    if not os.path.exists(config['BytesPath']):
        os.mkdir(config['BytesPath'])
        ShowLog('创建文件夹: Bytes')
    if not os.path.exists(config['ScriptsPath']):
        os.mkdir(config['ScriptsPath'])
        ShowLog('创建文件夹: Scripts')
    if not os.path.exists(config['CorePath']):
        os.mkdir(config['CorePath'])
        ShowLog('创建文件夹: Core')
    if not os.path.exists(config['LNGBytesPath']):
        os.mkdir(config['LNGBytesPath'])
        ShowLog('创建文件夹: LNGBytes')

    SaveJsonData(ConfigJsonPath, config)
    return config


def LoadTableJsonData():
    return LoadJsonData(TableConfigJsonPath)


def SaveTableJsonData(TableConfig):
    SaveJsonData(TableConfigJsonPath, TableConfig)

