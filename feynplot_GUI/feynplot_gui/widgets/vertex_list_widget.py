# feynplot_gui/widgets/vertex_list_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent # 导入 QMouseEvent

class VertexListWidget(QListWidget):
    """
    一个专门用于显示图中顶点列表的 QListWidget。
    可以发出信号，通知控制器用户交互。
    """
    # 信号：当一个顶点被选中时发出，传递选中的 Vertex 对象
    vertex_selected = Signal(object)
    # 信号：当一个顶点被双击时发出，传递双击的 Vertex 对象
    vertex_double_clicked = Signal(object)
    
    # 新增信号：当用户从右键菜单选择编辑顶点时发出，传递选中的 Vertex 对象
    edit_vertex_requested = Signal(object)
    # 新增信号：当用户从右键菜单选择删除顶点时发出，传递选中的 Vertex 对象
    delete_vertex_requested = Signal(object)
    # 新增信号：当用户从右键菜单选择关键字检索时发出，传递选中的 Vertex 对象
    search_vertex_requested = Signal(object) 

    # --- 新增信号：当列表空白处被点击时发出 ---
    list_blank_clicked = Signal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("顶点列表")
        self.setFixedWidth(200)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # ！！重要修改！！
        # 移除或注释掉这条连接。我们将直接在 mousePressEvent 中处理用户点击并发出信号。
        # self.itemSelectionChanged.connect(self._on_selection_changed) 
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    # ！！重要修改！！
    # 移除 _on_selection_changed 方法，因为它不再被连接，并且其逻辑已移至 mousePressEvent。
    # def _on_selection_changed(self):
    #     """处理列表项选择变化的槽函数。"""
    #     selected_items = self.selectedItems()
    #     if selected_items:
    #         vertex = selected_items[0].data(Qt.ItemDataRole.UserRole)
    #         self.vertex_selected.emit(vertex)
    #     else:
    #         # 当列表选择被程序性清空 (例如 clearSelection()) 时，也会触发这个 else 分支
    #         # 我们在这里发出 None 信号，通知 MainController 清除所有选中。
    #         # 这与 _mouse_press_event 中的 list_blank_clicked 配合，
    #         # 形成双重保险，确保选中状态能够被清除。
    #         self.vertex_selected.emit(None) 

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击的槽函数。"""
        vertex = item.data(Qt.ItemDataRole.UserRole)
        if vertex:
            self.vertex_double_clicked.emit(vertex)

    def _on_context_menu_requested(self, position):
        """
        处理上下文菜单请求的槽函数。
        :param position: 右键点击的位置 (QPoint)
        """
        item = self.itemAt(position)
        if item:
            vertex = item.data(Qt.ItemDataRole.UserRole)
            if vertex:
                menu = QMenu(self)

                edit_action = menu.addAction("编辑顶点")
                edit_action.triggered.connect(lambda: self.edit_vertex_requested.emit(vertex))

                delete_action = menu.addAction("删除顶点")
                delete_action.triggered.connect(lambda: self.delete_vertex_requested.emit(vertex))
                
                search_action = menu.addAction("关键字检索")
                search_action.triggered.connect(lambda: self.search_vertex_requested.emit(vertex))

                menu.exec(self.mapToGlobal(position))

    def mousePressEvent(self, event: QMouseEvent):
        """
        重写鼠标按下事件，检测是否点击了列表的空白处或列表项。
        """
        # ！！重要修改！！
        # 在处理鼠标事件期间，暂时阻塞信号，防止 itemSelectionChanged 意外触发循环
        # self.blockSignals(True) 
        
        # 先调用父类的 mousePressEvent，让 QListWidget 处理正常的UI选中逻辑（例如点击某个项就选中它）
        super().mousePressEvent(event) 

        if event.button() == Qt.MouseButton.LeftButton:
            # itemAt(pos) 返回给定位置的 QListWidgetItem，如果没有则返回 None
            item = self.itemAt(event.pos())
            
            if item is None:
                # 如果点击的位置没有列表项，表示点击了空白处
                print("VertexListWidget: 点击了空白区域。")
                self.list_blank_clicked.emit() # 发出空白点击信号
            else:
                # 如果点击了某个列表项，发出该项的选中信号
                vertex = item.data(Qt.ItemDataRole.UserRole)
                if vertex:
                    print(f"VertexListWidget: 点击了顶点 {vertex.id}")
                    self.vertex_selected.emit(vertex) # 发出选中的 Vertex 对象
        
        # ！！重要修改！！
        # 处理完毕后解除信号阻塞
        # self.blockSignals(False)


    def add_vertex_item(self, vertex_data):
        """
        向列表中添加一个顶点项。
        Args:
            vertex_data: 实际的 Vertex 对象。
        """
        item_text = rf"[{vertex_data.id}] 顶点: {vertex_data.label} ({vertex_data.x:.2f}, {vertex_data.y:.2f})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, vertex_data)
        self.addItem(item)
        
        # 优化：在添加项后，不自动选中，MainController 会统一管理选中状态
        # self.setCurrentItem(item)
        # self.scrollToItem(item)


    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_vertex(self):
        """获取当前选中的 Vertex 对象，如果没有选中则返回 None。"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None

    def set_selected_item_in_list(self, item_to_select):
        """
        根据传入的 Vertex 对象在列表中进行选中。
        如果传入 None，则取消所有选中。
        这个方法仅用于UI层面同步选中状态，不应触发新的选择信号。
        """
        # ！！重要！！
        # 确保这里继续阻塞信号，防止 itemSelectionChanged 信号被触发，导致循环
        # self.blockSignals(True) 
        print("VertexListWidget: 设置选中项")
        self.clearSelection() # 首先清除所有选中

        if item_to_select is not None: 
            for i in range(self.count()):
                item_widget = self.item(i)
                vertex_data = item_widget.data(Qt.ItemDataRole.UserRole)
                # 比较 Vertex 对象的 ID 来确定是否是同一个对象
                if vertex_data and hasattr(item_to_select, 'id') and vertex_data.id == item_to_select.id:
                    item_widget.setSelected(True)
                    self.setCurrentItem(item_widget) 
                    self.scrollToItem(item_widget) 
                    break 
        
        # ！！重要！！
        # 解除信号阻塞
        # self.blockSignals(False)