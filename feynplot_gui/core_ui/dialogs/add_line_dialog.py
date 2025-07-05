from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QCheckBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from feynplot.core.line import *
from feynplot.core.vertex import Vertex # Assuming you have a Vertex class
from PySide6.QtGui import QFont, QFontDatabase

class AddLineDialog(QDialog):
    # Add initial_start_vertex_id to the constructor
    def __init__(self, vertices_data: list[Vertex], parent=None, initial_start_vertex_id: str = None):
        super().__init__(parent)
        self.setWindowTitle("添加线")
        self.setMinimumWidth(350)

        self.vertices_data = vertices_data  # 传入所有可用的顶点数据
        # Create a map for quick lookup of vertices by ID
        self.vertex_map = {v.id: v for v in vertices_data}

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
                label = getattr(vertex, 'label', '')
                display_text = f"{label:<10} ({vertex.x:6.2f},{vertex.y:6.2f}) - |{vertex.id}|"
                # 取系统固定宽度字体
                # mono_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
                # 或者手动指定一个等宽字体，比如 Courier New
                mono_font = QFont("Consolas", 10)

                # 应用到 ComboBox 的显示区域
                self.start_vertex_combo.setFont(mono_font)
                self.end_vertex_combo.setFont(mono_font)

                # 应用到弹出列表
                self.start_vertex_combo.view().setFont(mono_font)
                self.end_vertex_combo.view().setFont(mono_font)
                self.start_vertex_combo.addItem(display_text, vertex)  # 存储顶点对象
                self.end_vertex_combo.addItem(display_text, vertex)    # 存储顶点对象

            # --- **新增逻辑：处理 initial_start_vertex_id** ---
            if initial_start_vertex_id:
                # 尝试根据 ID 找到对应的顶点在 ComboBox 中的索引
                # currentData() returns the stored Python object, so iterate and check
                found_index = -1
                for i in range(self.start_vertex_combo.count()):
                    if self.start_vertex_combo.itemData(i) and self.start_vertex_combo.itemData(i).id == initial_start_vertex_id:
                        found_index = i
                        break
                
                if found_index != -1:
                    self.start_vertex_combo.setCurrentIndex(found_index)
                    # Optionally, you might want to disable the start combo box
                    # if the start vertex is fixed by the context menu action
                    # self.start_vertex_combo.setEnabled(False)
                else:
                    # If initial_start_vertex_id is provided but not found, warn (optional)
                    QMessageBox.warning(self, "警告", f"预设起始顶点 ID '{initial_start_vertex_id}' 未找到。")
                    # Fallback to default selection if ID not found
                    if len(self.vertices_data) > 1:
                        self.end_vertex_combo.setCurrentIndex(1)
            else:
                # 原始逻辑：默认选择第一个顶点作为起始，第二个作为结束（如果存在）
                if len(self.vertices_data) > 1:
                    self.end_vertex_combo.setCurrentIndex(1)


        form_layout.addRow("起始顶点:", self.start_vertex_combo)
        form_layout.addRow("结束顶点:", self.end_vertex_combo)

        # 2. 粒子类型下拉选择框
        self.particle_type_combo = QComboBox()
        # 这里列出所有支持的粒子类型
        self.particle_types = {
            "费米子线 (Fermion)": FermionLine,
            "反费米子线 (Anti-Fermion)": AntiFermionLine,
            "光子线 (Photon)": PhotonLine,
            "胶子线 (Gluon)": GluonLine,
            "W+ 玻色子线 (W+)": WPlusLine,
            "W- 玻色子线 (W-)": WMinusLine,
            "Z 玻色子线 (Z)": ZBosonLine,
            # 如果你还有其他线类型，可以在这里添加
        }
        for display_name in self.particle_types.keys():
            self.particle_type_combo.addItem(display_name)
        
        form_layout.addRow("粒子类型:", self.particle_type_combo)

        # 3. 额外属性（例如，箭头和标签）
        self.add_arrow_checkbox = QCheckBox(self.tr("添加箭头"))
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
        start_vertex = self.start_vertex_combo.currentData()  # 获取存储的顶点对象
        end_vertex = self.end_vertex_combo.currentData()

        if start_vertex is None or end_vertex is None:
            # 如果没有可用顶点，或者用户没有选择
            QMessageBox.warning(self, "输入错误", "请选择起始和结束顶点。")
            return None

        if start_vertex == end_vertex:
            # 起始顶点和结束顶点不能相同
            QMessageBox.warning(self, "输入错误", "起始顶点和结束顶点不能相同！")
            return None
        
        selected_type_display = self.particle_type_combo.currentText()
        line_type_class = self.particle_types[selected_type_display] # 获取线类型的类

        arrow = self.add_arrow_checkbox.isChecked()
        label = self.label_input.text().strip()

        return {
            "v_start": start_vertex,
            "v_end": end_vertex,
            "line_type": line_type_class, # 返回类，Controller 会据此创建实例
            "arrow": arrow,
            "label": label if label else ""
        }

    # You might want to update your `Vertex` display text to include `label` more robustly
    # For instance, if `vertex.label` could be None or an empty string, `getattr(vertex, 'label', '')` is safer.
    # The `display_text` line in `__init__` has been updated to reflect this.