# feynplot_GUI/feynplot_gui/dialogs/delete_line_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
# 确保导入 FeynmanDiagram 类
from feynplot.core.diagram import FeynmanDiagram 
# 如果你的 Line 类也需要显示一些特定属性，可能需要导入它
from feynplot.core.line import Line # 仅为了类型提示，实际可能不需要在Dialog中直接使用

class DeleteLineDialog(QDialog):
    def __init__(self, diagram: FeynmanDiagram, parent=None):
        """
        用于确认删除线条的对话框。
        Args:
            diagram (FeynmanDiagram): 包含所有线条数据的费曼图模型实例。
            parent (QWidget, optional): 父窗口部件。
        """
        super().__init__(parent)
        self.setWindowTitle("删除线条确认")
        self.setMinimumWidth(300)

        self.diagram = diagram # 存储 diagram 实例
        self.lines_data = diagram.lines # 获取所有可用的线条数据

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 1. 创建用于选择线条的下拉列表
        self.delete_line_combobox = QComboBox()
        form_layout.addRow("选择要删除的线条", self.delete_line_combobox)

        # 2. 填充下拉列表
        if not self.lines_data:
            self.delete_line_combobox.addItem("无可用线条")
            self.delete_line_combobox.setEnabled(False) # 如果没有线条，禁用下拉列表
        else:
            for i, line in enumerate(self.lines_data):
                # 尝试构建一个有意义的显示文本，显示线条ID、类型以及连接的顶点ID
                # 假设 Line 对象有 v_start 和 v_end 属性，它们是 Vertex 对象
                start_vertex_id = line.v_start.id if line.v_start else "N/A"
                end_vertex_id = line.v_end.id if line.v_end else "N/A"
                line_type_name = type(line).__name__ # 获取线条的实际类型名称 (e.g., FermionLine)

                display_text = f"L{i}: {line.id} ({line_type_name}) from {start_vertex_id} to {end_vertex_id}"
                # 将实际的 Line 对象作为用户数据存储
                self.delete_line_combobox.addItem(display_text, line)
        
        main_layout.addLayout(form_layout)

        # 3. 添加标准确认和取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept) # 连接 OK 按钮到对话框的 accept 槽
        button_box.rejected.connect(self.reject) # 连接 Cancel 按钮到对话框的 reject 槽
        main_layout.addWidget(button_box)

        # 初始时，如果没有任何线条，禁用 OK 按钮
        if not self.lines_data:
            button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def get_selected_line(self) :
        """
        获取用户选择的 Line 对象。
        Returns:
            Line: 用户在下拉列表中选择的 Line 对象，如果没有选择或没有可用线条则返回 None。
        """
        if self.delete_line_combobox.isEnabled() and self.delete_line_combobox.count() > 0:
            # 获取当前选中项的用户数据，这个用户数据就是我们存储的 Line 对象
            return self.delete_line_combobox.currentData()
        return None

# # 示例用法 (仅供测试，通常在 MainController 或其他地方调用)
# if __name__ == '__main__':
#     import sys
#     from PySide6.QtWidgets import QApplication
#     from feynplot.core.vertex import Vertex
#     from feynplot.core.line import FermionLine, PhotonLine

#     app = QApplication(sys.argv)

#     # 创建一个虚拟的 FeynmanDiagram 实例并添加一些数据
#     diagram = FeynmanDiagram()
#     v1 = diagram.add_vertex(x=0.0, y=0.0, label="Origin")
#     v2 = diagram.add_vertex(x=1.0, y=1.0, label="Point A")
#     v3 = diagram.add_vertex(x=2.0, y=0.0, label="Point B")

#     l1 = diagram.add_line(v_start=v1, v_end=v2, line_type=FermionLine)
#     l2 = diagram.add_line(v_start=v2, v_end=v3, line_type=PhotonLine, label="Photon")
#     l3 = diagram.add_line(v_start=v3, v_end=v1, line_type=FermionLine, label="Return")

#     dialog = DeleteLineDialog(diagram)
#     result = dialog.exec() # 显示对话框并等待用户交互

#     if result == QDialog.Accepted:
#         selected_line = dialog.get_selected_line()
#         if selected_line:
#             print(f"用户选择了删除线条: ID={selected_line.id}, 类型={type(selected_line).__name__}")
#             # 在实际应用中，这里会调用 diagram.delete_line(selected_line.id)
#             if diagram.delete_line(selected_line.id):
#                 print("线条已从模型中删除。")
#             else:
#                 print("线条删除失败。")
#         else:
#             print("没有选择任何线条或没有可用线条可删除。")
#     else:
#         print("用户取消了删除操作。")

#     # 再次显示对话框，看看删除后是否更新
#     # dialog_after_delete = DeleteLineDialog(diagram)
#     # dialog_after_delete.exec()

#     sys.exit(app.exec())