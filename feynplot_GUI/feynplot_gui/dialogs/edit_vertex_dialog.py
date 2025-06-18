# /feynplot_GUI/feynplot_gui/widgets/edit_vertex_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog, QCheckBox, QGroupBox, QSpinBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from feynplot.core.vertex import Vertex, VertexType
import numpy as np # 用于处理 label_offset

class EditVertexDialog(QDialog):
    def __init__(self, vertex: Vertex, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"编辑顶点: {vertex.label} (ID: {vertex.id})")
        self.setGeometry(200, 200, 400, 600) # 适当调整对话框大小
        
        self.vertex = vertex
        self.original_vertex_id = vertex.id # 记录原始ID，ID通常不允许修改

        self.layout = QVBoxLayout(self)

        # --- 基本属性 ---
        basic_group = QGroupBox("基本属性")
        basic_layout = QVBoxLayout(basic_group)
        self.layout.addWidget(basic_group)

        # X, Y 坐标
        self.x_input = self._create_spinbox_row("X 坐标:", self.vertex.x)
        self.y_input = self._create_spinbox_row("Y 坐标:", self.vertex.y)
        basic_layout.addLayout(self.x_input)
        basic_layout.addLayout(self.y_input)

        # Label
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("标签:"))
        self.label_input = QLineEdit(self.vertex.label)
        label_layout.addWidget(self.label_input)
        basic_layout.addLayout(label_layout)

        # Vertex Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        for v_type in VertexType:
            self.type_combo.addItem(v_type.name.replace('_', ' ').title(), v_type)
        self.type_combo.setCurrentText(self.vertex.vertex_type.name.replace('_', ' ').title())
        type_layout.addWidget(self.type_combo)
        basic_layout.addLayout(type_layout)

        # Coupling Constant
        self.coupling_input = self._create_spinbox_row("耦合常数:", self.vertex.coupling_constant, min_val=0.0, max_val=100.0, step=0.1)
        basic_layout.addLayout(self.coupling_input)

        # Symmetry Factor
        self.symmetry_input = self._create_spinbox_row("对称因子:", self.vertex.symmetry_factor, is_int=True, min_val=1, max_val=100)
        basic_layout.addLayout(self.symmetry_input)

        # Label Offset
        label_offset_x = self.vertex.label_offset[0] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 0 else 0.0
        label_offset_y = self.vertex.label_offset[1] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 1 else 0.0
        self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
        self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
        basic_layout.addLayout(self.label_offset_x_input)
        basic_layout.addLayout(self.label_offset_y_input)

        # --- 结构化顶点参数 ---
        structured_group = QGroupBox("结构化顶点")
        structured_layout = QVBoxLayout(structured_group)
        self.layout.addWidget(structured_group)

        self.is_structured_checkbox = QCheckBox("是结构化顶点")
        self.is_structured_checkbox.setChecked(self.vertex.is_structured)
        structured_layout.addWidget(self.is_structured_checkbox)

        self.structured_radius_input = self._create_spinbox_row("半径:", self.vertex.structured_radius, min_val=0.1, max_val=5.0, step=0.1)
        structured_layout.addLayout(self.structured_radius_input)

        self.structured_facecolor_btn = QPushButton("填充颜色")
        self.structured_facecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_facecolor_btn, 'structured_facecolor'))
        structured_layout.addWidget(self.structured_facecolor_btn)
        self._set_button_color(self.structured_facecolor_btn, self.vertex.structured_facecolor)

        self.structured_edgecolor_btn = QPushButton("边框颜色")
        self.structured_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_edgecolor_btn, 'structured_edgecolor'))
        structured_layout.addWidget(self.structured_edgecolor_btn)
        self._set_button_color(self.structured_edgecolor_btn, self.vertex.structured_edgecolor)

        self.structured_linewidth_input = self._create_spinbox_row("线宽:", self.vertex.structured_linewidth, min_val=0.1, max_val=5.0, step=0.1)
        structured_layout.addLayout(self.structured_linewidth_input)

        self.structured_alpha_input = self._create_spinbox_row("透明度:", self.vertex.structured_alpha, min_val=0.0, max_val=1.0, step=0.01)
        structured_layout.addLayout(self.structured_alpha_input)

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
        self.custom_hatch_color_btn.clicked.connect(lambda: self._pick_color(self.custom_hatch_color_btn, 'custom_hatch_line_color'))
        hatch_layout.addWidget(self.custom_hatch_color_btn)
        self._set_button_color(self.custom_hatch_color_btn, self.vertex.custom_hatch_line_color)

        self.custom_hatch_linewidth_input = self._create_spinbox_row("自定义线宽:", self.vertex.custom_hatch_line_width, min_val=0.1, max_val=5.0, step=0.1)
        hatch_layout.addLayout(self.custom_hatch_linewidth_input)

        self.custom_hatch_angle_input = self._create_spinbox_row("自定义角度(度):", self.vertex.custom_hatch_line_angle_deg, min_val=0.0, max_val=360.0, step=1.0)
        hatch_layout.addLayout(self.custom_hatch_angle_input)

        self.custom_hatch_spacing_input = self._create_spinbox_row("自定义间距比例:", self.vertex.custom_hatch_spacing_ratio, min_val=0.01, max_val=1.0, step=0.01)
        hatch_layout.addLayout(self.custom_hatch_spacing_input)

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
        """Helper to create a label and spinbox in a horizontal layout."""
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
            spinbox.setDecimals(2) # For floats, show 2 decimal places by default
        h_layout.addWidget(spinbox)
        return h_layout, spinbox # Return both layout and spinbox

    def _pick_color(self, button, color_attr_name):
        """Opens a color dialog and sets the button's background color."""
        initial_color_str = getattr(self.vertex, color_attr_name)
        initial_qcolor = QColor(initial_color_str)
        color = QColorDialog.getColor(initial_qcolor, self)
        if color.isValid():
            self._set_button_color(button, color.name()) # Store hex string
            setattr(self, f"_{color_attr_name}_picked_color", color.name()) # Store in temp var for retrieval

    def _set_button_color(self, button, color_str):
        """Helper to set a button's background color."""
        palette = button.palette()
        palette.setColor(QPalette.Button, QColor(color_str))
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        button.setText(f"{button.text().split('(')[0].strip()} ({color_str})") # Update button text with color

    def get_vertex_data(self):
        """Returns a dictionary of updated vertex properties."""
        updated_data = {
            'x': self.x_input[1].value(),
            'y': self.y_input[1].value(),
            'label': self.label_input.text(),
            'vertex_type': self.type_combo.currentData(), # Returns VertexType enum
            'coupling_constant': self.coupling_input[1].value(),
            'symmetry_factor': self.symmetry_input[1].value(),
            'label_offset': np.array([self.label_offset_x_input[1].value(), self.label_offset_y_input[1].value()]),
            'is_structured': self.is_structured_checkbox.isChecked(),
            'structured_radius': self.structured_radius_input[1].value(),
            'structured_facecolor': getattr(self, '_structured_facecolor_picked_color', self.vertex.structured_facecolor),
            'structured_edgecolor': getattr(self, '_structured_edgecolor_picked_color', self.vertex.structured_edgecolor),
            'structured_linewidth': self.structured_linewidth_input[1].value(),
            'structured_alpha': self.structured_alpha_input[1].value(),
            'use_custom_hatch': self.use_custom_hatch_checkbox.isChecked(),
            'hatch_pattern': self.hatch_pattern_input.text() if self.hatch_pattern_input.text() else None,
            'custom_hatch_line_color': getattr(self, '_custom_hatch_line_color_picked_color', self.vertex.custom_hatch_line_color),
            'custom_hatch_line_width': self.custom_hatch_linewidth_input[1].value(),
            'custom_hatch_line_angle_deg': self.custom_hatch_angle_input[1].value(),
            'custom_hatch_spacing_ratio': self.custom_hatch_spacing_input[1].value(),
        }
        return updated_data