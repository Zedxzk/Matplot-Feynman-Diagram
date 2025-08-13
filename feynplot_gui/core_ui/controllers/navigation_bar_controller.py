# feynplot_gui/controllers/navigation_bar_controller.py

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog
from feynplot_gui.core_ui.widgets.navigation_bar_widget import NavigationBarWidget
from feynplot.core.vertex import Vertex # 用于类型提示
from feynplot.core.line import Line # 用于类型提示

# 导入 Matplotlib 设置对话框
from feynplot_gui.core_ui.dialogs.plt_dialogs.matplotlib_settings_dialog import MatplotlibSettingsDialog
# 导入编辑所有顶点的对话框
from feynplot_gui.core_ui.dialogs.vertex_dialogs.edit_all_vertices_dialog import EditAllVerticesDialog
from feynplot_gui.core_ui.dialogs.line_dialogs.edit_all_lines_dialog import EditAllLinesDialog


import matplotlib.pyplot as plt # 导入 matplotlib 用于应用 rcParams

# 导入图的导入/导出函数
from feynplot.io.diagram_io import export_diagram_to_json, import_diagram_from_json

# 为了避免循环导入，使用 TYPE_CHECKING
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#    from feynplot_gui.controllers.main_controller import MainController


class NavigationBarController(QObject):
    # 定义信号，这些信号将由 MainController 监听，用于触发核心业务逻辑
    add_vertex_requested = Signal()
    add_line_requested = Signal()
    edit_selected_vertex_requested = Signal()
    edit_selected_line_requested = Signal()
    delete_selected_object_requested = Signal()
    # 【新增】编辑所有线条的业务请求信号
    edit_all_lines_requested = Signal()


    # NavigationBarController 自己的状态更新信号，用于通知外部（如MainController）UI状态变化
    status_message = Signal(str) # 用于发送状态消息
    # 当项目被加载后，通知 MainController 更新图数据
    project_loaded = Signal()
    # 当项目被保存后，通知 MainController
    project_saved = Signal()


    def __init__(self, navigation_bar_widget: NavigationBarWidget, main_controller: 'MainController'):
        super().__init__()

        self.navigation_bar_widget = navigation_bar_widget
        self.main_controller = main_controller # 仍然持有MainController的引用，用于转发业务请求

        # 初始化 Matplotlib 设置对话框实例
        self._matplotlib_settings_dialog = MatplotlibSettingsDialog(parent=self.navigation_bar_widget)
        self._matplotlib_settings_dialog.settings_applied.connect(self._on_matplotlib_settings_applied)

        self.setup_connections()
        # 初始状态更新
        self._update_ui_state() 


    def setup_connections(self):
        """连接导航栏部件的信号到控制器槽函数，并发出请求信号给MainController。"""
        # 文件菜单动作 - 直接连接到控制器内的处理函数
        self.navigation_bar_widget.canvas_update_interval_changed_ui.connect(self._on_canvas_update_interval_changed_ui)
        self.navigation_bar_widget.canvas_set_range.connect(self._on_canvas_set_range_ui)
        # self.main_controller.canvas_controller.canvas_widget.canvas_panned.connect(self._on_canvas_set_range_ui)


        self.navigation_bar_widget.save_project_action_triggered.connect(self._on_save_project_ui_triggered)
        self.navigation_bar_widget.load_project_action_triggered.connect(self._on_load_project_ui_triggered)
        
        # 编辑菜单动作
        self.navigation_bar_widget.add_vertex_button_clicked.connect(self._on_add_vertex_ui_triggered)
        self.navigation_bar_widget.add_line_button_clicked.connect(self._on_add_line_ui_triggered)

        self.navigation_bar_widget.edit_all_vertices_triggered.connect(self._on_edit_all_vertices_ui_triggered)
        self.navigation_bar_widget.edit_all_lines_triggered.connect(self._on_edit_all_lines_ui_triggered)
        self.navigation_bar_widget.toggle_auto_scale_requested.connect(self._on_set_auto_scale_checked_ui_triggered)

        # “对象”菜单的“编辑属性”和“删除对象”动作
        self.navigation_bar_widget.edit_obj_action.triggered.connect(self._on_edit_object_ui_triggered)
        self.navigation_bar_widget.delete_obj_action.triggered.connect(self._on_delete_object_ui_triggered)

        # 后端设置菜单动作
        self.navigation_bar_widget.show_matplotlib_settings_triggered.connect(self._on_show_matplotlib_settings_ui_triggered)
        self.navigation_bar_widget.toggle_use_relative_unit.connect(self._on_toggle_use_relative_unit_ui_triggered)
        try:
            self.main_controller.selection_changed.connect(self._on_main_controller_selection_changed)
        except AttributeError:
            self.status_message.emit("警告：MainController未提供'selection_changed'信号。对象菜单状态更新可能不正确。")

        # 连接到 MainController 的图模型更新信号，以便在图模型发生变化时更新UI状态
        try:
            self.main_controller.diagram_updated.connect(self._on_main_controller_diagram_updated)
        except AttributeError:
            self.status_message.emit("警告：MainController未提供'diagram_updated'信号。保存/加载按钮状态可能不正确。")


    ## --- Internal UI Logic Handling Slots ---

    def _update_ui_state(self):
        """
        一个中心化方法，用于更新所有相关 UI 元素的启用/禁用状态。
        此方法将在初始化时以及任何可能影响 UI 的状态变化时被调用。
        """
        # 文件操作：保存/加载。保存仅在图模型存在时启用。加载始终启用。
        can_save = bool(self.main_controller.diagram_model)
        self.navigation_bar_widget.set_save_load_actions_enabled(save_enabled=can_save, load_enabled=True)

        # 添加操作：如果存在可添加到的图模型，则启用。
        can_add = bool(self.main_controller.diagram_model)
        self.navigation_bar_widget.set_add_vertex_enabled(can_add)
        self.navigation_bar_widget.set_add_line_enabled(can_add)

        # 编辑所有顶点和线条：现在始终启用
        self.navigation_bar_widget.set_edit_all_vertices_enabled(True)
        self.navigation_bar_widget.set_edit_all_lines_enabled(True) # 【新增】启用编辑所有线条


        # 对象操作（编辑/删除选中项）：取决于当前选中项。
        selected_item = self.main_controller.get_selected_item() 
        is_item_selected = (selected_item is not None)
        can_edit_selected = isinstance(selected_item, (Vertex, Line))

        self.navigation_bar_widget.set_object_menu_enabled(is_item_selected)
        self.navigation_bar_widget.set_edit_object_action_enabled(can_edit_selected)
        self.navigation_bar_widget.set_delete_object_action_enabled(is_item_selected)

        # 视图菜单：如果应用程序正在运行，通常总是启用。
        self.navigation_bar_widget.set_view_menu_actions_enabled(True)


    # 保存项目处理
    def _on_save_project_ui_triggered(self):
        """处理UI的保存项目触发，弹出文件对话框并调用保存逻辑。"""
        self.status_message.emit("请求保存项目。")
        # 弹出保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self.navigation_bar_widget, # 父窗口
            "保存费曼图项目",
            "untitled.json", # 默认文件名
            "Feynman Diagram Files (*.json);"
        )
        if file_path:
            try:
                # 获取当前图模型实例
                diagram = self.main_controller.diagram_model
                if diagram:
                    export_diagram_to_json(diagram, file_path)
                    QMessageBox.information(self.navigation_bar_widget, "保存成功", f"项目已成功保存到：\n{file_path}")
                    self.status_message.emit(f"项目已保存到：{file_path}")
                    self.project_saved.emit() # 通知MainController项目已保存
                else:
                    QMessageBox.warning(self.navigation_bar_widget, "保存失败", "当前没有可保存的费曼图项目。")
                    self.status_message.emit("保存失败：没有可保存的项目。")
            except Exception as e:
                QMessageBox.critical(self.navigation_bar_widget, "保存失败", f"保存项目时发生错误：\n{e}")
                self.status_message.emit(f"保存失败：{e}")
        self._update_ui_state() # 总是更新UI状态

    # 加载项目处理
    def _on_load_project_ui_triggered(self):
        """处理UI的加载项目触发，弹出文件对话框并调用加载逻辑。"""
        self.status_message.emit("请求加载项目。")
        # 弹出打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self.navigation_bar_widget, # 父窗口
            "加载费曼图项目",
            "", # 默认路径
            "Feynman Diagram Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                # 这里假设 MainController 的 diagram_model 是一个属性，并且其 setter 会触发 diagram_updated 信号
                # 或者 MainController 有一个 set_diagram_model 方法来处理这个逻辑。
                # 如果 MainController 只是直接赋值，则可能需要 MainController 内部做调整来发出信号。
                self.main_controller.diagram_model = import_diagram_from_json(file_path, self.main_controller.diagram_model)
                QMessageBox.information(self.navigation_bar_widget, "加载成功", f"项目已成功从：\n{file_path}")
                self.main_controller.picture_model()
                self.status_message.emit(f"项目已从：{file_path} 加载。")
                self.project_loaded.emit() # 通知NavigationBarController自身项目已加载
            except Exception as e:
                QMessageBox.critical(self.navigation_bar_widget, "加载失败", f"加载项目时发生错误：\n{e}")
                self.status_message.emit(f"加载失败：{e}")
        self.main_controller.update_all_views(canvas_options={'auto_scale': True}) # 调用 MainController 更新视图，这也可能触发 _on_main_controller_diagram_updated

    def _on_add_vertex_ui_triggered(self):
        """处理UI的添加顶点触发，并发出业务请求信号。"""
        if not self.main_controller.diagram_model:
            QMessageBox.warning(self.navigation_bar_widget, "操作禁用", "请先加载或创建一个图项目。")
            self.status_message.emit("添加顶点失败：没有图项目。")
            return

        self.status_message.emit("请求添加顶点。")
        self.add_vertex_requested.emit()
        self._update_ui_state() # 添加后可能会影响UI状态（例如，“编辑所有顶点”可能被启用）

    def _on_add_line_ui_triggered(self):
        """处理UI的添加线条触发，并发出业务请求信号。"""
        if not self.main_controller.diagram_model:
            QMessageBox.warning(self.navigation_bar_widget, "操作禁用", "请先加载或创建一个图项目。")
            self.status_message.emit("添加线条失败：没有图项目。")
            return

        self.status_message.emit("请求添加线条。")
        self.add_line_requested.emit()
        self._update_ui_state() # 添加后可能会影响UI状态

    # 处理“编辑所有顶点”的UI触发
    def _on_edit_all_vertices_ui_triggered(self):
        """
        处理“编辑所有顶点”菜单项的UI触发。
        显示 EditAllVerticesDialog 对话框，并在无顶点时提供提示。
        """
        self.status_message.emit("请求编辑所有顶点属性。")
        
        # 获取所有顶点对象列表
        # 确保 MainController 有一个 diagram_model 属性且它是 FeynmanDiagram 类型
        diagram = self.main_controller.diagram_model 
        all_vertices = diagram.vertices if diagram else []

        if not all_vertices:
            # 如果没有顶点，则弹出提示并返回
            QMessageBox.information(self.navigation_bar_widget, "无顶点", "当前图中没有顶点可供编辑。")
            self.status_message.emit("编辑所有顶点失败：当前图中没有顶点。")
            return

        # 如果有顶点，则显示对话框
        dialog = EditAllVerticesDialog(all_vertices, parent=self.navigation_bar_widget)
        dialog.settings_applied.connect(self._on_all_vertices_settings_applied)

        dialog.exec() # 以模态方式显示对话框
        # 对话框关闭后，如果用户点击OK，_on_all_vertices_settings_applied 会被调用并触发视图更新。
        # 如果用户点击Cancel，则不做任何事。

    # 【新增】处理“编辑所有线条”的UI触发
    def _on_edit_all_lines_ui_triggered(self):
        """
        处理“编辑所有线条”菜单项的UI触发。
        显示 EditAllLinesDialog 对话框，并在无线条时提供提示。
        """
        self.status_message.emit("请求编辑所有线条属性。")
        
        diagram = self.main_controller.diagram_model
        all_lines = diagram.lines if diagram else []

        if not all_lines:
            QMessageBox.information(self.navigation_bar_widget, "无线条", "当前图中没有线条可供编辑。")
            self.status_message.emit("编辑所有线条失败：当前图中没有线条。")
            return

        dialog = EditAllLinesDialog(parent=self.navigation_bar_widget, lines=all_lines)
        dialog.properties_updated.connect(self._on_all_lines_settings_applied)
        dialog.exec()

    def _on_edit_object_ui_triggered(self):
        """处理UI的编辑对象触发，并根据当前选中类型发出相应请求信号。"""
        selected_item = self.main_controller.get_selected_item() # 假设MainController提供此方法
        if isinstance(selected_item, Vertex):
            self.status_message.emit(f"请求编辑顶点: {selected_item.id}")
            self.edit_selected_vertex_requested.emit()
        elif isinstance(selected_item, Line):
            self.status_message.emit(f"请求编辑线条: {selected_item.id}")
            self.edit_selected_line_requested.emit()
        else:
            self.status_message.emit("没有选中的顶点或线条可供编辑。")
        self._update_ui_state() # 编辑后可能会影响UI状态

    def _on_delete_object_ui_triggered(self):
        """处理UI的删除对象触发，并发出通用删除请求信号。"""
        self.status_message.emit("请求删除选中对象。")
        self.delete_selected_object_requested.emit()
        self._update_ui_state() # 删除后会影响UI状态

    def _on_show_matplotlib_settings_ui_triggered(self):
        """
        处理UI触发的显示Matplotlib设置请求。
        这是 NavigationBarController 自己的业务逻辑：管理 Matplotlib 设置对话框的显示。
        """
        self.status_message.emit("请求显示Matplotlib后端设置。")
        self._matplotlib_settings_dialog.exec()

    def _on_matplotlib_settings_applied(self, settings: dict):
        """
        处理 Matplotlib 设置对话框发出的设置应用信号。
        这是 NavigationBarController 自己的业务逻辑：将设置应用到 Matplotlib。
        """
        self.status_message.emit("Matplotlib 设置已从对话框接收。")
        try:
            for key, value in settings.items():
                try:
                    if key == "font.family" and isinstance(value, str):
                        plt.rcParams[key] = [value]
                    else:
                        plt.rcParams[key] = value
                    self.status_message.emit(f"已应用 Matplotlib 参数: {key} = {value}")
                except KeyError:
                    self.status_message.emit(f"警告: Matplotlib中不存在参数 '{key}'，跳过。")
                except Exception as e:
                    self.status_message.emit(f"警告: 应用 Matplotlib 参数 '{key}' 失败: {e}")

            if hasattr(self.main_controller, 'update_all_views'):
                self.main_controller.update_all_views()
                self.status_message.emit("已通知主控制器更新所有视图以反映新设置。")
            else:
                self.status_message.emit("警告：MainController未提供update_all_views方法，视图可能未完全刷新。")

        except Exception as e:
            self.status_message.emit(f"应用Matplotlib设置时发生意外错误: {e}")
        self._update_ui_state() # 设置更改后更新UI状态

    # 处理所有顶点设置应用后的槽函数
    def _on_all_vertices_settings_applied(self):
        """
        处理 EditAllVerticesDialog 对话框发出的设置应用信号。
        通知 MainController 更新所有视图，因为顶点属性可能已更改。
        """
        self.status_message.emit("所有顶点属性已修改。")
        if hasattr(self.main_controller, 'update_all_views'):
            self.main_controller.update_all_views()
            self.status_message.emit("已通知主控制器更新所有视图以反映所有顶点的新属性。")
        else:
            self.status_message.emit("警告：MainController未提供update_all_views方法，视图可能未完全刷新。")
        self._update_ui_state() # 属性更改后更新UI状态

    # 【新增】处理所有线条设置应用后的槽函数
    def _on_all_lines_settings_applied(self):
        """
        处理 EditAllLinesDialog 对话框发出的设置应用信号。
        通知 MainController 更新所有视图，因为线条属性可能已更改。
        """
        self.status_message.emit("所有线条属性已修改。")
        if hasattr(self.main_controller, 'update_all_views'):
            self.main_controller.update_all_views()
            self.status_message.emit("已通知主控制器更新所有视图以反映所有线条的新属性。")
        else:
            self.status_message.emit("警告：MainController未提供update_all_views方法，视图可能未完全刷新。")
        self._update_ui_state() # 属性更改后更新UI状态


    ## --- UI Event Handlers from MainController ---

    def _on_main_controller_diagram_updated(self):
        """
        MainController 通知图模型已更新时的槽函数。
        触发 NavigationBarController 的 UI 状态更新。
        """
        self.status_message.emit("图模型已更新，正在刷新导航栏UI状态。")
        self._update_ui_state()

    def _on_main_controller_selection_changed(self, selected_item: object):
        """
        MainController 通知选中项已改变时的槽函数。
        触发 NavigationBarController 的 UI 状态更新。
        """
        self.status_message.emit(f"选中项已改变，正在刷新导航栏UI状态。选中项: {type(selected_item).__name__ if selected_item else 'None'}")
        self._update_ui_state()

    # 此方法已不再被外部直接调用，但作为公共接口保留，尽管其功能已被 _update_ui_state 吸收
    def set_add_actions_enabled(self, enabled: bool):
        """
        控制“添加顶点”和“添加线条”动作和按钮的启用状态。
        （此方法现在主要由 _update_ui_state 间接控制，但作为公共接口保留。）
        """
        self.navigation_bar_widget.set_add_vertex_enabled(enabled)
        self.navigation_bar_widget.set_add_line_enabled(enabled)


    def _on_set_auto_scale_checked_ui_triggered(self):
        # print("触发设置自动缩放的UI事件。")
        self.main_controller.update_all_views(canvas_options={'auto_scale': True})

    def _on_canvas_update_interval_changed_ui(self, interval: int):
        self.main_controller.canvas_controller.set_update_interval(interval)

    def _on_canvas_set_range_ui(self, x_min, x_max, y_min, y_max):
        canvas_opts = {
            "target_xlim": (x_min, x_max),
            "target_ylim": (y_min, y_max),
        }
        self.main_controller.update_all_views(canvas_options=canvas_opts)

    def _on_toggle_use_relative_unit_ui_triggered(self):
        """
        当用户在导航栏中切换“相对单位”复选框时调用。
        更新 canvas_controller 的 relative_size_unit 属性，并通知 MainController 更新所有视图。
        """
        print("触发切换相对单位的UI事件。")
        self.main_controller.canvas_controller.relative_size_unit = not self.main_controller.canvas_controller.relative_size_unit
        self.status_message.emit(f"已切换相对单位使用状态: {self.main_controller.canvas_controller.relative_size_unit}")
        print(f"当前相对单位状态: {self.main_controller.canvas_controller.relative_size_unit}")
        self.main_controller.update_all_views(canvas_options={'auto_scale': True})
