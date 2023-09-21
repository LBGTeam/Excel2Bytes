import os

import pandas as pd

from ExcelCShapUtil import FindExcelScript
from ExcelUtil import TurnBytesByExcel
from LogUtil import ShowLog
from GlobalUtil import BytesPath, GenerateScriptType


def GenerateFindBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelData = pd.read_excel(excelPath, sheet_name=sheetName, header=None)
    data_bytes = TurnBytesByExcel(excelData, 4, 0, GenerateScriptType.FindType)
    # 获取第一行包含'c'的列
    filteredColumns = excelData.columns[excelData.iloc[0].fillna('').str.contains('c', case=False)]
    pair = []
    for index, col in enumerate(filteredColumns):
        kv = [excelData.iloc[1, col], excelData.iloc[2, col]]
        pair.append(kv)
    FindExcelScript(scriptName, pair, scriptName.lower(), extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(BytesPath, f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')
