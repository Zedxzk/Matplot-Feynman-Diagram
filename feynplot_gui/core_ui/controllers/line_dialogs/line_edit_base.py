# feynplot_gui/controllers/line_dialogs/line_edit_base.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QColorDialog, QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
    QWidget, # Important for base class if it manages a QWidget
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
import numpy as np

# 基类，提供通用的辅助方法和 UI 结构
class LineEditBase(QWidget):
    def __init__(self):
        # 这个类不直接是 QDialog，它是一个混合类 (mixin) 或者一个组件提供者
        # 它需要访问 QDialog 的一些属性，比如 self（dialog 实例）
        pass

    def _create_spinbox_row(self, label_text: str, initial_value: float, min_val: float = -999.0, max_val: float = 999.0, step: float = 1.0, is_int: bool = False):
        """Helper function to create a label and QSpinBox/QDoubleSpinBox in a horizontal layout."""
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(label_text))
        if is_int:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_val), int(max_val))
            spinbox.setSingleStep(int(step))
            spinbox.setValue(int(initial_value))
        else:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setSingleStep(step)
            spinbox.setValue(float(initial_value))
            spinbox.setDecimals(2)
        h_layout.addWidget(spinbox)
        return h_layout, spinbox

    def _pick_color(self, button: QPushButton, color_attr_name: str):
        """Opens a color dialog, sets the button's background color, and stores the selected color."""
        initial_color_str = getattr(self, color_attr_name)
        initial_qcolor = QColor(initial_color_str)
        # Assuming 'self' refers to the QDialog instance
        color = QColorDialog.getColor(initial_qcolor, self) 
        if color.isValid():
            hex_color = color.name()
            self._set_button_color(button, hex_color)
            setattr(self, color_attr_name, hex_color)

    def _set_button_color(self, button: QPushButton, color_str: str):
        """Helper function to set the button's background and contrasting text color."""
        palette = button.palette()
        qcolor = QColor(color_str)
        
        # Calculate luminance to determine if the color is light or dark
        luminance = (0.299 * qcolor.red() + 0.587 * qcolor.green() + 0.114 * qcolor.blue()) / 255
        
        # Set text color based on luminance
        text_color = QColor(Qt.black) if luminance > 0.5 else QColor(Qt.white)

        palette.setColor(QPalette.Button, qcolor)
        palette.setColor(QPalette.ButtonText, text_color)
        
        button.setPalette(palette)
        button.setAutoFillBackground(True)
        button.setText(f"{button.text().split('(')[0].strip()} ({color_str})")

    def _set_widgets_visible(self, widgets: list, visible: bool):
        """Helper function: sets the visibility of a list of widgets and their children."""
        for item_or_layout in widgets:
            if isinstance(item_or_layout, (QHBoxLayout, QVBoxLayout)): # Check if it's a layout
                for i in range(item_or_layout.count()):
                    item = item_or_layout.itemAt(i)
                    if item.widget(): # If it's a widget
                        item.widget().setVisible(visible)
                    elif item.layout(): # If it's a nested layout
                        self._set_widgets_visible([item.layout()], visible) # Recursively call
            elif isinstance(item_or_layout, QWidget): # If it's a single QWidget (e.g., QCheckBox, QGroupBox)
                item_or_layout.setVisible(visible)
            # No need to handle QLayoutItem directly here, as we iterate through its widget/layout content
    
    def _get_value_or_default(self, obj, attr_name, default_val, target_type=float):
        """Safely gets an attribute value from an object, with default and type conversion."""
        val = getattr(obj, attr_name, default_val)
        if val is None: # If attribute exists but is None, use default
            return target_type(default_val)
        try: # Try converting to target type
            return target_type(val)
        except (ValueError, TypeError): # Conversion failed, use default
            return target_type(default_val)