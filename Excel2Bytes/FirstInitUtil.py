import os

from CSScriptBuilder import CSScriptBuilder
from ExcelUtil import TableLoadAssembly
from GlobalUtil import ScriptsPath


# 首次生成对应的脚本
def FirstGenerateData():
    CreateTableManagerCs()


# 生成单个字段的二进制文件
def CreateTableManagerCs():
    script = CSScriptBuilder()
    script.AppendUsing('System.Collections.Generic')
    script.AppendUsing('UnityEngine')
    script.BeginNamespace(TableLoadAssembly)
    script.BeginInterface('ITable', 'public')
    script.AppendInterfaceMethod('Dispose')
    script.EndInterface()
    script.AppendEmptyLine()
    script.BeginClass('TableManager', 'public static')
    script.AppendField('s_Inited', 'bool', 'private static')
    script.AppendField('s_Cached', 'List<ITable>', 'private static', 'new List<ITable>()')
    # 添加方法
    script.AppendEmptyLine()
    script.BeginMethod("Add", parameters="ITable table")
    script.AppendLine("Debug.Assert(s_Inited, \"add but TableManager not init \");")
    script.AppendLine("s_Cached.Add(table);")
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginMethod("Remove", parameters="ITable table")
    script.AppendLine("Debug.Assert(s_Inited, \"remove but TableManager not init\");")
    script.AppendLine("if (s_Cached.Remove(table))")
    script.BeginBrace()
    script.AppendLine("table.Dispose();")
    script.EndBrace()
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginMethod("Init")
    script.AppendLine("Debug.Assert(!s_Inited, \"TableManager already init\");")
    script.AppendLine("s_Inited = true;")
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginMethod("UnInit")
    script.AppendLine("Debug.Assert(s_Inited, \"TableManager not init\");")
    script.AppendLine("s_Inited = false;")
    script.AppendLine("foreach (var table in s_Cached)")
    script.BeginBrace()
    script.AppendLine("table.Dispose();")
    script.EndBrace()
    script.AppendLine("s_Cached.Clear();")
    script.EndMethod()
    script.EndClass()
    script.EndNamespace()
    script.GenerateScript(os.path.join(ScriptsPath, 'TableManager'))
