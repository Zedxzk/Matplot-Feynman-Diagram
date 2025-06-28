# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_axes_ticks_settings_panel.py

from PySide6.QtWidgets import QWidget, QComboBox, QCheckBox
from PySide6.QtCore import Qt # 导入Qt用于Qt.MatchFixedString
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox # 从同级目录导入

class AxesTicksSettingsPanel(CollapsibleGroupBox):
    """
    轴与刻度设置面板。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("轴与刻度设置", parent)

        self.axes_labelsize_combo = QComboBox()
        self.axes_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.axes_labelsize_combo.setEditable(True)
        self.content_layout().addRow("轴标签大小:", self.axes_labelsize_combo)

        self.xtick_labelsize_combo = QComboBox()
        self.xtick_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.xtick_labelsize_combo.setEditable(True)
        self.content_layout().addRow("X轴刻度标签大小:", self.xtick_labelsize_combo)

        self.ytick_labelsize_combo = QComboBox()
        self.ytick_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.ytick_labelsize_combo.setEditable(True)
        self.content_layout().addRow("Y轴刻度标签大小:", self.ytick_labelsize_combo)
        
        self.axes_grid_checkbox = QCheckBox("显示网格")
        self.content_layout().addRow("网格:", self.axes_grid_checkbox)

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self._set_combobox_value(self.axes_labelsize_combo, settings.get("axes.labelsize", 'medium'))
        self._set_combobox_value(self.xtick_labelsize_combo, settings.get("xtick.labelsize", 'medium'))
        self._set_combobox_value(self.ytick_labelsize_combo, settings.get("ytick.labelsize", 'medium'))
        self.axes_grid_checkbox.setChecked(settings.get("axes.grid", False))

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        return {
            "axes.labelsize": self.axes_labelsize_combo.currentText(),
            "xtick.labelsize": self.xtick_labelsize_combo.currentText(),
            "ytick.labelsize": self.ytick_labelsize_combo.currentText(),
            "axes.grid": self.axes_grid_checkbox.isChecked(),
        }

    def validate_inputs(self) -> list[str]:
        """此面板没有数字输入，无需特别验证。"""
        return []

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        index = combobox.findText(str_value, Qt.MatchFixedString)
        if index != -1:
            combobox.setCurrentIndex(index)
        else:
            combobox.setEditText(str_value)