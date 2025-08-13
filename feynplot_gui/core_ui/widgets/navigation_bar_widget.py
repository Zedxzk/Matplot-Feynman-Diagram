from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QMenuBar, QToolBar, QMenu, QSpinBox, QLabel, QCheckBox, QDoubleSpinBox, QHBoxLayout # Import QSpinBox and QLabel
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, Signal
from typing import Optional
from feynplot_gui.default.default_settings import canvas_widget_default_settings as cw_default_settings
from feynplot_gui.default.default_settings import canvas_controller_default_settings as cc_default_settings
from feynplot_gui.default.default_settings import navigation_widget_default_settings as nw_default_settings



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

    # --- 编辑所有顶点的信号 ---
    edit_all_vertices_triggered = Signal()

    # --- 编辑所有线条的信号 ---
    edit_all_lines_triggered = Signal()

    # --- 这些是信号，保持为类属性，不要在 __init__ 中用 self. 重新赋值 ---
    hide_all_vertices_requested = Signal()
    show_all_vertices_triggered = Signal()
    hide_all_vertex_labels_requested = Signal()
    show_all_vertex_labels_triggered = Signal()
    
    # 【修改】自动缩放信号，现在只在点击时触发，不携带状态
    toggle_auto_scale_requested = Signal() 
    toggle_gride_points_mode = Signal() 
    toggle_use_relative_unit = Signal() # <--- **新增信号：切换相对单位使用状态**


    # --- 【新增】画布更新间隔调整信号 ---
    # 当用户通过UI（QSpinBox）改变间隔时，NavigationBarWidget发出此信号
    canvas_update_interval_changed_ui = Signal(int) # 发送新的间隔值 (ms)
    canvas_set_range = Signal(float, float, float, float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # 【重要修改】只将 QAction 实例、QPushButton 实例和 QMenu 实例声明为类的属性并初始化为 None
        self.save_action: Optional[QAction] = None
        self.load_action: Optional[QAction] = None
        self.obj_menu: Optional[QMenu] = None
        self.edit_obj_action: Optional[QAction] = None
        self.delete_obj_action: Optional[QAction] = None
        self.add_line_button: Optional[QPushButton] = None
        self.add_vertex_button: Optional[QPushButton] = None
        self.edit_all_vertices_action: Optional[QAction] = None
        self.edit_all_lines_action: Optional[QAction] = None 
        self.view_menu: Optional[QMenu] = None
        self.hide_all_vertices_action: Optional[QAction] = None
        self.show_all_vertices_action: Optional[QAction] = None
        self.hide_all_vertex_labels_action: Optional[QAction] = None
        self.show_all_vertex_labels_action: Optional[QAction] = None
        # --- 【修改】自动缩放动作的属性，现在是一个普通 Action ---
        self.auto_scale_action: Optional[QAction] = None
        
        # --- 【新增】画布更新间隔的QSpinBox属性 ---
        self.canvas_update_interval_spinbox: Optional[QSpinBox] = None


        self.init_ui()

    def init_ui(self):
        """初始化导航栏的用户界面元素。"""
        main_layout = QVBoxLayout(self)

        # --- 菜单栏示例 ---
        self.menu_bar = QMenuBar(self)
        file_menu    = self.menu_bar.addMenu("文件")
        edit_menu    = self.menu_bar.addMenu("编辑") # 获取编辑菜单的引用
        self.view_menu      = self.menu_bar.addMenu("视图") # Assign to self for external control

        # === Backend Settings 菜单 ===
        self.backend_settings_menu = self.menu_bar.addMenu("后端设置")

        # 新增子菜单项：Matplotlib 设置
        self.show_matplotlib_settings_action = QAction("Matplotlib 设置...", self)
        self.show_matplotlib_settings_action.triggered.connect(self.show_matplotlib_settings_triggered.emit)
        self.backend_settings_menu.addAction(self.show_matplotlib_settings_action)

        # === 新增：对象操作菜单 ===
        self.obj_menu = self.menu_bar.addMenu("对象")
        self.obj_menu.setEnabled(False) # 默认禁用

        self.edit_obj_action = QAction("编辑属性", self)
        self.edit_obj_action.setEnabled(False)
        self.edit_obj_action.triggered.connect(self._on_edit_object_triggered) # 内部处理，转发给控制器
        self.obj_menu.addAction(self.edit_obj_action)

        self.delete_obj_action = QAction("删除对象", self)
        self.delete_obj_action.setEnabled(False)
        self.delete_obj_action.triggered.connect(self.delete_selected_object_triggered.emit)
        self.obj_menu.addAction(self.delete_obj_action)

        # 关于菜单
        about_menu = self.menu_bar.addMenu("关于")

        # 文件菜单项
        self.load_action = QAction("加载项目", self)
        self.load_action.triggered.connect(self.load_project_action_triggered.emit)
        file_menu.addAction(self.load_action)

        self.save_action = QAction("保存项目", self)
        self.save_action.triggered.connect(self.save_project_action_triggered.emit)
        file_menu.addAction(self.save_action)

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

        # --- 【修改】自动缩放作为一个普通 QAction ---
        self.auto_scale_action = QAction("自动调整画布", self) # 文本可以更明确
        self.auto_scale_action.triggered.connect(self.toggle_auto_scale_requested.emit) # 连接到 triggered 信号
        self.view_menu.addAction(self.auto_scale_action)
        # --- 修改结束 ---

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
        self.add_line_button = QPushButton(self.tr("添加线条"))
        self.add_line_button.clicked.connect(self.add_line_button_clicked.emit)
        self.tool_bar.addWidget(self.add_line_button)

        self.add_vertex_button = QPushButton(self.tr("添加顶点"))
        self.add_vertex_button.clicked.connect(self.add_vertex_button_clicked.emit)
        self.tool_bar.addWidget(self.add_vertex_button)
        
        # # --- 【新增】画布更新间隔的QSpinBox ---
        # self.tool_bar.addSeparator() # 添加分隔符，使UI更整洁
        # self.tool_bar.addWidget(QLabel("画布拖动更新间隔:", self)) # 添加标签
        # self.canvas_update_interval_spinbox = QSpinBox(self)
        # self.canvas_update_interval_spinbox.setRange(0, 1000) # 间隔范围 0ms 到 1000ms
        # self.canvas_update_interval_spinbox.setSingleStep(1) # 步长 1ms
        # self.canvas_update_interval_spinbox.setSuffix(" ms") # 单位后缀
        # self.canvas_update_interval_spinbox.setValue(cw_default_settings['SIGNAL_INTERVAL_MS'])
        # # 连接 spinbox 的 valueChanged 信号到我们自定义的 signal
        # self.canvas_update_interval_spinbox.valueChanged.connect(self.canvas_update_interval_changed_ui)
        # self.tool_bar.addWidget(self.canvas_update_interval_spinbox)


        # 添加网格模式
        self.tool_bar.addSeparator() # 添加分隔符，使UI更整洁
        self.tool_bar.addWidget(QLabel("仅允许拖动到格点上:", self)) # 添加标签

        # 添加一个选项框（QCheckBox）
        self.snap_to_grid_checkbox = QCheckBox(self)
        self.tool_bar.addWidget(self.snap_to_grid_checkbox)

        # 设置默认状态和关联信号
        # 默认状态从 main_controller 获取
        self.snap_to_grid_checkbox.setChecked(cc_default_settings['ONLY_ALLOW_GRID_POINTS'])
        # 连接 toggled 信号到一个处理函数
        self.snap_to_grid_checkbox.toggled.connect(self._on_snap_to_grid_toggled)


        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(QLabel("相对对象尺寸:", self))

        self.relative_units_checkbox = QCheckBox("随图像缩放", self)
        
        # 添加鼠标悬停的注释（Tooltip）
        # 这行代码在 PySide6 和 PyQt5/6 中都是通用的
        self.relative_units_checkbox.setToolTip("开启此项，绘图元素的尺寸（如文字、标记）将随图像的缩放而自动调整；关闭则保持绝对像素大小。")
        
        self.tool_bar.addWidget(self.relative_units_checkbox)

        self.relative_units_checkbox.setChecked(nw_default_settings['use_relative_unit'])
        self.relative_units_checkbox.stateChanged.connect(self._on_relative_units_toggled)

        

        # 创建一个容器小部件来放置
        # 数值框
        # --- 添加 X 轴范围显示 ---
        # self.tool_bar.addWidget(QLabel("X范围:", self))

        # # X min
        # self.tool_bar.addWidget(QLabel("min:", self))
        # self.x_min_spinbox = QDoubleSpinBox(self)
        # self.x_min_spinbox.setRange(-1000.0, 1000.0)
        # self.x_min_spinbox.setValue(-50.0)
        # # 设置键盘跟踪为False，这样只有在失去焦点或按Enter时才触发valueChanged
        # self.x_min_spinbox.setKeyboardTracking(False)
        # self.tool_bar.addWidget(self.x_min_spinbox)

        # # X max
        # self.tool_bar.addWidget(QLabel("max:", self))
        # self.x_max_spinbox = QDoubleSpinBox(self)
        # self.x_max_spinbox.setRange(-1000.0, 1000.0)
        # self.x_max_spinbox.setValue(50.0)
        # self.x_max_spinbox.setKeyboardTracking(False)
        # self.tool_bar.addWidget(self.x_max_spinbox)

        # # --- 添加 Y 轴范围显示 ---
        # self.tool_bar.addSeparator()
        # self.tool_bar.addWidget(QLabel("Y范围:", self))

        # # Y min
        # self.y_min_spinbox = QDoubleSpinBox(self)
        # self.tool_bar.addWidget(QLabel("min:", self))
        # self.y_min_spinbox.setRange(-1000.0, 1000.0)
        # self.y_min_spinbox.setValue(-50.0)
        # self.y_min_spinbox.setKeyboardTracking(False)
        # self.tool_bar.addWidget(self.y_min_spinbox)

        # # Y max
        # self.y_max_spinbox = QDoubleSpinBox(self)
        # self.tool_bar.addWidget(QLabel("max:", self))
        # self.y_max_spinbox.setRange(-1000.0, 1000.0)
        # self.y_max_spinbox.setValue(50.0)
        # self.y_max_spinbox.setKeyboardTracking(False)
        # self.tool_bar.addWidget(self.y_max_spinbox)

        # --- 将所有信号连接到同一个槽函数 ---
        # 方案1: 使用valueChanged信号 + setKeyboardTracking(False)
        # self.x_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        # self.x_max_spinbox.valueChanged.connect(self._on_canvas_range_set)
        # self.y_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        # self.y_max_spinbox.valueChanged.connect(self._on_canvas_range_set)

        # main_layout.addWidget(self.tool_bar)
        # --- bar 1 新增结束 ---
        # --- bar 2 新增开始 ---

       # --- 工具栏 2 ---
        self.second_tool_bar = QToolBar("画布控制区", self)

        self.second_tool_bar.setMovable(False)
        self.second_tool_bar.addSeparator()
        self.second_tool_bar.addWidget(QLabel("画布拖动更新间隔:", self))
        self.canvas_update_interval_spinbox = QSpinBox(self)
        self.canvas_update_interval_spinbox.setRange(0, 1000)
        self.canvas_update_interval_spinbox.setSingleStep(1)
        self.canvas_update_interval_spinbox.setSuffix(" ms")
        self.canvas_update_interval_spinbox.setValue(cw_default_settings['SIGNAL_INTERVAL_MS'])
        self.canvas_update_interval_spinbox.valueChanged.connect(self.canvas_update_interval_changed_ui)
        self.second_tool_bar.addWidget(self.canvas_update_interval_spinbox)

        main_layout.addWidget(self.second_tool_bar)

        self.second_tool_bar.addSeparator()
        # 创建一个容器小部件来放置数值框
        # --- 添加 X 轴范围显示 ---
        self.second_tool_bar.addWidget(QLabel("X范围:", self))

        # X min
        self.second_tool_bar.addWidget(QLabel("min:", self))
        self.x_min_spinbox = QDoubleSpinBox(self)
        self.x_min_spinbox.setRange(-1000.0, 1000.0)
        self.x_min_spinbox.setValue(-50.0)
        # 设置键盘跟踪为False，这样只有在失去焦点或按Enter时才触发valueChanged
        self.x_min_spinbox.setKeyboardTracking(False)
        self.second_tool_bar.addWidget(self.x_min_spinbox)

        # X max
        self.second_tool_bar.addWidget(QLabel("max:", self))
        self.x_max_spinbox = QDoubleSpinBox(self)
        self.x_max_spinbox.setRange(-1000.0, 1000.0)
        self.x_max_spinbox.setValue(50.0)
        self.x_max_spinbox.setKeyboardTracking(False)
        self.second_tool_bar.addWidget(self.x_max_spinbox)

        # --- 添加 Y 轴范围显示 ---
        self.second_tool_bar.addSeparator()
        self.second_tool_bar.addWidget(QLabel("Y范围:", self))

        # Y min
        self.y_min_spinbox = QDoubleSpinBox(self)
        self.second_tool_bar.addWidget(QLabel("min:", self))
        self.y_min_spinbox.setRange(-1000.0, 1000.0)
        self.y_min_spinbox.setValue(-50.0)
        self.y_min_spinbox.setKeyboardTracking(False)
        self.second_tool_bar.addWidget(self.y_min_spinbox)

        # Y max
        self.y_max_spinbox = QDoubleSpinBox(self)
        self.second_tool_bar.addWidget(QLabel("max:", self))
        self.y_max_spinbox.setRange(-1000.0, 1000.0)
        self.y_max_spinbox.setValue(50.0)
        self.y_max_spinbox.setKeyboardTracking(False)
        self.second_tool_bar.addWidget(self.y_max_spinbox)


        self.x_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.x_max_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.y_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.y_max_spinbox.valueChanged.connect(self._on_canvas_range_set)

        
        # 【重要改动】: 这行是必须的，将布局应用到这个 QWidget
        self.setLayout(main_layout) 


    # --- 槽函数和控制方法 ---
    def _on_edit_object_triggered(self):
        """内部槽函数，用于根据当前选中类型发出特定编辑信号 (此信号将被 NavigationBarController 监听)"""
        # 这个方法现在由 NavigationBarController 处理，此处只需触发通用信号
        # 如果需要，可以根据选中的对象类型在这里发射不同的信号，但目前设计是控制器判断
        self.edit_selected_vertex_triggered.emit() # 假设会由控制器根据选中类型转发
        self.edit_selected_line_triggered.emit()   # 假设会由控制器根据选中类型转发

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
        现在也包括“自动调整画布”动作。
        """
        if self.hide_all_vertices_action:
            self.hide_all_vertices_action.setEnabled(enabled)
        if self.show_all_vertices_action:
            self.show_all_vertices_action.setEnabled(enabled)
        if self.hide_all_vertex_labels_action:
            self.hide_all_vertex_labels_action.setEnabled(enabled)
        if self.show_all_vertex_labels_action:
            self.show_all_vertex_labels_action.setEnabled(enabled)
        # --- 【修改】控制“切换自动调整画布”动作的启用状态 ---
        if self.auto_scale_action:
            self.auto_scale_action.setEnabled(enabled)
        # --- 新增：启用/禁用画布更新间隔QSpinBox ---
        if self.canvas_update_interval_spinbox:
            self.canvas_update_interval_spinbox.setEnabled(enabled)
        # --- 修改结束 ---

    # --- 【新增】设置 Canvas Update Interval SpinBox 的值 ---
    def set_canvas_update_interval_value(self, value: int):
        """
        程序化地设置画布更新间隔QSpinBox的值。
        这用于在控制器初始化或状态同步时更新UI。
        Args:
            value: 要设置的毫秒值。
        """
        if self.canvas_update_interval_spinbox:
            # 避免触发valueChanged信号循环，断开再连接
            self.canvas_update_interval_spinbox.valueChanged.disconnect(self.canvas_update_interval_changed_ui)
            self.canvas_update_interval_spinbox.setValue(value)
            self.canvas_update_interval_spinbox.valueChanged.connect(self.canvas_update_interval_changed_ui)

    # --- 【新增】获取 Canvas Update Interval SpinBox 的值 ---
    def get_canvas_update_interval_value(self) -> int:
        """
        获取当前画布更新间隔QSpinBox的值。
        Returns:
            当前设置的毫秒值。
        """
        if self.canvas_update_interval_spinbox:
            return self.canvas_update_interval_spinbox.value()
        return 0 # 默认值

    def _on_snap_to_grid_toggled(self, checked: bool):
        """
        当“仅允许拖动到格点上”复选框状态改变时被调用。
        更新 canvas_controller 中的 only_allow_grid_points 属性。
        """
        self.toggle_gride_points_mode.emit()


    def _on_relative_units_toggled(self, checked: bool):
        """
        当“相对对象尺寸”复选框状态改变时被调用。
        更新 navigation_widget_default_settings 中的 use_relative_unit 属性。
        """
        self.toggle_use_relative_unit.emit()


    def update_plot_limits(self, x_min, x_max, y_min, y_max):
        """
        这个公共接口用于外部修改UI数值，但不会触发自定义信号。
        """
        # 在更新数值时，确保定时器是停止的
        # self.update_timer.stop() 
        
        # 暂时断开信号连接
        self.x_min_spinbox.valueChanged.disconnect(self._on_canvas_range_set)
        self.x_max_spinbox.valueChanged.disconnect(self._on_canvas_range_set)
        self.y_min_spinbox.valueChanged.disconnect(self._on_canvas_range_set)
        self.y_max_spinbox.valueChanged.disconnect(self._on_canvas_range_set)
        
        # 调用 setValue() 更新数值
        self.x_min_spinbox.setValue(x_min)
        self.x_max_spinbox.setValue(x_max)
        self.y_min_spinbox.setValue(y_min)
        self.y_max_spinbox.setValue(y_max)
        
        # 重新连接信号
        self.x_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.x_max_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.y_min_spinbox.valueChanged.connect(self._on_canvas_range_set)
        self.y_max_spinbox.valueChanged.connect(self._on_canvas_range_set)


    def _on_canvas_range_set(self):
        """
        这个槽函数会在任何一个 QDoubleSpinBox 的值改变时被触发。
        它会立即获取所有四个值，并将它们作为一个整体传递。
        """
        # 获取所有 SpinBox 的当前值
        x_min = self.x_min_spinbox.value()
        x_max = self.x_max_spinbox.value()
        y_min = self.y_min_spinbox.value()
        y_max = self.y_max_spinbox.value()
        
        # 在这里调用你的核心处理函数，并传入所有值
        self.canvas_set_range.emit(x_min, x_max, y_min, y_max)




    def _show_about_dialog(self):
        """
        显示“关于”对话框。
        """
        QMessageBox.about(self, "关于 FeynPlot GUI",
                          "这是一个用于绘制费曼图的简单GUI应用。\n"
                          "版本: 1.0   Release date: 2025.6.14\n"
                          "作者: ZED(武汉大学->香港中文大学)\n"
                          "邮箱：zedxzk@gmail.com\n"
                          "GitHub: https://github.com/Zedxzk/Matplot-Feynman-Diagram\n"
                          )