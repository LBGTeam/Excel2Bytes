using System.Collections.Generic;
using UnityEngine;

namespace LBRuntime.Table.Loader
{
	public interface ITable
	{
		void Dispose();
	}
	
	public static class TableManager
	{
		private static bool s_Inited;
		private static List<ITable> s_Cached = new List<ITable>();
		
		public void Add(ITable table)
		{
			Debug.Assert(s_Inited, "add but TableManager not init ");
			s_Cached.Add(table);
		}
		
		public void Remove(ITable table)
		{
			Debug.Assert(s_Inited, "remove but TableManager not init");
			if (s_Cached.Remove(table))
			{
				table.Dispose();
			}
		}
		
		public void Init()
		{
			Debug.Assert(!s_Inited, "TableManager already init");
			s_Inited = true;
		}
		
		public void UnInit()
		{
			Debug.Assert(s_Inited, "TableManager not init");
			s_Inited = false;
			foreach (var table in s_Cached)
			{
				table.Dispose();
			}
			s_Cached.Clear();
		}
	}
}