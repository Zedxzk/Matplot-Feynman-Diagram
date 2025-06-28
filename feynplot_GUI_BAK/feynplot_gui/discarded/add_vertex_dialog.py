# feynplot_GUI/feynplot_gui/dialogs/add_vertex_dialog.py (这是你需要修改的文件)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QDialogButtonBox, QMessageBox, QLabel 
)
from PySide6.QtCore import Qt

class AddVertexDialog(QDialog):
    # 修改这里，让 __init__ 接受初始的 x 和 y 坐标
    def __init__(self, initial_x: float = 0.0, initial_y: float = 0.0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加顶点")
        self.setMinimumWidth(300)

        main_layout = QVBoxLayout(self) # 主布局

        form_layout = QFormLayout() # 表单布局用于 X, Y 和 标签

        # 使用传入的 initial_x 和 initial_y 来设置 QLineEdit 的默认值
        self.x_input = QLineEdit(str(initial_x))
        self.y_input = QLineEdit(str(initial_y))
        self.label_input = QLineEdit("New Vertex")

        form_layout.addRow("X 坐标:", self.x_input)
        form_layout.addRow("Y 坐标:", self.y_input)
        form_layout.addRow("标签:", self.label_input)

        main_layout.addLayout(form_layout) # 将表单布局添加到主布局

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box) # 将按钮盒添加到主布局

    def get_coordinates(self):
        """
        返回输入的坐标和标签。
        如果转换失败则返回 None，并显示警告。
        """
        x_text = self.x_input.text().strip()
        y_text = self.y_input.text().strip()
        label = self.label_input.text().strip()

        try:
            x = float(x_text)
            y = float(y_text)
            return x, y, label if label else "New Vertex"
        except ValueError:
            QMessageBox.warning(self, "输入错误", "X 和 Y 坐标必须是数字。")
            return None