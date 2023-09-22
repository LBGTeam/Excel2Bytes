import os.path

import numpy as np

from CSScriptBuilder import CSScriptBuilder
from ExcelCShapUtil import FieldExcelScript, LNGExcelScript, CustomFieldExcelScript
from ExcelUtil import TurnBytesByExcel
from LogUtil import ShowLog
from GlobalUtil import GenerateScriptType
from ConfigData import Config
from TableLoadUtil import LoadExcel, TableDataIsNone


# 生成单个字段的二进制文件
def GenerateFieldBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelTableData = LoadExcel(excelPath, sheetName)
    secValueOldType = str(excelTableData[2][1])
    Scripts = CSScriptBuilder()
    data_bytes = TurnBytesByExcel(os.path.basename(excelPath), excelTableData, 4, 1, GenerateScriptType.FieldType, Scripts)
    FieldExcelScript(scriptName, secValueOldType, scriptName.lower(), Scripts, extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(Config.BytesPath(), f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


# 生成单个字段的二进制文件
def GenerateFindFieldBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelTableData = LoadExcel(excelPath, sheetName)
    Scripts = CSScriptBuilder()
    data_bytes = TurnBytesByExcel(os.path.basename(excelPath), excelTableData, 2, 2, GenerateScriptType.CustomTypeField, Scripts)
    CustomFieldExcelScript(scriptName, scriptName.lower(), Scripts, extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(Config.BytesPath(), f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


def GenerateLNGBytes(sheetName, extraNamespace):
    scriptName = f"Table{os.path.basename(Config.LanguageXlsxPath()).split('.')[0]}"
    excelTableData = LoadExcel(Config.LanguageXlsxPath(), sheetName)
    data_bytes = TurnBytesByExcel(os.path.basename(Config.LanguageXlsxPath()), excelTableData, 4, 0, GenerateScriptType.LNGType)
    cnLanguage = Config.CNLanguage()
    if cnLanguage == sheetName:
        LNGExcelScript(scriptName, scriptName.lower(), extraNamespace)
    # 将bytes保存到本地文件
    LNGPath = os.path.join(Config.LNGBytesPath(), sheetName)
    if not os.path.exists(LNGPath):
        os.mkdir(LNGPath)
    bytesPath = os.path.join(LNGPath, f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


def GenerateNoExportLNGBytes(excelPath, sheetName):
    excelTableData = LoadExcel(excelPath, sheetName)
    TurnBytesByExcel(os.path.basename(excelPath), excelTableData, 4, 0, GenerateScriptType.LNGType)
