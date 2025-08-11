# /feynplot_GUI/feynplot_gui/widgets/edit_line_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog, QCheckBox, QGroupBox, QSpinBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt # 导入 Qt.Orientation

from feynplot.core.line import Line, LineStyle
from feynplot.core.vertex import Vertex # 需要导入 Vertex 来处理 v_start/v_end 选择
import numpy as np
from typing import List, Dict, Any, Optional

class EditLineDialog(QDialog):
    def __init__(self, line: Line, all_vertices: List[Vertex], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"编辑线: {line.label} (ID: {line.id})")
        self.setGeometry(200, 200, 450, 700) # 适当调整大小

        self.line = line
        self.all_vertices = all_vertices # 用于选择起始/结束顶点

        self.layout = QVBoxLayout(self)

        # --- 基本属性 ---
        basic_group = QGroupBox(self.tr("基本属性"))
        basic_layout = QVBoxLayout(basic_group)
        self.layout.addWidget(basic_group)

        # Label
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel(self.tr("标签:")))
        self.label_input = QLineEdit(self.line.label)
        label_layout.addWidget(self.label_input)
        basic_layout.addLayout(label_layout)

        # Line Style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel(self.tr("样式:")))
        self.style_combo = QComboBox()
        for l_style in LineStyle:
            self.style_combo.addItem(l_style.name.replace('_', ' ').title(), l_style)
        self.style_combo.setCurrentText(self.line.style.name.replace('_', ' ').title())
        style_layout.addWidget(self.style_combo)
        basic_layout.addLayout(style_layout)

        # Start Vertex
        self.v_start_combo = self._create_vertex_combo("起始顶点:", self.line.v_start)
        basic_layout.addLayout(self.v_start_combo[0])

        # End Vertex
        self.v_end_combo = self._create_vertex_combo("结束顶点:", self.line.v_end)
        basic_layout.addLayout(self.v_end_combo[0])

        # Label Offset
        label_offset_x = self.line.label_offset[0] if self.line.label_offset is not None and len(self.line.label_offset) > 0 else 0.0
        label_offset_y = self.line.label_offset[1] if self.line.label_offset is not None and len(self.line.label_offset) > 1 else 0.0
        self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
        self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
        basic_layout.addLayout(self.label_offset_x_input)
        basic_layout.addLayout(self.label_offset_y_input)

        # Angles and Bezier Offset
        self.angle_in_input = self._create_spinbox_row("入口角度:", self.line.angleIn if self.line.angleIn is not None else 0.0, min_val=0.0, max_val=360.0, step=1.0)
        self.angle_out_input = self._create_spinbox_row("出口角度:", self.line.angleOut if self.line.angleOut is not None else 0.0, min_val=0.0, max_val=360.0, step=1.0)
        self.bezier_offset_input = self._create_spinbox_row("贝塞尔偏移:", self.line.bezier_offset, min_val=0.0, max_val=5.0, step=0.1)
        basic_layout.addLayout(self.angle_in_input)
        basic_layout.addLayout(self.angle_out_input)
        basic_layout.addLayout(self.bezier_offset_input)

        # Arrow (specific to FermionLine/AntiFermionLine)
        self.arrow_checkbox = None
        if hasattr(line, 'arrow'):
            arrow_layout = QHBoxLayout()
            self.arrow_checkbox = QCheckBox(self.tr("显示箭头"))
            self.arrow_checkbox.setChecked(line.arrow)
            arrow_layout.addWidget(self.arrow_checkbox)
            arrow_layout.addStretch(1)
            basic_layout.addLayout(arrow_layout)


        # --- 绘图配置 (linePlotConfig) ---
        line_plot_group = QGroupBox(self.tr("线条绘制配置"))
        line_plot_layout = QVBoxLayout(line_plot_group)
        self.layout.addWidget(line_plot_group)

        # Line Width
        self.linewidth_input = self._create_spinbox_row("线宽:", self.line.linePlotConfig().get('linewidth', 1.0), min_val=0.1, max_val=10.0, step=0.1)
        line_plot_layout.addLayout(self.linewidth_input)

        # Line Color
        self.line_color_btn = QPushButton(self.tr("线条颜色"))
        self.line_color_btn.clicked.connect(lambda: self._pick_color(self.line_color_btn, 'line_color_picked'))
        line_plot_layout.addWidget(self.line_color_btn)
        self._set_button_color(self.line_color_btn, self.line.linePlotConfig().get('color', 'black'))

        # Line Style (Matplotlib)
        line_style_mpl_layout = QHBoxLayout()
        line_style_mpl_layout.addWidget(QLabel(self.tr("线条样式(mpl):")))
        self.linestyle_input = QLineEdit(self.line.linePlotConfig().get('linestyle', 'solid')) # Default to solid
        line_style_mpl_layout.addWidget(self.linestyle_input)
        line_plot_layout.addLayout(line_style_mpl_layout)

        # Alpha
        self.alpha_input = self._create_spinbox_row("透明度:", self.line.linePlotConfig().get('alpha', 1.0), min_val=0.0, max_val=1.0, step=0.01)
        line_plot_layout.addLayout(self.alpha_input)

        # ZOrder
        self.zorder_input = self._create_spinbox_row("Z轴顺序:", self.line.linePlotConfig().get('zorder', 1), is_int=True, min_val=-100, max_val=100)
        line_plot_layout.addLayout(self.zorder_input)


        # --- 标签绘图配置 (labelPlotConfig) ---
        label_plot_group = QGroupBox(self.tr("标签绘制配置"))
        label_plot_layout = QVBoxLayout(label_plot_group)
        self.layout.addWidget(label_plot_group)

        # Font Size
        self.fontsize_input = self._create_spinbox_row("字体大小:", self.line.labelPlotConfig().get('fontsize', 10), is_int=True, min_val=5, max_val=72)
        label_plot_layout.addLayout(self.fontsize_input)

        # Label Color
        self.label_color_btn = QPushButton(self.tr("标签颜色"))
        self.label_color_btn.clicked.connect(lambda: self._pick_color(self.label_color_btn, 'label_color_picked'))
        label_plot_layout.addWidget(self.label_color_btn)
        self._set_button_color(self.label_color_btn, self.line.labelPlotConfig().get('color', 'black'))

        # Horizontal Alignment
        ha_layout = QHBoxLayout()
        ha_layout.addWidget(QLabel(self.tr("水平对齐:")))
        self.ha_combo = QComboBox()
        self.ha_combo.addItems(['left', 'center', 'right'])
        self.ha_combo.setCurrentText(self.line.labelPlotConfig().get('ha', 'center'))
        ha_layout.addWidget(self.ha_combo)
        label_plot_layout.addLayout(ha_layout)

        # Vertical Alignment
        va_layout = QHBoxLayout()
        va_layout.addWidget(QLabel(self.tr("垂直对齐:")))
        self.va_combo = QComboBox()
        self.va_combo.addItems(['top', 'center', 'bottom', 'baseline'])
        self.va_combo.setCurrentText(self.line.labelPlotConfig().get('va', 'center'))
        va_layout.addWidget(self.va_combo)
        label_plot_layout.addLayout(va_layout)


        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton(self.tr("确定"))
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton(self.tr("取消"))
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
            spinbox.setDecimals(2)
        h_layout.addWidget(spinbox)
        return h_layout, spinbox

    def _create_vertex_combo(self, label_text, current_vertex: Optional[Vertex]):
        """Helper to create a QComboBox for selecting vertices."""
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItem("None", None) # 允许不选择顶点
        for v in self.all_vertices:
            combo.addItem(f"[{v.id}] {v.label} ({v.x:.1f},{v.y:.1f})", v)
            if current_vertex is not None and v.id == current_vertex.id:
                combo.setCurrentIndex(combo.count() - 1) # Set to last added item if it's the current one
        h_layout.addWidget(combo)
        return h_layout, combo # Return both layout and combo

    def _pick_color(self, button, temp_attr_name):
        """Opens a color dialog and sets the button's background color."""
        # 从按钮的文本中提取当前颜色字符串，或从 linePlotConfig/labelPlotConfig 获取初始颜色
        current_color_str = button.text().split('(')[-1].strip(')') if '(' in button.text() else 'black'
        
        # 尝试从 line.linePlotConfig 或 line.labelPlotConfig 获取初始颜色
        if temp_attr_name == 'line_color_picked':
            initial_qcolor = QColor(self.line.linePlotConfig().get('color', 'black'))
        elif temp_attr_name == 'label_color_picked':
            initial_qcolor = QColor(self.line.labelPlotConfig().get('color', 'black'))
        else:
            initial_qcolor = QColor(current_color_str)

        color = QColorDialog.getColor(initial_qcolor, self)
        if color.isValid():
            self._set_button_color(button, color.name()) # Store hex string
            setattr(self, f"_{temp_attr_name}", color.name()) # Store in temp var for retrieval

    def _set_button_color(self, button, color_str):
        """Helper to set a button's background color."""
        palette = button.palette()
        palette.setColor(QPalette.Button, QColor(color_str))
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        button.setText(f"{button.text().split('(')[0].strip()} ({color_str})") # Update button text with color

    def get_line_data(self) -> Dict[str, Any]:
        """Returns a dictionary of updated line properties."""
        updated_data: Dict[str, Any] = {
            'label': self.label_input.text(),
            'style': self.style_combo.currentData(), # Returns LineStyle enum
            'v_start': self.v_start_combo[1].currentData(), # Returns Vertex object
            'v_end': self.v_end_combo[1].currentData(),     # Returns Vertex object
            'label_offset': np.array([self.label_offset_x_input[1].value(), self.label_offset_y_input[1].value()]),
            'angleIn': self.angle_in_input[1].value(),
            'angleOut': self.angle_out_input[1].value(),
            'bezier_offset': self.bezier_offset_input[1].value(),
        }

        # 添加箭头属性（如果存在）
        if self.arrow_checkbox and hasattr(self.line, 'arrow'):
            updated_data['arrow'] = self.arrow_checkbox.isChecked()

        # 更新 linePlotConfig 中的参数
        updated_data['linewidth'] = self.linewidth_input[1].value()
        updated_data['color'] = getattr(self, '_line_color_picked', self.line.linePlotConfig().get('color'))
        updated_data['linestyle'] = self.linestyle_input.text()
        updated_data['alpha'] = self.alpha_input[1].value()
        updated_data['zorder'] = self.zorder_input[1].value()

        # 更新 labelPlotConfig 中的参数
        updated_data['fontsize'] = self.fontsize_input[1].value()
        updated_data['label_color'] = getattr(self, '_label_color_picked', self.line.labelPlotConfig().get('color'))
        updated_data['ha'] = self.ha_combo.currentText()
        updated_data['va'] = self.va_combo.currentText()

        return updated_data