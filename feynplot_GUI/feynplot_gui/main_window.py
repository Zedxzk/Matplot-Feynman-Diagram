# feynplot_GUI/feynplot_gui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QMenu, QMessageBox, QPushButton, QFrame,
    QToolBar, QToolButton # 确保导入了 QToolBar 和 QToolButton，即使你没用它来创建按钮，如果以后想切换会用到
)
from PySide6.QtGui import QAction, QIcon # QIcon 用于设置按钮图标，如果需要
from PySide6.QtCore import Qt

# 确保这些模块的导入路径正确
from feynplot_GUI.feynplot_gui.canvas_widget import CanvasWidget
from feynplot_GUI.feynplot_gui.controller import Controller
from feynplot.core.diagram import FeynmanDiagram # 用于 _new_diagram

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FeynPlot GUI")
        self.setGeometry(100, 100, 1400, 800)

        # 1. 创建所有 UI 控件
        self._create_widgets()
        # 2. 布置所有 UI 控件
        self._create_layouts()

        # 3. 实例化 Controller，并传入必要的 UI 引用
        # Controller 负责处理业务逻辑和协调模型与视图
        self.ctrl = Controller(
            self.canvas,
            self.vertex_list_widget,
            self.line_list_widget
        )
        self.ctrl.main_window = self # 将 MainWindow 自身引用传递给 Controller (可选，但有时用于显示对话框等)

        # 4. 创建菜单栏
        self._create_menu_bar()

        # 5. 连接按钮的信号到 Controller 中的方法
        # 确保 Controller 中有这些方法 (save_diagram_to_file, undo, redo)
        # self.save_button.clicked.connect(self.ctrl.save_diagram_to_file)
        # self.undo_button.clicked.connect(self.ctrl.undo)
        # self.redo_button.clicked.connect(self.ctrl.redo)
        
        # 连接列表视图的选中信号，以便 Controller 能够处理选中项
        self.vertex_list_widget.itemClicked.connect(self._on_list_item_clicked)
        self.line_list_widget.itemClicked.connect(self._on_list_item_clicked)


    def _create_widgets(self):
        """
        创建并初始化所有 GUI 控件。
        """
        # 设置中心控件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 画布区域 (Matplotlib 图形)
        self.canvas = CanvasWidget(parent=self.central_widget)

        # 左侧的顶点列表
        self.vertex_list_widget = QListWidget()
        self.vertex_list_widget.setWindowTitle("顶点") # 窗口标题
        self.vertex_list_widget.setSelectionMode(QListWidget.SingleSelection) # 单选模式

        # 左侧的线条列表
        self.line_list_widget = QListWidget()
        self.line_list_widget.setWindowTitle("线条") # 窗口标题
        self.line_list_widget.setSelectionMode(QListWidget.SingleSelection) # 单选模式

        # --- 右侧工具栏/按钮区域 ---
        # 使用 QFrame 作为容器，可以给它设置边框样式，更清晰
        self.right_toolbar_widget = QFrame()
        self.right_toolbar_widget.setFrameShape(QFrame.StyledPanel) # 设置边框样式
        self.right_toolbar_widget.setFrameShadow(QFrame.Raised) # 设置阴影效果

        self.right_toolbar_layout = QVBoxLayout()
        self.right_toolbar_widget.setLayout(self.right_toolbar_layout)

        # 添加具体按钮
        self.save_button = QPushButton("保存图")
        # 可以设置图标: self.save_button.setIcon(QIcon("path/to/save_icon.png"))
        self.right_toolbar_layout.addWidget(self.save_button)

        self.undo_button = QPushButton("撤销")
        self.right_toolbar_layout.addWidget(self.undo_button)

        self.redo_button = QPushButton("重做")
        self.right_toolbar_layout.addWidget(self.redo_button)
        
        self.hide_all_vertices_button = QPushButton("隐藏所有顶点")
        self.right_toolbar_layout.addWidget(self.hide_all_vertices_button)

        self.show_all_vertices_button = QPushButton("显示所有顶点")
        self.right_toolbar_layout.addWidget(self.show_all_vertices_button)

        # 添加一个伸展器，将按钮推向顶部
        self.right_toolbar_layout.addStretch()


    def _create_layouts(self):
        """
        布局所有 GUI 控件。
        """
        # 左侧布局：包含顶点和线条列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.vertex_list_widget, 1) # 伸展因子 1，让两个列表平分空间
        left_layout.addWidget(self.line_list_widget, 1)
        # 如果你未来有属性编辑器，可以加在这里
        # left_layout.addWidget(self.property_editor_widget, 1)

        # 主布局：水平排列左侧列表、中心画布和右侧工具栏
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.addLayout(left_layout, 2)      # 左侧占 1 份空间
        main_layout.addWidget(self.canvas, 5)      # 画布占 4 份空间，是主要的绘图区
        main_layout.addWidget(self.right_toolbar_widget, 1) # 右侧工具栏占 1 份空间


    def _create_menu_bar(self):
        """
        创建应用程序的菜单栏。
        """
        menu_bar = self.menuBar()

        # --- 文件菜单 ---
        file_menu = menu_bar.addMenu("文件")

        new_action = QAction("新建", self)
        new_action.triggered.connect(self._new_diagram)
        file_menu.addAction(new_action)

        # 绑定保存动作到菜单，也可以触发右侧按钮的保存
        save_action = QAction("保存", self)
        # save_action.triggered.connect(self.ctrl.save_diagram_to_file)
        file_menu.addAction(save_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- 编辑菜单 ---
        edit_menu = menu_bar.addMenu("编辑")

        # 菜单中的添加顶点动作
        add_vertex_action = QAction("添加顶点...", self)
        # 默认在 (0,0) 添加，可以根据需求修改或弹出对话框
        add_vertex_action.triggered.connect(
            lambda: self.ctrl.item_manager.add_new_vertex_at_coords(0, 0))
        edit_menu.addAction(add_vertex_action)

        # 菜单中的添加线条动作
        add_line_action = QAction("添加线条...", self)
        # 这会启动线条添加流程，通常需要用户在画布上点击两个顶点
        add_line_action.triggered.connect(self.ctrl.item_manager.start_add_line_process)
        edit_menu.addAction(add_line_action)
        
        # 菜单中的撤销/重做
        undo_action = QAction("撤销", self)
        # undo_action.triggered.connect(self.ctrl.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        # redo_action.triggered.connect(self.ctrl.redo)
        edit_menu.addAction(redo_action)

        # --- 帮助菜单 ---
        help_menu = menu_bar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _new_diagram(self):
        """
        处理“新建”菜单项的点击事件。
        清空当前图表并初始化新数据。
        """
        reply = QMessageBox.question(self, '新建',
                                     "您确定要新建一个图表吗？这将清除当前所有数据。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 创建一个新的 FeynmanDiagram 实例，替换旧的
            self.ctrl.diagram_model = FeynmanDiagram()
            # 重新初始化示例数据（如果需要，否则会是一个空图）
            self.ctrl.initialize_diagram_data()
            # 确保视图更新以反映新数据
            self.ctrl.update_view()
            self.ctrl.status_message.emit("已创建新图表。")

    def _show_about_dialog(self):
        """
        显示“关于”对话框。
        """
        QMessageBox.about(self, "关于 FeynPlot GUI",
                          "这是一个用于绘制费曼图的简单GUI应用。\n"
                          "版本: 1.0\n"
                          "作者: ZED(武汉大学->香港中文大学)\n"
                          "邮箱：zedxzk@gmail.com\n"
                          "GitHub: https://github.com/Zedxzk/Matplot-Feynman-Diagram\n"
                          )

    def _on_list_item_clicked(self, item):
        """
        处理列表项点击事件，通知 Controller 选中相应的模型对象。
        """
        # 根据点击的是哪个列表来判断是 Vertex 还是 Line
        if item in [self.vertex_list_widget.item(i) for i in range(self.vertex_list_widget.count())]:
            # 查找对应的 Vertex 对象
            for vertex in self.ctrl.diagram_model.vertices:
                if f"ID: {vertex.id}" in item.text(): # 假设列表项包含 ID
                    self.ctrl.highlighter.select_item(vertex)
                    break
        elif item in [self.line_list_widget.item(i) for i in range(self.line_list_widget.count())]:
            # 查找对应的 Line 对象
            for line in self.ctrl.diagram_model.lines:
                if f"ID: {line.id}" in item.text(): # 假设列表项包含 ID
                    self.ctrl.highlighter.select_item(line)
                    break
        self.ctrl.update_view() # 选中后更新视图以高亮显示