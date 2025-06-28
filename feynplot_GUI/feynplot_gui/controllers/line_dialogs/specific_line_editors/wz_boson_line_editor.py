# feynplot_gui/controllers/line_dialogs/specific_line_editors/wz_boson_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QSizePolicy, QFormLayout
)
from feynplot.core.line import WPlusLine, WMinusLine, ZBosonLine
from feynplot_gui.controllers.line_dialogs.line_edit_base import LineEditBase

class WZBosonLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: (WPlusLine, WMinusLine, ZBosonLine)):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout

        # 初始化 GroupBox 并设置水平扩展策略
        self.group_box = QGroupBox(self.tr("W/Z 玻色子线属性"))
        self.group_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        # 设置 GroupBox 内部布局
        self.layout = QVBoxLayout(self.group_box)
        self.zigzag_amplitude_layout, self.zigzag_amplitude_input = \
            self._create_spinbox_row("折线振幅:", 0.2, min_val=0.0, max_val=1.0, step=0.01)
        self.zigzag_frequency_layout, self.zigzag_frequency_input = \
            self._create_spinbox_row("折线频率:", 2.0, min_val=0.1, max_val=10.0, step=0.1)

        self.layout.addLayout(self.zigzag_amplitude_layout)
        self.layout.addLayout(self.zigzag_frequency_layout)
        self.layout.addStretch(1)

        # 关键改动：直接添加 GroupBox 到父 QFormLayout 中（整行填满）
        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.group_box)

        self._load_properties()
        self.group_box.hide()  # 默认隐藏

    def _load_properties(self):
        self.zigzag_amplitude_input.setValue(self._get_value_or_default(self.line, 'zigzag_amplitude', 0.2, float))
        self.zigzag_frequency_input.setValue(self._get_value_or_default(self.line, 'zigzag_frequency', 2.0, float))

    def apply_properties(self, line: (WPlusLine, WMinusLine, ZBosonLine)):
        if isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            line.zigzag_amplitude = float(self.zigzag_amplitude_input.value())
            line.zigzag_frequency = float(self.zigzag_frequency_input.value())

    def get_specific_kwargs(self) -> dict:
        return {
            'zigzag_amplitude': float(self.zigzag_amplitude_input.value()),
            'zigzag_frequency': float(self.zigzag_frequency_input.value()),
        }

    def set_visible(self, visible: bool):
        self.group_box.setVisible(visible)
