# feynplot_gui/controllers/line_dialogs/edit_line.py

from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QColorDialog, QCheckBox, QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from typing import Optional, Dict, Any

# 引入所有具体的线条类型
from feynplot.core.line import (
    Line,
    FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine # 确保 WPlusLine, WMinusLine, ZBosonLine 已导入
)
from feynplot.core.diagram import FeynmanDiagram 

import numpy as np

def open_edit_line_dialog(line: Line, diagram_model: FeynmanDiagram, parent_widget=None) -> bool:
    """
    打开一个对话框以编辑给定 Line 对象的属性。

    Args:
        line (Line): 要编辑的 Line 对象。
        diagram_model (FeynmanDiagram): 整个图的 FeynmanDiagram 模型实例。
        parent_widget (QWidget, optional): 对话框的父控件。

    Returns:
        bool: 如果用户点击了“确定”并成功更新了线条属性，则返回 True；否则返回 False。
    """
    if not isinstance(line, Line):
        QMessageBox.critical(parent_widget, "错误", "提供的对象不是一个有效的线条。")
        return False

    class _InternalEditLineDialog(QDialog):
        def __init__(self, line_obj: Line, diagram_model: FeynmanDiagram, parent_dialog=None):
            super().__init__(parent_dialog)
            self.setWindowTitle(f"编辑线条: {line_obj.label} (ID: {line_obj.id})")
            self.setGeometry(200, 200, 480, 750) # 适当调整对话框大小以容纳更多控件

            self.line = line_obj
            self.diagram_model = diagram_model 
            
            self._original_v_start = line_obj.v_start
            self._original_v_end = line_obj.v_end

            self.layout = QVBoxLayout(self)

            # --- 基本属性 ---
            basic_group = QGroupBox("基本属性")
            basic_layout = QVBoxLayout(basic_group)
            self.layout.addWidget(basic_group)

            # 标签 (Label)
            label_layout = QHBoxLayout()
            label_layout.addWidget(QLabel("标签:"))
            self.label_input = QLineEdit(self.line.label)
            label_layout.addWidget(self.label_input)
            basic_layout.addLayout(label_layout)

            # 显示起点和终点（只读信息）
            start_label = self.line.v_start.label if self.line.v_start else '无'
            start_id = self.line.v_start.id if self.line.v_start else 'N/A'
            end_label = self.line.v_end.label if self.line.v_end else '无'
            end_id = self.line.v_end.id if self.line.v_end else 'N/A'

            basic_layout.addWidget(QLabel(f"<b>起点:</b> {start_label} (ID: {start_id})"))
            basic_layout.addWidget(QLabel(f"<b>终点:</b> {end_label} (ID: {end_id})"))

            # --- 线条类型选择 (Line Type Selection) ---
            particle_type_layout = QHBoxLayout()
            particle_type_layout.addWidget(QLabel("线条粒子类型:"))
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

            current_particle_type_class = type(self.line)
            current_index = -1
            for i, (display_name, particle_class) in enumerate(self.particle_types.items()):
                self.particle_type_combo.addItem(display_name, particle_class)
                if particle_class == current_particle_type_class:
                    current_index = i
            
            if current_index != -1:
                self.particle_type_combo.setCurrentIndex(current_index)
            else:
                self.particle_type_combo.addItem("未知类型", None)
                self.particle_type_combo.setCurrentIndex(self.particle_type_combo.count() - 1)
                QMessageBox.warning(self, "警告", f"当前线条类型 '{current_particle_type_class.__name__}' 不在可选择列表中。")

            particle_type_layout.addWidget(self.particle_type_combo)
            basic_layout.addLayout(particle_type_layout)

            # --- 通用绘图属性 ---
            self.line_color_btn = QPushButton("线条颜色")
            self._line_color_picked_color = self.line.linePlotConfig.get('color', '#000000') 
            self.line_color_btn.clicked.connect(lambda: self._pick_color(self.line_color_btn, '_line_color_picked_color'))
            basic_layout.addWidget(self.line_color_btn)
            self._set_button_color(self.line_color_btn, self._line_color_picked_color)

            self.line_width_layout, self.line_width_input = self._create_spinbox_row(
                "线宽:", float(self.line.linePlotConfig.get('linewidth', 1.0)), min_val=0.1, max_val=10.0, step=0.1
            )
            basic_layout.addLayout(self.line_width_layout)

            self.line_alpha_layout, self.line_alpha_input = self._create_spinbox_row(
                "透明度:", float(self.line.linePlotConfig.get('alpha', 1.0)), min_val=0.0, max_val=1.0, step=0.01
            )
            basic_layout.addLayout(self.line_alpha_layout)

            label_offset_x = float(self.line.label_offset[0]) if (isinstance(self.line.label_offset, (list, tuple, np.ndarray)) and len(self.line.label_offset) > 0 and self.line.label_offset[0] is not None) else 0.0
            label_offset_y = float(self.line.label_offset[1]) if (isinstance(self.line.label_offset, (list, tuple, np.ndarray)) and len(self.line.label_offset) > 1 and self.line.label_offset[1] is not None) else 0.0
            self.label_offset_x_layout, self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
            self.label_offset_y_layout, self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
            basic_layout.addLayout(self.label_offset_x_layout)
            basic_layout.addLayout(self.label_offset_y_layout)

            # --- 新增 bezier_offset 编辑 (通用属性) ---
            self.bezier_offset_layout, self.bezier_offset_input = self._create_spinbox_row(
                "贝塞尔偏移:", 0.3, min_val=0.0, max_val=1.0, step=0.01
            )
            basic_layout.addLayout(self.bezier_offset_layout)

            # --- 新增 angle_in 和 angle_out 编辑 ---
            self.angle_in_layout, self.angle_in_input = self._create_spinbox_row(
                "入角 (Angle In):", 0.0, min_val=-180.0, max_val=180.0, step=1.0
            )
            basic_layout.addLayout(self.angle_in_layout)

            self.angle_out_layout, self.angle_out_input = self._create_spinbox_row(
                "出角 (Angle Out):", 0.0, min_val=-180.0, max_val=180.0, step=1.0
            )
            basic_layout.addLayout(self.angle_out_layout)
            
            # --- 特定线条类型的属性组 ---
            self.specific_props_group = QGroupBox("特定线条属性")
            self.specific_props_layout = QVBoxLayout(self.specific_props_group)
            self.layout.addWidget(self.specific_props_group)

            # --- FermionLine / AntiFermionLine 特有属性 ---
            self.fermion_arrow_checkbox = QCheckBox("显示箭头")
            self.fermion_arrow_filled_checkbox = QCheckBox("箭头填充")
            self.fermion_arrow_position_layout, self.fermion_arrow_position_input = \
                self._create_spinbox_row("箭头位置 (0-1):", 0.5, min_val=0.0, max_val=1.0, step=0.01)
            self.fermion_arrow_size_layout, self.fermion_arrow_size_input = \
                self._create_spinbox_row("箭头大小:", 10.0, min_val=1.0, max_val=50.0, step=1.0, is_int=True)
            self.fermion_arrow_line_width_layout, self.fermion_arrow_line_width_input = \
                self._create_spinbox_row("箭头线宽:", 1.0, min_val=0.1, max_val=10.0, step=0.1)
            self.fermion_arrow_reversed_checkbox = QCheckBox("箭头反向")

            self.specific_props_layout.addWidget(self.fermion_arrow_checkbox)
            self.specific_props_layout.addWidget(self.fermion_arrow_filled_checkbox)
            self.specific_props_layout.addLayout(self.fermion_arrow_position_layout)
            self.specific_props_layout.addLayout(self.fermion_arrow_size_layout)
            self.specific_props_layout.addLayout(self.fermion_arrow_line_width_layout)
            self.specific_props_layout.addWidget(self.fermion_arrow_reversed_checkbox)

            # --- PhotonLine 特有属性 ---
            self.photon_amplitude_layout, self.photon_amplitude_input = \
                self._create_spinbox_row("振幅:", 0.1, min_val=0.01, max_val=1.0, step=0.01)
            self.photon_wavelength_layout, self.photon_wavelength_input = \
                self._create_spinbox_row("波长:", 0.5, min_val=0.1, max_val=2.0, step=0.05)
            
            # 初末相位选择 (0 或 180)
            self.photon_initial_phase_group = QButtonGroup(self)
            self.photon_initial_phase_0 = QRadioButton("0°")
            self.photon_initial_phase_180 = QRadioButton("180°")
            self.photon_initial_phase_group.addButton(self.photon_initial_phase_0, 0)
            self.photon_initial_phase_group.addButton(self.photon_initial_phase_180, 180)
            self.initial_phase_h_layout = QHBoxLayout() # 为初相位创建独立布局
            self.initial_phase_h_layout.addWidget(QLabel("初相位:"))
            self.initial_phase_h_layout.addWidget(self.photon_initial_phase_0)
            self.initial_phase_h_layout.addWidget(self.photon_initial_phase_180)
            self.specific_props_layout.addLayout(self.initial_phase_h_layout)

            self.photon_final_phase_group = QButtonGroup(self)
            self.photon_final_phase_0 = QRadioButton("0°")
            self.photon_final_phase_180 = QRadioButton("180°")
            self.photon_final_phase_group.addButton(self.photon_final_phase_0, 0)
            self.photon_final_phase_group.addButton(self.photon_final_phase_180, 180)
            self.final_phase_h_layout = QHBoxLayout() # 为末相位创建独立布局
            self.final_phase_h_layout.addWidget(QLabel("末相位:"))
            self.final_phase_h_layout.addWidget(self.photon_final_phase_0)
            self.final_phase_h_layout.addWidget(self.photon_final_phase_180)
            self.specific_props_layout.addLayout(self.final_phase_h_layout)

            self.specific_props_layout.addLayout(self.photon_amplitude_layout)
            self.specific_props_layout.addLayout(self.photon_wavelength_layout)


            # --- GluonLine 特有属性 ---
            self.gluon_amplitude_layout, self.gluon_amplitude_input = \
                self._create_spinbox_row("振幅:", 0.1, min_val=0.01, max_val=1.0, step=0.01)
            self.gluon_wavelength_layout, self.gluon_wavelength_input = \
                self._create_spinbox_row("波长:", 0.2, min_val=0.05, max_val=1.0, step=0.01)
            self.gluon_n_cycles_layout, self.gluon_n_cycles_input = \
                self._create_spinbox_row("周期数:", 16, min_val=1, max_val=100, step=1, is_int=True)
            # GluonLine 的 bezier_offset 如果与通用 Line 的 bezier_offset 概念不同，则保持独立
            # 如果是同一个概念，则 GluonLine 不应再有此属性，而应使用 Line 基类的属性
            # 在这里我们假设它是 GluonLine 特有的，如果实际是通用，请移除此行并使用通用控件
            self.gluon_bezier_offset_layout, self.gluon_bezier_offset_input = \
                self._create_spinbox_row("胶子贝塞尔偏移:", 0.3, min_val=0.0, max_val=1.0, step=0.01) 

            self.specific_props_layout.addLayout(self.gluon_amplitude_layout)
            self.specific_props_layout.addLayout(self.gluon_wavelength_layout)
            self.specific_props_layout.addLayout(self.gluon_n_cycles_layout)
            self.specific_props_layout.addLayout(self.gluon_bezier_offset_layout) # 保持 Gluon 特有贝塞尔偏移

            # --- W/Z 玻色子线特有属性 (新增) ---
            self.zigzag_amplitude_layout, self.zigzag_amplitude_input = \
                self._create_spinbox_row("折线振幅:", 0.2, min_val=0.0, max_val=1.0, step=0.01)
            self.zigzag_frequency_layout, self.zigzag_frequency_input = \
                self._create_spinbox_row("折线频率:", 2.0, min_val=0.1, max_val=10.0, step=0.1)
            
            self.specific_props_layout.addLayout(self.zigzag_amplitude_layout)
            self.specific_props_layout.addLayout(self.zigzag_frequency_layout)

            # 连接下拉框变化信号到更新函数
            self.particle_type_combo.currentIndexChanged.connect(self._update_specific_properties_ui)
            
            # 初始化 UI 显示：先加载当前线条属性值，再根据当前类型更新 UI 控件可见性
            self._load_current_line_properties()
            # self._update_specific_properties_ui 在 _load_current_line_properties 内部最后调用，确保初始状态正确

            # 确定/取消按钮 (OK/Cancel buttons)
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
            """辅助函数：创建带标签的 SpinBox."""
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(label_text))
            if is_int:
                spinbox = QSpinBox()
                spinbox.setRange(int(min_val), int(max_val))
                spinbox.setSingleStep(int(step))
                # 确保初始值是整数
                spinbox.setValue(int(initial_value))
            else:
                spinbox = QDoubleSpinBox()
                spinbox.setRange(min_val, max_val)
                spinbox.setSingleStep(step)
                # 确保初始值是浮点数
                spinbox.setValue(float(initial_value))
                spinbox.setDecimals(2)
            h_layout.addWidget(spinbox)
            return h_layout, spinbox

        def _pick_color(self, button, color_attr_name):
            """打开颜色对话框并设置按钮颜色，存储选定颜色."""
            initial_color_str = getattr(self, color_attr_name)
            initial_qcolor = QColor(initial_color_str)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                hex_color = color.name()
                self._set_button_color(button, hex_color)
                setattr(self, color_attr_name, hex_color)

        def _set_button_color(self, button, color_str):
            """辅助函数：设置按钮背景颜色."""
            palette = button.palette()
            palette.setColor(QPalette.Button, QColor(color_str))
            button.setPalette(palette)
            button.setAutoFillBackground(True)
            button.setText(f"{button.text().split('(')[0].strip()} ({color_str})")

        def _load_current_line_properties(self):
            """根据当前的 self.line 对象，初始化所有属性的 UI 控件值。"""
            
            # 辅助函数：安全地获取属性值并转换为指定类型
            def _get_value_or_default(obj, attr_name, default_val, target_type=float):
                val = getattr(obj, attr_name, default_val)
                if val is None: # 如果属性存在但值为 None，使用默认值
                    return target_type(default_val)
                try: # 尝试转换为目标类型
                    return target_type(val)
                except (ValueError, TypeError): # 转换失败，使用默认值
                    return target_type(default_val)

            # 通用属性 (包括 bezier_offset)
            self.bezier_offset_input.setValue(_get_value_or_default(self.line, 'bezier_offset', 0.3, float))
            self.angle_in_input.setValue(_get_value_or_default(self.line, '_angleIn', 0.0, float))
            self.angle_out_input.setValue(_get_value_or_default(self.line, '_angleOut', 0.0, float))

            # FermionLine 属性
            if isinstance(self.line, (FermionLine, AntiFermionLine)):
                self.fermion_arrow_checkbox.setChecked(getattr(self.line, 'arrow', True))
                self.fermion_arrow_filled_checkbox.setChecked(getattr(self.line, 'arrow_filled', False))
                self.fermion_arrow_position_input.setValue(_get_value_or_default(self.line, 'arrow_position', 0.5, float))
                self.fermion_arrow_size_input.setValue(_get_value_or_default(self.line, 'arrow_size', 10.0, float))
                self.fermion_arrow_line_width_input.setValue(_get_value_or_default(self.line, 'arrow_line_width', 1.0, float))
                self.fermion_arrow_reversed_checkbox.setChecked(getattr(self.line, 'arrow_reversed', False))
            
            # PhotonLine 属性
            elif isinstance(self.line, PhotonLine):
                self.photon_amplitude_input.setValue(_get_value_or_default(self.line, 'amplitude', 0.1, float))
                self.photon_wavelength_input.setValue(_get_value_or_default(self.line, 'wavelength', 0.5, float))
                initial_phase = _get_value_or_default(self.line, 'initial_phase', 0, int)
                if initial_phase == 0:
                    self.photon_initial_phase_0.setChecked(True)
                else:
                    self.photon_initial_phase_180.setChecked(True)
                final_phase = _get_value_or_default(self.line, 'final_phase', 0, int)
                if final_phase == 0:
                    self.photon_final_phase_0.setChecked(True)
                else:
                    self.photon_final_phase_180.setChecked(True)

            # GluonLine 属性
            elif isinstance(self.line, GluonLine):
                self.gluon_amplitude_input.setValue(_get_value_or_default(self.line, 'amplitude', 0.1, float))
                self.gluon_wavelength_input.setValue(_get_value_or_default(self.line, 'wavelength', 0.2, float))
                self.gluon_n_cycles_input.setValue(_get_value_or_default(self.line, 'n_cycles', 16, int))
                # GluonLine 的 bezier_offset
                self.gluon_bezier_offset_input.setValue(_get_value_or_default(self.line, 'bezier_offset', 0.3, float))
            
            # W/Z BosonLine 属性 (新增)
            elif isinstance(self.line, (WPlusLine, WMinusLine, ZBosonLine)):
                self.zigzag_amplitude_input.setValue(_get_value_or_default(self.line, 'zigzag_amplitude', 0.2, float))
                self.zigzag_frequency_input.setValue(_get_value_or_default(self.line, 'zigzag_frequency', 2.0, float))


            # 加载完成后，根据当前线条类型更新 UI 控件可见性
            self._update_specific_properties_ui(self.particle_type_combo.currentIndex())


        def _set_widgets_visible(self, widgets, visible):
            """辅助函数：设置一组控件及其子控件的可见性."""
            for widget in widgets:
                if isinstance(widget, QHBoxLayout) or isinstance(widget, QVBoxLayout): # 检查是布局
                    for i in range(widget.count()):
                        item = widget.itemAt(i)
                        if item.widget(): # 如果是控件
                            item.widget().setVisible(visible)
                        elif item.layout(): # 如果是嵌套布局
                            self._set_widgets_visible([item.layout()], visible) # 递归调用
                elif widget: # 如果是单个控件 (非布局)
                    widget.setVisible(visible)

        def _update_specific_properties_ui(self, index):
            """根据当前选择的线条类型，显示/隐藏特定的属性控件。"""
            selected_class = self.particle_type_combo.itemData(index)

            # 隐藏所有特定属性控件
            self._set_widgets_visible([
                self.fermion_arrow_checkbox, self.fermion_arrow_filled_checkbox,
                self.fermion_arrow_position_layout, self.fermion_arrow_size_layout,
                self.fermion_arrow_line_width_layout, self.fermion_arrow_reversed_checkbox,
                self.photon_amplitude_layout, self.photon_wavelength_layout,
                self.initial_phase_h_layout, 
                self.final_phase_h_layout,   
                self.gluon_amplitude_layout, self.gluon_wavelength_layout,
                self.gluon_n_cycles_layout, self.gluon_bezier_offset_layout, # GluonLine 特有的 bezier_offset
                self.zigzag_amplitude_layout, self.zigzag_frequency_layout, 
            ], False)

            # 根据选定类型显示相关控件
            if selected_class in (FermionLine, AntiFermionLine):
                self._set_widgets_visible([
                    self.fermion_arrow_checkbox, self.fermion_arrow_filled_checkbox,
                    self.fermion_arrow_position_layout, self.fermion_arrow_size_layout,
                    self.fermion_arrow_line_width_layout, self.fermion_arrow_reversed_checkbox,
                ], True)
            elif selected_class == PhotonLine:
                self._set_widgets_visible([
                    self.photon_amplitude_layout, self.photon_wavelength_layout,
                    self.initial_phase_h_layout, 
                    self.final_phase_h_layout,   
                ], True)
            elif selected_class == GluonLine:
                self._set_widgets_visible([
                    self.gluon_amplitude_layout, self.gluon_wavelength_layout,
                    self.gluon_n_cycles_layout, self.gluon_bezier_offset_layout,
                ], True)
            elif selected_class in (WPlusLine, WMinusLine, ZBosonLine): # 新增 W/Z 玻色子条件
                self._set_widgets_visible([
                    self.zigzag_amplitude_layout, self.zigzag_frequency_layout,
                ], True)


        def accept(self):
            """当点击 OK 按钮时调用。更新传入的 Line 对象的属性。
            如果线条类型发生变化，将替换原始线条。"""
            
            selected_particle_class = self.particle_type_combo.currentData()

            new_label = self.label_input.text()
            new_label_offset = np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()])
            new_color = self._line_color_picked_color
            new_linewidth = self.line_width_input.value()
            new_alpha = self.line_alpha_input.value()
            
            # 获取通用属性：bezier_offset, angle_in, angle_out 的值
            new_bezier_offset = float(self.bezier_offset_input.value()) # 获取通用 bezier_offset 值
            new_angle_in = float(self.angle_in_input.value())
            new_angle_out = float(self.angle_out_input.value())

            # 通用 kwargs (现在包含 bezier_offset)
            common_kwargs = {
                'label': new_label,
                'label_offset': new_label_offset,
                'bezier_offset': new_bezier_offset, # 将通用 bezier_offset 包含在通用 kwargs 中
                'line_plot_config': {
                    'color': new_color,
                    'linewidth': new_linewidth,
                    'alpha': new_alpha,
                    **self.line.linePlotConfig # 复制旧的所有配置，然后覆盖新的
                }
            }

            # 收集特定线条类型的参数
            specific_kwargs = {}
            if selected_particle_class in (FermionLine, AntiFermionLine):
                specific_kwargs = {
                    'arrow': self.fermion_arrow_checkbox.isChecked(),
                    'arrow_filled': self.fermion_arrow_filled_checkbox.isChecked(),
                    'arrow_position': float(self.fermion_arrow_position_input.value()),
                    'arrow_size': float(self.fermion_arrow_size_input.value()),
                    'arrow_line_width': float(self.fermion_arrow_line_width_input.value()),
                    'arrow_reversed': self.fermion_arrow_reversed_checkbox.isChecked(),
                }
            elif selected_particle_class == PhotonLine:
                specific_kwargs = {
                    'amplitude': float(self.photon_amplitude_input.value()),
                    'wavelength': float(self.photon_wavelength_input.value()),
                    'initial_phase': int(self.photon_initial_phase_group.checkedId()),
                    'final_phase': int(self.photon_final_phase_group.checkedId()),
                }
            elif selected_particle_class == GluonLine:
                specific_kwargs = {
                    'amplitude': float(self.gluon_amplitude_input.value()),
                    'wavelength': float(self.gluon_wavelength_input.value()),
                    'n_cycles': int(self.gluon_n_cycles_input.value()),
                    'bezier_offset': float(self.gluon_bezier_offset_input.value()), # 收集 GluonLine 特有的 bezier_offset
                }
            elif selected_particle_class in (WPlusLine, WMinusLine, ZBosonLine): # W/Z 玻色子参数收集
                specific_kwargs = {
                    'zigzag_amplitude': float(self.zigzag_amplitude_input.value()),
                    'zigzag_frequency': float(self.zigzag_frequency_input.value()),
                }

            # 如果线条类型发生变化
            if selected_particle_class and type(self.line) != selected_particle_class:
                self.diagram_model.remove_line(self.line.id)
                
                all_kwargs = {
                    'v_start': self._original_v_start, 
                    'v_end': self._original_v_end,
                    'line_type': selected_particle_class,
                    'id': self.line.id, # 保持ID
                    **common_kwargs, # 这里包含了通用 bezier_offset
                    **specific_kwargs
                }
                
                # 调用 diagram_model.add_line，它应该负责创建新线条实例
                self.line = self.diagram_model.add_line(**all_kwargs)
                
                # 新创建的线条，立即用 set_angles 设置用户指定的角度
                if hasattr(self.line, 'set_angles'):
                    self.line.set_angles(v_start=None, v_end=None, angleIn=new_angle_in, angleOut=new_angle_out)

            else:
                # 如果线条类型没有变化，更新现有线条的属性和绘图配置字典
                self.line.label = new_label
                self.line.label_offset = new_label_offset
                self.line.bezier_offset = new_bezier_offset # 更新 Line 基类的 bezier_offset 属性
                self.line.linePlotConfig['color'] = new_color
                self.line.linePlotConfig['linewidth'] = new_linewidth
                self.line.linePlotConfig['alpha'] = new_alpha

                # 使用新的 set_angles 方法来更新角度，确保优先使用用户设置的值
                if hasattr(self.line, 'set_angles'):
                    self.line.set_angles(v_start=None, v_end=None, angleIn=new_angle_in, angleOut=new_angle_out)

                # 更新特定线条的属性
                if isinstance(self.line, (FermionLine, AntiFermionLine)):
                    if hasattr(self.line, 'arrow'): self.line.arrow = self.fermion_arrow_checkbox.isChecked()
                    if hasattr(self.line, 'arrow_filled'): self.line.arrow_filled = self.fermion_arrow_filled_checkbox.isChecked()
                    if hasattr(self.line, 'arrow_position'): self.line.arrow_position = float(self.fermion_arrow_position_input.value())
                    if hasattr(self.line, 'arrow_size'): self.line.arrow_size = float(self.fermion_arrow_size_input.value())
                    if hasattr(self.line, 'arrow_line_width'): self.line.arrow_line_width = float(self.fermion_arrow_line_width_input.value())
                    if hasattr(self.line, 'arrow_reversed'): self.line.arrow_reversed = self.fermion_arrow_reversed_checkbox.isChecked()
                elif isinstance(self.line, PhotonLine):
                    if hasattr(self.line, 'amplitude'): self.line.amplitude = float(self.photon_amplitude_input.value())
                    if hasattr(self.line, 'wavelength'): self.line.wavelength = float(self.photon_wavelength_input.value())
                    if hasattr(self.line, 'initial_phase'): self.line.initial_phase = int(self.photon_initial_phase_group.checkedId())
                    if hasattr(self.line, 'final_phase'): self.line.final_phase = int(self.photon_final_phase_group.checkedId())
                elif isinstance(self.line, GluonLine):
                    if hasattr(self.line, 'amplitude'): self.line.amplitude = float(self.gluon_amplitude_input.value())
                    if hasattr(self.line, 'wavelength'): self.line.wavelength = float(self.gluon_wavelength_input.value())
                    if hasattr(self.line, 'n_cycles'): self.line.n_cycles = int(self.gluon_n_cycles_input.value())
                    if hasattr(self.line, 'bezier_offset'): self.line.bezier_offset = float(self.gluon_bezier_offset_input.value()) # 更新 GluonLine 特有的 bezier_offset
                elif isinstance(self.line, (WPlusLine, WMinusLine, ZBosonLine)): # W/Z 玻色子参数更新
                    if hasattr(self.line, 'zigzag_amplitude'): self.line.zigzag_amplitude = float(self.zigzag_amplitude_input.value())
                    if hasattr(self.line, 'zigzag_frequency'): self.line.zigzag_frequency = float(self.zigzag_frequency_input.value())

            super().accept()

    # 在 open_edit_line_dialog 函数内部实例化并执行这个局部定义的对话框
    dialog = _InternalEditLineDialog(line, diagram_model=diagram_model, parent_dialog=parent_widget)
    
    if dialog.exec() == QDialog.Accepted:
        QMessageBox.information(parent_widget, "编辑成功", f"线条 {line.id} 属性已更新。")
        return True # 返回 True 表示成功，LineController 会触发刷新
    else:
        QMessageBox.information(parent_widget, "编辑取消", f"线条 {line.id} 属性编辑已取消。")
        return False