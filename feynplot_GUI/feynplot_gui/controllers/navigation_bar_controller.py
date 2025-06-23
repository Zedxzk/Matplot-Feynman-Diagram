# feynplot_gui/controllers/navigation_bar_controller.py

from PySide6.QtCore import QObject, Signal
from feynplot_gui.widgets.navigation_bar_widget import NavigationBarWidget
# 【Important Change】Remove direct import of MainController to prevent circular imports
# from feynplot_gui.controllers.main_controller import MainController 
from feynplot.core.vertex import Vertex # 用于类型提示
from feynplot.core.line import Line     # 用于类型提示

# 导入 Matplotlib 设置对话框 (你需要创建这个文件和类)
from feynplot_gui.dialogs.plt_dialogs.matplotlib_settings_dialog import MatplotlibSettingsDialog 

import matplotlib.pyplot as plt # 导入 matplotlib 用于应用 rcParams

class NavigationBarController(QObject):
    # 定义信号，这些信号将由 MainController 监听，用于触发核心业务逻辑
    # 这些信号现在从 NavigationBarController 发出
    save_project_requested = Signal()
    load_project_requested = Signal()
    add_vertex_requested = Signal()
    add_line_requested = Signal()
    edit_selected_vertex_requested = Signal()
    edit_selected_line_requested = Signal()
    delete_selected_object_requested = Signal()
    # show_matplotlib_settings_requested 信号现在将直接连接到内部槽函数，不再向外暴露
    # 如果 MainController 确实需要知道 Matplotlib 设置对话框被打开，可以添加一个独立的信号

    # NavigationBarController 自己的状态更新信号，用于通知外部（如MainController）UI状态变化
    status_message = Signal(str) # 用于发送状态消息

    def __init__(self, navigation_bar_widget: NavigationBarWidget, main_controller: 'MainController'):
        super().__init__()

        self.navigation_bar_widget = navigation_bar_widget
        self.main_controller = main_controller # 仍然持有MainController的引用，用于转发业务请求

        # 初始化 Matplotlib 设置对话框实例
        # 对话框的 parent 设置为 navigation_bar_widget，确保其生命周期和层级关系正确
        self._matplotlib_settings_dialog = MatplotlibSettingsDialog(parent=self.navigation_bar_widget)
        # 连接对话框的设置应用信号到本控制器的槽函数
        self._matplotlib_settings_dialog.settings_applied.connect(self._on_matplotlib_settings_applied)

        self.setup_connections()
        # 初始状态更新
        self.update_object_menu_status(None) # 初始时，没有选中对象，禁用编辑/删除相关UI

    def setup_connections(self):
        """连接导航栏部件的信号到控制器槽函数，并发出请求信号给MainController。"""
        # 文件菜单动作
        self.navigation_bar_widget.save_project_action_triggered.connect(self.save_project_requested.emit)
        self.navigation_bar_widget.load_project_action_triggered.connect(self.load_project_requested.emit)
        
        # 编辑菜单动作
        # 连接到 NavigationBarController 自己的槽函数，然后由这些槽函数发出业务请求信号
        self.navigation_bar_widget.add_vertex_button_clicked.connect(self._on_add_vertex_ui_triggered)
        self.navigation_bar_widget.add_line_button_clicked.connect(self._on_add_line_ui_triggered)
        
        # “对象”菜单的“编辑属性”和“删除对象”动作
        self.navigation_bar_widget.edit_obj_action.triggered.connect(self._on_edit_object_ui_triggered)
        self.navigation_bar_widget.delete_obj_action.triggered.connect(self._on_delete_object_ui_triggered)

        # 后端设置菜单动作
        # 直接连接到 NavigationBarController 自己的槽函数，由它来管理和显示对话框
        self.navigation_bar_widget.show_matplotlib_settings_triggered.connect(self._on_show_matplotlib_settings_ui_triggered)

        # 连接到 MainController 的选中改变信号，以便更新自身UI状态
        if hasattr(self.main_controller, 'selection_changed'):
            self.main_controller.selection_changed.connect(self.update_object_menu_status)
        else:
            self.status_message.emit("警告：MainController未提供selection_changed信号。对象菜单状态更新可能不正确。")

    ## --- NavigationBarController 内部的 UI 逻辑处理槽函数 ---
    
    def _on_add_vertex_ui_triggered(self):
        """处理UI的添加顶点触发，并发出业务请求信号。"""
        self.status_message.emit("请求添加顶点。")
        self.add_vertex_requested.emit()

    def _on_add_line_ui_triggered(self):
        """处理UI的添加线条触发，并发出业务请求信号。"""
        self.status_message.emit("请求添加线条。")
        self.add_line_requested.emit()

    def _on_edit_object_ui_triggered(self):
        """处理UI的编辑对象触发，并根据当前选中类型发出相应请求信号。"""
        # 从MainController获取当前选中项，然后根据类型发出更具体的信号
        selected_item = self.main_controller.get_selected_item() # 假设MainController提供此方法
        if isinstance(selected_item, Vertex):
            self.status_message.emit(f"请求编辑顶点: {selected_item.id}")
            self.edit_selected_vertex_requested.emit() # 可以在这里传递 selected_item.id 或 selected_item 对象
        elif isinstance(selected_item, Line):
            self.status_message.emit(f"请求编辑线条: {selected_item.id}")
            self.edit_selected_line_requested.emit() # 可以在这里传递 selected_item.id 或 selected_item 对象
        else:
            self.status_message.emit("没有选中的顶点或线条可供编辑。")

    def _on_delete_object_ui_triggered(self):
        """处理UI的删除对象触发，并发出通用删除请求信号。"""
        self.status_message.emit("请求删除选中对象。")
        self.delete_selected_object_requested.emit()

    def _on_show_matplotlib_settings_ui_triggered(self):
        """
        处理UI触发的显示Matplotlib设置请求。
        这是 NavigationBarController 自己的业务逻辑：管理 Matplotlib 设置对话框的显示。
        """
        self.status_message.emit("请求显示Matplotlib后端设置。")
        
        # 1. 对话框在初始化时会读取 Matplotlib 当前的 rcParams。
        # 如果有额外的持久化配置（例如从文件加载），可以在这里通过 _matplotlib_settings_dialog.set_settings() 传入。
        # 目前我们依赖对话框自身加载当前的 Matplotlib rcParams。

        # 2. 显示对话框
        self._matplotlib_settings_dialog.exec()
        # 对话框关闭后，如果点击的是OK或Apply，_on_matplotlib_settings_applied 会被调用

    def _on_matplotlib_settings_applied(self, settings: dict):
        """
        处理 Matplotlib 设置对话框发出的设置应用信号。
        这是 NavigationBarController 自己的业务逻辑：将设置应用到 Matplotlib。
        """
        self.status_message.emit("Matplotlib 设置已从对话框接收。")
        try:
            # 将对话框返回的设置应用到 Matplotlib 的全局 rcParams
            for key, value in settings.items():
                try:
                    # Matplotlib 的 font.family 可以接受字符串或字符串列表
                    if key == "font.family" and isinstance(value, str):
                        plt.rcParams[key] = [value] # 确保是列表形式
                    else:
                        plt.rcParams[key] = value
                    self.status_message.emit(f"已应用 Matplotlib 参数: {key} = {value}")
                except KeyError:
                    self.status_message.emit(f"警告: Matplotlib中不存在参数 '{key}'，跳过。")
                except Exception as e:
                    self.status_message.emit(f"警告: 应用 Matplotlib 参数 '{key}' 失败: {e}")
            
            # TODO: 在此添加将当前设置保存到本地配置文件（如JSON）的逻辑
            # 目前，我们只是应用到内存中的 rcParams。
            # save_settings(settings) # 如果有配置文件管理器，可以在这里调用保存

            # 刷新 Matplotlib 的字体缓存（如果需要）
            # import matplotlib.font_manager as fm
            # fm._clear_cached_fonts() # 如果 Matplotlib 版本支持且需要强制刷新字体

            # 通知 MainController 更新所有视图，以反映新的设置
            # 这是关键的一步，确保所有绘图和列表都更新
            if hasattr(self.main_controller, 'update_all_views'):
                self.main_controller.update_all_views() # <--- 修正点
                self.status_message.emit("已通知主控制器更新所有视图以反映新设置。")
            else:
                self.status_message.emit("警告：MainController未提供update_all_views方法，视图可能未完全刷新。")

        except Exception as e:
            self.status_message.emit(f"应用Matplotlib设置时发生意外错误: {e}")


    ## --- UI 状态更新方法 ---

    def update_object_menu_status(self, selected_item: object):
        """
        根据 MainController 报告的当前选中项更新“对象”菜单及相关操作的启用/禁用状态。
        此方法监听 MainController 的 selection_changed 信号。
        """
        is_item_selected = (selected_item is not None)
        
        # 1. 控制“对象”菜单本身是否启用
        self.navigation_bar_widget.set_object_menu_enabled(is_item_selected)

        # 2. 控制“编辑属性”动作是否启用
        # 只有在选中顶点或线条时才启用编辑
        can_edit = False
        if isinstance(selected_item, (Vertex, Line)):
            can_edit = True
        self.navigation_bar_widget.set_edit_object_action_enabled(can_edit)

        # 3. 控制“删除对象”动作是否启用
        # 只要有任何可删除的对象选中，就启用删除
        self.navigation_bar_widget.set_delete_object_action_enabled(is_item_selected)

        self.status_message.emit(f"菜单状态更新：{'启用' if is_item_selected else '禁用'}对象操作。")

    def set_add_actions_enabled(self, enabled: bool):
        """
        控制“添加顶点”和“添加线条”动作和按钮的启用状态。
        """
        self.navigation_bar_widget.set_add_vertex_enabled(enabled)
        self.navigation_bar_widget.set_add_line_enabled(enabled)

    # 更多的UI状态控制方法可以根据需要添加，例如：
    # def set_save_action_enabled(self, enabled: bool):
    #     self.navigation_bar_widget.save_action.setEnabled(enabled)