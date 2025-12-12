import sys
import numpy as np
from typing import Dict, Any, Optional
# PySide6 imports
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QLabel, QMessageBox, QCheckBox, QColorDialog,
    QWidget, QFrame, QApplication, QGridLayout
)
from PySide6.QtGui import QDoubleValidator, QIntValidator, QColor
from PySide6.QtCore import Qt, Signal
# from feynplot.core.line import Line # 假设从您的库中导入
import enum

class LineStyle(enum.Enum):
    STRAIGHT = 'straight'
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

# 最小化的 Line 类的实现，以便代码可以运行
class Line:
    """Minimal mock Line class for demonstration."""
    def __init__(self, id, **kwargs):
        self.id = id
        self.label = kwargs.get('label', '')
        self.label_offset = kwargs.get('label_offset', (0.5, 0.0))
        self.linewidth = kwargs.get('linewidth', 1.0)
        self.color = kwargs.get('color', 'black')
        self.linestyle = kwargs.get('linestyle', '-')
        self.alpha = kwargs.get('alpha', 1.0)
        self.zorder = kwargs.get('zorder', 1)
        self.label_fontsize = kwargs.get('label_fontsize', 30)
        self.label_color = kwargs.get('label_color', 'black')
        self.label_ha = kwargs.get('label_ha', 'center')
        self.label_va = kwargs.get('label_va', 'center')
        self.bezier_offset = kwargs.get('bezier_offset', 0.3)
        self.style = kwargs.get('style', LineStyle.STRAIGHT)
        self.hidden_label = kwargs.get('hidden_label', False)
        
        self.arrow = kwargs.get('arrow', False) 
        self.arrow_filled = kwargs.get('arrow_filled', True)
        self.arrow_position = kwargs.get('arrow_position', 0.5)
        self.arrow_size = kwargs.get('arrow_size', 50.0)
        self.arrow_line_width = kwargs.get('arrow_line_width', 1.0)
        self.arrow_reversed = kwargs.get('arrow_reversed', False)
        self.mutation_scale = kwargs.get('mutation_scale', 20.0)
        self.arrow_offset_ratio = kwargs.get('arrow_offset_ratio', 0.1)
        self.arrow_angle = kwargs.get('arrow_angle', 90.0)
        self.arrow_tail_angle = kwargs.get('arrow_tail_angle', 60.0)
        self.arrow_style = kwargs.get('arrow_style', 'default')
        self.arrow_facecolor = kwargs.get('arrow_facecolor', 'black')
        self.arrow_edgecolor = kwargs.get('arrow_edgecolor', 'black')

    def update_properties(self, **kwargs):
        cout(f"  -> 更新 Line {self.id} 属性: {kwargs}")
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                cout(f"  -> 警告: Line {self.id} 没有属性 '{key}'")

    def __repr__(self):
        return f"<Line {self.id} (Arrow: {self.arrow}, Style: {self.arrow_style}, Angle: {self.arrow_angle})>"


def cout(message: str):
    """A simple debug output function."""
    print(message)


class EditAllLinesDialog(QDialog):
    """
    一个用于编辑多个 Line 对象共同属性的对话框。
    它根据预定义的属性列表动态创建输入字段。
    字段默认为空/中立状态，只有当字段被明确修改时，更改才会被应用。
    """
    properties_updated = Signal() # 属性应用后发出的信号

    def __init__(self, parent=None, lines: list[Line] = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("编辑所有线段属性"))
        # *** 更改：为双列布局增加宽度 ***
        self.setMinimumWidth(600) 

        self.lines = lines if lines is not None else []
        self._editable_properties = self._get_editable_common_properties()
        self._input_widgets = {} # 存储对输入控件的引用

        self._init_ui()

    def _get_editable_common_properties(self) -> dict:
        """
        定义可通过此对话框编辑的常见 Line 属性。
        顺序很重要，用于UI布局。
        """
        return {
            # --- 通用属性 ---
            'label_offset_x': {'type': float, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[0]', 'min': -10.0, 'max': 10.0, 'step': 0.1, 'decimals': 1},
            'label_offset_y': {'type': float, 'widget': 'QDoubleSpinBox', 'target_attr': 'label_offset[1]', 'min': -10.0, 'max': 10.0, 'step': 0.1, 'decimals': 1},
            'linewidth': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.1, 'max': 10.0, 'step': 0.1, 'decimals': 1},
            'color': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
            'linestyle': {'type': str, 'widget': 'QComboBox', 'options': ['-', '--', '-.', ':', '无']},
            'alpha': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01, 'decimals': 2},
            'zorder': {'type': int, 'widget': 'QSpinBox', 'min': 0, 'max': 10},
            'label_fontsize': {'type': int, 'widget': 'QSpinBox', 'min': 1, 'max': 100},
            'label_color': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
            'label_ha': {'type': str, 'widget': 'QComboBox', 'options': ['left', 'right', 'center']},
            'label_va': {'type': str, 'widget': 'QComboBox', 'options': ['top', 'bottom', 'center', 'baseline', 'center_baseline']},
            'bezier_offset': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01, 'decimals': 2},
            'style': {'type': LineStyle, 'widget': 'QComboBox', 'options': [s.name for s in LineStyle]},
            'hidden_label': {'type': bool, 'widget': 'QComboBox', 'options': ['True', 'False']},
            
            # --- 箭头属性 ---
            'arrow_filled': {'type': bool, 'widget': 'QComboBox', 'options': ['True', 'False']},
            'arrow_position': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.01, 'decimals': 2},
            'arrow_size': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 200.0, 'step': 0.5, 'decimals': 1},
            'arrow_line_width': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 20.0, 'step': 0.1, 'decimals': 1},
            'arrow_reversed': {'type': bool, 'widget': 'QComboBox', 'options': ['True', 'False']},
            'mutation_scale': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 200.0, 'step': 1, 'decimals': 0},
            'arrow_style': {'type': str, 'widget': 'QComboBox', 'options': ['default', 'fishtail']},
            'arrow_offset_ratio': {'type': float, 'widget': 'QDoubleSpinBox', 'min': -100.0, 'max': 100.0, 'step': 0.1, 'decimals': 1},
            'arrow_angle': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 180.0, 'step': 1.0, 'decimals': 0},
            'arrow_tail_angle': {'type': float, 'widget': 'QDoubleSpinBox', 'min': 0.0, 'max': 180.0, 'step': 1.0, 'decimals': 0},
            'arrow_facecolor': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
            'arrow_edgecolor': {'type': str, 'default': 'black', 'widget': 'ColorButton'},
        }

    def _create_color_chooser(self, display_widget: QLineEdit, prop_widget: QWidget, initial_color_str: str):
        """
        一个辅助函数，用于创建 QColorDialog 的槽函数，
        以正确捕获循环中变量的作用域。
        """
        def choose_color():
            # 如果用户已选择过颜色，则使用该颜色；否则使用默认建议色
            current_color_str = prop_widget.color_value if prop_widget.color_value else initial_color_str
            initial_color = QColor(current_color_str)
            
            color = QColorDialog.getColor(initial_color, self, "选择颜色")
            
            if color.isValid():
                color_name = color.name()
                display_widget.setText(color_name)
                display_widget.setStyleSheet(f"background-color: {color_name};")
                # 只有当用户点击“OK”时，才设置 color_value
                prop_widget.color_value = color_name
        return choose_color

    def _init_ui(self):
        """初始化对话框的用户界面（使用双列 QGridLayout）。"""
        main_layout = QVBoxLayout(self)

        # 用于“未更改”的占位符文本
        unchanged_placeholder = "--- (保持不变) ---"
        
        # --- 将属性分为“通用”和“箭头”两组 ---
        arrow_section_start_index = -1
        prop_keys = list(self._editable_properties.keys())
        try:
            arrow_section_start_index = prop_keys.index('arrow_filled')
        except ValueError:
            pass # 没有箭头属性

        if arrow_section_start_index != -1:
            general_props = list(self._editable_properties.items())[:arrow_section_start_index]
            arrow_props = list(self._editable_properties.items())[arrow_section_start_index:]
        else:
            general_props = list(self._editable_properties.items())
            arrow_props = []

        # --- 创建通用属性布局（双列） ---
        general_group_widget = QWidget()
        general_grid_layout = QGridLayout(general_group_widget)
        general_grid_layout.setColumnStretch(1, 1) # 拉伸第1列（输入框）
        general_grid_layout.setColumnStretch(3, 1) # 拉伸第3列（输入框）
        general_grid_layout.setColumnMinimumWidth(0, 100) # 标签列最小宽度
        general_grid_layout.setColumnMinimumWidth(2, 100) # 标签列最小宽度
        
        i = 0
        for prop_name, details in general_props:
            label_text = prop_name.replace('_', ' ').title()
            widget_type = details['widget']
            input_widget = None
            row_widget = QWidget() # 包含 CheckBox 和输入框的容器
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            is_spinbox = widget_type in ['QDoubleSpinBox', 'QSpinBox']
            checkbox = None 

            if is_spinbox:
                checkbox = QCheckBox()
                checkbox.setFixedWidth(20) 
                row_layout.addWidget(checkbox)

            if widget_type == 'QDoubleSpinBox':
                input_widget = QDoubleSpinBox()
                input_widget.setMinimum(details.get('min', -sys.float_info.max))
                input_widget.setMaximum(details.get('max', sys.float_info.max))
                input_widget.setSingleStep(details.get('step', 0.1))
                input_widget.setDecimals(details.get('decimals', 2)) 
                self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
            elif widget_type == 'QSpinBox':
                input_widget = QSpinBox()
                input_widget.setMinimum(details.get('min', -2147483647))
                input_widget.setMaximum(details.get('max', 2147483647))
                self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
            elif widget_type == 'QComboBox':
                input_widget = QComboBox()
                input_widget.addItem(unchanged_placeholder) 
                for option in details['options']:
                    input_widget.addItem(option)
                self._input_widgets[prop_name] = {'widget': input_widget}
            elif widget_type == 'ColorButton':
                color_display = QLineEdit()
                color_display.setReadOnly(True)
                color_display.setPlaceholderText(unchanged_placeholder)
                color_display.setFixedWidth(100)
                color_button = QPushButton(self.tr("选择颜色"))
                hbox = QHBoxLayout()
                hbox.setContentsMargins(0, 0, 0, 0)
                hbox.addWidget(color_display)
                hbox.addWidget(color_button)
                input_widget = QWidget() # input_widget 是颜色按钮的容器
                input_widget.setLayout(hbox)
                input_widget.color_value = None 
                initial_color_str = details.get('default', 'black')
                
                # 使用辅助函数来正确捕获作用域
                color_button.clicked.connect(self._create_color_chooser(color_display, input_widget, initial_color_str))
                self._input_widgets[prop_name] = {'widget': input_widget}
            else: 
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(unchanged_placeholder)
                self._input_widgets[prop_name] = {'widget': input_widget}
            
            if input_widget:
                if is_spinbox:
                    input_widget.setEnabled(False) 
                    if checkbox: 
                        checkbox.toggled.connect(input_widget.setEnabled)
                
                # ColorButton 是一种特殊情况，input_widget 已经是容器
                if widget_type != 'ColorButton':
                    row_layout.addWidget(input_widget)
                else:
                    # 对于 ColorButton，我们直接使用 input_widget 作为 row_widget
                    row_widget = input_widget
            
                # --- 添加到网格布局 ---
                row = i // 2
                col = (i % 2) * 2 # 0 或 2
                label_widget = QLabel(label_text + ":")
                label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                general_grid_layout.addWidget(label_widget, row, col)
                general_grid_layout.addWidget(row_widget, row, col + 1)
                
                # 存储对标签和行控件的引用，以便将来隐藏/显示
                self._input_widgets[prop_name]['row_widget'] = row_widget
                self._input_widgets[prop_name]['label_widget'] = label_widget 
                
                i += 1
            else:
                 cout(f"警告：未找到属性 '{prop_name}' 的合适控件。")
        
        main_layout.addWidget(general_group_widget)

        # --- 创建箭头属性布局（双列） ---
        if arrow_props:
            # 添加分隔符
            section_label = QLabel(self.tr("箭头属性 (仅作用于带箭头的线段):"))
            section_label.setStyleSheet('font-weight: bold; margin-top: 8px;')
            hr = QFrame()
            hr.setFrameShape(QFrame.HLine)
            hr.setFrameShadow(QFrame.Sunken)
            main_layout.addWidget(section_label)
            main_layout.addWidget(hr)

            arrow_group_widget = QWidget()
            arrow_grid_layout = QGridLayout(arrow_group_widget)
            arrow_grid_layout.setColumnStretch(1, 1) # 拉伸第1列
            arrow_grid_layout.setColumnStretch(3, 1) # 拉伸第3列
            arrow_grid_layout.setColumnMinimumWidth(0, 100) # 标签列
            arrow_grid_layout.setColumnMinimumWidth(2, 100) # 标签列

            fishtail_only_props = ['arrow_angle', 'arrow_tail_angle', 'arrow_offset_ratio']
            
            j = 0
            for prop_name, details in arrow_props:
                # --- (控件创建逻辑与上面重复) ---
                label_text = prop_name.replace('_', ' ').title()
                widget_type = details['widget']
                input_widget = None
                row_widget = QWidget() 
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                is_spinbox = widget_type in ['QDoubleSpinBox', 'QSpinBox']
                checkbox = None 

                if is_spinbox:
                    checkbox = QCheckBox()
                    checkbox.setFixedWidth(20) 
                    row_layout.addWidget(checkbox)

                if widget_type == 'QDoubleSpinBox':
                    input_widget = QDoubleSpinBox()
                    input_widget.setMinimum(details.get('min', -sys.float_info.max))
                    input_widget.setMaximum(details.get('max', sys.float_info.max))
                    input_widget.setSingleStep(details.get('step', 0.1))
                    input_widget.setDecimals(details.get('decimals', 2)) 
                    self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
                elif widget_type == 'QSpinBox':
                    input_widget = QSpinBox()
                    input_widget.setMinimum(details.get('min', -2147483647))
                    input_widget.setMaximum(details.get('max', 2147483647))
                    self._input_widgets[prop_name] = {'checkbox': checkbox, 'widget': input_widget}
                elif widget_type == 'QComboBox':
                    input_widget = QComboBox()
                    input_widget.addItem(unchanged_placeholder) 
                    for option in details['options']:
                        input_widget.addItem(option)
                    self._input_widgets[prop_name] = {'widget': input_widget}
                elif widget_type == 'ColorButton':
                    color_display = QLineEdit()
                    color_display.setReadOnly(True)
                    color_display.setPlaceholderText(unchanged_placeholder)
                    color_display.setFixedWidth(100)
                    color_button = QPushButton(self.tr("选择颜色"))
                    hbox = QHBoxLayout()
                    hbox.setContentsMargins(0, 0, 0, 0)
                    hbox.addWidget(color_display)
                    hbox.addWidget(color_button)
                    input_widget = QWidget() # input_widget 是颜色按钮的容器
                    input_widget.setLayout(hbox)
                    input_widget.color_value = None 
                    initial_color_str = details.get('default', 'black')
                    
                    color_button.clicked.connect(self._create_color_chooser(color_display, input_widget, initial_color_str))
                    self._input_widgets[prop_name] = {'widget': input_widget}
                else: 
                    input_widget = QLineEdit()
                    input_widget.setPlaceholderText(unchanged_placeholder)
                    self._input_widgets[prop_name] = {'widget': input_widget}
                
                if input_widget:
                    if is_spinbox:
                        input_widget.setEnabled(False) 
                        if checkbox: 
                            checkbox.toggled.connect(input_widget.setEnabled)
                    
                    if widget_type != 'ColorButton':
                        row_layout.addWidget(input_widget)
                    else:
                        row_widget = input_widget
                
                    # --- 添加到网格布局 ---
                    row = j // 2
                    col = (j % 2) * 2 # 0 或 2
                    label_widget = QLabel(label_text + ":")
                    label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    arrow_grid_layout.addWidget(label_widget, row, col)
                    arrow_grid_layout.addWidget(row_widget, row, col + 1)
                    
                    self._input_widgets[prop_name]['row_widget'] = row_widget
                    self._input_widgets[prop_name]['label_widget'] = label_widget 

                    # 连接 arrow_style 的信号
                    if prop_name == 'arrow_style':
                        if isinstance(input_widget, QComboBox):
                            input_widget.currentIndexChanged.connect(self._on_arrow_style_changed)
                    
                    # 默认隐藏 fishtail 特有属性
                    if prop_name in fishtail_only_props:
                        row_widget.setVisible(False)
                        label_widget.setVisible(False)
                    
                    j += 1
                else:
                    cout(f"警告：未找到属性 '{prop_name}' 的合适控件。")
            
            main_layout.addWidget(arrow_group_widget)
            
        # --- 添加按钮 ---
        button_layout = QHBoxLayout()
        button_layout.addStretch() # 居中
        self.apply_button = QPushButton(self.tr("应用"))
        self.apply_button.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton(self.tr("取消"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch() # 居中

        main_layout.addLayout(button_layout)

        # --- 最终初始化 ---
        # 根据默认选择（“--- 保持不变 ---”）初始化 fishtail 属性的可见性
        entry = self._input_widgets.get('arrow_style')
        if isinstance(entry, dict):
            combo = entry.get('widget')
            if isinstance(combo, QComboBox):
                self._on_arrow_style_changed(combo.currentIndex())

    def _apply_changes(self):
        """将对话框中的更改应用到所有选定的线段。"""
        if not self.lines:
            QMessageBox.information(self, self.tr("未选择线段"), self.tr("没有线段可供应用更改。"))
            return

        changes = {}
        try:
            for prop_name, details in self._editable_properties.items():
                control_entry = self._input_widgets.get(prop_name)
                if control_entry is None:
                    continue
                
                control_widget = control_entry.get('widget')
                control_checkbox = control_entry.get('checkbox', None)
                
                if control_widget is None:
                    continue

                value_to_set = None
                widget_type = details['widget']

                if widget_type in ['QDoubleSpinBox', 'QSpinBox']:
                    if control_checkbox and control_checkbox.isChecked():
                        value_to_set = control_widget.value()
                elif widget_type == 'QComboBox':
                    if isinstance(control_widget, QComboBox) and control_widget.currentIndex() > 0: 
                        selected_text = control_widget.currentText()
                        if details['type'] == LineStyle:
                            value_to_set = LineStyle[selected_text]
                        elif details['type'] == bool:
                            value_to_set = (selected_text.lower() == 'true')
                        else:
                            value_to_set = selected_text
                elif widget_type == 'ColorButton':
                    prop_widget = control_widget
                    if getattr(prop_widget, 'color_value', None) is not None:
                        value_to_set = prop_widget.color_value
                elif isinstance(control_widget, QLineEdit): 
                    # 确保我们没有获取到 "--- (保持不变) ---" 占位符
                    if control_widget.text().strip() and not control_widget.placeholderText():
                        text = control_widget.text().strip()
                        value_to_set = details['type'](text) 

                if value_to_set is not None:
                    if prop_name == 'label_offset_x':
                        changes['label_offset_x'] = value_to_set
                    elif prop_name == 'label_offset_y':
                        changes['label_offset_y'] = value_to_set
                    else:
                        changes[prop_name] = value_to_set
            
            # --- 应用更改（与之前相同） ---
            
            # 合并 label_offset 更改
            if 'label_offset_x' in changes or 'label_offset_y' in changes:
                new_offset_x = changes.pop('label_offset_x', None)
                new_offset_y = changes.pop('label_offset_y', None)
                
                for line in self.lines:
                    current_x, current_y = line.label_offset if hasattr(line, 'label_offset') else (0, 0)
                    final_x = new_offset_x if new_offset_x is not None else current_x
                    final_y = new_offset_y if new_offset_y is not None else current_y
                    line.update_properties(label_offset=(final_x, final_y))

            # 单独处理箭头属性
            arrow_props_set = {
                'arrow_filled', 'arrow_position', 'arrow_size', 'arrow_line_width', 'arrow_reversed',
                'mutation_scale', 'arrow_offset_ratio', 'arrow_angle', 'arrow_tail_angle', 'arrow_style',
                'arrow_facecolor', 'arrow_edgecolor'
            }
            
            arrow_changes = {k: v for k, v in changes.items() if k in arrow_props_set}
            
            if arrow_changes:
                for k in arrow_changes.keys():
                    changes.pop(k, None)
                    
                lines_with_arrows = [line for line in self.lines if hasattr(line, 'arrow') and getattr(line, 'arrow', False)]
                
                if not lines_with_arrows:
                    QMessageBox.information(self, self.tr("提示"), self.tr("未找到带箭头的线段。箭头设置不会生效。"))
                else:
                    cout(f"向 {len(lines_with_arrows)} 条带箭头的线段应用: {arrow_changes}")
                    for line in lines_with_arrows:
                        line.update_properties(**arrow_changes)

            # 应用所有其他收集到的更改
            if changes:
                cout(f"向 {len(self.lines)} 条线段应用通用更改: {changes}")
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

    def _on_arrow_style_changed(self, index: int):
        """根据选择的 arrow_style 显示/隐藏 fishtail 特有的属性。"""
        entry = self._input_widgets.get('arrow_style')
        if not entry or not isinstance(entry, dict):
            return
        combo = entry.get('widget')
        if not isinstance(combo, QComboBox):
            return
            
        selected_text = combo.currentText()
        # 只有当明确选择 'fishtail' 时才显示
        show_fishtail = (selected_text == 'fishtail')
        
        fishtail_props = ['arrow_angle', 'arrow_tail_angle', 'arrow_offset_ratio']
        
        for key in fishtail_props:
            e = self._input_widgets.get(key)
            if isinstance(e, dict):
                # *** 更改：同时隐藏/显示标签和输入框 ***
                row = e.get('row_widget')
                label = e.get('label_widget')
                if row:
                    row.setVisible(show_fishtail)
                if label:
                    label.setVisible(show_fishtail)

# --- 用于测试的最小化运行代码 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建一些模拟的 Line 对象
    line1 = Line(id=1, arrow=True, arrow_style='default')
    line2 = Line(id=2, arrow=False, label_fontsize=10)
    line3 = Line(id=3, arrow=True, arrow_style='default', arrow_angle=45)
    
    all_lines = [line1, line2, line3]
    
    cout("--- 初始状态 ---")
    for line in all_lines:
        cout(repr(line))

    dialog = EditAllLinesDialog(lines=all_lines)
    
    def on_update():
        cout("\n--- 属性更新后 ---")
        for line in all_lines:
            cout(repr(line))

    dialog.properties_updated.connect(on_update)
    
    dialog.exec()
    
    sys.exit()