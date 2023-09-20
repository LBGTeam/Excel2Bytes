import os

from JsonUtil import InitTableJsonData, LoadTableJsonData
from FindGenerate import GenerateFindBytes
from ExcelUtil import CopyScripts, CopyBytes, DeleteScripts, DeleteBytes
from FieldGenerate import GenerateFieldBytes, GenerateLNGBytes, GenerateFindFieldBytes
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


def ExportAllData():
    DeleteFile()
    tableConfig = LoadTableJsonData()
    for excelItem in tableConfig.items():
        for sheetItem in excelItem[1].items():
            if sheetItem[1]['ImportType'] == GenerateScriptType.FieldType.name:
                GenerateFieldBytes(os.path.join(TablePath, excelItem[0]), sheetItem[0], sheetItem[1]['ScriptsName'])
            elif sheetItem[1]['ImportType'] == GenerateScriptType.FindType.name:
                GenerateFindBytes(os.path.join(TablePath, excelItem[0]), sheetItem[0], sheetItem[1]['ScriptsName'])
            elif sheetItem[1]['ImportType'] == GenerateScriptType.LNGType.name:
                GenerateLNGBytes(sheetItem[0], sheetItem[1]['ScriptsName'])
            elif sheetItem[1]['ImportType'] == GenerateScriptType.CustomTypeField.name:
                GenerateFindFieldBytes(os.path.join(TablePath, excelItem[0]), sheetItem[0], sheetItem[1]['ScriptsName'])
    SaveLanguage()
    SaveResList()
    # CopyExportFiles()
    # CreateTableManagerCs()


if __name__ == '__main__':
    InitTable()
    ExportAllData()






