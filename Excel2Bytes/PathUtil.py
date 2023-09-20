import os

from FileUtil import ExePath
from LogUtil import ShowLog

SavePath = os.path.join(ExePath(), 'Save')
TablePath = os.path.join(SavePath, 'Table')
BytesPath = os.path.join(SavePath, 'Bytes')
ScriptsPath = os.path.join(SavePath, 'Scripts')
JsonsPath = os.path.join(SavePath, 'Jsons')
ResRefFileListPath = os.path.join(SavePath, 'reslist.json')
LanguageXlsxPath = os.path.join(TablePath, 'Languages.xlsx')
BytesExportPath = 'E:\GitPrograme\TW\client\client\Assets\_Resources\Config\Table'
ScriptsExportPath = 'E:\GitPrograme\TW\client\client\Assets\_Scripts\Table\Structure'


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
