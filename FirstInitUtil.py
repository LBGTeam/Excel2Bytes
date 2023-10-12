from CSScriptBuilder import CSScriptBuilder
from ConfigData import Config
from ExcelUtil import DeleteCore, CopyCore


# 首次生成对应的脚本
def FirstGenerateData():
    DeleteCore()
    CreateTableManagerCs()
    CopyCore()


# 生成单个字段的二进制文件
def CreateTableManagerCs():
    script = CSScriptBuilder()
    script.AppendUsing('System.Collections.Generic')
    script.AppendUsing('UnityEngine')
    script.AppendEmptyLine()
    script.BeginNamespace(Config.TableLoadAssembly())
    script.BeginInterface('ITable', 'public')
    script.AppendInterfaceMethod('Dispose')
    script.EndInterface()
    script.AppendEmptyLine()
    script.BeginClass('TableManager', 'public static')
    script.AppendField('s_Inited', 'bool', 'private static')
    script.AppendField('s_Cached', 'List<ITable>', 'private static', 'new List<ITable>()')
    # 添加方法
    script.AppendEmptyLine()
    script.BeginStaticMethod("Add", parameters="ITable table")
    script.AppendLine("Debug.Assert(s_Inited, \"add but TableManager not init \");")
    script.AppendLine("s_Cached.Add(table);")
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginStaticMethod("Remove", parameters="ITable table")
    script.AppendLine("Debug.Assert(s_Inited, \"remove but TableManager not init\");")
    script.AppendLine("if (s_Cached.Remove(table))")
    script.BeginBrace()
    script.AppendLine("table.Dispose();")
    script.EndBrace()
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginStaticMethod("Init")
    script.AppendLine("Debug.Assert(!s_Inited, \"TableManager already init\");")
    script.AppendLine("s_Inited = true;")
    script.EndMethod()
    script.AppendEmptyLine()
    script.BeginStaticMethod("UnInit")
    script.AppendLine("Debug.Assert(s_Inited, \"TableManager not init\");")
    script.AppendLine("s_Inited = false;")
    script.AppendLine("foreach (var table in s_Cached.ToArray())")
    script.BeginBrace()
    script.AppendLine("table.Dispose();")
    script.EndBrace()
    script.AppendLine("s_Cached.Clear();")
    script.EndMethod()
    script.EndClass()
    script.EndNamespace()
    script.GenerateScript('TableManager', Config.CorePath())
