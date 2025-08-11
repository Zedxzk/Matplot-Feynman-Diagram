from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDoubleSpinBox, QComboBox, QColorDialog, QCheckBox, QGroupBox, QSpinBox,
    QMessageBox, QScrollArea, QWidget
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from feynplot.core.vertex import Vertex, VertexType
import numpy as np
import matplotlib.pyplot as plt

def open_edit_vertex_dialog(vertex: Vertex, diagram_model, parent_widget=None) -> bool:
    """
    Opens a dialog to edit the properties of a given Vertex object.
    This function now includes the complete implementation of EditVertexDialog.
    """
    if not isinstance(vertex, Vertex):
        QMessageBox.critical(parent_widget, "错误", "提供的对象不是一个有效的顶点。")
        return False

    class _InternalEditVertexDialog(QDialog):
        def __init__(self, vertex_obj: Vertex, parent_dialog=None):
            super().__init__(parent_dialog)
            self.setWindowTitle(f"编辑顶点: {vertex_obj.label} (ID: {vertex_obj.id})")
            # 初始窗口大小，并设置最大高度
            self.setGeometry(200, 200, 400, 650)
            self.setMaximumHeight(800)

            self.vertex = vertex_obj
            self.original_vertex_id = vertex_obj.id
            self._original_x = vertex_obj.x
            self._original_y = vertex_obj.y

            # --- 对话框的主布局 (承载滚动区域和按钮) ---
            self.main_dialog_layout = QVBoxLayout(self)

            # --- 创建一个 QWidget 来承载所有可滚动的内容 ---
            scroll_content_widget = QWidget()
            scroll_content_layout = QVBoxLayout(scroll_content_widget) # 这是所有 GroupBox 的父布局

            # --- Basic Properties ---
            basic_group = QGroupBox(self.tr("基本属性"))
            basic_layout = QVBoxLayout(basic_group)
            scroll_content_layout.addWidget(basic_group) # 添加到可滚动内容布局

            # --- 严格按照要求：隐藏顶点和隐藏标签选项放在最顶端且同一行 ---
            visibility_layout = QHBoxLayout()

            self.hide_vertex_checkbox = QCheckBox(self.tr("隐藏顶点"))
            # 修正：根据 self.vertex.hidden_vertex 属性设置初始状态
            self.hide_vertex_checkbox.setChecked(self.vertex.hidden_vertex)
            # 绑定信号槽
            self.hide_vertex_checkbox.toggled.connect(self._toggle_vertex_visibility)
            visibility_layout.addWidget(self.hide_vertex_checkbox)

            self.hide_label_checkbox = QCheckBox(self.tr("隐藏标签"))
            # 修正：根据 self.vertex.hidden_label 属性设置初始状态
            self.hide_label_checkbox.setChecked(self.vertex.hidden_label)
            # 绑定信号槽
            self.hide_label_checkbox.toggled.connect(self._toggle_label_visibility)
            visibility_layout.addWidget(self.hide_label_checkbox)
            
            # Add this visibility layout to the top of the basic_layout
            basic_layout.addLayout(visibility_layout) 

            # --- 以下是原有的基本属性布局，保持不变 ---
            self.x_layout, self.x_input = self._create_spinbox_row("X 坐标:", self.vertex.x)
            self.y_layout, self.y_input = self._create_spinbox_row("Y 坐标:", self.vertex.y)
            basic_layout.addLayout(self.x_layout)
            basic_layout.addLayout(self.y_layout)

            label_layout = QHBoxLayout()
            label_layout.addWidget(QLabel(self.tr("标签:")))
            self.label_input = QLineEdit(self.vertex.label)
            label_layout.addWidget(self.label_input)
            basic_layout.addLayout(label_layout)

            # --- Vertex Color ---
            self.vertex_color_btn = QPushButton(self.tr("顶点颜色"))
            self._vertex_picked_color = getattr(self.vertex, 'color', 'blue')
            self.vertex_color_btn.clicked.connect(lambda: self._pick_color(self.vertex_color_btn, '_vertex_picked_color'))
            basic_layout.addWidget(self.vertex_color_btn)
            self._set_button_color(self.vertex_color_btn, self._vertex_picked_color)

            # --- Vertex Size ---
            initial_vertex_size = getattr(self.vertex, 'size', 100.0)
            self.vertex_size_layout, self.vertex_size_input = self._create_spinbox_row(
                "顶点尺寸 (size):", initial_vertex_size, min_val=1.0, max_val=1000.0, step=1.0, is_int=True
            )
            basic_layout.addLayout(self.vertex_size_layout)

            # --- Vertex Marker ---
            marker_layout = QHBoxLayout()
            marker_layout.addWidget(QLabel(self.tr("顶点标记 (marker):")))
            self.marker_input = QLineEdit(getattr(self.vertex, 'marker', 'o'))
            self.marker_input.setToolTip(self.tr("支持的标记有: 'o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', 'D', 'd', '|', '_'"))
            marker_layout.addWidget(self.marker_input)
            basic_layout.addLayout(marker_layout)

            # --- Vertex Alpha ---
            initial_vertex_alpha = getattr(self.vertex, 'alpha', 1.0)
            self.vertex_alpha_layout, self.vertex_alpha_input = self._create_spinbox_row(
                "顶点透明度 (alpha):", initial_vertex_alpha, min_val=0.0, max_val=1.0, step=0.01
            )
            basic_layout.addLayout(self.vertex_alpha_layout)

            # --- Vertex Edgecolor ---
            self.vertex_edgecolor_btn = QPushButton(self.tr("顶点边框颜色"))
            self._vertex_edgecolor_picked_color = getattr(self.vertex, 'edgecolor', '#000000')
            self.vertex_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.vertex_edgecolor_btn, '_vertex_edgecolor_picked_color'))
            basic_layout.addWidget(self.vertex_edgecolor_btn)
            self._set_button_color(self.vertex_edgecolor_btn, self._vertex_edgecolor_picked_color)

            # --- Vertex Linewidth ---
            initial_vertex_linewidth = getattr(self.vertex, 'linewidth', 1.0)
            self.vertex_linewidth_layout, self.vertex_linewidth_input = self._create_spinbox_row(
                "顶点线宽 (linewidth):", initial_vertex_linewidth, min_val=0.0, max_val=5.0, step=0.1
            )
            basic_layout.addLayout(self.vertex_linewidth_layout)


            # --- 顶点和标签 Z 轴顺序 (并排在一行) ---
            zorder_layout, self.vertex_zorder_input, self.label_zorder_input = self._create_dual_spinbox_row(
                label1_text=self.tr("顶点 zorder:"),
                initial1_value=getattr(self.vertex, 'zorder', 2),
                label2_text=self.tr("标签 zorder:"),
                initial2_value=getattr(self.vertex, 'label_zorder', 3),
                is_int=True
            )

            # 连接各自的信号到相应的更新函数
            # self.vertex_zorder_spinbox.valueChanged.connect(self.update_vertex_zorder)
            # self.label_zorder_spinbox.valueChanged.connect(self.update_label_zorder)

            # 将整个布局添加到主布局中
            basic_layout.addLayout(zorder_layout)

            # 将整个水平布局添加到主布局中




            
            # --- Label Font Size ---
            initial_label_size = getattr(self.vertex, 'label_size', 12.0)
            self.label_fontsize_layout, self.label_fontsize_input = self._create_spinbox_row(
                "标签字体大小:", initial_label_size, min_val=1.0, max_val=72.0, step=0.5
            )
            basic_layout.addLayout(self.label_fontsize_layout)

            # --- Global Font Settings (Read-only from rcParams) ---
            font_settings_group = QGroupBox(self.tr("全局字体设置 (Matplotlib rcParams)"))
            font_settings_layout = QVBoxLayout(font_settings_group)
            scroll_content_layout.addWidget(font_settings_group) # 添加到可滚动内容布局

            font_family_layout = QHBoxLayout()
            font_family_layout.addWidget(QLabel(self.tr("字体家族:")))
            current_font_family = plt.rcParams.get("font.family", ["sans-serif"])
            if isinstance(current_font_family, list) and current_font_family:
                current_font_family = current_font_family[0]
            else:
                current_font_family = str(current_font_family)
            self.label_fontfamily_display = QLabel(current_font_family)
            font_family_layout.addWidget(self.label_fontfamily_display)
            font_settings_layout.addLayout(font_family_layout)

            font_weight_layout = QHBoxLayout()
            font_weight_layout.addWidget(QLabel(self.tr("字体粗细:")))
            current_font_weight = plt.rcParams.get("font.weight", "normal")
            self.label_fontweight_display = QLabel(str(current_font_weight))
            font_weight_layout.addWidget(self.label_fontweight_display)
            font_settings_layout.addLayout(font_weight_layout)

            font_style_layout = QHBoxLayout()
            font_style_layout.addWidget(QLabel(self.tr("字体样式:")))
            current_font_style = plt.rcParams.get("font.style", "normal")
            self.label_fontstyle_display = QLabel(str(current_font_style))
            font_style_layout.addWidget(self.label_fontstyle_display)
            font_settings_layout.addLayout(font_style_layout)

            mathtext_it_layout = QHBoxLayout()
            mathtext_it_layout.addWidget(QLabel(self.tr("数学文本斜体字体 (mathtext.it):")))
            current_mathtext_it = plt.rcParams.get("mathtext.it", "serif:italic")
            self.mathtext_it_display = QLabel(str(current_mathtext_it))
            mathtext_it_layout.addWidget(self.mathtext_it_display)
            font_settings_layout.addLayout(mathtext_it_layout)

            mathtext_bf_layout = QHBoxLayout()
            mathtext_bf_layout.addWidget(QLabel(self.tr("数学文本粗体字体 (mathtext.bf):")))
            current_mathtext_bf = plt.rcParams.get("mathtext.bf", "serif:bold")
            self.mathtext_bf_display = QLabel(str(current_mathtext_bf))
            mathtext_bf_layout.addWidget(self.mathtext_bf_display)
            font_settings_layout.addLayout(mathtext_bf_layout)

            type_layout = QHBoxLayout()
            # type_layout.addWidget(QLabel(self.tr("类型:")))
            # self.type_combo = QComboBox()
            # for v_type in VertexType:
            #     self.type_combo.addItem(v_type.name.replace('_', ' ').title(), v_type)
            # current_type_name_formatted = self.vertex.vertex_type.name.replace('_', ' ').title()
            # index = self.type_combo.findText(current_type_name_formatted)
            # if index != -1:
            #     self.type_combo.setCurrentIndex(index)
            # type_layout.addWidget(self.type_combo)
            # basic_layout.addLayout(type_layout)

            # self.coupling_layout, self.coupling_input = self._create_spinbox_row("耦合常数:", self.vertex.coupling_constant, min_val=0.0, max_val=100.0, step=0.1)
            # basic_layout.addLayout(self.coupling_layout)

            # self.symmetry_layout, self.symmetry_input = self._create_spinbox_row("对称因子:", self.vertex.symmetry_factor, is_int=True, min_val=1, max_val=100)
            # basic_layout.addLayout(self.symmetry_layout)

            label_offset_x = self.vertex.label_offset[0] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 0 else 0.0
            label_offset_y = self.vertex.label_offset[1] if self.vertex.label_offset is not None and len(self.vertex.label_offset) > 1 else 0.0
            self.label_offset_x_layout, self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
            self.label_offset_y_layout, self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
            basic_layout.addLayout(self.label_offset_x_layout)
            basic_layout.addLayout(self.label_offset_y_layout)

            # --- Structured Vertex Parameters ---
            self.structured_group = QGroupBox(self.tr("结构化顶点"))
            self.structured_layout = QVBoxLayout(self.structured_group)
            scroll_content_layout.addWidget(self.structured_group)

            self.is_structured_checkbox = QCheckBox(self.tr("结构化顶点"))
            self.is_structured_checkbox.setChecked(self.vertex.is_structured)
            self.is_structured_checkbox.toggled.connect(self._toggle_structured_visibility)
            self.structured_layout.addWidget(self.is_structured_checkbox)

            initial_structured_radius = self.vertex.structured_radius if self.vertex.structured_radius is not None else 0.5
            self.structured_radius_layout, self.structured_radius_input = self._create_spinbox_row("半径:", initial_structured_radius, min_val=0.1, max_val=5.0, step=0.1)
            self.structured_layout.addLayout(self.structured_radius_layout)

            self.structured_facecolor_btn = QPushButton(self.tr("填充颜色"))
            self._structured_facecolor_picked_color = self.vertex.structured_facecolor if self.vertex.structured_facecolor is not None else '#FFFFFF'
            self.structured_facecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_facecolor_btn, '_structured_facecolor_picked_color'))
            self.structured_layout.addWidget(self.structured_facecolor_btn)
            self._set_button_color(self.structured_facecolor_btn, self._structured_facecolor_picked_color)

            self.structured_edgecolor_btn = QPushButton(self.tr("边框颜色"))
            self._structured_edgecolor_picked_color = self.vertex.structured_edgecolor if self.vertex.structured_edgecolor is not None else '#000000'
            self.structured_edgecolor_btn.clicked.connect(lambda: self._pick_color(self.structured_edgecolor_btn, '_structured_edgecolor_picked_color'))
            self.structured_layout.addWidget(self.structured_edgecolor_btn)
            self._set_button_color(self.structured_edgecolor_btn, self._structured_edgecolor_picked_color)

            initial_structured_linewidth = self.vertex.structured_linewidth if self.vertex.structured_linewidth is not None else 1.0
            self.structured_linewidth_layout, self.structured_linewidth_input = self._create_spinbox_row("线宽:", initial_structured_linewidth, min_val=0.1, max_val=5.0, step=0.1)
            self.structured_layout.addLayout(self.structured_linewidth_layout)

            initial_structured_alpha = self.vertex.structured_alpha if self.vertex.structured_alpha is not None else 1.0
            self.structured_alpha_layout, self.structured_alpha_input = self._create_spinbox_row("透明度:", initial_structured_alpha, min_val=0.0, max_val=1.0, step=0.01)
            self.structured_layout.addLayout(self.structured_alpha_layout)

            # Hatching Parameters
            self.hatch_group = QGroupBox(self.tr("阴影线 (Hatching)"))
            self.hatch_layout = QVBoxLayout(self.hatch_group)
            scroll_content_layout.addWidget(self.hatch_group)

            self.use_custom_hatch_checkbox = QCheckBox(self.tr("使用自定义阴影线"))
            self.use_custom_hatch_checkbox.setChecked(self.vertex.use_custom_hatch)
            self.use_custom_hatch_checkbox.toggled.connect(self._toggle_hatch_visibility)
            self.hatch_layout.addWidget(self.use_custom_hatch_checkbox)

            hatch_pattern_layout = QHBoxLayout()
            hatch_pattern_layout.addWidget(QLabel(self.tr("图案:")))
            self.hatch_pattern_input = QLineEdit(self.vertex.hatch_pattern if self.vertex.hatch_pattern is not None else "")
            hatch_pattern_layout.addWidget(self.hatch_pattern_input)
            self.hatch_layout.addLayout(hatch_pattern_layout)

            # Custom Hatch Parameters
            self.custom_hatch_color_btn = QPushButton(self.tr("自定义阴影线颜色"))
            self._custom_hatch_line_color_picked_color = self.vertex.custom_hatch_line_color if self.vertex.custom_hatch_line_color is not None else '#000000'
            self.custom_hatch_color_btn.clicked.connect(lambda: self._pick_color(self.custom_hatch_color_btn, '_custom_hatch_line_color_picked_color'))
            self.hatch_layout.addWidget(self.custom_hatch_color_btn)
            self._set_button_color(self.custom_hatch_color_btn, self._custom_hatch_line_color_picked_color)

            initial_custom_hatch_linewidth = self.vertex.custom_hatch_line_width if self.vertex.custom_hatch_line_width is not None else 1.0
            self.custom_hatch_linewidth_layout, self.custom_hatch_linewidth_input = self._create_spinbox_row("自定义线宽:", initial_custom_hatch_linewidth, min_val=0.1, max_val=5.0, step=0.1)
            self.hatch_layout.addLayout(self.custom_hatch_linewidth_layout)

            initial_custom_hatch_angle_deg = self.vertex.custom_hatch_line_angle_deg if self.vertex.custom_hatch_line_angle_deg is not None else 45.0
            self.custom_hatch_angle_layout, self.custom_hatch_angle_input = self._create_spinbox_row("自定义角度(度):", initial_custom_hatch_angle_deg, min_val=0.0, max_val=360.0, step=1.0)
            self.hatch_layout.addLayout(self.custom_hatch_angle_layout)

            initial_custom_hatch_spacing_ratio = self.vertex.custom_hatch_spacing_ratio if self.vertex.custom_hatch_spacing_ratio is not None else 0.1
            self.custom_hatch_spacing_layout, self.custom_hatch_spacing_input = self._create_spinbox_row("自定义间距比例:", initial_custom_hatch_spacing_ratio, min_val=0.01, max_val=1.0, step=0.01)
            self.hatch_layout.addLayout(self.custom_hatch_spacing_layout)

            # --- 将所有内容添加到 QScrollArea 中 ---
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(scroll_content_widget)

            self.main_dialog_layout.addWidget(scroll_area)

            # Initialize structured vertex settings visibility
            self._toggle_structured_visibility(self.is_structured_checkbox.isChecked())
            # Initialize hatch settings visibility based on its checkbox
            self._toggle_hatch_visibility(self.use_custom_hatch_checkbox.isChecked())


            # OK/Cancel buttons
            button_layout = QHBoxLayout()
            ok_button = QPushButton(self.tr("确定"))
            ok_button.clicked.connect(self.accept)
            cancel_button = QPushButton(self.tr("取消"))
            cancel_button.clicked.connect(self.reject)
            button_layout.addStretch(1)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            self.main_dialog_layout.addLayout(button_layout)


        def _create_spinbox_row(self, label_text, initial_value, min_val=-999.0, max_val=999.0, step=1.0, is_int=False):
            """Helper function to create a label and QSpinBox/QDoubleSpinBox in a horizontal layout."""
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
                spinbox.setValue(float(initial_value))
                spinbox.setDecimals(2)
            h_layout.addWidget(spinbox)
            return h_layout, spinbox


        def _create_dual_spinbox_row(self, label1_text, initial1_value, label2_text, initial2_value, is_int=True):
            """
            Helper function to create two labels and two spinboxes in a single horizontal layout.
            """
            h_layout = QHBoxLayout()

            # 第一个控件组 (左边)
            h_layout.addWidget(QLabel(label1_text))
            if is_int:
                spinbox1 = QSpinBox()
                spinbox1.setRange(0, 100)
                spinbox1.setValue(int(initial1_value))
            else:
                spinbox1 = QDoubleSpinBox()
                spinbox1.setRange(-999.0, 999.0)
                spinbox1.setValue(float(initial1_value))
                spinbox1.setDecimals(2)
            h_layout.addWidget(spinbox1)
            
            # 添加一个分隔符或间隔
            h_layout.addSpacing(20)

            # 第二个控件组 (右边)
            h_layout.addWidget(QLabel(label2_text))
            if is_int:
                spinbox2 = QSpinBox()
                spinbox2.setRange(0, 100)
                spinbox2.setValue(int(initial2_value))
            else:
                spinbox2 = QDoubleSpinBox()
                spinbox2.setRange(-999.0, 999.0)
                spinbox2.setValue(float(initial2_value))
                spinbox2.setDecimals(2)
            h_layout.addWidget(spinbox2)

            return h_layout, spinbox1, spinbox2


        def _pick_color(self, button, temp_attr_name):
            """Opens a color dialog, sets the button's background color, and stores the selected color."""
            initial_color_str = getattr(self, temp_attr_name)
            initial_qcolor = QColor(initial_color_str)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                hex_color = color.name()
                self._set_button_color(button, hex_color)
                setattr(self, temp_attr_name, hex_color)

        def _set_button_color(self, button, color_str):
            """Helper function to set the button's background and contrasting text color."""
            palette = button.palette()

            qcolor = QColor(color_str)

            # Calculate luminance to determine if the color is light or dark
            luminance = (0.299 * qcolor.red() + 0.587 * qcolor.green() + 0.114 * qcolor.blue()) / 255

            # Set text color based on luminance
            text_color = QColor(Qt.black) if luminance > 0.5 else QColor(Qt.white)

            palette.setColor(QPalette.Button, qcolor)
            palette.setColor(QPalette.ButtonText, text_color)

            button.setPalette(palette)
            button.setAutoFillBackground(True)
            button.setText(f"{button.text().split('(')[0].strip()} ({color_str})")

        def _toggle_structured_visibility(self, is_checked):
            """Controls the visibility of structured vertex settings based on checkbox state."""
            for i in range(self.structured_layout.count()):
                item = self.structured_layout.itemAt(i)
                if item:
                    if item.widget() == self.is_structured_checkbox:
                        continue

                    if item.widget():
                        item.widget().setVisible(is_checked)
                    elif item.layout():
                        for j in range(item.layout().count()):
                            sub_item = item.layout().itemAt(j)
                            if sub_item.widget():
                                sub_item.widget().setVisible(is_checked)

            if not is_checked:
                self.hatch_group.setVisible(False)
            else:
                self._toggle_hatch_visibility(self.use_custom_hatch_checkbox.isChecked())


        def _toggle_hatch_visibility(self, use_custom_hatch_checked):
            """Controls the visibility of custom hatch settings."""
            if not self.is_structured_checkbox.isChecked():
                self.hatch_group.setVisible(False)
                return

            self.hatch_group.setVisible(True)
            for i in range(self.hatch_layout.count()):
                item = self.hatch_layout.itemAt(i)
                if item:
                    if item.widget() == self.use_custom_hatch_checkbox:
                        continue

                    if item.widget():
                        item.widget().setVisible(use_custom_hatch_checked)
                    elif item.layout():
                        for j in range(item.layout().count()):
                            sub_item = item.layout().itemAt(j)
                            if sub_item.widget():
                                sub_item.widget().setVisible(use_custom_hatch_checked)

        # 修正：更新此方法以使用 self.vertex.hidden_vertex 属性
        def _toggle_vertex_visibility(self, checked: bool):
            """
            根据“隐藏顶点”复选框的状态，更新顶点对象的 hidden_vertex 属性。
            """
            self.vertex.hidden_vertex = checked
            # 通常，当你修改 hidden_vertex 属性时，需要一个机制来触发图的重新绘制，
            # 这样 Matplotlib 才能反映出这个变化。这个通常在 diagram_model 中处理。

        # 修正：更新此方法以使用 self.vertex.hidden_label 属性
        def _toggle_label_visibility(self, checked: bool):
            """
            根据“隐藏标签”复选框的状态，更新顶点标签对象的 hidden_label 属性。
            """
            self.vertex.hidden_label = checked
            # 同上，这里也需要一个触发图重新绘制的机制。


        def accept(self):
            """Called when the OK button is clicked. Updates the properties of the passed Vertex object."""
            # 属性的更新已在 _toggle_vertex_visibility 和 _toggle_label_visibility 中实时生效
            # 这里只需确保其他属性被正确保存。
            self.vertex.x = self.x_input.value()
            self.vertex.y = self.y_input.value()
            self.vertex.label = self.label_input.text()

            if hasattr(self.vertex, 'color'):
                self.vertex.color = self._vertex_picked_color

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
            if hasattr(self.vertex, 'zorder'):
                self.vertex.zorder = self.vertex_zorder_input.value()
            if hasattr(self.vertex, 'label_size'):
                self.vertex.label_size = self.label_fontsize_input.value()

            # self.vertex.vertex_type = self.type_combo.currentData()
            # self.vertex.coupling_constant = self.coupling_input.value()
            # self.vertex.symmetry_factor = self.symmetry_input.value()

            self.vertex.label_offset = np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()])
            if hasattr(self.vertex, 'label_zorder'):
                self.vertex.label_zorder = self.label_zorder_input.value()

            self.vertex.is_structured = self.is_structured_checkbox.isChecked()
            if self.vertex.is_structured:
                self.vertex.structured_radius = self.structured_radius_input.value()
                self.vertex.structured_facecolor = self._structured_facecolor_picked_color
                self.vertex.structured_edgecolor = self._structured_edgecolor_picked_color
                self.vertex.structured_linewidth = self.structured_linewidth_input.value()
                self.vertex.structured_alpha = self.structured_alpha_input.value()

            self.vertex.use_custom_hatch = self.use_custom_hatch_checkbox.isChecked()
            if self.vertex.use_custom_hatch:
                hatch_pattern_text = self.hatch_pattern_input.text()
                self.vertex.hatch_pattern = hatch_pattern_text if hatch_pattern_text else None
                self.vertex.custom_hatch_line_color = self._custom_hatch_line_color_picked_color
                self.vertex.custom_hatch_line_width = self.custom_hatch_linewidth_input.value()
                self.vertex.custom_hatch_line_angle_deg = self.custom_hatch_angle_input.value()
                self.vertex.custom_hatch_spacing_ratio = self.custom_hatch_spacing_input.value()

            super().accept()

    dialog = _InternalEditVertexDialog(vertex, parent_dialog=parent_widget)

    if dialog.exec() == QDialog.Accepted:
        if diagram_model:
            # Emit a signal to tell the model that the diagram has changed, so it can re-render
            # This is crucial for the hide/show changes to be visible immediately
            if hasattr(diagram_model, 'diagram_changed') and isinstance(diagram_model.diagram_changed, Qt.Signal):
                diagram_model.diagram_changed.emit()
            
            # The logic for adjusting associated line angles remains unchanged
            associated_line_ids = diagram_model.get_associated_line_ids(vertex.id)
            for line_id in associated_line_ids:
                line = diagram_model.get_line_by_id(line_id)
                if line:
                    v_start_updated = line.v_start
                    v_end_updated = line.v_end
                    if v_start_updated and v_end_updated:
                        line.set_angles(v_start_updated, v_end_updated)

        # QMessageBox.information(parent_widget, "编辑成功", f"顶点 {vertex.id} 属性已更新，关联线条角度已调整。")
        return True
    else:
        # If the user cancels, the visibility changes made via the checkboxes will remain.
        # If strict undo is required, the original visibility states of vertex and label
        # would need to be stored upon dialog opening and restored here.
        # QMessageBox.information(parent_widget, "编辑取消", f"顶点 {vertex.id} 属性编辑已取消。")
        return False