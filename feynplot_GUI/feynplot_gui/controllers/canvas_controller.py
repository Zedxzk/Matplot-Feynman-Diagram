# feynplot_gui/controllers/canvas_controller.py

from PySide6.QtCore import QObject, Signal, QPointF

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

        # **关键修正：实例化 MatplotlibBackend，同时传入 Figure 和 Axes 对象**
        # CanvasWidget 必须提供其内部的 Figure 和 Axes 对象。
        cout3(f"创建 MatplotlibBackend，Figure: {self.canvas_widget.get_figure()}，Axes: {self.canvas_widget.get_axes()}")
        self._matplotlib_backend = MatplotlibBackend(
            fig=self.canvas_widget.get_figure(), # 通过 get_figure() 获取 Figure 对象
            ax=self.canvas_widget.get_axes()     # 通过 get_axes() 获取 Axes 对象
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
        # selected_item = self.main_controller.get_selected_item() # 获取当前选中的项以便高亮
        # print(f"Selecting item: {selected_item}")
        # self.get_ax().clear() # 清除旧绘图
        # self.get_fig().clear() # 清除旧绘图
        # **关键改动：直接调用 MatplotlibBackend 的 render 方法**
        # 传入所有绘制所需的数据，包括当前选中项的信息
        # MatplotlibBackend 将负责清除旧绘图、设置轴、绘制所有元素和高亮选中项
        self._matplotlib_backend.render(
            vertices_data,
            lines_data,
            # selected_item # 将选中项传递给后端，由后端决定如何高亮
        )

        # 告诉 CanvasWidget 的 FigureCanvasQTAgg 实例需要重绘
        self.canvas_widget.draw_idle_canvas() # 假设 CanvasWidget 提供了一个触发其底层 FigureCanvasQTAgg 重绘的方法

    def set_selected_object(self, item: [Vertex, Line, None]):
        """
        接收 MainController 传来的当前选中对象，并触发画布更新以显示高亮。
        """
        # CanvasController 自身不直接管理高亮状态，而是通过 MainController 获取全局选中项
        # 然后在 update_canvas() 时将此信息传递给 MatplotlibBackend 进行绘制。
        # 因此，这里只需要触发一次 canvas 更新即可。
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
            # 在添加线条模式下，我们还需要知道点击了哪个对象（如果有的话）
            # CanvasWidget 应该已经处理了 hit_test 并发出了 object_selected 信号，
            # 这里只需确保逻辑流正确。如果点击了空白，则重置线条创建状态。
            self.main_controller.status_message.emit("在添加线条模式下，请点击一个顶点。")
            self.reset_line_creation_state()


    def _handle_object_selected_on_canvas_widget(self, item_id: str, item_type: str):
        """
        处理 CanvasWidget 发出的对象选中信号。
        通知 MainController 更新全局选中状态。
        """
        if self._current_canvas_mode == "select":
            if item_type == "vertex":
                obj = self.diagram_model.get_vertex_by_id(item_id)
            elif item_type == "line":
                obj = self.diagram_model.get_line_by_id(item_id)
            else:
                obj = None # 理论上不会发生，因为 object_selected 应该总是带 ID 和 Type
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
        if item_type == "vertex":
            obj = self.diagram_model.get_vertex_by_id(item_id)
        elif item_type == "line":
            obj = self.diagram_model.get_line_by_id(item_id)
        else:
            obj = None
        self.main_controller.edit_item_properties(obj)


    def _handle_object_moved_on_canvas_widget(self, item_id: str, new_pos: QPointF):
        """
        处理 CanvasWidget 发出的对象移动信号（仅限顶点）。
        通知 MainController 更新模型中顶点的位置。
        """
        # MainController 直接监听 CanvasWidget 的 object_moved 信号，这里无需额外转发。
        # 如果 MainController 不直接监听，你可以在这里添加：
        # self.main_controller.object_moved.emit(item_id, new_pos)
        pass


    def _handle_selection_cleared_on_canvas_widget(self):
        """
        处理 CanvasWidget 发出的清空选中信号。
        通知 MainController 清空全局选中状态。
        """
        self.main_controller.clear_selection()

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
            # 临时高亮第一个顶点：更新画布，由 backend 处理高亮
            self.update_canvas() # 触发一次绘制，backend 会利用 selected_item 进行高亮
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
            # 清除临时高亮：再次触发绘制，因为 _first_vertex_for_line 变 None，backend 不会再高亮
            self.update_canvas()