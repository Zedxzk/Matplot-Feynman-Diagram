from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QDialogButtonBox, QScrollArea, QWidget, QSpinBox, QColorDialog,
    QComboBox, QDoubleSpinBox
)
from PySide6.QtGui import QColor
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

        self.original_label_prefix = ""

        # Flags to track if spinbox values represent "multiple values"
        self._offset_x_multiple_values = False
        self._offset_y_multiple_values = False
        self._size_multiple_values = False
        self._alpha_multiple_values = False
        self._linewidth_multiple_values = False
        self._label_size_multiple_values = False


        self.init_ui()
        self._load_current_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # --- 通用标签前缀 ---
        self.content_layout.addWidget(QLabel("<b>设置所有顶点名:</b> (空表示不修改，空格表示清空)"))
        label_prefix_layout = QHBoxLayout()
        label_prefix_layout.addWidget(QLabel("前缀:"))
        self.label_prefix_input = QLineEdit()
        self.label_prefix_input.setPlaceholderText("留空表示不修改，输入空格清空所有标签")
        label_prefix_layout.addWidget(self.label_prefix_input)
        self.content_layout.addLayout(label_prefix_layout)
        self.content_layout.addSpacing(10)

        # --- 标签偏移 (label_offset) ---
        self.content_layout.addWidget(QLabel("<b>标签偏移 (Label Offset):</b> (X, Y)"))
        offset_layout = QHBoxLayout()
        self.offset_x_spinbox = QDoubleSpinBox()
        self.offset_x_spinbox.setRange(-100.0, 100.0)
        self.offset_x_spinbox.setSingleStep(0.1)
        self.offset_x_spinbox.setDecimals(2)
        # Connect to value changed to reset multiple values flag
        self.offset_x_spinbox.valueChanged.connect(lambda: setattr(self, '_offset_x_multiple_values', False))

        self.offset_y_spinbox = QDoubleSpinBox()
        self.offset_y_spinbox.setRange(-100.0, 100.0)
        self.offset_y_spinbox.setSingleStep(0.1)
        self.offset_y_spinbox.setDecimals(2)
        self.offset_y_spinbox.valueChanged.connect(lambda: setattr(self, '_offset_y_multiple_values', False))

        offset_layout.addWidget(QLabel("X:"))
        offset_layout.addWidget(self.offset_x_spinbox)
        offset_layout.addWidget(QLabel("Y:"))
        offset_layout.addWidget(self.offset_y_spinbox)
        self.content_layout.addLayout(offset_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点大小 (size) ---
        self.content_layout.addWidget(QLabel("<b>顶点大小 (Size):</b>"))
        size_layout = QHBoxLayout()
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 500)
        self.size_spinbox.valueChanged.connect(lambda: setattr(self, '_size_multiple_values', False))
        size_layout.addWidget(self.size_spinbox)
        self.content_layout.addLayout(size_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点颜色 (color) ---
        self.content_layout.addWidget(QLabel("<b>顶点颜色 (Color):</b>"))
        color_layout = QHBoxLayout()
        self.color_preview_button = QPushButton("选择颜色")
        self.color_preview_button.clicked.connect(self._select_vertex_color)
        self.current_vertex_color = QColor(Qt.blue)
        self.color_preview_button.setStyleSheet(f"background-color: {self.current_vertex_color.name()}")
        color_layout.addWidget(self.color_preview_button)
        self.content_layout.addLayout(color_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点标记 (marker) ---
        self.content_layout.addWidget(QLabel("<b>顶点标记 (Marker):</b>"))
        marker_layout = QHBoxLayout()
        self.marker_combobox = QComboBox()
        self.marker_combobox.addItems(['o', 's', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_'])
        marker_layout.addWidget(self.marker_combobox)
        self.content_layout.addLayout(marker_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点透明度 (alpha) ---
        self.content_layout.addWidget(QLabel("<b>顶点透明度 (Alpha):</b>"))
        alpha_layout = QHBoxLayout()
        self.alpha_spinbox = QSpinBox()
        self.alpha_spinbox.setRange(0, 100)
        self.alpha_spinbox.valueChanged.connect(lambda: setattr(self, '_alpha_multiple_values', False))
        alpha_layout.addWidget(self.alpha_spinbox)
        self.content_layout.addLayout(alpha_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点边缘颜色 (edgecolor) ---
        self.content_layout.addWidget(QLabel("<b>顶点边缘颜色 (Edgecolor):</b>"))
        edgecolor_layout = QHBoxLayout()
        self.edgecolor_preview_button = QPushButton("选择边缘颜色")
        self.edgecolor_preview_button.clicked.connect(self._select_edge_color)
        self.current_edge_color = QColor(Qt.blue)
        self.edgecolor_preview_button.setStyleSheet(f"background-color: {self.current_edge_color.name()}")
        edgecolor_layout.addWidget(self.edgecolor_preview_button)
        self.content_layout.addLayout(edgecolor_layout)
        self.content_layout.addSpacing(10)

        # --- 顶点线宽 (linewidth) ---
        self.content_layout.addWidget(QLabel("<b>顶点线宽 (Linewidth):</b>"))
        linewidth_layout = QHBoxLayout()
        self.linewidth_spinbox = QSpinBox()
        self.linewidth_spinbox.setRange(0, 10)
        self.linewidth_spinbox.setSingleStep(1)
        self.linewidth_spinbox.valueChanged.connect(lambda: setattr(self, '_linewidth_multiple_values', False))
        linewidth_layout.addWidget(self.linewidth_spinbox)
        self.content_layout.addLayout(linewidth_layout)
        self.content_layout.addSpacing(10)

        # --- 标签大小 (label_size) ---
        self.content_layout.addWidget(QLabel("<b>标签大小 (Label Size):</b>"))
        label_size_layout = QHBoxLayout()
        self.label_size_spinbox = QSpinBox()
        self.label_size_spinbox.setRange(5, 72)
        self.label_size_spinbox.valueChanged.connect(lambda: setattr(self, '_label_size_multiple_values', False))
        label_size_layout.addWidget(self.label_size_spinbox)
        self.content_layout.addLayout(label_size_layout)
        self.content_layout.addSpacing(10)

        # --- 标签颜色 (label_color) ---
        self.content_layout.addWidget(QLabel("<b>标签颜色 (Label Color):</b>"))
        label_color_layout = QHBoxLayout()
        self.label_color_preview_button = QPushButton("选择标签颜色")
        self.label_color_preview_button.clicked.connect(self._select_label_color)
        self.current_label_color = QColor(Qt.black)
        self.label_color_preview_button.setStyleSheet(f"background-color: {self.current_label_color.name()}")
        label_color_layout.addWidget(self.label_color_preview_button)
        self.content_layout.addLayout(label_color_layout)
        self.content_layout.addSpacing(10)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._on_accepted)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _load_current_settings(self):
        """
        加载当前顶点的公共属性到UI。
        对于所有顶点都相同的属性，显示其值。
        对于不同属性，清空输入并设置内部标志。
        """
        if not self.all_vertices:
            return

        first_vertex = self.all_vertices[0]

        # 标签前缀 (Label Prefix)
        self.label_prefix_input.setText("")
        self.original_label_prefix = ""

        # 标签偏移 (Label Offset)
        initial_offset_x = getattr(first_vertex, 'label_offset', np.array([0.0, 0.0]))[0]
        initial_offset_y = getattr(first_vertex, 'label_offset', np.array([0.0, 0.0]))[1]

        all_x_same = all(getattr(v, 'label_offset', np.array([0.0, 0.0]))[0] == initial_offset_x for v in self.all_vertices)
        all_y_same = all(getattr(v, 'label_offset', np.array([0.0, 0.0]))[1] == initial_offset_y for v in self.all_vertices)

        if all_x_same:
            self.offset_x_spinbox.setValue(initial_offset_x)
            self._offset_x_multiple_values = False
        else:
            self.offset_x_spinbox.clear() # Clears text and value
            # QSpinBox/QDoubleSpinBox don't have placeholderText, but setting empty string works
            # We use an internal flag to track the "multiple values" state
            self._offset_x_multiple_values = True
            # Optionally, you can set a tooltip or a temporary label to indicate "multiple values"
            # self.offset_x_spinbox.setToolTip("多个值")

        if all_y_same:
            self.offset_y_spinbox.setValue(initial_offset_y)
            self._offset_y_multiple_values = False
        else:
            self.offset_y_spinbox.clear()
            self._offset_y_multiple_values = True
            # self.offset_y_spinbox.setToolTip("多个值")

        # 顶点大小 (Size)
        initial_size = getattr(first_vertex, 'size', 100)
        if all(getattr(v, 'size', 100) == initial_size for v in self.all_vertices):
            self.size_spinbox.setValue(initial_size)
            self._size_multiple_values = False
        else:
            self.size_spinbox.clear()
            self._size_multiple_values = True

        # 顶点颜色 (Color)
        initial_color = getattr(first_vertex, 'color', 'blue')
        if all(getattr(v, 'color', 'blue') == initial_color for v in self.all_vertices):
            self.current_vertex_color.setNamedColor(initial_color)
            self.color_preview_button.setStyleSheet(f"background-color: {self.current_vertex_color.name()}")
            self.color_preview_button.setText("选择颜色")
        else:
            self.current_vertex_color.setNamedColor("lightgray")
            self.color_preview_button.setStyleSheet(f"background-color: lightgray;")
            self.color_preview_button.setText("多个颜色")

        # 顶点标记 (Marker)
        initial_marker = getattr(first_vertex, 'marker', 'o')
        if all(getattr(v, 'marker', 'o') == initial_marker for v in self.all_vertices):
            index = self.marker_combobox.findText(initial_marker)
            if index != -1:
                self.marker_combobox.setCurrentIndex(index)
            else:
                self.marker_combobox.setCurrentText('o')
        else:
            self.marker_combobox.setCurrentIndex(-1)
            # QComboBox doesn't have placeholderText; text becomes empty when no item is selected
            # You could add a temporary item if you really want a placeholder string
            # self.marker_combobox.setPlaceholderText("多个值") # Not available

        # 顶点透明度 (Alpha)
        initial_alpha = getattr(first_vertex, 'alpha', 1.0)
        if all(getattr(v, 'alpha', 1.0) == initial_alpha for v in self.all_vertices):
            self.alpha_spinbox.setValue(int(initial_alpha * 100))
            self._alpha_multiple_values = False
        else:
            self.alpha_spinbox.clear()
            self._alpha_multiple_values = True

        # 顶点边缘颜色 (Edgecolor)
        initial_edgecolor = getattr(first_vertex, 'edgecolor', first_vertex.color if hasattr(first_vertex, 'color') else 'blue')
        if all(getattr(v, 'edgecolor', v.color if hasattr(v, 'color') else 'blue') == initial_edgecolor for v in self.all_vertices):
            self.current_edge_color.setNamedColor(initial_edgecolor)
            self.edgecolor_preview_button.setStyleSheet(f"background-color: {self.current_edge_color.name()}")
            self.edgecolor_preview_button.setText("选择边缘颜色")
        else:
            self.current_edge_color.setNamedColor("lightgray")
            self.edgecolor_preview_button.setStyleSheet(f"background-color: lightgray;")
            self.edgecolor_preview_button.setText("多个颜色")

        # 顶点线宽 (Linewidth)
        initial_linewidth = getattr(first_vertex, 'linewidth', 1.0)
        if all(getattr(v, 'linewidth', 1.0) == initial_linewidth for v in self.all_vertices):
            self.linewidth_spinbox.setValue(int(initial_linewidth))
            self._linewidth_multiple_values = False
        else:
            self.linewidth_spinbox.clear()
            self._linewidth_multiple_values = True

        # 标签大小 (Label Size)
        initial_label_size = getattr(first_vertex, 'label_size', 30)
        if all(getattr(v, 'label_size', 30) == initial_label_size for v in self.all_vertices):
            self.label_size_spinbox.setValue(initial_label_size)
            self._label_size_multiple_values = False
        else:
            self.label_size_spinbox.clear()
            self._label_size_multiple_values = True

        # 标签颜色 (Label Color)
        initial_label_color = getattr(first_vertex, 'label_color', 'black')
        if all(getattr(v, 'label_color', 'black') == initial_label_color for v in self.all_vertices):
            self.current_label_color.setNamedColor(initial_label_color)
            self.label_color_preview_button.setStyleSheet(f"background-color: {self.current_label_color.name()}")
            self.label_color_preview_button.setText("选择标签颜色")
        else:
            self.current_label_color.setNamedColor("lightgray")
            self.label_color_preview_button.setStyleSheet(f"background-color: lightgray;")
            self.label_color_preview_button.setText("多个颜色")

    def _select_vertex_color(self):
        """打开颜色选择器，选择顶点颜色。"""
        initial_color_for_dialog = self.current_vertex_color if self.color_preview_button.text() != "多个颜色" else QColor(Qt.blue)
        color = QColorDialog.getColor(initial_color_for_dialog, self)
        if color.isValid():
            self.current_vertex_color = color
            self.color_preview_button.setStyleSheet(f"background-color: {color.name()}")
            self.color_preview_button.setText("选择颜色")

    def _select_edge_color(self):
        """打开颜色选择器，选择边缘颜色。"""
        initial_color_for_dialog = self.current_edge_color if self.edgecolor_preview_button.text() != "多个颜色" else QColor(Qt.blue)
        color = QColorDialog.getColor(initial_color_for_dialog, self)
        if color.isValid():
            self.current_edge_color = color
            self.edgecolor_preview_button.setStyleSheet(f"background-color: {color.name()}")
            self.edgecolor_preview_button.setText("选择边缘颜色")

    def _select_label_color(self):
        """打开颜色选择器，选择标签颜色。"""
        initial_color_for_dialog = self.current_label_color if self.label_color_preview_button.text() != "多个颜色" else QColor(Qt.black)
        color = QColorDialog.getColor(initial_color_for_dialog, self)
        if color.isValid():
            self.current_label_color = color
            self.label_color_preview_button.setStyleSheet(f"background-color: {color.name()}")
            self.label_color_preview_button.setText("选择标签颜色")

    def _on_accepted(self):
        """处理OK按钮点击事件，应用设置并发出信号。"""

        # 标签前缀
        new_prefix_text = self.label_prefix_input.text()
        print(f"new_prefix_text: {new_prefix_text}, empty:{new_prefix_text == ''}")
        # QLineEdit handles placeholderText directly, so this check is fine
        apply_label_prefix = new_prefix_text
        # print(f"apply_label_prefix: {apply_label_prefix}")

        # 标签偏移 - 使用内部标志
        apply_offset_x = not self._offset_x_multiple_values
        new_offset_x = self.offset_x_spinbox.value() if apply_offset_x else None

        apply_offset_y = not self._offset_y_multiple_values
        new_offset_y = self.offset_y_spinbox.value() if apply_offset_y else None

        # 顶点大小 - 使用内部标志
        apply_size = not self._size_multiple_values
        new_size = self.size_spinbox.value() if apply_size else None

        # 顶点颜色
        apply_color = self.color_preview_button.text() != "多个颜色"
        new_color = self.current_vertex_color.name() if apply_color else None

        # 顶点标记
        apply_marker = self.marker_combobox.currentIndex() != -1
        new_marker = self.marker_combobox.currentText() if apply_marker else None

        # 顶点透明度 - 使用内部标志
        apply_alpha = not self._alpha_multiple_values
        new_alpha = self.alpha_spinbox.value() / 100.0 if apply_alpha else None

        # 顶点边缘颜色
        apply_edgecolor = self.edgecolor_preview_button.text() != "多个颜色"
        new_edgecolor = self.current_edge_color.name() if apply_edgecolor else None

        # 顶点线宽 - 使用内部标志
        apply_linewidth = not self._linewidth_multiple_values
        new_linewidth = self.linewidth_spinbox.value() if apply_linewidth else None

        # 标签大小 - 使用内部标志
        apply_label_size = not self._label_size_multiple_values
        new_label_size = self.label_size_spinbox.value() if apply_label_size else None

        # 标签颜色
        apply_label_color = self.label_color_preview_button.text() != "多个颜色"
        new_label_color = self.current_label_color.name() if apply_label_color else None

        for vertex in self.all_vertices:
            # 标签前缀修改逻辑
            if apply_label_prefix:
                if new_prefix_text == " ":
                    vertex.label = ""
                else:
                    vertex.label = new_prefix_text

            if new_size is not None:
                vertex.size = new_size
            if new_color is not None:
                vertex.color = new_color
            if new_marker is not None:
                vertex.marker = new_marker
            if new_alpha is not None:
                vertex.alpha = new_alpha
            if new_edgecolor is not None:
                vertex.edgecolor = new_edgecolor
            if new_linewidth is not None:
                vertex.linewidth = new_linewidth
            if new_label_size is not None:
                vertex.label_size = new_label_size
            if new_label_color is not None:
                vertex.label_color = new_label_color

            current_label_offset = getattr(vertex, 'label_offset', np.array([0.0, 0.0]))

            temp_offset_x = current_label_offset[0] if new_offset_x is None else new_offset_x
            temp_offset_y = current_label_offset[1] if new_offset_y is None else new_offset_y

            if new_offset_x is not None or new_offset_y is not None:
                vertex.label_offset = np.array([temp_offset_x, temp_offset_y])

        QMessageBox.information(self, "成功", f"属性已成功应用于 {len(self.all_vertices)} 个顶点。")
        self.settings_applied.emit()
        self.accept()

    @staticmethod
    def show_dialog(all_vertices: list[Vertex], parent=None) -> bool:
        """
        显示对话框的静态方法，简化外部调用。
        返回True如果用户点击了OK，否则返回False。
        """
        dialog = EditAllVerticesDialog(all_vertices, parent)
        return dialog.exec() == QDialog.Accepted