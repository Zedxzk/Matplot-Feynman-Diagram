# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_figure_save_settings_panel.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton
from PySide6.QtGui import QDoubleValidator
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
        self.figure_width_edit.setPlaceholderText(self.tr("例如: 6.4"))
        self.figure_width_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_width_layout.addWidget(self.figure_width_edit)
        figure_width_layout.addWidget(QLabel(self.tr("英寸")))
        self.content_layout().addRow("图像宽度:", figure_width_layout)

        figure_height_layout = QHBoxLayout()
        self.figure_height_edit = QLineEdit()
        self.figure_height_edit.setPlaceholderText(self.tr("例如: 4.8"))
        self.figure_height_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_height_layout.addWidget(self.figure_height_edit)
        figure_height_layout.addWidget(QLabel(self.tr("英寸")))
        self.content_layout().addRow("图像高度:", figure_height_layout)

        sync_btn = QPushButton(self.tr("从画布获取"))
        sync_btn.setToolTip(self.tr("将当前画布显示尺寸填入宽高，使保存结果与界面一致"))
        sync_btn.clicked.connect(self._on_sync_from_canvas)
        self.content_layout().addRow("", sync_btn)

        self.savefig_dpi_spin = QSpinBox()
        self.savefig_dpi_spin.setRange(50, 1200)
        self.savefig_dpi_spin.setValue(300)
        self.content_layout().addRow("保存图片DPI:", self.savefig_dpi_spin)

        self.savefig_format_combo = QComboBox()
        self.savefig_format_combo.addItems(["png", "pdf", "svg", "jpeg", "tiff"])
        self.content_layout().addRow("保存图片格式:", self.savefig_format_combo)

        self._pixel_preview_label = QLabel("")
        self._update_pixel_preview()
        self.savefig_dpi_spin.valueChanged.connect(self._update_pixel_preview)
        self.figure_width_edit.textChanged.connect(self._update_pixel_preview)
        self.figure_height_edit.textChanged.connect(self._update_pixel_preview)
        self.content_layout().addRow("输出约:", self._pixel_preview_label)

        self._canvas_figsize_callback = None

    def set_canvas_figsize_callback(self, callback):
        """设置从画布获取尺寸的回调，由外部传入。"""
        self._canvas_figsize_callback = callback

    def _on_sync_from_canvas(self):
        """从画布获取当前尺寸并填入宽高。"""
        if self._canvas_figsize_callback:
            try:
                w, h = self._canvas_figsize_callback()
                self.figure_width_edit.setText(f"{w:.2f}")
                self.figure_height_edit.setText(f"{h:.2f}")
            except Exception:
                pass

    def _update_pixel_preview(self):
        """根据宽高和 DPI 更新输出像素预览。"""
        try:
            w = float(self.figure_width_edit.text() or 6.4)
            h = float(self.figure_height_edit.text() or 4.8)
            dpi = self.savefig_dpi_spin.value()
            pw, ph = int(w * dpi), int(h * dpi)
            self._pixel_preview_label.setText(f"{pw} × {ph} 像素")
        except (ValueError, TypeError):
            self._pixel_preview_label.setText("—")

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self.figure_width_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[0]))
        self.figure_height_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[1]))
        save_dpi = settings.get("savefig.dpi", 300)
        dpi_int = int(save_dpi) if isinstance(save_dpi, (int, float)) else 300
        self.savefig_dpi_spin.setValue(min(1200, max(50, dpi_int)))
        self._set_combobox_value(self.savefig_format_combo, settings.get("savefig.format", 'png'))
        self._update_pixel_preview()

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        return {
            "figure.figsize": [float(self.figure_width_edit.text()), float(self.figure_height_edit.text())],
            "savefig.dpi": self.savefig_dpi_spin.value(),
            "savefig.format": self.savefig_format_combo.currentText(),
        }

    def validate_inputs(self) -> list[str]:
        """验证输入字段。"""
        errors = []
        if not self.figure_width_edit.hasAcceptableInput():
            errors.append(f"图像宽度 (Figure Width) 输入无效。当前输入: '{self.figure_width_edit.text()}'。请检查是否为有效数字。")
        if not self.figure_height_edit.hasAcceptableInput():
            errors.append(f"图像高度 (Figure Height) 输入无效。当前输入: '{self.figure_height_edit.text()}'。请检查是否为有效数字。")
        # DPI 使用 QSpinBox，始终为有效整数，无需额外验证
        return errors

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        index = combobox.findText(str_value, Qt.MatchFixedString)
        if index != -1:
            combobox.setCurrentIndex(index)
        else:
            combobox.setEditText(str_value)