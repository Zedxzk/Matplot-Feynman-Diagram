# feynplot_gui\core_ui\widgets\other_texts_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox, QApplication # Added QApplication for global position
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QMouseEvent
# from requests import get # This import seems unrelated to UI logic, consider removing if not used elsewhere
from feynplot_gui.debug.find_caller import print_caller_info # Keep this for debugging, or remove when done
from feynplot_gui.debug.debug_output import other_texts_print

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
        self.setWindowTitle("文本列表") # Window title adapted for text elements
        # self.setFixedWidth(200) # 通常在父级布局中控制宽度，这里注释掉是好的实践

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        # 存储 project_root，以便 print_caller_info 可以使用相对路径
        # 理想情况下，这个值应该由 MainController 在初始化时传入
        self.project_root = None 
        # 可以考虑在这里设置一个默认值，或者要求它在构造函数中传入
        # 例如: self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

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
        """
        Overrides the mouse press event to detect clicks on blank areas or list items.
        """
        # Call the base class's method first to handle standard UI selection logic
        super().mousePressEvent(event) 

        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            
            if item is None:
                # 仅在点击空白区域时打印堆栈，且将 project_root 传入
                # 如果 self.project_root 未设置，它会打印完整路径
                print_caller_info(start_depth=2, max_depth=5, message="OtherTextsWidget: Blank Area Click - Call Stack", base_path=self.project_root) 
                
                # If no item was clicked, it's a click on the blank area
                print("OtherTextsWidget: 点击了空白区域。")
                self.clearSelection() # Clear any existing selection
                self.list_blank_clicked.emit() # Emit the blank click signal
            else:
                # If an item was clicked, emit its selection signal
                text_element = item.data(Qt.ItemDataRole.UserRole)
                if text_element:
                    print(f"OtherTextsWidget: 点击了文本 {text_element.id}")
                    self.text_selected.emit(text_element) # Emit the selected TextElement object
        

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
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None

    def set_selected_item_in_list(self, item_to_select):
        """
        Selects an item in the list based on the provided TextElement object.
        If None is passed, all selections are cleared.
        This method is for UI synchronization only and should not trigger new selection signals.
        """
        # Ensure signals are blocked to prevent infinite loops from itemSelectionChanged
        self.blockSignals(True) 
        print("OtherTextsWidget: 设置选中项")
        self.clearSelection() # Clear any existing selection

        if item_to_select is not None: 
            for i in range(self.count()):
                item_widget = self.item(i)
                text_data = item_widget.data(Qt.ItemDataRole.UserRole)
                # Compare TextElement objects by their ID to ensure it's the same object
                if text_data and hasattr(item_to_select, 'id') and text_data.id == item_to_select.id:
                    item_widget.setSelected(True)
                    self.setCurrentItem(item_widget) 
                    self.scrollToItem(item_widget) 
                    break 
            
        # Unblock signals after processing
        self.blockSignals(False)