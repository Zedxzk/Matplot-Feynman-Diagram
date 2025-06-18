# feynplot_GUI/feynplot_gui/dialogs/delete_vertex_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QCheckBox, QMessageBox,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt
# QFontMetrics 不再需要，已移除导入
from feynplot.core.line import *
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex

class DeleteVertexDialog(QDialog):
    def __init__(self, diagram: FeynmanDiagram, parent=None):
        super().__init__(parent)
        self.setWindowTitle("删除顶点确认")
        self.setMinimumWidth(400)

        self.diagram = diagram
        self.vertices_data = diagram.vertices

        self.selected_vertex: Vertex | None = None

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.vertex_combobox = QComboBox()
        form_layout.addRow("选择要删除的顶点", self.vertex_combobox)

        if not self.vertices_data:
            self.vertex_combobox.addItem("无可用顶点")
            self.vertex_combobox.setEnabled(False)
        else:
            for i, vertex in enumerate(self.vertices_data):
                display_text = f"{vertex.id}: {vertex.label} ({vertex.x:.2f},{vertex.y:.2f})"
                self.vertex_combobox.addItem(display_text, vertex)

        self.vertex_combobox.currentIndexChanged.connect(self._update_associated_lines_display)

        self.associated_lines_label = QLabel("关联线条:")
        self.associated_lines_label.setWordWrap(True)
        
        self.associated_lines_text_area = QLabel("请选择一个顶点以查看其关联的线条。")
        self.associated_lines_text_area.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid lightgray;")
        self.associated_lines_text_area.setWordWrap(True)
        self.associated_lines_text_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(50)
        self.scroll_area.setMaximumHeight(200) # 保持这个最大高度，以防内容过多

        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)
        scroll_area_layout.setContentsMargins(0,0,0,0)
        scroll_area_layout.addWidget(self.associated_lines_text_area)
        scroll_area_content.setLayout(scroll_area_layout)
        self.scroll_area.setWidget(scroll_area_content)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.associated_lines_label)
        main_layout.addWidget(self.scroll_area)


        self.confirm_checkbox = QCheckBox("我确认删除此顶点及其所有关联的线条。")
        # 初始时，复选框应为可交互状态，除非没有顶点
        self.confirm_checkbox.setEnabled(True) 
        self.confirm_checkbox.stateChanged.connect(self._update_ok_button_state)
        main_layout.addWidget(self.confirm_checkbox)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._on_ok_clicked)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # 初始状态设置
        if not self.vertices_data:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.vertex_combobox.setEnabled(False) # 确保下拉框禁用
            self.confirm_checkbox.setEnabled(False) # 没有顶点时，复选框也禁用
            self.associated_lines_text_area.setText("图中目前没有可供删除的顶点。")
            self.scroll_area.setFixedHeight(self.scroll_area.minimumHeight())
        else:
            # 初始时，OK 按钮默认禁用，直到用户操作
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            # 触发第一次更新显示，基于默认选中的顶点
            self._update_associated_lines_display()


    def _update_associated_lines_display(self):
        self.selected_vertex = self.vertex_combobox.currentData()
        
        if not self.selected_vertex:
            self.associated_lines_text_area.setText("请选择一个顶点以查看其关联的线条。")
            self.confirm_checkbox.setEnabled(False)
            self.confirm_checkbox.setChecked(False)
            self._update_ok_button_state()
            self.scroll_area.setFixedHeight(self.scroll_area.minimumHeight())
            return

        associated_line_ids = self.diagram.get_associated_line_ids(self.selected_vertex.id)
        
        lines_info = []
        if associated_line_ids:
            for line_id in associated_line_ids:
                line = self.diagram.get_line_by_id(line_id)
                if line:
                    start_id = line.v_start.id if line.v_start else "N/A"
                    end_id = line.v_end.id if line.v_end else "N/A"
                    lines_info.append(f"- {line.id} ({type(line).__name__}) from {start_id} to {end_id}")
            
            display_text = "将同时删除以下关联线条：\n" + "\n".join(lines_info)
            self.confirm_checkbox.setEnabled(True) # 有关联线条时，启用复选框
            self.confirm_checkbox.setChecked(False) # 默认不勾选，强制用户手动确认
        else:
            display_text = "此顶点没有关联的线条。"
            self.confirm_checkbox.setEnabled(False) # 没有关联线条时，禁用复选框
            self.confirm_checkbox.setChecked(True) # 自动勾选，表示无需额外确认
        
        self.associated_lines_text_area.setText(display_text)

        # --- Fixed Height Adjustment ---
        fixed_height_for_content = 500 
        final_height = max(self.scroll_area.minimumHeight(), min(fixed_height_for_content, self.scroll_area.maximumHeight()))
        self.scroll_area.setFixedHeight(final_height)
        # --- End Fixed Height Adjustment ---

        self._update_ok_button_state()

    def _update_ok_button_state(self):
        """
        Enables/disables the OK button based on checkbox state and selected vertex.
        """
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        
        if self.selected_vertex:
            associated_line_ids = self.diagram.get_associated_line_ids(self.selected_vertex.id)
            if associated_line_ids:
                # 如果有关联线条，OK按钮取决于复选框是否被勾选
                ok_button.setEnabled(self.confirm_checkbox.isChecked())
            else:
                # 如果没有关联线条，OK按钮直接可用
                ok_button.setEnabled(True)
        else:
            # 如果没有选中任何顶点，OK按钮不可用
            ok_button.setEnabled(False)

    def _on_ok_clicked(self):
        """
        Custom handler for the OK button to perform final checks before accepting.
        """
        if self.selected_vertex:
            associated_line_ids = self.diagram.get_associated_line_ids(self.selected_vertex.id)
            if associated_line_ids and not self.confirm_checkbox.isChecked():
                QMessageBox.warning(self, "确认删除", "请勾选确认框以删除顶点及其关联的线条。")
                return
            
            self.accept()
        else:
            QMessageBox.warning(self, "选择顶点", "请选择一个要删除的顶点。")

    def get_selected_vertex_id(self) :
        if self.vertex_combobox.isEnabled() and self.vertex_combobox.count() > 0:
            selected_vertex = self.vertex_combobox.currentData()
            if selected_vertex:
                return selected_vertex.id
        return None