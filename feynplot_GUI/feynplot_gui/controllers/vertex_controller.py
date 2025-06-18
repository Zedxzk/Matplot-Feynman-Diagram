# from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
# from PySide6.QtCore import Qt

# from feynplot.core.vertex import Vertex, VertexType
# from ..widgets.add_vertex_dialog import AddVertexDialog
# from ..widgets.edit_vertex_dialog import EditVertexDialog

# class VertexController:
#     def __init__(self, diagram_model, vertex_list_widget, main_window=None, canvas=None):
#         self.diagram_model = diagram_model
#         self.vertex_list_widget = vertex_list_widget
#         self.main_window = main_window
#         self.canvas = canvas

#     def update_vertex_list(self):
#         self.vertex_list_widget.clear()
#         for vertex in self.diagram_model.vertices:
#             item_text = f"[{vertex.id}] Vtx: {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})"
#             item = QListWidgetItem(item_text)
#             item.setData(Qt.ItemDataRole.UserRole, vertex)
#             self.vertex_list_widget.addItem(item)

#     def add_new_vertex_at_coords(self, x: float, y: float):
#         parent_widget = self.main_window if self.main_window else self.canvas 
#         dialog = AddVertexDialog(x, y, parent=parent_widget)
#         if dialog.exec() == QDialog.Accepted:
#             coords_and_label = dialog.get_coordinates()
#             if coords_and_label:
#                 new_x, new_y, label = coords_and_label
#                 new_id = f"vtx_{len(self.diagram_model.vertices)}"
#                 vertex_type = VertexType.GENERIC

#                 if hasattr(dialog, 'vertex_id') and dialog.vertex_id:
#                     new_id = dialog.vertex_id
#                 if hasattr(dialog, 'vertex_type') and dialog.vertex_type:
#                     try:
#                         vertex_type = VertexType[dialog.vertex_type.upper()]
#                     except KeyError:
#                         vertex_type = VertexType.GENERIC

#                 self.diagram_model.add_vertex(new_x, new_y)  # 你这里的 add_vertex 需要支持 label, id, type
#                 QMessageBox.information(parent_widget, "添加成功", f"顶点 {new_id} 已添加。")
#                 self.update_vertex_list()
#                 if self.canvas:
#                     self.canvas.repaint()
#             else:
#                 QMessageBox.warning(parent_widget, "添加失败", "无法获取有效的顶点数据。")

#     def edit_vertex_properties(self, vertex: Vertex):
#         parent_widget = self.main_window if self.main_window else self.canvas
#         dialog = EditVertexDialog(vertex, parent=parent_widget)
#         if dialog.exec() == QDialog.Accepted:
#             QMessageBox.information(parent_widget, "编辑成功", f"顶点 {vertex.id} 属性已更新。")
#             self.update_vertex_list()
#             if self.canvas:
#                 self.canvas.repaint()

#     def delete_vertex(self, vertex: Vertex, line_controller=None):
#         parent_widget = self.main_window if self.main_window else self.canvas
#         reply = QMessageBox.question(parent_widget, '确认删除',
#                                      f"您确定要删除顶点 {vertex.id} 吗？",
#                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#         if reply == QMessageBox.Yes:
#             if line_controller:
#                 # 先删除关联线条
#                 lines_to_remove = [line for line in line_controller.diagram_model.lines
#                                    if line.v_start is vertex or line.v_end is vertex]
#                 for line in lines_to_remove:
#                     line_controller.delete_line(line)
#             self.diagram_model.vertices.remove(vertex)
#             QMessageBox.information(parent_widget, "删除成功", f"顶点 {vertex.id} 已删除。")
#             self.update_vertex_list()
#             if self.canvas:
#                 self.canvas.repaint()
#     def update(self):
#         pass


# feynplot_gui/controllers/vertex_controller.py

from PySide6.QtCore import QObject, Signal, Qt # 导入 QObject 和 Signal，因为控制器通常会继承自 QObject
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog # 导入需要的 Qt 组件

# 导入核心模型类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import Line # 如果需要处理线条的选中状态

# 导入 UI Widget
from feynplot_gui.widgets.vertex_list_widget import VertexListWidget
from feynplot_gui.widgets.add_vertex_dialog import AddVertexDialog
from feynplot_gui.widgets.edit_vertex_dialog import EditVertexDialog
# 导入主控制器 (用于类型提示和访问 MainController 的方法/信号)
# from feynplot_gui.controllers.main_controller import MainController # 假设 MainController 在同一级目录

class VertexController(QObject): # 继承自 QObject
    def __init__(self, diagram_model: 'FeynmanDiagram', vertex_list_widget: VertexListWidget, main_controller: 'MainController'):
        super().__init__() # 调用 QObject 的构造函数

        self.diagram_model = diagram_model
        self.vertex_list_widget = vertex_list_widget
        self.main_controller = main_controller # 保存 MainController 的引用

        # 连接 VertexListWidget 发出的信号到本控制器的槽函数
        self.vertex_list_widget.vertex_selected.connect(self._on_vertex_list_selected)
        self.vertex_list_widget.vertex_double_clicked.connect(self._on_vertex_list_double_clicked)

        # 初始更新列表视图
        self.update_vertex_list()

    def update_vertex_list(self):
        """
        根据 diagram_model 中的数据刷新顶点列表视图。
        这个方法会被 MainController 在模型变化时调用。
        """
        self.vertex_list_widget.clear()
        for vertex in self.diagram_model.vertices:
            item_text = f"[{vertex.id}] Vtx: {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, vertex.id) # 存储顶点ID，而不是整个对象
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
                if list_item.data(Qt.ItemDataRole.UserRole) == item.id:
                    list_item.setSelected(True)
                    self.vertex_list_widget.scrollToItem(list_item) # 滚动到选中项
                    break

    # --- 槽函数：响应 VertexListWidget 的信号 ---

    def _on_vertex_list_selected(self, vertex_id: str):
        """
        当用户在顶点列表中选择一个顶点时触发。
        通知 MainController 统一管理选中状态。
        """
        vertex = self.diagram_model.get_vertex_by_id(vertex_id)
        if vertex:
            # 调用 MainController 的 select_item 方法来统一管理选中状态
            self.main_controller.select_item(vertex) 
        else:
            self.main_controller.status_message.emit(f"错误：未找到ID为 {vertex_id} 的顶点。")


    def _on_vertex_list_double_clicked(self, vertex_id: str):
        """
        当用户在顶点列表中双击一个顶点时触发。
        通知 MainController 打开属性编辑器。
        """
        vertex = self.diagram_model.get_vertex_by_id(vertex_id)
        if vertex:
            # 调用 MainController 的方法来编辑属性
            self.main_controller.edit_item_properties(vertex)


    # --- 以下方法现在由 MainController 统一管理，VertexController 不再直接处理 ---
    # add_new_vertex_at_coords: 现在由 MainController 的 add_vertex_at_coords 方法处理
    # edit_vertex_properties: 现在由 MainController 的 edit_item_properties 方法处理
    # delete_vertex: 现在由 MainController 的 delete_selected_vertex 方法处理
    # 这些方法如果需要，可以在 VertexController 中实现一个包装，然后调用 MainController 的方法，
    # 但直接在 MainController 中处理更符合其协调者的角色。

    # 例如，如果 ToolboxController 想要删除顶点，它应该调用 main_controller.delete_selected_vertex()
    # 而不是通过 VertexController 再去调用 diagram_model。