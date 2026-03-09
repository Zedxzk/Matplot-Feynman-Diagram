from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QLabel, 
    QTextBrowser, QDialogButtonBox, QPushButton, QApplication,
    QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import re
import html

class CustomErrorDialog(QDialog):
    """
    一个完全自定义的错误对话框，替代 QMessageBox。
    确保所有文本（包括标题、详细信息）都可以被选中和复制。
    自动调整高度以适应内容。
    """
    def __init__(self, title, message, detailed_text=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(600)  # 稍微减小最小宽度
        # 移除固定最小高度，允许根据内容收缩

        # 使用垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15) # 减小边距
        layout.setSpacing(10)

        # 1. 消息文本区域
        self.message_label = QLabel(message)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        self.message_label.setWordWrap(True)
        # 文本左对齐 (这才是 "文字本身")
        self.message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.message_label.setOpenExternalLinks(True)
        # 设置字体样式，并稍微限制最大宽度，以免太宽读起来累
        self.message_label.setStyleSheet("""
            QLabel {
                font-family: "Segoe UI", sans-serif;
                font-size: 10pt;
                line-height: 1.2;
                background-color: transparent;
                border: none;
            }
        """)
        
        # 为了让 "文字框" 居中，我们将其放入一个容器中，并使用水平布局 + 弹簧
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addStretch() # 左侧弹簧
        h_layout.addWidget(self.message_label)
        h_layout.addStretch() # 右侧弹簧
        
        # 初始高度可以估算一下，避免第一次打开太小
        initial_min_height = 80
        try:
            # 假设有效宽度约为 500 (留出两侧弹簧空间)
            # 使用 self.message_label.fontMetrics 可以获取准确的字体测量
            rect = self.message_label.fontMetrics().boundingRect(0, 0, 500, 5000, Qt.TextWordWrap, message)
            text_height = rect.height()
            initial_min_height = max(text_height + 40, 80)
        except:
            pass
            
        # 设置最小高度
        self.message_label.setMinimumHeight(int(initial_min_height))
        # 移除最大宽度限制，但为了保持一定的可读性，
        # 我们可以保留一个比较大的 MaximumWidth，或者不做任何限制，完全随窗口
        # 用户要求随窗口变化，所以不设 limit
        
        # 允许水平方向伸缩，垂直方向也伸缩
        from PySide6.QtWidgets import QSizePolicy
        # Label 本身的 SizePolicy。
        # 如果是 Expanding, 它会尽量利用所有给它的空间。
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        
        # 如果没有详细信息，让容器占据主要空间 (stretch=1)
        # 用居中对齐添加到垂直布局中，确保垂直也是居中的
        msg_stretch = 1 if not detailed_text else 0
        layout.addWidget(container, msg_stretch)

        # 2. 详细信息区域 (如果有)
        if detailed_text:
            detail_label = QLabel("Error Details:")
            detail_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            layout.addWidget(detail_label)
            
            self.detail_browser = QTextBrowser()
            
            # 使用简单的 HTML 高亮 Traceback
            highlighted_html = self._highlight_traceback(detailed_text)
            self.detail_browser.setHtml(highlighted_html)
            self.detail_browser.setOpenExternalLinks(False)
            self.detail_browser.setStyleSheet("""
                QTextBrowser {
                    font-family: Consolas, "Courier New", monospace;
                    font-size: 9pt;
                    background-color: #f8f8f8;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
            
            # 计算详细信息的高度
            line_count = detailed_text.count('\n') + 1
            # 粗略估算高度：每行约 18px，加上 padding，限制在 80 到 400 之间
            detail_height = max(max(line_count * 18 + 15, 80), 300)
            # 设置一个较小的最小高度，允许用户自己缩小详情区域
            self.detail_browser.setMinimumHeight(80) 
            
            # 允许垂直伸缩
            from PySide6.QtWidgets import QSizePolicy
            self.detail_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # 将 detail_browser 的拉伸因子设为 1，这样拉伸窗口时主要拉伸详情区域
            layout.addWidget(self.detail_browser, 1) 
        # else:
            # 如果没有详情，且消息区域 stretch=1，它会自动填满剩余空间
            # layout.addStretch()

        # 3. 按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        
        # 添加一个 "Copy All" 按钮
        copy_button = QPushButton("Copy Error Info")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(title, message, detailed_text))
        button_box.addButton(copy_button, QDialogButtonBox.ActionRole)
        
        layout.addWidget(button_box, 0) # 按钮区域不拉伸
        
        # 调整整个窗口大小
        # 强制设置初始大小，避免过高
        # 使用之前计算的 initial_min_height 作为消息框的基础高度
        total_height = initial_min_height + 80 # 基础高度 + 按钮 + padding
        if detailed_text:
            total_height += detail_height + 40 # 加上详情区域 + label + padding
        
        # 限制总高度不要超过屏幕高度的大部分 (例如 800)
        total_height = min(total_height, 800)
        
        self.resize(700, int(total_height))

    def _highlight_traceback(self, text):
        """简单的 Traceback 语法高亮"""
        if not text:
            return ""
            
        # 1. HTML 转义
        import html
        # 强制转义引号
        escaped = html.escape(text, quote=True)
        
        # 2. 正则替换颜色
        
        # 2.1 文件路径: File "..." -> 蓝色
        # 匹配 File + 空格 + 引号(可能是 " 或 &quot;) + 内容 + 引号
        # 使用 IGNORECASE 并且允许 &quot; 或 "
        escaped = re.sub(r'(File\s+(?:&quot;|").*?(?:&quot;|"))', r'<span style="color: #0066cc;">\1</span>', escaped, flags=re.IGNORECASE)
        
        # 2.2 行号: , line 123 -> 绿色
        escaped = re.sub(r'(,\s+line\s+\d+)', r'<span style="color: #009933;">\1</span>', escaped, flags=re.IGNORECASE)
        
        # 2.3 函数名: , in <module> -> 紫色
        # 匹配 , in ... 直到行尾
        escaped = re.sub(r'(,\s+in\s+.*?$)', r'<span style="color: #800080;">\1</span>', escaped, flags=re.MULTILINE|re.IGNORECASE)
        
        # 2.4 错误类型: xxxError: -> 红色加粗
        escaped = re.sub(r'(^\s*[\w\.]*Error:)', r'<span style="color: #cc0000; font-weight: bold;">\1</span>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'(^\s*[\w\.]*Exception:)', r'<span style="color: #cc0000; font-weight: bold;">\1</span>', escaped, flags=re.MULTILINE)
        
        # 3. 包装
        # 使用 div 和 pre-wrap 样式，指定字体
        style = 'font-family: Consolas, "Courier New", monospace; color: #333; margin: 0; white-space: pre-wrap;'
        return f'<div style="{style}">{escaped}</div>'

    def _copy_to_clipboard(self, title, message, detail):
        """复制所有错误信息到剪贴板"""
        clipboard = QApplication.clipboard()
        parts = [f"Title: {title}\n\nMessage:\n{message}"]
        if detail:
            parts.append(f"\nDetails:\n{detail}")
        clipboard.setText("".join(parts))

class MsgBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


    @staticmethod
    def show_message(parent, icon, title, text, detailed_text=None):
        msg = MsgBox(parent)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        if detailed_text:
            msg.setDetailedText(detailed_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    @staticmethod
    def warning(parent, title, text):
        MsgBox.show_message(parent, QMessageBox.Warning, title, text)

    @staticmethod
    def critical(parent, title, text):
        MsgBox.show_message(parent, QMessageBox.Critical, title, text)

    @staticmethod
    def information(parent, title, text):
        MsgBox.show_message(parent, QMessageBox.Information, title, text)

    @staticmethod
    def question(parent, title, text, buttons=None, default_button=None):
        """带可复制文本的确认对话框，返回用户点击的按钮。"""
        if buttons is None:
            buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        if default_button is None:
            default_button = QMessageBox.StandardButton.No
        msg = MsgBox(parent)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        msg.setDefaultButton(default_button)
        return msg.exec()
