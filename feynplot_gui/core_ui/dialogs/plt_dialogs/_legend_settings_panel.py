# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_legend_settings_panel.py

from PySide6.QtWidgets import QWidget, QComboBox, QCheckBox
from PySide6.QtCore import Qt # 导入Qt用于Qt.MatchFixedString
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox # 从同级目录导入

class LegendSettingsPanel(CollapsibleGroupBox):
    """
    图例设置面板。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("图例设置", parent)

        self.legend_fontsize_combo = QComboBox()
        self.legend_fontsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.legend_fontsize_combo.setEditable(True)
        self.content_layout().addRow("图例字体大小:", self.legend_fontsize_combo)

        self.legend_frameon_checkbox = QCheckBox(self.tr("显示图例边框"))
        self.content_layout().addRow("图例边框:", self.legend_frameon_checkbox)

        self.legend_loc_combo = QComboBox()
        self.legend_loc_combo.addItems([
            "best", "upper right", "upper left", "lower left", "lower right",
            "right", "center left", "center right", "lower center", "upper center", "center"
        ])
        self.content_layout().addRow("图例位置:", self.legend_loc_combo)

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self._set_combobox_value(self.legend_fontsize_combo, settings.get("legend.fontsize", 'medium'))
        self.legend_frameon_checkbox.setChecked(settings.get("legend.frameon", True))
        self._set_combobox_value(self.legend_loc_combo, settings.get("legend.loc", 'best'))

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        return {
            "legend.fontsize": self.legend_fontsize_combo.currentText(),
            "legend.frameon": self.legend_frameon_checkbox.isChecked(),
            "legend.loc": self.legend_loc_combo.currentText(),
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