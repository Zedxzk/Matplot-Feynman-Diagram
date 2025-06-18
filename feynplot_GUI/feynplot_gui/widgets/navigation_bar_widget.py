# feynplot_gui/widgets/navigation_bar_widget.py

from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QMenuBar, QToolBar
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Signal


class NavigationBarWidget(QWidget):
    # 定义信号，这些信号将被 MainController 或 NavigationBarController 监听
    add_line_button_clicked = Signal()
    add_vertex_button_clicked = Signal()
    save_project_action_triggered = Signal()
    load_project_action_triggered = Signal()
    
    # 新增信号：当编辑顶点或线条的操作被触发时
    edit_selected_vertex_triggered = Signal()
    edit_selected_line_triggered = Signal()
    delete_selected_object_triggered = Signal() # 可以有一个通用的删除信号，具体删除什么由控制器判断

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化导航栏的用户界面元素。"""
        main_layout = QVBoxLayout()
        
        # --- 菜单栏示例 ---
        self.menu_bar = QMenuBar(self)
        file_menu  = self.menu_bar.addMenu("文件")
        edit_menu  = self.menu_bar.addMenu("编辑")
        view_menu  = self.menu_bar.addMenu("视图")
        about_menu = self.menu_bar.addMenu("关于") # 你的"关于"菜单

        # === 新增：对象操作菜单 ===
        self.obj_menu = self.menu_bar.addMenu("对象")
        self.obj_menu.setEnabled(False) # 默认禁用

        self.edit_obj_action = QAction("编辑属性", self)
        self.edit_obj_action.setEnabled(False)
        self.edit_obj_action.triggered.connect(self._on_edit_object_triggered)
        self.obj_menu.addAction(self.edit_obj_action)

        self.delete_obj_action = QAction("删除对象", self)
        self.delete_obj_action.setEnabled(False)
        self.delete_obj_action.triggered.connect(self.delete_selected_object_triggered.emit)
        self.obj_menu.addAction(self.delete_obj_action)
        
        # 文件菜单项
        save_action = QAction("保存项目", self)
        save_action.triggered.connect(self.save_project_action_triggered.emit)
        file_menu.addAction(save_action)

        load_action = QAction("加载项目", self)
        load_action.triggered.connect(self.load_project_action_triggered.emit)
        file_menu.addAction(load_action)

        # 编辑菜单项
        add_vertex_action = QAction("添加顶点", self)
        add_vertex_action.triggered.connect(self.add_vertex_button_clicked.emit)
        edit_menu.addAction(add_vertex_action)

        add_line_action = QAction("添加线条", self)
        add_line_action.triggered.connect(self.add_line_button_clicked.emit)
        edit_menu.addAction(add_line_action)

        main_layout.addWidget(self.menu_bar)

        # --- 关于菜单项的完善 ---
        show_about_action = QAction("关于 FeynPlot GUI", self) # 可以更具体一点
        show_about_action.triggered.connect(self._show_about_dialog) # 连接到槽函数
        about_menu.addAction(show_about_action) # 添加到"关于"菜单
        # --- 完善结束 ---

        # --- 工具栏示例 ---
        self.tool_bar = QToolBar("主要操作", self)
        self.tool_bar.setMovable(False)

        add_line_button = QPushButton("添加线条")
        add_line_button.clicked.connect(self.add_line_button_clicked.emit)
        self.tool_bar.addWidget(add_line_button)

        add_vertex_button = QPushButton("添加顶点")
        add_vertex_button.clicked.connect(self.add_vertex_button_clicked.emit) # 修正这里，之前没有连接
        self.tool_bar.addWidget(add_vertex_button)

        main_layout.addWidget(self.tool_bar)

        self.setLayout(main_layout)

    # --- 新增的槽函数和控制方法 ---
    def _on_edit_object_triggered(self):
        """内部槽函数，用于根据当前选中类型发出特定编辑信号"""
        print("编辑对象操作被触发。")

    def set_object_menu_enabled(self, enabled: bool):
        """
        设置“对象”菜单的启用状态。
        """
        self.obj_menu.setEnabled(enabled)
            
    # 可以添加方法来禁用/启用特定按钮或菜单项
    def set_add_line_enabled(self, enabled):
        # 找到对应的Action或Button并设置其 enabled 属性
        pass

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