# feynplot_gui/__main__.py

import sys
import traceback
import time # 导入 time 模块
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTranslator, QLocale, QLibraryInfo

from feynplot_gui.core_ui.widgets.main_window import MainWindow
from feynplot_gui.core_ui.controllers.main_controller import MainController

pause_time = 0

def show_error_dialog(title, message, parent=None):
    """
    显示错误对话框的统一函数。所有对话框文本都将通过 QApplication.translate() 进行标记。
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    # 使用 QApplication.translate 来标记字符串，确保它们能被 lupdate 提取
    msg_box.setText(QApplication.translate("ErrorDialog", title))
    msg_box.setInformativeText(QApplication.translate("ErrorDialog", message))
    msg_box.setWindowTitle(QApplication.translate("ErrorDialog", "Error"))
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    msg_box.setMaximumHeight(800) # 限制最大高度，防止内容过多时对话框过高
    
    msg_box.exec()


def main():
    app = None
    window = None

    try:
        print("正在启动...")
        app = QApplication(sys.argv)
        print("正在加载翻译文件...")

        # --- 国际化（多语言支持）相关代码开始 ---
        # translator_app 用于加载应用程序自定义的翻译文件
        translator_app = QTranslator() 
        # translator_qt 用于加载 Qt 框架自带的翻译文件（例如标准对话框的“确定”、“取消”按钮）
        translator_qt = QTranslator()  

        # 1. 获取系统当前的语言环境名称
        # 例如 'zh_CN', 'en_US', 'ja_JP' 等。这决定了我们首先尝试加载哪个语言的翻译。
        system_locale_name = QLocale.system().name()
        system_locale_name = 'en_US'
        print(f"检测到系统语言环境: {system_locale_name}")

        # 定义翻译文件存放的基础路径
        # 假设你的 .qm 文件位于项目根目录下的 'locale/<language_code>/LC_MESSAGES/'
        # 例如 'locale/zh_CN/LC_MESSAGES/feynplot_gui.qm'
        translations_base_path = r"F:\Research\pyfeynplot\feynplot_gui\locale" 

        # 应用程序自身的翻译文件名
        app_qm_filename = f"feynplot_gui.qm" 

        # 2. 尝试加载应用程序自身的翻译文件
        # 首先尝试加载当前系统语言的翻译文件
        cwd = sys.path[0]  # 获取当前工作目录
        print(f"当前工作目录: {cwd} (检查 .qm 文件路径是否正确)")
        if translator_app.load(app_qm_filename, f"{translations_base_path}/{system_locale_name}/"):
            QApplication.installTranslator(translator_app)
            print(f"成功为系统语言 {system_locale_name} 加载了应用程序翻译。")
            time.sleep(pause_time) # 在加载成功后暂停 1 秒
        # 如果系统语言没有对应的翻译文件，则尝试加载英文（en_US）作为备用语言
        elif translator_app.load(app_qm_filename, f"{translations_base_path}/en_US/LC_MESSAGES"):
            QApplication.installTranslator(translator_app)
            print(f"未能为 {system_locale_name} 找到翻译，回退到加载英文 (en_US) 应用程序翻译。")
            time.sleep(pause_time) # 在回退加载成功后暂停 1 秒
        else:
            print(f"没有为系统语言 {system_locale_name} 或英文 (en_US) 找到应用程序翻译文件。")
            print(f"当前工作目录: {sys.path[0]} (检查 .qm 文件路径是否正确)") # 打印当前工作目录，便于调试路径问题
            time.sleep(pause_time) # 在未找到翻译文件后暂停 1 秒

        # 3. （可选）加载 Qt 框架自带的翻译文件
        # 这将翻译 Qt 标准组件的文本，例如 QMessageBox 的“OK”、“Cancel”按钮，QFileDialog 的文件选择器文本等。
        # Qt 框架的翻译文件通常在 PySide6 的安装目录下。
        # 请注意：QLibraryInfo.LibraryPath.TranslationsPath 是正确的，之前可能写成了 QLibraryInfo.LibraryPath.Translations
        qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        if translator_qt.load(f"qt_{system_locale_name}", qt_translations_path):
             QApplication.installTranslator(translator_qt)
             print(f"成功为系统语言 {system_locale_name} 加载了 Qt 框架翻译。")
             time.sleep(pause_time) # 在加载成功后暂停 1 秒
        else:
             print(f"没有为系统语言 {system_locale_name} 找到 Qt 框架翻译。")
             time.sleep(pause_time) # 在未找到翻译文件后暂停 1 秒

        # --- 国际化（多语言支持）相关代码结束 ---

        # 创建主窗口和控制器
        window = MainWindow()
        controller = MainController(window)

        window.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        tb_info = "".join(traceback.format_exc()) # 获取完整的堆栈信息
        
        # 标记错误信息中的字符串，确保这些关键信息也能被翻译
        title_str = QApplication.translate("Main", "Application Startup Error")
        message_str = QApplication.translate(
            "Main",
            "An unexpected startup error occurred: {e_detail}\n\nDetails:\n{tb_info_detail}\n\nThe application might not function correctly or may close."
        ).format(e_detail=e, tb_info_detail=tb_info)

        # 即使应用程序初始化失败，也尝试显示本地化的错误对话框
        show_error_dialog(title_str, message_str, parent=None)
        
        # 这条打印到 stderr 的信息通常用于调试，不一定是用户界面可见的，因此通常不需要翻译
        print(f"致命错误 (QApplication 未初始化): {e}\n{tb_info}", file=sys.stderr)
        
        sys.exit(pause_time)

if __name__ == "__main__":
    print("程序入口")
    main()