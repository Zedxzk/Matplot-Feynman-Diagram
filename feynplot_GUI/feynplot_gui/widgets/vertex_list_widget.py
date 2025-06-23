# feynplot_gui/widgets/vertex_list_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox # 导入 QMenu 和 QMessageBox
from PySide6.QtCore import Signal, Qt

class VertexListWidget(QListWidget):
    """
    一个专门用于显示图中顶点列表的 QListWidget。
    可以发出信号，通知控制器用户交互。
    """
    # 信号：当一个顶点被选中时发出，传递选中的 Vertex 对象
    vertex_selected = Signal(object)
    # 信号：当一个顶点被双击时发出，传递双击的 Vertex 对象
    vertex_double_clicked = Signal(object)
    
    # --- 确保这里定义了新增的信号 ---
    # 新增信号：当用户从右键菜单选择编辑顶点时发出，传递选中的 Vertex 对象
    edit_vertex_requested = Signal(object)
    # 新增信号：当用户从右键菜单选择删除顶点时发出，传递选中的 Vertex 对象
    delete_vertex_requested = Signal(object)
    # 新增信号：当用户从右键菜单选择关键字检索时发出，传递选中的 Vertex 对象
    search_vertex_requested = Signal(object) # <-- 确保这一行存在！
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("顶点列表") # 直接使用中文
        self.setFixedWidth(200)

        # 启用自定义上下文菜单策略
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 连接内置信号到自定义槽函数
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        # 连接自定义上下文菜单请求信号到槽函数
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    def _on_selection_changed(self):
        """处理列表项选择变化的槽函数。"""
        selected_items = self.selectedItems()
        if selected_items:
            # 获取存储在 ItemDataRole.UserRole 中的实际 Vertex 对象
            vertex = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.vertex_selected.emit(vertex)
        else:
            self.vertex_selected.emit(None) # 没有选中项时发出 None

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
        # 获取在点击位置下的列表项
        item = self.itemAt(position)
        if item:
            # 获取实际的 Vertex 对象
            vertex = item.data(Qt.ItemDataRole.UserRole)
            if vertex:
                menu = QMenu(self)

                # 添加“编辑顶点”动作
                edit_action = menu.addAction("编辑顶点")
                edit_action.triggered.connect(lambda: self.edit_vertex_requested.emit(vertex))

                # 添加“删除顶点”动作
                delete_action = menu.addAction("删除顶点")
                delete_action.triggered.connect(lambda: self.delete_vertex_requested.emit(vertex))
                
                # 添加“关键字检索”动作
                # 注意：这里我们假设“关键字检索”是针对当前选中的顶点进行某种检索操作。
                # 如果是全局检索，可能需要不同的设计。
                search_action = menu.addAction("关键字检索")
                search_action.triggered.connect(lambda: self.search_vertex_requested.emit(vertex))


                # 在鼠标点击的位置显示菜单
                menu.exec(self.mapToGlobal(position))
        # else:
            # 如果点击的位置没有列表项，你也可以选择显示一个通用菜单
            # 或者不显示任何菜单
            # pass

        # else:
            # 如果点击的位置没有列表项，你也可以选择显示一个通用菜单
            # 或者不显示任何菜单
            # pass

    def add_vertex_item(self, vertex_data):
        """
        向列表中添加一个顶点项。
        Args:
            vertex_data: 实际的 Vertex 对象。
        """
        # 直接使用中文 "顶点"
        item_text = rf"[{vertex_data.id}] 顶点: {vertex_data.label} ({vertex_data.x:.2f}, {vertex_data.y:.2f})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, vertex_data) # 将 Vertex 对象存储在用户数据中
        self.addItem(item)

    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_vertex(self):
        """获取当前选中的 Vertex 对象，如果没有选中则返回 None。"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None