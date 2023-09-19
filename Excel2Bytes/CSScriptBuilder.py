import os

from PathUtil import ScriptsPath


class CSScriptBuilder(list):
    BlackNum = 0

    def Append(self, message):
        if self.BlackNum > 0:
            self.append('\t' * self.BlackNum + message)
        else:
            self.append(message)

    def AppendEnter(self):
        self.Append('\n')

    def AppendLine(self, message):
        if len(self) > 0:
            self.append('\n')
        if self.BlackNum > 0:
            self.append('\t' * self.BlackNum + message)
        else:
            self.append(message)

    def AppendEmptyLine(self):
        self.AppendLine('')

    def AppendUsing(self, namespace):
        self.AppendLine(f'using {namespace};')

    def BeginNamespace(self, namespace):
        self.AppendLine(f'namespace {namespace}')
        self.BeginBrace()

    def EndNamespace(self):
        self.EndBrace()

    def BeginClass(self, className, modifier="public", superclass=None):
        if superclass is not None:
            self.AppendLine(f'{modifier} class {className} : {superclass}')
        else:
            self.AppendLine(f'{modifier} class {className}')
        self.BeginBrace()

    def EndClass(self):
        self.EndBrace()

    def BeginStruct(self, structName, modifier="public"):
        self.AppendLine(f'{modifier} struct {structName}')
        self.BeginBrace()

    def EndStruct(self):
        self.EndBrace()

    def BeginEnum(self, enumName, modifier="public"):
        self.AppendLine(f'{modifier} enum {enumName}')
        self.BeginBrace()

    def EndEnum(self):
        self.EndBrace()

    def AppendEnumField(self, fieldName, fieldValue):
        self.AppendLine(f'{fieldName} = {fieldValue},')

    def BeginInterface(self, interfaceName, modifier="public"):
        self.AppendLine(f'{modifier} interface {interfaceName}')
        self.BeginBrace()

    def EndInterface(self):
        self.EndBrace()

    def AppendInterfaceMethod(self, methodName, returnType='void', parameters=''):
        self.AppendLine(f'{returnType} {methodName}({parameters});')

    def AppendField(self, propertyName, propertyType, modifier="public", init=''):
        if len(init) > 0:
            self.AppendLine(f'{modifier} {propertyType} {propertyName} = {init};')
        else:
            self.AppendLine(f'{modifier} {propertyType} {propertyName};')

    def AppendProperty(self, propertyName, propertyType, field=None, modifier="public"):
        if field is not None:
            self.AppendLine(f'{modifier} {propertyType} {propertyName} => {field};')
        else:
            self.AppendLine(f'{modifier} {propertyType} {propertyName} {{ get; set; }}')

    def BeginProperty(self, propertyName, propertyType, modifier="public"):
        self.AppendLine(f'{modifier} {propertyType} {propertyName}')
        self.BeginBrace()

    def EndProperty(self):
        self.EndBrace()

    def BeginMethod(self, methodName, modifier="public", returnType='void', parameters=''):
        self.AppendLine(f'{modifier} {returnType} {methodName}({parameters})')
        self.BeginBrace()

    def BeginConstructionMethod(self, methodName, modifier="public", parameters=''):
        self.AppendLine(f'{modifier} {methodName}({parameters})')
        self.BeginBrace()

    def EndMethod(self):
        self.EndBrace()

    def BeginIf(self, condition):
        self.AppendLine(f'if ({condition})')
        self.BeginBrace()

    def BeginElif(self, condition):
        self.AppendLine(f'else if ({condition})')
        self.BeginBrace()

    def EndIf(self):
        self.EndBrace()

    def BeginWhile(self, condition):
        self.AppendLine(f'while ({condition})')
        self.BeginBrace()

    def EndWhile(self):
        self.EndBrace()

    def BeginTry(self):
        self.AppendLine('try')
        self.BeginBrace()

    def EndTry(self):
        self.EndBrace()

    def BeginCatch(self, exceptionType):
        self.AppendLine(f'catch ({exceptionType})')
        self.BeginBrace()

    def BeginForEach(self, name, collection, singleType='var'):
        self.AppendLine(f'foreach ({singleType} {name} in {collection})')
        self.BeginBrace()

    def EndForEach(self):
        self.EndBrace()

    def BeginFor(self, condition):
        self.AppendLine(f'for ({condition})')
        self.BeginBrace()

    def EndFor(self):
        self.EndBrace()

    def BeginForRange(self, name, start, end):
        self.AppendLine(f'for (int {name} = {start}; {name} < {end}; {name}++)')
        self.BeginBrace()

    def EndForRange(self):
        self.EndBrace()

    def EndCatch(self):
        self.EndBrace()

    def BeginBlank(self):
        self.BlackNum += 1

    def EndBlank(self):
        self.BlackNum -= 1

    def BeginBrace(self):
        self.AppendLine('{')
        self.BeginBlank()

    def EndBrace(self):
        self.EndBlank()
        self.AppendLine('}')

    def BeginRegion(self, regionName):
        self.AppendLine(f'#region {regionName}')
        self.AppendEmptyLine()

    def EndRegion(self):
        self.AppendEmptyLine()
        self.AppendLine('#endregion')
        self.AppendEmptyLine()

    def ToString(self):
        return ''.join(self)

    def GenerateScript(self, fileName, isDefPath=True):
        fileName = fileName.replace('.cs', '')
        if isDefPath:
            fileName = os.path.join(ScriptsPath, fileName)
        with open(f'{fileName}.cs', 'w', encoding='utf-8') as f:
            f.write(self.ToString())
