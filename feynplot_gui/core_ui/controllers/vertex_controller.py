from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog

# 导入核心模型类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import Line

# 导入 UI Widget
from feynplot_gui.core_ui.widgets.vertex_list_widget import VertexListWidget

# 导入对话框 (这里保留你的结构，尽管对话框的协调通常由 MainController 或专门的 DialogController 负责)
# from feynplot_gui.core_ui.dialogs.add_vertex_dialog import AddVertexDialog
# from feynplot_gui.core_ui.dialogs.edit_vertex_dialog import EditVertexDialog

# 导入你的功能函数
from .vertex_dialogs.edit_vertex import open_edit_vertex_dialog
from feynplot.io.diagram_io import diagram_to_json_string, diagram_from_json_string

class VertexController(QObject):
    # 移除: vertex_selection_changed 信号，因为我们将直接调用 main_controller.select_item

    # 保留这些信号用于转发右键菜单请求，因为这些操作可能涉及比简单选择更复杂的 MainController 行为。
    request_edit_vertex = Signal(object)
    request_delete_vertex = Signal(object)
    request_search_vertex = Signal(object)

    def __init__(self, diagram_model: 'FeynmanDiagram', vertex_list_widget: VertexListWidget, main_controller:'MainController'):
        super().__init__()

        self.diagram_model = diagram_model
        self.vertex_list_widget = vertex_list_widget
        self.main_controller = main_controller

        # 将 VertexListWidget 的用户交互信号连接到此控制器的槽函数
        # !! 重要改动 !!
        # 在这些槽函数中，我们将直接调用 main_controller.select_item
        # self.vertex_list_widget.vertex_selected.connect(self._on_vertex_list_selected)
        # self.vertex_list_widget.list_blank_clicked.connect(self._on_list_blank_clicked)
        self.vertex_list_widget.vertex_double_clicked.connect(self._on_vertex_list_double_clicked)

        # 连接 VertexListWidget 的右键菜单信号到对应的槽函数
        self.vertex_list_widget.edit_vertex_requested.connect(self._on_edit_vertex_requested_from_list)
        self.vertex_list_widget.delete_vertex_requested.connect(self._on_delete_vertex_requested_from_list)
        self.vertex_list_widget.search_vertex_requested.connect(self._on_search_vertex_requested_from_list)

        # 初始更新列表视图
        self.update_vertex_list()

    def update_vertex_list(self):
        """
        根据 diagram_model 中的数据刷新顶点列表视图。
        此方法由 MainController 在模型变化时调用。
        它只负责重建列表内容；不在此处直接设置选中状态。
        选中状态由 set_selected_item_in_list 负责。
        """
        # 在重新填充列表期间暂时阻塞信号，防止不必要的选择信号触发
        self.vertex_list_widget.blockSignals(True)

        self.vertex_list_widget.clear()

        for vertex in self.diagram_model.vertices:
            item_text = f"[{vertex.id}] {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, vertex)
            self.vertex_list_widget.addItem(item)

        self.vertex_list_widget.blockSignals(False)

        self.main_controller.status_message.emit("顶点列表已更新。")

        # 在更新列表后，根据 MainController 当前的选中项重新设置列表的选中状态。
        # 这确保了列表的 UI 与全局选中项保持一致。
        self.set_selected_item_in_list(self.main_controller.get_selected_item())


    def set_selected_item_in_list(self, item_to_select: [Vertex, Line, None]):
        """
        接收来自 MainController 的选中项，并在顶点列表中设置/清除选中状态。
        此方法由 MainController 调用。
        """
        # 此方法直接调用 QListWidget 的方法，该方法内部已处理信号阻塞。
        # print(f"VertexController: 设置列表选中项 {item_to_select}。")
        self.vertex_list_widget.set_selected_item_in_list(item_to_select)


    # --- 槽函数：响应 VertexListWidget 的信号 (用户交互) ---

    def _on_vertex_list_selected(self, vertex: Vertex):
        """
        当用户在顶点列表中选择一个顶点时触发。
        直接调用 MainController 的 select_item 方法进行统一的选中管理。
        """
        # Clear all existing highlights in the model first
        for v in self.diagram_model.vertices:
            if hasattr(v, 'highlighted_vertex'):
                v.highlighted_vertex = False

        if vertex:
            # Set the highlighted_vertex attribute for the newly selected vertex
            if hasattr(vertex, 'highlighted_vertex'):
                vertex.highlighted_vertex = True
            else:
                vertex.highlighted_vertex = True # Add the attribute if it doesn't exist

            # Call MainController's select_item method to unify selection management
            self.main_controller.select_item(vertex)
            self.main_controller.status_message.emit(f"顶点 {vertex.id} 已选中并高亮。")
        else:
            self.main_controller.select_item(None) # Clear selection
            self.main_controller.status_message.emit("顶点列表选中已清除。所有顶点高亮已移除。")

        # After selection change, ensure the view is updated to reflect the highlight status
        self.main_controller.update_all_views() # Assuming this updates the canvas as well


    def _on_vertex_list_double_clicked(self, vertex: Vertex):
        """
        当用户在顶点列表中双击一个顶点时触发。
        发出信号请求 MainController 打开属性编辑器。
        """
        print(f"VertexController: 收到列表双击顶点 {vertex.id}。发出 request_edit_vertex 信号。")
        # 对于编辑这种复杂操作，仍然通过信号转发，因为 MainController 可能有额外的逻辑或专门的对话框控制器。
        self._on_edit_vertex_requested_from_list(vertex)
        self.request_edit_vertex.emit(vertex)


    # --- 右键菜单请求的槽函数 (转发给 MainController) ---
    def _on_edit_vertex_requested_from_list(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“编辑顶点”请求。
        发出信号请求 MainController 处理编辑操作。
        """
        print(f"VertexController: 收到列表右键编辑顶点请求: {vertex.id}。发出 request_edit_vertex 信号。")
        self.request_edit_vertex.emit(vertex)
        self._on_edit_vertex_requested(vertex=vertex)

    def _on_delete_vertex_requested_from_list(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“删除顶点”请求。
        此方法将请求转发给 MainController 来处理实际的删除逻辑。

        Args:
            vertex (Vertex): 从列表中右键点击并选择删除的顶点实例。
        """
        # Print status message to indicate the request has been received (optional, for debugging)
        print(f"VertexController: 收到列表右键删除顶点请求: {vertex.id}。转发给 MainController。")
        self.main_controller.status_message.emit(f"列表接收到删除顶点请求: {vertex.id} (转发中...)")

        # Call MainController's delete_selected_vertex method, passing the specified vertex
        # This way, the delete dialog will pre-select and lock this vertex
        self.main_controller.delete_selected_vertex(vertex)

    def _on_search_vertex_requested_from_list(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“关键字检索”请求。
        发出信号请求 MainController 处理检索操作。
        """
        print(f"VertexController: 收到列表右键检索顶点请求: {vertex.id}。发出 request_search_vertex 信号。")
        self.request_search_vertex.emit(vertex)


    def _get_parent_widget(self):
        """辅助函数，获取对话框的父控件。"""
        # Assume MainController has main_window and canvas_widget attributes
        return self.main_controller.main_window if hasattr(self.main_controller, 'main_window') and self.main_controller.main_window else self.main_controller.canvas_widget


    def _on_edit_vertex_requested(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“编辑顶点”请求。
        通过调用外部函数来处理编辑对话框。
        """
        self.main_controller.status_message.emit(f"列表接收到编辑顶点请求: {vertex.id}")
        # self.main_controller.select_item()

        parent_widget = self._get_parent_widget() # Get parent widget

        # Call the imported functional function
        # self.main_controller.toolbox_controller._save_current_diagram_state()
        current_status = diagram_to_json_string(self.main_controller.diagram_model)
        if open_edit_vertex_dialog(vertex, self.main_controller.diagram_model, parent_widget=parent_widget):
            self.main_controller.toolbox_controller.update_redo_unto_status(current_status)
            self.main_controller.toolbox_controller.update_redo_unto_status()
            # If successfully edited, notify MainController to update UI
            self.main_controller.update_all_views() # Assume MainController has a method to trigger all UI updates
            self.main_controller.status_message.emit(f"顶点 {vertex.id} 属性已成功更新并刷新。")
            # print(f"顶点 {vertex.id} 属性已成功更新并刷新。")
            # Re-set the selected item to ensure its highlighted state is preserved/updated
            self.set_selected_item_in_list(vertex)
        else:
            self.main_controller.status_message.emit(f"顶点 {vertex.id} 属性编辑操作已取消。")