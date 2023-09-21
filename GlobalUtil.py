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


def GetScriptsName(excelPath, sheetName, scriptName=None):
    if scriptName is None:
        baseName = os.path.basename(excelPath).split(".")[0]
        if baseName.lower() == sheetName.lower():
            scriptName = baseName
        else:
            scriptName = f'{baseName}{sheetName}'
    return f'Table{scriptName}'
