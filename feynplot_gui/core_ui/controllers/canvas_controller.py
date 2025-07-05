from PySide6.QtCore import QObject, Signal, QPointF, Qt, QTimer 
from typing import Optional, Callable, Tuple, Dict, Any

from regex import F # <-- Ensure these are imported

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

last_move_time = QTimer

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
        self._canvas_instance = FeynmanDiagramCanvas(
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
        self.canvas_widget.object_edited.connect(self._handle_object_edited_on_canvas_widget)
        self.canvas_widget.object_deleted.connect(self._handle_object_deleted_on_canvas_widget)
        self.canvas_widget.object_double_clicked.connect(self._handle_object_double_clicked_on_canvas_widget)
        self.canvas_widget.object_moved.connect(self._handle_object_moved_on_canvas_widget)
        self.canvas_widget.blank_double_clicked.connect(self._handle_blank_double_clicked_on_canvas_widget)
        self.canvas_widget.selection_cleared.connect(self._handle_selection_cleared_on_canvas_widget)
        self.canvas_widget.key_delete_pressed.connect(self._handle_key_delete_pressed)
        self.canvas_widget.add_line_from_vertex_requested.connect(self._handle_add_line_from_vertex_requested)
        # Connect CanvasWidget's pan and zoom signals
        self.canvas_widget.canvas_panned.connect(self._handle_canvas_panned_start)
        self.canvas_widget.canvas_zoomed.connect(self._handle_canvas_zoomed) # <-- This is where the zoom signal is connected
        self.main_controller.toolbox_controller.toggle_grid_visibility_requested.connect(self.toggle_grid_visibility) # Example if MainController forwards it


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
        return self._canvas_instance

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
        self._canvas_instance.render(
            vertices_list, 
            lines_list,
            **render_kwargs # <--- 将所有接收到的 kwargs 传递下去
        )

        # 确保 MatplotlibBackend.render 完成后，text controller 拿到的是最新的 ax
        self.main_controller.other_texts_controller.draw_texts_on_canvas(self._canvas_instance.ax) 
        # self.get_ax().grid(True)
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


    def _perform_hit_test(self, x: float, y: float) -> Tuple[Optional[str], Optional[str]]:
        """
        执行点击测试，判断点击是否落在对象（顶点或线条）上。
        此方法需要根据 Matplotlib 的绘制方式准确判断，特别是考虑到存储在 plot_points 中的复杂线条路径。
        """
        # 遍历顶点进行点击检测
        for vertex in self.diagram_model.vertices:
            # 简单的距离检查，0.5 是经验值，根据顶点视觉大小调整
            dist_sq = (x - vertex.x)**2 + (y - vertex.y)**2
            if dist_sq < 0.5**2: # 假设点击半径为 0.5 数据单位
                return vertex.id, "vertex"

        # 遍历线条进行点击检测
        for line in self.diagram_model.lines:
            # 确保线条有 plot_points 且至少包含两个点以构成线段
            if not hasattr(line, 'plot_points') or not line.plot_points or len(line.plot_points) < 2:
                continue # 跳过没有有效绘制路径的线条

            num_plot_points = len(line.plot_points)
            
            # --- 优化开始：根据点数均分采样，最多遍历 30 个点 ---
            # 如果点的数量小于等于 30，则遍历所有点
            if num_plot_points <= 30:
                indices_to_check = range(num_plot_points - 1)
            else:
                # 否则，从总点数中均匀选择 30 个点（或更少，取决于 num_plot_points - 1 是否大于 0）
                # 确保步长至少为 1，避免无限循环
                step = max(1, (num_plot_points - 1) // 30) 
                indices_to_check = range(0, num_plot_points - 1, step)
            # --- 优化结束 ---

            # 现在，遍历由 plot_points 定义的各个线段
            for i in indices_to_check:
                # 确保 i+1 不超出范围
                if i + 1 >= num_plot_points:
                    continue 
                    
                p1_coords = np.array(line.plot_points[i])
                p2_coords = np.array(line.plot_points[i+1])

                line_vec = p2_coords - p1_coords
                mouse_vec = np.array([x, y]) - p1_coords

                line_len_sq = np.dot(line_vec, line_vec)

                # 如果线段是一个点（p1 == p2），跳过它
                if line_len_sq == 0:
                    continue

                # 将鼠标点投影到线段上
                t = np.dot(mouse_vec, line_vec) / line_len_sq
                t = max(0, min(1, t)) # 将 t 钳制在 [0, 1] 之间，确保投影在线段上

                # 找到线段上离鼠标点击最近的点
                closest_point = p1_coords + t * line_vec

                # 计算鼠标点击到这个最近点的距离平方
                dist_to_line_sq = (x - closest_point[0])**2 + (y - closest_point[1])**2

                # 如果距离在容忍范围内，则命中
                if dist_to_line_sq < 0.2**2: # 假设线条点击容差为 0.2 数据单位
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
            # return
            pass

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


    def _handle_object_edited_on_canvas_widget(self, item_id: str, item_type: str):
        """
        Handles object edited signal from CanvasWidget.
        Notifies MainController to update global selection state.
        """
        obj = None
        if item_type == "vertex":
            obj = self._get_item_by_id(self.diagram_model.vertices, item_id)
            if isinstance(obj, Vertex):
                self.main_controller.vertex_controller._on_edit_vertex_requested_from_list(obj)
        elif item_type == "line":
            obj = self._get_item_by_id(self.diagram_model.lines, item_id)
            if isinstance(obj, Line):
                self.main_controller.line_controller._on_request_edit_line(obj)


    def _handle_object_deleted_on_canvas_widget(self, item_id: str, item_type: str):
        """
        Handles object deleted signal from CanvasWidget.
        Notifies MainController to update global selection state.
        """
        obj = None
        if item_type == "vertex":
            obj = self._get_item_by_id(self.diagram_model.vertices, item_id)
            if isinstance(obj, Vertex):
                self.main_controller.vertex_controller._on_delete_vertex_requested_from_list(obj)
        elif item_type == "line":
                obj = self._get_item_by_id(self.diagram_model.lines, item_id)
                if isinstance(obj, Line):
                    self.main_controller.line_controller._on_request_delete_line(obj)

    def _handle_blank_double_clicked_on_canvas_widget(self, position: QPointF): # <--- **修改此处，接受 QPointF 参数**
        """
        Handles blank double-click signal from CanvasWidget.
        Notifies MainController to open new vertex creation dialog at the given position.
        """
        self.main_controller.status_message.emit(f"Canvas double-clicked at: ({position.x():.2f}, {position.y():.2f})")
        
        # Now, pass the coordinates to add_vertex
        # Assuming add_vertex can take optional x, y coordinates
        # You might need to adjust your add_vertex method signature in FeynmanDiagram
        self.main_controller.diagram_model.add_vertex(position.x(), position.y()) 
        
        self.main_controller.update_all_views() # Refresh the canvas to show the new vertex


    def _handle_add_line_from_vertex_requested(self, start_vertex_id: str):
        """
        Handles add line from vertex request signal from MainController.
        Notifies CanvasWidget to start line creation mode.
        """
        self.main_controller.add_line_between_vertices(start_vertex_id)

    def toggle_grid_visibility(self):
        """
        槽函数：切换画布的网格可见性。
        """
        self._canvas_instance.switch_grid_state()
        print(f"Grid visibility toggled. Current state: {self._canvas_instance.grid_on}")
        self.main_controller.update_all_views(canvas_options ={"auto_scale": False})
        # Optional: Update status message
        # status_msg = "网格已显示" if self._grid_visible else "网格已隐藏"
        # self.main_controller.status_message.emit(status_msg)

    def set_update_interval(self, interval: int):
        """
        槽函数：设置画布更新间隔。
        """
        self.canvas_widget.set_update_interval(interval)