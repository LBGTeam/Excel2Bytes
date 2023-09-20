import os

from FindGenerate import GenerateFindBytes
from ExcelUtil import CopyScripts, CopyBytes, DeleteScripts, DeleteBytes
from FieldGenerate import GenerateFieldBytes, GenerateLNGBytes, GenerateFindFieldBytes
from LanguageUtil import InitLanguage, SaveLanguage, TableLanguageCSName
from PathUtil import InitFileDir, TablePath
from ResRefUtil import SaveResList


def InitTable():
    InitFileDir()
    InitLanguage()


def DeleteFile():
    DeleteScripts()
    DeleteBytes()


def CopyExportFiles():
    CopyScripts()
    CopyBytes()


if __name__ == '__main__':
    InitTable()
    DeleteFile()
    # GenerateFieldBytes(os.path.join(TablePath, 'Text.xlsx'), "System")
    # GenerateFieldBytes(os.path.join(TablePath, 'ResName.xlsx'), "ResName", "ResName2")
    # GenerateFieldBytes(os.path.join(TablePath, 'ResName.xlsx'), "ArrayResName")
    GenerateFindFieldBytes(os.path.join(TablePath, 'Global.xlsx'), "Global", "Global2")
    # GenerateFindBytes(os.path.join(TablePath, 'Level.xlsx'), "Level", "Level2")
    # GenerateFieldBytes(os.path.join(TablePath, 'Text.xlsx'), "SystemArray")
    GenerateLNGBytes(TableLanguageCSName)
    SaveLanguage()
    SaveResList()
    CopyExportFiles()
    # CreateTableManagerCs()

