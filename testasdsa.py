# feynplot_gui/controllers/line_dialogs/specific_line_editors/fermion_line_editor.py

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QDoubleSpinBox, QSpinBox, QLabel, QHBoxLayout, QFormLayout # 增加了 QHBoxLayout, QFormLayout
from PySide6.QtCore import Qt # 引入 Qt 用于对齐
from feynplot.core.line import FermionLine # 导入线条类型

class FermionLineEditor:
    def __init__(self, parent_layout: QFormLayout, line_obj):
        self.parent_layout = parent_layout
        self.line = line_obj

        self.group_box = QGroupBox("费米子线属性")
        # 在 GroupBox 内部使用 QFormLayout 来组织费米子线的特定属性
        self.group_content_layout = QFormLayout(self.group_box)

        # --- 添加费米子线的特定控件 ---
        # 箭头大小 (arrow_size)
        initial_arrow_size = getattr(self.line, 'arrow_size', 0.15) if self.line else 0.15
        self.arrow_size_input = QDoubleSpinBox()
        self.arrow_size_input.setRange(0.01, 1.0)
        self.arrow_size_input.setSingleStep(0.01)
        self.arrow_size_input.setValue(initial_arrow_size)
        self.group_content_layout.addRow("箭头大小:", self.arrow_size_input)

        # 箭头数量 (num_arrows)
        initial_num_arrows = getattr(self.line, 'num_arrows', 1) if self.line else 1
        self.num_arrows_input = QSpinBox()
        self.num_arrows_input.setRange(0, 5) # 0 for no arrows
        self.num_arrows_input.setValue(initial_num_arrows)
        self.group_content_layout.addRow("箭头数量:", self.num_arrows_input)

        # ... 可以继续添加其他费米子线特有的属性控件

        # 创建一个 QHBoxLayout 来包裹 GroupBox，并强制其靠左对齐
        self.wrapper_layout = QHBoxLayout()
        self.wrapper_layout.addWidget(self.group_box)
        self.wrapper_layout.addStretch(1) # 添加伸缩器，强制 group_box 靠左

        # 将这个包装布局添加到父 QFormLayout 的一个新行中
        # 这种方式可以将整个 GroupBox 作为一个“字段”添加到 QFormLayout，
        # 并通过 wrapper_layout 确保其水平对齐。
        self.form_row_index = self.parent_layout.rowCount() # 获取当前行数
        self.parent_layout.insertRow(self.form_row_index, self.wrapper_layout)


        self.group_box.hide() # 默认隐藏

    def _load_properties(self):
        """从 self.line 对象加载属性到 UI 控件."""
        # 确保在加载属性前 self.line 已经被更新为正确的线条实例
        if self.line:
            self.arrow_size_input.setValue(getattr(self.line, 'arrow_size', 0.15))
            self.num_arrows_input.setValue(getattr(self.line, 'num_arrows', 1))

    def get_specific_kwargs(self) -> dict:
        """从 UI 控件获取特定属性作为 kwargs."""
        return {
            'arrow_size': self.arrow_size_input.value(),
            'num_arrows': self.num_arrows_input.value(),
        }

    def apply_properties(self, line: FermionLine):
        """将 UI 控件的值应用到 Line 对象."""
        if isinstance(line, FermionLine): # 确保类型匹配
            line.arrow_size = self.arrow_size_input.value()
            line.num_arrows = self.num_arrows_input.value()

    def set_visible(self, visible: bool):
        """设置特定属性组的可见性."""
        self.group_box.setVisible(visible)
        # 控制 wrapper_layout 所在行的可见性 (需要通过 parent_layout)
        # 这通常由 QFormLayout 自动处理，但为了明确，可以这样：
        # 如果 parent_layout 支持逐行隐藏/显示，这会更复杂。
        # 简单起见，仅控制 group_box 的可见性即可。