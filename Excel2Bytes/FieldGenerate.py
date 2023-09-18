import os.path

import numpy as np
import pandas as pd

from CSScriptBuilder import CSScriptBuilder
from ExcelCShapUtil import FieldExcelScript, LNGExcelScript
from ExcelUtil import IsNeedRecordSize, TurnBytesByExcel, GenerateScriptType, GetScriptsName, GetCShapeType
from LanguageUtil import CNLanguage
from LogUtil import ShowLog
from PathUtil import BytesPath, LanguageXlsxPath


# 生成单个字段的二进制文件
def GenerateFieldBytes(excelPath, sheetName, scriptName=None):
    scriptName = GetScriptsName(excelPath, sheetName, scriptName)
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    firstRow = excelData.iloc[0]
    columns_with_c = np.where(firstRow.str.contains('c', case=False))[0]
    firstIndex = columns_with_c[0]
    secondIndex = columns_with_c[1]
    firstValueOldType = str(excelData.iloc[1, firstIndex])
    firstValueType = GetCShapeType(firstValueOldType, True)
    secValueOldType = str(excelData.iloc[2, secondIndex])
    secValueType = GetCShapeType(secValueOldType, True)
    Scripts = CSScriptBuilder()
    data_bytes = TurnBytesByExcel(excelData, 4, 1, IsNeedRecordSize(excelData), GenerateScriptType.FieldType, Scripts)
    FieldExcelScript(scriptName, firstValueType, secValueType, scriptName.lower(), Scripts)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(BytesPath, f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')


def GenerateLNGBytes(scriptName=None):
    if scriptName is None:
        scriptName = f'{os.path.basename(LanguageXlsxPath).split(".")[0]}{CNLanguage}'
    scriptName = f'Table{scriptName}'
    excelData = pd.read_excel(LanguageXlsxPath, sheet_name=CNLanguage, header=None)
    data_bytes = TurnBytesByExcel(excelData, 4, 0, IsNeedRecordSize(excelData), GenerateScriptType.LNGType)
    LNGExcelScript(scriptName, scriptName.lower())
    # 将bytes保存到本地文件
    bytesPath = os.path.join(BytesPath, f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')
