# feynplot_GUI/feynplot_gui/item_manager.py (无需修改)

from PySide6.QtWidgets import QListWidgetItem, QInputDialog, QMessageBox, QDialog # 使用 PySide6
from PySide6.QtCore import Qt, QPointF # 使用 PySide6

# 导入你的模型类 (这里直接导入是为了类型提示和实例创建)
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine, LineStyle
)

# 导入自定义对话框 (确保这些文件存在于 feynplot_GUI/feynplot_gui/widgets/ 目录下)
from .widgets.add_vertex_dialog import AddVertexDialog # 这个文件被修改了
from .widgets.add_line_dialog import AddLineDialog
from .widgets.edit_vertex_dialog import EditVertexDialog
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
        QMessageBox.information(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                 "添加线条", "请点击图表中的第一个顶点作为线条的起点。")
        self._add_line_first_vertex = None # 重置选择
        # 连接一个临时信号槽来捕获下一次的顶点点击
        self.ctrl.vertex_list_widget.itemClicked.connect(self._on_first_vertex_selected_for_line)
        self.ctrl.canvas.canvas.mpl_connect('button_press_event', self._on_canvas_click_for_line_start)


    def _on_first_vertex_selected_for_line(self, item):
        """
        处理用户在列表或画布上选择第一个顶点作为线条起点的事件。
        """
        # 注意：QListWidgetItem(userData=clicked_item) 在 PySide6 中是 QListWidgetItem().setData(Qt.ItemDataRole.UserRole, clicked_item)
        # item.data(Qt.ItemDataRole.UserRole) 才能获取到数据
        vertex = item.data(Qt.ItemDataRole.UserRole) if isinstance(item, QListWidgetItem) else item # 适配两种传入方式
        
        if isinstance(vertex, Vertex):
            self._add_line_first_vertex = vertex
            QMessageBox.information(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                     "添加线条", f"已选择起点: {vertex.id}。现在请点击图表中的第二个顶点作为线条的终点。")
            # 断开第一个顶点的连接，连接第二个顶点的捕获
            self.ctrl.vertex_list_widget.itemClicked.disconnect(self._on_first_vertex_selected_for_line)
            self.ctrl.canvas.canvas.mpl_disconnect('button_press_event', self._on_canvas_click_for_line_start)
            
            # 连接捕获第二个顶点的事件
            self.ctrl.vertex_list_widget.itemClicked.connect(self._on_second_vertex_selected_for_line)
            self.ctrl.canvas.canvas.mpl_connect('button_press_event', self._on_canvas_click_for_line_end)
        else:
            QMessageBox.warning(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                 "错误", "请选择一个有效的顶点作为线条起点。")
            self.cancel_add_line_process() # 用户未选择有效顶点，取消流程

    def _on_canvas_click_for_line_start(self, event):
        """处理画布点击以选择第一个顶点。"""
        if event.inaxes == self.ctrl.canvas.axes and event.button == 1:
            clicked_item = self.ctrl.mouse_handler._get_item_at_coords(event.xdata, event.ydata)
            if isinstance(clicked_item, Vertex):
                # 模拟 QListWidgetItem，但直接传递 Vertex 对象
                # _on_first_vertex_selected_for_line 需要能够处理直接的 Vertex 对象
                self._on_first_vertex_selected_for_line(clicked_item) 
            else:
                QMessageBox.warning(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                     "错误", "请点击一个顶点作为线条起点。")
                self.cancel_add_line_process() # 用户未选择有效顶点，取消流程


    def _on_second_vertex_selected_for_line(self, item):
        """
        处理用户在列表或画布上选择第二个顶点作为线条终点的事件。
        """
        # 同样，适配两种传入方式
        end_vertex = item.data(Qt.ItemDataRole.UserRole) if isinstance(item, QListWidgetItem) else item

        if isinstance(end_vertex, Vertex) and self._add_line_first_vertex and self._add_line_first_vertex is not end_vertex:
            self.open_add_line_dialog(self._add_line_first_vertex, end_vertex)
            self.cancel_add_line_process() # 流程结束，清理状态
        else:
            QMessageBox.warning(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                 "错误", "请选择一个有效的不同于起点的顶点作为线条终点。")
            self.cancel_add_line_process() # 用户未选择有效顶点，取消流程

    def _on_canvas_click_for_line_end(self, event):
        """处理画布点击以选择第二个顶点。"""
        if event.inaxes == self.ctrl.canvas.axes and event.button == 1:
            clicked_item = self.ctrl.mouse_handler._get_item_at_coords(event.xdata, event.ydata)
            if isinstance(clicked_item, Vertex):
                # 模拟 QListWidgetItem，但直接传递 Vertex 对象
                self._on_second_vertex_selected_for_line(clicked_item) 
            else:
                QMessageBox.warning(self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas, 
                                     "错误", "请点击一个顶点作为线条终点。")
                self.cancel_add_line_process() # 用户未选择有效顶点，取消流程

    def cancel_add_line_process(self):
        """取消添加线条的流程，清理所有临时连接。"""
        self._add_line_first_vertex = None
        try:
            self.ctrl.vertex_list_widget.itemClicked.disconnect(self._on_first_vertex_selected_for_line)
        except TypeError: # 如果未连接，则会抛出TypeError
            pass
        try:
            self.ctrl.vertex_list_widget.itemClicked.disconnect(self._on_second_vertex_selected_for_line)
        except TypeError:
            pass
        try:
            self.ctrl.canvas.canvas.mpl_disconnect('button_press_event', self._on_canvas_click_for_line_start)
        except TypeError:
            pass
        try:
            self.ctrl.canvas.canvas.mpl_disconnect('button_press_event', self._on_canvas_click_for_line_end)
        except TypeError:
            pass
        print("添加线条流程已取消/完成。")


    def open_add_line_dialog(self, v_start: Vertex, v_end: Vertex):
        """打开添加线条的对话框。"""
        parent_widget = self.ctrl.main_window if self.ctrl.main_window else self.ctrl.canvas
        dialog = AddLineDialog(v_start, v_end, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            new_id = dialog.line_id
            label = dialog.line_label
            line_type = dialog.line_type # 获取线条类型
            
            # 根据 line_type 创建不同的线条实例
            if line_type == "FermionLine":
                new_line = FermionLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "AntiFermionLine":
                new_line = AntiFermionLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "PhotonLine":
                new_line = PhotonLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "GluonLine":
                new_line = GluonLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "WPlusLine":
                new_line = WPlusLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "WMinusLine":
                new_line = WMinusLine(v_start, v_end, label=label, id=new_id)
            elif line_type == "ZBosonLine":
                new_line = ZBosonLine(v_start, v_end, label=label, id=new_id)
            else:
                new_line = Line(v_start, v_end, label=label, id=new_id) # 默认通用Line

            self.ctrl.diagram_model.add_line(new_line)
            QMessageBox.information(parent_widget, "添加成功", f"线条 {new_id} 已添加。")
            self.ctrl.update_view() # 更新视图


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