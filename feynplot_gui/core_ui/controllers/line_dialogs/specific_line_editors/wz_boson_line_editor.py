# feynplot_gui/controllers/line_dialogs/specific_line_editors/wz_boson_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QSizePolicy, QFormLayout, QButtonGroup, QRadioButton, QLabel, QHBoxLayout
)
from feynplot.core.line import WPlusLine, WMinusLine, ZBosonLine
from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase

class WZBosonLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: (WPlusLine | WMinusLine | ZBosonLine)):
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


        self.wz_initial_phase_group = QButtonGroup(self.group_box) # Parent to group_box
        self.wz_initial_phase_0 = QRadioButton(self.tr("0°"))
        self.wz_initial_phase_180 = QRadioButton(self.tr("180°"))
        self.wz_initial_phase_group.addButton(self.wz_initial_phase_0, 0)
        self.wz_initial_phase_group.addButton(self.wz_initial_phase_180, 180)
        self.initial_phase_h_layout = QHBoxLayout()
        self.initial_phase_h_layout.addWidget(QLabel(self.tr("初相位:")))
        self.initial_phase_h_layout.addWidget(self.wz_initial_phase_0)
        self.initial_phase_h_layout.addWidget(self.wz_initial_phase_180)
        self.initial_phase_h_layout.addStretch(1) # 添加伸缩器以使单选按钮靠左对齐

        self.wz_final_phase_group = QButtonGroup(self.group_box) # Parent to group_box
        self.wz_final_phase_0 = QRadioButton(self.tr("0°"))
        self.wz_final_phase_180 = QRadioButton(self.tr("180°"))
        self.wz_final_phase_group.addButton(self.wz_final_phase_0, 0)
        self.wz_final_phase_group.addButton(self.wz_final_phase_180, 180)
        self.final_phase_h_layout = QHBoxLayout()
        self.final_phase_h_layout.addWidget(QLabel(self.tr("末相位:")))
        self.final_phase_h_layout.addWidget(self.wz_final_phase_0)
        self.final_phase_h_layout.addWidget(self.wz_final_phase_180)
        self.final_phase_h_layout.addStretch(1) # 添加伸缩器以使单选按钮靠左对齐

        self.layout.addLayout(self.zigzag_amplitude_layout)
        self.layout.addLayout(self.zigzag_frequency_layout)
        self.layout.addLayout(self.initial_phase_h_layout)
        self.layout.addLayout(self.final_phase_h_layout)
        self.layout.addStretch(1)

        # 关键改动：直接添加 GroupBox 到父 QFormLayout 中（整行填满）
        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.group_box)

        self._load_properties()
        self.group_box.hide()  # 默认隐藏

    def _load_properties(self):
        self.zigzag_amplitude_input.setValue(self._get_value_or_default(self.line, 'zigzag_amplitude', 0.2, float))
        self.zigzag_frequency_input.setValue(self._get_value_or_default(self.line, 'zigzag_frequency', 2.0, float))
        initial_phase = self._get_value_or_default(self.line, 'initial_phase', 0, int)
        if initial_phase == 0:
            self.wz_initial_phase_0.setChecked(True)
        else:
            self.wz_initial_phase_180.setChecked(True)
        final_phase = self._get_value_or_default(self.line, 'final_phase', 0, int)
        if final_phase == 0:
            self.wz_final_phase_0.setChecked(True)
        else:
            self.wz_final_phase_180.setChecked(True)
        # self.wz_initial_phase_0.setChecked(self.line.initial_phase == 0)
        # self.wz_initial_phase_180.setChecked(self.line.initial_phase == 180)
        # self.wz_final_phase_0.setChecked(self.line.final_phase == 0)
        # self.wz_final_phase_180.setChecked(self.line.final_phase == 180)

    def apply_properties(self, line: (WPlusLine | WMinusLine | ZBosonLine)):
        if isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            line.zigzag_amplitude = float(self.zigzag_amplitude_input.value())
            line.zigzag_frequency = float(self.zigzag_frequency_input.value())
            line.initial_phase = self.wz_initial_phase_group.checkedId()
            line.final_phase = self.wz_final_phase_group.checkedId()
        else:
            raise TypeError("传入的 line 对象必须是 WPlusLine, WMinusLine 或 ZBosonLine 的实例。")

    def get_specific_kwargs(self) -> dict:
        return {
            'zigzag_amplitude': float(self.zigzag_amplitude_input.value()),
            'zigzag_frequency': float(self.zigzag_frequency_input.value()),
            'initial_phase': self.wz_initial_phase_group.checkedId(),
            'final_phase': self.wz_final_phase_group.checkedId()
        }

    def set_visible(self, visible: bool):
        self.group_box.setVisible(visible)
