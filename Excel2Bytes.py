import sys

from GenerateUtil import ExportAllData, ExportExtraLNG, FirstExportProject

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-a':
            ExportAllData()
        elif sys.argv[1] == '-e':
            ExportExtraLNG()
    else:
        FirstExportProject()
