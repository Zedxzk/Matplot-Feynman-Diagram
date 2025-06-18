# feynplot_GUI/feynplot_gui/item_manager.py (无需修改)

from debug_utils import cout2
from PySide6.QtWidgets import QListWidgetItem, QInputDialog, QMessageBox, QDialog # 使用 PySide6
from PySide6.QtCore import Qt, QPointF
from cycler import V # 使用 PySide6

# 导入你的模型类 (这里直接导入是为了类型提示和实例创建)
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine, LineStyle
)

# 导入自定义对话框 (确保这些文件存在于 feynplot_GUI/feynplot_gui/widgets/ 目录下)
from .widgets.add_vertex_dialog import AddVertexDialog # 这个文件被修改了
from .widgets.add_line_dialog import AddLineDialog
from .widgets.edit_line_dialog import EditLineDialog

class ItemManager:
    def __init__(self, controller):
        self.ctrl = controller # 存储控制器实例
        self._add_line_first_vertex = None # 用于添加线条时的第一个顶点选择

    def update_list_widgets(self):
        """
        更新Qt列表视图以反映模型数据的最新状态。
        """
        print("--- Updating List Widgets ---")
        self.ctrl.vertex_list_widget.clear()
        self.ctrl.line_list_widget.clear()

        for vertex in self.ctrl.diagram_model.vertices:
            item_text = f"[{vertex.id}] Vtx: {vertex.label} ({vertex.x:.2f}, {vertex.y:.2f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, vertex)
            self.ctrl.vertex_list_widget.addItem(item)
            # print(f"Added Vertex to list: ID={vertex.id}, Stored data type: {type(vertex)}, Value: {vertex}") # 调试信息过多可以关闭

        for line in self.ctrl.diagram_model.lines:
            start_label = line.v_start.label if line.v_start else "None"
            end_label = line.v_end.label if line.v_end else "None"
            item_text = f"[{line.id}] Line: {line.label} ({start_label} -> {end_label})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, line)
            self.ctrl.line_list_widget.addItem(item)
            # print(f"Added Line to list: ID={line.id}, Stored data type: {type(line)}, Value: {line}") # 调试信息过多可以关闭
        
        print("--- List Widgets Updated ---")
        # self.ctrl.highlighter.highlight_selected_item() # 确保在列表更新后保持高亮状态


    def add_new_vertex_at_coords(self, x: float, y: float):
        """在指定坐标打开对话框添加一个新顶点。"""
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas 
        dialog = AddVertexDialog(x, y, parent=parent_widget) 
        if dialog.exec() == QDialog.Accepted:
            coords_and_label = dialog.get_coordinates()
            if coords_and_label:
                new_x, new_y, label = coords_and_label
                new_id = f"vtx_{len(self.ctrl.diagram_model.vertices)}" 

                # 修正：使用 VertexType 中已有的成员，例如 GENERIC
                vertex_type = VertexType.GENERIC # <-- 将这里的 ANY 替换为 GENERIC

                # 如果你的 AddVertexDialog 内部有 id 和 type 的输入，并且它们在 accept 后被设置
                # 则可以使用 dialog.vertex_id, dialog.vertex_type
                if hasattr(dialog, 'vertex_id') and dialog.vertex_id:
                    new_id = dialog.vertex_id
                if hasattr(dialog, 'vertex_type') and dialog.vertex_type:
                    # 确保从对话框获取的值是有效的 VertexType 成员
                    try:
                        # 假设对话框返回字符串，需要转换为枚举
                        vertex_type = VertexType[dialog.vertex_type.upper()]
                    except KeyError:
                        print(f"警告: 对话框返回的顶点类型 '{dialog.vertex_type}' 无效。将使用默认类型: {VertexType.GENERIC}")
                        vertex_type = VertexType.GENERIC # 无效则回退到通用类型

                # new_vertex = Vertex(new_x, new_y, label=label, id=new_id, vertex_type=vertex_type)
                self.ctrl.diagram_model.add_vertex(new_x,new_y )
                QMessageBox.information(parent_widget, "添加成功", f"顶点 {new_id} 已添加。")
                self.ctrl.update_view() # 更新视图
            else:
                QMessageBox.warning(parent_widget, "添加失败", "无法获取有效的顶点数据。") # 提示用户失败

    def start_add_line_process(self):
        """
        开始添加线条的过程，提示用户选择第一个顶点。
        """
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas 
        dialog = AddLineDialog(self.ctrl.diagram_model.vertices, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            line_info = dialog.get_line_data()
            if line_info:
                v_start = line_info['v_start']
                v_end = line_info['v_end']
                line_type = line_info['line_type']
                # if v_start == v_end:
                #     QMessageBox.information(parent_widget, "添加失败", "线条的起点和终点不能相同。")
                #     exit(1)
                cout2(f"LineType: {line_type}")
                cout2(f"添加线条: {line_info}")
                try:
                    self.ctrl.diagram_model.add_line(v_start=v_start, v_end=v_end, line_type=line_type)
                except Exception as e:
                    QMessageBox.critical(parent_widget, "添加失败", f"添加线条时发生错误：\n{str(e)}")
                else:
                    QMessageBox.information(parent_widget, "添加成功", "线条已添加。")
                    self.ctrl.update_view()

                

    def edit_vertex_properties(self, vertex_to_edit: Vertex):
        """打开对话框编辑顶点属性。"""
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas
        dialog = EditVertexDialog(vertex_to_edit, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            # 对话框内部应该已经修改了 vertex_to_edit 的属性
            QMessageBox.information(parent_widget, "编辑成功", f"顶点 {vertex_to_edit.id} 属性已更新。")
            self.ctrl.update_view() # 更新视图


    def edit_line_properties(self, line_to_edit: Line):
        """打开对话框编辑线条属性。"""
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas
        dialog = EditLineDialog(line_to_edit, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            # 对话框内部应该已经修改了 line_to_edit 的属性
            QMessageBox.information(parent_widget, "编辑成功", f"线条 {line_to_edit.id} 属性已更新。")
            self.ctrl.update_view() # 更新视图


    def delete_item(self, item_to_delete):
        """
        删除一个顶点或线条。
        """
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas
        reply = QMessageBox.question(parent_widget, '确认删除',
                                     f"您确定要删除 {type(item_to_delete).__name__} ({item_to_delete.id}) 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if isinstance(item_to_delete, Vertex):
                # 删除与该顶点关联的所有线条
                lines_to_remove = [line for line in self.ctrl.diagram_model.lines
                                   if line.v_start is item_to_delete or line.v_end is item_to_delete]
                for line in lines_to_remove:
                    self.ctrl.diagram_model.lines.remove(line)
                self.ctrl.diagram_model.vertices.remove(item_to_delete)
                QMessageBox.information(parent_widget, "删除成功", f"顶点 {item_to_delete.id} 及其关联线条已删除。")

            elif isinstance(item_to_delete, Line):
                self.ctrl.diagram_model.lines.remove(item_to_delete)
                QMessageBox.information(parent_widget, "删除成功", f"线条 {item_to_delete.id} 已删除。")

            # 清除可能的高亮
            if self.ctrl.highlighter.selected_item_data is item_to_delete:
                self.ctrl.highlighter.clear_selection()
            
            self.ctrl.update_view() # 刷新视图