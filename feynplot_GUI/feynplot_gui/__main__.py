# /home/zed/pyfeynmandiagram/feynplot_GUI/feynplot_gui/__main__.py
import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

if __name__ == "__main__":
    # Check if a QApplication instance already exists
    app = QApplication.instance()
    if app is None: # If no instance exists, create a new one
        app = QApplication(sys.argv)
    else: # If an instance exists, just use it
        print("QApplication instance already exists, reusing it.")
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())