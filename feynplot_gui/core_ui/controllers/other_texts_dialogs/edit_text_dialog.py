# -*- coding: utf-8 -*-
# feynplot_gui\core_ui\controllers\edit_text_dialog.py

from PySide6.QtWidgets import (
    QDialog, QLineEdit, QDoubleSpinBox, QPushButton, QFormLayout, QHBoxLayout,
    QCheckBox, QColorDialog, QComboBox, QLabel, QVBoxLayout,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from feynplot_gui.core_ui.dialogs.dialog_style import apply_dialog_style, apply_content_layout
from PySide6.QtGui import QColor, QBrush

class EditTextDialog(QDialog):
    """
    一个自定义对话框，用于编辑文本内容及其他属性，如位置、字号、颜色、粗体、斜体和对齐方式。
    """
    def __init__(self, parent=None, properties: dict = None):
        """
        初始化对话框，并接受一个可选的属性字典来设置默认值。
        
        Args:
            parent: 父窗口。
            properties: 一个包含文本所有属性的字典，用于设置默认值。
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("编辑文本属性"))
        self.setModal(True)

        # 存储用户输入结果
        self._text = ""
        self._x = 0.0
        self._y = 0.0
        self._size = 12
        self._color = QColor(0, 0, 0)
        self._bold = False
        self._italic = False
        self._ha = 'center'
        self._va = 'center'
        self.result = False
        apply_dialog_style(self)
        self.setup_ui()
        
        # 关键修改：如果传入了属性字典，调用 set_default_values
        if properties:
            self.set_default_values(properties)

    def setup_ui(self):
        """
        创建并布局对话框中的控件。
        """
        main_dialog_layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        form_layout = QFormLayout(scroll_content_widget)
        apply_content_layout(form_layout)

        self.text_input = QLineEdit(self)
        form_layout.addRow("文本内容:", self.text_input)

        hint_label = QLabel(r"提示: 使用 $\boldsymbol{}$ 来创建粗体数学符号" + "\n下面的设置(粗体、斜体)对符号无效", self)
        hint_label.setStyleSheet("color: gray; font-size: 10px;")
        hint_label.setAlignment(Qt.AlignLeft)
        form_layout.addRow("", hint_label)
        self.x_input = QDoubleSpinBox(self)
        self.x_input.setRange(-10000, 10000)
        self.x_input.setDecimals(2)
        self.x_input.setSingleStep(0.5)
        form_layout.addRow("X 坐标:", self.x_input)
        self.y_input = QDoubleSpinBox(self)
        self.y_input.setRange(-10000, 10000)
        self.y_input.setDecimals(2)
        self.y_input.setSingleStep(0.5)
        form_layout.addRow("Y 坐标:", self.y_input)
        self.size_input = QDoubleSpinBox(self)
        self.size_input.setRange(1, 1000)
        self.size_input.setDecimals(0)
        form_layout.addRow("字号:", self.size_input)

        self.color_button = QPushButton(self.tr("选择颜色"), self)
        self.color_button.clicked.connect(self._on_color_button_clicked)
        form_layout.addRow("文本颜色:", self.color_button)

        style_layout = QHBoxLayout()
        self.bold_checkbox = QCheckBox(self.tr("粗体"), self)
        self.italic_checkbox = QCheckBox(self.tr("斜体"), self)
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        form_layout.addRow("字体样式:", style_layout)

        self.ha_combobox = QComboBox(self)
        self.ha_combobox.addItems(['left', 'center', 'right'])
        form_layout.addRow("水平对齐:", self.ha_combobox)
        self.va_combobox = QComboBox(self)
        self.va_combobox.addItems(['top', 'center', 'bottom', 'baseline'])
        form_layout.addRow("垂直对齐:", self.va_combobox)

        scroll_area.setWidget(scroll_content_widget)
        main_dialog_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        self.ok_button = QPushButton(self.tr("确定"), self)
        self.cancel_button = QPushButton(self.tr("取消"), self)
        self.ok_button.setDefault(True)
        self.ok_button.setAutoDefault(True)
        self.color_button.setAutoDefault(False)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_dialog_layout.addLayout(button_layout)

        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.cancel_button.clicked.connect(self.reject)

    def set_default_values(self, properties: dict):
        """
        根据传入的属性字典设置控件的初始值。
        这个方法现在负责处理各种颜色格式的转换。
        """
        # 从字典中安全地获取值
        self._text = properties.get('text', "")
        self._x = properties.get('x', 0.0)
        self._y = properties.get('y', 0.0)
        self._size = properties.get('size', 12)
        self._bold = properties.get('bold', False)
        self._italic = properties.get('italic', False)
        self._ha = properties.get('ha', 'center')
        self._va = properties.get('va', 'center')

        # 核心修改：在对话框内部处理颜色转换
        color_data = properties.get('color', 'black')
        if isinstance(color_data, QColor):
            self._color = color_data
        elif isinstance(color_data, tuple) and len(color_data) in [3, 4]:
            try:
                # 假设元组是 Matplotlib 的 RGBF 格式
                self._color = QColor.fromRgbF(*color_data)
            except TypeError:
                self._color = QColor('black') # 转换失败，回退到黑色
        elif isinstance(color_data, str):
            self._color = QColor(color_data)
        else:
            self._color = QColor('black') # 无法识别的格式，回退到黑色

        # 更新UI控件
        self.text_input.setText(self._text)
        self.x_input.setValue(self._x)
        self.y_input.setValue(self._y)
        self.size_input.setValue(self._size)
        self.bold_checkbox.setChecked(self._bold)
        self.italic_checkbox.setChecked(self._italic)
        self.ha_combobox.setCurrentText(self._ha)
        self.va_combobox.setCurrentText(self._va)
        self._update_color_button_style()

    def _update_color_button_style(self):
        """根据当前颜色更新颜色按钮的背景色"""
        self.color_button.setStyleSheet(f"background-color: {self._color.name()};")

    def _on_color_button_clicked(self):
        """打开颜色选择对话框"""
        color_dialog = QColorDialog(self)
        color = color_dialog.getColor(self._color)
        if color.isValid():
            self._color = color
            self._update_color_button_style()

    def _on_ok_clicked(self):
        """
        处理“确定”按钮点击事件，保存输入数据并关闭对话框。
        """
        self._text = self.text_input.text()
        self._x = self.x_input.value()
        self._y = self.y_input.value()
        self._size = self.size_input.value()
        self._bold = self.bold_checkbox.isChecked()
        self._italic = self.italic_checkbox.isChecked()
        self._ha = self.ha_combobox.currentText()
        self._va = self.va_combobox.currentText()
        self.result = True
        self.accept()

    def get_text_properties(self) -> dict:
        """
        运行对话框并返回用户输入的所有属性。
        
        Returns:
            一个字典，如果用户点击“确定”，则返回包含所有属性的字典；
            如果点击“取消”，则返回 None。
        """
        if self.exec() == QDialog.Accepted:
            return {
                "text": self._text,
                "x": self._x,
                "y": self._y,
                "size": self._size,
                "color": self._color.getRgbF() ,
                "bold": self._bold,
                "italic": self._italic,
                "ha": self._ha,
                "va": self._va,
            }
        return None