# feynplot_GUI/feynplot_gui/dialogs/add_vertex_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QLabel, QPushButton, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from feynplot_gui.core_ui.msg_box_utils import MsgBox

from feynplot.core import diagram
from feynplot.core.diagram import FeynmanDiagram
from feynplot_gui.core_ui.dialogs.dialog_style import apply_dialog_style, apply_content_layout

class AddVertexDialog(QDialog):
    def __init__(self, initial_x: float = 0.0, initial_y: float = 0.0, diagram: FeynmanDiagram = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("添加顶点"))
        self.setMinimumWidth(300)

        self.diagram = diagram
        apply_dialog_style(self)

        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        form_layout = QFormLayout(scroll_content_widget)
        apply_content_layout(form_layout)

        self.x_input = QLineEdit(str(initial_x))
        self.y_input = QLineEdit(str(initial_y))
        default_label = diagram._generate_unique_vertex_id() if diagram else "V"
        self.label_input = QLineEdit(default_label)

        form_layout.addRow("X 坐标:", self.x_input)
        form_layout.addRow("Y 坐标:", self.y_input)
        form_layout.addRow("标签:", self.label_input)

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        ok_button = QPushButton(self.tr("确定"))
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton(self.tr("取消"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)



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
            # 如果标签为空，使用自动生成的默认标签，否则使用用户输入的标签
            return x, y, label if label else (self.diagram._generate_unique_vertex_id() if self.diagram else "V") 
        except ValueError:
            MsgBox.warning(self, self.tr("输入错误"), self.tr("X 和 Y 坐标必须是数字。"))
            return None