from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QCheckBox, QHBoxLayout,
    QFormLayout, QSizePolicy, QWidget, QPushButton, QLabel
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from feynplot.core.line import FermionLine, AntiFermionLine, Line
from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase
from typing import Optional
from feynplot.core.line import Line

class HollowLineEditor(LineEditBase):
    def __init__(self, parent_layout: QFormLayout, line_obj: Optional[Line]):
        super().__init__()
        self.line = line_obj
        self.parent_form_layout = parent_layout
        
        # 将 QDialog 的引用保存在 self._dialog_parent 中，以便 _pick_color 方法使用
        self._dialog_parent = self.parent_form_layout.parentWidget()

        # 创建 GroupBox 并设置横向填充策略
        self.group_box = QGroupBox(self.tr("空心线属性"))
        self.group_box.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )

        self.layout = QVBoxLayout(self.group_box)

        # 创建 UI 元素
        self.inner_linewidth_layout, self.inner_linewidth_input = \
            self._create_spinbox_row("内线宽度:", 1.0, min_val=0.1, max_val=10.0, step=0.1)
        
        # --- 手动创建内线颜色按钮 ---
        self.inner_color_button = QPushButton("选择颜色")
        self._inner_color_picked_color = self._get_value_or_default(self.line, 'inner_color', '#FFFFFF', target_type=str)
        self._set_button_color(self.inner_color_button, self._inner_color_picked_color)
        self.inner_color_button.clicked.connect(lambda: self._pick_color(self.inner_color_button, '_inner_color_picked_color', parent=self._dialog_parent))
        self.inner_color_layout = QHBoxLayout()
        self.inner_color_layout.addWidget(QLabel("内线颜色:"))
        self.inner_color_layout.addWidget(self.inner_color_button)

        self.outer_linewidth_layout, self.outer_linewidth_input = \
            self._create_spinbox_row("外线宽度:", 1.0, min_val=0.1, max_val=10.0, step=0.1) 
        
        # --- 手动创建外线颜色按钮 ---
        self.outer_color_button = QPushButton("选择颜色")
        self._outer_color_picked_color = self._get_value_or_default(self.line, 'outer_color', '#000000', target_type=str)
        self._set_button_color(self.outer_color_button, self._outer_color_picked_color)
        self.outer_color_button.clicked.connect(lambda: self._pick_color(self.outer_color_button, '_outer_color_picked_color', parent=self._dialog_parent))
        self.outer_color_layout = QHBoxLayout()
        self.outer_color_layout.addWidget(QLabel("外线颜色:"))
        self.outer_color_layout.addWidget(self.outer_color_button)

        self.inner_zorder_layout, self.inner_zorder_input = \
            self._create_spinbox_row("内线 Z-order:", 5, min_val=0, max_val=100, step=1, is_int=True)
        self.outer_zorder_layout, self.outer_zorder_input = \
            self._create_spinbox_row("外线 Z-order:", 4, min_val=0, max_val=100, step=1, is_int=True)
        
        self.layout.addLayout(self.inner_linewidth_layout)
        self.layout.addLayout(self.inner_color_layout)
        self.layout.addLayout(self.outer_linewidth_layout)
        self.layout.addLayout(self.outer_color_layout)
        self.layout.addLayout(self.inner_zorder_layout)
        self.layout.addLayout(self.outer_zorder_layout)
        self.layout.addStretch(1)

        self.wrapper_widget = QWidget()
        wrapper_layout = QHBoxLayout()
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self.group_box)
        self.wrapper_widget.setLayout(wrapper_layout)

        self.row_index = self.parent_form_layout.rowCount()
        self.parent_form_layout.insertRow(self.row_index, self.wrapper_widget)

        self._load_properties()
        self.group_box.hide()


    def _load_properties(self):
        """将 line 对象中的属性加载到 UI 元素中。"""
        if not self.line:
            return
        self.inner_linewidth_input.setValue(self._get_value_or_default(self.line, 'inner_linewidth', 1.0, float))
        print(f"DEBUG : {self._get_value_or_default(self.line, 'inner_linewidth', 1.0, float)}")
        print(f"DEBUG : {self.line.inner_linewidth}")
        self._inner_color_picked_color = self._get_value_or_default(self.line, 'inner_color', '#FFFFFF', str)
        self._set_button_color(self.inner_color_button, self._inner_color_picked_color)
        self.outer_linewidth_input.setValue(self._get_value_or_default(self.line, 'outer_linewidth', 1.0, float))
        self._outer_color_picked_color = self._get_value_or_default(self.line, 'outer_color', '#000000', str)
        self._set_button_color(self.outer_color_button, self._outer_color_picked_color)
        self.inner_zorder_input.setValue(self._get_value_or_default(self.line, 'inner_zorder', 5, int))
        self.outer_zorder_input.setValue(self._get_value_or_default(self.line, 'outer_zorder', 4, int))


    def apply_properties(self, line: Line):
        if self.line.linestyle.lower() != 'hollow':
            return
        else:
            """将 UI 值应用到给定的 line 对象。"""
            prop_dict = self.get_specific_kwargs()
            for key, value in prop_dict.items():
                if hasattr(line, key):
                    # print(f"DEBUG: Applying {key} = {value} to line {line.id}")
                    setattr(line, key, value)
                    # print(f"DEBUG: {key} applied, current value is {getattr(line, key)}")
                else:
                    print(f"警告:空心线属性 '{key}'应用失败 ")
            # 您的代码中有一个 else 分支，但没有对应的 if。这里修正一下。
            # 正确的逻辑应该是：如果属性不存在，则发出警告。
            if not all(hasattr(line, key) for key in prop_dict.keys()):
                print(f"警告：尝试将空心线属性应用于非空心线对象: {type(line)}")
                return False
            return True

    def get_specific_kwargs(self) -> dict:
        """返回用于创建线条的特定关键字参数字典。"""
        specific_kwargs = {
            'inner_linewidth': float(self.inner_linewidth_input.value()),
            'inner_color': self._inner_color_picked_color,
            'outer_linewidth': float(self.outer_linewidth_input.value()),
            'outer_color': self._outer_color_picked_color,
            'inner_zorder': int(self.inner_zorder_input.value()),
            'outer_zorder': int(self.outer_zorder_input.value()),
        }
        return specific_kwargs