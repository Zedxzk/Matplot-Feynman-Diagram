# feynplot_gui/widgets/toolbox_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QRadioButton, QLabel,
    QFrame, # 用于分隔线或面板样式
    QMessageBox # 如果按钮功能需要弹出消息框
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal # 用于对齐和信号

class ToolboxWidget(QWidget):
    """
    负责创建并管理 Feynman Diagram 绘图工具箱的按钮和工具选择。
    这个工具箱将包含绘图模式选择按钮以及图操作按钮（保存、撤销、重做、清空等）。
    """
    # 定义信号，这些信号将由 MainController 或 ToolboxController 监听
    # 用于通知控制器具体的 UI 操作
    tool_mode_selected = Signal(str) # 传递选中的工具模式 (e.g., 'select', 'line', 'vertex')
    save_diagram_requested = Signal()
    undo_action_requested = Signal()
    redo_action_requested = Signal()
    add_vertex_requested = Signal()
    add_line_requested = Signal()
    delete_selected_item_requested = Signal()
    clear_diagram_requested = Signal()

    def __init__(self, controller_instance, parent=None):
        super().__init__(parent)
        # ToolboxWidget 不直接持有 MainController 的完整引用，
        # 而是通过信号与控制器通信，或者只持有 ToolboxController 的引用。
        # 这里为了简化和直接转发，暂保留 controller_instance，但更推荐通过信号传递
        self.ctrl = controller_instance # 假设这是 MainController 的实例

        self.setWindowTitle("工具箱")
        self.setFixedWidth(180) # 设置固定宽度，适应按钮和文本

        # 可选：设置 QFrame 的样式，使其看起来像一个独立的面板
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # 设置边距
        self.layout.setSpacing(8) # 按钮和控件之间的间距

        self._create_tool_selection_buttons()
        self.layout.addWidget(self._create_separator()) # 分隔线
        self._create_action_buttons()
        self._connect_buttons_and_signals()

        self.layout.addStretch() # 添加一个伸展器，将按钮推向顶部

    def _create_tool_selection_buttons(self):
        """
        创建用于选择绘图模式（选择、画线、画顶点）的单选按钮。
        """
        self.layout.addWidget(QLabel("<b>绘图模式:</b>")) # 加粗标题

        self.tool_button_group = QButtonGroup(self)
        self.tool_button_group.setExclusive(True) # 确保每次只能选择一个工具

        # 选择工具 (默认)
        self.select_tool_radio = QRadioButton("选择/编辑")
        self.select_tool_radio.setChecked(True)
        self.tool_button_group.addButton(self.select_tool_radio, 0)
        # 连接到内部槽函数，再由其发出信号
        self.select_tool_radio.toggled.connect(lambda checked: self._emit_tool_signal('select_tool') if checked else None)
        self.layout.addWidget(self.select_tool_radio)

        # 画线工具
        self.line_tool_radio = QRadioButton("画线工具")
        self.tool_button_group.addButton(self.line_tool_radio, 1)
        self.line_tool_radio.toggled.connect(lambda checked: self._emit_tool_signal('line_tool') if checked else None)
        self.layout.addWidget(self.line_tool_radio)

        # 画顶点工具
        self.vertex_tool_radio = QRadioButton("画顶点工具")
        self.tool_button_group.addButton(self.vertex_tool_radio, 2)
        self.vertex_tool_radio.toggled.connect(lambda checked: self._emit_tool_signal('vertex_tool') if checked else None)
        self.layout.addWidget(self.vertex_tool_radio)

    def _create_action_buttons(self):
        """
        创建操作按钮（保存、撤销、重做、添加、删除、清空）。
        """
        self.layout.addWidget(QLabel("<b>操作:</b>")) # 加粗标题

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

        self.layout.addWidget(self._create_separator()) # 分隔线

        # 直接添加顶点按钮 (如果不需要在画布上点击)
        self.add_vertex_button = QPushButton("直接添加顶点")
        self.layout.addWidget(self.add_vertex_button)

        # 直接添加线条按钮 (如果不需要在画布上点击，但通常不是这样)
        self.add_line_button = QPushButton("直接添加线条")
        self.layout.addWidget(self.add_line_button)

        # 删除选中项
        self.delete_item_button = QPushButton("删除选中项")
        self.layout.addWidget(self.delete_item_button)

        # 清空图
        self.clear_diagram_button = QPushButton("清空图")
        self.layout.addWidget(self.clear_diagram_button)

    def _connect_buttons_and_signals(self):
        """
        连接按钮的点击信号到本类的槽函数，再由槽函数发出本类定义的信号。
        """
        # 工具模式选择按钮的信号已在 _create_tool_selection_buttons 中连接

        # 操作按钮的信号
        self.save_button.clicked.connect(self.save_diagram_requested.emit)
        self.undo_button.clicked.connect(self.undo_action_requested.emit)
        self.redo_button.clicked.connect(self.redo_action_requested.emit)
        self.add_vertex_button.clicked.connect(self.add_vertex_requested.emit)
        self.add_line_button.clicked.connect(self.add_line_requested.emit)
        self.delete_item_button.clicked.connect(self.delete_selected_item_requested.emit)
        # 清空图按钮需要确认，所以连接到本地槽函数
        self.clear_diagram_button.clicked.connect(self._on_clear_diagram_button_clicked)

    def _emit_tool_signal(self, tool_name):
        """内部方法：根据选中的工具发出 tool_mode_selected 信号。"""
        self.tool_mode_selected.emit(tool_name)

    def _on_clear_diagram_button_clicked(self):
        """清空图按钮的点击处理，带确认对话框。"""
        reply = QMessageBox.question(self, '清空图',
                                     "你确定要清空整个图吗？这将清除当前所有数据。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_diagram_requested.emit() # 只有确认后才发出信号

    def _create_separator(self):
        """创建一个可视化的分隔线。"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine) # 水平线
        separator.setFrameShadow(QFrame.Sunken) # 凹陷效果
        separator.setFixedHeight(2) # 设置高度，让线条更明显
        return separator

    def set_tool_active(self, tool_name):
        """
        外部方法：设置当前激活的工具模式。
        由 ToolboxController 调用，以响应模型状态变化。
        """
        if tool_name == 'select_tool':
            self.select_tool_radio.setChecked(True)
        elif tool_name == 'line_tool':
            self.line_tool_radio.setChecked(True)
        elif tool_name == 'vertex_tool':
            self.vertex_tool_radio.setChecked(True)
        # 确保setChecked会触发toggled信号，从而更新控制器状态