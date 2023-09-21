import os

from FirstInitUtil import FirstGenerateData
from FindGenerate import GenerateFindBytes
from ExcelUtil import CopyScripts, CopyBytes, DeleteScripts, DeleteBytes
from FieldGenerate import GenerateFieldBytes, GenerateLNGBytes, GenerateFindFieldBytes, GenerateNoExportLNGBytes
from LanguageUtil import InitLanguage, SaveLanguage
from GlobalUtil import GenerateScriptType
from ResRefUtil import SaveResList
from ConfigData import Config, TableConfig


def InitTable():
    InitLanguage()
    TableConfig.InitTableJsonData()


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


def ExportData(isUpdateAllLNG=False, isDeleteFile=False):
    IsUpdateAllLNG = isUpdateAllLNG
    InitTable()
    if isDeleteFile:
        DeleteFile()
    for excelItem in TableConfig.items():
        for sheetItem in excelItem[1].items():
            if (IsUpdateAllLNG or sheetItem[1]['ImportType'] != GenerateScriptType.LNGType.name
                    or sheetItem[0] == Config.CNLanguage()):
                GenerateBytes(sheetItem[1]['ImportType'], os.path.join(Config.TablePath(), excelItem[0]), sheetItem[0],
                              sheetItem[1]['ScriptsName'], sheetItem[1]['ExtraNamespace'])
    SaveLanguage()
    SaveResList()
    CopyExportFiles()


def ExportAllData():
    ExportData(True, True)


def ExportExtraLNG():
    config = {}
    for excelItem in TableConfig.items():
        for sheetItem in excelItem[1].items():
            importType = sheetItem[1]['ImportType']
            if importType == GenerateScriptType.NoExportLNGType.name or importType == GenerateScriptType.LNGType.name:
                if excelItem[0] not in config:
                    config[excelItem[0]] = {sheetItem[0]: sheetItem[1]}
                else:
                    config[excelItem[0]][sheetItem[0]] = sheetItem[1]
    ExportData(True, False)


def FirstExportProject():
    TableConfig.InitTableJsonData()
    FirstGenerateData()
