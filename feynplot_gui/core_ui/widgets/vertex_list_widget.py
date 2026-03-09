# feynplot_gui/widgets/vertex_list_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent
from feynplot_gui.core_ui.widgets.list_widget_common import (
    keyPressEvent_page_up_down,
    mousePressEvent_blank_or_item,
    set_selected_item_in_list_impl,
    get_selected_item_from_list,
)

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
        self.setWindowTitle(self.tr("顶点列表"))
        self.setFixedWidth(200)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # ！！重要修改！！
        # 移除或注释掉这条连接。我们将直接在 mousePressEvent 中处理用户点击并发出信号。
        # self.itemSelectionChanged.connect(self._on_selection_changed) 
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

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
        super().mousePressEvent(event)
        mousePressEvent_blank_or_item(self, event, self.vertex_selected, self.list_blank_clicked)

    def keyPressEvent(self, event: QKeyEvent):
        """用 Page Up/Down 切换选中项；方向键由全局处理（移动顶点/平移画布）。"""
        keyPressEvent_page_up_down(self, event, self.vertex_selected)

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
        return get_selected_item_from_list(self)

    def set_selected_item_in_list(self, item_to_select):
        """根据传入的 Vertex 对象在列表中进行选中；None 则清空选中。仅用于 UI 同步。"""
        set_selected_item_in_list_impl(self, item_to_select)