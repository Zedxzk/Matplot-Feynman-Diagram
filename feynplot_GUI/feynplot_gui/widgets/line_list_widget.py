# feynplot_gui/widgets/line_list_widget.py

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem,
    QMenu, QWidget 
)
from PySide6.QtCore import Signal, Qt 
from PySide6.QtGui import QMouseEvent 

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
        self.setWindowTitle("线条列表")
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
        """
        重写鼠标按下事件，检测是否点击了列表的空白处或列表项。
        """
        # ！！重要修改！！
        # 在处理鼠标事件期间，暂时阻塞信号，防止 itemSelectionChanged 意外触发循环
        # self.blockSignals(True) 
        
        # 先调用父类的 mousePressEvent，让 QListWidget 处理正常的UI选中逻辑
        super().mousePressEvent(event) 

        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            
            if item is None:
                # 如果点击的位置没有列表项，表示点击了空白处
                print("LineListWidget: 点击了空白区域。")
                self.list_blank_clicked.emit() # 发出空白点击信号
            else:
                # 如果点击了某个列表项，发出该项的选中信号
                line = item.data(Qt.ItemDataRole.UserRole)
                if line:
                    print(f"LineListWidget: 点击了线条 {line.id}")
                    self.line_selected.emit(line) # 发出选中的 Line 对象
        
        # ！！重要修改！！
        # 处理完毕后解除信号阻塞
        # self.blockSignals(False)


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
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None
        
    def set_selected_item_in_list(self, item_to_select):
        """
        根据传入的 Line 对象在列表中进行选中。
        如果传入 None，则取消所有选中。
        这个方法仅用于UI层面同步选中状态，不应触发新的选择信号。
        """
        # ！！重要！！
        # 确保这里继续阻塞信号，防止 itemSelectionChanged 信号被触发，导致循环
        self.blockSignals(True) 
        
        self.clearSelection() # 首先清除所有选中

        if item_to_select is not None: 
            for i in range(self.count()):
                item_widget = self.item(i)
                line_data = item_widget.data(Qt.ItemDataRole.UserRole)
                if line_data and hasattr(item_to_select, 'id') and line_data.id == item_to_select.id:
                    item_widget.setSelected(True)
                    self.setCurrentItem(item_widget) 
                    self.scrollToItem(item_widget) 
                    break 
        
        # ！！重要！！
        # 解除信号阻塞
        self.blockSignals(False)