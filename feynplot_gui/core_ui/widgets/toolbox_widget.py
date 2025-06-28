# feynplot_gui/widgets/toolbox_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QRadioButton, QLabel,
    QFrame, # 用于分隔线或面板样式
    QMessageBox # 如果按钮功能需要弹出消息框
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal # 用于对齐和信号

class ToolboxWidget(QFrame): # <-- 改为继承 QFrame
    """
    负责创建并管理 Feynman Diagram 绘图工具箱的按钮和工具选择。
    这个工具箱将包含绘图模式选择按钮以及图操作按钮（保存、撤销、重做、清空等）。
    """
    # 定义信号，这些信号将由 MainController 或 ToolboxController 监听
    # 用于通知控制器具体的 UI 操作
    # tool_mode_selected = Signal(str) # 传递选中的工具模式 (e.g., 'select', 'line', 'vertex')
    save_diagram_requested = Signal()
    undo_action_requested = Signal()
    redo_action_requested = Signal()
    add_vertex_requested = Signal()
    add_line_requested = Signal()
    delete_selected_item_requested = Signal()
    clear_diagram_requested = Signal()
    delete_vertex_requested = Signal() # 新增信号
    delete_line_requested = Signal()   # 新增信号

    # --- 顶点可见性信号 ---
    show_all_vertices_requested = Signal()
    hide_all_vertices_requested = Signal()
    
    # --- 顶点标签可见性信号 ---
    show_all_vertex_labels_requested = Signal()
    hide_all_vertex_labels_requested = Signal()

    # --- 【新增】线标签可见性信号 ---
    show_all_line_labels_requested = Signal()
    hide_all_line_labels_requested = Signal()

    def __init__(self, controller_instance, parent=None):
        super().__init__(parent)
        self.ctrl = controller_instance # 假设这是 MainController 的实例

        self.setWindowTitle("工具箱")
        self.setFixedWidth(300) # 设置固定宽度，适应按钮和文本

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # 设置边距
        self.layout.setSpacing(8) # 按钮和控件之间的间距

        self.layout.addWidget(self._create_separator()) # 分隔线
        self._create_action_buttons()
        self._connect_buttons_and_signals()

        self.layout.addStretch() # 添加一个伸展器，将按钮推向顶部


    def _create_action_buttons(self):
        """
        创建操作按钮（保存、撤销、重做、添加、删除、清空）。
        """
        self.layout.addWidget(QLabel(self.tr("<b>操作:</b>"))) # 加粗标题

        # 保存图按钮
        self.save_button = QPushButton(self.tr("保存图"))
        self.layout.addWidget(self.save_button)

        # 撤销按钮
        self.undo_button = QPushButton(self.tr("撤销"))
        self.layout.addWidget(self.undo_button)

        # 重做按钮
        self.redo_button = QPushButton(self.tr("重做"))
        self.layout.addWidget(self.redo_button)

        self.layout.addWidget(self._create_separator()) # 分隔线

        # 直接添加顶点按钮
        self.add_vertex_button = QPushButton(self.tr("添加顶点"))
        self.layout.addWidget(self.add_vertex_button)

        # 直接添加线条按钮
        self.add_line_button = QPushButton(self.tr("添加线条"))
        self.layout.addWidget(self.add_line_button)

        # 删除顶点按钮
        self.delete_vertex_button = QPushButton(self.tr("删除顶点"))
        self.layout.addWidget(self.delete_vertex_button)

        # 删除线条按钮
        self.delete_line_button = QPushButton(self.tr("删除线条"))
        self.layout.addWidget(self.delete_line_button)

        # --- 顶点可见性按钮 ---
        self.layout.addWidget(self._create_separator()) # 分隔线
        self.layout.addWidget(QLabel(self.tr("<b>顶点:</b>")))
        self.show_all_vertices_button = QPushButton(self.tr("显示所有顶点"))
        self.layout.addWidget(self.show_all_vertices_button)
        self.hide_all_vertices_button = QPushButton(self.tr("隐藏所有顶点"))
        self.layout.addWidget(self.hide_all_vertices_button)

        # --- 顶点标签可见性按钮 ---
        self.layout.addWidget(self._create_separator()) # 分隔线
        self.layout.addWidget(QLabel(self.tr("<b>顶点标签:</b>")))
        self.show_all_vertex_labels_button = QPushButton(self.tr("显示所有标签"))
        self.layout.addWidget(self.show_all_vertex_labels_button)
        self.hide_all_vertex_labels_button = QPushButton(self.tr("隐藏所有标签"))
        self.layout.addWidget(self.hide_all_vertex_labels_button)

        # --- 【新增】线标签可见性按钮 ---
        self.layout.addWidget(self._create_separator()) # 分隔线
        self.layout.addWidget(QLabel(self.tr("<b>线标签:</b>")))
        self.show_all_line_labels_button = QPushButton(self.tr("显示所有标签"))
        self.layout.addWidget(self.show_all_line_labels_button)
        self.hide_all_line_labels_button = QPushButton(self.tr("隐藏所有标签"))
        self.layout.addWidget(self.hide_all_line_labels_button)

        # 清空图
        self.layout.addWidget(self._create_separator()) # 分隔线
        self.clear_diagram_button = QPushButton(self.tr("清空图"))
        self.layout.addWidget(self.clear_diagram_button)


    def _connect_buttons_and_signals(self):
        """
        连接按钮的点击信号到本类的槽函数，再由槽函数发出本类定义的信号。
        """
        # 操作按钮的信号
        self.save_button.clicked.connect(self.save_diagram_requested.emit)
        self.undo_button.clicked.connect(self.undo_action_requested.emit)
        self.redo_button.clicked.connect(self.redo_action_requested.emit)
        self.add_vertex_button.clicked.connect(self.add_vertex_requested.emit)
        self.add_line_button.clicked.connect(self.add_line_requested.emit)
        self.delete_vertex_button.clicked.connect(self.delete_vertex_requested.emit)
        self.delete_line_button.clicked.connect(self.delete_line_requested.emit)
        
        # 顶点可见性信号
        self.show_all_vertices_button.clicked.connect(self.show_all_vertices_requested.emit)
        self.hide_all_vertices_button.clicked.connect(self.hide_all_vertices_requested.emit) 
        
        # 顶点标签可见性信号
        self.show_all_vertex_labels_button.clicked.connect(self.show_all_vertex_labels_requested.emit)
        self.hide_all_vertex_labels_button.clicked.connect(self.hide_all_vertex_labels_requested.emit)

        # --- 【新增】线标签可见性信号 ---
        self.show_all_line_labels_button.clicked.connect(self.show_all_line_labels_requested.emit)
        self.hide_all_line_labels_button.clicked.connect(self.hide_all_line_labels_requested.emit)

        # 清空图按钮需要确认，所以连接到本地槽函数
        self.clear_diagram_button.clicked.connect(self._on_clear_diagram_button_clicked)

    def _emit_tool_signal(self, tool_name):
        """内部方法：根据选中的工具发出 tool_mode_selected 信号。"""
        pass 

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
        if hasattr(self.toolbox_widget, 'select_tool_radio') and tool_name == 'select_tool':
            self.select_tool_radio.setChecked(True)
        elif hasattr(self.toolbox_widget, 'line_tool_radio') and tool_name == 'line_tool':
            self.line_tool_radio.setChecked(True)
        elif hasattr(self.toolbox_widget, 'vertex_tool_radio') and tool_name == 'vertex_tool':
            self.vertex_tool_radio.setChecked(True)