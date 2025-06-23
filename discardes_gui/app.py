# gui/app.py
import sys
from PyQt6.QtWidgets import QApplication
from .mainwindow import FeynmanDiagramApp # 从新的 mainwindow 模块导入 FeynmanDiagramApp

def main():
    """应用程序主入口点"""
    app = QApplication(sys.argv)
    window = FeynmanDiagramApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()