# feynplot_gui/core_ui/widgets/list_widget_common.py
"""列表控件共用逻辑：Page Up/Down、mousePress、set_selected、get_selected。"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent


def keyPressEvent_page_up_down(self, event: QKeyEvent, selection_signal):
    """用 Page Up/Down 切换选中项并发出信号；方向键交给父类。"""
    if event.key() == Qt.Key.Key_PageUp:
        row = max(0, self.currentRow() - 1)
        self.setCurrentRow(row)
        item = self.item(row)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                selection_signal.emit(data)
        event.accept()
        return
    if event.key() == Qt.Key.Key_PageDown:
        row = min(self.count() - 1, self.currentRow() + 1)
        self.setCurrentRow(row)
        item = self.item(row)
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                selection_signal.emit(data)
        event.accept()
        return
    super(type(self), self).keyPressEvent(event)


def mousePressEvent_blank_or_item(self, event: QMouseEvent, selection_signal, blank_signal):
    """
    处理点击：空白处发 blank_signal，点击项发 selection_signal(data)。
    调用前需 super().mousePressEvent(event)。
    """
    if event.button() not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
        return
    item = self.itemAt(event.pos())
    if item is None:
        blank_signal.emit()
    else:
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            selection_signal.emit(data)


def set_selected_item_in_list_impl(list_widget, item_to_select, *, block_signals: bool = True):
    """
    在列表中同步选中项。若 item_to_select 为 None 则清空选中；否则按 id 匹配并选中。
    """
    if block_signals:
        list_widget.blockSignals(True)
    list_widget.clearSelection()
    if item_to_select is not None and hasattr(item_to_select, "id"):
        for i in range(list_widget.count()):
            w = list_widget.item(i)
            data = w.data(Qt.ItemDataRole.UserRole)
            if data and getattr(data, "id", None) == item_to_select.id:
                w.setSelected(True)
                list_widget.setCurrentItem(w)
                list_widget.scrollToItem(w)
                break
    if block_signals:
        list_widget.blockSignals(False)


def get_selected_item_from_list(list_widget):
    """获取列表当前选中项对应的 UserRole 数据，无选中则返回 None。"""
    sel = list_widget.selectedItems()
    return sel[0].data(Qt.ItemDataRole.UserRole) if sel else None
