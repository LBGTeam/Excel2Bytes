import os
import re
import struct
import sys
from enum import Enum

import numpy as np
import pandas as pd

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
    CustomType = 3


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
    if fieldType.replace('[]', '') in typeMap:
        return fieldType
    return fieldType


def GetDataProperty(fieldType, fieldName, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' in fieldType:
        script.AppendLine(f"private uint {fieldName}Id;")
        script.AppendLine(f"public {valueType} {fieldName} => Table{TableLanguageCSName}.Find({fieldName}Id);")
    else:
        script.AppendLine(f"public {valueType} {fieldName};")


def GetDataAssignment(fieldType, fieldName, script):
    if '[][]' in fieldType:
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)}[{fieldName}Size][];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        script.AppendLine(f"var {fieldName}Size2 = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName}[{fieldName}Index] = new {GetCShapeType(fieldType)}[{fieldName}Size2];")
        script.BeginFor(f"var {fieldName}Index2 = 0; {fieldName}Index2 < {fieldName}Size2; {fieldName}Index2++")
        GetDataAssignmentBase(fieldType[:-4], f"{fieldName}[{fieldName}Index][{fieldName}Index2]", script)
        script.EndFor()
        script.EndFor()
    elif '[]' in fieldType:
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)}[{fieldName}Size];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        GetDataAssignmentBase(fieldType[:-2], f"{fieldName}[{fieldName}Index]", script)
        script.EndFor()
    elif 'slc' in fieldType.lower():
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)}[{fieldName}Size];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        GetDataAssignmentBase(fieldType.replace('slc|', ''), f"{fieldName}[{fieldName}Index]", script)
        script.EndFor()
    elif 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new Dictionary<{GetCShapeType(type1)}, {GetCShapeType(type2)}>();")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        GetDataAssignmentBase(type1, f"var {fieldName}key", script)
        GetDataAssignmentBase(type2, f"var {fieldName}value", script)
        script.AppendLine(f"{fieldName}.Add({fieldName}key, {fieldName}value);")
        script.EndFor()
    elif 'dictionary' in fieldType.lower():
        pattern = r"dictionary\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new Dictionary<{GetCShapeType(type1)}, {GetCShapeType(type2)}>();")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        GetDataAssignmentBase(type1, f"var {fieldName}key", script)
        GetDataAssignmentBase(type2, f"var {fieldName}value", script)
        script.AppendLine(f"{fieldName}.Add({fieldName}key, {fieldName}value);")
        script.EndFor()
    elif 'double_slc' in fieldType.lower():
        script.AppendLine(f"var {fieldName}Size = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName} = new {GetCShapeType(fieldType)}[{fieldName}Size][];")
        script.BeginFor(f"var {fieldName}Index = 0; {fieldName}Index < {fieldName}Size; {fieldName}Index++")
        script.AppendLine(f"var {fieldName}Size2 = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName}[{fieldName}Index] = new {GetCShapeType(fieldType)}[{fieldName}Size2][];")
        script.BeginFor(f"var {fieldName}Index2 = 0; {fieldName}Index2 < {fieldName}Size2; {fieldName}Index2++")
        script.AppendLine(f"var {fieldName}Size3 = reader.ReadUInt16();")
        script.AppendLine(f"{fieldName}[{fieldName}Index][{fieldName}Index2] = new {GetCShapeType(fieldType)}[{fieldName}Size3];")
        script.BeginFor(f"var {fieldName}Index3 = 0; {fieldName}Index3 < {fieldName}Size3; {fieldName}Index3++")
        GetDataAssignmentBase(fieldType.replace('double_slc|', ''), f"{fieldName}[{fieldName}Index][{fieldName}Index2][{fieldName}Index3]", script)
        script.EndFor()
        script.EndFor()
        script.EndFor()
    else:
        GetDataAssignmentBase(fieldType, fieldName, script)


def GetDataAssignmentBase(fieldType, fieldName, script):
    if 'LNGRef' in fieldType:
        script.AppendLine(f"{fieldName}Id = reader.ReadUInt32();")
    if 'ResName' in fieldType:
        script.AppendLine(f"{fieldName} = reader.ReadString();")
    else:
        script.AppendLine(f"{fieldName} = reader.{GetTypeRead(fieldType)}();")


def GetFieldProperty(fieldType, fieldName, fieldValue, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' in fieldType:
        script.AppendLine(
            f"public static {valueType} {fieldName} => TableLanguage.Find(Instance.ReadData({fieldValue}));")
    if 'ResName' in fieldType:
        script.AppendLine(
            f"public static {valueType} {fieldName} => Instance.ReadData({fieldValue});")
    else:
        script.AppendLine(
            f"public static {valueType} {fieldName} => Instance.ReadData({fieldValue});")


# 将Excel数据转换为二进制
def TurnBytesByExcel(excelData, startRow, startColumn, isNeedRecordSize, generateScriptType, script=None):
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
    for index, row in rows:
        tBytes = b''
        tSize = 0
        if generateScriptType == GenerateScriptType.FieldType:
            GetFieldProperty(valueOldType, row[firstIndex], allSize, script)
        # 将数据添加到 Data1 对象中
        for col_index in range(startColumn, len(row)):
            if 'c' in str(excelData.iloc[0, col_index]):  # 判断是否需要的数据
                fieldType = excelData.iloc[2, col_index]
                fieldValue = row[col_index]
                data = TurnBytes(fieldType, fieldValue)
                tBytes += data[0]
                tSize += data[1]
        if generateScriptType != GenerateScriptType.FieldType and generateScriptType != GenerateScriptType.LNGType:
            tSize += typeMap[SizeMap][1]
            dataBytes += struct.pack(f"{typeMap[SizeMap][0]}", tSize)
        dataBytes += tBytes
        allSize += tSize
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
        singleType = fieldType[:-2]
        pSize = 0
        pByte = b''
        for singleValue in fieldValue.split('|'):
            qSize = 0
            qByte = b''
            for value in singleValue.split(':'):
                sByte, sSize = SingleTurnBytes(singleType, value)
                qByte += sByte
                qSize += sSize
            pByte += struct.pack(f"{typeMap[SizeMap][0]}", qSize) + qByte
            pSize += typeMap[SizeMap][1] + qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", pSize) + pByte
        pSize += typeMap[SizeMap][1]
        return byte, pSize
    if '[]' in fieldType:
        singleType = fieldType[:-2]
        size = 0
        tByte = b''
        if not pd.isna(fieldValue):
            for singleValue in fieldValue.split('|'):
                sByte, sSize = SingleTurnBytes(singleType, singleValue)
                tByte += sByte
                size += sSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", size) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'slc' in fieldType.lower():
        singleType = fieldType.replace('slc|', '')
        size = 0
        tByte = b''
        for singleValue in fieldValue.split('|'):
            sByte, sSize = SingleTurnBytes(singleType, singleValue)
            tByte += sByte
            size += sSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", size) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        size = 0
        tByte = b''
        if not pd.isna(fieldValue):
            for singleValue in fieldValue.split('|'):
                qByte, qSize = SingleTurnBytes(type1, singleValue.split(':')[0])
                tByte += qByte
                size += qSize
                qByte, qSize = SingleTurnBytes(type2, singleValue.split(':')[1])
                tByte += qByte
                size += qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", size) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'dictionary' in fieldType.lower():
        pattern = r"dictionary\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        size = 0
        tByte = b''
        for singleValue in fieldValue.split('|'):
            qByte, qSize = SingleTurnBytes(type1, singleValue.split(':')[0])
            tByte += qByte
            size += qSize
            qByte, qSize = SingleTurnBytes(type2, singleValue.split(':')[1])
            tByte += qByte
            size += qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", size) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    if 'double_slc' in fieldType.lower():
        singleType = fieldType.replace('double_slc|', '')
        size = 0
        tByte = b''
        for singleValue in fieldValue.split('|'):
            qSize = 0
            qByte = b''
            for value in singleValue.split(':'):
                sByte, sSize = SingleTurnBytes(singleType, value)
                qByte += sByte
                qSize += sSize
            tByte += struct.pack(f"{typeMap[SizeMap][0]}", qSize) + qByte
            size += typeMap[SizeMap][1] + qSize
        byte = struct.pack(f"{typeMap[SizeMap][0]}", size) + tByte
        size += typeMap[SizeMap][1]
        return byte, size
    else:
        return SingleTurnBytes(fieldType, fieldValue)


# 将单个数据转换为二进制
def SingleTurnBytes(fieldType, fieldValue):
    if fieldType in typeMap:
        fmt, size = typeMap[fieldType]
        return struct.pack(fmt, GetBaseType(fieldType)(fieldValue)), size
    elif fieldType == 'string':
        if pd.isna(fieldValue):
            byte = struct.pack(f"{typeMap[SizeMap][0]}", 0)
            size = typeMap[SizeMap][1]
            return byte, size
        value = fieldValue.encode('utf-8')
        strSize = len(str(value))
        byte = struct.pack(f"{typeMap[SizeMap][0]}", strSize) + struct.pack(f'{strSize}s', value)
        size = typeMap[SizeMap][1] + strSize
        return byte, size
    elif fieldType == 'LNGRef':
        if pd.isna(fieldValue):
            struct.pack('I', 0), 4
        return struct.pack('I', GetLanguageKey(fieldValue)), 4
    elif 'ResName' in fieldType:
        if pd.isna(fieldValue):
            byte = struct.pack(f"{typeMap[SizeMap][0]}", 0)
            size = typeMap[SizeMap][1]
            return byte, size
        value = fieldValue.encode('utf-8')
        strSize = len(str(value))
        AddResRef(fieldValue)
        byte = struct.pack(f"{typeMap[SizeMap][0]}", strSize) + struct.pack(f'{strSize}s', value)
        size = typeMap[SizeMap][1] + strSize
        return byte, size
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


def CopyBytes():
    for root, dirs, files in os.walk(BytesPath):
        for file in files:
            CopyFile(os.path.join(BytesPath, file), os.path.join(BytesExportPath, file))


def GetScriptsName(excelPath, sheetName, scriptName=None):
    if scriptName is None:
        baseName = os.path.basename(excelPath).split(".")[0]
        if baseName.lower() == sheetName.lower():
            scriptName = baseName
        else:
            scriptName = f'{baseName}{sheetName}'
    return f'Table{scriptName}'
