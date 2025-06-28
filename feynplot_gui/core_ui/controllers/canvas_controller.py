# feynplot_gui/controllers/canvas_controller.py

from PySide6.QtCore import QObject, Signal, QPointF, Qt
from typing import Optional, Callable # <-- Ensure these are imported

# Import CanvasWidget, which is the "view" part of the canvas
from feynplot_gui.core_ui.widgets.canvas_widget import CanvasWidget

# Import your MatplotlibBackend (renderer, don't modify it directly)
from feynplot.drawing.renderer import MatplotlibBackend

# Import your core model classes (ensure Vertex and Line have is_selected property)
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line

# from debug_utils import cout3 # Uncomment if you have this utility for debugging

import numpy as np # <-- Ensure numpy is imported for hit testing

class CanvasController(QObject):
    # CanvasController's own signals, mainly to notify MainController of completed actions
    line_creation_completed = Signal(str, str) # Emitted when two vertices are selected for line creation (start_vertex_id, end_vertex_id)

    def __init__(self, diagram_model: FeynmanDiagram, canvas_widget: CanvasWidget, main_controller: QObject):
        super().__init__()

        self.diagram_model = diagram_model
        self.canvas_widget = canvas_widget
        self.main_controller = main_controller

        # Instantiate MatplotlibBackend, passing Figure and Axes objects.
        # cout3(f"Creating MatplotlibBackend, Figure: {self.canvas_widget.get_figure()}, Axes: {self.canvas_widget.get_axes()}") # Debug info
        self._matplotlib_backend = MatplotlibBackend(
            fig=self.canvas_widget.get_figure(),
            ax=self.canvas_widget.get_axes()
        )

        # State: for 'add line' mode, track the first selected vertex
        self._first_vertex_for_line = None
        # Current canvas operation mode, set by MainController
        self._current_canvas_mode = "select"

        # Connect CanvasWidget's user interaction signals to CanvasController's slots
        self.canvas_widget.canvas_clicked.connect(self._handle_canvas_click)
        self.canvas_widget.object_selected.connect(self._handle_object_selected_on_canvas_widget)
        self.canvas_widget.object_double_clicked.connect(self._handle_object_double_clicked_on_canvas_widget)
        self.canvas_widget.object_moved.connect(self._handle_object_moved_on_canvas_widget)
        self.canvas_widget.selection_cleared.connect(self._handle_selection_cleared_on_canvas_widget)
        self.canvas_widget.key_delete_pressed.connect(self._handle_key_delete_pressed)

        # Connect CanvasWidget's pan and zoom signals
        self.canvas_widget.canvas_panned.connect(self._handle_canvas_panned_start)
        self.canvas_widget.canvas_zoomed.connect(self._handle_canvas_zoomed) # <-- This is where the zoom signal is connected

        # Critical: Provide the hit_test method to CanvasWidget
        self.canvas_widget.set_hit_test_callback(self._perform_hit_test)

        # Pan state tracking (managed internally by CanvasController)
        self._is_panning_active = False
        self._pan_start_data_pos = None
        self._motion_cid: Optional[int] = None # Stores Matplotlib event connection ID
        self._release_cid: Optional[int] = None # Stores Matplotlib event connection ID

    def get_fig(self):
        return self.canvas_widget.get_figure()

    def get_ax(self):
        return self.canvas_widget.get_axes()

    def get_backend(self):
        return self._matplotlib_backend

    def set_mode(self, mode: str):
        """
        Sets the current canvas mode (e.g., 'select', 'add_vertex', 'add_line').
        Called by MainController.
        """
        self._current_canvas_mode = mode
        self.canvas_widget.set_mode(mode) # Notify CanvasWidget to update its internal mode and cursor
        self.reset_line_creation_state() # Reset line creation state when changing mode

    def update_canvas(self):
        """
        Retrieves the latest data from the model and draws it directly via MatplotlibBackend.
        This is the entry point for MainController to force canvas refresh after model changes.
        """
        # Assuming diagram_model.vertices and diagram_model.lines are lists of objects
        vertices_list = self.diagram_model.vertices
        lines_list = self.diagram_model.lines

        selected_item = self.main_controller.get_selected_item()

        # Key: Update the is_selected state of model objects BEFORE calling the renderer
        # Iterate all vertices and set their is_selected state
        for vertex in vertices_list:
            vertex.is_selected = False # Clear all previous selections
            if selected_item and selected_item.id == vertex.id and isinstance(selected_item, Vertex):
                vertex.is_selected = True

        # Iterate all lines and set their is_selected state
        for line in lines_list:
            line.is_selected = False # Clear all previous selections
            if selected_item and selected_item.id == line.id and isinstance(selected_item, Line):
                line.is_selected = True

        # Call MatplotlibBackend's render method; it only draws the objects based on their properties
        self._matplotlib_backend.render(
            vertices_list,
            lines_list
        )

        # Tell FigureCanvasQTAgg instance in CanvasWidget to redraw
        self.canvas_widget.draw_idle_canvas()

    def set_selected_object(self, item: [Vertex, Line, None]):
        """
        Receives the current selected object from MainController and triggers canvas update for highlighting.
        """
        self.update_canvas() # Redraw the entire canvas to update highlighting

    ### CanvasWidget Signal Handling Slots ###

    def _handle_canvas_click(self, pos: QPointF):
        """
        Handles canvas click events (not on objects) emitted by CanvasWidget.
        Performs different actions based on current mode.
        """
        if self._current_canvas_mode == "add_vertex":
            self.main_controller.add_vertex_at_coords(pos.x(), pos.y())
        elif self._current_canvas_mode == "add_line":
            self.main_controller.status_message.emit("In 'add line' mode, please click a vertex.")
            self.reset_line_creation_state()


    def _handle_object_selected_on_canvas_widget(self, item_id: str, item_type: str):
        """
        Handles object selection signal from CanvasWidget.
        Notifies MainController to update global selection state.
        """
        if self._current_canvas_mode == "select" or self._current_canvas_mode == "add_line":
            obj = None
            if item_type == "vertex":
                obj = self._get_item_by_id(self.diagram_model.vertices, item_id)
            elif item_type == "line":
                obj = self._get_item_by_id(self.diagram_model.lines, item_id)

            if self._current_canvas_mode == "select":
                self.main_controller.select_item(obj) # MainController handles selection and updates all views
            elif self._current_canvas_mode == "add_line":
                if item_type == "vertex": # Only vertices proceed with line creation
                    self._collect_vertex_for_line(item_id)
                else:
                    self.main_controller.status_message.emit("In 'add line' mode, you must click a vertex.")
                    self.reset_line_creation_state()


    def _handle_object_double_clicked_on_canvas_widget(self, item_id: str, item_type: str):
        """
        Handles object double-click signal from CanvasWidget.
        Notifies MainController to open property editing dialog.
        """
        obj = None
        if item_type == "vertex":
            obj = self._get_item_by_id(self.diagram_model.vertices, item_id)
        elif item_type == "line":
            obj = self._get_item_by_id(self.diagram_model.lines, item_id)

        self.main_controller.edit_item_properties(obj)


    def _handle_object_moved_on_canvas_widget(self, item_id: str, new_pos: QPointF):
        """
        Handles object movement signal (vertices only) from CanvasWidget.
        Notifies MainController to update the vertex's position in the model.
        """
        # The MainController should directly listen to CanvasWidget's object_moved signal to update the model.
        # CanvasController does not directly update the model here, it forwards to MainController.
        # Assuming MainController listens and handles this signal.
        pass


    def _handle_selection_cleared_on_canvas_widget(self):
        """
        Handles selection clear signal from CanvasWidget.
        Notifies MainController to clear global selection.
        """
        self.main_controller.clear_selection()

    def _handle_key_delete_pressed(self):
        """
        Handles Delete key press signal from CanvasWidget.
        Notifies MainController to delete the currently selected object.
        """
        self.main_controller.delete_selected_object()


    ### Utility method for getting item by ID from a list ###
    def _get_item_by_id(self, item_list: list, item_id: str):
        """Helper to find an item in a list by its 'id' attribute."""
        for item in item_list:
            if hasattr(item, 'id') and item.id == item_id:
                return item
        return None

    ### Canvas Panning and Zooming Logic ###

    def _handle_canvas_panned_start(self, pan_start_data_pos: QPointF):
        """
        Handles canvas pan start signal from CanvasWidget.
        Connects to Matplotlib's motion_notify_event for continuous panning.
        """
        self._pan_start_data_pos = pan_start_data_pos
        self._is_panning_active = True

        # Connect to Matplotlib Canvas's motion_notify_event and button_release_event
        self._motion_cid = self.canvas_widget.get_figure().canvas.mpl_connect('motion_notify_event', self._continuous_pan_update)
        self._release_cid = self.canvas_widget.get_figure().canvas.mpl_connect('button_release_event', self._handle_canvas_panned_end)

        # Set cursor
        self.canvas_widget.setCursor(Qt.ClosedHandCursor)


    def _continuous_pan_update(self, event):
        """
        Helper method to handle continuous mouse movement when in panning mode.
        """
        if not self._is_panning_active:
            return

        if event.inaxes != self.get_ax():
            return

        if event.xdata is None or event.ydata is None:
            return

        current_x, current_y = event.xdata, event.ydata
        start_x, start_y = self._pan_start_data_pos.x(), self._pan_start_data_pos.y()

        dx = current_x - start_x
        dy = current_y - start_y

        xlim = self.get_ax().get_xlim()
        ylim = self.get_ax().get_ylim()

        self.get_ax().set_xlim(xlim[0] - dx, xlim[1] - dx)
        self.get_ax().set_ylim(ylim[0] - dy, ylim[1] - dy)

        self.canvas_widget.draw_idle_canvas()

        self._pan_start_data_pos = QPointF(current_x, current_y)


    def _handle_canvas_panned_end(self, event):
        """
        Handles canvas pan end signal from CanvasWidget.
        """
        if event.button == 1: # Ensure it's left button release
            self._is_panning_active = False
            self._pan_start_data_pos = None

            # Disconnect event handlers to prevent memory leaks or unwanted behavior
            if self._motion_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._motion_cid)
                self._motion_cid = None
            if self._release_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._release_cid)
                self._release_cid = None

            # Restore cursor to default state
            self.canvas_widget.setCursor(Qt.ArrowCursor)


    def _handle_canvas_zoomed(self, mouse_pos: QPointF, scale_factor: float):
        """
        Handles canvas zoom signal from CanvasWidget.
        Updates Matplotlib axes limits based on mouse position and zoom factor.
        """
        x_mouse, y_mouse = mouse_pos.x(), mouse_pos.y()

        xlim = self.get_ax().get_xlim()
        ylim = self.get_ax().get_ylim()

        # Calculate new axes limits, zooming around the mouse position
        new_xlim = [x_mouse - (x_mouse - xlim[0]) * scale_factor,
                    x_mouse + (xlim[1] - x_mouse) * scale_factor]
        new_ylim = [y_mouse - (y_mouse - ylim[0]) * scale_factor,
                    y_mouse + (ylim[1] - y_mouse) * scale_factor]

        self.get_ax().set_xlim(new_xlim)
        self.get_ax().set_ylim(new_ylim)
        self.canvas_widget.draw_idle_canvas()

    ### Line Creation Logic ###
    def _collect_vertex_for_line(self, vertex_id: str):
        """
        Collects clicked vertices in 'add line' mode.
        """
        clicked_vertex = self._get_item_by_id(self.diagram_model.vertices, vertex_id)

        if clicked_vertex is None:
            self.main_controller.status_message.emit("Clicked vertex is not valid.")
            self.reset_line_creation_state()
            return

        if self._first_vertex_for_line is None:
            self._first_vertex_for_line = clicked_vertex
            self.main_controller.status_message.emit(f"Start vertex selected: {clicked_vertex.id}. Please click the second vertex.")
            self.update_canvas() # Update canvas to highlight the first selected vertex
        else:
            if self._first_vertex_for_line.id == clicked_vertex.id:
                self.main_controller.status_message.emit("Cannot connect the same vertex. Please select a different vertex.")
                return

            # Emit signal to notify MainController that line creation is complete
            self.line_creation_completed.emit(self._first_vertex_for_line.id, clicked_vertex.id)
            self.reset_line_creation_state() # Reset state after creation

    def reset_line_creation_state(self):
        """
        Resets the internal state for line creation, clearing the first selected vertex.
        """
        if self._first_vertex_for_line:
            self.main_controller.status_message.emit("Line creation mode reset.")
            self._first_vertex_for_line = None
            self.main_controller.clear_selection() # Clear selection and trigger canvas update

    ### Hit Test Implementation ###
    def _perform_hit_test(self, x: float, y: float) -> tuple[Optional[str], Optional[str]]:
        """
        Performs hit testing to determine if a click is on an object (vertex or line).
        This method needs to be accurate based on how Matplotlib draws.
        """
        # Iterate over vertices for hit detection
        for vertex in self.diagram_model.vertices:
            # Simple distance check, 0.5 is an empirical value, adjust based on visual size of your vertices
            dist_sq = (x - vertex.x)**2 + (y - vertex.y)**2
            if dist_sq < 0.5**2: # Assuming a click radius of 0.5 data units
                return vertex.id, "vertex"

        # Iterate over lines for hit detection
        for line in self.diagram_model.lines:
            start_v = self._get_item_by_id(self.diagram_model.vertices, line.start_vertex_id)
            end_v = self._get_item_by_id(self.diagram_model.vertices, line.end_vertex_id)
            if start_v and end_v:
                # This is a simplified point-to-line segment distance check
                line_vec = np.array([end_v.x - start_v.x, end_v.y - start_v.y])
                mouse_vec = np.array([x - start_v.x, y - start_v.y])

                line_len_sq = np.dot(line_vec, line_vec)
                if line_len_sq == 0: # Avoid division by zero if it's a point
                    continue

                t = np.dot(mouse_vec, line_vec) / line_len_sq
                t = max(0, min(1, t)) # Ensure projection is within line segment [0, 1]

                closest_point = np.array([start_v.x, start_v.y]) + t * line_vec
                dist_to_line_sq = (x - closest_point[0])**2 + (y - closest_point[1])**2

                if dist_to_line_sq < 0.2**2: # Assuming a line click tolerance of 0.2 data units
                    return line.id, "line"

        return None, None