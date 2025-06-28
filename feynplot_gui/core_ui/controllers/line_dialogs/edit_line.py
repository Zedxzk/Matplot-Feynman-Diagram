# feynplot_gui/controllers/line_dialogs/edit_line.py

from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QColorDialog, QGroupBox,
    QScrollArea, QWidget, QFormLayout
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, Signal
from typing import Optional, Dict, Any, Type

# 引入所有具体的线条类型
from feynplot.core.line import (
    Line, LineStyle,
    FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine
)
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
import numpy as np

# 导入新的模块化编辑器
from feynplot_gui.core_ui.controllers.line_dialogs.line_edit_base import LineEditBase
from feynplot_gui.core_ui.controllers.line_dialogs.specific_line_editors.fermion_line_editor import FermionLineEditor
from feynplot_gui.core_ui.controllers.line_dialogs.specific_line_editors.photon_line_editor import PhotonLineEditor
from feynplot_gui.core_ui.controllers.line_dialogs.specific_line_editors.gluon_line_editor import GluonLineEditor
from feynplot_gui.core_ui.controllers.line_dialogs.specific_line_editors.wz_boson_line_editor import WZBosonLineEditor


def open_edit_line_dialog(line: Line, diagram_model: FeynmanDiagram, parent_widget=None) -> bool:
    """
    Opens a dialog to edit the properties of a given Line object.
    This function is now exclusively for editing existing lines.
    """
    # 确保 line 参数是一个 Line 实例，因为现在只处理编辑模式
    if not isinstance(line, Line):
        QMessageBox.critical(parent_widget, "错误", "提供的对象不是一个有效的线条，无法编辑。")
        return False

    class _InternalEditLineDialog(QDialog, LineEditBase):
        line_updated = Signal(Line, Optional[Line])

        def __init__(self, line_obj: Line, diagram_model: FeynmanDiagram, parent_dialog=None):
            super().__init__(parent_dialog)
            LineEditBase.__init__(self)

            # 现在 line_obj 永远不会是 None，因为我们只处理编辑模式
            self.line = line_obj
            self.diagram_model = diagram_model

            # 存储原始线条的顶点和ID，以便在类型改变时重新创建线条
            self._original_v_start = line_obj.v_start
            self._original_v_end = line_obj.v_end
            self._original_line_id = line_obj.id

            # 对话框标题现在只显示编辑模式下的标题
            dialog_title = f"编辑线条: {self.line.label} (ID: {self.line.id})"
            self.setWindowTitle(dialog_title)
            self.setGeometry(200, 200, 480, 750)
            self.setMinimumHeight(300)
            self.setMaximumHeight(800)

            # --- 主对话框布局 ---
            self.main_dialog_layout = QVBoxLayout(self)

            # --- 滚动区域，用于承载所有属性控件 ---
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_content_widget = QWidget()
            self.main_form_layout = QFormLayout(self.scroll_content_widget)
            self.scroll_area.setWidget(self.scroll_content_widget)
            self.main_dialog_layout.addWidget(self.scroll_area)

            # --- 1. ID (永远只读，使用 QLabel 显示) ---
            # 移除 QLineEdit 和 setReadOnly(True)
            self._current_line_id_str = self.line.id 

            # QLabel 只用于显示，用纯字符串来构建显示文本
            self.id_label = QLabel(self)
            self.id_label.setTextFormat(Qt.RichText)
            self.id_label.setText(f"<b>{self._current_line_id_str}</b>") # 使用 _current_line_id_str 来设置显示文本
            self.main_form_layout.addRow("ID:", self.id_label)

            # --- 2. 标签 (Label) ---
            self.label_input = QLineEdit(self)
            self.label_input.setText(self.line.label)
            self.main_form_layout.addRow("标签:", self.label_input)

            # --- 3. 起点和终点 (只读信息) ---
            start_label = self._original_v_start.label if self._original_v_start else '无'
            start_id = self._original_v_start.id if self._original_v_start else 'N/A'
            end_label = self._original_v_end.label if self._original_v_end else '无'
            end_id = self._original_v_end.id if self._original_v_end else 'N/A'
            self.main_form_layout.addRow(QLabel(self.tr("<b>起点:</b>")), QLabel(f"{start_label} (ID: {start_id})"))
            self.main_form_layout.addRow(QLabel(self.tr("<b>终点:</b>")), QLabel(f"{end_label} (ID: {end_id})"))

            # --- 4. 线条粒子类型选择 (Line Type Selection) ---
            self.particle_type_combo = QComboBox(self)
            self.particle_types: Dict[str, Type[Line]] = {
                "费米子线 (Fermion)": FermionLine,
                "反费米子线 (Anti-Fermion)": AntiFermionLine,
                "光子线 (Photon)": PhotonLine,
                "胶子线 (Gluon)": GluonLine,
                "W+ 玻色子线 (W+)": WPlusLine,
                "W- 玻色子线 (W-)": WMinusLine,
                "Z 玻色子线 (Z)": ZBosonLine,
            }

            current_particle_type_class = type(self.line)
            current_index = -1
            for i, (display_name, particle_class) in enumerate(self.particle_types.items()):
                self.particle_type_combo.addItem(display_name, particle_class)
                if particle_class == current_particle_type_class:
                    current_index = i

            if current_index != -1:
                self.particle_type_combo.setCurrentIndex(current_index)
            else:  # 如果编辑的线条类型不在列表中
                self.particle_type_combo.addItem("未知类型", None)
                self.particle_type_combo.setCurrentIndex(self.particle_type_combo.count() - 1)
                QMessageBox.warning(self, "警告", f"当前线条类型 '{current_particle_type_class.__name__}' 不在可选择列表中。")

            self.main_form_layout.addRow("线条粒子类型:", self.particle_type_combo)

            # --- 5. 线条样式 (LineStyle 枚举) ---
            self.line_style_combo = QComboBox(self)
            for style_enum in LineStyle:
                self.line_style_combo.addItem(style_enum.name.replace('_', ' ').title(), style_enum)

            # 遍历 QComboBox 的所有项目，找到数据匹配的项并设置当前索引
            target_style = self.line.style
            found_index = -1
            for i in range(self.line_style_combo.count()):
                item_data = self.line_style_combo.itemData(i)
                if item_data == target_style:
                    found_index = i
                    break
            if found_index != -1:
                self.line_style_combo.setCurrentIndex(found_index)
            else:
                print(f"Warning: LineStyle '{target_style}' not found in QComboBox items. Defaulting to first item.")
                self.line_style_combo.setCurrentIndex(0)  # 默认选中第一个

            self.main_form_layout.addRow("线条样式:", self.line_style_combo)

            # --- 6. 颜色 (color) ---
            self.color_button = QPushButton("选择颜色", self)
            self._line_color_picked_color = self.line.color
            self._set_button_color(self.color_button, self._line_color_picked_color)
            self.color_button.clicked.connect(lambda: self._pick_color(self.color_button, '_line_color_picked_color'))
            self.main_form_layout.addRow("线条颜色:", self.color_button)

            # --- 7. 线宽 (linewidth) ---
            initial_linewidth = self.line.linewidth
            self.linewidth_layout, self.linewidth_input = self._create_spinbox_row(
                "线宽:", initial_linewidth, min_val=0.1, max_val=10.0, step=0.1
            )
            self.main_form_layout.addRow(self.linewidth_layout)

            # --- 8. 透明度 (alpha) ---
            initial_alpha = self.line.alpha
            self.alpha_layout, self.alpha_input = self._create_spinbox_row(
                "透明度:", initial_alpha, min_val=0.0, max_val=1.0, step=0.01
            )
            self.main_form_layout.addRow(self.alpha_layout)

            # --- 9. Matplotlib 线型 (linestyle) ---
            self.mpl_linestyle_combo = QComboBox(self)
            mpl_line_styles = ['-', '--', '-.', ':', 'None', ' ', '']  # Matplotlib 常见的线条样式
            for style_str in mpl_line_styles:
                self.mpl_linestyle_combo.addItem(style_str if style_str != '' else '(空)')

            current_mpl_ls = self.line.linestyle if self.line.linestyle is not None else '-'
            self.mpl_linestyle_combo.setCurrentText(current_mpl_ls if current_mpl_ls != '' else '(空)')
            self.main_form_layout.addRow("Matplotlib 线型:", self.mpl_linestyle_combo)

            # --- 10. Z-order ---
            initial_zorder = self.line.zorder
            self.zorder_layout, self.zorder_input = self._create_spinbox_row(
                "Z轴顺序:", initial_zorder, min_val=-100, max_val=100, step=1, is_int=True
            )
            self.main_form_layout.addRow(self.zorder_layout)

            # --- 11. 标签字体大小 (label_fontsize) ---
            initial_label_fontsize = self.line.label_fontsize
            self.label_fontsize_layout, self.label_fontsize_input = self._create_spinbox_row(
                "标签字体大小:", initial_label_fontsize, min_val=1.0, max_val=72.0, step=0.5, is_int=True
            )
            self.main_form_layout.addRow(self.label_fontsize_layout)

            # --- 12. 标签颜色 (label_color) ---
            self.label_color_button = QPushButton("选择颜色", self)
            self._label_color_picked_color = self.line.label_color
            self._set_button_color(self.label_color_button, self._label_color_picked_color)
            self.label_color_button.clicked.connect(lambda: self._pick_color(self.label_color_button, '_label_color_picked_color'))
            self.main_form_layout.addRow("标签颜色:", self.label_color_button)

            # --- 13. 标签水平对齐 (label_ha) ---
            self.label_ha_combo = QComboBox(self)
            self.label_ha_combo.addItems(['left', 'right', 'center'])
            self.label_ha_combo.setCurrentText(self.line.label_ha)
            self.main_form_layout.addRow("标签水平对齐:", self.label_ha_combo)

            # --- 14. 标签垂直对齐 (label_va) ---
            self.label_va_combo = QComboBox(self)
            self.label_va_combo.addItems(['top', 'bottom', 'center', 'baseline'])
            self.label_va_combo.setCurrentText(self.line.label_va)
            self.main_form_layout.addRow("标签垂直对齐:", self.label_va_combo)

            # --- 15. 标签偏移 X, Y (label_offset) ---
            label_offset_x = self.line.label_offset[0]
            label_offset_y = self.line.label_offset[1]

            self.label_offset_x_layout, self.label_offset_x_input = self._create_spinbox_row("标签偏移 X:", label_offset_x, min_val=-10.0, max_val=10.0, step=0.1)
            self.label_offset_y_layout, self.label_offset_y_input = self._create_spinbox_row("标签偏移 Y:", label_offset_y, min_val=-10.0, max_val=10.0, step=0.1)
            self.main_form_layout.addRow(self.label_offset_x_layout)
            self.main_form_layout.addRow(self.label_offset_y_layout)

            # --- 16. 入角 (angleIn) ---
            initial_angle_in = self.line._angleIn if self.line._angleIn is not None else 0.0
            self.angle_in_layout, self.angle_in_input = self._create_spinbox_row(
                "入角 (Angle In):", initial_angle_in, min_val=-180.0, max_val=180.0, step=1.0
            )
            self.main_form_layout.addRow(self.angle_in_layout)

            # --- 17. 出角 (angleOut) ---
            initial_angle_out = self.line._angleOut if self.line._angleOut is not None else 0.0
            self.angle_out_layout, self.angle_out_input = self._create_spinbox_row(
                "出角 (Angle Out):", initial_angle_out, min_val=-180.0, max_val=180.0, step=1.0
            )
            self.main_form_layout.addRow(self.angle_out_layout)

            # --- 18. 贝塞尔偏移 (bezier_offset) ---
            initial_bezier_offset = self.line.bezier_offset
            self.bezier_offset_layout, self.bezier_offset_input = self._create_spinbox_row(
                "贝塞尔偏移:", initial_bezier_offset, min_val=0.0, max_val=1.0, step=0.01
            )
            self.main_form_layout.addRow(self.bezier_offset_layout)

            # --- 特定线条类型的属性组 (由各自的编辑器管理) ---
            self.fermion_editor = FermionLineEditor(self.main_form_layout, self.line)
            self.photon_editor = PhotonLineEditor(self.main_form_layout, self.line)
            self.gluon_editor = GluonLineEditor(self.main_form_layout, self.line)
            self.wz_boson_editor = WZBosonLineEditor(self.main_form_layout, self.line)

            # 存储所有特定编辑器实例，以便动态显示/隐藏
            self.specific_editors = {
                FermionLine: self.fermion_editor,
                AntiFermionLine: self.fermion_editor,
                PhotonLine: self.photon_editor,
                GluonLine: self.gluon_editor,
                WPlusLine: self.wz_boson_editor,
                WMinusLine: self.wz_boson_editor,
                ZBosonLine: self.wz_boson_editor,
            }

            # 连接线条类型选择框的信号到更新函数
            self.particle_type_combo.currentIndexChanged.connect(self._update_specific_properties_ui)

            # 初始 UI 显示：根据当前线条类型显示对应的特定属性
            self._update_specific_properties_ui(self.particle_type_combo.currentIndex())

            # --- 确定/取消按钮 ---
            button_layout = QHBoxLayout()
            ok_button = QPushButton(self.tr("确定"))
            ok_button.clicked.connect(self.accept)
            cancel_button = QPushButton(self.tr("取消"))
            cancel_button.clicked.connect(self.reject)
            button_layout.addStretch(1)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            self.main_dialog_layout.addLayout(button_layout)

        # --- 辅助方法 (从 LineEditBase 继承，或直接实现) ---
        def _update_color_label(self):
            """更新线条颜色按钮的背景色"""
            self.color_button.setStyleSheet(f"background-color: {self._line_color_picked_color}; border: 1px solid black;")

        def _select_color(self):
            """打开颜色选择器，更新线条颜色"""
            initial_qcolor = QColor(self._line_color_picked_color)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                self._line_color_picked_color = color.name()
                self._update_color_label()

        def _update_label_color_label(self):
            """更新标签颜色按钮的背景色"""
            self.label_color_button.setStyleSheet(f"background-color: {self._label_color_picked_color}; border: 1px solid black;")

        def _select_label_color(self):
            """打开颜色选择器，更新标签颜色"""
            initial_qcolor = QColor(self._label_color_picked_color)
            color = QColorDialog.getColor(initial_qcolor, self)
            if color.isValid():
                self._label_color_picked_color = color.name()
                self._update_label_color_label()

        def _update_specific_properties_ui(self, index: int):
            """隐藏所有特定属性编辑器，并只显示相关的那个。"""
            selected_class = self.particle_type_combo.itemData(index)

            # 首先隐藏所有编辑器
            for editor in set(self.specific_editors.values()):  # 使用 set 处理共享编辑器
                editor.set_visible(False)

            # 显示选定类型对应的编辑器
            if selected_class in self.specific_editors:
                editor_to_show = self.specific_editors[selected_class]
                # 在显示之前，确保编辑器持有的 line 对象是当前对话框的 line 对象
                editor_to_show.line = self.line
                editor_to_show.set_visible(True)
                editor_to_show._load_properties()

        def accept(self):
            """当点击 OK 按钮时调用。更新 Line 对象的属性。
            如果线条类型发生变化，将替换原始线条。
            """
            new_line_id = self._current_line_id_str
            # ID现在是只读，所以new_line_id总是等于self._original_line_id
            # 移除ID冲突检查，因为ID不能被修改
            
            selected_particle_class = self.particle_type_combo.currentData()
            selected_line_style_enum = self.line_style_combo.currentData()  # 获取 LineStyle 枚举成员

            # 从 UI 获取所有通用属性
            common_kwargs = {
                'label': self.label_input.text(),
                'label_offset': np.array([self.label_offset_x_input.value(), self.label_offset_y_input.value()]),
                'bezier_offset': float(self.bezier_offset_input.value()),
                'linewidth': float(self.linewidth_input.value()),
                'color': self._line_color_picked_color,
                'linestyle': self.mpl_linestyle_combo.currentText() if self.mpl_linestyle_combo.currentText() != '(空)' else None,
                'alpha': float(self.alpha_input.value()),
                'zorder': int(self.zorder_input.value()),
                'label_fontsize': int(self.label_fontsize_input.value()),
                'label_color': self._label_color_picked_color,
                'label_ha': self.label_ha_combo.currentText(),
                'label_va': self.label_va_combo.currentText(),
                'style': selected_line_style_enum,
            }

            # 处理 angleIn 和 angleOut 的“自动”选项 (None)
            if self.angle_in_input.text() == self.angle_in_input.specialValueText():
                common_kwargs['angleIn'] = None
            else:
                common_kwargs['angleIn'] = float(self.angle_in_input.value())

            if self.angle_out_input.text() == self.angle_out_input.specialValueText():
                common_kwargs['angleOut'] = None
            else:
                common_kwargs['angleOut'] = float(self.angle_out_input.value())

            # 获取特定线条类型的参数
            specific_kwargs = {}
            if selected_particle_class in self.specific_editors:
                current_editor = self.specific_editors[selected_particle_class]
                specific_kwargs = current_editor.get_specific_kwargs()

            # 合并所有 kwargs
            all_kwargs = {**common_kwargs, **specific_kwargs}

            # --- 线条类型发生变化时的处理逻辑 ---
            if type(self.line) != selected_particle_class:
                # 移除旧线条
                self.diagram_model.remove_line(self._original_line_id)

                # 创建新的线条实例
                new_line_instance = selected_particle_class(
                    v_start=self._original_v_start,
                    v_end=self._original_v_end,
                    id=new_line_id,
                    **all_kwargs
                )

                try:
                    # 使用 diagram_model 的 add_line 方法 (它应该能处理 line 实例)
                    # 注意：diagram_model.add_line 可能需要一个 line 实例，而不是 line_type
                    # 如果 diagram_model.add_line 期望 line_type，你需要调整它或直接添加 new_line_instance
                    self.diagram_model.add_line(line=new_line_instance) # 假设 add_line 可以直接接受 Line 实例
                    
                    # 关键：更新对话框内部的 line 引用，以便 line_updated 信号传递的是正确的对象
                    self.line = new_line_instance
                    QMessageBox.information(self, "操作成功", f"线条 {new_line_id} 类型已更换并更新。")

                except ValueError as e:
                    QMessageBox.critical(self, "操作失败", str(e))
                    super().reject()
                    return
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"更新线条时发生未知错误: {e}")
                    super().reject()
                    return
            # --- 线条类型未变化时的处理逻辑 (编辑现有线条) ---
            else:
                # 直接更新现有线条的属性
                self.line.label = common_kwargs['label']
                self.line.label_offset = common_kwargs['label_offset']
                self.line.bezier_offset = common_kwargs['bezier_offset']
                self.line.linewidth = common_kwargs['linewidth']
                self.line.color = common_kwargs['color']
                self.line.linestyle = common_kwargs['linestyle']
                self.line.alpha = common_kwargs['alpha']
                self.line.zorder = common_kwargs['zorder']
                self.line.label_fontsize = common_kwargs['label_fontsize']
                self.line.label_color = common_kwargs['label_color']
                self.line.label_ha = common_kwargs['label_ha']
                self.line.label_va = common_kwargs['label_va']
                self.line.style = common_kwargs['style']
                self.line._angleIn = common_kwargs['angleIn']
                self.line._angleOut = common_kwargs['angleOut']

                # 通过特定编辑器更新其独有属性
                if selected_particle_class in self.specific_editors:
                    current_editor = self.specific_editors[selected_particle_class]
                    current_editor.apply_properties(self.line)

                QMessageBox.information(self, "操作成功", f"线条 {self.line.id} 属性已更新。")

            super().accept()  # 接受对话框

    # 在 open_edit_line_dialog 函数内部实例化并执行这个局部定义的对话框
    dialog = _InternalEditLineDialog(line, diagram_model=diagram_model, parent_dialog=parent_widget)

    if dialog.exec() == QDialog.Accepted:
        # 对话框接受后，dialog.line 已经是更新后的线条对象，并且已经在 diagram_model 中
        return True
    else:
        # 对话框取消
        QMessageBox.information(parent_widget, "编辑取消", f"线条 {line.id} 属性编辑已取消。")
        return False