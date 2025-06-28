# feynplot_gui/controllers/line_dialogs/specific_line_editors/photon_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QSizePolicy, QFormLayout # 导入 QSizePolicy 和 QFormLayout
)
from PySide6.QtCore import Qt # 导入 Qt
from feynplot.core.line import PhotonLine
from feynplot_gui.controllers.line_dialogs.line_edit_base import LineEditBase

class PhotonLineEditor(LineEditBase):
    # 将 parent_layout 类型提示更改为 QFormLayout，与 edit_line.py 传递的类型一致
    def __init__(self, parent_layout: QFormLayout, line_obj: PhotonLine):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout # 存储父级 QFormLayout

        self.group_box = QGroupBox("光子线属性")
        # --- 关键更改：设置 QGroupBox 的 sizePolicy 为水平 Expanding ---
        self.group_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,   # 水平方向应扩展
            QSizePolicy.Policy.Preferred    # 垂直方向保持首选大小
        )
        # 如果需要 GroupBox 内部的 padding 最小化，可以设置样式，但这通常由 GroupBox 默认处理
        # self.group_box.setStyleSheet("QGroupBox { padding: 5px; }") # 示例，可根据需要调整

        self.layout = QVBoxLayout(self.group_box) # 这是 GroupBox 内部内容的主布局

        self.photon_amplitude_layout, self.photon_amplitude_input = \
            self._create_spinbox_row("振幅:", 0.1, min_val=0.01, max_val=1.0, step=0.01)
        self.photon_wavelength_layout, self.photon_wavelength_input = \
            self._create_spinbox_row("波长:", 0.5, min_val=0.1, max_val=2.0, step=0.05)

        self.photon_initial_phase_group = QButtonGroup(self.group_box) # Parent to group_box
        self.photon_initial_phase_0 = QRadioButton("0°")
        self.photon_initial_phase_180 = QRadioButton("180°")
        self.photon_initial_phase_group.addButton(self.photon_initial_phase_0, 0)
        self.photon_initial_phase_group.addButton(self.photon_initial_phase_180, 180)
        self.initial_phase_h_layout = QHBoxLayout()
        self.initial_phase_h_layout.addWidget(QLabel("初相位:"))
        self.initial_phase_h_layout.addWidget(self.photon_initial_phase_0)
        self.initial_phase_h_layout.addWidget(self.photon_initial_phase_180)
        self.initial_phase_h_layout.addStretch(1) # 添加伸缩器以使单选按钮靠左对齐

        self.photon_final_phase_group = QButtonGroup(self.group_box) # Parent to group_box
        self.photon_final_phase_0 = QRadioButton("0°")
        self.photon_final_phase_180 = QRadioButton("180°")
        self.photon_final_phase_group.addButton(self.photon_final_phase_0, 0)
        self.photon_final_phase_group.addButton(self.photon_final_phase_180, 180)
        self.final_phase_h_layout = QHBoxLayout()
        self.final_phase_h_layout.addWidget(QLabel("末相位:"))
        self.final_phase_h_layout.addWidget(self.photon_final_phase_0)
        self.final_phase_h_layout.addWidget(self.photon_final_phase_180)
        self.final_phase_h_layout.addStretch(1) # 添加伸缩器以使单选按钮靠左对齐

        # 将内部布局添加到 GroupBox 的主内部布局中
        self.layout.addLayout(self.photon_amplitude_layout)
        self.layout.addLayout(self.photon_wavelength_layout)
        self.layout.addLayout(self.initial_phase_h_layout)
        self.layout.addLayout(self.final_phase_h_layout)
        self.layout.addStretch(1) # 在内部布局底部添加伸缩器，将内容推到顶部

        # --- 关键改动：直接添加 GroupBox 到父 QFormLayout 中（整行填满）---
        self.row_index = self.parent_form_layout.rowCount() # 获取当前行数以插入到末尾
        self.parent_form_layout.insertRow(self.row_index, self.group_box)


        self._load_properties() # 加载初始值
        self.group_box.hide() # 默认隐藏

    def _load_properties(self):
        """将 line 对象中的属性加载到 UI 元素中。"""
        self.photon_amplitude_input.setValue(self._get_value_or_default(self.line, 'amplitude', 0.1, float))
        self.photon_wavelength_input.setValue(self._get_value_or_default(self.line, 'wavelength', 0.5, float))

        initial_phase = self._get_value_or_default(self.line, 'initial_phase', 0, int)
        if initial_phase == 0:
            self.photon_initial_phase_0.setChecked(True)
        else:
            self.photon_initial_phase_180.setChecked(True)

        final_phase = self._get_value_or_default(self.line, 'final_phase', 0, int)
        if final_phase == 0:
            self.photon_final_phase_0.setChecked(True)
        else:
            self.photon_final_phase_180.setChecked(True)

    def apply_properties(self, line: PhotonLine):
        """将 UI 值应用到给定的 line 对象。"""
        if isinstance(line, PhotonLine):
            line.amplitude = float(self.photon_amplitude_input.value())
            line.wavelength = float(self.photon_wavelength_input.value())
            line.initial_phase = int(self.photon_initial_phase_group.checkedId())
            line.final_phase = int(self.photon_final_phase_group.checkedId())
        else:
            print(f"警告：尝试将 PhotonLine 属性应用于非 PhotonLine 对象: {type(line)}")


    def get_specific_kwargs(self) -> dict:
        """返回用于创建线条的特定关键字参数字典。"""
        return {
            'amplitude': float(self.photon_amplitude_input.value()),
            'wavelength': float(self.photon_wavelength_input.value()),
            'initial_phase': int(self.photon_initial_phase_group.checkedId()),
            'final_phase': int(self.photon_final_phase_group.checkedId()),
        }

    def set_visible(self, visible: bool):
        """设置特定属性组的可见性。"""
        self.group_box.setVisible(visible)