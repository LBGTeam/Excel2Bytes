import os

import pandas as pd

from LogUtil import ShowLog


def TableDataIsNone(value):
    if value is None:
        return True
    elif len(str(value)) <= 0:
        return True
    elif str(value).lower() in ['na', 'nan', '']:
        return True
    return False


def LoadExcel(fileName, sheetName):
    df = pd.read_excel(fileName, sheet_name=sheetName, header=None, index_col=None, na_values=['NaN'])
    # 删除整行都是NaN值的行
    df.dropna(axis=0, how='all', inplace=True)
    # 删除整列都是NaN值的列
    df.dropna(axis=1, how='all', inplace=True)
    # 导入第一行中含有字母"c"的列，不区分大小写
    df = df.loc[:, df.iloc[0].str.contains('c', case=False) | df.iloc[0].isna()]
    ShowLog(f'加载表格: {fileName} - {sheetName}')
    return df.values.tolist()


def LoadCSV(fileName):
    df = pd.read_csv(fileName, header=None, index_col=None, na_values=['NaN'])
    # 删除整行都是NaN值的行
    df.dropna(axis=0, how='all', inplace=True)
    # 删除整列都是NaN值的列
    df.dropna(axis=1, how='all', inplace=True)
    # 导入第一行中含有字母"c"的列，不区分大小写
    df = df.loc[:, df.iloc[0].str.contains('c', case=False)]
    ShowLog(f'加载表格: {fileName}')
    return df.values.tolist()


def GetSheetNames(fileName):
    if fileName.endswith('.xlsx'):
        return pd.ExcelFile(fileName).sheet_names
    elif fileName.endswith('.csv'):
        return [os.path.basename(fileName).split('.')[0]]
    else:
        ShowLog(f'不支持的文件格式: {fileName}')


def LoadTableData(fileName, sheetName=None):
    if fileName.endswith('.xlsx'):
        return LoadExcel(fileName, sheetName)
    elif fileName.endswith('.csv'):
        return LoadCSV(fileName)
    else:
        ShowLog(f'不支持的文件格式: {fileName}')
