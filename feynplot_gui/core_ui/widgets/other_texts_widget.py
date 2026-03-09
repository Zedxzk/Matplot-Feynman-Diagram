# feynplot_gui\core_ui\widgets\other_texts_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QMouseEvent, QKeyEvent
from feynplot_gui.core_ui.widgets.list_widget_common import (
    keyPressEvent_page_up_down,
    mousePressEvent_blank_or_item,
    set_selected_item_in_list_impl,
    get_selected_item_from_list,
)
class OtherTextsWidget(QListWidget):
    """
    A QListWidget specifically for displaying a list of TextElement objects in the diagram.
    It emits signals to notify the controller about user interactions.
    """
    # Signal: Emitted when a text element is selected, passing the selected TextElement object
    text_selected = Signal(object)
    # Signal: Emitted when a text element is double-clicked, passing the double-clicked TextElement object
    text_double_clicked = Signal(object)
    
    # New signal: Emitted when the user requests to edit a text element from the context menu, passing the selected TextElement object
    edit_text_requested = Signal(object)
    # New signal: Emitted when the user requests to delete a text element from the context menu, passing the selected TextElement object
    delete_text_requested = Signal(object)
    # New signal: Emitted when the user requests a keyword search from the context menu, passing the selected TextElement object
    search_text_requested = Signal(object) 

    # New signal: Emitted when the blank area of the list is clicked
    list_blank_clicked = Signal() 

    # === 新增信号：当用户请求添加新文本时发出 ===
    add_new_text_requested = Signal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("文本列表")) # Window title adapted for text elements
        # self.setFixedWidth(200) # 通常在父级布局中控制宽度，这里注释掉是好的实践

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handler for list item double-clicks."""
        text_element = item.data(Qt.ItemDataRole.UserRole)
        if text_element:
            self.text_double_clicked.emit(text_element)

    def _on_context_menu_requested(self, position: QPoint):
        """
        Handles context menu requests.
        :param position: The right-click position (QPoint)
        """
        item = self.itemAt(position)
        menu = QMenu(self)

        # 总是添加“添加新文本”的选项，因为它是一个全局操作
        add_action = menu.addAction("添加新文本")
        add_action.triggered.connect(self.add_new_text_requested.emit)
        
        # 添加一个分隔线，以区分全局操作和针对具体项的操作
        if item:
            menu.addSeparator()

        if item:
            # 右键点击了列表项
            text_element = item.data(Qt.ItemDataRole.UserRole)
            if text_element:
                edit_action = menu.addAction("编辑文本")
                edit_action.triggered.connect(lambda: self.edit_text_requested.emit(text_element))

                delete_action = menu.addAction("删除文本")
                delete_action.triggered.connect(lambda: self.delete_text_requested.emit(text_element))
        
        # 只有当菜单中有动作时才显示菜单
        if menu.actions():
            menu.exec(self.mapToGlobal(position))


    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        mousePressEvent_blank_or_item(self, event, self.text_selected, self.list_blank_clicked)

    def keyPressEvent(self, event: QKeyEvent):
        """用 Page Up/Down 切换选中项；方向键由全局处理（移动顶点/平移画布）。"""
        keyPressEvent_page_up_down(self, event, self.text_selected)

    def add_text_item(self, text_data):
        """
        Adds a text item to the list.
        Args:
            text_data: The actual TextElement object.
        """
        # Display text content, ID, and coordinates
        # print(text_data)
        item_text = rf"[{text_data.id}] 文本: '{text_data.text[:20]}...' ({text_data.x:.2f}, {text_data.y:.2f})" \
                    if len(text_data.text) > 20 else rf"[{text_data.id}] 文本: '{text_data.text}' ({text_data.x:.2f}, {text_data.y:.2f})"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, text_data)
        self.addItem(item)
        
        # Don't auto-select here; MainController will manage selection state
        # self.setCurrentItem(item)
        # self.scrollToItem(item)


    def clear_list(self):
        """Clears all items from the list."""
        self.clear()

    def get_selected_text_element(self):
        """Retrieves the currently selected TextElement object, or None if nothing is selected."""
        return get_selected_item_from_list(self)

    def set_selected_item_in_list(self, item_to_select):
        """Selects an item in the list based on the provided TextElement object; None clears selection."""
        set_selected_item_in_list_impl(self, item_to_select)