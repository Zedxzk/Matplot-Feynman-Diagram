# feynplot_GUI/feynplot_gui/buttons.py

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton,
    QToolBar, QToolButton, # 如果你更喜欢使用 QToolButton
    QMessageBox # 如果按钮功能需要弹出消息框
)
from PySide6.QtGui import QIcon # 如果你计划使用图标
from PySide6.QtCore import Qt # 用于对齐和样式

class RightToolbarButtons(QFrame):
    """
    负责创建并管理 MainWindow 右侧工具栏的按钮。
    """
    def __init__(self, controller_instance, parent=None):
        super().__init__(parent)
        self.ctrl = controller_instance # 持有 Controller 的引用
        
        # 可选：设置 QFrame 的样式，使其看起来像一个独立的面板
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5) # 设置边距
        self.layout.setSpacing(10) # 按钮之间的间距

        self._create_buttons()
        self._connect_buttons()

    def _create_buttons(self):
        """
        创建所有右侧工具栏的按钮。
        """
        # 可以选择使用 QPushButton 或 QToolButton。这里沿用你代码中的 QPushButton
        
        # 保存图按钮
        self.save_button = QPushButton("保存图")
        # self.save_button.setIcon(QIcon("path/to/save_icon.png")) # 可选：添加图标
        self.layout.addWidget(self.save_button)

        # 撤销按钮
        self.undo_button = QPushButton("撤销")
        self.layout.addWidget(self.undo_button)

        # 重做按钮
        self.redo_button = QPushButton("重做")
        self.layout.addWidget(self.redo_button)
        
        # 添加一个分隔符 (如果你想用 QToolBar 里的 addSeparator() 效果，这里可以模拟)
        # self.layout.addWidget(self._create_separator()) # 需要一个辅助方法来创建分隔线
        
        # --- 添加你之前或未来需要的其他按钮 ---
        # 示例：添加顶点（如果不在画布双击模式下）
        self.add_vertex_button = QPushButton("添加顶点")
        self.layout.addWidget(self.add_vertex_button)

        # 示例：添加线条（启动选择模式）
        self.add_line_button = QPushButton("添加线条")
        self.layout.addWidget(self.add_line_button)

        # 示例：删除选中项
        self.delete_item_button = QPushButton("删除选中项")
        self.layout.addWidget(self.delete_item_button)
        
        # 示例：清空图
        self.clear_diagram_button = QPushButton("清空图")
        self.layout.addWidget(self.clear_diagram_button)


        self.layout.addStretch() # 添加一个伸展器，将按钮推向顶部

    def _connect_buttons(self):
        """
        连接按钮的点击信号到 Controller 中的相应方法。
        """
        # 这些方法需要在 Controller 类中实现
        self.save_button.clicked.connect(self.ctrl.save_diagram_to_file)
        self.undo_button.clicked.connect(self.ctrl.undo)
        self.redo_button.clicked.connect(self.ctrl.redo)

        # 连接其他按钮
        self.add_vertex_button.clicked.connect(self._on_add_vertex_button_clicked)
        self.add_line_button.clicked.connect(self._on_add_line_button_clicked)
        self.delete_item_button.clicked.connect(self._on_delete_item_button_clicked)
        self.clear_diagram_button.clicked.connect(self._on_clear_diagram_button_clicked)


    # --- 按钮点击的槽方法（这些方法可以直接调用 Controller 的方法） ---
    # 这些方法最好直接转发给 Controller，保持 Buttons 类专注 UI
    def _on_add_vertex_button_clicked(self):
        # 假设你的 ItemManager 知道如何处理添加顶点
        x_default, y_default = 0, 0 # 可以是默认值，也可以弹出对话框让用户输入
        self.ctrl.item_manager.add_new_vertex_at_coords(x_default, y_default)
        self.ctrl.status_message.emit("点击了 '添加顶点' 按钮。")

    def _on_add_line_button_clicked(self):
        # 启动线条添加流程，通常需要用户在画布上点击两个顶点
        self.ctrl.status_message.emit("点击了 '添加线条' 按钮。请在画布上点击两个顶点来创建一条线条。")
        self.ctrl.mouse_event_handler.set_mode("add_line") # 设置鼠标事件处理器模式

    def _on_delete_item_button_clicked(self):
        selected_item = self.ctrl.highlighter.get_selected_item()
        if selected_item:
            self.ctrl.item_manager.delete_item(selected_item)
            self.ctrl.status_message.emit(f"删除了项目: {selected_item.id}")
        else:
            self.ctrl.status_message.emit("没有选中项可删除。")

    def _on_clear_diagram_button_clicked(self):
        reply = QMessageBox.question(self, '清空图',
                                     "你确定要清空整个图吗？这将清除当前所有数据。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ctrl.diagram_model.clear_all_items()
            self.ctrl.highlighter.clear_selection()
            self.ctrl.update_view()
            self.ctrl.status_message.emit("图已清空。")

    # 可选：如果需要一个可视化分隔符
    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine) # 水平线
        separator.setFrameShadow(QFrame.Sunken) # 凹陷效果
        return separator