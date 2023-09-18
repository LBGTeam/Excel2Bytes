import os

import pandas as pd

from ExcelCShapUtil import FindExcelScript
from ExcelUtil import TurnBytesByExcel, IsNeedRecordSize, GenerateScriptType, GetScriptsName
from LogUtil import ShowLog
from PathUtil import BytesPath


def GenerateFindBytes(excelPath, sheetName, scriptName=None):
    scriptName = GetScriptsName(excelPath, sheetName, scriptName)
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    isNeedSize = IsNeedRecordSize(excelData)
    data_bytes = TurnBytesByExcel(excelData, 4, 0, isNeedSize, GenerateScriptType.FindType)
    # 获取第一行包含'c'的列
    filteredColumns = excelData.columns[excelData.iloc[0].fillna('').str.contains('c', case=False)]
    pair = []
    for index, col in enumerate(filteredColumns):
        kv = [excelData.iloc[1, col], excelData.iloc[2, col]]
        pair.append(kv)
    FindExcelScript(scriptName, pair, scriptName.lower())
    # 将bytes保存到本地文件
    bytesPath = os.path.join(BytesPath, f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')