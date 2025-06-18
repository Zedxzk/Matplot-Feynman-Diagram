# from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
# from PySide6.QtCore import Qt

# from feynplot.core.line import Line, LineStyle, FermionLine, GluonLine, PhotonLine  # 这里补充需要的线条类
# from ..widgets.add_line_dialog import AddLineDialog
# from ..widgets.edit_line_dialog import EditLineDialog

# class LineController:
#     def __init__(self, diagram_model, line_list_widget, main_window=None, canvas=None):
#         self.diagram_model = diagram_model
#         self.line_list_widget = line_list_widget
#         self.main_window = main_window
#         self.canvas = canvas

#     def update_line_list(self):
#         self.line_list_widget.clear()
#         for line in self.diagram_model.lines:
#             start_label = line.v_start.label if line.v_start else "None"
#             end_label = line.v_end.label if line.v_end else "None"
#             item_text = f"[{line.id}] Line: {line.label} ({start_label} -> {end_label})"
#             item = QListWidgetItem(item_text)
#             item.setData(Qt.ItemDataRole.UserRole, line)
#             self.line_list_widget.addItem(item)

#     def start_add_line_process(self):
#         parent_widget = self.main_window if self.main_window else self.canvas
#         dialog = AddLineDialog(self.diagram_model.vertices, parent=parent_widget)
#         if dialog.exec() == QDialog.Accepted:
#             line_info = dialog.get_line_data()
#             if line_info:
#                 v_start = line_info['v_start']
#                 v_end = line_info['v_end']
#                 line_type = line_info['line_type']
#                 if v_start == v_end:
#                     QMessageBox.warning(parent_widget, "输入错误", "起始顶点和结束顶点不能相同！")
#                     return
#                 try:
#                     self.diagram_model.add_line(v_start=v_start, v_end=v_end, line_type=line_type)
#                 except Exception as e:
#                     QMessageBox.critical(parent_widget, "添加失败", f"添加线条时发生错误：\n{str(e)}")
#                 else:
#                     QMessageBox.information(parent_widget, "添加成功", "线条已添加。")
#                     self.update_line_list()
#                     if self.canvas:
#                         self.canvas.repaint()

#     def edit_line_properties(self, line: Line):
#         parent_widget = self.main_window if self.main_window else self.canvas
#         dialog = EditLineDialog(line, parent=parent_widget)
#         if dialog.exec() == QDialog.Accepted:
#             QMessageBox.information(parent_widget, "编辑成功", f"线条 {line.id} 属性已更新。")
#             self.update_line_list()
#             if self.canvas:
#                 self.canvas.repaint()

#     def delete_line(self, line: Line):
#         parent_widget = self.main_window if self.main_window else self.canvas
#         reply = QMessageBox.question(parent_widget, '确认删除',
#                                      f"您确定要删除线条 {line.id} 吗？",
#                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#         if reply == QMessageBox.Yes:
#             self.diagram_model.lines.remove(line)
#             QMessageBox.information(parent_widget, "删除成功", f"线条 {line.id} 已删除。")
#             self.update_line_list()
#             if self.canvas:
#                 self.canvas.repaint()

#     def update(self):
#         pass


# feynplot_gui/controllers/line_controller.py

from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
from PySide6.QtCore import Qt, QObject, Signal # 导入 QObject 和 Signal

# 导入核心模型类
from feynplot.core.line import Line, LineStyle, FermionLine, GluonLine, PhotonLine
from feynplot.core.diagram import FeynmanDiagram # 导入 FeynmanDiagram 用于类型提示

# 导入 UI Widget 和 Dialogs
from feynplot_gui.widgets.line_list_widget import LineListWidget # 假设你有这个 Widget
from feynplot_gui.widgets.add_line_dialog import AddLineDialog
from feynplot_gui.widgets.edit_line_dialog import EditLineDialog

# 【重要修改】移除对 MainController 的直接导入，以避免循环导入
# from feynplot_gui.controllers.main_controller import MainController

class LineController(QObject): # 继承自 QObject
    def __init__(self, diagram_model: FeynmanDiagram, line_list_widget: LineListWidget, main_controller: 'MainController'): # 修正后的签名和类型提示
        super().__init__() # 调用 QObject 的构造函数

        self.diagram_model = diagram_model
        self.line_list_widget = line_list_widget
        self.main_controller = main_controller # 保存 MainController 的引用

        # 移除不再需要的参数
        # self.main_window = main_window
        # self.canvas = canvas

        self.setup_connections()
        self.update_line_list() # 初始化时更新列表


    def setup_connections(self):
        """连接 LineListWidget 的信号到本控制器的槽函数。"""
        self.line_list_widget.line_selected.connect(self._on_line_list_selected)
        self.line_list_widget.line_double_clicked.connect(self._on_line_list_double_clicked)

    def update_line_list(self):
        """根据 diagram_model 中的数据刷新线条列表视图。"""
        self.line_list_widget.clear()
        for line in self.diagram_model.lines:
            start_label = line.v_start.label if line.v_start else "None"
            end_label = line.v_end.label if line.v_end else "None"
            item_text = f"[{line.id}] Line: {line.label} ({start_label} -> {end_label})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, line.id) # 存储线条ID，而不是整个对象
            self.line_list_widget.addItem(item)
        
        # 重新应用选中状态
        current_selected = self.main_controller.get_selected_item()
        if isinstance(current_selected, Line):
            self.set_selected_item_in_list(current_selected)

        self.main_controller.status_message.emit("线条列表已更新。")

    def set_selected_item_in_list(self, item: [Line, None]):
        """
        接收来自 MainController 的选中项，并在线条列表中设置/清除选中状态。
        """
        self.line_list_widget.clearSelection() # 先清除所有选中状态

        if isinstance(item, Line):
            for i in range(self.line_list_widget.count()):
                list_item = self.line_list_widget.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == item.id:
                    list_item.setSelected(True)
                    self.line_list_widget.scrollToItem(list_item) # 滚动到选中项
                    break

    # --- 槽函数：响应 LineListWidget 的信号 ---

    def _on_line_list_selected(self, line_id: str):
        """
        当用户在线条列表中选择一条线条时触发。
        通知 MainController 统一管理选中状态。
        """
        line = self.diagram_model.get_line_by_id(line_id)
        if line:
            self.main_controller.select_item(line) # 调用 MainController 的 select_item 方法
        else:
            self.main_controller.status_message.emit(f"错误：未找到ID为 {line_id} 的线条。")

    def _on_line_list_double_clicked(self, line_id: str):
        """
        当用户在线条列表中双击一条线条时触发。
        通知 MainController 打开属性编辑器。
        """
        line = self.diagram_model.get_line_by_id(line_id)
        if line:
            self.main_controller.edit_item_properties(line) # 调用 MainController 的 edit_item_properties 方法


    # --- 以下方法现在由 MainController 统一管理，LineController 不再直接处理 ---
    # start_add_line_process: 现在由 MainController 的 start_add_line_process 方法处理
    # edit_line_properties: 现在由 MainController 的 edit_item_properties 方法处理
    # delete_line: 现在由 MainController 的 delete_selected_line 方法处理
    # 这些方法如果需要，可以在 LineController 中实现一个包装，然后调用 MainController 的方法，
    # 但直接在 MainController 中处理更符合其协调者的角色。

    def update(self):
        """一个通用的更新方法，如果需要，可以由 MainController 调用。"""
        pass # 目前不需要额外逻辑