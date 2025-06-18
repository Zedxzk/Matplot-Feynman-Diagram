# feynplot_gui/controllers/navigation_bar_controller.py

from PySide6.QtCore import QObject, Signal # Import QObject and Signal
from feynplot_gui.widgets.navigation_bar_widget import NavigationBarWidget # Import the specific widget

# 【Important Change】Remove direct import of MainController to prevent circular imports
# from feynplot_gui.controllers.main_controller import MainController 

class NavigationBarController(QObject): # Inherit from QObject
    def __init__(self, navigation_bar_widget: NavigationBarWidget, main_controller: 'MainController'): # Use string for type hint
        super().__init__() # Call QObject's constructor

        self.navigation_bar_widget = navigation_bar_widget # Renamed from self.navbar for clarity
        self.main_controller = main_controller # Store reference to MainController

        self.setup_connections()
        # Initial status update for menus/buttons
        self.update_object_menu_status(None)


    def setup_connections(self):
        """Connects signals from the navigation bar widget to controller slots."""
        # File Menu Actions
        self.navigation_bar_widget.save_project_action_triggered.connect(self.main_controller.save_diagram_to_file)
        self.navigation_bar_widget.load_project_action_triggered.connect(self.main_controller.load_diagram_from_file)
        # self.navigation_bar_widget.clear_diagram_action_triggered.connect(self.main_controller.clear_diagram)
        
        # Edit Menu Actions
        # self.navigation_bar_widget.add_vertex_button_clicked.connect(self.main_controller.start_add_vertex_process)
        # self.navigation_bar_widget.add_line_button_clicked.connect(self.main_controller.start_add_line_process)
        # # self.navigation_bar_widget.edit_selected_object_triggered.connect(self.main_controller.edit_selected_object_properties)
        # self.navigation_bar_widget.delete_selected_object_triggered.connect(self.main_controller.delete_selected_object)

        # Other actions can be connected here as needed
        # self.navigation_bar_widget.undo_action_triggered.connect(self.main_controller.undo)
        # self.navigation_bar_widget.redo_action_triggered.connect(self.main_controller.redo)

    def update_object_menu_status(self, selected_item: object):
        """
        Updates the enabled/disabled state of 'Edit' and 'Delete' menu items
        based on whether an item is selected.
        This method is called by MainController's selection_changed signal.
        """
        is_item_selected = (selected_item is not None)
        # self.navigation_bar_widget.set_edit_delete_actions_enabled(is_item_selected)
        self.main_controller.status_message.emit(f"菜单状态更新：{'启用' if is_item_selected else '禁用'}编辑/删除选项。")

    # The original on_save and update methods are now handled by MainController or the status update logic above.
    # self.main_controller.save_diagram_to_file()
    # self.update_object_menu_status(selected_item)