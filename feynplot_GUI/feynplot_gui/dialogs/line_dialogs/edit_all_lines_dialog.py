import sys
import numpy as np
from typing import Dict, Any, Optional
# PySide6 imports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QLabel, QMessageBox, QCheckBox, QColorDialog
)
from PySide6.QtGui import QDoubleValidator, QIntValidator, QColor
from PySide6.QtCore import Qt, Signal


from PySide6.QtWidgets import QWidget

# Assume these imports from your core library structure
# For demonstration, I'll include a minimal Line and LineStyle definition here,
# but in your actual project, these should be imported from their respective files.
# --- Start of minimal Line and LineStyle for demonstration ---
import enum
import math

class LineStyle(enum.Enum):
    STRAIGHT = 'straight'
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

# Mock Vertex class for demonstration if not available
class MockVertex:
    _counter = 0
    def __init__(self, x, y, _id=None):
        self.x = x
        self.y = y
        self.id = _id if _id else f"mock_v{MockVertex._counter}"
        MockVertex._counter += 1
    def __repr__(self):
        return f"MockVertex(id='{self.id}', x={self.x}, y={self.y})"
    # Added for hasattr checks in Line.__init__
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, val):
        self._x = val
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        self._y = val

def cout(message: str):
    """一个简单的调试输出函数。"""
    print(message)

class Line:
    # Counter for generating unique IDs
    _line_counter_global = 0

    def __init__(self, v_start, v_end,
                 label: str = '',
                 label_offset=(0.5, 0.0),
                 angleIn=None, angleOut=None, bezier_offset=0.3,
                 # Direct line plotting attributes (formerly in linePlotConfig)
                 linewidth: float = 1.0,
                 color: str = 'black',
                 linestyle: Optional[str] = '-', # Default for STRAIGHT line style
                 alpha: float = 1.0,
                 zorder: int = 1,
                 # Direct label plotting attributes (formerly in labelPlotConfig)
                 label_fontsize: int = 30, # Renamed to avoid clash with `fontsize` kwarg
                 label_color: str = 'black', # Renamed to avoid clash with `color` kwarg
                 label_ha: str = 'center',
                 label_va: str = 'center',
                 # Style is now an internal property, not directly passed to super in subclasses
                 style: LineStyle = LineStyle.STRAIGHT,
                 **kwargs):

        # Ensure v_start and v_end are correctly assigned
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")

        self.v_start = v_start
        self.v_end = v_end

        # Line style (now a direct attribute)
        # Handle style conversion from string to enum if passed via kwargs
        if isinstance(style, str):
            try:
                self.style = getattr(LineStyle, style.upper())
            except KeyError:
                cout(f"警告：无效的线型字符串 '{style}'。默认使用 STRAIGHT。")
                self.style = LineStyle.STRAIGHT
        else:
            self.style = style

        self.label = label
        self.label_offset = np.array(label_offset)

        self._angleOut = angleOut
        self._angleIn = angleIn

        self.bezier_offset = bezier_offset

        self.id = kwargs.pop('id', f"l_{Line._line_counter_global}")
        if self.id.startswith("l_"):
            Line._line_counter_global += 1

        # --- Direct Line Plotting Attributes ---
        self.linewidth = kwargs.pop('linewidth', linewidth)
        self.color = kwargs.pop('color', color)
        # If linestyle wasn't explicitly passed, use the default based on the initial style.
        # This will be overridden by style_properties_defaults in get_plot_properties if no style.
        self.linestyle = kwargs.pop('linestyle', linestyle)
        self.alpha = kwargs.pop('alpha', alpha)
        self.zorder = kwargs.pop('zorder', zorder)

        # Support aliases for line properties
        if 'lw' in kwargs: self.linewidth = kwargs.pop('lw')
        if 'c' in kwargs: self.color = kwargs.pop('c')
        if 'ls' in kwargs: self.linestyle = kwargs.pop('ls')

        # --- Direct Label Plotting Attributes ---
        self.label_fontsize = kwargs.pop('fontsize', label_fontsize) # 'fontsize' is a common kwarg in matplotlib
        self.label_color = kwargs.pop('label_color', label_color) # 'label_color' as explicit kwarg
        self.label_ha = kwargs.pop('ha', label_ha)
        self.label_va = kwargs.pop('va', label_va)

        # Support aliases for label properties
        if 'label_size' in kwargs: self.label_fontsize = kwargs.pop('label_size')
        if 'labelcolor' in kwargs: self.label_color = kwargs.pop('labelcolor')

        self.is_selected: bool = False

        self.metadata = {}
        for key, value in kwargs.items():
            if not hasattr(self, key): # Only set if it's not already a predefined attribute
                if key in ['dash_joinstyle', 'dash_capstyle', 'solid_joinstyle', 'solid_capstyle',
                           'drawstyle', 'fillstyle', 'markerfacecolor', 'markeredgecolor',
                           'markeredgewidth', 'markersize', 'marker', 'visible', 'picker',
                           'pickradius', 'antialiased', 'rasterized', 'url', 'snap']:
                    setattr(self, key, value)
                else:
                    self.metadata[key] = value

        # If angleIn/out not provided, calculate them
        if self._angleOut is None or self._angleIn is None:
            self.set_vertices(v_start, v_end)

        cout(f"调试(Line_init): ID='{self.id}', 颜色='{self.color}', 线宽='{self.linewidth}', 样式='{self.style.name}'")

    # Minimal necessary methods for Line to work with the dialog's logic
    def set_vertices(self, v_start, v_end):
        self.v_start = v_start
        self.v_end = v_end
        # Simplified for mock
        if self._angleOut is None:
            self._angleOut = self._calc_angle(self.v_start, self.v_end)
        if self._angleIn is None:
            self._angleIn = self._calc_angle(self.v_end, self.v_start)

    @staticmethod
    def _calc_angle(p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return math.degrees(math.atan2(dy, dx))

    def update_properties(self, **kwargs):
        """
        根据提供的关键字参数更新线的属性。
        """
        for key, value in kwargs.items():
            # 处理别名，将其映射到实际的属性名
            if key == 'lw':
                self.linewidth = value
            elif key == 'c':
                self.color = value
            elif key == 'ls':
                self.linestyle = value
            elif key == 'label_size':
                self.label_fontsize = value
            elif key == 'labelcolor':
                self.label_color = value
            # 显式处理样式转换
            elif key == 'style' and isinstance(value, (str, LineStyle)):
                if isinstance(value, str):
                    try:
                        self.style = LineStyle[value.upper()]
                    except KeyError:
                        cout(f"警告：无效的线型 '{value}'。属性 '{key}' 未更新。")
                else: # 假定它已经是 LineStyle 枚举
                    self.style = value
            # 处理可能需要类型转换的特定属性
            elif key == 'label_offset' and isinstance(value, (list, tuple, np.ndarray)):
                self.label_offset = np.array(value)
            # 直接设置其他属性（如果它们存在）
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                # 对于任何其他未知关键字参数，将其存储在 metadata 中
                self.metadata[key] = value

# --- End of minimal Line and LineStyle for demonstration ---


class EditAllLinesDialog(QDialog):
    """
    一个用于编辑多个 Line 对象共同属性的对话框。
    它根据预定义的 Common 可编辑属性列表动态创建输入字段。
    """
    properties_updated = Signal() # 应用属性时发出的信号

    def __init__(self, parent=None, lines: list[Line] = None):
        super().__init__(parent)
        self.setWindowTitle("编辑所有线段属性")
        self.setMinimumWidth(400)

        self.lines = lines if lines is not None else []
        self._editable_properties = self._get_editable_common_properties()
        self._input_widgets = {} # 用于存储输入控件的引用，以便获取值

        self._init_ui()
        self._load_current_properties()

    def _get_editable_common_properties(self) -> dict:
        """
        定义可以通过此对话框编辑的共同 Line 属性，
        以及它们的类型、默认值（用于显示）和控件提示。
        此列表应明确排除子类特有的属性。
        这基于提供的 Line 类 __init__ 签名。
        """
        # 定义共同属性及其初始类型/值（用于 UI）
        # 以及用于何种类型控件的提示。
        # 此列表明确反映了 Line 基类中定义的属性。
        return {
            # 'label': {'type': str, 'default': '', 'widget': 'QLineEdit'}, # 根据要求移除 label 字段
            'label_offset_x': {'type': float, 'default': 0.5, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[0]', 'min': -10.0, 'max': 10.0, 'step': 0.1},
            'label_offset_y': {'type': float, 'default': 0.0, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[1]', 'min': -10.0, 'max': 10.0, 'step': 0.1},
            'linewidth': {'type': float, 'default': 1.0, 'widget': 'QDoubleSpinBox', 'min': 0.1, 'max': 10.0, 'step': 0.1},
            'color': {'type': str, 'default': 'black', 'widget': 'ColorButton'}, # 使用自定义的颜色选择按钮
            'linestyle': {'type': str, 'default': '-', 'widget': 'QComboBox', 'options': ['-', '--', '-.', ':', '无']},
            'alpha': {'type': float, 'default': 1.0, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01},
            'zorder': {'type': int, 'default': 1, 'widget': 'QSpinBox', 'min': 0, 'max': 10},
            'label_fontsize': {'type': int, 'default': 30, 'widget': 'QSpinBox', 'min': 1, 'max': 100},
            'label_color': {'type': str, 'default': 'black', 'widget': 'ColorButton'}, # 使用自定义的颜色选择按钮
            'label_ha': {'type': str, 'default': 'center', 'widget': 'QComboBox', 'options': ['left', 'right', 'center']},
            'label_va': {'type': str, 'default': 'center', 'widget': 'QComboBox', 'options': ['top', 'bottom', 'center', 'baseline', 'center_baseline']},
            'bezier_offset': {'type': float, 'default': 0.3, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01},
            'style': {'type': LineStyle, 'default': LineStyle.STRAIGHT, 'widget': 'QComboBox', 'options': [s.name for s in LineStyle]},
        }

    def _init_ui(self):
        """初始化对话框的用户界面。"""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        # PySide6 中 QFormLayout 的字段增长策略
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        for prop_name, details in self._editable_properties.items():
            label_text = prop_name.replace('_', ' ').title() # 转换成用户友好的文本
            widget_type = details['widget']

            input_widget = None
            if widget_type == 'QLineEdit':
                input_widget = QLineEdit()
                if details['type'] == float:
                    input_widget.setValidator(QDoubleValidator())
                elif details['type'] == int:
                    input_widget.setValidator(QIntValidator())
            elif widget_type == 'QDoubleSpinBox':
                input_widget = QDoubleSpinBox()
                input_widget.setMinimum(details.get('min', -sys.float_info.max)) # 使用 sys.float_info.max
                input_widget.setMaximum(details.get('max', sys.float_info.max))
                input_widget.setSingleStep(details.get('step', 0.1))
                input_widget.setDecimals(2) # 浮点数默认2位小数
            elif widget_type == 'QSpinBox':
                input_widget = QSpinBox()
                input_widget.setMinimum(details.get('min', -2147483647)) # int 最小值
                input_widget.setMaximum(details.get('max', 2147483647)) # int 最大值
            elif widget_type == 'QComboBox':
                input_widget = QComboBox()
                for option in details['options']:
                    input_widget.addItem(option)
            elif widget_type == 'ColorButton':
                # 自定义颜色选择按钮
                color_button = QPushButton(self.tr("选择颜色"))
                color_display = QLineEdit() # 用于显示颜色值或颜色框
                color_display.setReadOnly(True)
                color_display.setFixedWidth(80) # 固定宽度
                color_display.setText(details['default']) # 默认颜色
                # 添加一个点击事件处理函数，打开颜色对话框
                def choose_color(button=color_button, display=color_display, prop=prop_name):
                    # 获取当前按钮显示的颜色作为默认颜色
                    current_color_text = display.text()
                    initial_color = QColor(current_color_text)
                    if not initial_color.isValid():
                        initial_color = QColor(details['default']) # 如果当前颜色无效，则使用默认颜色

                    color = QColorDialog.getColor(initial_color, self)
                    if color.isValid():
                        # 设置按钮的背景色和文本
                        color_name = color.name() # 获取十六进制颜色字符串
                        display.setText(color_name)
                        display.setStyleSheet(f"background-color: {color_name};")
                        # 存储实际用于更新的值（例如，十六进制字符串）
                        self._input_widgets[prop].color_value = color_name
                        # cout(f"DEBUG: 属性 '{prop}' 颜色设置为: {color_name}") # 调试输出
                color_button.clicked.connect(choose_color)

                hbox = QHBoxLayout()
                hbox.addWidget(color_display)
                hbox.addWidget(color_button)
                input_widget = QWidget() # 创建一个包裹 widget
                input_widget.setLayout(hbox)
                # 存储颜色值供后面获取
                input_widget.color_display_widget = color_display # 存储对显示 widget 的引用
                input_widget.color_value = details['default'] # 初始颜色值

            if input_widget:
                form_layout.addRow(QLabel(label_text + ":"), input_widget)
                self._input_widgets[prop_name] = input_widget
            else:
                cout(f"警告：未为属性 '{prop_name}' 的类型 '{widget_type}' 找到合适的控件。")

        main_layout.addLayout(form_layout)

        # 按钮
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton(self.tr("应用"))
        self.apply_button.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton(self.tr("取消"))
        self.cancel_button.clicked.connect(self.reject) # 关闭对话框并返回 QDialog.Rejected
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def _load_current_properties(self):
        """
        从第一条线（如果有的话）加载当前属性，或使用默认值。
        如果所有线段对于某个属性共享一个共同值，则显示该值。
        否则，字段留空或显示“多个值”指示。
        """
        if not self.lines:
            return

        # 使用第一条线作为初始值的参考
        ref_line = self.lines[0]

        for prop_name, details in self._editable_properties.items():
            widget = self._input_widgets.get(prop_name)
            if not widget:
                continue

            current_value = None
            try:
                # 处理 label_offset 的特殊情况，访问单个组件
                if prop_name == 'label_offset_x':
                    current_value = ref_line.label_offset[0] if ref_line.label_offset is not None else details['default']
                elif prop_name == 'label_offset_y':
                    current_value = ref_line.label_offset[1] if ref_line.label_offset is not None else details['default']
                elif prop_name == 'style':
                    current_value = ref_line.style.name # 获取枚举名称用于 QComboBox
                else:
                    # 检查属性是否存在于线段实例上。
                    # 如果不存在，使用对话框的默认值，表示它可能不是所有线段的共同属性。
                    if hasattr(ref_line, prop_name):
                        current_value = getattr(ref_line, prop_name)
                    else:
                        current_value = details['default']

                # 检查所有线段是否对该属性具有相同的值
                all_same = True
                for line in self.lines:
                    line_prop_value = None
                    if prop_name == 'label_offset_x':
                        line_prop_value = line.label_offset[0] if line.label_offset is not None else details['default']
                    elif prop_name == 'label_offset_y':
                        line_prop_value = line.label_offset[1] if line.label_offset is not None else details['default']
                    elif prop_name == 'style':
                        line_prop_value = line.style.name
                    else:
                        if hasattr(line, prop_name):
                            line_prop_value = getattr(line, prop_name)
                        else:
                            line_prop_value = details['default'] # 如果缺少属性，则假定为默认值

                    if line_prop_value != current_value:
                        all_same = False
                        break
            except Exception as e:
                # 捕获属性访问过程中的任何错误，并将其视为值不同
                all_same = False
                current_value = details['default']
                cout(f"调试：加载线段 ID '{ref_line.id}' 的属性 '{prop_name}' 时出错：{e}。视为多个值。")

            # 设置控件值
            if all_same:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(current_value))
                    # 如果是颜色显示框，也设置其背景色
                    if prop_name in ['color', 'label_color']:
                        widget.setStyleSheet(f"background-color: {current_value};")
                elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                    widget.setValue(current_value)
                elif isinstance(widget, QComboBox):
                    # PySide6 的枚举
                    index = widget.findText(str(current_value), Qt.MatchFlag.MatchExactly)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif prop_name in ['color', 'label_color'] and hasattr(widget, 'color_display_widget'):
                    # 对于自定义颜色按钮，更新其显示和内部存储值
                    widget.color_display_widget.setText(str(current_value))
                    widget.color_display_widget.setStyleSheet(f"background-color: {current_value};")
                    widget.color_value = current_value # 更新内部存储的颜色值
            else:
                # 如果值不同，则进行指示（例如，清除文本，设置特殊值）
                if isinstance(widget, QLineEdit):
                    widget.clear() # 清除文本以显示不同值
                    widget.setPlaceholderText("多个值")
                elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                    # 对于数值框，设置为 NaN 或哨兵值可能很棘手。
                    # 最好将其保留为默认值或中性值。
                    widget.setValue(details['default'])
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(-1) # 未选择任何项
                    # 注意：QComboBox 在 PySide6 中不直接支持占位符文本。
                    # 您可以在索引 0 处插入一个虚拟项，例如“--多个值--”。
                elif prop_name in ['color', 'label_color'] and hasattr(widget, 'color_display_widget'):
                    # 对于自定义颜色按钮，清除显示并设置占位符文本
                    widget.color_display_widget.clear()
                    widget.color_display_widget.setPlaceholderText("多个值")
                    widget.color_display_widget.setStyleSheet("") # 清除背景色
                    widget.color_value = None # 清除内部存储的颜色值

    def _apply_changes(self):
        """将对话框中的更改应用到所有线段。"""
        if not self.lines:
            QMessageBox.information(self, "未选择线段", "没有线段可供应用更改。")
            return

        changes = {}
        try:
            for prop_name, details in self._editable_properties.items():
                widget = self._input_widgets.get(prop_name)
                if not widget:
                    continue

                value_to_set = None

                # 检查控件的内容是否指示“多个值”或为空
                is_empty_or_multiple = False
                if isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    if not text or text == "多个值":
                        is_empty_or_multiple = True
                elif isinstance(widget, QComboBox):
                    if widget.currentIndex() == -1: # 未选择任何内容
                        is_empty_or_multiple = True
                elif prop_name in ['color', 'label_color'] and hasattr(widget, 'color_display_widget'):
                    if not widget.color_display_widget.text().strip() or widget.color_display_widget.placeholderText() == "多个值":
                        is_empty_or_multiple = True


                if not is_empty_or_multiple: # 仅当用户输入了特定值时才处理
                    if isinstance(widget, QLineEdit):
                        text = widget.text().strip()
                        if details['type'] == float:
                            value_to_set = float(text)
                        elif details['type'] == int:
                            value_to_set = int(text)
                        else:
                            value_to_set = text
                    elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                        value_to_set = widget.value()
                    elif isinstance(widget, QComboBox):
                        selected_text = widget.currentText()
                        if details['type'] == LineStyle:
                            value_to_set = LineStyle[selected_text] # 将字符串转换回枚举
                        else:
                            value_to_set = selected_text
                    elif prop_name in ['color', 'label_color'] and hasattr(widget, 'color_value'):
                        value_to_set = widget.color_value # 从自定义按钮获取颜色值

                # 仅当从控件中检索到值时才应用更改
                if value_to_set is not None:
                    # 处理 label_offset 的单个组件
                    if prop_name == 'label_offset_x':
                        changes['label_offset_x'] = value_to_set
                    elif prop_name == 'label_offset_y':
                        changes['label_offset_y'] = value_to_set
                    else:
                        changes[prop_name] = value_to_set

            # 合并 label_offset 更改（如果设置了 x 或 y）
            if 'label_offset_x' in changes or 'label_offset_y' in changes:
                # 获取第一条线的当前偏移量或默认值（如果可用）
                # 如果线段没有该属性，则回退到对话框的属性默认值
                current_offset_x = self.lines[0].label_offset[0] if hasattr(self.lines[0], 'label_offset') and self.lines[0].label_offset is not None else self._editable_properties['label_offset_x']['default']
                current_offset_y = self.lines[0].label_offset[1] if hasattr(self.lines[0], 'label_offset') and self.lines[0].label_offset is not None else self._editable_properties['label_offset_y']['default']

                new_offset_x = changes.pop('label_offset_x', current_offset_x)
                new_offset_y = changes.pop('label_offset_y', current_offset_y)
                changes['label_offset'] = (new_offset_x, new_offset_y)

            # 将所有收集到的更改应用到每条线
            for line in self.lines:
                line.update_properties(**changes)
                cout(f"调试：线段 '{line.id}' 已更新，更改为：{changes}")

            QMessageBox.information(self, "成功", f"属性已成功应用于 {len(self.lines)} 条线段。")
            self.properties_updated.emit() # 通知主应用程序
            self.accept() # 关闭对话框并返回 QDialog.Accepted

        except ValueError as ve:
            QMessageBox.critical(self, "输入错误", f"无效输入：{ve}\n请检查您的值。")
            cout(f"错误：输入错误：{ve}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用更改失败：{e}")
            cout(f"错误：应用更改失败：{e}")


# 导入 QWidget 是因为我们创建了一个自定义的 ColorButton 的包裹控件