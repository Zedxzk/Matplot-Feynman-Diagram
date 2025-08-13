# feynplot_gui/controllers/line_dialogs/edit_loop.py

from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QColorDialog, QGroupBox,
    QScrollArea, QWidget, QFormLayout, QCheckBox, QButtonGroup, QRadioButton
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, Signal
from typing import Optional, Dict, Any, Type

# 引入Line类，因为环形线条是通过Line的loop属性实现的
from feynplot.core.line import (
    Line, LineStyle,
    FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine
)
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
import numpy as np


# ============================================================================
# 内嵌的模块化编辑器基类和具体实现
# ============================================================================

class LoopEditBase:
    """环形线条编辑器的基类，提供通用的UI创建方法"""
    
    def __init__(self):
        pass
    
    def _create_spinbox_row(self, label_text: str, initial_value: float, 
                            min_val: float = 0.0, max_val: float = 100.0, 
                            step: float = 0.1, is_int: bool = False):
        """创建一个带标签的数值输入框行"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        
        if is_int:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_val), int(max_val))
            spinbox.setSingleStep(int(step))
            spinbox.setValue(int(initial_value))
        else:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setSingleStep(step)
            spinbox.setDecimals(2)
            spinbox.setValue(initial_value)
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        
        return layout, spinbox
    
    def _set_button_color(self, button: QPushButton, color: str):
        """设置按钮的背景颜色"""
        button.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
    
    def _pick_color(self, button: QPushButton, color_attr_name: str):
        """打开颜色选择器，更新指定的颜色属性"""
        current_color = getattr(self, color_attr_name)
        initial_qcolor = QColor(current_color)
        color = QColorDialog.getColor(initial_qcolor, button.parent())
        if color.isValid():
            setattr(self, color_attr_name, color.name())
            self._set_button_color(button, color.name())


class FermionLoopEditor:
    """费米子环形线条编辑器"""
    
    def __init__(self, form_layout: QFormLayout, loop: Line):
        self.form_layout = form_layout
        self.loop = loop
        self.widgets = []
        self._create_ui()
    
    def _create_ui(self):
        """创建费米子环形线条特有的UI控件"""
        # 费米子环形线条特有属性：箭头方向
        self.arrow_direction_combo = QComboBox()
        self.arrow_direction_combo.addItems(['顺时针', '逆时针'])
        
        arrow_direction_label = QLabel("箭头方向:")
        self.form_layout.addRow(arrow_direction_label, self.arrow_direction_combo)
        
        self.widgets.extend([arrow_direction_label, self.arrow_direction_combo])
        self._load_properties()
    
    def _load_properties(self):
        """从loop对象加载属性到UI"""
        # 使用 getattr 安全地访问属性，提供默认值
        direction = getattr(self.loop, 'arrow_direction', 'clockwise')
        if direction == 'clockwise':
            self.arrow_direction_combo.setCurrentText('顺时针')
        else:
            self.arrow_direction_combo.setCurrentText('逆时针')
    
    def set_visible(self, visible: bool):
        """设置所有控件的可见性"""
        for widget in self.widgets:
            widget.setVisible(visible)
    
    def get_specific_kwargs(self) -> Dict[str, Any]:
        """获取费米子环形线条特有的参数"""
        direction = 'clockwise' if self.arrow_direction_combo.currentText() == '顺时针' else 'counterclockwise'
        return {'arrow_direction': direction}
    
    def apply_properties(self, loop: Line):
        """将UI中的值应用到loop对象"""
        kwargs = self.get_specific_kwargs()
        for key, value in kwargs.items():
            setattr(loop, key, value)


class PhotonLoopEditor:
    """光子环形线条编辑器"""
    
    def __init__(self, form_layout: QFormLayout, loop: Line):
        self.form_layout = form_layout
        self.loop = loop
        self.widgets = []
        self._create_ui()
    
    def _create_ui(self):
        """创建光子环形线条特有的UI控件"""
        # 光子环形线条特有属性：波长、振幅、初始相位、终止相位
        self.wavelength_spinbox = QDoubleSpinBox()
        self.wavelength_spinbox.setRange(0, 20)
        self.wavelength_spinbox.setSingleStep(0.1)
        wavelength_label = QLabel("波长:")
        self.form_layout.addRow(wavelength_label, self.wavelength_spinbox)
        self.widgets.extend([wavelength_label, self.wavelength_spinbox])

        self.amplitude_spinbox = QDoubleSpinBox()
        self.amplitude_spinbox.setRange(0.01, 2.0)
        self.amplitude_spinbox.setSingleStep(0.02)
        amplitude_label = QLabel("振幅:")
        self.form_layout.addRow(amplitude_label, self.amplitude_spinbox)
        self.widgets.extend([amplitude_label, self.amplitude_spinbox])

        self.initial_phase_label = QLabel("初始相位:")
        self.initial_phase_group = QButtonGroup(self.form_layout.parentWidget() if self.form_layout else None)
        self.initial_phase_0_checkbox = QCheckBox("0°")
        self.initial_phase_180_checkbox = QCheckBox("180°")
        self.initial_phase_group.addButton(self.initial_phase_0_checkbox)
        self.initial_phase_group.addButton(self.initial_phase_180_checkbox)
        initial_phase_layout = QHBoxLayout()
        initial_phase_layout.addWidget(self.initial_phase_0_checkbox)
        initial_phase_layout.addWidget(self.initial_phase_180_checkbox)
        self.form_layout.addRow(self.initial_phase_label, initial_phase_layout)
        self.widgets.extend([self.initial_phase_label, self.initial_phase_0_checkbox, self.initial_phase_180_checkbox])

        self.final_phase_label = QLabel("终止相位:")
        self.final_phase_group = QButtonGroup(self.form_layout.parentWidget() if self.form_layout else None)
        self.final_phase_0_checkbox = QCheckBox("0°")
        self.final_phase_180_checkbox = QCheckBox("180°")
        self.final_phase_group.addButton(self.final_phase_0_checkbox)
        self.final_phase_group.addButton(self.final_phase_180_checkbox)
        final_phase_layout = QHBoxLayout()
        final_phase_layout.addWidget(self.final_phase_0_checkbox)
        final_phase_layout.addWidget(self.final_phase_180_checkbox)
        self.form_layout.addRow(self.final_phase_label, final_phase_layout)
        self.widgets.extend([self.final_phase_label, self.final_phase_0_checkbox, self.final_phase_180_checkbox])
        
        self._load_properties()
    
    def _load_properties(self):
        """从loop对象加载属性到UI"""
        # 使用 getattr 安全地访问属性，提供默认值
        self.wavelength_spinbox.setValue(getattr(self.loop, 'wavelength', 6))
        self.amplitude_spinbox.setValue(getattr(self.loop, 'amplitude', 0.1))
        
        initial_phase = getattr(self.loop, 'initial_phase', 0)
        final_phase = getattr(self.loop, 'final_phase', 0)
        
        if initial_phase == 0:
            self.initial_phase_0_checkbox.setChecked(True)
        else:
            self.initial_phase_180_checkbox.setChecked(True)

        if final_phase == 0:
            self.final_phase_0_checkbox.setChecked(True)
        else:
            self.final_phase_180_checkbox.setChecked(True)
    
    def set_visible(self, visible: bool):
        """设置所有控件的可见性"""
        for widget in self.widgets:
            widget.setVisible(visible)
    
    def get_specific_kwargs(self) -> Dict[str, Any]:
        """获取光子环形线条特有的参数"""
        return {
            'wavelength': self.wavelength_spinbox.value(),
            'amplitude': self.amplitude_spinbox.value(),
            'initial_phase': 0 if self.initial_phase_0_checkbox.isChecked() else 180,
            'final_phase': 0 if self.final_phase_0_checkbox.isChecked() else 180
        }
    
    def apply_properties(self, loop: Line):
        """将UI中的值应用到loop对象"""
        kwargs = self.get_specific_kwargs()
        for key, value in kwargs.items():
            setattr(loop, key, value)


class GluonLoopEditor:
    """胶子环形线条编辑器"""
    
    def __init__(self, form_layout: QFormLayout, loop: Line):
        self.form_layout = form_layout
        self.loop = loop
        self.widgets = []
        self._create_ui()
    
    def _create_ui(self):
        """创建胶子环形线条特有的UI控件"""
        # 胶子环形线条特有属性：螺旋数量和振幅
        self.n_cycles_spinbox = QSpinBox()
        self.n_cycles_spinbox.setRange(1, 20)
        n_cycles_label = QLabel("螺旋数量:")
        
        self.form_layout.addRow(n_cycles_label, self.n_cycles_spinbox)
        
        self.amplitude_spinbox = QDoubleSpinBox()
        self.amplitude_spinbox.setRange(0.1, 2.0)
        self.amplitude_spinbox.setSingleStep(0.1)
        amplitude_label = QLabel("螺旋振幅:")
        
        self.form_layout.addRow(amplitude_label, self.amplitude_spinbox)
        
        self.widgets.extend([
            n_cycles_label, self.n_cycles_spinbox,
            amplitude_label, self.amplitude_spinbox
        ])
        self._load_properties()
    
    def _load_properties(self):
        """从loop对象加载属性到UI"""
        # 使用 getattr 安全地访问属性，提供默认值
        self.n_cycles_spinbox.setValue(getattr(self.loop, 'n_cycles', 8))
        self.amplitude_spinbox.setValue(getattr(self.loop, 'amplitude', 0.3))
    
    def set_visible(self, visible: bool):
        """设置所有控件的可见性"""
        for widget in self.widgets:
            widget.setVisible(visible)
    
    def get_specific_kwargs(self) -> Dict[str, Any]:
        """获取胶子环形线条特有的参数"""
        return {
            'n_cycles': self.n_cycles_spinbox.value(),
            'amplitude': self.amplitude_spinbox.value()
        }
    
    def apply_properties(self, loop: Line):
        """将UI中的值应用到loop对象"""
        kwargs = self.get_specific_kwargs()
        for key, value in kwargs.items():
            setattr(loop, key, value)


class WZBosonLoopEditor:
    """W/Z玻色子环形线条编辑器"""
    
    def __init__(self, form_layout: QFormLayout, loop: Line):
        self.form_layout = form_layout
        self.loop = loop
        self.widgets = []
        self._create_ui()
    
    def _create_ui(self):
        """创建W/Z玻色子环形线条特有的UI控件"""
        # W/Z玻色子环形线条特有属性：虚线模式
        self.amplitude_spinbox = QDoubleSpinBox()
        self.amplitude_spinbox.setRange(0.1, 20)
        self.amplitude_spinbox.setSingleStep(0.01)
        amplitude_label = QLabel("振幅:")
        self.form_layout.addRow(amplitude_label, self.amplitude_spinbox)
        self.widgets.extend([amplitude_label, self.amplitude_spinbox])

        self.frequency_spinbox = QDoubleSpinBox()
        self.frequency_spinbox.setRange(0.1, 100)
        self.frequency_spinbox.setSingleStep(0.1)
        frequency_label = QLabel("频率:")
        self.form_layout.addRow(frequency_label, self.frequency_spinbox)
        self.widgets.extend([frequency_label, self.frequency_spinbox])

        # 初始相位
        self.initial_phase_label = QLabel("初始相位:")
        self.initial_phase_group = QButtonGroup(self.form_layout.parentWidget() if self.form_layout else None) # 假设 self 是一个 QObject 的子类
        self.initial_phase_0_checkbox = QCheckBox("0°")
        self.initial_phase_180_checkbox = QCheckBox("180°")
        self.initial_phase_group.addButton(self.initial_phase_0_checkbox, 0)
        self.initial_phase_group.addButton(self.initial_phase_180_checkbox, 180)
        initial_phase_layout = QHBoxLayout()
        initial_phase_layout.addWidget(self.initial_phase_0_checkbox)
        initial_phase_layout.addWidget(self.initial_phase_180_checkbox)
        self.form_layout.addRow(self.initial_phase_label, initial_phase_layout)
        self.widgets.extend([self.initial_phase_label, self.initial_phase_0_checkbox, self.initial_phase_180_checkbox])


        # 终止相位
        self.final_phase_label = QLabel("终止相位:")
        self.final_phase_group = QButtonGroup(self.form_layout.parentWidget() if self.form_layout else None) # 假设 self 是一个 QObject 的子类
        self.final_phase_0_checkbox = QCheckBox("0°")
        self.final_phase_180_checkbox = QCheckBox("180°")
        self.final_phase_group.addButton(self.final_phase_0_checkbox, 0)
        self.final_phase_group.addButton(self.final_phase_180_checkbox, 180)
        final_phase_layout = QHBoxLayout()
        final_phase_layout.addWidget(self.final_phase_0_checkbox)
        final_phase_layout.addWidget(self.final_phase_180_checkbox)
        self.form_layout.addRow(self.final_phase_label, final_phase_layout)
        self.widgets.extend([self.final_phase_label, self.final_phase_0_checkbox, self.final_phase_180_checkbox])


        self.dash_pattern_combo = QComboBox()
        self.dash_pattern_combo.addItems(['短虚线', '长虚线', '点划线'])
        
        dash_pattern_label = QLabel("虚线模式:")
        self.form_layout.addRow(dash_pattern_label, self.dash_pattern_combo)
        
        self.widgets.extend([dash_pattern_label, self.dash_pattern_combo])
        self._load_properties()
    
    def _load_properties(self):
        """从loop对象加载属性到UI"""
        # 使用 getattr 安全地访问属性，提供默认值
        pattern = getattr(self.loop, 'dash_pattern', 'short')
        if pattern == 'short':
            self.dash_pattern_combo.setCurrentText('短虚线')
        elif pattern == 'long':
            self.dash_pattern_combo.setCurrentText('长虚线')
        else:
            self.dash_pattern_combo.setCurrentText('点划线')
        self.amplitude_spinbox.setValue(getattr(self.loop, 'zigzag_amplitude', 0.3))
        self.frequency_spinbox.setValue(getattr(self.loop, 'zigzag_frequency', 1.0))
        self.initial_phase_0_checkbox.setChecked(getattr(self.loop, 'initial_phase', 0) == 0)
        self.initial_phase_180_checkbox.setChecked(getattr(self.loop, 'initial_phase', 0) == 180)
        self.final_phase_0_checkbox.setChecked(getattr(self.loop, 'final_phase', 0) == 0)
        self.final_phase_180_checkbox.setChecked(getattr(self.loop, 'final_phase', 0) == 180)

    def set_visible(self, visible: bool):
        """设置所有控件的可见性"""
        for widget in self.widgets:
            widget.setVisible(visible)
    
    def get_specific_kwargs(self) -> Dict[str, Any]:
        """获取W/Z玻色子环形线条特有的参数"""
        pattern_map = {
            '短虚线': 'short',
            '长虚线': 'long',
            '点划线': 'dashdot'
        }
        pattern = pattern_map.get(self.dash_pattern_combo.currentText(), 'short')
        return {
            'dash_pattern': pattern,
            'zigzag_amplitude': self.amplitude_spinbox.value(),
            'zigzag_frequency': self.frequency_spinbox.value(),
            'initial_phase': 0 if self.initial_phase_0_checkbox.isChecked() else 180,
            'final_phase': 0 if self.final_phase_0_checkbox.isChecked() else 180,
        }

    def apply_properties(self, loop: Line):
        """将UI中的值应用到loop对象"""
        kwargs = self.get_specific_kwargs()
        for key, value in kwargs.items():
            setattr(loop, key, value)


# ============================================================================
# 主要的编辑对话框函数
# ============================================================================

def open_edit_loop_dialog(loop: Line, diagram_model: FeynmanDiagram, parent_widget=None) -> bool:
    """
    Opens a dialog to edit the properties of a given Loop object (Line with loop=True).
    This function is exclusively for editing existing loops.
    """
    if not isinstance(loop, Line) or not getattr(loop, 'loop', False):
        QMessageBox.critical(parent_widget, "错误", "提供的对象不是一个有效的环形线条，无法编辑。")
        return False

    class _InternalEditLoopDialog(QDialog, LoopEditBase):
        loop_updated = Signal(Line, Optional[Line])

        def __init__(self, loop_obj: Line, diagram_model: FeynmanDiagram, parent_dialog=None):
            super().__init__(parent_dialog)
            LoopEditBase.__init__(self)

            self.loop = loop_obj
            self.diagram_model = diagram_model
            self._original_v_start = loop_obj.v_start
            self._original_v_end = loop_obj.v_end
            self._original_loop_id = loop_obj.id
            dialog_title = f"编辑环形线条: {self.loop.label} (ID: {self.loop.id})"
            self.setWindowTitle(dialog_title)
            self.setGeometry(200, 200, 480, 750)
            self.setMinimumHeight(300)
            self.setMaximumHeight(800)
            self.main_dialog_layout = QVBoxLayout(self)
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_content_widget = QWidget()
            self.main_form_layout = QFormLayout(self.scroll_content_widget)
            self.scroll_area.setWidget(self.scroll_content_widget)
            self.main_dialog_layout.addWidget(self.scroll_area)
            self._current_loop_id_str = self.loop.id 
            self.id_label = QLabel(self)
            self.id_label.setTextFormat(Qt.RichText)
            self.id_label.setText(f"<b>{self._current_loop_id_str}</b>")
            self.main_form_layout.addRow("ID:", self.id_label)
            self.label_input = QLineEdit(self)
            self.label_input.setText(self.loop.label)
            self.main_form_layout.addRow("标签:", self.label_input)
            start_label = self._original_v_start.label if self._original_v_start else '无'
            start_id = self._original_v_start.id if self._original_v_start else 'N/A'
            end_label = self._original_v_end.label if self._original_v_end else '无'
            end_id = self._original_v_end.id if self._original_v_end else 'N/A'
            self.main_form_layout.addRow(QLabel(self.tr("<b>起点:</b>")), QLabel(f"{start_label} (ID: {start_id})"))
            self.main_form_layout.addRow(QLabel(self.tr("<b>终点:</b>")), QLabel(f"{end_label} (ID: {end_id})"))
            self.particle_type_combo = QComboBox(self)
            self.particle_types: Dict[str, Type[Line]] = {
                "费米子环 (Fermion Loop)": FermionLine,
                "反费米子环 (Anti-Fermion Loop)": AntiFermionLine,
                "光子环 (Photon Loop)": PhotonLine,
                "胶子环 (Gluon Loop)": GluonLine,
                "W+ 玻色子环 (W+ Loop)": WPlusLine,
                "W- 玻色子环 (W- Loop)": WMinusLine,
                "Z 玻色子环 (Z Loop)": ZBosonLine,
            }
            current_particle_type_class = type(self.loop)
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
                QMessageBox.warning(self, "警告", f"当前环形线条类型 '{current_particle_type_class.__name__}' 不在可选择列表中。")

            self.main_form_layout.addRow("环形线条粒子类型:", self.particle_type_combo)
            initial_semi_major = getattr(self.loop, 'a', 1.0)
            self.semi_major_layout, self.semi_major_input = self._create_spinbox_row(
                "长轴 a:", initial_semi_major, min_val=0.1, max_val=10.0, step=0.1
            )
            self.main_form_layout.addRow(self.semi_major_layout)
            initial_semi_minor = getattr(self.loop, 'b', 0.5)
            self.semi_minor_layout, self.semi_minor_input = self._create_spinbox_row(
                "短轴 b:", initial_semi_minor, min_val=0.1, max_val=10.0, step=0.1
            )
            self.main_form_layout.addRow(self.semi_minor_layout)
            initial_angular_direction = getattr(self.loop, 'angular_direction', 0.0)
            self.angular_direction_layout, self.angular_direction_input = self._create_spinbox_row(
                "角度方向:", initial_angular_direction, min_val=-180.0, max_val=180.0, step=1.0
            )
            self.main_form_layout.addRow(self.angular_direction_layout)
            self.color_button = QPushButton("选择颜色", self)
            self._loop_color_picked_color = self.loop.color
            self._set_button_color(self.color_button, self._loop_color_picked_color)
            self.color_button.clicked.connect(lambda: self._pick_color(self.color_button, '_loop_color_picked_color'))
            self.main_form_layout.addRow("环形线条颜色:", self.color_button)
            initial_linewidth = self.loop.linewidth
            self.linewidth_layout, self.linewidth_input = self._create_spinbox_row(
                "线宽:", initial_linewidth, min_val=0.1, max_val=10.0, step=0.1
            )
            self.main_form_layout.addRow(self.linewidth_layout)
            initial_alpha = self.loop.alpha
            self.alpha_layout, self.alpha_input = self._create_spinbox_row(
                "透明度:", initial_alpha, min_val=0.0, max_val=1.0, step=0.01
            )
            self.main_form_layout.addRow(self.alpha_layout)
            self.mpl_linestyle_combo = QComboBox(self)
            mpl_line_styles = ['-', '--', '-.', ':', 'None', ' ', '']
            for style_str in mpl_line_styles:
                self.mpl_linestyle_combo.addItem(style_str if style_str != '' else '(空)')
            current_mpl_ls = self.loop.linestyle if self.loop.linestyle is not None else '-'
            self.mpl_linestyle_combo.setCurrentText(current_mpl_ls if current_mpl_ls != '' else '(空)')
            self.main_form_layout.addRow("Matplotlib 线型:", self.mpl_linestyle_combo)
            initial_zorder = self.loop.zorder
            self.zorder_layout, self.zorder_input = self._create_spinbox_row(
                "Z轴顺序:", initial_zorder, min_val=-100, max_val=100, step=1, is_int=True
            )
            self.main_form_layout.addRow(self.zorder_layout)
            initial_label_fontsize = self.loop.label_fontsize
            self.label_fontsize_layout, self.label_fontsize_input = self._create_spinbox_row(
                "标签字体大小:", initial_label_fontsize, min_val=1.0, max_val=72.0, step=0.5, is_int=True
            )
            self.main_form_layout.addRow(self.label_fontsize_layout)
            self.label_color_button = QPushButton("选择颜色", self)
            self._label_color_picked_color = self.loop.label_color
            self._set_button_color(self.label_color_button, self._label_color_picked_color)
            self.label_color_button.clicked.connect(lambda: self._pick_color(self.label_color_button, '_label_color_picked_color'))
            self.main_form_layout.addRow("标签颜色:", self.label_color_button)
            self.label_ha_combo = QComboBox(self)
            self.label_ha_combo.addItems(['left', 'right', 'center'])
            self.label_ha_combo.setCurrentText(self.loop.label_ha)
            self.main_form_layout.addRow("标签水平对齐:", self.label_ha_combo)
            self.label_va_combo = QComboBox(self)
            self.label_va_combo.addItems(['top', 'bottom', 'center', 'baseline'])
            self.label_va_combo.setCurrentText(self.loop.label_va)
            self.main_form_layout.addRow("标签垂直对齐:", self.label_va_combo)
            label_offset_x = self.loop.label_offset[0]
            label_offset_y = self.loop.label_offset[1]
            self.label_offset_x_layout, self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
            self.label_offset_y_layout, self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
            self.main_form_layout.addRow(self.label_offset_x_layout)
            self.main_form_layout.addRow(self.label_offset_y_layout)

            # --- 特定环形线条类型的属性组 (由各自的编辑器管理) ---
            self.fermion_editor = FermionLoopEditor(self.main_form_layout, self.loop)
            self.photon_editor = PhotonLoopEditor(self.main_form_layout, self.loop)
            self.gluon_editor = GluonLoopEditor(self.main_form_layout, self.loop)
            self.wz_boson_editor = WZBosonLoopEditor(self.main_form_layout, self.loop)

            self.specific_editors = {
                FermionLine: self.fermion_editor,
                AntiFermionLine: self.fermion_editor,
                PhotonLine: self.photon_editor,
                GluonLine: self.gluon_editor,
                WPlusLine: self.wz_boson_editor,
                WMinusLine: self.wz_boson_editor,
                ZBosonLine: self.wz_boson_editor,
            }

            self.particle_type_combo.currentIndexChanged.connect(self._update_specific_properties_ui)
            self._update_specific_properties_ui(self.particle_type_combo.currentIndex())
            button_layout = QHBoxLayout()
            ok_button = QPushButton(self.tr("确定"))
            ok_button.clicked.connect(self.accept)
            cancel_button = QPushButton(self.tr("取消"))
            cancel_button.clicked.connect(self.reject)
            button_layout.addStretch(1)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            self.main_dialog_layout.addLayout(button_layout)

        def _update_specific_properties_ui(self, index: int):
            """隐藏所有特定属性编辑器，并只显示相关的那个。"""
            selected_class = self.particle_type_combo.itemData(index)
            for editor in set(self.specific_editors.values()):
                editor.set_visible(False)

            if selected_class in self.specific_editors:
                editor_to_show = self.specific_editors[selected_class]
                editor_to_show.loop = self.loop
                editor_to_show.set_visible(True)
                editor_to_show._load_properties()

        def accept(self):
            """当点击 OK 按钮时调用。更新 Loop 对象的属性。
            如果环形线条类型发生变化，将替换原始环形线条。
            """
            new_loop_id = self._current_loop_id_str
            selected_particle_class = self.particle_type_combo.currentData()

            common_kwargs = {
                'label': self.label_input.text(),
                'a': float(self.semi_major_input.value()),
                'b': float(self.semi_minor_input.value()),
                'angular_direction': float(self.angular_direction_input.value()),
                'label_offset': np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()]),
                'linewidth': float(self.linewidth_input.value()),
                'color': self._loop_color_picked_color,
                'linestyle': self.mpl_linestyle_combo.currentText() if self.mpl_linestyle_combo.currentText() != '(空)' else None,
                'alpha': float(self.alpha_input.value()),
                'zorder': int(self.zorder_input.value()),
                'label_fontsize': int(self.label_fontsize_input.value()),
                'label_color': self._label_color_picked_color,
                'label_ha': self.label_ha_combo.currentText(),
                'label_va': self.label_va_combo.currentText(),
                'loop': True,
            }

            specific_kwargs = {}
            if selected_particle_class in self.specific_editors:
                current_editor = self.specific_editors[selected_particle_class]
                specific_kwargs = current_editor.get_specific_kwargs()

            all_kwargs = {**common_kwargs, **specific_kwargs}
            
            # --- 环形线条类型发生变化时的处理逻辑 ---
            if type(self.loop) != selected_particle_class:
                self.diagram_model.remove_line(self._original_loop_id)
                new_loop_instance = selected_particle_class(
                    v_start=self._original_v_start,
                    v_end=self._original_v_end,
                    id=new_loop_id,
                    **all_kwargs
                )
                try:
                    self.diagram_model.add_line(line=new_loop_instance)
                    self.loop = new_loop_instance
                    QMessageBox.information(self, "操作成功", f"环形线条 {new_loop_id} 类型已更换并更新。")
                except ValueError as e:
                    QMessageBox.critical(self, "操作失败", str(e))
                    super().reject()
                    return
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"更新环形线条时发生未知错误: {e}")
                    super().reject()
                    return
            # --- 环形线条类型未变化时的处理逻辑 (编辑现有环形线条) ---
            else:
                self.loop.label = common_kwargs['label']
                self.loop.a = common_kwargs['a']
                self.loop.b = common_kwargs['b']
                self.loop.angular_direction = common_kwargs['angular_direction']
                self.loop.label_offset = common_kwargs['label_offset']
                self.loop.linewidth = common_kwargs['linewidth']
                self.loop.color = common_kwargs['color']
                self.loop.linestyle = common_kwargs['linestyle']
                self.loop.alpha = common_kwargs['alpha']
                self.loop.zorder = common_kwargs['zorder']
                self.loop.label_fontsize = common_kwargs['label_fontsize']
                self.loop.label_color = common_kwargs['label_color']
                self.loop.label_ha = common_kwargs['label_ha']
                self.loop.label_va = common_kwargs['label_va']
                self.loop.loop = common_kwargs['loop']

                if selected_particle_class in self.specific_editors:
                    current_editor = self.specific_editors[selected_particle_class]
                    current_editor.apply_properties(self.loop)
                QMessageBox.information(self, "操作成功", f"环形线条 {self.loop.id} 属性已更新。")

            super().accept()

    dialog = _InternalEditLoopDialog(loop, diagram_model=diagram_model, parent_dialog=parent_widget)
    if dialog.exec() == QDialog.Accepted:
        return True
    else:
        return False