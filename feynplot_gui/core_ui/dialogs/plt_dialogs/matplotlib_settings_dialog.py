# feynplot_GUI/feynplot_gui/dialogs/plt_dialogs/matplotlib_settings_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox, QWidget,
    QSpacerItem, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Signal, Qt
from typing import Dict, Any, Optional

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 导入 font_manager

# 导入所有新的面板组件
from ._font_settings_panel import FontSettingsPanel
from ._latex_settings_panel import LatexSettingsPanel
from ._lines_markers_settings_panel import LinesMarkersSettingsPanel
from ._axes_ticks_settings_panel import AxesTicksSettingsPanel
from ._legend_settings_panel import LegendSettingsPanel
from ._figure_save_settings_panel import FigureSaveSettingsPanel

class MatplotlibSettingsDialog(QDialog):
    """
    一个用于配置 Matplotlib 后端设置的对话框。
    它集成了一系列独立的设置面板。整个对话框内容区域的高度最高为800像素，超出部分可滚动。
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
        
        self.latex_panel.use_latex_checkbox.stateChanged.connect(self._on_usetex_changed_global)

    def init_ui(self):
        """初始化对话框的用户界面元素和布局。"""
        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(800) 

        self.scroll_content_widget = QWidget(self.scroll_area)
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)

        self.scroll_area.setWidget(self.scroll_content_widget)
        main_layout.addWidget(self.scroll_area)

        # 实例化所有面板，并添加到 scroll_content_layout
        self.font_panel = FontSettingsPanel(self.scroll_content_widget)
        self.latex_panel = LatexSettingsPanel(self.scroll_content_widget)
        self.lines_markers_panel = LinesMarkersSettingsPanel(self.scroll_content_widget)
        self.axes_ticks_panel = AxesTicksSettingsPanel(self.scroll_content_widget)
        self.legend_panel = LegendSettingsPanel(self.scroll_content_widget)
        self.figure_save_panel = FigureSaveSettingsPanel(self.scroll_content_widget)

        # 将面板添加到 scroll_content_layout
        self.scroll_content_layout.addWidget(self.font_panel)
        self.scroll_content_layout.addWidget(self.latex_panel)
        self.scroll_content_layout.addWidget(self.lines_markers_panel)
        self.scroll_content_layout.addWidget(self.axes_ticks_panel)
        self.scroll_content_layout.addWidget(self.legend_panel)
        self.scroll_content_layout.addWidget(self.figure_save_panel)

        self.scroll_content_layout.addStretch(1)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel | 
            QDialogButtonBox.StandardButton.Apply 
        )
        button_box.accepted.connect(self._on_ok_clicked)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply_clicked)
        
        main_layout.addWidget(button_box)

    def _get_current_matplotlib_settings(self) -> Dict[str, Any]:
        """
        从 Matplotlib 的 rcParams 中读取当前设置。
        这是对话框启动时的默认值来源。
        """
        # 获取 usetex 状态
        usetex = plt.rcParams.get("text.usetex", False)

        current_font_family = plt.rcParams.get("font.family", ["sans-serif"])
        if isinstance(current_font_family, list):
            current_font_family = current_font_family[0]

        savefig_dpi_val = plt.rcParams.get("savefig.dpi", 300)
        if isinstance(savefig_dpi_val, str) and savefig_dpi_val.lower() == 'figure':
            savefig_dpi_val = plt.rcParams.get("figure.dpi", 100) 

        mathtext_rm = plt.rcParams.get("mathtext.rm", "")
        mathtext_it = plt.rcParams.get("mathtext.it", "")
        mathtext_bf = plt.rcParams.get("mathtext.bf", "")
        mathtext_bfit = plt.rcParams.get("mathtext.bfit", "")
        
        # --- MODIFICATION START ---
        # Set the default for mathtext.fontset to 'custom' here
        mathtext_fontset = plt.rcParams.get("mathtext.fontset", "custom") # Changed default to "custom"
        # --- MODIFICATION END ---

        # For text.fontfamily, when usetex is True, matplotlib tends to use font.family.
        # So here, when usetex is True, we make the UI default to showing the value of font.family.
        text_fontfamily_val = plt.rcParams.get("text.fontfamily", "sans-serif")
        if usetex: # If usetex is enabled, text.fontfamily is effectively controlled by font.family
            text_fontfamily_val = current_font_family 

        text_fontsize = plt.rcParams.get("text.fontsize", plt.rcParams.get("font.size", 10.0))
        text_fontweight = plt.rcParams.get("text.fontweight", "normal")
        text_fontstyle = plt.rcParams.get("text.fontstyle", "normal")

        return {
            "font.family": current_font_family,
            "font.size": plt.rcParams.get("font.size", 10.0),
            "text.usetex": usetex, 
            
            "mathtext.fontset": mathtext_fontset, # Now defaults to "custom" if not found in rcParams
            "mathtext.rm": mathtext_rm,
            "mathtext.it": mathtext_it,
            "mathtext.bf": mathtext_bf,
            "mathtext.bfit": mathtext_bfit,

            "text.fontfamily": text_fontfamily_val, 
            "text.fontsize": text_fontsize,
            "text.fontweight": text_fontweight,
            "text.fontstyle": text_fontstyle,

            "lines.linewidth": plt.rcParams.get("lines.linewidth", 1.5),
            "lines.linestyle": plt.rcParams.get("lines.linestyle", '-'),
            "lines.marker": plt.rcParams.get("lines.marker", 'None'),
            "lines.markersize": plt.rcParams.get("lines.markersize", 6.0),

            "axes.labelsize": plt.rcParams.get("axes.labelsize", 'medium'),
            "xtick.labelsize": plt.rcParams.get("xtick.labelsize", 'medium'),
            "ytick.labelsize": plt.rcParams.get("ytick.labelsize", 'medium'),
            "axes.grid": plt.rcParams.get("axes.grid", False),

            "legend.fontsize": plt.rcParams.get("legend.fontsize", 'medium'),
            "legend.frameon": plt.rcParams.get("legend.frameon", True),
            "legend.loc": plt.rcParams.get("legend.loc", 'best'),

            "figure.figsize": plt.rcParams.get("figure.figsize", [6.4, 4.8]),
            "savefig.dpi": savefig_dpi_val,
            "savefig.format": plt.rcParams.get("savefig.format", 'png'),
        }

    def set_settings(self, settings: Dict[str, Any]):
        """
        External method to pass new settings data to the dialog to update the UI.
        If external persistent configuration is loaded, it can be passed in via this method to override the current Matplotlib rcParams values.
        """
        self._current_settings.update(settings)
        self.load_settings_to_ui(self._current_settings)

    def load_settings_to_ui(self, settings: Dict[str, Any]):
        """Loads the given settings dictionary into the UI controls."""
        self.font_panel.load_settings(settings)
        self.latex_panel.load_settings(settings)
        self.lines_markers_panel.load_settings(settings)
        self.axes_ticks_panel.load_settings(settings)
        self.legend_panel.load_settings(settings)
        self.figure_save_panel.load_settings(settings)

        self._on_usetex_changed_global(self.latex_panel.use_latex_checkbox.checkState())

    def get_settings_from_ui(self) -> Dict[str, Any]:
        """Gets current settings from UI controls."""
        settings = {}
        # Get settings from all panels and merge
        settings.update(self.font_panel.get_settings()) 

        latex_settings = self.latex_panel.get_settings()
        settings["text.usetex"] = latex_settings["text.usetex"]

        if latex_settings.get("text.usetex"):
            # When use_usetex = True, Matplotlib uses LaTeX for all text, including math and regular text,
            # ignoring most mathtext.* and text.* settings.
            # Therefore, remove these potentially conflicting settings.
            settings["font.family"] = latex_settings["font.family"] 
            
            for key_prefix in ["mathtext.", "text."]: 
                for key in list(settings.keys()): 
                    if key.startswith(key_prefix) and key != "text.usetex": 
                        settings.pop(key)
        
        settings.update(self.lines_markers_panel.get_settings())
        settings.update(self.axes_ticks_panel.get_settings())
        settings.update(self.legend_panel.get_settings())
        settings.update(self.figure_save_panel.get_settings())
        
        return settings

    def _on_usetex_changed_global(self, state: int):
        """
        Globally handles changes in use_latex state, controlling general font family selection and text font group in FontSettingsPanel.
        """
        is_checked = (state == Qt.CheckState.Checked)
        self.font_panel.general_font_group.setEnabled(not is_checked) 
        self.font_panel.mathtext_font_group.setEnabled(not is_checked) 
        self.font_panel.text_font_group.setEnabled(not is_checked) 


    def _validate_inputs(self) -> list[str]:
        """
        Validates input fields across all sub-panels and returns a list of error messages.
        """
        errors = []
        errors.extend(self.font_panel.validate_inputs())
        errors.extend(self.lines_markers_panel.validate_inputs())
        errors.extend(self.figure_save_panel.validate_inputs())
        
        return errors

    def _on_ok_clicked(self):
        """Handles OK button click, emits signal and accepts the dialog."""
        validation_errors = self._validate_inputs()
        if not validation_errors:
            new_settings = self.get_settings_from_ui()
            self.settings_applied.emit(new_settings)
            self.accept()
        else:
            error_message = "Invalid input in the following fields, please correct:\n\n" + "\n".join(validation_errors)
            QMessageBox.warning(self, "Input Error", error_message)

    def _on_apply_clicked(self):
        """Handles Apply button click, emits signal but does not close the dialog."""
        validation_errors = self._validate_inputs()
        if not validation_errors:
            new_settings = self.get_settings_from_ui()
            self.settings_applied.emit(new_settings)
            QMessageBox.information(self, "Settings Applied", "Matplotlib settings have been applied.")
        else:
            error_message = "Invalid input in the following fields, please correct:\n\n" + "\n".join(validation_errors)
            QMessageBox.warning(self, "Input Error", error_message)
