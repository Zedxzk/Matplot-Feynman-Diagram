# feynplot_gui/widgets/canvas_widget.py

from PySide6.QtCore import QPointF, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
# --- 导入 Axes 类型 ---
from matplotlib.axes import Axes
# --------------------
from typing import Optional, Callable

class CanvasWidget(QWidget):
    # Various user interaction signals
    canvas_clicked = Signal(QPointF)
    object_selected = Signal(str, str)
    object_double_clicked = Signal(str, str)
    object_moved = Signal(str, QPointF)
    selection_cleared = Signal()
    key_delete_pressed = Signal()

    # Pan and zoom signals
    canvas_panned = Signal(QPointF)
    canvas_zoomed = Signal(QPointF, float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111) # self.axes 是一个 Axes 对象
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setParent(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Connect Matplotlib events
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('scroll_event', self._on_mouse_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_double_click_check)

        # Internal state variables
        self._is_panning = False
        self._is_dragging_object = False
        self._dragged_object_id: Optional[str] = None
        self._dragged_object_type: Optional[str] = None
        self._mouse_press_pos: Optional[QPointF] = None
        self._last_click_time = 0

        self._current_mode = "select"
        self._hit_test_callback: Optional[Callable[[float, float], tuple[Optional[str], Optional[str]]]] = None

        # Axes initial setup
        self.axes.set_aspect('equal', adjustable='box')
        self.axes.set_axis_off()
        self.figure.tight_layout()

    def get_figure(self) -> Figure:
        """返回 Matplotlib Figure 对象。"""
        return self.figure

    # --- 关键修正：将返回类型从 Figure 改为 Axes ---
    def get_axes(self) -> Axes:
        """返回 Matplotlib Axes 对象。"""
        return self.axes # 确保这里返回的是 Axes 对象
    # ----------------------------------------------

    def set_mode(self, mode: str):
        """
        允许 CanvasController 设置当前模式，并根据模式调整光标。
        """
        self._current_mode = mode
        if mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif mode == "add_line":
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_hit_test_callback(self, callback: Callable[[float, float], tuple[Optional[str], Optional[str]]]):
        """允许 CanvasController 提供一个点击检测函数。"""
        self._hit_test_callback = callback

    def draw_idle_canvas(self):
        """触发 Matplotlib 画布的空闲重绘。"""
        self.canvas.draw_idle()

    # --- 以下鼠标事件处理函数和 _on_mouse_scroll 保持不变 ---
    def _on_mouse_press(self, event):
        # ... (与之前提供的代码相同)
        if event.inaxes != self.axes or event.xdata is None or event.ydata is None:
            return

        self._mouse_press_pos = QPointF(event.xdata, event.ydata)

        if event.button == 1:  # 左键
            if self._current_mode == "select":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id:
                        self._is_dragging_object = True
                        self._dragged_object_id = item_id
                        self._dragged_object_type = item_type
                        self.object_selected.emit(item_id, item_type)
                        self.setCursor(Qt.SizeAllCursor)
                    else:
                        self.selection_cleared.emit()
                        self._is_panning = True
                        self.canvas_panned.emit(self._mouse_press_pos)
                        self.setCursor(Qt.ClosedHandCursor)
                else:
                    self._is_panning = True
                    self.canvas_panned.emit(self._mouse_press_pos)
                    self.setCursor(Qt.ClosedHandCursor)
            elif self._current_mode == "add_vertex":
                pass
            elif self._current_mode == "add_line":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id and item_type == "vertex":
                        self.object_selected.emit(item_id, item_type)
                    else:
                        self.canvas_clicked.emit(self._mouse_press_pos)
                else:
                    self.canvas_clicked.emit(self._mouse_press_pos)
        elif event.button == 3:  # 右键
            if self._current_mode == "select":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id:
                        self.object_selected.emit(item_id, item_type)
                    else:
                        self.selection_cleared.emit()
                else:
                    self.selection_cleared.emit()

    def _on_mouse_release(self, event):
        # ... (与之前提供的代码相同)
        self._is_panning = False
        self._is_dragging_object = False
        self._dragged_object_id = None
        self._dragged_object_type = None
        self._mouse_press_pos = None

        self.set_mode(self._current_mode)

        if event.button == 1 and event.inaxes == self.axes and self._current_mode == "add_vertex":
             if event.xdata is not None and event.ydata is not None:
                self.canvas_clicked.emit(QPointF(event.xdata, event.ydata))

    def _on_mouse_move(self, event):
        # ... (与之前提供的代码相同)
        if event.inaxes != self.axes or event.xdata is None or event.ydata is None:
            return

        if self._is_dragging_object and self._dragged_object_id:
            self.object_moved.emit(self._dragged_object_id, QPointF(event.xdata, event.ydata))
            self.draw_idle_canvas()
            
    def _on_double_click_check(self, event):
        # ... (与之前提供的代码相同)
        if event.button == 1:
            current_time = self.canvas.manager.timer.time()
            double_click_interval = 250
            
            if (current_time - self._last_click_time) < double_click_interval:
                if event.inaxes == self.axes and event.xdata is not None and event.ydata is not None:
                    if self._hit_test_callback:
                        item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                        if item_id:
                            self.object_double_clicked.emit(item_id, item_type)
                self._last_click_time = 0
            else:
                self._last_click_time = current_time

    def _on_mouse_scroll(self, event):
        """
        处理鼠标滚轮事件，用于缩放。
        event.step > 0 表示滚轮向上滚动 (放大)
        event.step < 0 表示滚轮向下滚动 (缩小)
        """
        if event.inaxes != self.axes:
            return

        if event.xdata is None or event.ydata is None:
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            mouse_x = (xlim[0] + xlim[1]) / 2
            mouse_y = (ylim[0] + ylim[1]) / 2
        else:
            mouse_x, mouse_y = event.xdata, event.ydata

        zoom_factor = 1.15

        if event.step > 0: # Scroll up (zoom in)
            scale_factor = 1.0 / zoom_factor
        else: # Scroll down (zoom out)
            scale_factor = zoom_factor

        self.canvas_zoomed.emit(QPointF(mouse_x, mouse_y), scale_factor)