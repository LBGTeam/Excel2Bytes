import ast
import sys

from GenerateUtil import ExportAllData, ExportExtraLNG, FirstExportProject, ExportData

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-a':
            ExportAllData()
        elif sys.argv[1] == '-e':
            ExportExtraLNG()
        elif sys.argv[1] == '-c':
            tableNames = ast.literal_eval(sys.argv[2])
            ExportData(False, False, tableNames)
    else:
        FirstExportProject()
