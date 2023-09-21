import os

import pandas as pd

from GlobalUtil import ConfigJsonPath, GetScriptsName, TableConfigJsonPath
from JsonUtil import LoadConfigJsonData, SaveJsonData, LoadTableJsonData


class ConfigData:
    config = LoadConfigJsonData()

    def ModifyConfigJsonData(self, key, value):
        self.config[key] = value
        SaveJsonData(ConfigJsonPath, ConfigData.config)

    def GetOrSetConfigJsonData(self, key, value=None):
        if value is not None:
            self.config[key] = value
            SaveJsonData(ConfigJsonPath, ConfigData.config)
        return self.config[key]

    def IsUpdateAllLNG(self, value=None):
        return self.GetOrSetConfigJsonData('IsUpdateAllLNG', value)

    def TablePath(self, value=None):
        return self.GetOrSetConfigJsonData('TablePath', value)

    def BytesPath(self, value=None):
        return self.GetOrSetConfigJsonData('BytesPath', value)

    def ScriptsPath(self, value=None):
        return self.GetOrSetConfigJsonData('ScriptsPath', value)

    def CorePath(self, value=None):
        return self.GetOrSetConfigJsonData('CorePath', value)

    def LNGBytesPath(self, value=None):
        return self.GetOrSetConfigJsonData('LNGBytesPath', value)

    def ResRefFileListPath(self, value=None):
        return self.GetOrSetConfigJsonData('ResRefFileListPath', value)

    def LanguageXlsxPath(self, value=None):
        return self.GetOrSetConfigJsonData('LanguageXlsxPath', value)

    def CNLanguage(self, value=None):
        return self.GetOrSetConfigJsonData('CNLanguage', value)

    def TableLanguageCSName(self, value=None):
        return self.GetOrSetConfigJsonData('TableLanguageCSName', value)

    def BytesExportPath(self, value=None):
        return self.GetOrSetConfigJsonData('BytesExportPath', value)

    def ScriptsExportPath(self, value=None):
        return self.GetOrSetConfigJsonData('ScriptsExportPath', value)

    def CoreExportPath(self, value=None):
        return self.GetOrSetConfigJsonData('CoreExportPath', value)

    def TableRootNamespace(self, value=None):
        return self.GetOrSetConfigJsonData('TableRootNamespace', value)

    def TableAssembly(self):
        return f"{self.TableRootNamespace()}.Table"

    def TableLoadAssembly(self):
        return f"{self.TableRootNamespace()}.Table.Loader"

    def TableStructAssembly(self):
        return f"{self.TableRootNamespace()}.Table.Structure"

    def TableResLoadAssembly(self, value=None):
        return self.GetOrSetConfigJsonData('TableResLoadAssembly', value)

    def LanguageKey(self, value=None):
        return self.GetOrSetConfigJsonData('LanguageKey', value)

    def SupportExcelFormats(self, value=None):
        return self.GetOrSetConfigJsonData('SupportExcelFormats', value)

    def TableSheetInfo(self, value=None):
        return self.GetOrSetConfigJsonData('TableSheetInfo', value)


Config = ConfigData()


class TableConfigData:
    tableConfig = LoadTableJsonData()

    def InitTableJsonData(self):
        fileLists = os.listdir(Config.TablePath())
        for fileName in fileLists:
            if any([fileName.endswith(ext) for ext in Config.SupportExcelFormats()]):
                filePath = os.path.join(Config.TablePath(), fileName)
                workbook = pd.ExcelFile(filePath)
                for sheetName in workbook.sheet_names:
                    for info in Config.TableSheetInfo().keys():
                        self.GetOrSetTableJsonData(fileName, sheetName, info)
                    scriptName = self.ScriptsName(fileName, sheetName)
                    if scriptName.isspace() or len(scriptName) == 0 or scriptName is None:
                        self.ScriptsName(fileName, sheetName, GetScriptsName(filePath, sheetName))

    def ModifyTableJsonData(self, fileName, sheetName, info, value):
        self.tableConfig[fileName][sheetName][info] = value
        SaveJsonData(TableConfigJsonPath, TableConfig.tableConfig)

    def GetOrSetTableJsonData(self, fileName, sheetName, info, value=None):
        if fileName not in self.tableConfig.keys():
            self.tableConfig[fileName] = {}
            self.tableConfig[fileName][sheetName] = {}
            self.tableConfig[fileName][sheetName][info] = Config.TableSheetInfo()[info]
            SaveJsonData(TableConfigJsonPath, TableConfig.tableConfig)
        elif sheetName not in self.tableConfig[fileName].keys():
            self.tableConfig[fileName][sheetName] = {}
            self.tableConfig[fileName][sheetName][info] = Config.TableSheetInfo()[info]
            SaveJsonData(TableConfigJsonPath, TableConfig.tableConfig)
        elif info not in self.tableConfig[fileName][sheetName].keys() and value is None:
            self.tableConfig[fileName][sheetName][info] = Config.TableSheetInfo()[info]
            SaveJsonData(TableConfigJsonPath, TableConfig.tableConfig)
        if value is not None:
            self.tableConfig[fileName][sheetName][info] = value
            SaveJsonData(TableConfigJsonPath, TableConfig.tableConfig)
        return self.tableConfig[fileName][sheetName][info]

    def ScriptsName(self, fileName, sheetName, value=None):
        return self.GetOrSetTableJsonData(fileName, sheetName, "ScriptsName", value)

    def ImportType(self, fileName, sheetName, value=None):
        return self.GetOrSetTableJsonData(fileName, sheetName, "ImportType", value)

    def ExtraNamespace(self, fileName, sheetName, value=None):
        return self.GetOrSetTableJsonData(fileName, sheetName, "ExtraNamespace", value)

    def items(self):
        return self.tableConfig.items()


TableConfig = TableConfigData()
