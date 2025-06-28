# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_latex_settings_panel.py

from PySide6.QtWidgets import QWidget, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox # 从同级目录导入

class LatexSettingsPanel(CollapsibleGroupBox):
    """
    LaTeX 设置面板，包含 LaTeX 渲染支持和字体家族。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("LaTeX 设置", parent)

        self.use_latex_checkbox = QCheckBox(self.tr("使用 LaTeX 渲染文本"))
        self.content_layout().addRow("LaTeX 支持:", self.use_latex_checkbox)

        self.latex_font_family_combo = QComboBox()
        self.latex_font_family_combo.addItems([
            "serif (Times New Roman)", "sans-serif (Helvetica/Arial)", "monospace (Courier)"
        ])
        self.latex_font_family_combo.setEditable(False)
        self.content_layout().addRow("LaTeX 字体家族:", self.latex_font_family_combo)

        # 连接信号以控制 LaTeX 字体家族组合框的启用状态
        self.use_latex_checkbox.stateChanged.connect(self._on_usetex_changed)

    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        self.use_latex_checkbox.setChecked(settings.get("text.usetex", False))

        # 根据 font.family 设置 LaTeX 字体家族组合框
        latex_font_key = ""
        current_mpl_font_family = settings.get("font.family", "serif")
        if isinstance(current_mpl_font_family, list):
             current_mpl_font_family = current_mpl_font_family[0]

        if "serif" in current_mpl_font_family.lower():
            latex_font_key = "serif (Times New Roman)"
        elif "sans-serif" in current_mpl_font_family.lower():
            latex_font_key = "sans-serif (Helvetica/Arial)"
        elif "monospace" in current_mpl_font_family.lower():
            latex_font_key = "monospace (Courier)"
        
        index_latex = self.latex_font_family_combo.findText(latex_font_key, Qt.MatchContains)
        if index_latex != -1:
            self.latex_font_family_combo.setCurrentIndex(index_latex)
        else:
            self.latex_font_family_combo.setCurrentIndex(0) # 默认选中第一个

        # 初始化时也更新启用状态
        self._on_usetex_changed(self.use_latex_checkbox.checkState())

    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        settings = {
            "text.usetex": self.use_latex_checkbox.isChecked(),
        }
        if self.use_latex_checkbox.isChecked():
            selected_latex_font_text = self.latex_font_family_combo.currentText()
            if "serif" in selected_latex_font_text.lower():
                settings["font.family"] = "serif"
            elif "sans-serif" in selected_latex_font_text.lower():
                settings["font.family"] = "sans-serif"
            elif "monospace" in selected_latex_font_text.lower():
                settings["font.family"] = "monospace"
            else:
                settings["font.family"] = "serif" # 默认值
        return settings

    def validate_inputs(self) -> list[str]:
        """此面板没有数字输入，无需特别验证。"""
        return []

    def _on_usetex_changed(self, state: int):
        """当“使用 LaTeX 渲染文本”复选框状态改变时调用。"""
        is_checked = (state == Qt.CheckState.Checked)
        self.latex_font_family_combo.setEnabled(is_checked)