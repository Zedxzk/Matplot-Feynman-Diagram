# feynplot_gui/widgets/navigation_bar_widget.py

from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QMenuBar, QToolBar
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Signal
from typing import Optional 


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

    # 新增信号：用于触发后端设置对话框
    # 原有的 show_backend_settings_triggered 信号现在更具体地用于 Matplotlib 设置
    show_matplotlib_settings_triggered = Signal() 

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化导航栏的用户界面元素。"""
        main_layout = QVBoxLayout()
        
        # --- 菜单栏示例 ---
        self.menu_bar = QMenuBar(self)
        file_menu    = self.menu_bar.addMenu("文件")
        edit_menu    = self.menu_bar.addMenu("编辑")
        view_menu    = self.menu_bar.addMenu("视图")
        
        # === 修改：Backend Settings 菜单 ===
        self.backend_settings_menu = self.menu_bar.addMenu("后端设置") 
        
        # 新增子菜单项：Matplotlib 设置
        self.show_matplotlib_settings_action = QAction("Matplotlib 设置...", self)
        # 连接到新的信号
        self.show_matplotlib_settings_action.triggered.connect(self.show_matplotlib_settings_triggered.emit)
        self.backend_settings_menu.addAction(self.show_matplotlib_settings_action)

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
        
        # 关于菜单
        about_menu = self.menu_bar.addMenu("关于")

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
        show_about_action = QAction("关于 FeynPlot GUI", self)
        show_about_action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(show_about_action)
        # --- 完善结束 ---

        # --- 工具栏示例 ---
        self.tool_bar = QToolBar("主要操作", self)
        self.tool_bar.setMovable(False)

        # 直接引用按钮，方便后续控制其 enabled 状态
        self.add_line_button = QPushButton("添加线条")
        self.add_line_button.clicked.connect(self.add_line_button_clicked.emit)
        self.tool_bar.addWidget(self.add_line_button)

        self.add_vertex_button = QPushButton("添加顶点")
        self.add_vertex_button.clicked.connect(self.add_vertex_button_clicked.emit)
        self.tool_bar.addWidget(self.add_vertex_button)

        main_layout.addWidget(self.tool_bar)

        self.setLayout(main_layout)

    # --- 槽函数和控制方法 ---
    def _on_edit_object_triggered(self):
        """内部槽函数，用于根据当前选中类型发出特定编辑信号"""
        print("编辑对象操作被触发。")

    def set_object_menu_enabled(self, enabled: bool):
        """
        设置“对象”菜单的启用状态。
        """
        self.obj_menu.setEnabled(enabled)
            
    def set_add_line_enabled(self, enabled: bool):
        """
        启用/禁用“添加线条”菜单项和工具栏按钮。
        """
        # 控制菜单项
        for action in self.menu_bar.actions():
            if action.text() == "编辑": # 找到“编辑”菜单
                for sub_action in action.menu().actions():
                    if sub_action.text() == "添加线条":
                        sub_action.setEnabled(enabled)
                        break
                break
        # 控制工具栏按钮
        self.add_line_button.setEnabled(enabled)
        
    def set_add_vertex_enabled(self, enabled: bool):
        """
        启用/禁用“添加顶点”菜单项和工具栏按钮。
        """
        # 控制菜单项
        for action in self.menu_bar.actions():
            if action.text() == "编辑": # 找到“编辑”菜单
                for sub_action in action.menu().actions():
                    if sub_action.text() == "添加顶点":
                        sub_action.setEnabled(enabled)
                        break
                break
        # 控制工具栏按钮
        self.add_vertex_button.setEnabled(enabled)

    def set_edit_object_action_enabled(self, enabled: bool):
        """
        设置“编辑属性”动作的启用状态。
        """
        self.edit_obj_action.setEnabled(enabled)

    def set_delete_object_action_enabled(self, enabled: bool):
        """
        设置“删除对象”动作的启用状态。
        """
        self.delete_obj_action.setEnabled(enabled)

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