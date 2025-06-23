# feynplot_GUI/feynplot_gui/controllers/vertex_dialogs/edit_vertex.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog, QCheckBox, QGroupBox, QSpinBox,
    QMessageBox
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from feynplot.core.vertex import Vertex, VertexType
import numpy as np
import matplotlib.pyplot as plt # 导入 matplotlib 以访问 rcParams

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
            self.setGeometry(200, 200, 400, 650) # 适当调整窗口大小以容纳更多控件
            self.setMaximumHeight(800) # 设置对话框的最大高度为 800 像素
            
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

            # --- 顶点颜色 (新增) ---
            self.vertex_color_btn = QPushButton("顶点颜色")
            # 从 Vertex 获取初始值，如果没有则使用默认蓝色
            self._vertex_picked_color = getattr(self.vertex, 'color', 'blue') 
            self.vertex_color_btn.clicked.connect(lambda: self._pick_color(self.vertex_color_btn, '_vertex_picked_color'))
            basic_layout.addWidget(self.vertex_color_btn)
            self._set_button_color(self.vertex_color_btn, self._vertex_picked_color)

            # --- 顶点尺寸 (新增) ---
            initial_vertex_size = getattr(self.vertex, 'size', 100.0)
            self.vertex_size_layout, self.vertex_size_input = self._create_spinbox_row(
                "顶点尺寸 (size):", initial_vertex_size, min_val=1.0, max_val=1000.0, step=1.0, is_int=True # size通常是整数
            )
            basic_layout.addLayout(self.vertex_size_layout)

            # --- 顶点标记 (marker) (新增) ---
            marker_layout = QHBoxLayout()
            marker_layout.addWidget(QLabel("顶点标记 (marker):"))
            self.marker_input = QLineEdit(getattr(self.vertex, 'marker', 'o')) # 默认'o'
            self.marker_input.setToolTip("支持的标记有: 'o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd', '|', '_'")
            marker_layout.addWidget(self.marker_input)
            basic_layout.addLayout(marker_layout)

            # --- 顶点透明度 (alpha) (新增) ---
            initial_vertex_alpha = getattr(self.vertex, 'alpha', 1.0)
            self.vertex_alpha_layout, self.vertex_alpha_input = self._create_spinbox_row(
                "顶点透明度 (alpha):", initial_vertex_alpha, min_val=0.0, max_val=1.0, step=0.01
            )
            basic_layout.addLayout(self.vertex_alpha_layout)

            # --- 顶点边框颜色 (edgecolor) (新增) ---
            self.vertex_edgecolor_btn = QPushButton("顶点边框颜色")
            # 从 Vertex 获取初始值，如果没有则使用默认黑色
            self._vertex_edgecolor_picked_color = getattr(self.vertex, 'edgecolor', '#000000') 
            self.vertex_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.vertex_edgecolor_btn, '_vertex_edgecolor_picked_color'))
            basic_layout.addWidget(self.vertex_edgecolor_btn)
            self._set_button_color(self.vertex_edgecolor_btn, self._vertex_edgecolor_picked_color)

            # --- 顶点线宽 (linewidth) (新增) ---
            initial_vertex_linewidth = getattr(self.vertex, 'linewidth', 1.0)
            self.vertex_linewidth_layout, self.vertex_linewidth_input = self._create_spinbox_row(
                "顶点线宽 (linewidth):", initial_vertex_linewidth, min_val=0.0, max_val=5.0, step=0.1
            )
            basic_layout.addLayout(self.vertex_linewidth_layout)

            # --- 顶点 Z 轴顺序 (zorder) (只读，新增) ---
            zorder_layout = QHBoxLayout()
            zorder_layout.addWidget(QLabel("顶点 Z 轴顺序 (zorder):"))
            # zorder通常由Feynplot内部管理，这里只做显示
            self.zorder_display = QLabel(str(getattr(self.vertex, 'zorder', 2))) 
            zorder_layout.addWidget(self.zorder_display)
            basic_layout.addLayout(zorder_layout)


            # --- 标签字体大小 (可编辑) ---
            initial_label_size = getattr(self.vertex, 'label_size', 12.0) 
            self.label_fontsize_layout, self.label_fontsize_input = self._create_spinbox_row(
                "标签字体大小:", initial_label_size, min_val=1.0, max_val=72.0, step=0.5
            )
            basic_layout.addLayout(self.label_fontsize_layout)

            # --- 全局字体设置 (只读，从 rcParams 获取) ---
            font_settings_group = QGroupBox("全局字体设置 (Matplotlib rcParams)")
            font_settings_layout = QVBoxLayout(font_settings_group)
            self.layout.addWidget(font_settings_group)

            # 字体家族
            font_family_layout = QHBoxLayout()
            font_family_layout.addWidget(QLabel("字体家族:"))
            current_font_family = plt.rcParams.get("font.family", ["sans-serif"])
            if isinstance(current_font_family, list) and current_font_family:
                current_font_family = current_font_family[0]
            else:
                current_font_family = str(current_font_family)
            self.label_fontfamily_display = QLabel(current_font_family)
            font_family_layout.addWidget(self.label_fontfamily_display)
            font_settings_layout.addLayout(font_family_layout)

            # 字体粗细
            font_weight_layout = QHBoxLayout()
            font_weight_layout.addWidget(QLabel("字体粗细:"))
            current_font_weight = plt.rcParams.get("font.weight", "normal")
            self.label_fontweight_display = QLabel(str(current_font_weight))
            font_weight_layout.addWidget(self.label_fontweight_display)
            font_settings_layout.addLayout(font_weight_layout)

            # 字体样式
            font_style_layout = QHBoxLayout()
            font_style_layout.addWidget(QLabel("字体样式:"))
            current_font_style = plt.rcParams.get("font.style", "normal")
            self.label_fontstyle_display = QLabel(str(current_font_style))
            font_style_layout.addWidget(self.label_fontstyle_display)
            font_settings_layout.addLayout(font_style_layout)

            # Mathtext 斜体字体
            mathtext_it_layout = QHBoxLayout()
            mathtext_it_layout.addWidget(QLabel("数学文本斜体字体 (mathtext.it):"))
            current_mathtext_it = plt.rcParams.get("mathtext.it", "serif:italic")
            self.mathtext_it_display = QLabel(str(current_mathtext_it))
            mathtext_it_layout.addWidget(self.mathtext_it_display)
            font_settings_layout.addLayout(mathtext_it_layout)

            # Mathtext 粗体字体
            mathtext_bf_layout = QHBoxLayout()
            mathtext_bf_layout.addWidget(QLabel("数学文本粗体字体 (mathtext.bf):"))
            current_mathtext_bf = plt.rcParams.get("mathtext.bf", "serif:bold")
            self.mathtext_bf_display = QLabel(str(current_mathtext_bf))
            mathtext_bf_layout.addWidget(self.mathtext_bf_display)
            font_settings_layout.addLayout(mathtext_bf_layout)
            # 全局字体设置部分结束

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
            basic_layout.addLayout(self.label_offset_y_layout)

            # --- 结构化顶点参数 ---
            self.structured_group = QGroupBox("结构化顶点")
            self.structured_layout = QVBoxLayout(self.structured_group)
            self.layout.addWidget(self.structured_group)

            self.is_structured_checkbox = QCheckBox("结构化顶点")
            self.is_structured_checkbox.setChecked(self.vertex.is_structured)
            # 连接信号槽，控制结构化顶点设置的显示/隐藏
            self.is_structured_checkbox.toggled.connect(self._toggle_structured_visibility)
            self.structured_layout.addWidget(self.is_structured_checkbox)

            # Safeguard numerical properties that might be None
            initial_structured_radius = self.vertex.structured_radius if self.vertex.structured_radius is not None else 0.5 # Default radius
            self.structured_radius_layout, self.structured_radius_input = self._create_spinbox_row("半径:", initial_structured_radius, min_val=0.1, max_val=5.0, step=0.1)
            self.structured_layout.addLayout(self.structured_radius_layout)

            self.structured_facecolor_btn = QPushButton("填充颜色")
            self._structured_facecolor_picked_color = self.vertex.structured_facecolor if self.vertex.structured_facecolor is not None else '#FFFFFF' # Default color
            self.structured_facecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_facecolor_btn, '_structured_facecolor_picked_color'))
            self.structured_layout.addWidget(self.structured_facecolor_btn)
            self._set_button_color(self.structured_facecolor_btn, self._structured_facecolor_picked_color)

            self.structured_edgecolor_btn = QPushButton("边框颜色")
            self._structured_edgecolor_picked_color = self.vertex.structured_edgecolor if self.vertex.structured_edgecolor is not None else '#000000' # Default color
            self.structured_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_edgecolor_btn, '_structured_edgecolor_picked_color'))
            self.structured_layout.addWidget(self.structured_edgecolor_btn)
            self._set_button_color(self.structured_edgecolor_btn, self._structured_edgecolor_picked_color)

            initial_structured_linewidth = self.vertex.structured_linewidth if self.vertex.structured_linewidth is not None else 1.0 # Default linewidth
            self.structured_linewidth_layout, self.structured_linewidth_input = self._create_spinbox_row("线宽:", initial_structured_linewidth, min_val=0.1, max_val=5.0, step=0.1)
            self.structured_layout.addLayout(self.structured_linewidth_layout)

            initial_structured_alpha = self.vertex.structured_alpha if self.vertex.structured_alpha is not None else 1.0 # Default alpha
            self.structured_alpha_layout, self.structured_alpha_input = self._create_spinbox_row("透明度:", initial_structured_alpha, min_val=0.0, max_val=1.0, step=0.01)
            self.structured_layout.addLayout(self.structured_alpha_layout)

            # Hatching (阴影线) 参数
            self.hatch_group = QGroupBox("阴影线 (Hatching)")
            self.hatch_layout = QVBoxLayout(self.hatch_group)
            self.layout.addWidget(self.hatch_group)

            self.use_custom_hatch_checkbox = QCheckBox("使用自定义阴影线")
            self.use_custom_hatch_checkbox.setChecked(self.vertex.use_custom_hatch)
            self.hatch_layout.addWidget(self.use_custom_hatch_checkbox)

            hatch_pattern_layout = QHBoxLayout()
            hatch_pattern_layout.addWidget(QLabel("图案:"))
            self.hatch_pattern_input = QLineEdit(self.vertex.hatch_pattern if self.vertex.hatch_pattern is not None else "")
            hatch_pattern_layout.addWidget(self.hatch_pattern_input)
            self.hatch_layout.addLayout(hatch_pattern_layout)

            # 自定义阴影线参数
            self.custom_hatch_color_btn = QPushButton("自定义阴影线颜色")
            self._custom_hatch_line_color_picked_color = self.vertex.custom_hatch_line_color if self.vertex.custom_hatch_line_color is not None else '#000000' # Default color
            self.custom_hatch_color_btn.clicked.connect(lambda: self._pick_color(self.custom_hatch_color_btn, '_custom_hatch_line_color_picked_color'))
            self.hatch_layout.addWidget(self.custom_hatch_color_btn)
            self._set_button_color(self.custom_hatch_color_btn, self._custom_hatch_line_color_picked_color)

            initial_custom_hatch_linewidth = self.vertex.custom_hatch_line_width if self.vertex.custom_hatch_line_width is not None else 1.0 # Default linewidth
            self.custom_hatch_linewidth_layout, self.custom_hatch_linewidth_input = self._create_spinbox_row("自定义线宽:", initial_custom_hatch_linewidth, min_val=0.1, max_val=5.0, step=0.1)
            self.hatch_layout.addLayout(self.custom_hatch_linewidth_layout)

            initial_custom_hatch_angle_deg = self.vertex.custom_hatch_line_angle_deg if self.vertex.custom_hatch_line_angle_deg is not None else 45.0 # Default angle
            self.custom_hatch_angle_layout, self.custom_hatch_angle_input = self._create_spinbox_row("自定义角度(度):", initial_custom_hatch_angle_deg, min_val=0.0, max_val=360.0, step=1.0)
            self.hatch_layout.addLayout(self.custom_hatch_angle_layout)

            initial_custom_hatch_spacing_ratio = self.vertex.custom_hatch_spacing_ratio if self.vertex.custom_hatch_spacing_ratio is not None else 0.1 # Default spacing
            self.custom_hatch_spacing_layout, self.custom_hatch_spacing_input = self._create_spinbox_row("自定义间距比例:", initial_custom_hatch_spacing_ratio, min_val=0.01, max_val=1.0, step=0.01)
            self.hatch_layout.addLayout(self.custom_hatch_spacing_layout)

            # 初始化结构化顶点设置的可见性
            self._toggle_structured_visibility(self.is_structured_checkbox.isChecked())


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
            """辅助函数，用于在一个水平布局中创建标签和 QSpinBox/QDoubleSpinBox，并返回布局和 QSpinBox。"""
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
                spinbox.setValue(float(initial_value)) # Ensure float type for QDoubleSpinBox
                spinbox.setDecimals(2)
            h_layout.addWidget(spinbox)
            return h_layout, spinbox

        def _pick_color(self, button, temp_attr_name):
            """打开一个颜色对话框，设置按钮的背景颜色，并将选中的颜色存储在临时属性中。"""
            # 从对话框实例的临时属性中获取初始颜色。
            initial_color_str = getattr(self, temp_attr_name)
            initial_qcolor = QColor(initial_color_str)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                hex_color = color.name()
                self._set_button_color(button, hex_color)
                setattr(self, temp_attr_name, hex_color) # 将选中的颜色存入对应的临时属性

        def _set_button_color(self, button, color_str):
            """辅助函数，用于设置按钮的背景颜色。"""
            palette = button.palette()
            palette.setColor(QPalette.Button, QColor(color_str))
            button.setPalette(palette)
            button.setAutoFillBackground(True)
            button.setText(f"{button.text().split('(')[0].strip()} ({color_str})")

        def _toggle_structured_visibility(self, is_checked):
            """根据复选框的状态控制结构化顶点相关设置的可见性。"""
            for i in range(self.structured_layout.count()):
                item = self.structured_layout.itemAt(i)
                if item:
                    if item.widget() == self.is_structured_checkbox:
                        continue # Skip the checkbox itself
                    
                    if item.widget():
                        item.widget().setVisible(is_checked)
                    elif item.layout():
                        for j in range(item.layout().count()):
                            sub_item = item.layout().itemAt(j)
                            if sub_item.widget():
                                sub_item.widget().setVisible(is_checked)

            # 隐藏/显示阴影线组
            self.hatch_group.setVisible(is_checked)


        def accept(self):
            """当点击 OK 按钮时调用。更新传入的 Vertex 对象的属性。"""
            self.vertex.x = self.x_input.value()
            self.vertex.y = self.y_input.value()
            self.vertex.label = self.label_input.text()
            
            # 更新顶点颜色属性
            if hasattr(self.vertex, 'color'):
                self.vertex.color = self._vertex_picked_color

            # 更新新增的顶点属性
            if hasattr(self.vertex, 'size'):
                self.vertex.size = self.vertex_size_input.value()
            if hasattr(self.vertex, 'marker'):
                self.vertex.marker = self.marker_input.text()
            if hasattr(self.vertex, 'alpha'):
                self.vertex.alpha = self.vertex_alpha_input.value()
            if hasattr(self.vertex, 'edgecolor'):
                self.vertex.edgecolor = self._vertex_edgecolor_picked_color
            if hasattr(self.vertex, 'linewidth'):
                self.vertex.linewidth = self.vertex_linewidth_input.value()
            # zorder 是只读的，所以不需要在这里更新

            # --- 安全地更新标签字体大小属性 ---
            if hasattr(self.vertex, 'label_size'):
                self.vertex.label_size = self.label_fontsize_input.value()
            
            self.vertex.vertex_type = self.type_combo.currentData()
            self.vertex.coupling_constant = self.coupling_input.value()
            self.vertex.symmetry_factor = self.symmetry_input.value()
            
            self.vertex.label_offset = np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()])

            # 结构化顶点参数：直接从对话框的临时属性中读取并更新 Vertex 对象的属性
            self.vertex.is_structured = self.is_structured_checkbox.isChecked()
            # 只有在结构化顶点被勾选时才更新其具体属性
            if self.vertex.is_structured:
                self.vertex.structured_radius = self.structured_radius_input.value()
                self.vertex.structured_facecolor = self._structured_facecolor_picked_color
                self.vertex.structured_edgecolor = self._structured_edgecolor_picked_color
                self.vertex.structured_linewidth = self.structured_linewidth_input.value()
                self.vertex.structured_alpha = self.structured_alpha_input.value()
            else: # 如果未勾选，将这些属性重置为 None 或默认值（如果Vertex类有定义）
                self.vertex.structured_radius = None
                self.vertex.structured_facecolor = None
                self.vertex.structured_edgecolor = None
                self.vertex.structured_linewidth = None
                self.vertex.structured_alpha = None


            # Hatching 参数：直接更新 Vertex 对象的属性
            self.vertex.use_custom_hatch = self.use_custom_hatch_checkbox.isChecked()
            # 只有在使用自定义阴影线被勾选时才更新其具体属性
            if self.vertex.use_custom_hatch:
                hatch_pattern_text = self.hatch_pattern_input.text()
                self.vertex.hatch_pattern = hatch_pattern_text if hatch_pattern_text else None
                self.vertex.custom_hatch_line_color = self._custom_hatch_line_color_picked_color
                self.vertex.custom_hatch_line_width = self.custom_hatch_linewidth_input.value()
                self.vertex.custom_hatch_line_angle_deg = self.custom_hatch_angle_input.value()
                self.vertex.custom_hatch_spacing_ratio = self.custom_hatch_spacing_input.value()
            else: # 如果未勾选，将这些属性重置为 None 或默认值
                self.vertex.hatch_pattern = None
                self.vertex.custom_hatch_line_color = None
                self.vertex.custom_hatch_line_width = None
                self.vertex.custom_hatch_line_angle_deg = None
                self.vertex.custom_hatch_spacing_ratio = None
            
            super().accept()

    dialog = _InternalEditVertexDialog(vertex, parent_dialog=parent_widget)
    
    if dialog.exec() == QDialog.Accepted:
        if diagram_model:
            # 重新计算并设置关联线条的角度
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