import os

from FindGenerate import GenerateFindBytes
from JsonUtil import InitTableJsonData, LoadTableJsonData
from ExcelUtil import CopyScripts, CopyBytes, DeleteScripts, DeleteBytes
from FieldGenerate import GenerateFieldBytes, GenerateLNGBytes, GenerateFindFieldBytes, GenerateNoExportLNGBytes
from LanguageUtil import InitLanguage, SaveLanguage
from GlobalUtil import InitFileDir, TablePath, GenerateScriptType, IsUpdateAllLNG
from ResRefUtil import SaveResList


def InitTable():
    InitFileDir()
    InitLanguage()
    InitTableJsonData()


def DeleteFile():
    DeleteScripts()
    DeleteBytes()


def CopyExportFiles():
    CopyScripts()
    CopyBytes()


def GenerateBytes(scriptType, excelPath, sheetName, scriptName, extraNamespace):
    if scriptType == GenerateScriptType.FieldType.name:
        GenerateFieldBytes(excelPath, sheetName, scriptName, extraNamespace)
    elif scriptType == GenerateScriptType.FindType.name:
        GenerateFindBytes(excelPath, sheetName, scriptName, extraNamespace)
    elif scriptType == GenerateScriptType.LNGType.name:
        GenerateLNGBytes(sheetName, scriptName, extraNamespace)
    elif scriptType == GenerateScriptType.CustomTypeField.name:
        GenerateFindFieldBytes(excelPath, sheetName, scriptName, extraNamespace)
    elif scriptType == GenerateScriptType.NoExportLNGType.name:
        GenerateNoExportLNGBytes(excelPath, sheetName)


def ExportData(tableConfig, isUpdateAllLNG=False, isDeleteFile=False):
    IsUpdateAllLNG = isUpdateAllLNG
    if IsUpdateAllLNG:
        DeleteFile()
    for excelItem in tableConfig.items():
        for sheetItem in excelItem[1].items():
            GenerateBytes(sheetItem[1]['ImportType'], os.path.join(TablePath, excelItem[0]), sheetItem[0],
                          sheetItem[1]['ScriptsName'], sheetItem[1]['ExtraNamespace'])
    SaveLanguage()
    SaveResList()
    # CopyExportFiles()
    # CreateTableManagerCs()


def ExportAllData():
    tableConfig = LoadTableJsonData()
    ExportData(tableConfig, True, True)


def ExportExtraLNG():
    tableConfig = LoadTableJsonData()
    config = {}
    for excelItem in tableConfig.items():
        for sheetItem in excelItem[1].items():
            importType = sheetItem[1]['ImportType']
            if importType == GenerateScriptType.NoExportLNGType.name or importType == GenerateScriptType.LNGType.name:
                if excelItem[0] not in config:
                    config[excelItem[0]] = {sheetItem[0]: sheetItem[1]}
                else:
                    config[excelItem[0]][sheetItem[0]] = sheetItem[1]
    print(config)
    ExportData(config, True, False)
