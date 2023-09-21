import os
from enum import Enum

from FileUtil import ExePath
from LogUtil import ShowLog


class GenerateScriptType(Enum):
    NoneType = 0
    FieldType = 1
    FindType = 2
    LNGType = 3
    NoExportLNGType = 4
    CustomTypeField = 5
    CustomType = 6


ConfigPath = os.path.join(ExePath(), 'Config')
ConfigJsonPath = os.path.join(ConfigPath, 'Config.json')
TableConfigJsonPath = os.path.join(ConfigPath, 'TableConfig.json')
SavePath = os.path.join(ExePath(), 'Save')
TablePath = os.path.join(SavePath, 'Table')
BytesPath = os.path.join(SavePath, 'Bytes')
CorePath = os.path.join(SavePath, 'Core')
LNGBytesPath = os.path.join(SavePath, 'Bytes')
ScriptsPath = os.path.join(SavePath, 'Scripts')
ResRefFileListPath = os.path.join(SavePath, 'reslist.json')
LanguageXlsxPath = os.path.join(TablePath, 'Languages.xlsx')

LanguageDict = {}


IgnoreSizeTypes = [
    GenerateScriptType.FieldType,
    GenerateScriptType.LNGType,
    GenerateScriptType.CustomTypeField,
]


def InitFileDir():
    if not os.path.exists(ConfigPath):
        os.mkdir(ConfigPath)
        ShowLog('创建文件夹: Config')
    if not os.path.exists(SavePath):
        os.mkdir(SavePath)
        ShowLog('创建文件夹: Save')
    if not os.path.exists(TablePath):
        os.mkdir(TablePath)
        ShowLog('创建文件夹: Table')
    if not os.path.exists(BytesPath):
        os.mkdir(BytesPath)
        ShowLog('创建文件夹: Bytes')
    if not os.path.exists(ScriptsPath):
        os.mkdir(ScriptsPath)
        ShowLog('创建文件夹: Scripts')
    if not os.path.exists(CorePath):
        os.mkdir(CorePath)
        ShowLog('创建文件夹: Core')


def GetScriptsName(excelPath, sheetName, scriptName=None):
    if scriptName is None:
        baseName = os.path.basename(excelPath).split(".")[0]
        if baseName.lower() == sheetName.lower():
            scriptName = baseName
        else:
            scriptName = f'{baseName}{sheetName}'
    return f'Table{scriptName}'
