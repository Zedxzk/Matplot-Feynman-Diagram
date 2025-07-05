# feynplot_gui/widgets/toolbox_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QRadioButton, QLabel,
    QFrame,
    QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal

class ToolboxWidget(QFrame):
    """
    负责创建并管理 Feynman Diagram 绘图工具箱的按钮和工具选择。
    这个工具箱将包含绘图模式选择按钮以及图操作按钮（保存、撤销、重做、清空等）。
    """
    # 定义信号，这些信号将由 MainController 或 ToolboxController 监听
    # 用于通知控制器具体的 UI 操作
    save_diagram_requested = Signal()
    undo_action_requested = Signal()
    redo_action_requested = Signal()
    add_vertex_requested = Signal()
    add_line_requested = Signal()
    delete_selected_item_requested = Signal()
    clear_diagram_requested = Signal()
    delete_vertex_requested = Signal()
    delete_line_requested = Signal()
    
    # --- 新增/更新的信号 ---
    request_auto_grid_adjustment = Signal()
    request_toggle_grid_visibility = Signal() # <--- **新增信号：请求切换网格可见性**

    # --- 顶点可见性信号 ---
    show_all_vertices_requested = Signal()
    hide_all_vertices_requested = Signal()
    
    # --- 顶点标签可见性信号 ---
    show_all_vertex_labels_requested = Signal()
    hide_all_vertex_labels_requested = Signal()

    # --- 线标签可见性信号 ---
    show_all_line_labels_requested = Signal()
    hide_all_line_labels_requested = Signal()
    
    # --- 自动调整画布信号 ---
    request_auto_scale = Signal()

    # --- 自动设置线角度信号 ---
    request_auto_set_line_angles = Signal()


    def __init__(self, controller_instance, parent=None):
        super().__init__(parent)
        self.ctrl = controller_instance # 假设这是 MainController 的实例

        self.setWindowTitle("工具箱")
        self.setFixedWidth(300)

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)

        self.layout.addWidget(self._create_separator())
        self._create_action_buttons()
        self._connect_buttons_and_signals()

        self.layout.addStretch()


    def _create_action_buttons(self):
        """
        创建操作按钮（保存、撤销、重做、添加、删除、清空）。
        """

        self.layout.addWidget(QLabel(self.tr("<b>操作:</b>")))
        self.save_button = QPushButton(self.tr("保存图"))
        self.layout.addWidget(self.save_button)

        self.undo_button = QPushButton(self.tr("撤销"))
        self.layout.addWidget(self.undo_button)

        self.redo_button = QPushButton(self.tr("重做"))
        self.layout.addWidget(self.redo_button)

        self.layout.addWidget(self._create_separator())

        # 对象操作部分
        self.layout.addWidget(QLabel(self.tr("<b>对象操作</b>")))
        self.add_vertex_button = QPushButton(self.tr("添加顶点"))
        self.layout.addWidget(self.add_vertex_button)

        self.add_line_button = QPushButton(self.tr("添加线条"))
        self.layout.addWidget(self.add_line_button)

        self.delete_vertex_button = QPushButton(self.tr("删除顶点"))
        self.layout.addWidget(self.delete_vertex_button)

        self.delete_line_button = QPushButton(self.tr("删除线条"))
        self.layout.addWidget(self.delete_line_button)
        
        self.auto_grid_button = QPushButton(self.tr("自动调整格点"))
        self.layout.addWidget(self.auto_grid_button)


        # --- 顶点可见性按钮 ---
        self.layout.addWidget(self._create_separator())
        self.layout.addWidget(QLabel(self.tr("<b>顶点:</b>")))
        self.show_all_vertices_button = QPushButton(self.tr("显示所有顶点"))
        self.layout.addWidget(self.show_all_vertices_button)
        self.hide_all_vertices_button = QPushButton(self.tr("隐藏所有顶点"))
        self.layout.addWidget(self.hide_all_vertices_button)

        # --- 顶点标签可见性按钮 ---
        self.layout.addWidget(self._create_separator())
        self.layout.addWidget(QLabel(self.tr("<b>顶点标签:</b>")))
        self.show_all_vertex_labels_button = QPushButton(self.tr("显示所有标签"))
        self.layout.addWidget(self.show_all_vertex_labels_button)
        self.hide_all_vertex_labels_button = QPushButton(self.tr("隐藏所有标签"))
        self.layout.addWidget(self.hide_all_vertex_labels_button)

        # --- 线标签可见性按钮及线角度设置按钮 ---
        self.layout.addWidget(self._create_separator())
        self.layout.addWidget(QLabel(self.tr("<b>线标签/角度:</b>")))
        self.show_all_line_labels_button = QPushButton(self.tr("显示所有标签"))
        self.layout.addWidget(self.show_all_line_labels_button)
        self.hide_all_line_labels_button = QPushButton(self.tr("隐藏所有标签"))
        self.layout.addWidget(self.hide_all_line_labels_button)
        
        self.auto_set_line_angles_button = QPushButton(self.tr("自动设置所有线角度"))
        self.layout.addWidget(self.auto_set_line_angles_button)


        # --- 画布操作按钮 ---
        self.layout.addWidget(self._create_separator())
        self.layout.addWidget(QLabel(self.tr("<b>画布操作</b>")))
        self.auto_scale_button = QPushButton(self.tr("自动调整画布"))
        self.layout.addWidget(self.auto_scale_button)

        # 【新增】切换网格可见性按钮
        self.toggle_grid_button = QPushButton(self.tr("切换网格可见性")) # <--- **新增按钮**
        self.layout.addWidget(self.toggle_grid_button) # <--- **将按钮添加到布局中**

        # 清空图
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

        # 线标签可见性信号
        self.show_all_line_labels_button.clicked.connect(self.show_all_line_labels_requested.emit)
        self.hide_all_line_labels_button.clicked.connect(self.hide_all_line_labels_requested.emit)
        
        self.auto_set_line_angles_button.clicked.connect(self.request_auto_set_line_angles.emit)

        self.auto_grid_button.clicked.connect(self.request_auto_grid_adjustment.emit)

        self.auto_scale_button.clicked.connect(self.request_auto_scale.emit)

        # 【新增】连接切换网格可见性按钮信号
        self.toggle_grid_button.clicked.connect(self.request_toggle_grid_visibility.emit) # <--- **连接信号**

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
            self.clear_diagram_requested.emit()

    def _create_separator(self):
        """创建一个可视化的分隔线。"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedHeight(2)
        return separator

    def set_tool_active(self, tool_name):
        """
        外部方法：设置当前激活的工具模式。
        由 ToolboxController 调用，以响应模型状态变化。
        """
        if hasattr(self, 'select_tool_radio') and tool_name == 'select_tool':
            self.select_tool_radio.setChecked(True)
        elif hasattr(self, 'line_tool_radio') and tool_name == 'line_tool':
            self.line_tool_radio.setChecked(True)
        elif hasattr(self.toolbox_widget, 'vertex_tool_radio') and tool_name == 'vertex_tool':
            self.vertex_tool_radio.setChecked(True)