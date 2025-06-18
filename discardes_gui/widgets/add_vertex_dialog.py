# gui/widgets/add_vertex_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox
from PyQt6.QtCore import Qt

class AddVertexDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加顶点")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.x_input.setPlaceholderText("例如: 0.0")
        self.y_input.setPlaceholderText("例如: 0.0")

        form_layout.addRow("X 坐标:", self.x_input)
        form_layout.addRow("Y 坐标:", self.y_input)
        layout.addLayout(form_layout)

        # 确定 / 取消 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_coordinates(self):
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            return x, y
        except ValueError:
            return None
