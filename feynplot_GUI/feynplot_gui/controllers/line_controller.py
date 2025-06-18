from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
from PySide6.QtCore import Qt

from feynplot.core.line import Line, LineStyle, FermionLine, GluonLine, PhotonLine  # 这里补充需要的线条类
from ..widgets.add_line_dialog import AddLineDialog
from ..widgets.edit_line_dialog import EditLineDialog

class LineController:
    def __init__(self, diagram_model, line_list_widget, main_window=None, canvas=None):
        self.diagram_model = diagram_model
        self.line_list_widget = line_list_widget
        self.main_window = main_window
        self.canvas = canvas

    def update_line_list(self):
        self.line_list_widget.clear()
        for line in self.diagram_model.lines:
            start_label = line.v_start.label if line.v_start else "None"
            end_label = line.v_end.label if line.v_end else "None"
            item_text = f"[{line.id}] Line: {line.label} ({start_label} -> {end_label})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, line)
            self.line_list_widget.addItem(item)

    def start_add_line_process(self):
        parent_widget = self.main_window if self.main_window else self.canvas
        dialog = AddLineDialog(self.diagram_model.vertices, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            line_info = dialog.get_line_data()
            if line_info:
                v_start = line_info['v_start']
                v_end = line_info['v_end']
                line_type = line_info['line_type']
                if v_start == v_end:
                    QMessageBox.warning(parent_widget, "输入错误", "起始顶点和结束顶点不能相同！")
                    return
                try:
                    self.diagram_model.add_line(v_start=v_start, v_end=v_end, line_type=line_type)
                except Exception as e:
                    QMessageBox.critical(parent_widget, "添加失败", f"添加线条时发生错误：\n{str(e)}")
                else:
                    QMessageBox.information(parent_widget, "添加成功", "线条已添加。")
                    self.update_line_list()
                    if self.canvas:
                        self.canvas.repaint()

    def edit_line_properties(self, line: Line):
        parent_widget = self.main_window if self.main_window else self.canvas
        dialog = EditLineDialog(line, parent=parent_widget)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(parent_widget, "编辑成功", f"线条 {line.id} 属性已更新。")
            self.update_line_list()
            if self.canvas:
                self.canvas.repaint()

    def delete_line(self, line: Line):
        parent_widget = self.main_window if self.main_window else self.canvas
        reply = QMessageBox.question(parent_widget, '确认删除',
                                     f"您确定要删除线条 {line.id} 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.diagram_model.lines.remove(line)
            QMessageBox.information(parent_widget, "删除成功", f"线条 {line.id} 已删除。")
            self.update_line_list()
            if self.canvas:
                self.canvas.repaint()
