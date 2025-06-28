# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_lines_markers_settings_panel.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox
from PySide6.QtCore import Qt # 导入Qt用于Qt.MatchFixedString
from PySide6.QtGui import QDoubleValidator
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox # 从同级目录导入

class LinesMarkersSettingsPanel(CollapsibleGroupBox):
    """
    线条和标记设置面板。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("线条与标记设置", parent)

        line_width_layout = QHBoxLayout()
        self.lines_linewidth_edit = QLineEdit()
        self.lines_linewidth_edit.setPlaceholderText("例如: 1.5")
        self.lines_linewidth_edit.setValidator(QDoubleValidator(0.1, 10.0, 2, self))
        line_width_layout.addWidget(self.lines_linewidth_edit)
        line_width_layout.addWidget(QLabel("pt"))
        self.content_layout().addRow("默认线条宽度:", line_width_layout)

        self.lines_linestyle_combo = QComboBox()
        self.lines_linestyle_combo.addItems([
            "- (实线)", "-- (虚线)", "-. (点划线)", ": (点线)"
        ])
        self.content_layout().addRow("默认线条样式:", self.lines_linestyle_combo)
        
        self.lines_marker_combo = QComboBox()
        self.lines_marker_combo.addItems([
            "None", "o (圆圈)", "s (方块)", "^ (三角形)", "v (倒三角形)",
            "x (X形)", "+ (加号)", "* (星号)", "D (菱形)", "p (五边形)"
        ])
        self.content_layout().addRow("默认标记样式:", self.lines_marker_combo)

        marker_size_layout = QHBoxLayout()
        self.lines_markersize_edit = QLineEdit()
        self.lines_markersize_edit.setPlaceholderText("例如: 6.0")
        self.lines_markersize_edit.setValidator(QDoubleValidator(0.1, 50.0, 2, self))
        marker_size_layout.addWidget(self.lines_markersize_edit)
        marker_size_layout.addWidget(QLabel("pt"))
        self.content_layout().addRow("默认标记大小:", marker_size_layout)

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self.lines_linewidth_edit.setText(str(settings.get("lines.linewidth", 1.5)))
        self._set_combobox_value(self.lines_linestyle_combo, settings.get("lines.linestyle", '-'))
        self._set_combobox_value(self.lines_marker_combo, settings.get("lines.marker", 'None'))
        self.lines_markersize_edit.setText(str(settings.get("lines.markersize", 6.0)))

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        selected_linestyle_text = self.lines_linestyle_combo.currentText()
        marker_value = self.lines_marker_combo.currentText()
        if marker_value == "None":
            marker_value = None # Matplotlib 期望 None, 不是字符串 "None"

        return {
            "lines.linewidth": float(self.lines_linewidth_edit.text()),
            "lines.linestyle": selected_linestyle_text.split(' ')[0],
            "lines.marker": marker_value,
            "lines.markersize": float(self.lines_markersize_edit.text()),
        }

    def validate_inputs(self) -> list[str]:
        """验证输入字段。"""
        errors = []
        if not self.lines_linewidth_edit.hasAcceptableInput():
            errors.append(f"默认线条宽度 (Line Width) 输入无效。当前输入: '{self.lines_linewidth_edit.text()}'。请检查是否为有效数字。")
        if not self.lines_markersize_edit.hasAcceptableInput():
            errors.append(f"默认标记大小 (Marker Size) 输入无效。当前输入: '{self.lines_markersize_edit.text()}'。请检查是否为有效数字。")
        return errors

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        if combobox == self.lines_linestyle_combo:
            found_index = -1
            for i in range(combobox.count()):
                item_text = combobox.itemText(i)
                if item_text.startswith(str_value) and (len(item_text) == len(str_value) or item_text[len(str_value)] == ' '):
                    found_index = i
                    break
            if found_index != -1:
                combobox.setCurrentIndex(found_index)
            else:
                combobox.setEditText(str_value)
        elif combobox == self.lines_marker_combo:
            index = combobox.findText(str_value, Qt.MatchFixedString)
            if index != -1:
                combobox.setCurrentIndex(index)
            else:
                index_none = combobox.findText("None", Qt.MatchFixedString)
                if value is None and index_none != -1:
                    combobox.setCurrentIndex(index_none)
                else:
                    combobox.setEditText(str_value)
        else:
            index = combobox.findText(str_value, Qt.MatchFixedString)
            if index != -1:
                combobox.setCurrentIndex(index)
            else:
                combobox.setEditText(str_value)