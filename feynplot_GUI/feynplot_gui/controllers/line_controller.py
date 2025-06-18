# feynplot_gui/controllers/line_controller.py

from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog
from PySide6.QtCore import Qt, QObject, Signal

# Import core model classes
from feynplot.core.line import Line, LineStyle, FermionLine, GluonLine, PhotonLine
from feynplot.core.diagram import FeynmanDiagram 

# Import UI Widgets and Dialogs
from feynplot_gui.widgets.line_list_widget import LineListWidget 
# Import the line-specific edit dialog function directly
from feynplot_gui.controllers.line_dialogs.edit_line import open_edit_line_dialog 

# Type hint for MainController to avoid circular imports
class MainController: 
    pass 

class LineController(QObject):
    def __init__(self, diagram_model: FeynmanDiagram, line_list_widget: LineListWidget, main_controller: 'MainController'):
        super().__init__()

        self.diagram_model = diagram_model
        self.line_list_widget = line_list_widget
        self.main_controller = main_controller 

        self.setup_connections()
        self.update_line_list() 

    def setup_connections(self):
        """Connects LineListWidget signals to this controller's slots."""
        self.line_list_widget.line_selected.connect(self._on_line_list_selected)
        self.line_list_widget.line_double_clicked.connect(self._on_line_list_double_clicked)
        
        # Connect context menu requests directly to this controller's handling methods
        self.line_list_widget.request_edit_line.connect(self._on_request_edit_line)
        self.line_list_widget.request_delete_line.connect(self._on_request_delete_line)

    def update_line_list(self):
        """
        Refreshes the line list view based on data in diagram_model.
        Lines are sorted by their unique identifier (ID) in ascending order.
        """
        self.line_list_widget.clear() # 清空所有现有项目

        # 关键改动：在这里对线条列表进行排序
        # 假设 line.id 是一个唯一的、可比较的标识符（例如，整数或字符串）
        sorted_lines = sorted(self.diagram_model.lines, key=lambda line: line.id)
        
        for line in sorted_lines:
            start_label = line.v_start.label if line.v_start else "None"
            end_label = line.v_end.label if line.v_end else "None"
            item_text = f"[{line.id}] Line: {line.label} ({start_label} -> {end_label})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, line) 
            self.line_list_widget.addItem(item)
        
        # 重新应用选中状态
        current_selected = self.main_controller.get_selected_item()
        if isinstance(current_selected, Line):
            self.set_selected_item_in_list(current_selected)

        self.main_controller.status_message.emit("线条列表已更新并按ID排序。")

    def set_selected_item_in_list(self, item: [Line, None]):
        """
        Receives selected item from MainController and sets/clears selection in the line list.
        """
        self.line_list_widget.clearSelection() 

        if isinstance(item, Line):
            for i in range(self.line_list_widget.count()):
                list_item = self.line_list_widget.item(i)
                stored_line = list_item.data(Qt.ItemDataRole.UserRole)
                if stored_line and stored_line.id == item.id:
                    list_item.setSelected(True)
                    self.line_list_widget.scrollToItem(list_item)
                    break

    # --- Slot functions: Respond to LineListWidget signals ---

    def _on_line_list_selected(self, line: Line):
        """
        Triggered when a user selects a line in the list.
        Notifies MainController to manage the selection state.
        """
        if line:
            self.main_controller.select_item(line) 
        else:
            self.main_controller.select_item(None) 

    def _on_line_list_double_clicked(self, line: Line):
        """
        Triggered when a user double-clicks a line in the list.
        Directly opens the edit dialog, then notifies MainController for UI refresh.
        """
        if line:
            self._on_request_edit_line(line) # Directly call the edit handling logic
        else:
            self.main_controller.status_message.emit("No line selected to edit.")

    # --- New Slot functions: Respond to context menu requests ---
    def _on_request_edit_line(self, line: Line):
        """
        Handles the "Edit Line" request from the LineListWidget context menu
        or a double-click event. Opens the line-specific edit dialog directly.
        """
        self.main_controller.status_message.emit(f"Opening edit dialog for line: {line.id}")
        
        # Directly call the line-specific edit dialog function
        parent_widget = self.main_controller.canvas_controller.canvas_widget # Get a suitable parent for the dialog
        if open_edit_line_dialog(line, self.diagram_model, parent_widget=parent_widget):
            # If dialog accepted, notify MainController to update everything
            self.main_controller.update_all_views() 
            self.main_controller.status_message.emit(f"Successfully edited line: {line.id}")
        else:
            self.main_controller.status_message.emit(f"Line edit for {line.id} cancelled.")

    def _on_request_delete_line(self, line: Line):
        """
        Handles the "Delete Line" request from the LineListWidget context menu.
        Delegates deletion logic to MainController, which manages model changes.
        """
        self.main_controller.status_message.emit(f"Requesting deletion for line: {line.id}")
        # Deletion is still a global model change, so it's appropriate for MainController to handle it.
        self.main_controller.delete_item(line) 

    def update(self):
        """A general update method, called by MainController if needed."""
        self.update_line_list()