# feynplot_GUI/feynplot_gui/dialogs/delete_vertex_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QLabel, QCheckBox, QMessageBox,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from feynplot.core.line import * # Assuming these are needed for line info display
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
from typing import Optional # Import Optional for type hinting

class DeleteVertexDialog(QDialog):
    def __init__(self, diagram: FeynmanDiagram, vertex_to_delete: Optional[Vertex] = None, parent=None):
        """
        初始化删除顶点对话框。

        Args:
            diagram (FeynmanDiagram): 当前的费曼图模型。
            vertex_to_delete (Optional[Vertex]): 可选参数，如果提供，则预选并锁定此顶点。
                                                  默认为 None。
            parent (QWidget, optional): 对话框的父控件。
        """
        super().__init__(parent)
        self.setWindowTitle("删除顶点确认")
        self.setMinimumWidth(400)

        self.diagram = diagram
        self.vertices_data = diagram.vertices

        # 将传入的预选顶点保存到实例变量
        self._pre_selected_vertex = vertex_to_delete
        self.selected_vertex: Vertex | None = None # This will be set by combobox or pre-selection

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
            
            # 如果提供了预选顶点，则设置并锁定下拉框
            if self._pre_selected_vertex:
                index = self.vertex_combobox.findData(self._pre_selected_vertex)
                if index != -1:
                    self.vertex_combobox.setCurrentIndex(index)
                    self.vertex_combobox.setEnabled(False) # 锁定下拉框
                else:
                    # 如果预选顶点不在当前图中，则退回正常模式并警告
                    QMessageBox.warning(self, "警告", "预选顶点在图中不存在，请手动选择。")
                    self._pre_selected_vertex = None # 清除预选状态
            
            # 如果没有预选，或者预选失败，确保下拉框是可交互的
            if not self._pre_selected_vertex:
                self.vertex_combobox.setEnabled(True)

        self.vertex_combobox.currentIndexChanged.connect(self._update_associated_lines_display)

        self.associated_lines_label = QLabel(self.tr("关联线条:"))
        self.associated_lines_label.setWordWrap(True)
        
        self.associated_lines_text_area = QLabel(self.tr("请选择一个顶点以查看其关联的线条。"))
        self.associated_lines_text_area.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid lightgray;")
        self.associated_lines_text_area.setWordWrap(True)
        self.associated_lines_text_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(400)

        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)
        scroll_area_layout.setContentsMargins(0,0,0,0)
        scroll_area_layout.addWidget(self.associated_lines_text_area)
        scroll_area_content.setLayout(scroll_area_layout)
        self.scroll_area.setWidget(scroll_area_content)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.associated_lines_label)
        main_layout.addWidget(self.scroll_area)

        self.confirm_checkbox = QCheckBox(self.tr("我确认删除此顶点及其所有关联的线条。"))
        self.confirm_checkbox.setEnabled(True) 
        self.confirm_checkbox.stateChanged.connect(self._update_ok_button_state)
        main_layout.addWidget(self.confirm_checkbox)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._on_ok_clicked)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # Initial state setup
        if not self.vertices_data:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.vertex_combobox.setEnabled(False)
            self.confirm_checkbox.setEnabled(False)
            self.associated_lines_text_area.setText(self.tr("图中目前没有可供删除的顶点。"))
            self.scroll_area.setFixedHeight(self.scroll_area.minimumHeight())
        else:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            # Ensure the display is updated based on the initial selection (could be pre-selected)
            self._update_associated_lines_display()


    def _update_associated_lines_display(self):
        """
        更新显示选定顶点的关联线条信息。
        """
        self.selected_vertex = self.vertex_combobox.currentData()
        
        if not self.selected_vertex:
            self.associated_lines_text_area.setText(self.tr("请选择一个顶点以查看其关联的线条。"))
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
            self.confirm_checkbox.setEnabled(True)
            self.confirm_checkbox.setChecked(False) # Always uncheck to force explicit confirmation
        else:
            display_text = "此顶点没有关联的线条。"
            self.confirm_checkbox.setEnabled(True) # Even if no lines, user still needs to confirm vertex deletion
            self.confirm_checkbox.setChecked(True) # Auto-check if no lines, indicating "no lines to delete"

        self.associated_lines_text_area.setText(display_text)

        # Dynamic height adjustment based on content, within limits
        # To make the scroll area adjust its height to the content within the min/max range
        # You need to temporarily set the text on a dummy QLabel to get its size hint
        dummy_label = QLabel(display_text)
        dummy_label.setWordWrap(True)
        dummy_label.adjustSize() # Adjusts to content height
        content_height = dummy_label.height()

        final_height = max(self.scroll_area.minimumHeight(), min(content_height, self.scroll_area.maximumHeight()))
        self.scroll_area.setFixedHeight(final_height)

        self._update_ok_button_state()

    def _update_ok_button_state(self):
        """
        根据复选框状态和选定顶点启用/禁用 OK 按钮。
        """
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        
        if self.selected_vertex:
            # OK button is enabled only if the checkbox is checked.
            # This applies whether there are associated lines or not.
            ok_button.setEnabled(self.confirm_checkbox.isChecked())
        else:
            # If no vertex is selected (e.g., initial state with no vertices or "None" selected), OK button is disabled.
            ok_button.setEnabled(False)

    def _on_ok_clicked(self):
        """
        OK 按钮的自定义处理程序，在接受前执行最终检查。
        """
        if self.selected_vertex:
            # The _update_ok_button_state already ensures the OK button is disabled if
            # the checkbox isn't checked when there are lines.
            # However, an explicit check here provides a user-friendly warning.
            associated_line_ids = self.diagram.get_associated_line_ids(self.selected_vertex.id)
            if associated_line_ids and not self.confirm_checkbox.isChecked():
                QMessageBox.warning(self, "确认删除", "请勾选确认框以删除顶点及其关联的线条。")
                return # Prevent dialog from closing
            
            self.accept() # Close dialog with QDialog.Accepted result
        else:
            QMessageBox.warning(self, "选择顶点", "请选择一个要删除的顶点。")

    def get_selected_vertex_id(self) -> Optional[str]:
        """
        获取用户选择的要删除的顶点ID。
        """
        if self.vertex_combobox.isEnabled() and self.vertex_combobox.count() > 0:
            selected_vertex = self.vertex_combobox.currentData()
            if selected_vertex:
                return selected_vertex.id
        return self._pre_selected_vertex.id if self._pre_selected_vertex else None