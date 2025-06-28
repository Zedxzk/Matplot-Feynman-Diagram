# feynplot_gui/controllers/toolbox_controller.py

from PySide6.QtCore import QObject, Signal 

# 导入 UI Widget
from feynplot_gui.core_ui.widgets.toolbox_widget import ToolboxWidget 

# 【重要】使用类型提示的字符串引用 'MainController' 避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core_ui.controllers.main_controller import MainController

class ToolboxController(QObject): # 继承自 QObject
    def __init__(self, toolbox_widget: ToolboxWidget, main_controller: 'MainController', parent=None): 
        super().__init__(parent) 

        self.toolbox_widget = toolbox_widget
        self.main_controller = main_controller 

        self.setup_buttons()

    def setup_buttons(self):
        """连接工具箱按钮的信号到 MainController 的相应方法，或本控制器内部的业务逻辑方法。"""
        
        # 删除操作
        self.toolbox_widget.delete_vertex_requested.connect(self.main_controller.delete_selected_object)
        self.toolbox_widget.delete_line_requested.connect(self.main_controller.delete_selected_object)
        
        # 清空图
        self.toolbox_widget.clear_diagram_requested.connect(self.main_controller.clear_diagram)

        # 顶点可见性信号
        self.toolbox_widget.show_all_vertices_requested.connect(self._handle_show_all_vertices)
        self.toolbox_widget.hide_all_vertices_requested.connect(self._handle_hide_all_vertices)

        # --- 【新增】顶点标签可见性信号连接 ---
        self.toolbox_widget.show_all_vertex_labels_requested.connect(self._handle_show_all_vertex_labels)
        self.toolbox_widget.hide_all_vertex_labels_requested.connect(self._handle_hide_all_vertex_labels)

        # --- 【新增】线标签可见性信号连接 ---
        self.toolbox_widget.show_all_line_labels_requested.connect(self._handle_show_all_line_labels)
        self.toolbox_widget.hide_all_line_labels_requested.connect(self._handle_hide_all_line_labels)


    def _handle_show_all_vertices(self):
        """
        处理“显示所有顶点”的请求。
        调用 MainController 的 diagram_model 的 show_all_vertices 方法，并更新视图。
        """
        self.main_controller.diagram_model.show_all_vertices()
        status_msg = "所有顶点已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views() 

    def _handle_hide_all_vertices(self):
        """
        处理“隐藏所有顶点”的请求。
        调用 MainController 的 diagram_model 的 hide_all_vertices 方法，并更新视图。
        """
        self.main_controller.diagram_model.hide_all_vertices()
        status_msg = "所有顶点已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views() 

    # --- 【新增】处理顶点标签可见性的方法 ---
    def _handle_show_all_vertex_labels(self):
        """
        处理“显示所有顶点标签”的请求。
        调用 MainController 的 diagram_model 的 show_all_vertice_labels 方法，并更新视图。
        """
        # 注意：这里我们调用的是您在 diagram_model 中提供的 hide_all_vertice_labels 接口
        self.main_controller.diagram_model.show_all_vertice_labels()
        status_msg = "所有顶点标签已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    def _handle_hide_all_vertex_labels(self):
        """
        处理“隐藏所有顶点标签”的请求。
        调用 MainController 的 diagram_model 的 hide_all_vertice_labels 方法，并更新视图。
        """
        # 注意：这里我们调用的是您在 diagram_model 中提供的 show_all_vertice_labels 接口
        self.main_controller.diagram_model.hide_all_vertice_labels()
        status_msg = "所有顶点标签已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    # --- 【新增】处理线标签可见性的方法 ---
    def _handle_show_all_line_labels(self):
        """
        处理“显示所有线标签”的请求。
        调用 MainController 的 diagram_model 的 show_all_line_labels 方法，并更新视图。
        """
        # 假设你的 diagram_model 有一个 show_all_line_labels 方法
        self.main_controller.diagram_model.show_all_line_labels()
        status_msg = "所有线标签已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    def _handle_hide_all_line_labels(self):
        """
        处理“隐藏所有线标签”的请求。
        调用 MainController 的 diagram_model 的 hide_all_line_labels 方法，并更新视图。
        """
        # 假设你的 diagram_model 有一个 hide_all_line_labels 方法
        self.main_controller.diagram_model.hide_all_line_labels()
        status_msg = "所有线标签已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()


    def update_tool_mode(self, mode: str):
        """
        根据 MainController 传递的当前工具模式更新工具箱按钮的选中状态。
        """
        if hasattr(self.toolbox_widget, 'add_vertex_button') and mode == 'add_vertex':
            self.toolbox_widget.add_vertex_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'add_line_button') and mode == 'add_line':
            self.toolbox_widget.add_line_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'selection_button') and mode == 'select':
            self.toolbox_widget.selection_button.setChecked(True)
        else:
            if hasattr(self.toolbox_widget, 'add_vertex_button'): self.toolbox_widget.add_vertex_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'add_line_button'): self.toolbox_widget.add_line_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'selection_button'): self.toolbox_widget.selection_button.setChecked(False)
            
        self.main_controller.status_message.emit(f"工具箱工具模式已更新为：{mode}")

    def update(self):
        """通用的更新方法，目前不需要额外逻辑。"""
        pass