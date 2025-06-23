# feynplot_GUI/feynplot_gui/dialogs/add_vertex_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

# 导入 FeynmanDiagram 模型类，用于访问其顶点数据
# 注意：这里我们假设 FeynmanDiagram 提供了访问所有顶点ID的方法
# 如果 FeynmanDiagram 还没有 _vertex_ids 属性，请在 FeynmanDiagram 类中添加
from feynplot.core import diagram
from feynplot.core.diagram import FeynmanDiagram # <-- 确保导入了你的模型类

class AddVertexDialog(QDialog):
    def __init__(self, initial_x: float = 0.0, initial_y: float = 0.0, diagram: FeynmanDiagram = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加顶点")
        self.setMinimumWidth(300)

        self.diagram = diagram # 保存 diagram 引用，以便生成唯一 ID
        
        main_layout = QVBoxLayout(self) # 主布局

        form_layout = QFormLayout() # 表单布局用于 X, Y 和 标签

        # 使用传入的 initial_x 和 initial_y 来设置 QLineEdit 的默认值
        self.x_input = QLineEdit(str(initial_x))
        self.y_input = QLineEdit(str(initial_y))

        # --- 修改点：自动生成唯一的默认标签 ---
        default_label = diagram._generate_unique_vertex_id()
        self.label_input = QLineEdit(default_label)

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
            # 如果标签为空，使用自动生成的默认标签，否则使用用户输入的标签
            return x, y, label if label else diagram._generate_unique_vertex_id() 
        except ValueError:
            QMessageBox.warning(self, "输入错误", "X 和 Y 坐标必须是数字。")
            return None