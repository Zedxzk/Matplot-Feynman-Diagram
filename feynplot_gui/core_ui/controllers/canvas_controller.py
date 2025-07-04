from PySide6.QtCore import QObject, Signal, QPointF, Qt
from typing import Optional, Callable, Tuple, Dict, Any # <-- Ensure these are imported

# Import CanvasWidget, which is the "view" part of the canvas
from feynplot_gui.core_ui.widgets.canvas_widget import CanvasWidget

# Import your MatplotlibBackend (renderer, don't modify it directly)
from feynplot.drawing.renderer import FeynmanDiagramCanvas

# Import your core model classes (ensure Vertex and Line have is_selected property)
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line
from feynplot_gui.core_ui.controllers.other_texts_controller import TextElement
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
        self._matplotlib_backend = FeynmanDiagramCanvas(
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

    def update_canvas(self, **render_kwargs: Any):
        """
        从模型中检索最新数据，并直接通过 MatplotlibBackend 绘制。
        这是 MainController 在模型更改后强制刷新画布的入口点。
        
        Args:
            **render_kwargs: 传递给 MatplotlibBackend.render 方法的额外关键词参数，
                             例如 'target_xlim', 'target_ylim', 'auto_scale' 等。
        """
        vertices_list = self.diagram_model.vertices
        lines_list = self.diagram_model.lines
        
        selected_item = self.main_controller.get_selected_item() 

        for vertex in vertices_list:
            vertex.is_selected = False 
            if selected_item and hasattr(selected_item, 'id') and selected_item.id == vertex.id and isinstance(selected_item, Vertex):
                vertex.is_selected = True

        for line in lines_list:
            line.is_selected = False 
            if selected_item and hasattr(selected_item, 'id') and selected_item.id == line.id and isinstance(selected_item, Line):
                line.is_selected = True

        for text_elem in self.main_controller.other_texts_controller.text_elements:
            text_elem.is_selected = False
            if selected_item and hasattr(selected_item, 'id') and selected_item.id == text_elem.id and isinstance(selected_item, TextElement):
                text_elem.is_selected = True

        # 调用 MatplotlibBackend 的 render 方法，并原样传递所有 render_kwargs
        self._matplotlib_backend.render(
            vertices_list, 
            lines_list,
            **render_kwargs # <--- 将所有接收到的 kwargs 传递下去
        )

        # 确保 MatplotlibBackend.render 完成后，text controller 拿到的是最新的 ax
        self.main_controller.other_texts_controller.draw_texts_on_canvas(self._matplotlib_backend.ax) 
        self.get_ax().grid(True)
        self.canvas_widget.draw_idle_canvas() 

    def set_selected_object(self, item: [Vertex, Line, None]):
        """
        Receives the current selected object from MainController and triggers canvas update for highlighting.
        Now, it should call MainController's update_all_views.
        """
        # Relaying to MainController to ensure all views are updated consistently
        self.main_controller.update_all_views() 

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
        处理来自 CanvasWidget 的对象移动信号。
        更新模型中的对象位置，并通知 MainController 重新绘制所有视图。
        """
        obj = None
        # 查找被移动的对象
        if any(v.id == item_id for v in self.diagram_model.vertices):
            obj = next((v for v in self.diagram_model.vertices if v.id == item_id), None)
            if obj:
                # 更新顶点位置
                obj.x = new_pos.x()
                obj.y = new_pos.y()
                # 同时更新受影响的线条的端点引用，确保数据一致性
                for line in self.diagram_model.lines:
                    if line.v_start.id == obj.id:
                        line.v_start = obj 
                    if line.v_end.id == obj.id:
                        line.v_end = obj

        # 如果是线条被拖动，目前你的模型结构不支持直接拖动线条，
        # 通常线条是连接顶点的，移动线条意味着移动其连接的顶点，这需要更复杂的逻辑。
        # 这里假设只有顶点可以被直接拖动。
        # 如果将来支持线条拖动，可能需要在这里添加逻辑。

        current_xlim = self.get_ax().get_xlim()
        current_ylim = self.get_ax().get_ylim()
        
        canvas_options = {}

        if obj:
            # --- 处理对象移动 ---
            needs_view_adjust = False
            adjusted_xlim = list(current_xlim)
            adjusted_ylim = list(current_ylim)
            
            # 定义一个小的边距，避免对象刚出视图就触发调整
            margin_x = (current_xlim[1] - current_xlim[0]) * 0.1
            margin_y = (current_ylim[1] - current_ylim[0]) * 0.1

            # 检查 X 轴边界
            if obj.x < current_xlim[0] + margin_x:
                adjusted_xlim[0] = obj.x - margin_x
                needs_view_adjust = True
            elif obj.x > current_xlim[1] - margin_x:
                adjusted_xlim[1] = obj.x + margin_x
                needs_view_adjust = True
            
            # 检查 Y 轴边界
            if obj.y < current_ylim[0] + margin_y:
                adjusted_ylim[0] = obj.y - margin_y
                needs_view_adjust = True
            elif obj.y > current_ylim[1] - margin_y:
                adjusted_ylim[1] = obj.y + margin_y
                needs_view_adjust = True

            if needs_view_adjust:
                canvas_options = {'target_xlim': tuple(adjusted_xlim), 'target_ylim': tuple(adjusted_ylim)}
            else:
                # 如果对象仍在视图内，直接更新画布以反映其新位置
                # 传入当前的视图限制，避免不必要的视图重置或自动缩放
                canvas_options = {'target_xlim': current_xlim, 'target_ylim': current_ylim}
        else:
            # --- 处理空白区域拖动（平移）---
            # item_id 为 None 或空字符串表示拖动的是空白区域
            # 需要计算拖动距离来平移视图
            if hasattr(self, '_last_mouse_data_pos') and self._last_mouse_data_pos is not None:
                drag_start_x, drag_start_y = self._last_mouse_data_pos
                
                # 计算拖动距离（从起始点到当前点）
                dx = new_pos.x() - drag_start_x
                dy = new_pos.y() - drag_start_y

                # 计算新的视图限制：将当前视图反向平移拖动距离
                new_xlim = (current_xlim[0] - dx, current_xlim[1] - dx)
                new_ylim = (current_ylim[0] - dy, current_ylim[1] - dy)

                canvas_options = {'target_xlim': new_xlim, 'target_ylim': new_ylim}
            else:
                # Fallback if _last_mouse_data_pos is not set (e.g., initial drag event)
                # In this case, simply redraw maintaining the current view
                canvas_options = {'target_xlim': current_xlim, 'target_ylim': current_ylim}
        
        # 统一通过 MainController 触发更新
        self.main_controller.update_all_views(canvas_options=canvas_options)


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

    def _handle_canvas_zoomed(self, mouse_pos: QPointF, scale_factor: float):
        """
        处理来自 CanvasWidget 的画布缩放信号。
        根据鼠标位置和缩放因子计算新的 Matplotlib 坐标轴限制，并传递给 MainController。
        """
        x_mouse, y_mouse = mouse_pos.x(), mouse_pos.y()

        current_xlim = self.get_ax().get_xlim()
        current_ylim = self.get_ax().get_ylim()

        # 计算新的坐标轴限制，围绕鼠标位置进行缩放
        new_xlim = (x_mouse - (x_mouse - current_xlim[0]) * scale_factor,
                    x_mouse + (current_xlim[1] - x_mouse) * scale_factor)
        new_ylim = (y_mouse - (y_mouse - current_ylim[0]) * scale_factor,
                    y_mouse + (current_ylim[1] - y_mouse) * scale_factor)
        
        # 关键点：将计算出的新轴限制作为字典传递给 MainController 的 update_all_views
        self.main_controller.update_all_views(canvas_options={'target_xlim': new_xlim, 'target_ylim': new_ylim})

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
            # Trigger full update via MainController to highlight the first selected vertex
            self.main_controller.update_all_views() 
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
            # Trigger full update via MainController to clear selection/highlight
            self.main_controller.clear_selection() 

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
            start_v = self._get_item_by_id(self.diagram_model.vertices, line.v_start.id)
            end_v = self._get_item_by_id(self.diagram_model.vertices, line.v_end.id)
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
    

    def _handle_canvas_panned_start(self, pan_start_data_pos: QPointF, current_pan_data_pos: QPointF):
        """
        处理 canvas_widget 发出的画布平移信号 (在 _on_mouse_move 中持续发出)。
        """
        # 第一次收到这个信号时，记录下平移的起始点
        if not self._is_panning_active:
            self._pan_start_data_pos = pan_start_data_pos # 记录初始按下点
            self._is_panning_active = True
            self.canvas_widget.setCursor(Qt.ClosedHandCursor)
        
        # 在连续平移中，每次收到信号都计算位移并更新视图
        self._continuous_pan_update(pan_start_data_pos, current_pan_data_pos)


    def _continuous_pan_update(self, pan_start_data_pos: QPointF, current_pan_data_pos: QPointF):
        """
        Helper method to handle continuous mouse movement when in panning mode.
        直接被 _handle_canvas_panned_start 调用，或者你也可以将其直接连接到 canvas_panned 信号。
        """
        if not self._is_panning_active:
            return

        start_x, start_y = pan_start_data_pos.x(), pan_start_data_pos.y()
        current_x, current_y = current_pan_data_pos.x(), current_pan_data_pos.y()

        dx = current_x - start_x
        dy = current_y - start_y

        current_xlim = self.get_ax().get_xlim()
        current_ylim = self.get_ax().get_ylim()

        # 计算新的视图限制：将当前视图反向平移拖动距离
        new_xlim = (current_xlim[0] - dx, current_xlim[1] - dx)
        new_ylim = (current_ylim[0] - dy, current_ylim[1] - dy)

        # 关键：通过 MainController 的 update_all_views 来更新视图
        self.main_controller.update_all_views(canvas_options={'target_xlim': new_xlim, 'target_ylim': new_ylim})

        # No need to update _pan_start_data_pos here as canvas_panned signal always provides
        # the initial press point and the current mouse position.


    def _handle_canvas_panned_end(self, event):
        """
        Handles canvas pan end signal from CanvasWidget.
        """
        # This method should be connected to a Matplotlib 'button_release_event' directly from CanvasWidget
        # to ensure it's triggered when the mouse button is released anywhere.
        if event.button == 1: # Ensure it's left button release
            self._is_panning_active = False
            self._pan_start_data_pos = None

            # Disconnect event handlers to prevent memory leaks or unwanted behavior
            # These connections are typically managed in CanvasWidget, so ensure this logic
            # aligns with where Matplotlib event connections are made/broken.
            if self._motion_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._motion_cid)
                self._motion_cid = None
            if self._release_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._release_cid)
                self._release_cid = None

            # Restore cursor to default state
            self.canvas_widget.setCursor(Qt.ArrowCursor)