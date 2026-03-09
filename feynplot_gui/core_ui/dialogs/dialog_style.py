# feynplot_gui/core_ui/dialogs/dialog_style.py
"""
统一所有对话框的页面布局与字体风格（与 edit line / edit vertex 一致）。
不包含窗口大小设置。
"""
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLayout

# 与 edit line / edit vertex 一致的正文字号
DIALOG_FONT_POINT_SIZE = 10
# 内容区边距（与常见 Qt 对话框一致）
DIALOG_CONTENT_MARGINS = (11, 11, 11, 11)  # left, top, right, bottom
DIALOG_LAYOUT_SPACING = 6


def apply_dialog_style(dialog: QDialog, *, font_point_size: int = None) -> None:
    """对对话框应用统一字体（继承系统字体族，统一字号）。"""
    if font_point_size is None:
        font_point_size = DIALOG_FONT_POINT_SIZE
    family = dialog.font().family() or ""
    dialog.setFont(QFont(family, font_point_size))


def apply_content_layout(layout: QLayout) -> None:
    """对内容区布局应用统一边距与间距。"""
    m = DIALOG_CONTENT_MARGINS
    layout.setContentsMargins(m[0], m[1], m[2], m[3])
    layout.setSpacing(DIALOG_LAYOUT_SPACING)
