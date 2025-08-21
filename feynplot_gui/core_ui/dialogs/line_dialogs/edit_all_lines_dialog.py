import sys
import numpy as np
from typing import Dict, Any, Optional
# PySide6 imports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QLabel, QMessageBox, QCheckBox, QColorDialog,
    QWidget
)
from PySide6.QtGui import QDoubleValidator, QIntValidator, QColor
from PySide6.QtCore import Qt, Signal
from feynplot.core.line import Line
import enum

class LineStyle(enum.Enum):
    STRAIGHT = 'straight'
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

# class Line:
#     """Minimal mock Line class for demonstration."""
#     def __init__(self, id, **kwargs):
#         self.id = id
#         self.label = kwargs.get('label', '')
#         self.label_offset = kwargs.get('label_offset', (0.5, 0.0))
#         self.linewidth = kwargs.get('linewidth', 1.0)
#         self.color = kwargs.get('color', 'black')
#         self.linestyle = kwargs.get('linestyle', '-')
#         self.alpha = kwargs.get('alpha', 1.0)
#         self.zorder = kwargs.get('zorder', 1)
#         self.label_fontsize = kwargs.get('label_fontsize', 30)
#         self.label_color = kwargs.get('label_color', 'black')
#         self.label_ha = kwargs.get('label_ha', 'center')
#         self.label_va = kwargs.get('label_va', 'center')
#         self.bezier_offset = kwargs.get('bezier_offset', 0.3)
#         self.style = kwargs.get('style', LineStyle.STRAIGHT)

#     def update_properties(self, **kwargs):
#         for key, value in kwargs.items():
#             setattr(self, key, value)

def cout(message: str):
    """A simple debug output function."""
    print(message)


class EditAllLinesDialog(QDialog):
    """
    A dialog for editing common properties of multiple Line objects.
    It dynamically creates input fields based on a predefined list of editable properties.
    Fields are empty/neutral by default, and changes are only applied if a field is explicitly modified.
    """
    properties_updated = Signal() # Signal emitted when properties are applied

    def __init__(self, parent=None, lines: list[Line] = None):
        super().__init__(parent)
        self.setWindowTitle("编辑所有线段属性")
        self.setMinimumWidth(450) # Increased width for checkboxes

        self.lines = lines if lines is not None else []
        self._editable_properties = self._get_editable_common_properties()
        self._input_widgets = {} # To store references to input controls

        self._init_ui()

    def _get_editable_common_properties(self) -> dict:
        """
        Defines the common Line properties that can be edited via this dialog,
        along with their types, default values, and widget hints.
        """
        return {
            'label_offset_x': {'type': float, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[0]', 'min': -10.0, 'max': 10.0, 'step': 0.1},
            'label_offset_y': {'type': float, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[1]', 'min': -10.0, 'max': 10.0, 'step': 0.1},
            'linewidth': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.1, 'max': 10.0, 'step': 0.1},
            'color': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
            'linestyle': {'type': str, 'widget': 'QComboBox', 'options': ['-', '--', '-.', ':', '无']},
            'alpha': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01},
            'zorder': {'type': int, 'widget': 'QSpinBox', 'min': 0, 'max': 10},
            'label_fontsize': {'type': int, 'widget': 'QSpinBox', 'min': 1, 'max': 100},
            'label_color': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
            'label_ha': {'type': str, 'widget': 'QComboBox', 'options': ['left', 'right', 'center']},
            'label_va': {'type': str, 'widget': 'QComboBox', 'options': ['top', 'bottom', 'center', 'baseline', 'center_baseline']},
            'bezier_offset': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01},
            'style': {'type': LineStyle, 'widget': 'QComboBox', 'options': [s.name for s in LineStyle]},
        }

    def _init_ui(self):
        """Initializes the user interface of the dialog."""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Placeholder text for fields that should not be changed
        unchanged_placeholder = "--- (保持不变) ---"

        for prop_name, details in self._editable_properties.items():
            label_text = prop_name.replace('_', ' ').title()
            widget_type = details['widget']
            input_widget = None
            row_widget = QWidget() # Container for the entire row
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            # For widgets that cannot be empty, we use a checkbox to enable/disable them
            is_spinbox = widget_type in ['QDoubleSpinBox', 'QSpinBox']

            if is_spinbox:
                checkbox = QCheckBox()
                checkbox.setFixedWidth(20) # Compact checkbox
                row_layout.addWidget(checkbox)

            if widget_type == 'QDoubleSpinBox':
                input_widget = QDoubleSpinBox()
                input_widget.setMinimum(details.get('min', -sys.float_info.max))
                input_widget.setMaximum(details.get('max', sys.float_info.max))
                input_widget.setSingleStep(details.get('step', 0.1))
                input_widget.setDecimals(2)
                self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
            elif widget_type == 'QSpinBox':
                input_widget = QSpinBox()
                input_widget.setMinimum(details.get('min', -2147483647))
                input_widget.setMaximum(details.get('max', 2147483647))
                self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
            elif widget_type == 'QComboBox':
                input_widget = QComboBox()
                input_widget.addItem(unchanged_placeholder) # Add neutral option
                for option in details['options']:
                    input_widget.addItem(option)
                self._input_widgets[prop_name] = input_widget
            elif widget_type == 'ColorButton':
                color_display = QLineEdit()
                color_display.setReadOnly(True)
                color_display.setPlaceholderText(unchanged_placeholder)
                color_display.setFixedWidth(100)
                color_button = QPushButton("选择颜色")

                # Wrapper widget for the color button and display
                hbox = QHBoxLayout()
                hbox.setContentsMargins(0, 0, 0, 0)
                hbox.addWidget(color_display)
                hbox.addWidget(color_button)
                input_widget = QWidget()
                input_widget.setLayout(hbox)
                input_widget.color_value = None # No color selected by default

                def choose_color(display=color_display, prop_widget=input_widget):
                    initial_color = QColor('black') if not prop_widget.color_value else QColor(prop_widget.color_value)
                    color = QColorDialog.getColor(initial_color, self, "选择颜色")
                    if color.isValid():
                        color_name = color.name()
                        display.setText(color_name)
                        display.setStyleSheet(f"background-color: {color_name};")
                        prop_widget.color_value = color_name

                color_button.clicked.connect(choose_color)
                self._input_widgets[prop_name] = input_widget
            
            # This is a fallback for any other widget type, e.g., QLineEdit
            else: 
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(unchanged_placeholder)
                self._input_widgets[prop_name] = input_widget


            if input_widget:
                if is_spinbox:
                    input_widget.setEnabled(False) # Disabled by default
                    checkbox.toggled.connect(input_widget.setEnabled)
                row_layout.addWidget(input_widget)
                form_layout.addRow(QLabel(label_text + ":"), row_widget)
            else:
                 cout(f"Warning: No suitable widget found for property '{prop_name}' of type '{widget_type}'.")


        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def _apply_changes(self):
        """Applies the changes from the dialog to all selected lines."""
        if not self.lines:
            QMessageBox.information(self, "未选择线段", "没有线段可供应用更改。")
            return

        changes = {}
        try:
            for prop_name, details in self._editable_properties.items():
                control = self._input_widgets.get(prop_name)
                if not control:
                    continue

                value_to_set = None
                widget_type = details['widget']

                if widget_type in ['QDoubleSpinBox', 'QSpinBox']:
                    if control['checkbox'].isChecked():
                        value_to_set = control['widget'].value()
                elif widget_type == 'QComboBox':
                    if control.currentIndex() > 0: # Index 0 is the "unchanged" placeholder
                        selected_text = control.currentText()
                        if details['type'] == LineStyle:
                            value_to_set = LineStyle[selected_text]
                        else:
                            value_to_set = selected_text
                elif widget_type == 'ColorButton':
                    if control.color_value is not None:
                        value_to_set = control.color_value
                elif isinstance(control, QLineEdit): # Fallback for other types
                    if control.text().strip():
                        text = control.text().strip()
                        value_to_set = details['type'](text) # Convert to target type

                # If a value was set by the user, add it to the changes dictionary
                if value_to_set is not None:
                    if prop_name == 'label_offset_x':
                        changes['label_offset_x'] = value_to_set
                    elif prop_name == 'label_offset_y':
                        changes['label_offset_y'] = value_to_set
                    else:
                        changes[prop_name] = value_to_set
            
            # Combine label_offset changes if either x or y was modified
            if 'label_offset_x' in changes or 'label_offset_y' in changes:
                # Apply changes relative to each line's current offset
                # This requires iterating and applying offsets individually
                new_offset_x = changes.pop('label_offset_x', None)
                new_offset_y = changes.pop('label_offset_y', None)
                
                for line in self.lines:
                    current_x, current_y = line.label_offset if hasattr(line, 'label_offset') else (0, 0)
                    final_x = new_offset_x if new_offset_x is not None else current_x
                    final_y = new_offset_y if new_offset_y is not None else current_y
                    line.update_properties(label_offset=(final_x, final_y))

            # Apply all other collected changes to each line
            if changes:
                for line in self.lines:
                    line.update_properties(**changes)
            
            cout(f"调试：已将更改应用到 {len(self.lines)} 条线段。")

            QMessageBox.information(self, "成功", f"属性已成功应用于 {len(self.lines)} 条线段。")
            self.properties_updated.emit()
            self.accept()

        except ValueError as ve:
            QMessageBox.critical(self, "输入错误", f"无效输入：{ve}\n请检查您的值。")
            cout(f"错误：输入错误：{ve}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用更改失败：{e}")
            cout(f"错误：应用更改失败：{e}")