# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_collapsible_group_box.py

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QFormLayout, QWidget
from PySide6.QtCore import Qt

class CollapsibleGroupBox(QGroupBox):
    """
    一个可折叠的 QGroupBox，当其复选框被切换时，
    其内容将隐藏或显示。它返回其内部的 FormLayout
    以便外部可以直接向其添加控件。
    """
    def __init__(self, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True) # 默认展开

        # 创建一个独立的 QWidget 来作为内容容器
        self._content_widget = QWidget(self)
        self._content_layout = QFormLayout(self._content_widget) # FormLayout 用于放置实际控件

        # --- 设置内容 widget 的最大高度为 800 像素 ---
        # self._content_widget.setMaximumHeight(800)
        # --- 修改结束 ---

        # 创建 group_box 的主布局，并将 content_widget 添加进去
        _main_layout = QVBoxLayout(self)
        _main_layout.addWidget(self._content_widget)
        _main_layout.setContentsMargins(0, 0, 0, 0) # 移除额外边距，让内容更紧凑

        # 连接 toggled 信号来控制 content_widget 的可见性
        self.toggled.connect(self._content_widget.setVisible)

    def content_layout(self) -> QFormLayout:
        """
        返回用于放置组盒内容控件的 QFormLayout。
        """
        return self._content_layout

    def content_widget(self) -> QWidget:
        """
        返回包含组盒内容布局的 QWidget。
        """
        return self._content_widget