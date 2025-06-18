from PySide6.QtCore import QObject, Signal, Qt 
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog 

# 导入核心模型类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import Line 

# 导入 UI Widget
from feynplot_gui.widgets.vertex_list_widget import VertexListWidget
from feynplot_gui.widgets.add_vertex_dialog import AddVertexDialog
from feynplot_gui.widgets.edit_vertex_dialog import EditVertexDialog
# 导入主控制器 (用于类型提示和访问 MainController 的方法/信号)
# from feynplot_gui.controllers.main_controller import MainController 
# 导入你刚刚创建的功能函数
from .vertex_dialogs.edit_vertex import open_edit_vertex_dialog 


class VertexController(QObject): 
    def __init__(self, diagram_model: 'FeynmanDiagram', vertex_list_widget: VertexListWidget, main_controller:'MainController'):
        super().__init__() 

        self.diagram_model = diagram_model
        self.vertex_list_widget = vertex_list_widget
        self.main_controller = main_controller 

        # 连接 VertexListWidget 发出的信号到本控制器的槽函数
        self.vertex_list_widget.vertex_selected.connect(self._on_vertex_list_selected)
        self.vertex_list_widget.vertex_double_clicked.connect(self._on_vertex_list_double_clicked)
        
        # --- 连接 VertexListWidget 的右键菜单信号到对应的槽函数 ---
        # 注意：你需要确保 VertexListWidget 已经定义了这些信号
        # 例如：edit_vertex_requested, delete_vertex_requested, search_vertex_requested
        # 如果没有定义，PySide6 会在运行时报错。
        self.vertex_list_widget.edit_vertex_requested.connect(self._on_edit_vertex_requested)
        self.vertex_list_widget.delete_vertex_requested.connect(self._on_delete_vertex_requested)
        self.vertex_list_widget.search_vertex_requested.connect(self._on_search_vertex_requested)


        # 初始更新列表视图
        self.update_vertex_list()

    def update_vertex_list(self):
        """
        根据 diagram_model 中的数据刷新顶点列表视图。
        这个方法会被 MainController 在模型变化时调用。
        """
        self.vertex_list_widget.clear()
        for vertex in self.diagram_model.vertices:
            # 这里的 'Vtx' 暂时硬编码，如果你之前有翻译字典，这里应该使用翻译函数
            item_text = f"[{vertex.id}] Vtx: {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})" 
            item = QListWidgetItem(item_text)
            # 这里是之前的一个关键点：确保存储的是 Vertex 对象本身，而不是它的 ID
            # 这样在槽函数中可以直接获取完整的 Vertex 对象
            item.setData(Qt.ItemDataRole.UserRole, vertex) 
            self.vertex_list_widget.addItem(item)
        
        # 重新应用选中状态
        current_selected = self.main_controller.get_selected_item()
        if isinstance(current_selected, Vertex):
            self.set_selected_item_in_list(current_selected)
            
        self.main_controller.status_message.emit("顶点列表已更新。")


    def set_selected_item_in_list(self, item: [Vertex, Line, None]):
        """
        接收来自 MainController 的选中项，并在顶点列表中设置/清除选中状态。
        """
        # 先清除列表中的所有选中状态
        self.vertex_list_widget.clearSelection()

        if isinstance(item, Vertex):
            for i in range(self.vertex_list_widget.count()):
                list_item = self.vertex_list_widget.item(i)
                # 比较存储的 Vertex 对象与传入的 Vertex 对象
                if list_item.data(Qt.ItemDataRole.UserRole) is item: 
                    list_item.setSelected(True)
                    self.vertex_list_widget.scrollToItem(list_item) 
                    break

    # --- 槽函数：响应 VertexListWidget 的信号 ---

    def _on_vertex_list_selected(self, vertex: Vertex): # 接收 Vertex 对象
        """
        当用户在顶点列表中选择一个顶点时触发。
        通知 MainController 统一管理选中状态。
        """
        if vertex:
            # 调用 MainController 的 select_item 方法来统一管理选中状态
            self.main_controller.select_item(vertex) 
        else:
            self.main_controller.select_item(None) # 清除选中
            self.main_controller.status_message.emit("顶点列表选中已清除。")


    def _on_vertex_list_double_clicked(self, vertex: Vertex): # 接收 Vertex 对象
        """
        当用户在顶点列表中双击一个顶点时触发。
        通知 MainController 打开属性编辑器。
        """
        if vertex:
            # 调用 MainController 的方法来编辑属性
            self.main_controller.edit_item_properties(vertex)


    # --- 右键菜单请求的槽函数（将请求转发给 MainController） ---
    # 这些函数体目前留空，待 MainController 相应方法完善后，再实现转发逻辑。

    # def _on_edit_vertex_requested(self, vertex: Vertex):
    #     """
    #     处理来自 VertexListWidget 右键菜单的“编辑顶点”请求。
    #     此方法将请求转发给 MainController 来处理实际的编辑逻辑。
    #     """
    #     # 功能待实现：将请求转发给 main_controller.edit_item_properties(vertex)
    #     self.main_controller.status_message.emit(f"列表接收到编辑顶点请求: {vertex.id} (待转发)")
    #     pass

    def _on_delete_vertex_requested(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“删除顶点”请求。
        此方法将请求转发给 MainController 来处理实际的删除逻辑。
        """
        # 功能待实现：将请求转发给 main_controller.delete_item(vertex)
        self.main_controller.status_message.emit(f"列表接收到删除顶点请求: {vertex.id} (待转发)")
        pass

    def _on_search_vertex_requested(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“关键字检索”请求。
        此方法将请求转发给 MainController 来处理实际的检索逻辑。
        """
        # 功能待实现：将请求转发给 main_controller.search_for_item(vertex) 或类似方法
        self.main_controller.status_message.emit(f"列表接收到关键字检索请求: {vertex.id} (待转发)")
        pass

    def _get_parent_widget(self):
        """辅助函数，获取对话框的父控件。"""
        # 假设 MainController 有 main_window 和 canvas_widget 属性
        return self.main_controller.main_window if self.main_controller.main_window else self.main_controller.canvas_widget


    def _on_edit_vertex_requested(self, vertex: Vertex):
        """
        处理来自 VertexListWidget 右键菜单的“编辑顶点”请求。
        通过调用外部函数来处理编辑对话框。
        """
        self.main_controller.status_message.emit(f"列表接收到编辑顶点请求: {vertex.id}")
        
        parent_widget = self._get_parent_widget() # 获取父控件
        
        # 调用导入的功能函数
        if open_edit_vertex_dialog(vertex, self.main_controller.diagram_model, parent_widget=parent_widget):
            # 如果成功编辑，通知 MainController 更新UI
            self.main_controller.update_all_views() # 假设 MainController 有一个方法来触发所有UI更新
            self.main_controller.status_message.emit(f"顶点 {vertex.id} 属性已成功更新并刷新。")
        else:
            self.main_controller.status_message.emit(f"顶点 {vertex.id} 属性编辑操作已取消。")