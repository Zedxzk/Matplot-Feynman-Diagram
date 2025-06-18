# feynplot_gui/widgets/main_window.py (更新)

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel
from PySide6.QtCore import Qt

from feynplot_gui.widgets.canvas_widget import CanvasWidget
from feynplot_gui.widgets.navigation_bar_widget import NavigationBarWidget
from feynplot_gui.widgets.toolbox_widget import ToolboxWidget
from feynplot_gui.widgets.vertex_list_widget import VertexListWidget
from feynplot_gui.widgets.line_list_widget import LineListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feynman Diagram Plotter")
        self.setGeometry(100, 100, 1400, 800) # 增大窗口尺寸以更好地容纳三列
        self.init_ui()

    def init_ui(self):
        """初始化主窗口的布局和包含的组件。"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主水平布局：左侧面板 | 画布 | 右侧面板
        main_horizontal_layout = QHBoxLayout(central_widget)
        main_horizontal_layout.setContentsMargins(0, 0, 0, 0) # 移除边距以最大化空间

        # --- 左侧面板：顶点和线条列表 ---
        # --- 左侧面板：顶点和线条列表 ---
        left_panel_layout = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel_layout)
        left_panel_widget.setFixedWidth(220)

        # 顶点列表标题
        vertex_list_label = QLabel("顶点列表") # 创建标签
        vertex_list_label.setAlignment(Qt.AlignCenter) # 居中对齐，可选
        left_panel_layout.addWidget(vertex_list_label) # 将标签添加到布局

        self.vertex_list_widget = VertexListWidget(self)
        # self.vertex_list_widget.setWindowTitle("顶点列表") # 这行可以删掉，因为它不起作用
        left_panel_layout.addWidget(self.vertex_list_widget)

        # 线条列表标题
        line_list_label = QLabel("线条列表") # 创建标签
        line_list_label.setAlignment(Qt.AlignCenter) # 居中对齐，可选
        left_panel_layout.addWidget(line_list_label) # 将标签添加到布局

        self.line_list_widget = LineListWidget(self)
        # self.line_list_widget.setWindowTitle("线条列表") # 这行也可以删掉
        left_panel_layout.addWidget(self.line_list_widget)

        left_panel_layout.addStretch(1)

        main_horizontal_layout.addWidget(left_panel_widget)

        # --- 中间区域：画布 (占据大部分空间) ---
        self.canvas_widget = CanvasWidget(self)
        main_horizontal_layout.addWidget(self.canvas_widget, 1) # 设置伸展因子为 1，让它尽可能填充空间

        # --- 右侧面板：工具箱 ---
        self.toolbox_widget = ToolboxWidget(controller_instance=None, parent=self)
        self.toolbox_widget.setFixedWidth(120) # 保持工具箱的固定宽度
        main_horizontal_layout.addWidget(self.toolbox_widget)


        # 顶部导航栏 (通常通过 self.setMenuBar 和 self.addToolBar 添加)
        self.navigation_bar_widget = NavigationBarWidget(self)
        self.setMenuBar(self.navigation_bar_widget.menu_bar)
        self.addToolBar(Qt.TopToolBarArea, self.navigation_bar_widget.tool_bar)

        # 将重要的子组件实例暴露出来，供 MainController 访问
        self.canvas_widget_instance = self.canvas_widget
        self.toolbox_widget_instance = self.toolbox_widget
        self.vertex_list_widget_instance = self.vertex_list_widget
        self.line_list_widget_instance = self.line_list_widget
        self.navigation_bar_widget_instance = self.navigation_bar_widget