import os
import sys

from LogUtil import ShowLog


def ExePath():
    if hasattr(sys, 'frozen'):
        path_sys = os.path.dirname(sys.executable)
        return path_sys  # 使用pyinstaller打包后的exe目录
    path_py = os.path.dirname(__file__)
    return path_py  # 没打包前的py目录


def CopyFile(source, target):
    if os.path.exists(target):
        os.remove(target)
    if os.path.exists(source):
        with open(source, 'rb') as f:
            with open(target, 'wb') as t:
                t.write(f.read())
        ShowLog(f'复制文件: {source} -> {target}')
    else:
        ShowLog(f'文件不存在: {source}')

