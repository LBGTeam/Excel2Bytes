import os

from FindGenerate import GenerateFindBytes
from JsonUtil import InitTableJsonData, LoadTableJsonData
from ExcelUtil import CopyScripts, CopyBytes, DeleteScripts, DeleteBytes
from FieldGenerate import GenerateFieldBytes, GenerateLNGBytes, GenerateFindFieldBytes, GenerateNoExportLNGBytes
from LanguageUtil import InitLanguage, SaveLanguage
from GlobalUtil import InitFileDir, TablePath, GenerateScriptType
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


def ExportAllData():
    DeleteFile()
    tableConfig = LoadTableJsonData()
    for excelItem in tableConfig.items():
        for sheetItem in excelItem[1].items():
            GenerateBytes(sheetItem[1]['ImportType'], os.path.join(TablePath, excelItem[0]), sheetItem[0],
                          sheetItem[1]['ScriptsName'], sheetItem[1]['ExtraNamespace'])
    SaveLanguage()
    SaveResList()
    # CopyExportFiles()
    # CreateTableManagerCs()
