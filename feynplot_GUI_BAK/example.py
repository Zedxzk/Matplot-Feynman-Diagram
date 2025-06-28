# /home/zed/pyfeynmandiagram/feynplot_GUI/feynplot_gui/__main__.py
import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow # 确保这里是相对导入

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())