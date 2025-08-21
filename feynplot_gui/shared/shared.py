import os
import sys

def resource_path(relative_path):
    """
    获取应用程序资源文件的绝对路径。
    它会移除传入路径中的所有 '../'，以确保路径是相对于
    应用程序的根目录（打包后为 _MEIPASS，开发时为脚本目录）。
    """
    # 移除路径开头的所有 '../'
    if hasattr(sys, '_MEIPASS'):
        while relative_path.startswith('../'):
            relative_path = relative_path[3:]
        # 当程序被 PyInstaller 打包时
        base_path = sys._MEIPASS
    else:
        # 当程序作为普通 Python 脚本运行时
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)