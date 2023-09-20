import os
import re
import struct
import sys
from enum import Enum

import numpy as np
import pandas as pd

from CSScriptBuilder import CSScriptBuilder
from FileUtil import CopyFile
from LanguageUtil import GetLanguageKey, TableLanguageCSName
from LogUtil import ShowLog
from PathUtil import ScriptsPath, ScriptsExportPath, BytesPath, BytesExportPath
from ResRefUtil import AddResRef

TAbleRootNamespace = 'ZHRuntime'
TableAssembly = f'{TAbleRootNamespace}.Table'
TableLoadAssembly = f'{TAbleRootNamespace}.Table.Loader'
TableStructAssembly = f'{TAbleRootNamespace}.Table.Structure'
TableResLoadAssembly = 'ZHUnity'

SizeMap = 'ushort'
OfferMap = 'ulong'

typeMap = {
        'uint8': ('B', 1),
        'byte': ('b', 1),
        'int': ('i', 4),
        'float': ('f', 4),
        'double': ('d', 8),
        'bool': ('?', 1),
        'long': ('q', 8),
        'short': ('h', 2),
        'ushort': ('H', 2),
        'uint': ('I', 4),
        'ulong': ('Q', 8),
        'int64': ('q', 8),
        'uint64': ('Q', 8)
    }


baseTypes = {
        'uint8': int,
        'byte': int,
        'int': int,
        'float': float,
        'double': float,
        'bool': bool,
        'long': int,
        'short': int,
        'ushort': int,
        'uint': int,
        'ulong': int,
        'int64': int,
        'uint64': int
    }


def GetTypeRead(fieldType):
    if fieldType == 'int':
        return 'ReadInt32'
    elif fieldType == 'float':
        return 'ReadSingle'
    elif fieldType == 'double':
        return 'ReadDouble'
    elif fieldType == 'bool':
        return 'ReadBoolean'
    elif fieldType == 'long':
        return 'ReadInt64'
    elif fieldType == 'ulong':
        return 'ReadUInt64'
    elif fieldType == 'short':
        return 'ReadInt16'
    elif fieldType == 'ushort':
        return 'ReadUInt16'
    elif fieldType == 'uint':
        return 'ReadUInt32'
    elif fieldType == 'byte':
        return 'ReadByte'
    elif fieldType == 'uint8':
        return 'ReadByte'
    elif fieldType == 'int64':
        return 'ReadInt64'
    elif fieldType == 'uint64':
        return 'ReadUInt64'
    elif fieldType == 'string':
        return 'ReadString'
    elif fieldType == 'LNGRef':
        return 'ReadUInt32'
    elif fieldType == 'ResName':
        return 'ReadString'


class GenerateScriptType(Enum):
    FieldType = 0
    FindType = 1
    LNGType = 2
    CustomTypeField = 3
    CustomType = 4


IgnoreSizeTypes = [
    GenerateScriptType.FieldType,
    GenerateScriptType.LNGType,
    GenerateScriptType.CustomTypeField,
]


def GetFieldName(fieldType, fieldName):
    if 'LNGRef' in fieldType:
        return f'{fieldName}Id'
    else:
        return fieldName


# 读取bytes的时候的类型
def GetCShapeType(fieldType, isBase=False):
    if 'LNGRef' in fieldType:
        if isBase:
            return fieldType.replace('LNGRef', 'uint')
        return fieldType.replace('LNGRef', 'string')
    if 'ResName' in fieldType:
        return fieldType.replace('ResName', 'string')
    if 'int64' in fieldType:
        return fieldType.replace('int64', 'long')
    if 'uint64' in fieldType:
        return fieldType.replace('uint64', 'ulong')
    if 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        replacement = r"Dictionary<\1,\2>"
        return re.sub(pattern, replacement, fieldType, flags=re.IGNORECASE)
    if 'dictionary' in fieldType.lower():
        pattern = r"dictionary\|(\w+)\|(\w+)"
        replacement = r"Dictionary<\1,\2>"
        return re.sub(pattern, replacement, fieldType, flags=re.IGNORECASE)
    if 'slc' in fieldType.lower():
        return f'{GetCShapeType(fieldType.replace("slc|", ""))}[]'
    if 'double_slc' in fieldType.lower():
        return f'{GetCShapeType(fieldType.replace("double_slc|", ""))}[][]'
    if fieldType.replace('[]', '') in typeMap:
        return fieldType
    return fieldType


def GetDataProperty(fieldType, fieldName, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' in fieldType:
        script.AppendLine(f"private uint {GetFieldName(fieldType, fieldName)};")
        script.AppendLine(f"public {valueType} {fieldName} => Table{TableLanguageCSName}"
                          f".Find({GetFieldName(fieldType, fieldName)});")
    elif 'ResName' in fieldType:
        script.AppendLine(f"public string {fieldName};")
    else:
        script.AppendLine(f"public {GetCShapeType(fieldType, True)} {fieldName};")


def GetDataAssignment(fieldType, fieldName, script, isInitLNG=True):
    if '[][]' in fieldType:
        singleType = fieldType[:-4]
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f'var {fieldName}Row = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)[:-4]}[{fieldName}Row][];")
        script.BeginFor(f"var {fieldName}RowIndex = 0; {fieldName}RowIndex < {fieldName}Row; {fieldName}RowIndex++")
        script.AppendLine(f'var {fieldName}Col = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName}[{fieldName}RowIndex] = new {GetCShapeType(fieldType)[:-4]}[{fieldName}Col];")
        script.BeginFor(f"var {fieldName}ColIndex = 0; {fieldName}ColIndex < {fieldName}Col; {fieldName}ColIndex++")
        GetDataAssignmentBase(singleType, f"{fieldName}[{fieldName}RowIndex][{fieldName}ColIndex]", script, False, isInitLNG)
        script.EndFor()
        script.EndFor()
    elif 'double_slc' in fieldType.lower():
        singleType = fieldType.replace('double_slc|', '')
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f'var {fieldName}Row = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)[:-4]}[{fieldName}Row][];")
        script.BeginFor(f"var {fieldName}RowIndex = 0; {fieldName}RowIndex < {fieldName}Row; {fieldName}RowIndex++")
        script.AppendLine(f'var {fieldName}Col = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName}[{fieldName}RowIndex] = new {GetCShapeType(fieldType)[:-4]}[{fieldName}Col];")
        script.BeginFor(f"var {fieldName}ColIndex = 0; {fieldName}ColIndex < {fieldName}Col; {fieldName}ColIndex++")
        GetDataAssignmentBase(singleType, f"{fieldName}[{fieldName}RowIndex][{fieldName}ColIndex]", script, False, isInitLNG)
        script.EndFor()
        script.EndFor()
    elif '[]' in fieldType:
        script.AppendLine(f'var {fieldName}Count = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)[:-2]}[{fieldName}Count];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Count; {fieldName}Index++")
        GetDataAssignmentBase(fieldType[:-2], f"{fieldName}[{fieldName}Index]", script, False, isInitLNG)
        script.EndFor()
    elif 'slc' in fieldType.lower():
        script.AppendLine(f'var {fieldName}Count = reader.ReadUInt16();')
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)[:-2]}[{fieldName}Count];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Count; {fieldName}Index++")
        GetDataAssignmentBase(fieldType.replace('slc|', ''), f"{fieldName}[{fieldName}Index]", script, False, isInitLNG)
        script.EndFor()
    elif 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        script.AppendLine(f"var {fieldName}Count = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new Dictionary<{GetCShapeType(type1)}, {GetCShapeType(type2)}>();")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Count; {fieldName}Index++")
        GetDataAssignmentBase(type1, f"{fieldName}Key", script, True, isInitLNG)
        GetDataAssignmentBase(type2, f"{fieldName}Value", script, True, isInitLNG)
        script.AppendLine(f"{fieldName}.Add({fieldName}Key, {fieldName}Value);")
        script.EndFor()
    elif 'dictionary' in fieldType.lower():
        pattern = r"dictionary<(\w+),(\w+)>"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        script.AppendLine(f"var {fieldName}Count = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new Dictionary<{GetCShapeType(type1)}, {GetCShapeType(type2)}>();")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Count; {fieldName}Index++")
        GetDataAssignmentBase(type1, f"{fieldName}Key", script, True, isInitLNG)
        GetDataAssignmentBase(type2, f"{fieldName}Value", script, True, isInitLNG)
        script.AppendLine(f"{fieldName}.Add({fieldName}Key, {fieldName}Value);")
        script.EndFor()
    else:
        GetDataAssignmentBase(fieldType, fieldName, script, False, isInitLNG)


def GetDataAssignmentBase(fieldType, fieldName, script, isNewField=False, isInitLNG=True):
    leftFieldName = fieldName if not isNewField else f"var {fieldName}"
    if 'LNGRef' in fieldType:
        script.AppendLine(f"var LNGId = reader.ReadUInt32();")
        if isInitLNG:
            script.AppendLine(f"{leftFieldName} = Table{TableLanguageCSName}.Find(LNGId);")
    elif 'ResName' in fieldType or 'string' in fieldType:
        script.AppendLine(f"var tSize = reader.ReadUInt16();")
        script.AppendLine(f"var tBytes = reader.ReadBytes(tSize);")
        script.AppendLine(f"{leftFieldName} = Encoding.UTF8.GetString(tBytes);")
    else:
        script.AppendLine(f"{leftFieldName} = reader.{GetTypeRead(fieldType)}();")


def GetFieldProperty(fieldType, fieldName, fieldValue, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' == fieldType:
        script.AppendLine(
            f"public static {valueType} {fieldName} => Instance.ReadData({fieldValue});")
    elif 'ResName' == fieldType:
        script.AppendLine(
            f"public static {valueType} {fieldName} => Instance.ReadData({fieldValue});")
    else:
        script.AppendLine(
            f"public static {valueType} {fieldName} => Instance.ReadData({fieldValue});")


def GetCustomField(fieldType, fieldName, script):
    valueType = GetCShapeType(fieldType)
    script.AppendLine(f"public {valueType} m_{fieldName};")


def GetCustomFieldProperty(fieldType, fieldName, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' in fieldType:
        script.AppendLine(f"public static {valueType} {fieldName} => Instance.m_{fieldName};")
    elif 'ResName' in fieldType:
        script.AppendLine(f"public static {valueType} {fieldName} => Instance.m_{fieldName};")
    else:
        script.AppendLine(f"public static {valueType} {fieldName} => Instance.m_{fieldName};")


# 将Excel数据转换为二进制
def TurnBytesByExcel(excelData, startRow, startColumn, generateScriptType, script=None):
    rows = excelData.iloc[startRow:].iterrows() if startRow > 0 else excelData.iterrows()
    firstRow = excelData.iloc[0]
    columns_with_c = np.where(firstRow.str.contains('c', case=False))[0]
    if len(columns_with_c) < 2:
        ShowLog(f'表格数据不完整, 请检查表格: {excelData}')
        sys.exit(1)
    firstIndex = columns_with_c[0]
    secondIndex = columns_with_c[1]
    valueOldType = str(excelData.iloc[2, secondIndex])
    dataBytes = b''
    allSize = 0
    scInit = CSScriptBuilder()
    scField = CSScriptBuilder()
    scProperty = CSScriptBuilder()
    for index, row in rows:
        tBytes = b''
        tSize = 0
        fieldType = row[secondIndex]
        if generateScriptType == GenerateScriptType.FieldType:
            GetFieldProperty(valueOldType, row[firstIndex], allSize, script)
        elif generateScriptType == GenerateScriptType.CustomTypeField:
            GetDataAssignment(fieldType, f'm_{row[firstIndex]}', scInit)
            GetCustomField(fieldType, row[firstIndex], scField)
            GetCustomFieldProperty(fieldType, row[firstIndex], scProperty)
        # 将数据添加到 Data1 对象中
        for col_index in range(startColumn, len(row)):
            if 'c' in str(excelData.iloc[0, col_index]):  # 判断是否需要的数据
                if generateScriptType != GenerateScriptType.CustomTypeField:
                    fieldType = excelData.iloc[2, col_index]
                fieldValue = row[col_index]
                data = TurnBytes(fieldType, fieldValue)
                tBytes += data[0]
                tSize += data[1]
        if generateScriptType not in IgnoreSizeTypes:
            tSize += typeMap[SizeMap][1]
            dataBytes += struct.pack(f"{typeMap[SizeMap][0]}", tSize)
        dataBytes += tBytes
        allSize += tSize
    if generateScriptType == GenerateScriptType.CustomTypeField:
        script.BeginMethod('InitData', 'public', 'void')
        script.AppendEnter()
        for sc in scInit:
            script.Append(sc)
        script.EndMethod()
        script.AppendEnter()
        for sc in scField:
            script.Append(sc)
        script.AppendEnter()
        for sc in scProperty:
            script.Append(sc)
    return dataBytes


# 是否需要记录大小(方法：如果不是基础类型都是要记录的)
def IsNeedRecordSize(excelData):
    for index, colum in excelData.iloc[0].items():  # 修改为第一行（索引为0）
        # 将数据添加到 Data1 对象中
        if 'c' in str(colum).lower():
            fieldType = excelData.iloc[2, index]  # 修改为当前行（索引为1）的当前列
            if fieldType in typeMap or fieldType == 'LNGRef':  # 修改为当前行（索引为2）的当前列
                return False
    return True


# 将Excel数据转换为二进制
def TurnBytes(fieldType, fieldValue):
    if '[][]' in fieldType:
        singleType = fieldType[:-4]
        pSize = 0
        pByte = b''
        maxRow = 0
        for singleValue in fieldValue.split('|'):
            qSize = 0
            qByte = b''
            maxRow += 1
            maxCol = len(singleValue.split(':'))
            for value in singleValue.split(':'):
                sByte, sSize = SingleTurnBytes(singleType, value)
                qByte += sByte
                qSize += sSize
            pByte += struct.pack(f"{typeMap[SizeMap][0]}", maxCol) + qByte
            pSize += (typeMap[SizeMap][1] * 2) + qSize
        byte = (struct.pack(f"{typeMap[SizeMap][0]}", pSize) + struct.pack(f"{typeMap[SizeMap][0]}", maxRow)
                + pByte)
        pSize += (typeMap[SizeMap][1] * 2)
        return byte, pSize
    if 'double_slc' in fieldType.lower():
        singleType = fieldType.replace('double_slc|', '')
        pSize = 0
        pByte = b''
        maxRow = 0
        maxCol = 0
        for singleValue in fieldValue.split('|'):
            qSize = 0
            qByte = b''
            maxRow += 1
            maxCol = max(maxCol, len(singleValue.split(':')))
            for value in singleValue.split(':'):
                sByte, sSize = SingleTurnBytes(singleType, value)
                qByte += sByte
                qSize += sSize
            pByte += struct.pack(f"{typeMap[SizeMap][0]}", maxCol) + qByte
            pSize += (typeMap[SizeMap][1] * 2) + qSize
        byte = (struct.pack(f"{typeMap[SizeMap][0]}", pSize) + struct.pack(f"{typeMap[SizeMap][0]}", maxRow)
                + pByte)
        pSize += (typeMap[SizeMap][1] * 2)
        return byte, pSize
    if '[]' in fieldType:
        singleType = fieldType[:-2]
        size = 0
        tByte = b''
        maxCount = 0
        if not pd.isna(fieldValue):
            maxCount = len(fieldValue.split('|'))
            for singleValue in fieldValue.split('|'):
                sByte, sSize = SingleTurnBytes(singleType, singleValue)
                tByte += sByte
                size += sSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", maxCount) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'slc' in fieldType.lower():
        singleType = fieldType.replace('slc|', '')
        size = 0
        tByte = b''
        maxCount = 0
        if not pd.isna(fieldValue):
            maxCount = len(fieldValue.split('|'))
            for singleValue in fieldValue.split('|'):
                sByte, sSize = SingleTurnBytes(singleType, singleValue)
                tByte += sByte
                size += sSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", maxCount) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        size = 0
        tByte = b''
        tCon = 0
        if not pd.isna(fieldValue):
            tCon = len(fieldValue.split('|'))
            for singleValue in fieldValue.split('|'):
                array = singleValue.split(':')
                qByte, qSize = SingleTurnBytes(type1, array[0])
                tByte += qByte
                size += qSize
                qByte, qSize = SingleTurnBytes(type2, array[1])
                tByte += qByte
                size += qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", tCon) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'dictionary' in fieldType.lower():
        pattern = r"dictionary<(\w+),(\w+)>"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        size = 0
        tByte = b''
        tCon = 0
        if not pd.isna(fieldValue):
            tCon = len(fieldValue.split('|'))
            for singleValue in fieldValue.split('|'):
                array = singleValue.split(':')
                qByte, qSize = SingleTurnBytes(type1, array[0])
                tByte += qByte
                size += qSize
                qByte, qSize = SingleTurnBytes(type2, array[1])
                tByte += qByte
                size += qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", tCon) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    else:
        return SingleTurnBytes(fieldType, fieldValue)


# 将单个数据转换为二进制
def SingleTurnBytes(fieldType, fieldValue):
    if fieldType in typeMap:
        fmt, size = typeMap[fieldType]
        return struct.pack(fmt, GetBaseType(fieldType)(fieldValue)), size
    elif fieldType == 'string' or fieldType == 'ResName':
        if pd.isna(fieldValue):
            fieldValue = ' '
        if fieldType == 'ResName':
            AddResRef(fieldValue)
        value = fieldValue.encode('utf-8')
        strSize = len(str(value))
        byte = struct.pack(f"{typeMap[SizeMap][0]}", strSize) + struct.pack(f'{strSize}s', value)
        size = typeMap[SizeMap][1] + strSize
        return byte, size
    elif fieldType == 'LNGRef':
        if pd.isna(fieldValue):
            struct.pack('I', 0), 4
        return struct.pack('I', GetLanguageKey(fieldValue)), 4
    else:
        sys.stderr.write(f"Error: Unknown field type '{fieldType}'\n")
        input("Press Enter to exit...")
        sys.exit()


def GetBaseType(fieldType):
    return baseTypes.get(fieldType, fieldType)


def CopyScripts():
    for root, dirs, files in os.walk(ScriptsPath):
        for file in files:
            CopyFile(os.path.join(ScriptsPath, file), os.path.join(ScriptsExportPath, file))


def DeleteScripts():
    for root, dirs, files in os.walk(ScriptsPath):
        for file in files:
            os.remove(os.path.join(ScriptsPath, file))


def CopyBytes():
    for root, dirs, files in os.walk(BytesPath):
        for file in files:
            CopyFile(os.path.join(BytesPath, file), os.path.join(BytesExportPath, file))


def DeleteBytes():
    for root, dirs, files in os.walk(BytesPath):
        for file in files:
            os.remove(os.path.join(BytesPath, file))


def GetScriptsName(excelPath, sheetName, scriptName=None):
    if scriptName is None:
        baseName = os.path.basename(excelPath).split(".")[0]
        if baseName.lower() == sheetName.lower():
            scriptName = baseName
        else:
            scriptName = f'{baseName}{sheetName}'
    return f'Table{scriptName}'
