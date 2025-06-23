# feynplot_GUI/feynplot_gui/controllers/vertex_dialogs/edit_vertex.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog, QCheckBox, QGroupBox, QSpinBox,
    QMessageBox, QFontComboBox # 导入 QFontComboBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from feynplot.core.vertex import Vertex, VertexType
import numpy as np

def open_edit_vertex_dialog(vertex: Vertex, diagram_model, parent_widget=None) -> bool:
    """
    打开一个对话框以编辑给定 Vertex 对象的属性。
    此函数现在包含了 EditVertexDialog 的完整实现。
    """
    if not isinstance(vertex, Vertex):
        QMessageBox.critical(parent_widget, "错误", "提供的对象不是一个有效的顶点。")
        return False

    class _InternalEditVertexDialog(QDialog):
        def __init__(self, vertex_obj: Vertex, parent_dialog=None):
            super().__init__(parent_dialog)
            self.setWindowTitle(f"编辑顶点: {vertex_obj.label} (ID: {vertex_obj.id})")
            self.setGeometry(200, 200, 400, 600)
            
            self.vertex = vertex_obj
            self.original_vertex_id = vertex_obj.id
            self._original_x = vertex_obj.x
            self._original_y = vertex_obj.y

            self.layout = QVBoxLayout(self)

            # --- 基本属性 ---
            basic_group = QGroupBox("基本属性")
            basic_layout = QVBoxLayout(basic_group)
            self.layout.addWidget(basic_group)

            self.x_layout, self.x_input = self._create_spinbox_row("X 坐标:", self.vertex.x)
            self.y_layout, self.y_input = self._create_spinbox_row("Y 坐标:", self.vertex.y)
            basic_layout.addLayout(self.x_layout)
            basic_layout.addLayout(self.y_layout)

            label_layout = QHBoxLayout()
            label_layout.addWidget(QLabel("标签:"))
            self.label_input = QLineEdit(self.vertex.label)
            label_layout.addWidget(self.label_input)
            basic_layout.addLayout(label_layout)

            # --- 标签字体大小 ---
            # 使用 getattr 安全地获取 label_size，如果不存在则默认为 12.0
            initial_label_size = getattr(self.vertex, 'label_size', 12.0) 
            self.label_fontsize_layout, self.label_fontsize_input = self._create_spinbox_row(
                "标签字体大小:", initial_label_size, min_val=1.0, max_val=72.0, step=0.5
            )
            basic_layout.addLayout(self.label_fontsize_layout)

            # --- 标签字体家族 ---
            self.label_fontfamily_layout = QHBoxLayout()
            self.label_fontfamily_layout.addWidget(QLabel("标签字体家族:"))
            self.label_fontfamily_combo = QFontComboBox()
            # 使用 getattr 安全地获取 label_fontfamily，如果不存在则默认为 None
            initial_fontfamily = getattr(self.vertex, 'label_fontfamily', None)
            if initial_fontfamily:
                index = self.label_fontfamily_combo.findText(initial_fontfamily)
                if index != -1:
                    self.label_fontfamily_combo.setCurrentIndex(index)
                else:
                    # 如果当前字体不在列表中，尝试设置为文本
                    self.label_fontfamily_combo.setEditText(initial_fontfamily)
            self.label_fontfamily_layout.addWidget(self.label_fontfamily_combo)
            basic_layout.addLayout(self.label_fontfamily_layout)

            # --- 标签字体粗细 ---
            self.label_fontweight_layout = QHBoxLayout()
            self.label_fontweight_layout.addWidget(QLabel("标签字体粗细:"))
            self.label_fontweight_combo = QComboBox()
            font_weights = ["normal", "bold", "light", "ultralight", "semibold", "heavy", "extra bold", "black"]
            self.label_fontweight_combo.addItems(font_weights)
            # 使用 getattr 安全地获取 label_fontweight，如果不存在则默认为 None
            initial_fontweight = getattr(self.vertex, 'label_fontweight', None)
            if initial_fontweight and initial_fontweight in font_weights:
                index = self.label_fontweight_combo.findText(initial_fontweight)
                if index != -1:
                    self.label_fontweight_combo.setCurrentIndex(index)
            self.label_fontweight_layout.addWidget(self.label_fontweight_combo)
            basic_layout.addLayout(self.label_fontweight_layout)

            # --- 标签字体样式 ---
            self.label_fontstyle_layout = QHBoxLayout()
            self.label_fontstyle_layout.addWidget(QLabel("标签字体样式:"))
            self.label_fontstyle_combo = QComboBox()
            font_styles = ["normal", "italic", "oblique"]
            self.label_fontstyle_combo.addItems(font_styles)
            # 使用 getattr 安全地获取 label_fontstyle，如果不存在则默认为 None
            initial_fontstyle = getattr(self.vertex, 'label_fontstyle', None)
            if initial_fontstyle and initial_fontstyle in font_styles:
                index = self.label_fontstyle_combo.findText(initial_fontstyle)
                if index != -1:
                    self.label_fontstyle_combo.setCurrentIndex(index)
            self.label_fontstyle_layout.addWidget(self.label_fontstyle_combo)
            basic_layout.addLayout(self.label_fontstyle_layout)


            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("类型:"))
            self.type_combo = QComboBox()
            for v_type in VertexType:
                self.type_combo.addItem(v_type.name.replace('_', ' ').title(), v_type)
            current_type_name_formatted = self.vertex.vertex_type.name.replace('_', ' ').title()
            index = self.type_combo.findText(current_type_name_formatted)
            if index != -1:
                self.type_combo.setCurrentIndex(index)
            type_layout.addWidget(self.type_combo)
            basic_layout.addLayout(type_layout)

            self.coupling_layout, self.coupling_input = self._create_spinbox_row("耦合常数:", self.vertex.coupling_constant, min_val=0.0, max_val=100.0, step=0.1)
            basic_layout.addLayout(self.coupling_layout)

            self.symmetry_layout, self.symmetry_input = self._create_spinbox_row("对称因子:", self.vertex.symmetry_factor, is_int=True, min_val=1, max_val=100)
            basic_layout.addLayout(self.symmetry_layout)

            label_offset_x = self.vertex.label_offset[0] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 0 else 0.0
            label_offset_y = self.vertex.label_offset[1] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 1 else 0.0
            self.label_offset_x_layout, self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
            self.label_offset_y_layout, self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
            basic_layout.addLayout(self.label_offset_x_layout)
            basic_layout.addLayout(self.label_offset_y_layout) # 修正了这里的bug：之前写成了label_offset_y_input_layout

            # --- 结构化顶点参数 ---
            structured_group = QGroupBox("结构化顶点")
            structured_layout = QVBoxLayout(structured_group)
            self.layout.addWidget(structured_group)

            self.is_structured_checkbox = QCheckBox("结构化顶点")
            self.is_structured_checkbox.setChecked(self.vertex.is_structured)
            structured_layout.addWidget(self.is_structured_checkbox)

            self.structured_radius_layout, self.structured_radius_input = self._create_spinbox_row("半径:", self.vertex.structured_radius, min_val=0.1, max_val=5.0, step=0.1)
            structured_layout.addLayout(self.structured_radius_layout)

            self.structured_facecolor_btn = QPushButton("填充颜色")
            self._structured_facecolor_picked_color = self.vertex.structured_facecolor # 从 Vertex 获取初始值
            self.structured_facecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_facecolor_btn, '_structured_facecolor_picked_color'))
            structured_layout.addWidget(self.structured_facecolor_btn)
            self._set_button_color(self.structured_facecolor_btn, self._structured_facecolor_picked_color)

            self.structured_edgecolor_btn = QPushButton("边框颜色")
            self._structured_edgecolor_picked_color = self.vertex.structured_edgecolor # 从 Vertex 获取初始值
            self.structured_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_edgecolor_btn, '_structured_edgecolor_picked_color'))
            structured_layout.addWidget(self.structured_edgecolor_btn)
            self._set_button_color(self.structured_edgecolor_btn, self._structured_edgecolor_picked_color)

            self.structured_linewidth_layout, self.structured_linewidth_input = self._create_spinbox_row("线宽:", self.vertex.structured_linewidth, min_val=0.1, max_val=5.0, step=0.1)
            structured_layout.addLayout(self.structured_linewidth_layout)

            self.structured_alpha_layout, self.structured_alpha_input = self._create_spinbox_row("透明度:", self.vertex.structured_alpha, min_val=0.0, max_val=1.0, step=0.01)
            structured_layout.addLayout(self.structured_alpha_layout)

            # Hatching (阴影线) 参数
            hatch_group = QGroupBox("阴影线 (Hatching)")
            hatch_layout = QVBoxLayout(hatch_group)
            self.layout.addWidget(hatch_group)

            self.use_custom_hatch_checkbox = QCheckBox("使用自定义阴影线")
            self.use_custom_hatch_checkbox.setChecked(self.vertex.use_custom_hatch)
            hatch_layout.addWidget(self.use_custom_hatch_checkbox)

            hatch_pattern_layout = QHBoxLayout()
            hatch_pattern_layout.addWidget(QLabel("图案:"))
            self.hatch_pattern_input = QLineEdit(self.vertex.hatch_pattern if self.vertex.hatch_pattern is not None else "")
            hatch_pattern_layout.addWidget(self.hatch_pattern_input)
            hatch_layout.addLayout(hatch_pattern_layout)

            # 自定义阴影线参数
            self.custom_hatch_color_btn = QPushButton("自定义阴影线颜色")
            self._custom_hatch_line_color_picked_color = self.vertex.custom_hatch_line_color # 从 Vertex 获取初始值
            self.custom_hatch_color_btn.clicked.connect(lambda: self._pick_color(self.custom_hatch_color_btn, '_custom_hatch_line_color_picked_color'))
            hatch_layout.addWidget(self.custom_hatch_color_btn)
            self._set_button_color(self.custom_hatch_color_btn, self._custom_hatch_line_color_picked_color)

            self.custom_hatch_linewidth_layout, self.custom_hatch_linewidth_input = self._create_spinbox_row("自定义线宽:", self.vertex.custom_hatch_line_width, min_val=0.1, max_val=5.0, step=0.1)
            hatch_layout.addLayout(self.custom_hatch_linewidth_layout)

            self.custom_hatch_angle_layout, self.custom_hatch_angle_input = self._create_spinbox_row("自定义角度(度):", self.vertex.custom_hatch_line_angle_deg, min_val=0.0, max_val=360.0, step=1.0)
            hatch_layout.addLayout(self.custom_hatch_angle_layout)

            self.custom_hatch_spacing_layout, self.custom_hatch_spacing_input = self._create_spinbox_row("自定义间距比例:", self.vertex.custom_hatch_spacing_ratio, min_val=0.01, max_val=1.0, step=0.01)
            hatch_layout.addLayout(self.custom_hatch_spacing_layout)

            # OK/Cancel buttons
            button_layout = QHBoxLayout()
            ok_button = QPushButton("确定")
            ok_button.clicked.connect(self.accept)
            cancel_button = QPushButton("取消")
            cancel_button.clicked.connect(self.reject)
            button_layout.addStretch(1)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            self.layout.addLayout(button_layout)

        def _create_spinbox_row(self, label_text, initial_value, min_val=-999.0, max_val=999.0, step=1.0, is_int=False):
            """Helper to create a label and spinbox in a horizontal layout, returning both layout and spinbox."""
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label_text))
            if is_int:
                spinbox = QSpinBox()
                spinbox.setRange(int(min_val), int(max_val))
                spinbox.setSingleStep(int(step))
                spinbox.setValue(int(initial_value))
            else:
                spinbox = QDoubleSpinBox()
                spinbox.setRange(min_val, max_val)
                spinbox.setSingleStep(step)
                spinbox.setValue(initial_value)
                spinbox.setDecimals(2)
            h_layout.addWidget(spinbox)
            return h_layout, spinbox

        def _pick_color(self, button, temp_attr_name):
            """Opens a color dialog, sets the button's background color, and stores the selected color in a temporary attribute."""
            # 从对话框实例的临时属性中获取初始颜色。
            initial_color_str = getattr(self, temp_attr_name)
            initial_qcolor = QColor(initial_color_str)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                hex_color = color.name()
                self._set_button_color(button, hex_color)
                setattr(self, temp_attr_name, hex_color) # 将选中的颜色存入对应的临时属性

        def _set_button_color(self, button, color_str):
            """Helper to set a button's background color."""
            palette = button.palette()
            palette.setColor(QPalette.Button, QColor(color_str))
            button.setPalette(palette)
            button.setAutoFillBackground(True)
            button.setText(f"{button.text().split('(')[0].strip()} ({color_str})")

        def accept(self):
            """当点击 OK 按钮时调用。更新传入的 Vertex 对象的属性。"""
            self.vertex.x = self.x_input.value()
            self.vertex.y = self.y_input.value()
            self.vertex.label = self.label_input.text()
            
            # --- 安全地更新标签字体大小等属性 ---
            # 只有当 Vertex 对象有这些属性时才尝试更新
            if hasattr(self.vertex, 'label_size'):
                self.vertex.label_size = self.label_fontsize_input.value()
            if hasattr(self.vertex, 'label_fontfamily'):
                # 只有当 QFontComboBox 有选中的文本时才更新字体家族
                self.vertex.label_fontfamily = self.label_fontfamily_combo.currentFont().family() if self.label_fontfamily_combo.currentText() else None
            if hasattr(self.vertex, 'label_fontweight'):
                self.vertex.label_fontweight = self.label_fontweight_combo.currentText() if self.label_fontweight_combo.currentText() else None
            if hasattr(self.vertex, 'label_fontstyle'):
                self.vertex.label_fontstyle = self.label_fontstyle_combo.currentText() if self.label_fontstyle_combo.currentText() else None
            # --- 安全更新结束 ---

            self.vertex.vertex_type = self.type_combo.currentData()
            self.vertex.coupling_constant = self.coupling_input.value()
            self.vertex.symmetry_factor = self.symmetry_input.value()
            
            self.vertex.label_offset = np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()])

            # 结构化顶点参数：直接从对话框的临时属性中读取并更新 Vertex 对象的属性
            self.vertex.is_structured = self.is_structured_checkbox.isChecked()
            self.vertex.structured_radius = self.structured_radius_input.value()
            self.vertex.structured_facecolor = self._structured_facecolor_picked_color # 从对话框临时属性赋值给 Vertex 属性
            self.vertex.structured_edgecolor = self._structured_edgecolor_picked_color # 从对话框临时属性赋值给 Vertex 属性
            self.vertex.structured_linewidth = self.structured_linewidth_input.value()
            self.vertex.structured_alpha = self.structured_alpha_input.value()

            # Hatching 参数：直接更新 Vertex 对象的属性
            self.vertex.use_custom_hatch = self.use_custom_hatch_checkbox.isChecked()
            hatch_pattern_text = self.hatch_pattern_input.text()
            self.vertex.hatch_pattern = hatch_pattern_text if hatch_pattern_text else None
            self.vertex.custom_hatch_line_color = self._custom_hatch_line_color_picked_color # 从对话框临时属性赋值给 Vertex 属性
            self.vertex.custom_hatch_line_width = self.custom_hatch_linewidth_input.value()
            self.vertex.custom_hatch_line_angle_deg = self.custom_hatch_angle_input.value()
            self.vertex.custom_hatch_spacing_ratio = self.custom_hatch_spacing_input.value()
            
            super().accept()

    dialog = _InternalEditVertexDialog(vertex, parent_dialog=parent_widget)
    
    if dialog.exec() == QDialog.Accepted:
        if diagram_model:
            associated_line_ids = diagram_model.get_associated_line_ids(vertex.id)
            
            for line_id in associated_line_ids:
                line = diagram_model.get_line_by_id(line_id)
                if line:
                    v_start_updated = line.v_start
                    v_end_updated = line.v_end
                    
                    if v_start_updated and v_end_updated:
                        line.set_angles(v_start_updated, v_end_updated)

        QMessageBox.information(parent_widget, "编辑成功", f"顶点 {vertex.id} 属性已更新，关联线条角度已调整。")
        return True
    else:
        QMessageBox.information(parent_widget, "编辑取消", f"顶点 {vertex.id} 属性编辑已取消。")
        return False