# feynplot_gui/dialogs/matplotlib_settings_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QComboBox, QDialogButtonBox, QLabel, QMessageBox, QFontComboBox,
    QSpinBox, QHBoxLayout, QWidget, QGroupBox, QSpacerItem, QSizePolicy # 导入 QSpacerItem 和 QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator

from typing import Dict, Any, Optional

import matplotlib.pyplot as plt

class MatplotlibSettingsDialog(QDialog):
    """
    一个用于配置 Matplotlib 后端设置的对话框。
    它允许用户调整字体、LaTeX 支持、线条样式等参数。
    对话框初始化时会从 Matplotlib 的当前 rcParams 中读取默认值。
    """
    settings_applied = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Matplotlib 后端设置")
        self.setMinimumWidth(500)
        print(f"当前 rcParams['savefig.dpi'] 的值为: {plt.rcParams['savefig.dpi']}")

        self._current_settings = self._get_current_matplotlib_settings()

        self.init_ui()
        self.load_settings_to_ui(self._current_settings)

    def init_ui(self):
        """初始化对话框的用户界面元素和布局。"""
        main_layout = QVBoxLayout(self)

        # --- 1. 字体设置组 ---
        # 调整：现在 _create_collapsible_group_box 返回 group_box 和其内部的 content_layout
        self.font_group_box, font_layout = self._create_collapsible_group_box("字体设置")

        self.font_family_combo = QFontComboBox()
        font_layout.addRow("字体家族:", self.font_family_combo)

        font_size_layout = QHBoxLayout()
        self.font_size_edit = QLineEdit()
        self.font_size_edit.setPlaceholderText("例如: 12.0")
        self.font_size_edit.setValidator(QDoubleValidator(0.1, 100.0, 2, self))
        font_size_layout.addWidget(self.font_size_edit)
        font_size_layout.addWidget(QLabel(self.tr("pt")))
        font_layout.addRow("字体大小:", font_size_layout)
        
        main_layout.addWidget(self.font_group_box)

        # --- 2. LaTeX 设置组 ---
        self.latex_group_box, latex_layout = self._create_collapsible_group_box("LaTeX 设置")

        self.use_latex_checkbox = QCheckBox(self.tr("使用 LaTeX 渲染文本"))
        self.use_latex_checkbox.stateChanged.connect(self._on_usetex_changed)
        latex_layout.addRow("LaTeX 支持:", self.use_latex_checkbox)

        self.latex_font_family_combo = QComboBox()
        self.latex_font_family_combo.addItems([
            "serif (Times New Roman)", "sans-serif (Helvetica/Arial)", "monospace (Courier)"
        ])
        self.latex_font_family_combo.setEditable(False)
        latex_layout.addRow("LaTeX 字体家族:", self.latex_font_family_combo)
        
        main_layout.addWidget(self.latex_group_box)


        # --- 3. 线条和标记设置组 ---
        self.lines_group_box, lines_layout = self._create_collapsible_group_box("线条与标记设置")

        line_width_layout = QHBoxLayout()
        self.lines_linewidth_edit = QLineEdit()
        self.lines_linewidth_edit.setPlaceholderText("例如: 1.5")
        self.lines_linewidth_edit.setValidator(QDoubleValidator(0.1, 10.0, 2, self))
        line_width_layout.addWidget(self.lines_linewidth_edit)
        line_width_layout.addWidget(QLabel(self.tr("pt")))
        lines_layout.addRow("默认线条宽度:", line_width_layout)

        self.lines_linestyle_combo = QComboBox()
        self.lines_linestyle_combo.addItems([
            "- (实线)", "-- (虚线)", "-. (点划线)", ": (点线)"
        ])
        lines_layout.addRow("默认线条样式:", self.lines_linestyle_combo)
        
        self.lines_marker_combo = QComboBox()
        self.lines_marker_combo.addItems([
            "None", "o (圆圈)", "s (方块)", "^ (三角形)", "v (倒三角形)",
            "x (X形)", "+ (加号)", "* (星号)", "D (菱形)", "p (五边形)"
        ])
        lines_layout.addRow("默认标记样式:", self.lines_marker_combo)

        marker_size_layout = QHBoxLayout()
        self.lines_markersize_edit = QLineEdit()
        self.lines_markersize_edit.setPlaceholderText("例如: 6.0")
        self.lines_markersize_edit.setValidator(QDoubleValidator(0.1, 50.0, 2, self))
        marker_size_layout.addWidget(self.lines_markersize_edit)
        marker_size_layout.addWidget(QLabel(self.tr("pt")))
        lines_layout.addRow("默认标记大小:", marker_size_layout)

        main_layout.addWidget(self.lines_group_box)


        # --- 4. 轴与刻度设置组 ---
        self.axes_ticks_group_box, axes_ticks_layout = self._create_collapsible_group_box("轴与刻度设置")

        self.axes_labelsize_combo = QComboBox()
        self.axes_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.axes_labelsize_combo.setEditable(True)
        axes_ticks_layout.addRow("轴标签大小:", self.axes_labelsize_combo)

        self.xtick_labelsize_combo = QComboBox()
        self.xtick_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.xtick_labelsize_combo.setEditable(True)
        axes_ticks_layout.addRow("X轴刻度标签大小:", self.xtick_labelsize_combo)

        self.ytick_labelsize_combo = QComboBox()
        self.ytick_labelsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.ytick_labelsize_combo.setEditable(True)
        axes_ticks_layout.addRow("Y轴刻度标签大小:", self.ytick_labelsize_combo)
        
        self.axes_grid_checkbox = QCheckBox(self.tr("显示网格"))
        axes_ticks_layout.addRow("网格:", self.axes_grid_checkbox)

        main_layout.addWidget(self.axes_ticks_group_box)

        # --- 5. 图例设置组 ---
        self.legend_group_box, legend_layout = self._create_collapsible_group_box("图例设置")

        self.legend_fontsize_combo = QComboBox()
        self.legend_fontsize_combo.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large"])
        self.legend_fontsize_combo.setEditable(True)
        legend_layout.addRow("图例字体大小:", self.legend_fontsize_combo)

        self.legend_frameon_checkbox = QCheckBox(self.tr("显示图例边框"))
        legend_layout.addRow("图例边框:", self.legend_frameon_checkbox)

        self.legend_loc_combo = QComboBox()
        self.legend_loc_combo.addItems([
            "best", "upper right", "upper left", "lower left", "lower right",
            "right", "center left", "center right", "lower center", "upper center", "center"
        ])
        legend_layout.addRow("图例位置:", self.legend_loc_combo)
        
        main_layout.addWidget(self.legend_group_box)


        # --- 6. 图像与保存设置组 ---
        self.figure_save_group_box, figure_save_layout = self._create_collapsible_group_box("图像与保存设置")

        figure_width_layout = QHBoxLayout()
        self.figure_width_edit = QLineEdit()
        self.figure_width_edit.setPlaceholderText("例如: 6.4")
        self.figure_width_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_width_layout.addWidget(self.figure_width_edit)
        figure_width_layout.addWidget(QLabel(self.tr("英寸")))
        figure_save_layout.addRow("图像宽度:", figure_width_layout)

        figure_height_layout = QHBoxLayout()
        self.figure_height_edit = QLineEdit()
        self.figure_height_edit.setPlaceholderText("例如: 4.8")
        self.figure_height_edit.setValidator(QDoubleValidator(1.0, 20.0, 2, self))
        figure_height_layout.addWidget(self.figure_height_edit)
        figure_height_layout.addWidget(QLabel(self.tr("英寸")))
        figure_save_layout.addRow("图像高度:", figure_height_layout)

        self.savefig_dpi_edit = QLineEdit()
        self.savefig_dpi_edit.setPlaceholderText("例如: 300")
        self.savefig_dpi_edit.setValidator(QIntValidator(50, 1200, self))
        figure_save_layout.addRow("保存图片DPI:", self.savefig_dpi_edit)

        self.savefig_format_combo = QComboBox()
        self.savefig_format_combo.addItems(["png", "pdf", "svg", "jpeg", "tiff"])
        figure_save_layout.addRow("保存图片格式:", self.savefig_format_combo)
        
        main_layout.addWidget(self.figure_save_group_box)


        # 添加一个垂直伸缩器，确保内容不会顶到对话框顶部
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- 按钮盒 ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel | 
            QDialogButtonBox.StandardButton.Apply 
        )
        button_box.accepted.connect(self._on_ok_clicked)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply_clicked)
        
        main_layout.addWidget(button_box)

    def _create_collapsible_group_box(self, title: str) -> tuple[QGroupBox, QFormLayout]:
        """
        创建并返回一个可折叠的 QGroupBox 和一个 FormLayout 作为其内容布局。
        当 QGroupBox 被折叠时，其内容将被隐藏。
        """
        group_box = QGroupBox(title)
        group_box.setCheckable(True)
        group_box.setChecked(True) # 默认展开

        # 创建一个独立的 QWidget 来作为内容容器
        content_widget = QWidget(group_box)
        content_layout = QFormLayout(content_widget) # 将 FormLayout 设置到内容容器上

        # 创建 group_box 的主布局
        group_box_main_layout = QVBoxLayout(group_box)
        group_box_main_layout.addWidget(content_widget)
        group_box_main_layout.setContentsMargins(0, 0, 0, 0) # 移除额外边距

        # 连接 toggled 信号来控制 content_widget 的可见性
        group_box.toggled.connect(content_widget.setVisible)

        return group_box, content_layout

    def _get_current_matplotlib_settings(self) -> Dict[str, Any]:
        """
        从 Matplotlib 的 rcParams 中读取当前设置。
        这是对话框启动时的默认值来源。
        """
        current_font_family = plt.rcParams.get("font.family", ["sans-serif"])
        if isinstance(current_font_family, list):
            current_font_family = current_font_family[0]

        savefig_dpi_val = plt.rcParams.get("savefig.dpi", 300)
        if isinstance(savefig_dpi_val, str) and savefig_dpi_val.lower() == 'figure':
            savefig_dpi_val = plt.rcParams.get("figure.dpi", 100) 

        return {
            "font.family": current_font_family,
            "font.size": plt.rcParams.get("font.size", 10.0),
            "text.usetex": plt.rcParams.get("text.usetex", False),
            
            "lines.linewidth": plt.rcParams.get("lines.linewidth", 1.5),
            "lines.linestyle": plt.rcParams.get("lines.linestyle", '-'),
            "lines.marker": plt.rcParams.get("lines.marker", 'None'),
            "lines.markersize": plt.rcParams.get("lines.markersize", 6.0),

            "axes.labelsize": plt.rcParams.get("axes.labelsize", 'medium'),
            "xtick.labelsize": plt.rcParams.get("xtick.labelsize", 'medium'),
            "ytick.labelsize": plt.rcParams.get("ytick.labelsize", 'medium'),
            "axes.grid": plt.rcParams.get("axes.grid", True),

            "legend.fontsize": plt.rcParams.get("legend.fontsize", 'medium'),
            "legend.frameon": plt.rcParams.get("legend.frameon", True),
            "legend.loc": plt.rcParams.get("legend.loc", 'best'),

            "figure.figsize": plt.rcParams.get("figure.figsize", [6.4, 4.8]),
            "savefig.dpi": savefig_dpi_val,
            "savefig.format": plt.rcParams.get("savefig.format", 'png'),
        }

    def set_settings(self, settings: Dict[str, Any]):
        """
        外部方法，用于向对话框传入新的设置数据以更新UI。
        如果外部有加载的持久化配置，可以通过此方法传入以覆盖当前 Matplotlib rcParams 的值。
        """
        self._current_settings.update(settings)
        self.load_settings_to_ui(self._current_settings)

    def load_settings_to_ui(self, settings: Dict[str, Any]):
        """将给定的设置字典加载到UI控件中。"""
        font_family = settings.get("font.family", "sans-serif")
        if isinstance(font_family, list):
            font_family = font_family[0]
        index = self.font_family_combo.findText(font_family, Qt.MatchFixedString)
        if index != -1:
            self.font_family_combo.setCurrentIndex(index)
        else:
            self.font_family_combo.setEditText(font_family)

        self.font_size_edit.setText(str(settings.get("font.size", 10.0)))
        self.use_latex_checkbox.setChecked(settings.get("text.usetex", False))

        latex_font_key = ""
        current_mpl_font_family = settings.get("font.family", "serif")
        if isinstance(current_mpl_font_family, list):
             current_mpl_font_family = current_mpl_font_family[0]

        if "serif" in current_mpl_font_family.lower():
            latex_font_key = "serif (Times New Roman)"
        elif "sans-serif" in current_mpl_font_family.lower():
            latex_font_key = "sans-serif (Helvetica/Arial)"
        elif "monospace" in current_mpl_font_family.lower():
            latex_font_key = "monospace (Courier)"
        
        index_latex = self.latex_font_family_combo.findText(latex_font_key, Qt.MatchContains)
        if index_latex != -1:
            self.latex_font_family_combo.setCurrentIndex(index_latex)
        else:
            self.latex_font_family_combo.setCurrentIndex(0)

        self.lines_linewidth_edit.setText(str(settings.get("lines.linewidth", 1.5)))
        self._set_combobox_value(self.lines_linestyle_combo, settings.get("lines.linestyle", '-'))
        self._set_combobox_value(self.lines_marker_combo, settings.get("lines.marker", 'None'))
        self.lines_markersize_edit.setText(str(settings.get("lines.markersize", 6.0)))

        self._set_combobox_value(self.axes_labelsize_combo, settings.get("axes.labelsize", 'medium'))
        self._set_combobox_value(self.xtick_labelsize_combo, settings.get("xtick.labelsize", 'medium'))
        self._set_combobox_value(self.ytick_labelsize_combo, settings.get("ytick.labelsize", 'medium'))
        self.axes_grid_checkbox.setChecked(settings.get("axes.grid", True))

        self._set_combobox_value(self.legend_fontsize_combo, settings.get("legend.fontsize", 'medium'))
        self.legend_frameon_checkbox.setChecked(settings.get("legend.frameon", True))
        self._set_combobox_value(self.legend_loc_combo, settings.get("legend.loc", 'best'))

        self.figure_width_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[0]))
        self.figure_height_edit.setText(str(settings.get("figure.figsize", [6.4, 4.8])[1]))
        self.savefig_dpi_edit.setText(str(settings.get("savefig.dpi", 300))) 
        self._set_combobox_value(self.savefig_format_combo, settings.get("savefig.format", 'png'))

        self._on_usetex_changed(self.use_latex_checkbox.checkState())

    def _set_combobox_value(self, combobox: QComboBox, value: Any):
        """辅助方法：设置 QComboBox 的值，如果值不在列表中则设置为编辑文本。"""
        str_value = str(value)
        if combobox == self.lines_linestyle_combo:
            found_index = -1
            for i in range(combobox.count()):
                item_text = combobox.itemText(i)
                if item_text.startswith(str_value) and (len(item_text) == len(str_value) or item_text[len(str_value)] == ' '):
                    found_index = i
                    break
            if found_index != -1:
                combobox.setCurrentIndex(found_index)
            else:
                combobox.setEditText(str_value)
        elif combobox == self.lines_marker_combo:
            index = combobox.findText(str_value, Qt.MatchFixedString)
            if index != -1:
                combobox.setCurrentIndex(index)
            else:
                index_none = combobox.findText("None", Qt.MatchFixedString)
                if value is None and index_none != -1:
                    combobox.setCurrentIndex(index_none)
                else:
                    combobox.setEditText(str_value)
        else:
            index = combobox.findText(str_value, Qt.MatchFixedString)
            if index != -1:
                combobox.setCurrentIndex(index)
            else:
                combobox.setEditText(str_value)

    def get_settings_from_ui(self) -> Dict[str, Any]:
        """从UI控件获取当前设置。"""
        settings = {}
        
        if self.use_latex_checkbox.isChecked():
            selected_latex_font_text = self.latex_font_family_combo.currentText()
            if "serif" in selected_latex_font_text.lower():
                settings["font.family"] = "serif"
            elif "sans-serif" in selected_latex_font_text.lower():
                settings["font.family"] = "sans-serif"
            elif "monospace" in selected_latex_font_text.lower():
                settings["font.family"] = "monospace"
            else:
                settings["font.family"] = "serif"
        else:
            settings["font.family"] = self.font_family_combo.currentFont().family()
        
        settings["font.size"] = float(self.font_size_edit.text())
            
        settings["text.usetex"] = self.use_latex_checkbox.isChecked()

        settings["lines.linewidth"] = float(self.lines_linewidth_edit.text())

        selected_linestyle_text = self.lines_linestyle_combo.currentText()
        settings["lines.linestyle"] = selected_linestyle_text.split(' ')[0]

        settings["lines.marker"] = self.lines_marker_combo.currentText()
        if settings["lines.marker"] == "None":
            settings["lines.marker"] = None
        
        settings["lines.markersize"] = float(self.lines_markersize_edit.text())

        settings["axes.labelsize"] = self.axes_labelsize_combo.currentText()
        settings["xtick.labelsize"] = self.xtick_labelsize_combo.currentText()
        settings["ytick.labelsize"] = self.ytick_labelsize_combo.currentText()
        settings["axes.grid"] = self.axes_grid_checkbox.isChecked()

        settings["legend.fontsize"] = self.legend_fontsize_combo.currentText()
        settings["legend.frameon"] = self.legend_frameon_checkbox.isChecked()
        settings["legend.loc"] = self.legend_loc_combo.currentText()

        figure_width = float(self.figure_width_edit.text())
        figure_height = float(self.figure_height_edit.text())
        settings["figure.figsize"] = [figure_width, figure_height]

        settings["savefig.dpi"] = int(self.savefig_dpi_edit.text())

        settings["savefig.format"] = self.savefig_format_combo.currentText()

        return settings

    def _on_usetex_changed(self, state: int):
        """
        当“使用 LaTeX 渲染文本”复选框状态改变时调用。
        控制 LaTeX 字体家族组合框的启用状态，以及普通字体选择的启用状态。
        """
        is_checked = (state == Qt.CheckState.Checked)
        self.latex_font_family_combo.setEnabled(is_checked)
        self.font_family_combo.setEnabled(not is_checked)
        self.font_size_edit.setEnabled(True)

    def _validate_inputs(self) -> list[str]:
        """
        验证所有数字输入字段，并返回一个错误消息列表。
        如果列表为空，则表示所有输入都有效。
        同时会包含用户输入的值。
        """
        errors = []

        if not self.font_size_edit.hasAcceptableInput():
            errors.append(f"字体大小 (Font Size) 输入无效。当前输入: '{self.font_size_edit.text()}'。请检查是否为有效数字。")
        
        if not self.lines_linewidth_edit.hasAcceptableInput():
            errors.append(f"默认线条宽度 (Line Width) 输入无效。当前输入: '{self.lines_linewidth_edit.text()}'。请检查是否为有效数字。")
        if not self.lines_markersize_edit.hasAcceptableInput():
            errors.append(f"默认标记大小 (Marker Size) 输入无效。当前输入: '{self.lines_markersize_edit.text()}'。请检查是否为有效数字。")

        if not self.figure_width_edit.hasAcceptableInput():
            errors.append(f"图像宽度 (Figure Width) 输入无效。当前输入: '{self.figure_width_edit.text()}'。请检查是否为有效数字。")
        if not self.figure_height_edit.hasAcceptableInput():
            errors.append(f"图像高度 (Figure Height) 输入无效。当前输入: '{self.figure_height_edit.text()}'。请检查是否为有效数字。")
        if not self.savefig_dpi_edit.hasAcceptableInput():
            errors.append(f"保存图片DPI (Save DPI) 输入无效。当前输入: '{self.savefig_dpi_edit.text()}'。请检查是否为有效整数。")
        
        return errors

    def _on_ok_clicked(self):
        """处理OK按钮点击，发出信号并接受对话框。"""
        validation_errors = self._validate_inputs()
        if not validation_errors:
            new_settings = self.get_settings_from_ui()
            self.settings_applied.emit(new_settings)
            self.accept()
        else:
            error_message = "以下字段输入无效，请修正：\n\n" + "\n".join(validation_errors)
            QMessageBox.warning(self, "输入错误", error_message)

    def _on_apply_clicked(self):
        """处理Apply按钮点击，发出信号但不关闭对话框。"""
        validation_errors = self._validate_inputs()
        if not validation_errors:
            new_settings = self.get_settings_from_ui()
            self.settings_applied.emit(new_settings)
            QMessageBox.information(self, "设置已应用", "Matplotlib 设置已应用。")
        else:
            error_message = "以下字段输入无效，请修正：\n\n" + "\n".join(validation_errors)
            QMessageBox.warning(self, "输入错误", error_message)

