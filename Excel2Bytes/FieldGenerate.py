import os.path

import numpy as np
import pandas as pd

from CSScriptBuilder import CSScriptBuilder
from ExcelCShapUtil import FieldExcelScript, LNGExcelScript, CustomFieldExcelScript
from ExcelUtil import TurnBytesByExcel
from LogUtil import ShowLog
from GlobalUtil import GenerateScriptType
from ConfigData import Config


# 生成单个字段的二进制文件
def GenerateFieldBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    firstRow = excelData.iloc[0]
    columns_with_c = np.where(firstRow.str.contains('c', case=False))[0]
    secondIndex = columns_with_c[1]
    secValueOldType = str(excelData.iloc[2, secondIndex])
    Scripts = CSScriptBuilder()
    data_bytes = TurnBytesByExcel(excelData, 4, 1, GenerateScriptType.FieldType, Scripts)
    FieldExcelScript(scriptName, secValueOldType, scriptName.lower(), Scripts, extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(Config.BytesPath(), f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


# 生成单个字段的二进制文件
def GenerateFindFieldBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    Scripts = CSScriptBuilder()
    data_bytes = TurnBytesByExcel(excelData, 2, 2, GenerateScriptType.CustomTypeField, Scripts)
    CustomFieldExcelScript(scriptName, scriptName.lower(), Scripts, extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(Config.BytesPath(), f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


def GenerateLNGBytes(sheetName, scriptName, extraNamespace):
    excelData = pd.read_excel(Config.LanguageXlsxPath(), sheet_name=sheetName, header=None)
    data_bytes = TurnBytesByExcel(excelData, 4, 0, GenerateScriptType.LNGType)
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
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    TurnBytesByExcel(excelData, 4, 0, GenerateScriptType.LNGType)
