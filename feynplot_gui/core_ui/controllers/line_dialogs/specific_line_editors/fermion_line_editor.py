# feynplot_gui/controllers/line_dialogs/specific_line_editors/fermion_line_editor.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox, QHBoxLayout,
    QFormLayout, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt
from feynplot.core.line import FermionLine, AntiFermionLine
from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase


class FermionLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: FermionLine):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout

        # 创建 GroupBox 并设置横向填充策略
        self.group_box = QGroupBox(self.tr("费米子/反费米子线属性"))
        self.group_box.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )

        # 设置 GroupBox 内部垂直布局
        self.layout = QVBoxLayout(self.group_box)

        # 创建 UI 元素
        self.fermion_arrow_checkbox = QCheckBox(self.tr("显示箭头"))
        self.fermion_arrow_filled_checkbox = QCheckBox(self.tr("箭头填充"))
        self.fermion_arrow_position_layout, self.fermion_arrow_position_input = \
            self._create_spinbox_row("箭头位置 (0-1):", 0.5, min_val=0.0, max_val=1.0, step=0.01)
        self.fermion_arrow_size_layout, self.fermion_arrow_size_input = \
            self._create_spinbox_row("箭头大小:", 50.0, min_val=0.0, max_val=9999.0, step=1.0, is_int=True)
        self.fermion_arrow_line_width_layout, self.fermion_arrow_line_width_input = \
            self._create_spinbox_row("箭头线宽:", 1.0, min_val=0.1, max_val=10.0, step=0.1)
        self.fermion_arrow_reversed_checkbox = QCheckBox(self.tr("箭头反向"))

        # 添加组件到 GroupBox 内部布局
        self.layout.addWidget(self.fermion_arrow_checkbox)
        self.layout.addWidget(self.fermion_arrow_filled_checkbox)
        self.layout.addLayout(self.fermion_arrow_position_layout)
        self.layout.addLayout(self.fermion_arrow_size_layout)
        self.layout.addLayout(self.fermion_arrow_line_width_layout)
        self.layout.addWidget(self.fermion_arrow_reversed_checkbox)
        self.layout.addStretch(1)  # 顶部对齐

        # --- 创建包装 QWidget 以插入 QFormLayout 的一整行 ---
        self.wrapper_widget = QWidget()
        wrapper_layout = QHBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self.group_box)
        self.wrapper_widget.setLayout(wrapper_layout)

        # 插入到 QFormLayout 的一整行中
        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.wrapper_widget)

        self._load_properties()
        self.group_box.hide()

    def _load_properties(self):
        """将 line 对象中的属性加载到 UI 元素中。"""
        self.fermion_arrow_checkbox.setChecked(self._get_value_or_default(self.line, 'arrow', True, bool))
        self.fermion_arrow_filled_checkbox.setChecked(self._get_value_or_default(self.line, 'arrow_filled', False, bool))
        self.fermion_arrow_position_input.setValue(self._get_value_or_default(self.line, 'arrow_position', 0.5, float))
        self.fermion_arrow_size_input.setValue(self._get_value_or_default(self.line, 'mutation_scale', 10.0, float))
        self.fermion_arrow_line_width_input.setValue(self._get_value_or_default(self.line, 'arrow_line_width', 1.0, float))
        self.fermion_arrow_reversed_checkbox.setChecked(self._get_value_or_default(self.line, 'arrow_reversed', False, bool))

    def apply_properties(self, line: FermionLine):
        """将 UI 值应用到给定的 line 对象。"""
        if isinstance(line, (FermionLine, AntiFermionLine)):
            line.arrow = self.fermion_arrow_checkbox.isChecked()
            line.arrow_filled = self.fermion_arrow_filled_checkbox.isChecked()
            line.arrow_position = float(self.fermion_arrow_position_input.value())
            line.mutation_scale = float(self.fermion_arrow_size_input.value())
            line.arrow_line_width = float(self.fermion_arrow_line_width_input.value())
            line.arrow_reversed = self.fermion_arrow_reversed_checkbox.isChecked()
        else:
            print(f"警告：尝试将费米子线属性应用于非费米子线对象: {type(line)}")

    def get_specific_kwargs(self) -> dict:
        """返回用于创建线条的特定关键字参数字典。"""
        specific_kwargs = {
            'arrow': self.fermion_arrow_checkbox.isChecked(),
            'arrow_filled': self.fermion_arrow_filled_checkbox.isChecked(),
            'arrow_position': float(self.fermion_arrow_position_input.value()),
            'mutation_scale': float(self.fermion_arrow_size_input.value()),
            'arrow_line_width': float(self.fermion_arrow_line_width_input.value()),
            'arrow_reversed': self.fermion_arrow_reversed_checkbox.isChecked(),
        }
        print(f"获取特定关键字参数: {specific_kwargs}")
        return specific_kwargs

    def set_visible(self, visible: bool):
        """设置特定属性组的可见性。"""
        self.group_box.setVisible(visible)
