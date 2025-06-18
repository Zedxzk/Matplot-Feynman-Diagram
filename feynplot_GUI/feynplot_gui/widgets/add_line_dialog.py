from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt

class AddLineDialog(QDialog):
    def __init__(self, vertices_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加线")
        self.setMinimumWidth(350)

        self.vertices_data = vertices_data # 传入所有可用的顶点数据

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 1. 起始顶点下拉选择框
        self.start_vertex_combo = QComboBox()
        self.end_vertex_combo = QComboBox()

        # 填充下拉框
        if not self.vertices_data:
            # 如果没有顶点，显示提示
            self.start_vertex_combo.addItem("无可用顶点")
            self.end_vertex_combo.addItem("无可用顶点")
            self.start_vertex_combo.setEnabled(False)
            self.end_vertex_combo.setEnabled(False)
        else:
            for i, vertex in enumerate(self.vertices_data):
                display_text = f"V{i}: {vertex.label} ({vertex.x},{vertex.y})"
                self.start_vertex_combo.addItem(display_text, vertex) # 存储顶点对象
                self.end_vertex_combo.addItem(display_text, vertex) # 存储顶点对象
            # 默认选择第一个顶点作为起始，第二个作为结束（如果存在）
            if len(self.vertices_data) > 1:
                self.end_vertex_combo.setCurrentIndex(1)


        form_layout.addRow("起始顶点:", self.start_vertex_combo)
        form_layout.addRow("结束顶点:", self.end_vertex_combo)

        # 2. 粒子类型下拉选择框
        self.particle_type_combo = QComboBox()
        # 这里列出所有支持的粒子类型
        self.particle_types = {
            "费米子线 (Fermion)": "FermionLine",
            "反费米子线 (Anti-Fermion)": "AntiFermionLine",
            "光子线 (Photon)": "PhotonLine",
            "胶子线 (Gluon)": "GluonLine",
            "W+ 玻色子线 (W+)": "WPlusLine",
            "W- 玻色子线 (W-)": "WMinusLine",
            "Z 玻色子线 (Z)": "ZBosonLine",
            # 如果你还有其他线类型，可以在这里添加
        }
        for display_name in self.particle_types.keys():
            self.particle_type_combo.addItem(display_name)
        
        form_layout.addRow("粒子类型:", self.particle_type_combo)

        # 3. 额外属性（例如，箭头和标签）
        self.add_arrow_checkbox = QCheckBox("添加箭头")
        self.add_arrow_checkbox.setChecked(True) # 默认选中

        self.label_input = QLineEdit("") # 可选的标签
        
        form_layout.addRow("显示箭头:", self.add_arrow_checkbox)
        form_layout.addRow("标签 (可选):", self.label_input)


        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_line_data(self):
        """
        返回用户选择的起始顶点、结束顶点、线类型和属性。
        如果选择无效，则返回 None。
        """
        start_vertex = self.start_vertex_combo.currentData() # 获取存储的顶点对象
        end_vertex = self.end_vertex_combo.currentData()

        if start_vertex is None or end_vertex is None:
            # 如果没有可用顶点，或者用户没有选择
            return None

        if start_vertex == end_vertex:
            # 起始顶点和结束顶点不能相同
            QMessageBox.warning(self, "输入错误", "起始顶点和结束顶点不能相同！")
            return None
        
        selected_type_display = self.particle_type_combo.currentText()
        line_type_str = self.particle_types[selected_type_display] # 获取线类型的字符串表示

        arrow = self.add_arrow_checkbox.isChecked()
        label = self.label_input.text().strip()

        return {
            "v_start": start_vertex,
            "v_end": end_vertex,
            "line_type": line_type_str, # 返回字符串，Controller 会据此创建实例
            "arrow": arrow,
            "label": label if label else ""
        }