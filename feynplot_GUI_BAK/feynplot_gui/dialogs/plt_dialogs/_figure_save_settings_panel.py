# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_figure_save_settings_panel.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt # 导入Qt用于Qt.MatchFixedString
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox # 从同级目录导入

class FigureSaveSettingsPanel(CollapsibleGroupBox):
    """
    图像与保存设置面板。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("图像与保存设置", parent)

        figure_width_layout = QHBoxLayout()
        self.figure_width_edit = QLineEdit()
        self.figure_width_edit.setPlaceholderText("例如: 6.4")
        self.figure_width_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_width_layout.addWidget(self.figure_width_edit)
        figure_width_layout.addWidget(QLabel("英寸"))
        self.content_layout().addRow("图像宽度:", figure_width_layout)

        figure_height_layout = QHBoxLayout()
        self.figure_height_edit = QLineEdit()
        self.figure_height_edit.setPlaceholderText("例如: 4.8")
        self.figure_height_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_height_layout.addWidget(self.figure_height_edit)
        figure_height_layout.addWidget(QLabel("英寸"))
        self.content_layout().addRow("图像高度:", figure_height_layout)

        self.savefig_dpi_edit = QLineEdit()
        self.savefig_dpi_edit.setPlaceholderText("例如: 300")
        self.savefig_dpi_edit.setValidator(QIntValidator(50, 1200, self))
        self.content_layout().addRow("保存图片DPI:", self.savefig_dpi_edit)

        self.savefig_format_combo = QComboBox()
        self.savefig_format_combo.addItems(["png", "pdf", "svg", "jpeg", "tiff"])
        self.content_layout().addRow("保存图片格式:", self.savefig_format_combo)

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self.figure_width_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[0]))
        self.figure_height_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[1]))
        self.savefig_dpi_edit.setText("300") 
        self._set_combobox_value(self.savefig_format_combo, settings.get("savefig.format", 'png'))

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        return {
            "figure.figsize": [float(self.figure_width_edit.text()), float(self.figure_height_edit.text())],
            "savefig.dpi": int(self.savefig_dpi_edit.text()),
            "savefig.format": self.savefig_format_combo.currentText(),
        }

    def validate_inputs(self) -> list[str]:
        """验证输入字段。"""
        errors = []
        if not self.figure_width_edit.hasAcceptableInput():
            errors.append(f"图像宽度 (Figure Width) 输入无效。当前输入: '{self.figure_width_edit.text()}'。请检查是否为有效数字。")
        if not self.figure_height_edit.hasAcceptableInput():
            errors.append(f"图像高度 (Figure Height) 输入无效。当前输入: '{self.figure_height_edit.text()}'。请检查是否为有效数字。")
        if not self.savefig_dpi_edit.hasAcceptableInput():
            errors.append(f"保存图片DPI (Save DPI) 输入无效。当前输入: '{self.savefig_dpi_edit.text()}'。请检查是否为有效整数。")
        return errors

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        index = combobox.findText(str_value, Qt.MatchFixedString)
        if index != -1:
            combobox.setCurrentIndex(index)
        else:
            combobox.setEditText(str_value)