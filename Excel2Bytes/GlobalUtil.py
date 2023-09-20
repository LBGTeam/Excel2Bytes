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


SavePath = os.path.join(ExePath(), 'Save')
TablePath = os.path.join(SavePath, 'Table')
BytesPath = os.path.join(SavePath, 'Bytes')
LNGBytesPath = os.path.join(SavePath, 'Bytes')
ScriptsPath = os.path.join(SavePath, 'Scripts')
JsonsPath = os.path.join(SavePath, 'Jsons')
ResRefFileListPath = os.path.join(SavePath, 'reslist.json')
TableConfigJsonPath = os.path.join(JsonsPath, 'TableConfig.json')
LanguageXlsxPath = os.path.join(TablePath, 'Languages.xlsx')
BytesExportPath = 'E:\GitPrograme\TW\client\client\Assets\_Resources\Config\Table'
ScriptsExportPath = 'E:\GitPrograme\TW\client\client\Assets\_Scripts\Table\Structure'
SupportExcelFormats = ['.xlsx', '.xls']
TableSheetInfo = {'ScriptsName': '', 'ImportType': GenerateScriptType.NoneType.name, 'ExtraNamespace': ''}

IsUpdateLng = True
CNLanguage = 'cn'
LanguageKey = ['tw', 'en']
LanguageDict = {}
TableLanguageCSName = 'Languages'

TAbleRootNamespace = 'LBRuntime'
TableAssembly = f'{TAbleRootNamespace}.Table'
TableLoadAssembly = f'{TAbleRootNamespace}.Table.Loader'
TableStructAssembly = f'{TAbleRootNamespace}.Table.Structure'
TableResLoadAssembly = 'LBUnity'


IgnoreSizeTypes = [
    GenerateScriptType.FieldType,
    GenerateScriptType.LNGType,
    GenerateScriptType.CustomTypeField,
]


def InitFileDir():
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
    if not os.path.exists(JsonsPath):
        os.mkdir(JsonsPath)
        ShowLog('创建文件夹: Jsons')


def GetScriptsName(excelPath, sheetName, scriptName=None):
    if scriptName is None:
        baseName = os.path.basename(excelPath).split(".")[0]
        if baseName.lower() == sheetName.lower():
            scriptName = baseName
        else:
            scriptName = f'{baseName}{sheetName}'
    return f'Table{scriptName}'
