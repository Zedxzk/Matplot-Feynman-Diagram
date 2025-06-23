# feynplot_gui/controllers/canvas_controller.py

from PySide6.QtCore import QObject, Signal, QPointF, Qt # Import Qt for cursor

# 导入 CanvasWidget，它现在是画布的 "视图" 部分
from feynplot_gui.widgets.canvas_widget import CanvasWidget

# 导入你的 MatplotlibBackend
from feynplot.drawing.renderer import MatplotlibBackend

# 导入模型相关类
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line


from debug_utils import cout3


class CanvasController(QObject):
    # CanvasController 自身发出的信号，主要用于通知 MainController 完成特定操作
    line_creation_completed = Signal(str, str) # 当收集到两个顶点完成线条创建时发出 (start_vertex_id, end_vertex_id)

    def __init__(self, diagram_model: FeynmanDiagram, canvas_widget: CanvasWidget, main_controller: QObject):
        super().__init__()

        self.diagram_model = diagram_model
        self.canvas_widget = canvas_widget
        self.main_controller = main_controller

        # 实例化 MatplotlibBackend，同时传入 Figure 和 Axes 对象。
        # MatplotlibBackend 会在内部管理其 Figure 和 Axes。
        cout3(f"创建 MatplotlibBackend，Figure: {self.canvas_widget.get_figure()}，Axes: {self.canvas_widget.get_axes()}")
        self._matplotlib_backend = MatplotlibBackend(
            fig=self.canvas_widget.get_figure(), 
            ax=self.canvas_widget.get_axes()     
        )

        # 状态：用于添加线条模式，跟踪第一个选中的顶点
        self._first_vertex_for_line = None
        # 当前画布操作模式，由 MainController 设定
        self._current_canvas_mode = "select"

        # 连接 CanvasWidget 发出的用户交互信号到 CanvasController 的槽函数
        self.canvas_widget.canvas_clicked.connect(self._handle_canvas_click)
        self.canvas_widget.object_selected.connect(self._handle_object_selected_on_canvas_widget)
        self.canvas_widget.object_double_clicked.connect(self._handle_object_double_clicked_on_canvas_widget)
        self.canvas_widget.object_moved.connect(self._handle_object_moved_on_canvas_widget)
        self.canvas_widget.selection_cleared.connect(self._handle_selection_cleared_on_canvas_widget)
        self.canvas_widget.key_delete_pressed.connect(self._handle_key_delete_pressed) 

        # **CanvasWidget 的平移和缩放信号 (现在 CanvasController 负责处理)**
        # 当鼠标左键按下并拖动时，CanvasWidget 发出此信号（一次）
        self.canvas_widget.canvas_panned.connect(self._handle_canvas_panned_start)
        # 鼠标滚轮缩放信号
        self.canvas_widget.canvas_zoomed.connect(self._handle_canvas_zoomed)
        
        # **重要：将 hit_test 方法传递给 CanvasWidget**
        # CanvasController 需要提供一个 hit_test 方法给 CanvasWidget，
        # 因为 CanvasWidget 只是报告像素事件，需要控制器来解释这些事件。
        # 注意：由于 MatplotlibBackend 不提供 hit_test_object，
        # 我们需要在 CanvasController 或一个辅助类中实现它。
        # 这里使用一个简单的内部实现作为备用，但建议您在适当的层实现更精确的 hit_test。
        self.canvas_widget.set_hit_test_callback(self._perform_hit_test)

        # 平移状态追踪 (仅在 CanvasController 内部管理)
        self._is_panning_active = False # 标志平移是否正在进行
        self._pan_start_data_pos = None # 记录平移开始时的数据坐标

    def get_fig(self):
        return self.canvas_widget.get_figure()
    
    def get_ax(self):
        return self.canvas_widget.get_axes()
    
    def get_backend(self):
        return self._matplotlib_backend

    def set_mode(self, mode: str):
        """
        设置当前画布的模式（如“选择”、“添加顶点”、“添加线条”）。
        由 MainController 调用。
        """
        self._current_canvas_mode = mode
        self.canvas_widget.set_mode(mode) # 通知 CanvasWidget 更新其内部模式和光标
        self.reset_line_creation_state() # 切换模式时重置线条创建状态

    def update_canvas(self):
        """
        从模型获取最新数据，并直接通过 MatplotlibBackend 进行绘制。
        这是 MainController 每次修改模型后，强制 Canvas 刷新的入口。
        """
        vertices_data = self.diagram_model.vertices
        lines_data = self.diagram_model.lines
        
        selected_item = self.main_controller.get_selected_item() 

        # **关键：在调用渲染器之前，更新模型对象的选中状态**
        # 遍历所有顶点，设置它们的 is_selected 状态
        for vertex_id, vertex in vertices_data.items():
            vertex.is_selected = (selected_item and selected_item.id == vertex_id and isinstance(selected_item, Vertex))
        
        # 遍历所有线，设置它们的 is_selected 状态
        for line_id, line in lines_data.items():
            line.is_selected = (selected_item and selected_item.id == line_id and isinstance(selected_item, Line))

        # 调用 MatplotlibBackend 的 render 方法，它不关心选中状态，只绘制对象
        self._matplotlib_backend.render(
            list(vertices_data.values()), # 确保传递的是列表
            list(lines_data.values())    # 确保传递的是列表
        )

        # 告诉 CanvasWidget 的 FigureCanvasQTAgg 实例需要重绘
        self.canvas_widget.draw_idle_canvas() 

    def set_selected_object(self, item: [Vertex, Line, None]):
        """
        接收 MainController 传来的当前选中对象，并触发画布更新以显示高亮。
        """
        # CanvasController 不直接管理高亮状态，而是通过 MainController 获取全局选中项
        # 然后在 update_canvas() 时将此信息用于更新模型对象的 is_selected 属性，
        # 最终由 MatplotlibBackend 和 plot_functions 完成高亮。
        self.update_canvas() # 重新绘制整个画布以更新高亮

    # --- CanvasWidget 信号处理槽函数 ---

    def _handle_canvas_click(self, pos: QPointF):
        """
        处理 CanvasWidget 发出的画布点击事件（非对象点击）。
        根据当前模式进行不同操作。
        """
        if self._current_canvas_mode == "add_vertex":
            self.main_controller.add_vertex_at_coords(pos.x(), pos.y())
        elif self._current_canvas_mode == "add_line":
            self.main_controller.status_message.emit("在添加线条模式下，请点击一个顶点。")
            self.reset_line_creation_state()


    def _handle_object_selected_on_canvas_widget(self, item_id: str, item_type: str):
        """
        处理 CanvasWidget 发出的对象选中信号。
        通知 MainController 更新全局选中状态。
        """
        if self._current_canvas_mode == "select":
            obj = None
            if item_type == "vertex":
                obj = self.diagram_model.get_vertex_by_id(item_id)
            elif item_type == "line":
                obj = self.diagram_model.get_line_by_id(item_id)
            
            self.main_controller.select_item(obj) # MainController 会处理选中并更新所有视图

        elif self._current_canvas_mode == "add_line":
            # 在添加线条模式下，我们只关心顶点
            if item_type == "vertex":
                self._collect_vertex_for_line(item_id)
            else:
                self.main_controller.status_message.emit("在添加线条模式下，您必须点击顶点。")
                self.reset_line_creation_state() # 如果点击的不是顶点，重置状态

    def _handle_object_double_clicked_on_canvas_widget(self, item_id: str, item_type: str):
        """
        处理 CanvasWidget 发出的对象双击信号。
        通知 MainController 打开属性编辑对话框。
        """
        obj = None
        if item_type == "vertex":
            obj = self.diagram_model.get_vertex_by_id(item_id)
        elif item_type == "line":
            obj = self.diagram_model.get_line_by_id(item_id)
        
        self.main_controller.edit_item_properties(obj)


    def _handle_object_moved_on_canvas_widget(self, item_id: str, new_pos: QPointF):
        """
        处理 CanvasWidget 发出的对象移动信号（仅限顶点）。
        通知 MainController 更新模型中顶点的位置。
        """
        # MainController 应该直接监听 CanvasWidget 的 object_moved 信号来更新模型。
        # 此处 CanvasController 仅是转发或不处理，取决于 MainController 的设计。
        # 假设 MainController 监听了，这里不需要额外逻辑。
        pass 


    def _handle_selection_cleared_on_canvas_widget(self):
        """
        处理 CanvasWidget 发出的清空选中信号。
        通知 MainController 清空全局选中状态。
        """
        self.main_controller.clear_selection()

    def _handle_key_delete_pressed(self):
        """
        处理 CanvasWidget 发出的删除键按下信号。
        通知 MainController 删除当前选中对象。
        """
        self.main_controller.delete_selected_object()


    # --- 画布平移和缩放逻辑 (在 CanvasController 中实现) ---

    def _handle_canvas_panned_start(self, pan_start_data_pos: QPointF):
        """
        处理 CanvasWidget 发出的画布平移开始信号。
        连接 Matplotlib 的 motion_notify_event 以实现连续平移。
        """
        self._pan_start_data_pos = pan_start_data_pos
        self._is_panning_active = True
        
        # 连接 Matplotlib Canvas 的 motion_notify_event 和 button_release_event
        # 使用 lambda 函数捕获 connection ID，以便稍后可以断开
        self._motion_cid = self.canvas_widget.get_figure().canvas.mpl_connect('motion_notify_event', self._continuous_pan_update)
        self._release_cid = self.canvas_widget.get_figure().canvas.mpl_connect('button_release_event', self._handle_canvas_panned_end)
        
        # 设置光标
        self.canvas_widget.setCursor(Qt.ClosedHandCursor)


    def _continuous_pan_update(self, event):
        """
        辅助方法，处理持续的鼠标移动，当处于平移模式时。
        """
        if not self._is_panning_active:
            # 如果平移已经停止，这里不应该被调用，但作为安全措施检查
            return

        # 确保事件在坐标轴内
        if event.inaxes != self.get_ax():
            return

        # 确保数据坐标有效
        if event.xdata is None or event.ydata is None:
            return

        current_x, current_y = event.xdata, event.ydata
        start_x, start_y = self._pan_start_data_pos.x(), self._pan_start_data_pos.y()

        # 计算鼠标移动的位移
        dx = current_x - start_x
        dy = current_y - start_y

        # 获取当前轴限
        xlim = self.get_ax().get_xlim()
        ylim = self.get_ax().get_ylim()

        # 应用平移：通过减去位移来移动轴限，实现内容移动
        self.get_ax().set_xlim(xlim[0] - dx, xlim[1] - dy) # Note: Fixed typo, should be dx for x and dy for y
        self.get_ax().set_ylim(ylim[0] - dy, ylim[1] - dy)

        self.canvas_widget.draw_idle_canvas()

        # 重要的是：在平移过程中，`_pan_start_data_pos` 应该更新为当前的鼠标位置
        # 这样每次移动都是相对于上次绘制的位置，实现平滑拖动效果
        self._pan_start_data_pos = QPointF(current_x, current_y)


    def _handle_canvas_panned_end(self, event):
        """
        处理 CanvasWidget 发出的画布平移结束信号。
        """
        if event.button == 1: # 确保是左键释放
            self._is_panning_active = False
            self._pan_start_data_pos = None
            
            # 断开连接，避免内存泄漏或意外行为
            if hasattr(self, '_motion_cid') and self._motion_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._motion_cid)
                self._motion_cid = None
            if hasattr(self, '_release_cid') and self._release_cid is not None:
                self.canvas_widget.get_figure().canvas.mpl_disconnect(self._release_cid)
                self._release_cid = None
            
            # 恢复光标到默认状态（或基于当前模式的光标）
            self.canvas_widget.setCursor(Qt.ArrowCursor)


    def _handle_canvas_zoomed(self, mouse_pos: QPointF, scale_factor: float):
        """
        处理 CanvasWidget 发出的画布缩放信号。
        根据鼠标位置和缩放因子更新 Matplotlib 坐标轴的范围。
        """
        x_mouse, y_mouse = mouse_pos.x(), mouse_pos.y()
        
        xlim = self.get_ax().get_xlim()
        ylim = self.get_ax().get_ylim()

        # 计算新的轴限，以鼠标位置为中心进行缩放
        new_xlim = [x_mouse - (x_mouse - xlim[0]) * scale_factor,
                    x_mouse + (xlim[1] - x_mouse) * scale_factor]
        new_ylim = [y_mouse - (y_mouse - ylim[0]) * scale_factor,
                    y_mouse + (ylim[1] - y_mouse) * scale_factor]

        self.get_ax().set_xlim(new_xlim)
        self.get_ax().set_ylim(new_ylim)
        self.canvas_widget.draw_idle_canvas() # 触发重绘

    # --- 线条创建逻辑 ---
    def _collect_vertex_for_line(self, vertex_id: str):
        """
        在添加线条模式下，收集用户点击的顶点。
        """
        clicked_vertex = self.diagram_model.get_vertex_by_id(vertex_id)

        if clicked_vertex is None:
            self.main_controller.status_message.emit("点击的不是有效顶点。")
            self.reset_line_creation_state()
            return

        if self._first_vertex_for_line is None:
            self._first_vertex_for_line = clicked_vertex
            self.main_controller.status_message.emit(f"选中起始顶点: {clicked_vertex.id}。请点击第二个顶点。")
            # 此时 `clicked_vertex.is_selected` 应该已经被 MainController 设置为 True
            # MainController 的 `select_item` 方法应该处理这个，并触发 update_canvas
            # 如果没有，确保这里触发一次 update_canvas() 来高亮第一个顶点
            self.update_canvas() 
        else:
            if self._first_vertex_for_line.id == clicked_vertex.id:
                self.main_controller.status_message.emit("不能连接同一个顶点。请选择不同的顶点。")
                return

            self.line_creation_completed.emit(self._first_vertex_for_line.id, clicked_vertex.id)
            self.reset_line_creation_state() # 创建完成后重置状态

    def reset_line_creation_state(self):
        """
        重置线条创建的内部状态，清除已选的第一个顶点。
        """
        if self._first_vertex_for_line:
            self.main_controller.status_message.emit("线条创建模式已重置。")
            self._first_vertex_for_line = None
            # 清除临时高亮：通过 MainController 清空选中状态，然后更新画布
            self.main_controller.clear_selection() 
        # 如果没有 _first_vertex_for_line，则无需重置或更新画布

    # --- Hit Test Implementation (within CanvasController or an auxiliary class) ---
    def _perform_hit_test(self, x: float, y: float) -> (str, str):
        """
        执行点击检测，判断点击位置是否在某个对象（顶点或线）上。
        CanvasWidget 会调用此方法。
        此方法需要根据 Matplotlib 绘制的实际情况进行精确检测。
        由于 MatplotlibBackend 未提供，这里提供一个基础实现作为参考。
        更精确的实现可能需要遍历 Matplotlib 的 Artist 对象并检查它们的 contains 方法。
        """
        # 遍历顶点进行检测
        for v_id, vertex in self.diagram_model.vertices.items():
            # 假设一个点击容差，例如像素坐标系下的某个半径
            # 这里是数据坐标系，需要考虑缩放
            # 简单距离检测，0.5是一个经验值，可能需要根据实际显示大小调整
            # 理想情况下，应该将数据坐标转换为像素坐标进行更精确的点击检测
            dist_sq = (x - vertex.x)**2 + (y - vertex.y)**2
            # 假设顶点有一个默认的点击半径，或者根据其绘制大小来决定
            # 这里我们假设一个统一的“可点击区域”半径，例如0.5个单位
            if dist_sq < 0.5**2: 
                return vertex.id, "vertex"
        
        # 遍历线进行检测 (更复杂，以下仅为示意性代码，可能不完全准确)
        for l_id, line in self.diagram_model.lines.items():
            start_v = self.diagram_model.get_vertex_by_id(line.start_vertex_id)
            end_v = self.diagram_model.get_vertex_by_id(line.end_vertex_id)
            if start_v and end_v:
                # 简单地检查鼠标是否靠近线段。精确的“点到线段距离”算法更复杂。
                # 这是一个非常简化的判断，实际应用中推荐使用专门的几何库或Matplotlib的Path/Artist.contains()方法。
                # 计算线段向量
                line_vec = np.array([end_v.x - start_v.x, end_v.y - start_v.y])
                # 计算从起点到鼠标点的向量
                mouse_vec = np.array([x - start_v.x, y - start_v.y])
                
                # 计算投影长度
                line_len_sq = np.dot(line_vec, line_vec)
                if line_len_sq == 0: # 避免除以零，如果是点
                    continue
                
                t = np.dot(mouse_vec, line_vec) / line_len_sq
                
                # 确保投影在线段范围内 [0, 1]
                t = max(0, min(1, t))
                
                # 计算线上最近点
                closest_point = np.array([start_v.x, start_v.y]) + t * line_vec
                
                # 计算鼠标点到线上最近点的距离
                dist_to_line_sq = (x - closest_point[0])**2 + (y - closest_point[1])**2
                
                # 假设线的点击容差，例如 0.2 个单位
                if dist_to_line_sq < 0.2**2:
                    return line.id, "line"

        return None, None