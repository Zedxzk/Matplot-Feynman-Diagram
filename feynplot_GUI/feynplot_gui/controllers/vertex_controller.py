from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
from PySide6.QtCore import Qt

from feynplot.core.vertex import Vertex, VertexType
from ..widgets.add_vertex_dialog import AddVertexDialog
from ..widgets.edit_vertex_dialog import EditVertexDialog

class VertexController:
    def __init__(self, diagram_model, vertex_list_widget, main_window=None, canvas=None):
        self.diagram_model = diagram_model
        self.vertex_list_widget = vertex_list_widget
        self.main_window = main_window
        self.canvas = canvas

    def update_vertex_list(self):
        self.vertex_list_widget.clear()
        for vertex in self.diagram_model.vertices:
            item_text = f"[{vertex.id}] Vtx: {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, vertex)
            self.vertex_list_widget.addItem(item)

    def add_new_vertex_at_coords(self, x: float, y: float):
        parent_widget = self.main_window if self.main_window else self.canvas 
        dialog = AddVertexDialog(x, y, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            coords_and_label = dialog.get_coordinates()
            if coords_and_label:
                new_x, new_y, label = coords_and_label
                new_id = f"vtx_{len(self.diagram_model.vertices)}"
                vertex_type = VertexType.GENERIC

                if hasattr(dialog, 'vertex_id') and dialog.vertex_id:
                    new_id = dialog.vertex_id
                if hasattr(dialog, 'vertex_type') and dialog.vertex_type:
                    try:
                        vertex_type = VertexType[dialog.vertex_type.upper()]
                    except KeyError:
                        vertex_type = VertexType.GENERIC

                self.diagram_model.add_vertex(new_x, new_y)  # 你这里的 add_vertex 需要支持 label, id, type
                QMessageBox.information(parent_widget, "添加成功", f"顶点 {new_id} 已添加。")
                self.update_vertex_list()
                if self.canvas:
                    self.canvas.repaint()
            else:
                QMessageBox.warning(parent_widget, "添加失败", "无法获取有效的顶点数据。")

    def edit_vertex_properties(self, vertex: Vertex):
        parent_widget = self.main_window if self.main_window else self.canvas
        dialog = EditVertexDialog(vertex, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(parent_widget, "编辑成功", f"顶点 {vertex.id} 属性已更新。")
            self.update_vertex_list()
            if self.canvas:
                self.canvas.repaint()

    def delete_vertex(self, vertex: Vertex, line_controller=None):
        parent_widget = self.main_window if self.main_window else self.canvas
        reply = QMessageBox.question(parent_widget, '确认删除',
                                     f"您确定要删除顶点 {vertex.id} 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if line_controller:
                # 先删除关联线条
                lines_to_remove = [line for line in line_controller.diagram_model.lines
                                   if line.v_start is vertex or line.v_end is vertex]
                for line in lines_to_remove:
                    line_controller.delete_line(line)
            self.diagram_model.vertices.remove(vertex)
            QMessageBox.information(parent_widget, "删除成功", f"顶点 {vertex.id} 已删除。")
            self.update_vertex_list()
            if self.canvas:
                self.canvas.repaint()
