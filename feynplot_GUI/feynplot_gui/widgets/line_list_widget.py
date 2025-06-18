from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem,
    QMenu, QWidget # 导入 QMenu 和 QWidget
)
from PySide6.QtCore import Signal, Qt

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("线条列表")
        self.setFixedWidth(200) # 可以设置一个默认宽度

        # 连接内置信号到自定义槽函数
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # 启用自定义上下文菜单策略
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    def _on_selection_changed(self):
        """处理列表项选择变化的槽函数。"""
        selected_items = self.selectedItems()
        if selected_items:
            # 获取存储在 ItemDataRole.UserRole 中的实际 Line 对象
            line = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.line_selected.emit(line)
        else:
            self.line_selected.emit(None) # 没有选中项时发出 None

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
        # 获取在鼠标位置的列表项
        item = self.itemAt(pos)
        
        # 如果右键点击处有项，并且该项是当前选中的项之一
        if item and item in self.selectedItems():
            line = item.data(Qt.ItemDataRole.UserRole)
            if line:
                menu = QMenu(self)
                
                edit_action = menu.addAction("编辑线条...")
                delete_action = menu.addAction("删除线条")
                
                # 连接菜单项的 triggered 信号到相应的请求信号
                edit_action.triggered.connect(lambda: self.request_edit_line.emit(line))
                delete_action.triggered.connect(lambda: self.request_delete_line.emit(line))
                
                # 在鼠标位置显示菜单
                menu.exec(self.mapToGlobal(pos))
        else:
            # 如果没有选中项或者右键点击在空白处，可以显示一个不同的菜单
            # 或者什么都不做，这取决于你的设计需求
            pass


    def add_line_item(self, line_data):
        """
        向列表中添加一个线条项。
        Args:
            line_data: 实际的 Line 对象。
        """
        # 假设 line_data 有 v_start 和 v_end 属性，它们也是 Vertex 对象
        start_label = line_data.v_start.label if line_data.v_start else "None"
        end_label = line_data.v_end.label if line_data.v_end else "None"
        item_text = f"[{line_data.id}] Line: {line_data.label} ({start_label} -> {end_label})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, line_data) # 将 Line 对象存储在用户数据中
        self.addItem(item)
        
        # 优化：在添加项后，自动选中它，并滚动到可见区域（可选）
        self.setCurrentItem(item)
        self.scrollToItem(item)


    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_line(self):
        """获取当前选中的 Line 对象，如果没有选中则返回 None。"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None
        
    def set_selected_item_in_list(self, item_to_select):
        """
        根据传入的 Line 对象在列表中进行选中。
        如果传入 None，则取消所有选中。
        """
        self.clearSelection() # 首先清除所有选中
        if item_to_select is None:
            return

        for i in range(self.count()):
            item_widget = self.item(i)
            line_data = item_widget.data(Qt.ItemDataRole.UserRole)
            if line_data and line_data.id == item_to_select.id:
                item_widget.setSelected(True)
                self.setCurrentItem(item_widget) # 设置为当前项，以便滚动到视图中
                self.scrollToItem(item_widget) # 确保该项可见
                break
