# feynplot_gui/controllers/line_dialogs/specific_line_editors/gluon_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt
from feynplot.core.line import GluonLine
from feynplot_gui.controllers.line_dialogs.line_edit_base import LineEditBase

class GluonLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: GluonLine):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout

        self.group_box = QGroupBox("胶子线属性")
        self.group_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        self.layout = QVBoxLayout(self.group_box)

        # 振幅 (Amplitude)，默认值 0.15
        self.amplitude_layout, self.amplitude_input = \
            self._create_spinbox_row("振幅 (Amplitude):", 0.15, min_val=0.0, max_val=1.0, step=0.01)
        
        # 周期数 (N_Cycles)，默认值 16，整数类型
        self.n_cycles_layout, self.n_cycles_input = \
            self._create_spinbox_row("周期数 (N_Cycles):", 18, min_val=1, max_val=100, step=1, is_int=True)
        
        self.layout.addLayout(self.amplitude_layout)
        self.layout.addLayout(self.n_cycles_layout)
        self.layout.addStretch(1)

        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.group_box)

        self._load_properties()
        self.group_box.hide()

    def _load_properties(self):
        """将 line 对象中的属性加载到 UI 元素中。"""
        # 修正：确保这里的默认值也与创建 SpinBox 时保持一致，即 0.15
        self.amplitude_input.setValue(self._get_value_or_default(self.line, 'amplitude', 0.18, float))
        self.n_cycles_input.setValue(self._get_value_or_default(self.line, 'n_cycles', 18, int))

    def apply_properties(self, line: GluonLine):
        """将 UI 值应用到给定的 line 对象。"""
        if isinstance(line, GluonLine):
            line.amplitude = float(self.amplitude_input.value())
            line.n_cycles = int(self.n_cycles_input.value())
        else:
            print(f"警告：尝试将 GluonLine 属性应用于非 GluonLine 对象: {type(line)}")

    def get_specific_kwargs(self) -> dict:
        """返回用于创建线条的特定关键字参数字典。"""
        return {
            'amplitude': float(self.amplitude_input.value()),
            'n_cycles': int(self.n_cycles_input.value()),
        }

    def set_visible(self, visible: bool):
        """设置特定属性组的可见性。"""
        self.group_box.setVisible(visible)