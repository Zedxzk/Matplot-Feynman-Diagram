# feynplot_GUI/feynplot_gui/dialogs/delete_line_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
# 确保导入 FeynmanDiagram 类
from feynplot.core.diagram import FeynmanDiagram 
# 导入 Line 类型用于类型提示
from feynplot.core.line import Line 
from typing import Optional # 导入 Optional 用于类型提示

class DeleteLineDialog(QDialog):
    def __init__(self, diagram: FeynmanDiagram, line_to_delete: Optional[Line] = None, parent=None):
        """
        用于确认删除线条的对话框。

        Args:
            diagram (FeynmanDiagram): 包含所有线条数据的费曼图模型实例。
            line_to_delete (Optional[Line]): 可选参数，如果提供，则预选并锁定此线条。
                                              默认为 None。
            parent (QWidget, optional): 父窗口部件。
        """
        super().__init__(parent)
        self.setWindowTitle("删除线条确认")
        self.setMinimumWidth(300)

        self.diagram = diagram # 存储 diagram 实例
        self.lines_data = diagram.lines # 获取所有可用的线条数据

        # 将传入的预选线条保存到实例变量
        self._pre_selected_line = line_to_delete
        # self.selected_line 将在 get_selected_line 中返回

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
                start_vertex_id = line.v_start.id if line.v_start else "N/A"
                end_vertex_id = line.v_end.id if line.v_end else "N/A"
                line_type_name = type(line).__name__ # 获取线条的实际类型名称 (e.g., FermionLine)

                # 使用 line.label 作为主要显示，如果 label 为空则使用默认格式
                display_text = f"[{line.id}] {line.label or line_type_name} ({start_vertex_id} -> {end_vertex_id})"
                
                # 将实际的 Line 对象作为用户数据存储
                self.delete_line_combobox.addItem(display_text, line)
            
            # 如果提供了预选线条，则设置并锁定下拉框
            if self._pre_selected_line:
                # 查找与 _pre_selected_line 对应的数据项
                # 使用循环查找，因为 findData 默认只比较值，不比较对象ID
                found_index = -1
                for i in range(self.delete_line_combobox.count()):
                    item_data = self.delete_line_combobox.itemData(i)
                    if item_data and hasattr(item_data, 'id') and item_data.id == self._pre_selected_line.id:
                        found_index = i
                        break

                if found_index != -1:
                    self.delete_line_combobox.setCurrentIndex(found_index)
                    self.delete_line_combobox.setEnabled(False) # 锁定下拉框
                else:
                    # 如果预选线条不在当前图中，则退回正常模式并警告
                    QMessageBox.warning(self, "警告", "预选线条在图中不存在，请手动选择。")
                    self._pre_selected_line = None # 清除预选状态
            
            # 如果没有预选，或者预选失败，确保下拉框是可交互的
            if not self._pre_selected_line:
                self.delete_line_combobox.setEnabled(True)

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
            self.delete_line_combobox.setEnabled(False) # 确保禁用
        else:
            # 初始时，OK 按钮默认可用（只要有线条可供选择），除非被锁定且预选失败
            # 如果没有预选，或者预选失败，OK 按钮初始是可用的
            if self._pre_selected_line is None: # 表示用户可以自己选择
                button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            elif found_index == -1: # 表示预选失败，用户仍需选择
                 button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            else: # 预选成功并锁定
                 button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)


    def get_selected_line(self) -> Optional[Line]:
        """
        获取用户选择的 Line 对象。

        Returns:
            Optional[Line]: 用户在下拉列表中选择的 Line 对象，如果没有选择或没有可用线条则返回 None。
        """
        if self.delete_line_combobox.isEnabled() or self._pre_selected_line: # 如果是禁用的，说明有预选
            # 如果有预选，直接返回预选的线条
            if self._pre_selected_line and self.delete_line_combobox.isEnabled() == False:
                return self._pre_selected_line
            
            # 否则，从当前下拉框的选中项中获取
            if self.delete_line_combobox.count() > 0:
                return self.delete_line_combobox.currentData()
        return None