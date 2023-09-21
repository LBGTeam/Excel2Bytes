# Excel2Bytes(开发中)
[**Excel2Bytes仓库**](https://github.com/LBGTeam/Excel2Bytes)  

py写的游戏开发用的导表工具。目前支持C#脚本。
## 原理
该工具的原理是将表格数据转换为二进制数据，并生成对应的bytes文件。同时，它还会生成可供访问的C#脚本，使得在游戏中可以通过C#按照二进制字节的方式读取所需的数据。

这个工具的优势在于它可以提高游戏的加载速度和性能。通过将表格数据转换为二进制格式，可以减少文件大小和加载时间。同时，使用C#脚本读取二进制数据可以更高效地访问和处理数据。

该工具目前正在开发中，预计会提供更多功能和优化。敬请期待！  

## 工具配置

首次运行会在当前目录的Config文件夹下生成一个Config.json配置文件，这个文件里面是导表工具的配置。  
这里的配置**后续开发**将支持QT面板进行修改，不用修改文件。  

示例  

	{
	    "IsUpdateAllLNG": true,
	    "TablePath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Table",
	    "BytesPath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Bytes",
	    "ScriptsPath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Scripts",
	    "CorePath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Core",
	    "LNGBytesPath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Bytes",
	    "ResRefFileListPath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\reslist.json",
	    "LanguageXlsxPath": "F:\\MyPrograme\\Excel2Bytes\\Excel2Bytes\\Save\\Table\\Languages.xlsx",
	    "CNLanguage": "cn",
	    "TableLanguageCSName": "Languages",
	    "BytesExportPath": "",
	    "ScriptsExportPath": "",
	    "CoreExportPath": "",
	    "TableRootNamespace": "LBRuntime",
	    "TableResLoadAssembly": "LBUnity",
	    "ResLoadScripts": "ResManager.OpenFile(\"{0}\")",
	    "LanguageKey": [
	        "tw",
	        "en"
	    ],
	    "SupportExcelFormats": [
	        ".xlsx",
	        ".xls"
	    ],
	    "TableSheetInfo": {
	        "ScriptsName": "",
	        "ImportType": "NoneType",
	        "ExtraNamespace": ""
	    }
	}

|字段|描述|
|:--|:--|
|IsUpdateAllLNG|表示是否要更新多语言，如果为False，只有中文语言表会更新，其他的语言不会更新|
|TablePath|表格存放的目录|
|BytesPath|生成的字节文件存放的目录（非项目内路径，后面有项目内的路径配置，会把这里的文件复制到后面配置的项目路径）|
|ScriptsPath|生成的脚本文件存放目录（和BytesPath一样是临时存放目录)|
|CorePath|核心脚本目录，初次导入的时候会生成TableManager等管理脚本存放目录（也是临时存放目录）|
|LNGBytesPath|多语言的字节生成目录，所有的语言生成的字节文件都是一样的名字，会放在与语言页签同样名字的文件夹下，开发者加载的时候处理不同语言访问的字节文件。|
|ResRefFileListPath|收集配置的资源名字的json文件路径（里面存放的都是表里配置的资源的名字）|
|LanguageXlsxPath|多语言的表格路径，这个是自动生成的。<font color=Red>只有处理其他语言显示文字才会修改这个表，这个表的中文页签是会自动更新的</font>|
|CNLanguage|多语言表中文页签的页签名|
|TableLanguageCSName|读取语言的脚本名字，这里不需要带前缀"Table"（如上图配置，游戏中访问语言就是：TableLanguages.Find(10)）|
|BytesExportPath|项目里表格字节文件存放的路径，工具会把临时存放的字节文件复制到这个文件里|
|ScriptsExportPath|项目里表格脚本文件存放的路径，同上|
|CoreExportPath|表格核心脚本存放路径，同上|
|TableRootNamespace|表格脚本所在的程序集名字（把导表生成的脚本都放在这个程序集下）|
|TableResLoadAssembly|脚本加载字节文件的时候需要用到的项目资源加载脚本所在的命名空间|
|ResLoadScripts|加载字节文件用到的项目里的方法|
|LanguageKey|多语言中其他语言的页签名字|
|SupportExcelFormats|表格文件支持的后缀|
|TableSheetInfo|页签文件要包含的信息，扩展使用（正常情况下不要修改，增加需要修改代码以作支持）|

## 表格类型
### 导入类型  

每个表格得每个页签都需要选择一个导入类型，没选择导入类型得页签代表不进行导入。导入类型决定了生成得表格数据得bytes文件和对应得脚本文件。  

类型总览：  

|导入类型|描述|
|:--|:--|  
|FieldType|字段类型，用于配置游戏中动态替换的数据（注：只允许含有c的字段两列，一列是代码访问关键字，一列是值）|  
|FindType|查找类型，用于配置游戏中的数据，根据关键字进行查找对应数据。|  
|LNGType|语言类型，用于存放所有语言的表，这个表工具会自动生成，不需要手动创建|  
|NoExportLNGType|无导入语言类型，用于游戏中固定的文字，非代码访问的，需要玩家自动创建并收集游戏中的文字（注：导表是不会生成脚本和bytes文件，只是为了收集游戏中语言到语言表里）|  
|CustomTypeField|针对此类型表专门做的类型。(注：只允许含有c的字段三列，一列是代码访问关键字，一列是值得类型，一列是值)|   


#### FieldType

字段的导入类型，用于根据字段的关键字来访问对应的值。此类型只允许有两列第一行包含'c'的列（第一行包含'c'代表要导入的数据），一列是代码访问关键字，一列是值。   

示例  

|c|c|  
|:--|:--|  
|ID|text|  
|int|LNGRef|  
|名称|内容|  
|NetworkUnreachable|连接出错，请检查您的网络！|  
|GetServerListFailed|拉取服务器列表失败，请稍后再试！|  
|TipsFormatInitParamFailed|初始化参数请求失败，请检查您的网络！{0}|  

在这个示例中，我们展示了一个普通表格的结构。每一列都有一个对应的数据类型和字段描述。  
在第一行中，我们使用了字符c来表示是否要导入该列的数据。只有含有c的列才会被导入到数据文件中。  
在第二行中，我们列出了每一列的字段名字。这些字段名字用于标识每一列所代表的数据。  
在第三行中，我们指定了每一列数据的类型。这些类型可以是整数(int)、字符串(string)、长整型(long)等。  
在第四行中，我们提供了对每一列所代表的字段的描述。这些描述可以帮助读者更好地理解每一列数据的含义。  
接下来的行中，第一列表示的是我们要搜索的关键字，第二列就是关键字对应的数值


#### FindType

查找的导入类型，用于根据数据的key查找对应的数据，此类型包含'c'的列至少是两列，一列是查找的时候的关键字，后面就是一系列的配置数据了。  

示例  

|c|c||c|  
|:--|:--|:--|:--|  
|ID|Level|des|Exp|  
|int|int|string|long|  
|关键key|等级|描述|经验|  
|1|1|练气|100|  

在这个示例中，我们展示了一个普通表格的结构。每一列都有一个对应的数据类型和字段描述。  
在第一行中，我们使用了字符c来表示是否要导入该列的数据。只有含有c的列才会被导入到数据文件中。  
在第二行中，我们列出了每一列的字段名字。这些字段名字用于标识每一列所代表的数据。  
在第三行中，我们指定了每一列数据的类型。这些类型可以是整数(int)、字符串(string)、长整型(long)等。  
在第四行中，我们提供了对每一列所代表的字段的描述。这些描述可以帮助读者更好地理解每一列数据的含义。  
接下来的行中，我们可以输入对应的数据。在这个示例中，我们输入了一条数据，其中ID为1，等级为1，描述为"练气"，经验为100。  
以上是对普通表格的描述和示例。你可以根据需要调整表格的结构和内容。 

#### LNGType  

这个是语言表类型，是导表工具自动生成的多语言表内的页签用的类型，这个类型的表在生成多语言的时候每页都会生成一个语言的字节文件，游戏可以在加载字节文件里做处理，只需要加载对应语言即可。  

示例  

|c|c|  
|:--|:--|  
|ID|text|  
|uint|string|  
|编号|文本|  
|1|多语言1|  
|2|多语言2|  

这个语言表会自动生成，不需要创建，只需要添加要生成语言的配置即可

#### NoExportLNGType  

这个类型的表也是语言类型表，这个表需要玩家自己收集游戏中不是动态变化的语言，类似Unity的prefab上的语言，导表的时候会把这些语言收集到多语言表中，并且不会生成脚本和字节文件，游戏中开发者只需要通过id访问语言表的字节文件即可。  

示例  

|c|c|  
|:--|:--|  
|ID|text|  
|uint|LNGRef|  
|编号|文本|  
|1|多语言1|  
|2|多语言2|  

#### CustomTypeField  
自定义类型的字段导入类型，这个和字段导入类型差不多，但是要求有效列(第一行含'c')的列必须是三列。  

示例  

|c|c|c|  
|:--|:--|:--|  
|关键字|类型|值|  
|currencyFormatSplit|nt[]|5\|7|10|13|  
|currencyNumSplit|slc\|int|4\|7|10|13|  
|currencyFormatSplitMap|map\|int|string|1:你好\|2:我不好|  
|currencyFormatSplitDic|Dictionary<int,LNGRef>|1:你好\|2:我不好|  

在这个示例中，我们展示了一个多类型表格的结构。每一行都有一个对应的数据类型和字段描述。
在第一行中，我们使用了字符c来表示是否要导入该列的数据。只有含有c的列才会被导入到数据文件中。
在第二行中，我们提供了对每一列所代表的字段的描述。这些描述可以帮助读者更好地理解每一列数据的含义。   
以上是对多类型表格的描述和示例。你可以根据需要调整表格的结构和内容。  

## 支持的数据格式

|类型|写法|描述|  
|:--|:--|--|  
|uint8|1|基础类型|  
|byte|1|基础类型|  
|int|1|基础类型|  
|uint|1|基础类型|  
|float|1|基础类型|  
|double|1|基础类型|  
|bool|false、true或者空|基础类型|  
|long|1|基础类型|  
|ulong|1|基础类型|  
|int64|1|基础类型|  
|uint|64|基础类型|  
|short|1|基础类型|  
|ushort|1|基础类型|  
|string|文本描述|基础类型|  
|基础类型[]|1\|1|3|基础类型的数组|  
|slc\|基础类型|1\|1|3|基础类型的数组|  
|基础类型[][]|1:2:3\|1:2|1:2:3:4|基础类型的二维数组|  
|double_slc\|基础类型|1:2:3\|1:2|1:2:3:4|基础类型的二维数组|  
|map\|基础类型|基础类型|1:2\|3:4|5:6|基础类型的字典|  
|Dictionary<基础类型，基础类型>|1:2\|3:4|5:6|基础类型的字典|  
|LNGRef|这段话多语言|字符串类型，会在多语言表生成，用于游戏语言切换功能|  
|ResName|Icon.png|资源类型，这里会收集表里配置的所有资源，可根据自身需求来获取，Save目录会生成reslist.json，记录了所有的资源|  