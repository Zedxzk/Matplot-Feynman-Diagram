# /home/zed/pyfeynmandiagram/feynplot_GUI/feynplot_gui/__main__.py

import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt # Import Qt for setting maximumHeight

from feynplot_gui.widgets.main_window import MainWindow
from feynplot_gui.controllers.main_controller import MainController

# from debug_utils import cout3  # 如果没用可以删除

def show_error_dialog(title, message, parent=None):
    """
    显示错误对话框的统一函数。
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText(title)
    msg_box.setInformativeText(message)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    # --- Add this line to limit the maximum height ---
    msg_box.setMaximumHeight(800) 
    # Alternatively, use stylesheet if you prefer:
    # msg_box.setStyleSheet("QMessageBox { max-height: 800px; }")
    # --- End of added line ---

    msg_box.exec()

if __name__ == "__main__":
    app = None
    window = None

    try:
        app = QApplication(sys.argv)

        # 创建主窗口和控制器
        window = MainWindow()
        controller = MainController(window)

        # ✅ 设置全局异常钩子，在窗口创建之后绑定
        def excepthook(exc_type, exc_value, exc_tb):
            tb_info = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            error_message = f"An unexpected runtime error occurred:\n\n{tb_info}\n\n" \
                            "The application might not function correctly or may close."
            show_error_dialog("Runtime Error", error_message, parent=window)
            sys.__excepthook__(exc_type, exc_value, exc_tb)

        sys.excepthook = excepthook

        window.show()
        sys.exit(app.exec())

    except Exception as e:
        # 应用初始化异常
        error_message = f"An unexpected startup error occurred: {e}\n\n" \
                        "The application might not function correctly or may close."

        if app:
            # Here, 'window' might not be fully initialized if the error occurs very early.
            # It's safer to just pass 'None' as parent or ensure 'window' is created before calling.
            # In the startup error, 'window' could still be 'None'.
            # We'll pass None as parent for the startup error case to avoid issues if window isn't ready.
            show_error_dialog("Application Startup Error", error_message, parent=None) 
        else:
            print(f"FATAL ERROR (QApplication not initialized): {error_message}", file=sys.stderr)

        sys.exit(1)