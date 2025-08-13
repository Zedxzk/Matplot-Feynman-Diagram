from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QCheckBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from feynplot.core.line import *
from feynplot.core.vertex import Vertex
from typing import List, Tuple, Dict, Any

class AddLineDialog(QDialog):
    def __init__(self, vertices_data: List[Vertex], parent=None, initial_start_vertex_id: str = None):
        super().__init__(parent)
        self.setWindowTitle("添加线")
        self.setMinimumWidth(350)

        self.vertices_data = vertices_data
        self.vertex_map = {v.id: v for v in vertices_data}

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 1. 起始顶点下拉选择框
        self.start_vertex_combo = QComboBox()
        self.end_vertex_combo = QComboBox()

        if not self.vertices_data:
            self.start_vertex_combo.addItem("无可用顶点")
            self.end_vertex_combo.addItem("无可用顶点")
            self.start_vertex_combo.setEnabled(False)
            self.end_vertex_combo.setEnabled(False)
        else:
            mono_font = QFont("Consolas", 10)
            self.start_vertex_combo.setFont(mono_font)
            self.end_vertex_combo.setFont(mono_font)
            self.start_vertex_combo.view().setFont(mono_font)
            self.end_vertex_combo.view().setFont(mono_font)
            
            for vertex in self.vertices_data:
                label = getattr(vertex, 'label', '')
                display_text = f"{label:<10} ({vertex.x:6.2f},{vertex.y:6.2f}) - |{vertex.id}|"
                self.start_vertex_combo.addItem(display_text, vertex)
                self.end_vertex_combo.addItem(display_text, vertex)

            if initial_start_vertex_id:
                found_index = -1
                for i in range(self.start_vertex_combo.count()):
                    if self.start_vertex_combo.itemData(i) and self.start_vertex_combo.itemData(i).id == initial_start_vertex_id:
                        found_index = i
                        break
                
                if found_index != -1:
                    self.start_vertex_combo.setCurrentIndex(found_index)
                else:
                    QMessageBox.warning(self, "警告", f"预设起始顶点 ID '{initial_start_vertex_id}' 未找到。")
                    if len(self.vertices_data) > 1:
                        self.end_vertex_combo.setCurrentIndex(1)
            else:
                if len(self.vertices_data) > 1:
                    self.end_vertex_combo.setCurrentIndex(1)

        # 2. 新增一个复选框来控制是否为自环
        self.is_loop_checkbox = QCheckBox("创建自环 (Loop)")
        # 连接信号，当复选框状态改变时，更新UI
        self.is_loop_checkbox.stateChanged.connect(self._on_is_loop_state_changed)
        
        # 连接起点选择框的信号到新的槽函数
        self.start_vertex_combo.currentIndexChanged.connect(self._on_start_vertex_changed)
        
        # 3. 粒子类型下拉选择框
        self.particle_type_combo = QComboBox()
        self.particle_types = {
            "费米子线 (Fermion)": FermionLine,
            "反费米子线 (Anti-Fermion)": AntiFermionLine,
            "光子线 (Photon)": PhotonLine,
            "胶子线 (Gluon)": GluonLine,
            "W+ 玻色子线 (W+)": WPlusLine,
            "W- 玻色子线 (W-)": WMinusLine,
            "Z 玻色子线 (Z)": ZBosonLine,
        }
        for display_name in self.particle_types.keys():
            self.particle_type_combo.addItem(display_name)
        
        # 将UI组件添加到布局中
        form_layout.addRow("起始顶点:", self.start_vertex_combo)
        form_layout.addRow("结束顶点:", self.end_vertex_combo)
        form_layout.addRow(self.is_loop_checkbox)
        form_layout.addRow("粒子类型:", self.particle_type_combo)

        # 4. 额外属性（箭头和标签）
        self.add_arrow_checkbox = QCheckBox("添加箭头")
        self.add_arrow_checkbox.setChecked(True)
        self.label_input = QLineEdit("")
        
        form_layout.addRow("显示箭头:", self.add_arrow_checkbox)
        form_layout.addRow("标签 (可选):", self.label_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def _on_is_loop_state_changed(self, state: int):
        """
        根据自环复选框的状态，启用或禁用结束顶点选择框，并同步其内容。
        """
        is_loop = (state == Qt.CheckState.Checked.value)
        self.end_vertex_combo.setEnabled(not is_loop)
        # 如果是环形，立即将结束顶点设置为与起始顶点相同
        if is_loop:
            self.end_vertex_combo.setCurrentIndex(self.start_vertex_combo.currentIndex())
            
    def _on_start_vertex_changed(self, index: int):
        """
        当起始顶点选择发生变化时调用。如果处于环形模式，则同步结束顶点。
        """
        if self.is_loop_checkbox.isChecked():
            self.end_vertex_combo.setCurrentIndex(index)

    def get_line_data(self) -> Dict[str, Any] | None:
        """
        返回用户选择的起始顶点、结束顶点、线类型和属性。
        如果选择无效，则返回 None。
        """
        start_vertex = self.start_vertex_combo.currentData()
        is_loop = self.is_loop_checkbox.isChecked()
        
        if start_vertex is None:
            QMessageBox.warning(self, "输入错误", "请选择一个起始顶点。")
            return None

        # 根据是否是自环，确定结束顶点
        if is_loop:
            end_vertex = start_vertex
        else:
            end_vertex = self.end_vertex_combo.currentData()
            if end_vertex is None:
                QMessageBox.warning(self, "输入错误", "请选择一个结束顶点。")
                return None
            
            if start_vertex == end_vertex:
                QMessageBox.warning(self, "输入错误", "起始顶点和结束顶点不能相同！")
                return None
        
        selected_type_display = self.particle_type_combo.currentText()
        line_type_class = self.particle_types.get(selected_type_display)
        if line_type_class is None:
            QMessageBox.warning(self, "输入错误", "无效的粒子类型。")
            return None

        arrow = self.add_arrow_checkbox.isChecked()
        label = self.label_input.text().strip()

        return {
            "v_start": start_vertex,
            "v_end": end_vertex,
            "line_type": line_type_class,
            "arrow": arrow,
            "label": label if label else "",
            "loop": is_loop
        }