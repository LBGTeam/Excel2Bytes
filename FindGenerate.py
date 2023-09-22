import os

from ExcelCShapUtil import FindExcelScript
from ExcelUtil import TurnBytesByExcel
from LogUtil import ShowLog
from GlobalUtil import GenerateScriptType
from ConfigData import Config
from TableLoadUtil import LoadExcel


def GenerateFindBytes(excelPath, sheetName, scriptName, extraNamespace):
    excelTableData = LoadExcel(excelPath, sheetName)
    data_bytes = TurnBytesByExcel(os.path.basename(excelPath), excelTableData, 4, 0, GenerateScriptType.FindType)
    pair = []
    for index, col in enumerate(excelTableData[0]):
        kv = [excelTableData[1][index], excelTableData[2][index]]
        pair.append(kv)
    FindExcelScript(scriptName, pair, scriptName.lower(), extraNamespace)
    # 将bytes保存到本地文件
    bytesPath = os.path.join(Config.BytesPath(), f'{scriptName.lower()}.bytes')
    with open(bytesPath, 'wb') as f:
        f.write(data_bytes)
    ShowLog(f'生成二进制文件: {bytesPath}')
