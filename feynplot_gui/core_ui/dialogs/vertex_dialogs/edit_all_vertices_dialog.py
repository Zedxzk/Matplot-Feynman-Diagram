from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QDialogButtonBox, QScrollArea, QWidget, QSpinBox, QColorDialog,
    QComboBox, QDoubleSpinBox, QCheckBox # ADDED QCheckBox
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Signal, Qt

import numpy as np

from feynplot.core.vertex import Vertex

class EditAllVerticesDialog(QDialog):
    """
    一个对话框，用于批量编辑所有顶点的公共属性。
    """
    settings_applied = Signal()

    def __init__(self, all_vertices: list[Vertex], parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑所有顶点属性")
        self.setGeometry(100, 100, 500, 600)

        self.all_vertices = all_vertices

        # REMOVED: The state-tracking booleans are no longer needed.
        # The checkboxes and other widgets will hold the state directly.
        # self.apply_label_prefix = False
        # ... and so on for all others

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        tip_label = QLabel("提示：勾选要修改的属性，然后设置新值。未勾选的属性将保持不变。")
        tip_font = QFont()
        tip_font.setPointSize(9)
        tip_label.setFont(tip_font)
        tip_label.setStyleSheet("color: #666666; padding: 5px; background-color: #f5f5f5; border-radius: 3px;")
        tip_label.setWordWrap(True)
        main_layout.addWidget(tip_label)
        main_layout.addSpacing(10)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # --- 通用标签前缀 ---
        self.content_layout.addWidget(QLabel(self.tr("设置所有顶点名:")))
        label_prefix_layout = QHBoxLayout()
        label_prefix_layout.addWidget(QLabel(self.tr("新名称:")))
        self.label_prefix_input = QLineEdit()
        # CHANGED: Placeholder text is simpler. An empty field means no change.
        self.label_prefix_input.setPlaceholderText("留空不修改，输入一个空格来清空名称")
        label_prefix_layout.addWidget(self.label_prefix_input)
        self.content_layout.addLayout(label_prefix_layout)
        self.content_layout.addSpacing(10)

        # --- 标签偏移 (label_offset) ---
        # CHANGED: Use a checkbox to control this section
        offset_layout = QHBoxLayout()
        self.offset_checkbox = QCheckBox(self.tr("标签偏移 (Label Offset):"))
        self.offset_checkbox.setFont(QFont("Any", -1, QFont.Bold))
        self.content_layout.addWidget(self.offset_checkbox)

        self.offset_x_spinbox = QDoubleSpinBox()
        self.offset_x_spinbox.setRange(-100.0, 100.0)
        self.offset_x_spinbox.setSingleStep(0.1)
        self.offset_x_spinbox.setDecimals(2)
        self.offset_x_spinbox.setEnabled(False) # Initially disabled

        self.offset_y_spinbox = QDoubleSpinBox()
        self.offset_y_spinbox.setRange(-100.0, 100.0)
        self.offset_y_spinbox.setSingleStep(0.1)
        self.offset_y_spinbox.setDecimals(2)
        self.offset_y_spinbox.setEnabled(False) # Initially disabled

        # Connect checkbox to enable/disable spinboxes
        self.offset_checkbox.toggled.connect(self.offset_x_spinbox.setEnabled)
        self.offset_checkbox.toggled.connect(self.offset_y_spinbox.setEnabled)

        offset_layout.addWidget(QLabel(self.tr("X:")))
        offset_layout.addWidget(self.offset_x_spinbox)
        offset_layout.addSpacing(10)
        offset_layout.addWidget(QLabel(self.tr("Y:")))
        offset_layout.addWidget(self.offset_y_spinbox)
        self.content_layout.addLayout(offset_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点大小 (size) ---
        # CHANGED: Use a checkbox
        size_layout = QHBoxLayout()
        self.size_checkbox = QCheckBox(self.tr("顶点大小 (Size):"))
        self.size_checkbox.setFont(QFont("Any", -1, QFont.Bold))
        size_layout.addWidget(self.size_checkbox)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 500)
        self.size_spinbox.setValue(100) # A sensible default
        self.size_spinbox.setEnabled(False) # Initially disabled
        size_layout.addWidget(self.size_spinbox)
        size_layout.addStretch()
        self.size_checkbox.toggled.connect(self.size_spinbox.setEnabled)
        self.content_layout.addLayout(size_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点颜色 (color) ---
        # This widget's logic is already fine, as it's event-driven. We'll just track the color.
        self.content_layout.addWidget(QLabel(self.tr("顶点颜色 (Color):")))
        self.color_preview_button = QPushButton(self.tr("点击选择颜色（默认不修改）"))
        self.color_preview_button.clicked.connect(self._select_vertex_color)
        self.current_vertex_color = None # None means no change
        self.content_layout.addWidget(self.color_preview_button)
        self.content_layout.addSpacing(10)

        # --- 顶点标记 (marker) ---
        # This widget's logic is also fine. "不修改" is a good first item.
        self.content_layout.addWidget(QLabel(self.tr("顶点标记 (Marker):")))
        self.marker_combobox = QComboBox()
        self.marker_combobox.addItems(['不修改', 'o', 's', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_'])
        self.content_layout.addWidget(self.marker_combobox)
        self.content_layout.addSpacing(10)
        
        # --- Create other properties using the same checkbox pattern ---
        self._create_spinbox_property("顶点透明度 (Alpha):", "alpha_spinbox", 0, 100, 100, is_percent=True)
        self._create_color_property("顶点边缘颜色 (Edgecolor):", "edgecolor_preview_button", "_select_edge_color", "current_edge_color")
        self._create_spinbox_property("顶点线宽 (Linewidth):", "linewidth_spinbox", 1, 10, 1)
        self._create_spinbox_property("标签大小 (Label Size):", "label_size_spinbox", 5, 72, 12)
        self._create_color_property("标签颜色 (Label Color):", "label_color_preview_button", "_select_label_color", "current_label_color")

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._on_accepted)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    # HELPER to reduce code duplication for spinbox properties
    def _create_spinbox_property(self, label, widget_name, min_val, max_val, default_val, is_percent=False):
        layout = QHBoxLayout()
        checkbox = QCheckBox(label)
        checkbox.setFont(QFont("Any", -1, QFont.Bold))
        layout.addWidget(checkbox)

        spinbox = QSpinBox()
        if is_percent:
            spinbox.setSuffix(" %")
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default_val)
        spinbox.setEnabled(False)
        layout.addWidget(spinbox)
        layout.addStretch()
        
        checkbox.toggled.connect(spinbox.setEnabled)
        
        # Store checkbox and spinbox on self
        setattr(self, widget_name + "_checkbox", checkbox)
        setattr(self, widget_name, spinbox)

        self.content_layout.addLayout(layout)
        self.content_layout.addSpacing(10)

    # HELPER to reduce code duplication for color properties
    def _create_color_property(self, label, button_name, slot_name, color_attr_name):
        self.content_layout.addWidget(QLabel(label))
        button = QPushButton(self.tr("点击选择颜色（默认不修改）"))
        button.clicked.connect(getattr(self, slot_name))
        setattr(self, color_attr_name, None) # None means no change
        setattr(self, button_name, button)
        self.content_layout.addWidget(button)
        self.content_layout.addSpacing(10)
    
    # REMOVED all the _on_..._changed slots. They are no longer necessary.

    def _select_vertex_color(self):
        color = QColorDialog.getColor(QColor(Qt.blue), self)
        if color.isValid():
            self.current_vertex_color = color
            self.color_preview_button.setStyleSheet(f"background-color: {color.name()}; color: { 'white' if color.value() < 128 else 'black' }")
            self.color_preview_button.setText(f"已选择: {color.name()}")

    def _select_edge_color(self):
        color = QColorDialog.getColor(QColor(Qt.black), self)
        if color.isValid():
            self.current_edge_color = color
            self.edgecolor_preview_button.setStyleSheet(f"background-color: {color.name()}; color: { 'white' if color.value() < 128 else 'black' }")
            self.edgecolor_preview_button.setText(f"已选择: {color.name()}")

    def _select_label_color(self):
        color = QColorDialog.getColor(QColor(Qt.black), self)
        if color.isValid():
            self.current_label_color = color
            self.label_color_preview_button.setStyleSheet(f"background-color: {color.name()}; color: { 'white' if color.value() < 128 else 'black' }")
            self.label_color_preview_button.setText(f"已选择: {color.name()}")

    def _on_accepted(self):
        """处理OK按钮点击事件，应用设置并发出信号。"""
        
        # A flag to track if anything was changed at all
        any_setting_applied = False
        
        # Check which settings were enabled by the user
        apply_label = len(self.label_prefix_input.text()) > 0
        apply_offset = self.offset_checkbox.isChecked()
        apply_size = self.size_checkbox.isChecked()
        apply_color = self.current_vertex_color is not None
        apply_marker = self.marker_combobox.currentIndex() > 0
        apply_alpha = self.alpha_spinbox_checkbox.isChecked()
        apply_edgecolor = self.current_edge_color is not None
        apply_linewidth = self.linewidth_spinbox_checkbox.isChecked()
        apply_label_size = self.label_size_spinbox_checkbox.isChecked()
        apply_label_color = self.current_label_color is not None

        # Check if at least one checkbox/action was triggered
        any_setting_applied = any([
            apply_label, apply_offset, apply_size, apply_color, apply_marker,
            apply_alpha, apply_edgecolor, apply_linewidth, apply_label_size,
            apply_label_color
        ])
        
        if not any_setting_applied:
            QMessageBox.information(self, "提示", "没有需要修改的属性。")
            self.reject() # Use reject() to indicate no changes were made
            return

        for vertex in self.all_vertices:
            if apply_label:
                new_text = self.label_prefix_input.text()
                vertex.label = "" if new_text == " " else new_text
            
            if apply_size:
                vertex.size = self.size_spinbox.value()
                
            if apply_color:
                vertex.color = self.current_vertex_color.name()
                
            if apply_marker:
                vertex.marker = self.marker_combobox.currentText()
                
            if apply_alpha:
                vertex.alpha = self.alpha_spinbox.value() / 100.0
                
            if apply_edgecolor:
                vertex.edgecolor = self.current_edge_color.name()
                
            if apply_linewidth:
                vertex.linewidth = self.linewidth_spinbox.value()
                
            if apply_label_size:
                vertex.label_size = self.label_size_spinbox.value()
                
            if apply_label_color:
                vertex.label_color = self.current_label_color.name()

            if apply_offset:
                new_offset_x = self.offset_x_spinbox.value()
                new_offset_y = self.offset_y_spinbox.value()
                vertex.label_offset = np.array([new_offset_x, new_offset_y])

        QMessageBox.information(self, "成功", f"属性已成功应用于 {len(self.all_vertices)} 个顶点。")
        self.settings_applied.emit()
        self.accept()

    @staticmethod
    def show_dialog(all_vertices: list[Vertex], parent=None) -> bool:
        dialog = EditAllVerticesDialog(all_vertices, parent)
        return dialog.exec() == QDialog.Accepted