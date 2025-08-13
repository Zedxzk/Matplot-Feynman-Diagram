# feynplot_gui/core_ui/controllers/line_dialogs/specific_line_editors/loop_editors.py

from PySide6.QtWidgets import (
    QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox, QHBoxLayout, QLabel, QWidget
)
from PySide6.QtCore import Qt
import numpy as np
from typing import Tuple

from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase

# 导入所有可能成为自环的线条类型
from feynplot.core.line import Line, FermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine

class LoopEditor(LineEditBase):
    """
    一个通用的自环编辑器，它包含所有自环共有的属性，
    并根据其内部线条类型（FermionLine, PhotonLine等）动态显示特定属性。
    它不保存 Line 对象的状态，而是通过方法参数接收 Line 对象。
    """
    def __init__(self, parent_layout: QFormLayout):
        super().__init__()
        # self.line = line_obj  <-- 移除此行
        self.parent_layout = parent_layout
        
        self.all_widgets = []
        self.fermion_loop_widgets = []
        self.wz_loop_widgets = []
        self.photon_loop_widgets = []
        self.gluon_loop_widgets = []
        
        # --- 通用自环属性控件 ---
        # 椭圆中心偏移
        self.center_x_container, self.center_x_input = self._create_spinbox_container(
            "中心偏移 X:", 0.0, min_val=-50.0, max_val=50.0, step=0.1
        )
        self.center_y_container, self.center_y_input = self._create_spinbox_container(
            "中心偏移 Y:", 0.0, min_val=-50.0, max_val=50.0, step=0.1
        )

        # 长短半轴
        self.major_axis_container, self.major_axis_input = self._create_spinbox_container(
            "长半轴 (a):", 1.0, min_val=0.1, max_val=50.0, step=0.1
        )
        self.minor_axis_container, self.minor_axis_input = self._create_spinbox_container(
            "短半轴 (b):", 1.0, min_val=0.1, max_val=50.0, step=0.1
        )

        # 旋转角度
        self.rotation_container, self.rotation_input = self._create_spinbox_container(
            "旋转角度:", 0.0, min_val=-360.0, max_val=360.0, step=1.0
        )
        
        # 将通用自环属性的容器添加到布局和总列表中
        self.parent_layout.addRow(self.center_x_container)
        self.parent_layout.addRow(self.center_y_container)
        self.parent_layout.addRow(self.major_axis_container)
        self.parent_layout.addRow(self.minor_axis_container)
        self.parent_layout.addRow(self.rotation_container)
        
        self.all_widgets.extend([
            self.center_x_container, self.center_y_container,
            self.major_axis_container, self.minor_axis_container,
            self.rotation_container
        ])

        # --- 特定粒子类型属性控件 ---
        # 费米子自环特有控件
        self.arrow_position_container, self.arrow_position_input = self._create_spinbox_container(
            "箭头位置:", 0.5, min_val=0.0, max_val=1.0, step=0.01
        )
        self.parent_layout.addRow(self.arrow_position_container)
        self.fermion_loop_widgets.append(self.arrow_position_container)

        # WZ 玻色子自环特有控件
        self.dash_length_container, self.dash_length_input = self._create_spinbox_container(
            "虚线长度:", 0.2, min_val=0.01, max_val=1.0, step=0.01
        )
        self.gap_length_container, self.gap_length_input = self._create_spinbox_container(
            "间隙长度:", 0.1, min_val=0.01, max_val=1.0, step=0.01
        )
        self.parent_layout.addRow(self.dash_length_container)
        self.parent_layout.addRow(self.gap_length_container)
        self.wz_loop_widgets.extend([self.dash_length_container, self.gap_length_container])
        
        # 光子自环特有控件 (波浪线圈数和半径)
        self.loops_container, self.loops_input = self._create_spinbox_container(
            "环的圈数 (Loops):", 2, min_val=0, max_val=10, step=1, is_int=True
        )
        self.loop_radius_container, self.loop_radius_input = self._create_spinbox_container(
            "环的半径 (Radius):", 0.5, min_val=0.1, max_val=5.0, step=0.1
        )
        self.parent_layout.addRow(self.loops_container)
        self.parent_layout.addRow(self.loop_radius_container)
        self.photon_loop_widgets.extend([self.loops_container, self.loop_radius_input])

        # 胶子自环特有控件 (双线偏移)
        self.double_line_offset_container, self.double_line_offset_input = self._create_spinbox_container(
            "双线偏移 (Offset):", 0.1, min_val=0.01, max_val=1.0, step=0.01
        )
        self.parent_layout.addRow(self.double_line_offset_container)
        self.gluon_loop_widgets.append(self.double_line_offset_container)

        self.all_widgets.extend(self.fermion_loop_widgets)
        self.all_widgets.extend(self.wz_loop_widgets)
        self.all_widgets.extend(self.photon_loop_widgets)
        self.all_widgets.extend(self.gluon_loop_widgets)
        
        self.set_visible(False) # 默认隐藏

    def _create_spinbox_container(self, label_text: str, default_value: float, **kwargs) -> Tuple[QWidget, QDoubleSpinBox | QSpinBox]:
        """
        创建一个包含标签和输入框的 QWidget 容器，返回容器和输入框。
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        spinbox = QDoubleSpinBox() if not kwargs.get('is_int') else QSpinBox()
        spinbox.setRange(kwargs.get('min_val', -np.inf), kwargs.get('max_val', np.inf))
        spinbox.setSingleStep(kwargs.get('step', 1.0))
        spinbox.setValue(default_value)
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        
        return container, spinbox

    def set_visible(self, visible: bool):
        """
        根据传入的布尔值显示或隐藏所有控件容器。
        """
        for widget_container in self.all_widgets:
            widget_container.setVisible(visible)

    def _load_properties(self, line: Line): # <-- 关键改变：现在接受 line 参数
        """
        从传入的 line 对象加载通用和特定属性到 UI 控件。
        """
        if not line:
            return

        # 隐藏所有特定控件
        for widgets in [self.fermion_loop_widgets, self.wz_loop_widgets, self.photon_loop_widgets, self.gluon_loop_widgets]:
            for widget in widgets:
                widget.setVisible(False)
        
        # 加载通用自环属性
        self.center_x_input.setValue(line.center_offset[0])
        self.center_y_input.setValue(line.center_offset[1])
        self.major_axis_input.setValue(line.a)
        self.minor_axis_input.setValue(line.b)
        self.rotation_input.setValue(line.angular_direction)

        # 加载特定粒子类型属性并显示相应的控件
        if isinstance(line, FermionLine):
            self.arrow_position_input.setValue(line.arrow_position)
            for widget in self.fermion_loop_widgets:
                widget.setVisible(True)
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            self.dash_length_input.setValue(line.dash_length)
            self.gap_length_input.setValue(line.gap_length)
            for widget in self.wz_loop_widgets:
                widget.setVisible(True)
        elif isinstance(line, PhotonLine):
            self.loops_input.setValue(line.loops)
            self.loop_radius_input.setValue(line.loop_radius)
            for widget in self.photon_loop_widgets:
                widget.setVisible(True)
        elif isinstance(line, GluonLine):
            self.double_line_offset_input.setValue(line.double_line_offset)
            for widget in self.gluon_loop_widgets:
                widget.setVisible(True)

    def get_specific_kwargs(self, line: Line): # <-- 关键改变：现在接受 line 参数
        """
        从 UI 控件获取所有特定于自环的属性，并返回一个字典。
        """
        kwargs = {
            'center_offset': np.array([self.center_x_input.value(), self.center_y_input.value()]),
            'major_axis': self.major_axis_input.value(),
            'minor_axis': self.minor_axis_input.value(),
            'rotation': self.rotation_input.value(),
        }
        
        # 添加特定粒子类型的属性
        if isinstance(line, FermionLine):
            kwargs['arrow_position'] = self.arrow_position_input.value()
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            kwargs['dash_length'] = self.dash_length_input.value()
            kwargs['gap_length'] = self.gap_length_input.value()
        elif isinstance(line, PhotonLine):
            kwargs['loops'] = self.loops_input.value()
            kwargs['loop_radius'] = self.loop_radius_input.value()
        elif isinstance(line, GluonLine):
            kwargs['double_line_offset'] = self.double_line_offset_input.value()

        return kwargs

    def apply_properties(self, line: Line): # <-- 关键改变：现在接受 line 参数
        """
        将 UI 控件中的值直接应用到传入的 line 对象上。
        """
        if not line:
            return

        # 应用通用自环属性
        line.center_offset = np.array([self.center_x_input.value(), self.center_y_input.value()])
        line.major_axis = self.major_axis_input.value()
        line.minor_axis = self.minor_axis_input.value()
        line.rotation = self.rotation_input.value()

        # 应用特定粒子类型的属性
        if isinstance(line, FermionLine):
            line.arrow_position = self.arrow_position_input.value()
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            line.dash_length = self.dash_length_input.value()
            line.gap_length = self.gap_length_input.value()
        elif isinstance(line, PhotonLine):
            line.loops = self.loops_input.value()
            line.loop_radius = self.loop_radius_input.value()
        elif isinstance(line, GluonLine):
            line.double_line_offset = self.double_line_offset_input.value()