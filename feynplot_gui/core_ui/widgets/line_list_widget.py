# feynplot_gui/widgets/line_list_widget.py

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem,
    QMenu, QWidget 
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent
from feynplot_gui.core_ui.widgets.list_widget_common import (
    keyPressEvent_page_up_down,
    mousePressEvent_blank_or_item,
    set_selected_item_in_list_impl,
    get_selected_item_from_list,
)

class LineListWidget(QListWidget):
    """
    一个专门用于显示图中线条列表的 QListWidget。
    可以发出信号，通知控制器用户交互。
    """
    # 信号：当一条线条被选中时发出，传递选中的 Line 对象
    line_selected = Signal(object)
    # 信号：当一条线条被双击时发出，传递双击的 Line 对象
    line_double_clicked = Signal(object)
    
    # 新增信号：请求编辑线条，传递选中的 Line 对象
    request_edit_line = Signal(object)
    # 新增信号：请求删除线条，传递选中的 Line 对象
    request_delete_line = Signal(object)

    # --- 新增信号：当列表空白处被点击时发出 ---
    list_blank_clicked = Signal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("线条列表"))
        self.setFixedWidth(200)

        # ！！重要修改！！
        # 移除或注释掉这条连接，因为我们将在 mousePressEvent 中直接处理用户选择逻辑并发出信号
        # self.itemSelectionChanged.connect(self._on_selection_changed) 
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    # ！！重要修改！！
    # 移除 _on_selection_changed 方法，因为它不再被连接，并且逻辑已移至 mousePressEvent
    # def _on_selection_changed(self):
    #     selected_items = self.selectedItems()
    #     if selected_items:
    #         line = selected_items[0].data(Qt.ItemDataRole.UserRole)
    #         self.line_selected.emit(line)
    #     else:
    #         self.line_selected.emit(None)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击的槽函数。"""
        line = item.data(Qt.ItemDataRole.UserRole)
        if line:
            self.line_double_clicked.emit(line)

    def _on_context_menu_requested(self, pos):
        """
        处理右键上下文菜单请求。
        根据鼠标位置检查是否有选中项，并显示相应菜单。
        """
        item = self.itemAt(pos)
        
        if item:
            line = item.data(Qt.ItemDataRole.UserRole)
            if line:
                menu = QMenu(self)
                
                edit_action = menu.addAction("编辑线条...")
                delete_action = menu.addAction("删除线条")
                
                edit_action.triggered.connect(lambda: self.request_edit_line.emit(line))
                delete_action.triggered.connect(lambda: self.request_delete_line.emit(line))
                
                menu.exec(self.mapToGlobal(pos))

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        mousePressEvent_blank_or_item(self, event, self.line_selected, self.list_blank_clicked)

    def keyPressEvent(self, event: QKeyEvent):
        """用 Page Up/Down 切换选中项；方向键由全局处理（移动顶点/平移画布）。"""
        keyPressEvent_page_up_down(self, event, self.line_selected)

    def add_line_item(self, line_data):
        """
        向列表中添加一个线条项。
        Args:
            line_data: 实际的 Line 对象。
        """
        start_label = line_data.v_start.label if line_data.v_start else "None"
        end_label = line_data.v_end.label if line_data.v_end else "None"
        item_text = f"[{line_data.id}] Line: {line_data.label} ({start_label} -> {end_label})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, line_data) 
        self.addItem(item)
        
        # 优化：在添加项后，自动选中它，并滚动到可见区域（可选）
        # 这里不自动选中，因为 MainController 会统一处理选中状态
        # self.setCurrentItem(item)
        # self.scrollToItem(item)


    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_line(self):
        """获取当前选中的 Line 对象，如果没有选中则返回 None。"""
        return get_selected_item_from_list(self)

    def set_selected_item_in_list(self, item_to_select):
        """根据传入的 Line 对象在列表中进行选中；None 则清空选中。仅用于 UI 同步。"""
        set_selected_item_in_list_impl(self, item_to_select)