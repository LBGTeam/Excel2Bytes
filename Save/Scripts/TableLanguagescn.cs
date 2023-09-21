using System.Collections.Generic;
using System.IO;
using System.Text;
using LBUnity;
using LBRuntime;

namespace LBRuntime.Table.Structure
{
	public sealed class TableLanguagescn : ITable
	{
		
		private static TableLanguagescn s_Instance;
		private Dictionary<uint, string> m_Cached;
		private Dictionary<uint, ulong> m_Entries;
		private BinaryReader reader;
		
		public static TableLanguagescn Instance => s_Instance ??= new TableLanguagescn();
		
		public TableLanguagescn()
		{
			TableManager.Add(this);
			m_Cached = new Dictionary<uint, string>();
			m_Entries = new Dictionary<uint, ulong>();
			//这里需要走自己资源加载字节文件
			reader = new BinaryReader(ResManager.OpenFile("tablelanguagescn.bytes")), Encoding.UTF8);
			ulong allOffset = 0;
			while (true)
			{
				try
				{
					var key = reader.ReadUInt32();
					if (key == 0)
					{
						break;
					}
					var offset = reader.ReadUInt16();
					m_Entries.Add(key, allOffset + 4);
					allOffset += 4 + 2 + (ulong)offset;
					reader.BaseStream.Position += offset;
					//判断是否读取完毕
					if (reader.BaseStream.Position >= reader.BaseStream.Length)
					{
						break;
					}
				}
				catch (Exception e)
				{
					reader.Close();
					break;
				}
			}
		}
		
		public void Dispose()
		{
			TableManager.Remove(this);
			m_Cached.Clear();
			reader.Close();
		}
		
		public static string Find(uint id, bool throwException = true)
		{
			if (id <= 0)
			{
				return string.Empty;
			}
			if (Instance.m_Cached.TryGetValue(id, out var value))
			{
				return value;
			}
			if (Instance.m_Entries.TryGetValue(id, out var offset))
			{
				Instance.reader.BaseStream.Position = (long)Instance.m_Entries[id];
				value = Instance.reader.ReadString();
				Instance.m_Cached.Add(id, value);
				return value;
			}
			if (throwException)
			{
				throw new Exception($"Can not find TableLanguagescn id: <built-in function id>");
			}
			return id.ToString();
		}
		
	}
}