# feynplot_gui/controllers/line_dialogs/specific_line_editors/gluon_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt
from feynplot.core.line import GluonLine
from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase
from feynplot_gui.debug_utils import cout

class GluonLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: GluonLine):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout

        self.group_box = QGroupBox(self.tr("胶子线属性"))
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
            self._create_spinbox_row("周期数 (N_Cycles):", 18, min_val=0.5, max_val=100, step=0.5, is_int=False)

        # 绕向：逆时针 / 顺时针（沿路径方向看）
        self.winding_combo = QComboBox()
        self.winding_combo.addItems([self.tr("逆时针"), self.tr("顺时针")])

        # 扁率：控制圈圈“压扁”程度（1.0 圆形；0.5 更扁；2.0 更高）
        self.squash_ratio_layout, self.squash_ratio_input = \
            self._create_spinbox_row("扁率 (Squash):", 1.0, min_val=0.1, max_val=3.0, step=0.05, is_int=False)

        # 开始/终止直线比例（UI 保留，当前螺旋算法未使用）
        self.start_straight_layout, self.start_straight_input = \
            self._create_spinbox_row(self.tr("开始直线比例:"), 0.0, min_val=0.0, max_val=1.0, step=0.05, is_int=False)
        self.end_straight_layout, self.end_straight_input = \
            self._create_spinbox_row(self.tr("终止直线比例:"), 0.0, min_val=0.0, max_val=1.0, step=0.05, is_int=False)

        self.layout.addLayout(self.amplitude_layout)
        self.layout.addLayout(self.n_cycles_layout)
        self.layout.addLayout(self._wrap_row(self.tr("绕向:"), self.winding_combo))
        self.layout.addLayout(self.squash_ratio_layout)
        self.layout.addLayout(self.start_straight_layout)
        self.layout.addLayout(self.end_straight_layout)
        self.layout.addStretch(1)

        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.group_box)

        self._load_properties()
        self.group_box.hide()

    def _wrap_row(self, label: str, widget):
        row = QHBoxLayout()
        row.addWidget(self.tr_widget(label))
        row.addWidget(widget)
        return row

    def tr_widget(self, text: str):
        from PySide6.QtWidgets import QLabel
        return QLabel(self.tr(text))

    def _load_properties(self):
        """将 line 对象中的属性加载到 UI 元素中。"""
        # 修正：确保这里的默认值也与创建 SpinBox 时保持一致，即 0.15
        self.amplitude_input.setValue(self._get_value_or_default(self.line, 'amplitude', 0.18, float))
        self.n_cycles_input.setValue(self._get_value_or_default(self.line, 'n_cycles', 18, float))

        clockwise = self._get_value_or_default(self.line, 'clockwise', False, bool)
        self.winding_combo.setCurrentText(self.tr("顺时针") if clockwise else self.tr("逆时针"))
        self.squash_ratio_input.setValue(self._get_value_or_default(self.line, 'squash_ratio', 1.0, float))
        self.start_straight_input.setValue(self._get_value_or_default(self.line, 'start_straight_ratio', 0.0, float))
        self.end_straight_input.setValue(self._get_value_or_default(self.line, 'end_straight_ratio', 0.0, float))

    def apply_properties(self, line: GluonLine):
        """将 UI 值应用到给定的 line 对象。"""
        if isinstance(line, GluonLine):
            line.amplitude = float(self.amplitude_input.value())
            line.n_cycles = float(self.n_cycles_input.value())
            line.clockwise = (self.winding_combo.currentText() == self.tr("顺时针"))
            line.squash_ratio = float(self.squash_ratio_input.value())
            line.start_straight_ratio = float(self.start_straight_input.value())
            line.end_straight_ratio = float(self.end_straight_input.value())
        else:
            cout(f"警告：尝试将 GluonLine 属性应用于非 GluonLine 对象: {type(line)}")

    def get_specific_kwargs(self) -> dict:
        """返回用于创建线条的特定关键字参数字典。"""
        return {
            'amplitude': float(self.amplitude_input.value()),
            'n_cycles': float(self.n_cycles_input.value()),
            'clockwise': (self.winding_combo.currentText() == self.tr("顺时针")),
            'squash_ratio': float(self.squash_ratio_input.value()),
            'start_straight_ratio': float(self.start_straight_input.value()),
            'end_straight_ratio': float(self.end_straight_input.value()),
        }

    def set_visible(self, visible: bool):
        """设置特定属性组的可见性。"""
        self.group_box.setVisible(visible)