# feynplot_gui/widgets/navigation_bar_widget.py

from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QMenuBar, QToolBar, QMenu, QWidget
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Signal
from typing import Optional 

class NavigationBarWidget(QWidget):
    # 定义信号，这些信号将被 MainController 或 NavigationBarController 监听
    add_line_button_clicked = Signal()
    add_vertex_button_clicked = Signal()
    save_project_action_triggered = Signal()
    load_project_action_triggered = Signal()
    
    # 当编辑顶点或线条的操作被触发时
    edit_selected_vertex_triggered = Signal()
    edit_selected_line_triggered = Signal()
    delete_selected_object_triggered = Signal() # 可以有一个通用的删除信号，具体删除什么由控制器判断

    # 用于触发后端设置对话框
    show_matplotlib_settings_triggered = Signal() 

    # --- 【新增】编辑所有顶点的信号 ---
    edit_all_vertices_triggered = Signal()
    
    # --- 【新增】编辑所有线条的信号 ---
    edit_all_lines_triggered = Signal()
    
    # --- 【重要】这些是信号，保持为类属性，不要在 __init__ 中用 self. 重新赋值 ---
    hide_all_vertices_requested = Signal()
    show_all_vertices_triggered = Signal()
    hide_all_vertex_labels_requested = Signal()
    show_all_vertex_labels_triggered = Signal()
    # --- 信号定义结束 ---


    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # 【重要修改】只将 QAction 实例、QPushButton 实例和 QMenu 实例声明为类的属性并初始化为 None
        # 移除此处对信号的初始化，例如：self.hide_all_vertices_triggered: Signal = None
        self.save_action: Optional[QAction] = None
        self.load_action: Optional[QAction] = None
        self.obj_menu: Optional[QMenu] = None 
        self.edit_obj_action: Optional[QAction] = None
        self.delete_obj_action: Optional[QAction] = None
        self.add_line_button: Optional[QPushButton] = None
        self.add_vertex_button: Optional[QPushButton] = None
        self.edit_all_vertices_action: Optional[QAction] = None
        self.edit_all_lines_action: Optional[QAction] = None # New: Edit all lines action
        self.view_menu: Optional[QMenu] = None 
        self.hide_all_vertices_action: Optional[QAction] = None
        self.show_all_vertices_action: Optional[QAction] = None
        self.hide_all_vertex_labels_action: Optional[QAction] = None
        self.show_all_vertex_labels_action: Optional[QAction] = None

        self.init_ui()

    def init_ui(self):
        """初始化导航栏的用户界面元素。"""
        main_layout = QVBoxLayout()
        
        # --- 菜单栏示例 ---
        self.menu_bar = QMenuBar(self)
        file_menu    = self.menu_bar.addMenu("文件")
        edit_menu    = self.menu_bar.addMenu("编辑") # 获取编辑菜单的引用
        self.view_menu    = self.menu_bar.addMenu("视图") # Assign to self for external control
        
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
        self.save_action = QAction("保存项目", self)
        self.save_action.triggered.connect(self.save_project_action_triggered.emit)
        file_menu.addAction(self.save_action)

        self.load_action = QAction("加载项目", self)
        self.load_action.triggered.connect(self.load_project_action_triggered.emit)
        file_menu.addAction(self.load_action)

        # 编辑菜单项
        add_vertex_action = QAction("添加顶点", self)
        add_vertex_action.triggered.connect(self.add_vertex_button_clicked.emit)
        edit_menu.addAction(add_vertex_action)

        add_line_action = QAction("添加线条", self)
        add_line_action.triggered.connect(self.add_line_button_clicked.emit)
        edit_menu.addAction(add_line_action)

        # --- 在“编辑”菜单中添加“编辑所有顶点”选项 ---
        self.edit_all_vertices_action = QAction("编辑所有顶点", self)
        self.edit_all_vertices_action.triggered.connect(self.edit_all_vertices_triggered.emit)
        edit_menu.addAction(self.edit_all_vertices_action)
        # --- 结束 ---

        # --- 【新增】在“编辑”菜单中添加“编辑所有线条”选项 ---
        self.edit_all_lines_action = QAction("编辑所有线条", self)
        self.edit_all_lines_action.triggered.connect(self.edit_all_lines_triggered.emit)
        edit_menu.addAction(self.edit_all_lines_action)
        # --- 新增结束 ---

        # --- View Menu Items ---
        self.hide_all_vertices_action = QAction("隐藏所有顶点", self)
        self.hide_all_vertices_action.triggered.connect(self.hide_all_vertices_requested.emit)
        self.view_menu.addAction(self.hide_all_vertices_action)

        self.show_all_vertices_action = QAction("显示所有顶点", self)
        self.show_all_vertices_action.triggered.connect(self.show_all_vertices_triggered.emit)
        self.view_menu.addAction(self.show_all_vertices_action)

        self.hide_all_vertex_labels_action = QAction("隐藏所有顶点标签", self)
        self.hide_all_vertex_labels_action.triggered.connect(self.hide_all_vertex_labels_requested.emit)
        self.view_menu.addAction(self.hide_all_vertex_labels_action)

        self.show_all_vertex_labels_action = QAction("显示所有顶点标签", self)
        self.show_all_vertex_labels_action.triggered.connect(self.show_all_vertex_labels_triggered.emit)
        self.view_menu.addAction(self.show_all_vertex_labels_action)

        self.set_view_menu_actions_enabled(False) # Default to disabled
        # --- View Menu Items End ---

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
        # 此处需要 NavigationBarController 来判断当前选中对象类型并发出正确的信号
        # 例如：
        # if isinstance(self.main_controller.get_selected_item(), Vertex):
        #    self.edit_selected_vertex_triggered.emit()
        # elif isinstance(self.main_controller.get_selected_item(), Line):
        #    self.edit_selected_line_triggered.emit()

    def set_object_menu_enabled(self, enabled: bool):
        """
        设置“对象”菜单的启用状态。
        """
        if self.obj_menu:
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
        if self.add_line_button:
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
        if self.add_vertex_button:
            self.add_vertex_button.setEnabled(enabled)

    # --- 控制“编辑所有顶点”菜单项的启用/禁用状态的方法 ---
    def set_edit_all_vertices_enabled(self, enabled: bool):
        """
        设置“编辑所有顶点”动作的启用状态。
        """
        if self.edit_all_vertices_action:
            self.edit_all_vertices_action.setEnabled(enabled)
    # --- 结束 ---

    # --- 【新增】控制“编辑所有线条”菜单项的启用/禁用状态的方法 ---
    def set_edit_all_lines_enabled(self, enabled: bool):
        """
        设置“编辑所有线条”动作的启用状态。
        """
        if self.edit_all_lines_action:
            self.edit_all_lines_action.setEnabled(enabled)
    # --- 新增结束 ---

    def set_edit_object_action_enabled(self, enabled: bool):
        """
        设置“编辑属性”动作的启用状态。
        """
        if self.edit_obj_action:
            self.edit_obj_action.setEnabled(enabled)

    def set_delete_object_action_enabled(self, enabled: bool):
        """
        设置“删除对象”动作的启用状态。
        """
        if self.delete_obj_action:
            self.delete_obj_action.setEnabled(enabled)

    # --- set_save_load_actions_enabled 方法 ---
    def set_save_load_actions_enabled(self, save_enabled: bool, load_enabled: bool):
        """
        设置“保存项目”和“加载项目”动作的启用状态。
        """
        if self.save_action:
            self.save_action.setEnabled(save_enabled)
        if self.load_action:
            self.load_action.setEnabled(load_enabled)
    # --- 结束 ---

    # --- 用于控制“视图”菜单中动作的方法 ---
    def set_view_menu_actions_enabled(self, enabled: bool):
        """
        设置“视图”菜单中所有与图内容相关的动作的启用状态。
        """
        if self.hide_all_vertices_action:
            self.hide_all_vertices_action.setEnabled(enabled)
        if self.show_all_vertices_action:
            self.show_all_vertices_action.setEnabled(enabled)
        if self.hide_all_vertex_labels_action:
            self.hide_all_vertex_labels_action.setEnabled(enabled)
        if self.show_all_vertex_labels_action:
            self.show_all_vertex_labels_action.setEnabled(enabled)
    # --- 结束 ---


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