# feynplot_gui/widgets/canvas_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Signal, QPointF, Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class CanvasWidget(QWidget):
    # 定义 CanvasWidget 自身发出的信号，供 CanvasController 监听
    canvas_clicked = Signal(QPointF)  # 当画布空白处被点击时，发出点击位置（模型坐标）
    object_selected = Signal(str, str) # 当一个对象被选中时，发出对象ID和类型 ("vertex"或"line")
    object_double_clicked = Signal(str, str) # 当一个对象被双击时，发出对象ID和类型
    object_moved = Signal(str, QPointF) # 当一个对象被拖动移动时，发出对象ID和新位置
    selection_cleared = Signal() # 当点击空白区域清除选中时发出

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True) # 启用鼠标跟踪，用于悬停检测等

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240)) # 淡灰色背景
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self._figure = Figure() # Matplotlib Figure 对象
        self._canvas_figure = FigureCanvas(self._figure) # PySide6 包装的 Matplotlib Canvas
        self._axes = self._figure.add_subplot(111) # Matplotlib Axes 对象

        self._canvas_figure.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas_figure.updateGeometry()

        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas_figure)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._current_mode = "select" # 当前画布操作模式 ('select', 'add_vertex', 'add_line', 'move')

        # 鼠标拖动状态
        self._is_dragging = False
        self._drag_start_pos_pixels = None # 拖动开始时的像素坐标
        self._dragged_object_id = None
        self._dragged_object_original_model_pos = None # 拖动前对象的模型坐标
        self._hit_test_callback = None
        
        # 连接 Matplotlib 事件监听器
        self._canvas_figure.mpl_connect('button_press_event', self._on_mouse_press)
        self._canvas_figure.mpl_connect('button_release_event', self._on_mouse_release)
        self._canvas_figure.mpl_connect('motion_notify_event', self._on_mouse_move)
        self._canvas_figure.mpl_connect('scroll_event', self._on_mouse_scroll)
        self._canvas_figure.mpl_connect('key_press_event', self._on_key_press) # 用于删除等

    def get_figure(self) -> Figure:
        """提供 Matplotlib Figure 对象给 CanvasController。"""
        return self._figure

    def get_axes(self):
        """提供 Matplotlib Axes 对象给 CanvasController。"""
        return self._axes

    def draw_idle_canvas(self):
        """
        触发底层 Matplotlib Canvas 的非阻塞重绘。
        由 CanvasController 调用。
        """
        self._canvas_figure.draw_idle()

    def set_mode(self, mode: str):
        """设置画布的当前操作模式，并更新光标。"""
        self._current_mode = mode
        if mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif mode == "add_line":
            self.setCursor(Qt.UpArrowCursor)
        elif mode == "move":
            self.setCursor(Qt.OpenHandCursor)
        else: # select
            self.setCursor(Qt.ArrowCursor)

    def set_selected_object(self, object_id: str, object_type: str):
        """
        CanvasWidget 不再管理选中状态的绘制，只作为信号转发。
        这个方法现在只是一个占位符，如果 CanvasController 决定让 CanvasWidget 临时显示一些高亮，
        这里可以实现一个临时绘制逻辑，但通常由 MatplotlibBackend 统一处理。
        """
        # 在新的架构中，这个方法可能不再需要，或者只用于 CanvasWidget 内部的临时视觉反馈
        # 而真正的选中高亮由 MatplotlibBackend 统一绘制。
        pass # CanvasController 现在通过 update_canvas 将选中项传递给 backend

    # --- Matplotlib 事件处理 ---
    def _on_mouse_press(self, event):
        if event.inaxes != self._axes: # 确保点击在坐标轴区域内
            return

        # 将点击的屏幕像素坐标转换为 Matplotlib 数据坐标
        x_data, y_data = event.xdata, event.ydata

        if event.button == 1: # 左键点击
            if self._current_mode == "select":
                # 在 select 模式下，需要先进行 hit_test
                # CanvasWidget 无法直接访问 backend 的 hit_test，所以这个逻辑应该在 CanvasController 中
                # 这里 CanvasWidget 只能发出原始坐标，让 CanvasController 来判断
                # 这是一个架构权衡，为了简化 CanvasWidget，我们将 hit_test 决策推给 CanvasController
                
                # 由于 CanvasWidget 之前发出 object_selected 信号，为了兼容，
                # 我们需要在 CanvasWidget 中以某种方式获取 hit_test 结果。
                # 最好的方式是 CanvasController 在初始化时，将其 MatplotlibBackend 的 hit_test 方法
                # 传递给 CanvasWidget。
                # 为了保持当前代码结构，我们暂时假设一个内部 hit_test 方法，
                # 但它的实现依赖于 MatplotlibBackend。
                
                # 让我们明确一下：CanvasWidget 不应该直接访问 MatplotlibBackend。
                # CanvasWidget 应该只发出鼠标事件的原始信息（坐标）。
                # CanvasController 收到原始鼠标事件后，再调用其 MatplotlibBackend 进行 hit_test。
                
                # 鉴于你提供的 `_handle_object_selected_on_canvas_widget` 签名，
                # 意味着 `CanvasWidget` 必须发出 `item_id` 和 `item_type`。
                # 这就要求 `CanvasWidget` 能够进行 hit_test。
                # 为了解决这个矛盾，我们让 `CanvasWidget` 在初始化时接收 `hit_test_callback`。

                hit_object_id, hit_object_type = self._hit_test_object(x_data, y_data)
                
                if hit_object_id:
                    self._is_dragging = True
                    self._drag_start_pos_pixels = QPointF(event.x, event.y)
                    self._dragged_object_id = hit_object_id
                    # 发出对象选中信号
                    self.object_selected.emit(hit_object_id, hit_object_type)
                    
                    # 原始位置由 MainController 在收到 object_selected 后，通过模型查询并传递回来
                    pass

                else:
                    self.selection_cleared.emit() # 点击空白处，清除选中
                    self._is_dragging = False

            elif self._current_mode == "add_vertex":
                self.canvas_clicked.emit(QPointF(x_data, y_data))
            elif self._current_mode == "add_line":
                hit_object_id, hit_object_type = self._hit_test_object(x_data, y_data)
                if hit_object_id and hit_object_type == "vertex":
                    self.object_selected.emit(hit_object_id, hit_object_type)
                else:
                    self.canvas_clicked.emit(QPointF(x_data, y_data))


    def _on_mouse_release(self, event):
        if event.button == 1: # 左键释放
            if self._is_dragging:
                self._is_dragging = False
                if self._dragged_object_id and self._current_mode == "select":
                    if event.xdata is not None and event.ydata is not None:
                        new_model_pos = QPointF(event.xdata, event.ydata)
                        
                        # 这部分逻辑（判断是否是顶点和位置变化）应该由 MainController 处理
                        # CanvasWidget 只是发出原始的移动信息
                        # 暂时先移除冗余的判断，让 CanvasWidget 仅发出信号
                        # self.object_moved.emit(self._dragged_object_id, new_model_pos)
                        pass # 实际的 object_moved 信号在 mouse_move 中发出（如果实时拖动）或在 MainController 处理
                self._dragged_object_id = None
                self._dragged_object_original_model_pos = None
            else: # 非拖动情况下的单击
                if event.dblclick:
                    x_data, y_data = event.xdata, event.ydata
                    if x_data is not None and y_data is not None:
                        hit_object_id, hit_object_type = self._hit_test_object(x_data, y_data)
                        if hit_object_id:
                            self.object_double_clicked.emit(hit_object_id, hit_object_type)

    def _on_mouse_move(self, event):
        if event.inaxes != self._axes:
            self.setCursor(Qt.ArrowCursor)
            return

        if self._is_dragging and self._dragged_object_id and self._current_mode == "select":
            self.setCursor(Qt.ClosedHandCursor)
            # 在这里，如果需要实时预览，CanvasWidget 应该发出一个包含新位置的信号
            # 让 MainController 更新模型，然后 CanvasController 刷新视图
            # 这里我们直接发出 object_moved 信号，因为 CanvasController 会监听它
            if event.xdata is not None and event.ydata is not None:
                new_model_pos = QPointF(event.xdata, event.ydata)
                # 只有当拖动的是顶点时才发出移动信号
                # 这里的 hit_test_object 需要足够智能，知道 _dragged_object_id 是顶点还是线
                # 假设 _dragged_object_id 是顶点，且 CanvasWidget 某种方式知道其类型
                # 更健壮的实现是在 `object_selected` 信号中附带类型信息。
                # 为了简化，我们假设 `object_moved` 信号是针对顶点的。
                
                # 临时添加一个类型判断，但最好在拖动开始时就知道类型
                # 这是 `_hit_test_object` 需要改进的地方
                # 我们可以让 `_dragged_object_type` 也成为状态
                # if self._dragged_object_type == "vertex":
                self.object_moved.emit(self._dragged_object_id, new_model_pos)


        elif self._current_mode == "move":
            self.setCursor(Qt.OpenHandCursor)
        elif self._current_mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif self._current_mode == "add_line":
            self.setCursor(Qt.UpArrowCursor)
        else: # select mode
            x_data, y_data = event.xdata, event.ydata
            if x_data is not None and y_data is not None:
                hit_object_id, _ = self._hit_test_object(x_data, y_data)
                if hit_object_id:
                    self.setCursor(Qt.PointingHandCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

    def _on_mouse_scroll(self, event):
        """处理鼠标滚轮事件进行缩放。"""
        if event.inaxes != self._axes:
            return

        xlim = self._axes.get_xlim()
        ylim = self._axes.get_ylim()

        x_mouse, y_mouse = event.xdata, event.ydata
        scale_factor = 1.1 if event.button == 'up' else 1 / 1.1

        new_xlim = [x_mouse - (x_mouse - xlim[0]) * scale_factor,
                    x_mouse + (xlim[1] - x_mouse) * scale_factor]
        new_ylim = [y_mouse - (y_mouse - ylim[0]) * scale_factor,
                    y_mouse + (ylim[1] - y_mouse) * scale_factor]

        self._axes.set_xlim(new_xlim)
        self._axes.set_ylim(new_ylim)
        self.draw_idle_canvas() # 触发重绘

    def _on_key_press(self, event):
        """处理键盘事件，例如删除选中对象。"""
        # CanvasWidget 应该只发出键盘事件信号，而不是直接调用 MainController
        # MainController 应该监听这些事件。
        # 为了简化，这里暂时直接调用 MainController 方法
        if event.key == 'delete' or event.key == 'backspace':
            self.main_controller.delete_selected_object()
            self.selection_cleared.emit() # 删除后清除选中状态

    # **重要：这个方法现在必须在 CanvasWidget 初始化时，通过 CanvasController 传入 MatplotlibBackend 的 hit_test 方法。**
    # 或者，CanvasWidget 只发出原始点击事件，由 CanvasController 负责 hit_test。
    # 为了保持 object_selected 信号由 CanvasWidget 发出，我们选择传入 hit_test 方法。
    # 所以，CanvasWidget 的 __init__ 将需要一个额外的参数 `hit_test_callback`。
    def _hit_test_object(self, x: float, y: float) -> (str, str):
        """
        这个方法将调用由 CanvasController 传入的 MatplotlibBackend 的 hit_test 方法。
        """
        if self._hit_test_callback: # 确保回调函数已设置
            return self._hit_test_callback(x, y)
        return None, None # 如果回调未设置，返回None