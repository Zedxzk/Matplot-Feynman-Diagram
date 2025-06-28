# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/_font_settings_panel.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QFontComboBox, QVBoxLayout, QComboBox
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt
from typing import Dict, Any

from ._collapsible_group_box import CollapsibleGroupBox




class FontSettingsPanel(CollapsibleGroupBox):
    """
    字体设置面板，包含通用字体家族、字体大小以及 MathText 特定字体设置。
    它作为一个 CollapsibleGroupBox 的子类，将其所有内容（其他子CollapsibleGroupBox）
    放置在父类的内部 QVBoxLayout 中，以确保清晰的垂直布局。
    """
    def __init__(self, parent: QWidget = None):
        super().__init__("字体设置", parent) # 调用父类 CollapsibleGroupBox 的构造函数

        # 创建一个 QWidget 来容纳所有的子折叠组
        self._sub_panels_container = QWidget(self)
        self._sub_panels_layout = QVBoxLayout(self._sub_panels_container) # 使用 QVBoxLayout 来垂直堆叠子组

        # 将这个容器 QWidget 添加到 FontSettingsPanel 的 FormLayout 中
        self.content_layout().addWidget(self._sub_panels_container)

        # --- 通用字体设置 ---
        self.general_font_group = CollapsibleGroupBox("通用字体", self._sub_panels_container)
        self._sub_panels_layout.addWidget(self.general_font_group)

        self.font_family_combo = QFontComboBox()
        self.general_font_group.content_layout().addRow("字体家族:", self.font_family_combo)

        font_size_layout = QHBoxLayout()
        self.font_size_edit = QLineEdit()
        self.font_size_edit.setPlaceholderText("例如: 12.0")
        self.font_size_edit.setValidator(QDoubleValidator(0.1, 100.0, 2, self))
        font_size_layout.addWidget(self.font_size_edit)
        font_size_layout.addWidget(QLabel("pt"))
        self.general_font_group.content_layout().addRow("字体大小:", font_size_layout)

        # --- MathText 字体设置 ---
        self.mathtext_font_group = CollapsibleGroupBox("数学文本 (MathText) 字体", self._sub_panels_container)
        self._sub_panels_layout.addWidget(self.mathtext_font_group)

        self.mathtext_fontset_combo = QFontComboBox()
        self.mathtext_fontset_combo.addItems(['dejavusans', 'dejavaserif', 'cm', 'stix', 'stixsans', 'custom'])
        self.mathtext_font_group.content_layout().addRow("字体集 (fontset):", self.mathtext_fontset_combo)
        
        self.mathtext_rm_combo = QFontComboBox()
        self.mathtext_font_group.content_layout().addRow("正体 (rm):", self.mathtext_rm_combo)

        self.mathtext_it_combo = QFontComboBox()
        self.mathtext_font_group.content_layout().addRow("斜体 (it):", self.mathtext_it_combo)
        
        self.mathtext_bf_combo = QFontComboBox()
        self.mathtext_font_group.content_layout().addRow("粗体 (bf):", self.mathtext_bf_combo)

        self.mathtext_bfit_combo = QFontComboBox()
        self.mathtext_font_group.content_layout().addRow("粗斜体 (bfit):", self.mathtext_bfit_combo)
        
        # --- 新增：ax.text 默认字体设置 ---
        self.text_font_group = CollapsibleGroupBox("文本 (ax.text) 默认字体", self._sub_panels_container)
        self._sub_panels_layout.addWidget(self.text_font_group)

        self.text_font_family_combo = QFontComboBox()
        self.text_font_group.content_layout().addRow("字体家族:", self.text_font_family_combo)

        text_font_size_layout = QHBoxLayout()
        self.text_font_size_edit = QLineEdit()
        self.text_font_size_edit.setPlaceholderText("例如: 10.0")
        self.text_font_size_edit.setValidator(QDoubleValidator(0.1, 100.0, 2, self))
        text_font_size_layout.addWidget(self.text_font_size_edit)
        text_font_size_layout.addWidget(QLabel("pt"))
        self.text_font_group.content_layout().addRow("字体大小:", text_font_size_layout)

        self.text_font_weight_combo = QComboBox()
        self.text_font_weight_combo.addItems(["normal", "bold", "light", "ultralight", "semibold", "heavy", "extra bold", "black"])
        self.text_font_group.content_layout().addRow("字体粗细:", self.text_font_weight_combo)

        self.text_font_style_combo = QComboBox()
        self.text_font_style_combo.addItems(["normal", "italic", "oblique"])
        self.text_font_group.content_layout().addRow("字体样式:", self.text_font_style_combo)

        # 在 _sub_panels_layout 中添加一个伸展器，确保内容靠上
        self._sub_panels_layout.addStretch(1)

        # --- 设置默认值 ---
        # 1. MathText 字体集默认选择 'custom'
        index_custom = self.mathtext_fontset_combo.findText('custom')
        if index_custom != -1:
            self.mathtext_fontset_combo.setCurrentIndex(index_custom)
        
        # 2. 所有 MathText 字体默认设置为 'Times New Roman'
        self._set_font_combo_text(self.mathtext_rm_combo, "Times New Roman")
        self._set_font_combo_text(self.mathtext_it_combo, "Times New Roman")
        self._set_font_combo_text(self.mathtext_bf_combo, "Times New Roman")
        self._set_font_combo_text(self.mathtext_bfit_combo, "Times New Roman")

        # 3. ax.text 默认字体家族设置为 'Times New Roman'
        self._set_font_combo_text(self.text_font_family_combo, "Times New Roman")
        # 您可能还想为 ax.text 的字体大小、粗细和样式设置默认值，这里假设您默认保持现有代码逻辑。
        # 如果需要，可以像下面这样设置：
        # self.text_font_size_edit.setText("10.0") # 或者您想要的默认值
        # self._set_combobox_value(self.text_font_weight_combo, "normal") # 或者您想要的默认值
        # self._set_combobox_value(self.text_font_style_combo, "normal") # 或者您想要的默认值


    def load_settings(self, settings: Dict[str, Any]):
        """从字典加载设置到UI。"""
        # --- 通用字体 ---
        font_family = settings.get("font.family", "sans-serif")
        if isinstance(font_family, list):
            font_family = font_family[0] 
        index = self.font_family_combo.findText(font_family)
        if index != -1:
            self.font_family_combo.setCurrentIndex(index)
        else:
            self.font_family_combo.setEditText(font_family)

        self.font_size_edit.setText(str(settings.get("font.size", 10.0)))

        # --- MathText 字体 ---
        mathtext_fontset = settings.get("mathtext.fontset", "dejavusans")
        index = self.mathtext_fontset_combo.findText(mathtext_fontset)
        if index != -1:
            self.mathtext_fontset_combo.setCurrentIndex(index)
        else:
            self.mathtext_fontset_combo.setEditText(mathtext_fontset) 

        mathtext_rm = settings.get("mathtext.rm", "") 
        self._set_font_combo_text(self.mathtext_rm_combo, mathtext_rm)

        mathtext_it = settings.get("mathtext.it", "")
        self._set_font_combo_text(self.mathtext_it_combo, mathtext_it)
        
        mathtext_bf = settings.get("mathtext.bf", "")
        self._set_font_combo_text(self.mathtext_bf_combo, mathtext_bf)
        
        mathtext_bfit = settings.get("mathtext.bfit", "")
        self._set_font_combo_text(self.mathtext_bfit_combo, mathtext_bfit)

        # --- 新增：ax.text 默认字体 ---
        self._set_font_combo_text(self.text_font_family_combo, settings.get("text.fontfamily", "sans-serif"))
        self.text_font_size_edit.setText(str(settings.get("text.fontsize", 10.0)))
        self._set_combobox_value(self.text_font_weight_combo, settings.get("text.fontweight", "normal"))
        self._set_combobox_value(self.text_font_style_combo, settings.get("text.fontstyle", "normal"))


    def get_settings(self) -> Dict[str, Any]:
        """从UI获取设置并返回字典。"""
        settings = {
            "font.family": [self.font_family_combo.currentFont().family()], 
            "font.size": float(self.font_size_edit.text()),
            "mathtext.fontset": self.mathtext_fontset_combo.currentText(),
            "mathtext.rm": self.mathtext_rm_combo.currentFont().family() if self.mathtext_fontset_combo.currentText() == 'custom' else "",
            "mathtext.it": self.mathtext_it_combo.currentFont().family() if self.mathtext_fontset_combo.currentText() == 'custom' else "",
            "mathtext.bf": self.mathtext_bf_combo.currentFont().family() if self.mathtext_fontset_combo.currentText() == 'custom' else "",
            "mathtext.bfit": self.mathtext_bfit_combo.currentFont().family() if self.mathtext_fontset_combo.currentText() == 'custom' else "",
            # --- 新增：ax.text 默认字体 ---
            "text.fontfamily": self.text_font_family_combo.currentFont().family(),
            "text.fontsize": float(self.text_font_size_edit.text()),
            "text.fontweight": self.text_font_weight_combo.currentText(),
            "text.fontstyle": self.text_font_style_combo.currentText(),
        }
        if settings["mathtext.fontset"] != 'custom':
            settings.pop("mathtext.rm")
            settings.pop("mathtext.it")
            settings.pop("mathtext.bf")
            settings.pop("mathtext.bfit")
        return settings

    def validate_inputs(self) -> list[str]:
        """验证输入字段。"""
        errors = []
        if not self.font_size_edit.hasAcceptableInput():
            errors.append(f"通用字体大小 (Font Size) 输入无效。当前输入: '{self.font_size_edit.text()}'。请检查是否为有效数字。")
        
        if self.mathtext_fontset_combo.currentText() == 'custom':
            if not self.mathtext_rm_combo.currentFont().family():
                errors.append("当 MathText 字体集为 'custom' 时，正体 (rm) 字体不能为空。")
            if not self.mathtext_it_combo.currentFont().family():
                errors.append("当 MathText 字体集为 'custom' 时，斜体 (it) 字体不能为空。")
        
        # --- 新增：ax.text 字体验证 ---
        if not self.text_font_size_edit.hasAcceptableInput():
            errors.append(f"文本字体大小 (Text Font Size) 输入无效。当前输入: '{self.text_font_size_edit.text()}'。请检查是否为有效数字。")

        return errors

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        index = combobox.findText(str_value, Qt.MatchFixedString)
        if index != -1:
            combobox.setCurrentIndex(index)
        else:
            combobox.setEditText(str_value)

    def _set_font_combo_text(self, combo: QFontComboBox, text: str):
        """辅助函数：设置 QFontComboBox 的文本，并尝试精确匹配或设置编辑文本。"""
        if not text:
            combo.setEditText("") 
            return
        index = combo.findText(text)
        if index != -1:
            combo.setCurrentIndex(index)
        else:
            combo.setEditText(text)