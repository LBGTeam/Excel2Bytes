import os
import re
import shutil
import struct
import sys

import numpy as np

from CSScriptBuilder import CSScriptBuilder
from FileUtil import CopyFile
from LanguageUtil import GetLanguageKey
from LogUtil import ShowLog
from GlobalUtil import GenerateScriptType, IgnoreSizeTypes
from ResRefUtil import AddResRef
from ConfigData import Config
from TableLoadUtil import TableDataIsNone

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


def GetFieldName(fieldType, fieldName):
    if 'LNGRef' in fieldType:
        return f'{fieldName}Id'
    else:
        return fieldName


# 读取bytes的时候的类型
def GetCShapeType(fieldType, isBase=False):
    if 'map' in fieldType.lower():
        pattern = r"map\|(\w+)\|(\w+)"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = GetCShapeType(matches[0][0], isBase)
        type2 = GetCShapeType(matches[0][1], isBase)
        return f'Dictionary<{type1}, {type2}>' if isBase else f'Dictionary<{type1}, {type2}>'
    if 'dictionary' in fieldType.lower():
        pattern = r"dictionary<(\w+),(\w+)>"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = GetCShapeType(matches[0][0], isBase)
        type2 = GetCShapeType(matches[0][1], isBase)
        return f'Dictionary<{type1}, {type2}>' if isBase else f'Dictionary<{type1}, {type2}>'
    if 'double_slc' in fieldType.lower():
        return f'{GetCShapeType(fieldType.replace("double_slc|", ""))}[][]'
    if '[][]' in fieldType:
        return f'{GetCShapeType(fieldType[:-4])}[][]'
    if 'slc' in fieldType.lower():
        return f'{GetCShapeType(fieldType.replace("slc|", ""))}[]'
    if '[]' in fieldType:
        return f'{GetCShapeType(fieldType[:-2])}[]'
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
    return fieldType


def GetDataProperty(fieldType, fieldName, script):
    valueType = GetCShapeType(fieldType)
    if 'LNGRef' in fieldType:
        tableLanguageCSName = Config.TableLanguageCSName()
        script.AppendLine(f"private uint {GetFieldName(fieldType, fieldName)};")
        script.AppendLine(f"public {valueType} {fieldName} => Table{tableLanguageCSName}"
                          f".Find({GetFieldName(fieldType, fieldName)});")
    elif 'ResName' in fieldType:
        script.AppendLine(f"public string {fieldName};")
    else:
        script.AppendLine(f"public {GetCShapeType(fieldType, True)} {fieldName};")


def GetFieldInitDataSize(fieldType, script):
    if '[][]' in fieldType or 'double_slc' in fieldType:
        script.AppendLine(f'reader.ReadUInt16();')
        script.AppendLine(f'var valueRow = reader.ReadUInt16();')
        script.BeginFor(f'var valueRowIndex = 0; valueRowIndex < valueRow; valueRowIndex++')
        script.AppendLine(f'var valueCol = reader.ReadUInt16();')
        script.BeginFor(f'var valueColIndex = 0; valueColIndex < valueCol; valueColIndex++')
        if '[][]' in fieldType:
            GetFieldInitDataSizeBase(fieldType[:-4], script)
        else:
            GetFieldInitDataSizeBase(fieldType.replace('double_slc|', ''), script)
        script.EndFor()
        script.EndFor()
    elif 'map' in fieldType or 'dictionary' in fieldType:
        if 'map' in fieldType:
            pattern = r"map\|(\w+)\|(\w+)"
        else:
            pattern = r"dictionary<(\w+),(\w+)>"
        matches = re.findall(pattern, fieldType, flags=re.IGNORECASE)
        type1 = matches[0][0]
        type2 = matches[0][1]
        script.AppendLine(f"var count = reader.ReadUInt16();")
        script.BeginFor(f"var index = 0; index < count; index++")
        GetFieldInitDataSizeBase(type1, script)
        GetFieldInitDataSizeBase(type2, script)
        script.EndFor()
    elif '[]' in fieldType.lower() or 'slc' in fieldType.lower():
        script.AppendLine(f'var count = reader.ReadUInt16();')
        script.BeginFor(f'var arrIndex = 0; arrIndex < count; arrIndex++')
        if '[]' in fieldType.lower():
            GetFieldInitDataSizeBase(fieldType[:-2], script)
        else:
            GetFieldInitDataSizeBase(fieldType.replace('slc|', ''), script)
        script.EndFor()
    else:
        GetFieldInitDataSizeBase(fieldType, script)


def GetFieldInitDataSizeBase(fieldType, script):
    if 'LNGRef' in fieldType:
        script.AppendLine(f"reader.ReadUInt32();")
    elif 'ResName' in fieldType or 'string' in fieldType:
        script.AppendLine(f"reader.ReadBytes(reader.ReadUInt16());")
    else:
        script.AppendLine(f"reader.{GetTypeRead(fieldType)}();")


def GetDataAssignment(fieldType, fieldName, script, isInitLNG=True):
    if 'LNGRef' in fieldType or 'ResName' in fieldType:
        script.BeginBrace()
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
    if 'LNGRef' in fieldType or 'ResName' in fieldType:
        script.EndBrace()


def GetDataAssignmentBase(fieldType, fieldName, script, isNewField=False, isInitLNG=True):
    leftFieldName = fieldName if not isNewField else f"var {fieldName}"
    if 'LNGRef' in fieldType:
        script.AppendLine(f"var LNGId = reader.ReadUInt32();")
        if isInitLNG:
            tableLanguageCSName = Config.TableLanguageCSName()
            script.AppendLine(f"{leftFieldName} = Table{tableLanguageCSName}.Find(LNGId);")
        else:
            script.AppendLine(f"{leftFieldName}Id = LNGId;")
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
def TurnBytesByExcel(excelName, excelTableData, startRow, startColumn, generateScriptType, script=None):
    rows = excelTableData[startRow:]
    firstRow = excelTableData[0]
    if len(firstRow) < 2:
        ShowLog(f'表格数据不完整, 请检查表格: {excelName}')
        sys.exit(1)
    valueOldType = str(excelTableData[2][1])
    dataBytes = b''
    allSize = 0
    scInit = CSScriptBuilder()
    scField = CSScriptBuilder()
    scProperty = CSScriptBuilder()
    index = 0
    for row in rows:
        tBytes = b''
        tSize = 0
        fieldType = row[1]
        if generateScriptType == GenerateScriptType.FieldType:
            GetFieldProperty(valueOldType, row[0], index, script)
        elif generateScriptType == GenerateScriptType.CustomTypeField:
            GetDataAssignment(fieldType, f'm_{row[0]}', scInit)
            GetCustomField(fieldType, row[0], scField)
            GetCustomFieldProperty(fieldType, row[0], scProperty)
        # 将数据添加到 Data1 对象中
        for col_index in range(startColumn, len(row)):
            if generateScriptType != GenerateScriptType.CustomTypeField:
                fieldType = excelTableData[2][col_index]
            fieldValue = row[col_index]
            data = TurnBytes(fieldType, fieldValue)
            tBytes += data[0]
            tSize += data[1]
        if generateScriptType not in IgnoreSizeTypes:
            tSize += typeMap[SizeMap][1]
            dataBytes += struct.pack(f"{typeMap[SizeMap][0]}", tSize)
        dataBytes += tBytes
        allSize += tSize
        index += 1
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
def IsNeedRecordSize(excelTableData):
    for index, colum in excelTableData[0].items():  # 修改为第一行（索引为0）
        fieldType = excelTableData[2][index]  # 修改为当前行（索引为1）的当前列
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
        if not TableDataIsNone(fieldValue):
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
        if not TableDataIsNone(fieldValue):
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
        if not TableDataIsNone(fieldValue):
            tCon = len(str(fieldValue).split('|'))
            for singleValue in str(fieldValue).split('|'):
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
        if not TableDataIsNone(fieldValue):
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
        if TableDataIsNone(fieldValue):
            fieldValue = 0
        else:
            fieldValue = GetBaseType(fieldType)(fieldValue)
        return struct.pack(fmt, fieldValue), size
    elif fieldType == 'string' or fieldType == 'ResName':
        if TableDataIsNone(fieldValue):
            fieldValue = ''
        if fieldType == 'ResName':
            AddResRef(fieldValue)
        value = (str(fieldValue).rstrip('\0')).encode('utf-8')

        strSize = len(value)
        print(str(fieldValue), strSize)
        byte = struct.pack(f"{typeMap[SizeMap][0]}", strSize) + struct.pack(f'{strSize}s', value)
        size = typeMap[SizeMap][1] + strSize

        return byte, size
    elif fieldType == 'LNGRef':
        if TableDataIsNone(fieldValue):
            struct.pack('I', 0), 4
        return struct.pack('I', GetLanguageKey(fieldValue)), 4
    else:
        sys.stderr.write(f"Error: Unknown field type '{fieldType}'\n")
        input("Press Enter to exit...")
        sys.exit()


def GetBaseType(fieldType):
    return baseTypes.get(fieldType, fieldType)


def CopyScripts():
    scriptsExportPath = Config.ScriptsExportPath()
    if scriptsExportPath.isspace() or len(scriptsExportPath) == 0 or not os.path.exists(scriptsExportPath):
        return
    for root, dirs, files in os.walk(Config.ScriptsPath()):
        for file in files:
            if os.path.exists(os.path.join(scriptsExportPath, file)):
                os.remove(os.path.join(scriptsExportPath, file))
            CopyFile(os.path.join(Config.ScriptsPath(), file), os.path.join(scriptsExportPath, file))


def DeleteScripts():
    for root, dirs, files in os.walk(Config.ScriptsPath()):
        for file in files:
            if os.path.exists(os.path.join(Config.ScriptsPath(), file)):
                os.remove(os.path.join(Config.ScriptsPath(), file))


def CopyBytes():
    bytesExportPath = Config.BytesExportPath()
    if bytesExportPath.isspace() or len(bytesExportPath) == 0 or not os.path.exists(bytesExportPath):
        return
    for root, dirs, files in os.walk(Config.BytesPath()):
        for file in files:
            if os.path.exists(os.path.join(bytesExportPath, file)):
                os.remove(os.path.join(bytesExportPath, file))
            CopyFile(os.path.join(Config.BytesPath(), file), os.path.join(bytesExportPath, file))
        for tDir in dirs:
            if os.path.exists(os.path.join(bytesExportPath, tDir)):
                shutil.rmtree(os.path.join(bytesExportPath, tDir))
            shutil.copytree(os.path.join(Config.BytesPath(), tDir), os.path.join(bytesExportPath, tDir))


def DeleteBytes():
    for root, dirs, files in os.walk(Config.BytesPath()):
        for tFile in files:
            if os.path.exists(os.path.join(Config.BytesPath(), tFile)):
                os.remove(os.path.join(Config.BytesPath(), tFile))
        for tDir in dirs:
            if os.path.exists(os.path.join(Config.BytesPath(), tDir)):
                shutil.rmtree(os.path.join(Config.BytesPath(), tDir))


def CopyCore():
    for root, dirs, files in os.walk(Config.CorePath()):
        for file in files:
            if os.path.exists(os.path.join(Config.ScriptsPath(), file)):
                os.remove(os.path.join(Config.ScriptsPath(), file))
            CopyFile(os.path.join(Config.CorePath(), file), os.path.join(Config.CoreExportPath(), file))
        for tDir in dirs:
            if os.path.exists(os.path.join(Config.ScriptsPath(), tDir)):
                shutil.rmtree(os.path.join(Config.ScriptsPath(), tDir))
            shutil.copytree(os.path.join(Config.CorePath(), tDir), os.path.join(Config.CoreExportPath(), tDir))


def DeleteCore():
    for root, dirs, files in os.walk(Config.CorePath()):
        for tFile in files:
            if os.path.exists(os.path.join(Config.CoreExportPath(), tFile)):
                os.remove(os.path.join(Config.CoreExportPath(), tFile))
        for tDir in dirs:
            if os.path.exists(os.path.join(Config.CoreExportPath(), tDir)):
                shutil.rmtree(os.path.join(Config.CoreExportPath(), tDir))
