# Excel2Bytes(开发中)
py写的游戏开发用的导表工具。目前支持C#脚本。
## 原理
该工具的原理是将表格数据转换为二进制数据，并生成对应的bytes文件。同时，它还会生成可供访问的C#脚本，使得在游戏中可以通过C#按照二进制字节的方式读取所需的数据。

这个工具的优势在于它可以提高游戏的加载速度和性能。通过将表格数据转换为二进制格式，可以减少文件大小和加载时间。同时，使用C#脚本读取二进制数据可以更高效地访问和处理数据。

该工具目前正在开发中，预计会提供更多功能和优化。敬请期待！

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